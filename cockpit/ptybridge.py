"""Cockpit terminal bridge — real interactive `claude` over a PTY.

Why this exists (the B pivot, S066): the /chat driver in backend.py runs headless
`claude -p`, which Anthropic moves onto a metered API-rate credit pool on
2026-06-15 (Agent SDK + `claude -p` + GitHub Actions stop counting toward the
Claude subscription). *Interactive* Claude Code in a terminal stays on the
subscription, unchanged. So this bridge spawns a real PowerShell PTY and runs
`claude --session-id <uuid>` interactively inside it, piped to an xterm.js
terminal in the cockpit window. Bonuses, both free with a real TTY:
  - Esc cancels (the headless path never wired it),
  - AskUserQuestion / ExitPlanMode / permission prompts work natively (the
    headless path can't answer them — the CLI auto-dismisses, see S065).

Lifted near-verbatim from the archived switchboard/server.py /pty handler, which
was proven but never shipped. Kept in its own module so it stays out of the
backend.py merge surface while siblings edit chat_handler.

Wire protocol (one WS ⇄ one PTY ⇄ one claude session):
  server → client : {"t":"session","sessionId","sid8"} once, then {"t":"out","d"}.
  client → server : {"type":"input","data"} | {"type":"resize","cols","rows"}.

cwd = brain root, so brain/.claude/settings.json is picked up → a claude launched
here lands on the fleet board like any VS Code session. The server mints the
session uuid (--session-id) and announces it, so a board-row click can jump to
the terminal hosting that session.
"""
from __future__ import annotations

import asyncio
import json
import os
import threading
import uuid
from pathlib import Path
from urllib.parse import urlsplit

from aiohttp import web, WSMsgType

BRAIN_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SHELL = ["powershell.exe", "-NoLogo"]
# Terminal dimensions are attacker-influenceable (query params); clamp to sane
# bounds so a hostile/garbage value can't wedge the PTY or winpty.
COLS_MIN, COLS_MAX = 20, 500
ROWS_MIN, ROWS_MAX = 5, 200

# The live switchboard manifest (status-sidecar.py writes it). We read it to map
# this PTY's shell pid → the session id currently live in the terminal, so we can
# re-announce when claude rotates its id mid-terminal (see _session_for_shell_pid
# / the watch task in pty_handler). Same file the board reads — guaranteed in sync.
MANIFEST_PATH = BRAIN_ROOT / "switchboard" / "state-switchboard.json"
# {sid8: label} — disk-backed board renames (same store as backend.api_rename,
# rename-intercept.py, status-sidecar.py). Carried across an id rotation below.
NAMES_PATH = BRAIN_ROOT / "switchboard" / "state-names.json"
SESSION_WATCH_SEC = 2.0  # how often to re-check the live session id (board cadence)


def _carry_disk_name(old_sid8: str, new_sid8: str) -> None:
    """Carry a board label across a session-id rotation. `claude --resume` (what a
    cockpit reopen runs) and `/clear` both mint a NEW session id; the rename in
    state-names.json is keyed on the OLD sid8, so without this it's orphaned and
    the resumed row comes back on its bare actor label — the "lost rename on
    reopen" bug. Copy old→new only when the old has a label and the new doesn't
    (never clobber a fresh rename). Best-effort: any IO/parse failure leaves the
    row unnamed, exactly as before, and never raises into the PTY pump."""
    if not old_sid8 or not new_sid8 or old_sid8 == new_sid8:
        return
    try:
        names = json.loads(NAMES_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return
    if not isinstance(names, dict):
        return
    label = names.get(old_sid8)
    if not label or names.get(new_sid8):
        return
    names[new_sid8] = label
    try:
        NAMES_PATH.write_text(json.dumps(names, indent=2), encoding="utf-8")
    except OSError:
        pass


def _session_for_shell_pid(shell_pid: int):
    """The session id currently live in the PTY whose shell process is `shell_pid`.

    The cockpit pins the FIRST conversation via `claude --session-id <uuid>` and
    announces that id once. But a `/clear` (or one task ending and a new one
    starting in the same shell) rotates claude's session id out from under us —
    the hooks then track the new id while the cockpit still drives/labels the old
    one, splitting the terminal into a stale drivable row + a read-only manifest
    row (the duplicate-row bug). Every session's status record carries its
    `claude_pid_chain`, and this PTY's shell pid is always an ancestor of the
    claude.exe it launched — so the freshest manifest session whose chain contains
    our shell pid IS the conversation live in this terminal right now. The
    manifest already excludes `ended` sessions, so a match is always live.
    Returns the full session_id, or None when nothing matches (claude not up yet,
    or sitting at a bare shell prompt)."""
    try:
        data = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    except Exception:
        return None
    best = None  # (last_event_ts, session_id)
    for j in (data.get("sessions") or []):
        if not isinstance(j, dict):
            continue
        chain = j.get("claude_pid_chain") or []
        pids = {e.get("pid") for e in chain if isinstance(e, dict)}
        if shell_pid not in pids:
            continue
        sid = j.get("session_id")
        if not sid:
            continue
        try:
            ts = float(j.get("last_event_ts") or 0)
        except (TypeError, ValueError):
            ts = 0.0
        if best is None or ts > best[0]:
            best = (ts, sid)
    return best[1] if best else None


def _clamp(v, lo, hi):
    return max(lo, min(hi, v))


async def _ws_send(ws, obj) -> bool:
    try:
        await ws.send_str(json.dumps(obj))
        return True
    except Exception:
        return False


def _qint(request, key, default):
    try:
        return int(request.query.get(key, default))
    except (TypeError, ValueError):
        return default


def _is_uuid(s):
    try:
        uuid.UUID(s)
        return True
    except (ValueError, TypeError, AttributeError):
        return False


async def pty_handler(request):
    """One WebSocket ⇄ one PTY running interactive claude.

    Auth (S085): /pty spawns and drives a PowerShell PTY, so an unauthenticated
    handler is a localhost RCE — any webpage the user visits while the cockpit is
    running could open this WS and run commands. Two gates, both before the WS
    upgrade: (1) a per-process token baked into the same-origin HTML (a cross-
    origin page can't read it, so it can't forge a connection) — fail-closed;
    (2) an Origin check rejecting any cross-host browser origin. The legit
    pywebview page (served from this same host) passes both.
    """
    if request.query.get("token") != request.app.get("cockpit_token"):
        return web.Response(status=403, text="forbidden")
    origin = request.headers.get("Origin")
    if origin:
        netloc = urlsplit(origin).netloc
        if netloc and netloc != request.host:
            return web.Response(status=403, text="forbidden")

    ws = web.WebSocketResponse(heartbeat=30, max_msg_size=0)
    await ws.prepare(request)
    loop = asyncio.get_running_loop()

    try:
        from winpty import PtyProcess
    except Exception as exc:  # pywinpty missing — tell the client, don't 500
        await _ws_send(ws, {"t": "out", "d": f"\r\n[cockpit] pywinpty not installed: {exc}\r\n"})
        await ws.close()
        return ws

    cols = _clamp(_qint(request, "cols", 120), COLS_MIN, COLS_MAX)
    rows = _clamp(_qint(request, "rows", 30), ROWS_MIN, ROWS_MAX)
    launch = request.query.get("launch", "").strip()
    resume = request.query.get("resume", "").strip()
    resuming = bool(resume) and _is_uuid(resume)
    session_id = resume if resuming else str(uuid.uuid4())

    # The cockpit is often launched from a VSCode-hosted shell, which leaks
    # VSCODE_PID/TERM_PROGRAM into every child — so a claude spawned here would
    # masquerade as a "vscode" session on the board (status-sidecar._detect_host).
    # Strip those and stamp CLAUDE_COCKPIT so the hook attributes it to "cockpit".
    env = dict(os.environ)
    env.pop("VSCODE_PID", None)
    if env.get("TERM_PROGRAM") == "vscode":
        env.pop("TERM_PROGRAM", None)
    env["CLAUDE_COCKPIT"] = "1"

    try:
        proc = PtyProcess.spawn(DEFAULT_SHELL, cwd=str(BRAIN_ROOT), env=env, dimensions=(rows, cols))
    except Exception as exc:
        await _ws_send(ws, {"t": "out", "d": f"\r\n[cockpit] failed to start shell: {exc}\r\n"})
        await ws.close()
        return ws

    # Announce the session before any output flows (frame #1). `announced` tracks
    # the id the client currently believes it's driving; the watch task below
    # re-announces (and updates this) when claude rotates its id mid-terminal.
    announced = {"sid": session_id}
    await _ws_send(ws, {"t": "session", "sessionId": session_id,
                        "sid8": session_id[:8], "resumed": resuming})

    if resuming:
        # reattach to the saved session — survives cockpit reload/restart.
        proc.write(f"claude --resume {session_id}\r")
    elif launch == "claude":
        # powershell resolves the `claude` .cmd shim via its own lookup,
        # sidestepping CreateProcess PATH quirks. Interactive — no -p.
        proc.write(f"claude --session-id {session_id}\r")
    # NOTE (S085): the old `elif launch: proc.write(launch + "\r")` arbitrary
    # passthrough is GONE — it let any caller run an arbitrary command in the PTY
    # (RCE). Only the two fixed launches above are accepted; an unknown `launch`
    # value just leaves the user at a fresh PowerShell prompt, runs nothing.

    queue: asyncio.Queue = asyncio.Queue()
    stop = threading.Event()

    def reader():
        try:
            while not stop.is_set():
                try:
                    data = proc.read(1024)
                except EOFError:
                    break
                except Exception:
                    break
                if data:
                    loop.call_soon_threadsafe(queue.put_nowait, data)
                elif not proc.isalive():
                    break
        finally:
            loop.call_soon_threadsafe(queue.put_nowait, None)  # sentinel

    threading.Thread(target=reader, daemon=True).start()

    async def pump_out():
        while True:
            data = await queue.get()
            if data is None:
                break
            if not await _ws_send(ws, {"t": "out", "d": data}):
                break
        if not ws.closed:
            await ws.close()

    out_task = asyncio.create_task(pump_out())

    async def watch_session():
        """Re-announce when claude rotates its session id inside this PTY.

        Polls the manifest for the live session id bound to this PTY's shell pid
        (see _session_for_shell_pid). When it differs from what the client last
        heard, we send a fresh `session` frame — the client swaps its sid8 so
        liveTerms reports the current id, the manifest row becomes drivable, and
        the stale duplicate row collapses without a cockpit relaunch. File reads
        run in the executor so a slow disk never stalls the PTY pump."""
        shell_pid = getattr(proc, "pid", None)
        if not shell_pid:
            return
        try:
            while not stop.is_set():
                await asyncio.sleep(SESSION_WATCH_SEC)
                cur = await loop.run_in_executor(None, _session_for_shell_pid, shell_pid)
                if cur and cur != announced["sid"]:
                    prev = announced["sid"]
                    announced["sid"] = cur
                    # Carry the disk-backed board label old sid8 → new sid8 before
                    # the client swaps, so a rotated/resumed row keeps its name.
                    await loop.run_in_executor(None, _carry_disk_name, prev[:8], cur[:8])
                    await _ws_send(ws, {"t": "session", "sessionId": cur,
                                        "sid8": cur[:8], "resumed": False, "rotated": True})
        except asyncio.CancelledError:
            pass

    watch_task = asyncio.create_task(watch_session())

    try:
        async for msg in ws:
            if msg.type != WSMsgType.TEXT:
                if msg.type == WSMsgType.ERROR:
                    break
                continue
            try:
                obj = json.loads(msg.data)
            except (ValueError, TypeError):
                continue
            kind = obj.get("type")
            if kind == "input":
                try:
                    proc.write(obj.get("data", ""))
                except Exception:
                    break
            elif kind == "resize":
                try:
                    proc.setwinsize(_clamp(int(obj["rows"]), ROWS_MIN, ROWS_MAX),
                                    _clamp(int(obj["cols"]), COLS_MIN, COLS_MAX))
                except Exception:
                    pass
    finally:
        stop.set()
        try:
            proc.terminate(force=True)
        except Exception:
            pass
        out_task.cancel()
        watch_task.cancel()
    return ws
