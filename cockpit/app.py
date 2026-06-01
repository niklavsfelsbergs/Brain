"""Cockpit app shell — ONE process: backend + native window.

pywebview opens a chromeless OS window; the aiohttp backend runs in a daemon
thread in the same process. Launch and death are atomic — there is no separate
server to go stale or squat the port (the disease that plagued the old build).

If something is already serving the port (a dev server, or another cockpit),
we reuse it instead of binding a second time, and just open a window at it.

Launch via the desktop/Start-menu shortcut (made by make-shortcut.ps1) or
run.bat. config.json may set {"on_top": true}.
"""
from __future__ import annotations

import asyncio
import json
import os
import socket
import threading
import time
from pathlib import Path

import webview
from aiohttp import web

from backend import make_app, COCKPIT_DIR

PORT = 8770
CONFIG = COCKPIT_DIR / "config.json"
ICON = COCKPIT_DIR / "icon.ico"
# Taskbar identity. Windows groups taskbar buttons by AppUserModelID and resolves
# the button ICON from it — with no explicit AUMID the cockpit's button inherits
# pythonw.exe's python icon regardless of the window icon. Declaring our own AUMID
# makes the taskbar use the window icon (SB). The SAME id is stamped onto the
# Desktop/Start shortcut by make-shortcut.ps1 so the running window coalesces with
# the pinned shortcut into one button instead of splitting. (S140)
APP_ID = "gielinor.cockpit.switchboard"


def _apply_window_icon(window):
    """Stamp the SB icon onto the running window's title bar + taskbar button.

    The Windows pywebview backend hosts EdgeChromium in a .NET WinForms Form, so
    window.native.Icon takes a System.Drawing.Icon. NOTE: the `System` namespace
    only resolves after clr.AddReference — the bare `from System.Drawing import
    Icon` raises ModuleNotFoundError (this silently no-op'd before). If the .NET
    path fails we fall back to a raw Win32 WM_SETICON on the window handle.

    Best-effort — a failure here must never break launch (the cockpit's whole
    launch story is "can't go stale"); worst case the window keeps pythonw's icon.
    A one-line status is written to icon-apply.log so a relaunch can confirm it
    took without eyeballing (temporary diag — strip once verified).
    """
    import time
    # pywebview runs this start-callback in its own thread, which can fire BEFORE
    # the GUI thread has constructed the native WinForms window — window.native is
    # None for the first beat. Poll until it exists (~5s ceiling) before touching it.
    native = None
    for _ in range(100):
        native = getattr(window, "native", None)
        if native is not None:
            break
        time.sleep(0.05)
    status = "unset"
    try:
        if native is None:
            raise RuntimeError("window.native never appeared")
        import clr
        clr.AddReference("System.Drawing")
        from System.Drawing import Icon
        native.Icon = Icon(str(ICON))
        status = "ok: System.Drawing.Icon"
    except Exception as e:
        status = f"net-fail ({type(e).__name__}: {e})"
        try:
            import ctypes
            hwnd = int(native.Handle.ToInt64())
            # LoadImageW(NULL, path, IMAGE_ICON=1, 0, 0, LR_LOADFROMFILE|LR_DEFAULTSIZE)
            hicon = ctypes.windll.user32.LoadImageW(None, str(ICON), 1, 0, 0, 0x10 | 0x40)
            if hicon:
                WM_SETICON = 0x0080
                ctypes.windll.user32.SendMessageW(hwnd, WM_SETICON, 0, hicon)  # ICON_SMALL
                ctypes.windll.user32.SendMessageW(hwnd, WM_SETICON, 1, hicon)  # ICON_BIG
                status += " | win32 fallback: ok"
            else:
                status += " | win32 fallback: LoadImage returned 0"
        except Exception as e2:
            status += f" | win32 fallback fail ({type(e2).__name__}: {e2})"
    try:
        (COCKPIT_DIR / "icon-apply.log").write_text(status + "\n", encoding="utf-8")
    except OSError:
        pass


def _set_app_id():
    """Declare our AppUserModelID before any window is created, so the taskbar
    button uses the window's SB icon (not pythonw's) and coalesces with the
    matching-AUMID pinned shortcut. Must run before create_window."""
    try:
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_ID)
    except Exception:
        pass


def _own_process_tree():
    """PIDs of this process plus all descendants (Toolhelp snapshot — no deps)."""
    import ctypes
    from ctypes import wintypes
    TH32CS_SNAPPROCESS = 0x2

    class PROCESSENTRY32(ctypes.Structure):
        _fields_ = [("dwSize", wintypes.DWORD), ("cntUsage", wintypes.DWORD),
                    ("th32ProcessID", wintypes.DWORD), ("th32DefaultHeapID", ctypes.POINTER(ctypes.c_ulong)),
                    ("th32ModuleID", wintypes.DWORD), ("cntThreads", wintypes.DWORD),
                    ("th32ParentProcessID", wintypes.DWORD), ("pcPriClassBase", ctypes.c_long),
                    ("dwFlags", wintypes.DWORD), ("szExeFile", ctypes.c_char * 260)]

    k32 = ctypes.windll.kernel32
    snap = k32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
    parent = {}
    pe = PROCESSENTRY32(); pe.dwSize = ctypes.sizeof(PROCESSENTRY32)
    if k32.Process32First(snap, ctypes.byref(pe)):
        while True:
            parent[pe.th32ProcessID] = pe.th32ParentProcessID
            if not k32.Process32Next(snap, ctypes.byref(pe)):
                break
    k32.CloseHandle(snap)
    me = os.getpid()
    mine = {me}
    changed = True
    while changed:  # transitive closure of descendants
        changed = False
        for pid, ppid in parent.items():
            if ppid in mine and pid not in mine:
                mine.add(pid); changed = True
    return mine


def _hide_stray_consoles():
    """Hide stray console windows belonging to the cockpit's own process tree.

    The cockpit drives every terminal in its web UI, so it needs no OS console
    window — but pywebview re-execs into a console-subsystem python.exe child, and
    the auto-resumed PTYs' conhost can surface a ConsoleWindowClass window. Both
    carry the cockpit's icon and are pure noise. We hide (never kill) any such
    window owned by us or a descendant. Runs in a daemon thread because sessions
    can be opened any time, not just at launch. Best-effort, never fatal."""
    import ctypes
    from ctypes import wintypes
    u32 = ctypes.windll.user32
    SW_HIDE = 0
    EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)

    def sweep():
        try:
            mine = _own_process_tree()
        except Exception:
            mine = {os.getpid()}

        def cb(hwnd, _):
            if not u32.IsWindowVisible(hwnd):
                return True
            cls = ctypes.create_unicode_buffer(64)
            u32.GetClassNameW(hwnd, cls, 64)
            if cls.value != "ConsoleWindowClass":
                return True
            pid = wintypes.DWORD()
            u32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            if pid.value in mine:
                u32.ShowWindow(hwnd, SW_HIDE)
            return True

        try:
            u32.EnumWindows(EnumWindowsProc(cb), 0)
        except Exception:
            pass

    def loop():
        for _ in range(60):      # ~30s of half-second sweeps covers launch + early opens
            sweep()
            time.sleep(0.5)
        while True:              # then a slow heartbeat for sessions opened later
            sweep()
            time.sleep(3)

    threading.Thread(target=loop, daemon=True).start()


def _port_serving(port: int) -> bool:
    s = socket.socket()
    s.settimeout(0.3)
    try:
        s.connect(("127.0.0.1", port))
        return True
    except OSError:
        return False
    finally:
        s.close()


def _start_backend(host: str = "127.0.0.1"):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    runner = web.AppRunner(make_app())
    loop.run_until_complete(runner.setup())
    loop.run_until_complete(web.TCPSite(runner, host, PORT).start())
    loop.run_forever()


def _load_config() -> dict:
    try:
        return json.loads(CONFIG.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def main():
    cfg = _load_config()
    # Bind host. Default 127.0.0.1 = localhost-only (the historical, fully-safe
    # behavior — the cockpit's only security boundary is "loopback-bound", see
    # backend.py). Opt in to remote access (e.g. from a phone over Tailscale) by
    # setting config.json {"host": "0.0.0.0"} or {"host": "<this-PC-tailscale-ip>"}.
    # ONLY widen this on a trusted network/VPN: anyone who can load the page gets
    # the baked-in /pty token and can drive claude (== shell on this machine).
    host = str(cfg.get("host", "127.0.0.1"))
    if not _port_serving(PORT):
        threading.Thread(target=_start_backend, args=(host,), daemon=True).start()
        time.sleep(0.4)  # let the socket bind before the window loads
    # The local pywebview window always reaches the backend on loopback when the
    # bind host accepts loopback (127.0.0.1 / 0.0.0.0); for a specific non-loopback
    # bind IP the window must use that IP instead.
    window_host = "127.0.0.1" if host in ("127.0.0.1", "0.0.0.0") else host
    _set_app_id()
    _hide_stray_consoles()
    win = webview.create_window(
        "Switchboard",
        f"http://{window_host}:{PORT}/",
        width=1500,
        height=920,          # fallback size if un-maximized
        min_size=(960, 640),
        maximized=True,       # open filling the screen
        on_top=bool(cfg.get("on_top", False)),
    )
    # Set the taskbar/title-bar icon once the native window actually exists. The
    # `shown` event fires on the GUI thread after window creation, so window.native
    # is populated by then — the start() callback raced ahead of native creation
    # and saw None (icon-apply.log: 'NoneType has no attribute Icon'). `loaded` is
    # registered as a backstop in case `shown` doesn't fire on this backend. (S140)
    win.events.shown += lambda *a: _apply_window_icon(win)
    win.events.loaded += lambda *a: _apply_window_icon(win)
    # private_mode defaults to True (ephemeral profile) — that wipes localStorage
    # on every launch, which is where session-persistence, renames, and toggles
    # live. Persist to a stable profile dir so they survive close/reopen. (S066)
    webview.start(private_mode=False, storage_path=str(COCKPIT_DIR / ".webview"))


if __name__ == "__main__":
    main()
