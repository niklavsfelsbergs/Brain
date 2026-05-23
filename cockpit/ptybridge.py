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
import threading
import uuid
from pathlib import Path

from aiohttp import web, WSMsgType

BRAIN_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SHELL = ["powershell.exe", "-NoLogo"]


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


async def pty_handler(request):
    """One WebSocket ⇄ one PTY running interactive claude."""
    ws = web.WebSocketResponse(heartbeat=30, max_msg_size=0)
    await ws.prepare(request)
    loop = asyncio.get_running_loop()

    try:
        from winpty import PtyProcess
    except Exception as exc:  # pywinpty missing — tell the client, don't 500
        await _ws_send(ws, {"t": "out", "d": f"\r\n[cockpit] pywinpty not installed: {exc}\r\n"})
        await ws.close()
        return ws

    cols = _qint(request, "cols", 120)
    rows = _qint(request, "rows", 30)
    launch = request.query.get("launch", "").strip()
    session_id = str(uuid.uuid4())

    try:
        proc = PtyProcess.spawn(DEFAULT_SHELL, cwd=str(BRAIN_ROOT), dimensions=(rows, cols))
    except Exception as exc:
        await _ws_send(ws, {"t": "out", "d": f"\r\n[cockpit] failed to start shell: {exc}\r\n"})
        await ws.close()
        return ws

    # Announce the minted session before any output flows (frame #1).
    await _ws_send(ws, {"t": "session", "sessionId": session_id, "sid8": session_id[:8]})

    if launch == "claude":
        # powershell resolves the `claude` .cmd shim via its own lookup,
        # sidestepping CreateProcess PATH quirks. Interactive — no -p.
        proc.write(f"claude --session-id {session_id}\r")
    elif launch:
        proc.write(launch + "\r")

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
                    proc.setwinsize(int(obj["rows"]), int(obj["cols"]))
                except Exception:
                    pass
    finally:
        stop.set()
        try:
            proc.terminate(force=True)
        except Exception:
            pass
        out_task.cancel()
    return ws
