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
import socket
import threading
import time
from pathlib import Path

import webview
from aiohttp import web

from backend import make_app, COCKPIT_DIR

PORT = 8770
CONFIG = COCKPIT_DIR / "config.json"


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


def _start_backend():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    runner = web.AppRunner(make_app())
    loop.run_until_complete(runner.setup())
    loop.run_until_complete(web.TCPSite(runner, "127.0.0.1", PORT).start())
    loop.run_forever()


def _load_config() -> dict:
    try:
        return json.loads(CONFIG.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def main():
    if not _port_serving(PORT):
        threading.Thread(target=_start_backend, daemon=True).start()
        time.sleep(0.4)  # let the socket bind before the window loads
    cfg = _load_config()
    webview.create_window(
        "Switchboard",
        f"http://127.0.0.1:{PORT}/",
        width=1500,
        height=920,          # fallback size if un-maximized
        min_size=(960, 640),
        maximized=True,       # open filling the screen
        on_top=bool(cfg.get("on_top", False)),
    )
    # private_mode defaults to True (ephemeral profile) — that wipes localStorage
    # on every launch, which is where session-persistence, renames, and toggles
    # live. Persist to a stable profile dir so they survive close/reopen. (S066)
    webview.start(private_mode=False, storage_path=str(COCKPIT_DIR / ".webview"))


if __name__ == "__main__":
    main()
