"""switchboard/server.py — static file server + PTY-bridge WebSocket.

Replaces `python -m http.server 8765` for the switchboard. Two jobs in one
process:

  1. Serve the switchboard's static files (index.html, the JS modules, the
     hook-written state-*.json / chat.ndjson the panels poll). GET-only, same
     as the old http.server — the observability surface stays read-only.
  2. Bridge browser xterm.js terminals to real PTYs over a WebSocket at /pty.
     Each WS connection owns one PTY running a shell that auto-launches
     `claude --session-id <uuid>` at the brain root.

Two things make the loop close:
  - cwd = brain root, so `brain/.claude/settings.json` is picked up → a claude
    launched here lands on the switchboard board like any VS Code session.
  - the server MINTS the session UUID (`--session-id`) and announces it back to
    the browser, so each terminal knows its own sid8. That lets a switchboard
    row click jump straight to the terminal hosting that session (S060 slice 2).

Wire protocol (per /pty connection):
  server → client : JSON frames. `{"t":"session","sessionId","sid8"}` once at
                    start, then `{"t":"out","d":<pty text>}` for output.
  client → server : `{"type":"input","data"}` / `{"type":"resize","cols","rows"}`.

Run:  switchboard/.venv/Scripts/python.exe switchboard/server.py
      then open http://localhost:8765/?live=1

Deps (in switchboard/.venv): pywinpty, aiohttp.
"""

import asyncio
import json
import shutil
import threading
import uuid
from pathlib import Path

from aiohttp import web, WSMsgType
from winpty import PtyProcess

SWITCHBOARD_DIR = Path(__file__).resolve().parent
BRAIN_ROOT = SWITCHBOARD_DIR.parent          # cwd for spawned sessions
DEFAULT_SHELL = ["powershell.exe", "-NoLogo"]
CLAUDE_EXE = shutil.which("claude") or "claude"
PORT = 8765


# ─── PTY bridge ───────────────────────────────────────────────────────────

async def pty_handler(request: web.Request) -> web.WebSocketResponse:
    """One WebSocket ⇄ one PTY (one claude session)."""
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    loop = asyncio.get_running_loop()

    cols = _qint(request, "cols", 120)
    rows = _qint(request, "rows", 30)
    launch = request.query.get("launch", "").strip()

    # Mint the session id up front so we can both pass it to claude and tell
    # the browser which sid8 this terminal will own.
    session_id = str(uuid.uuid4())
    sid8 = session_id[:8]

    try:
        proc = PtyProcess.spawn(
            DEFAULT_SHELL, cwd=str(BRAIN_ROOT), dimensions=(rows, cols)
        )
    except Exception as exc:  # spawn failure — tell the client, don't 500
        await _send(ws, {"t": "out", "d": f"\r\n[switchboard] failed to start shell: {exc}\r\n"})
        await ws.close()
        return ws

    # Announce the session before any output flows (frame #1).
    await _send(ws, {"t": "session", "sessionId": session_id, "sid8": sid8})

    if launch == "claude":
        # Deterministic session id → the board row for this session is keyed by
        # `sid8`, which the browser now knows. powershell resolves `claude` (the
        # .cmd shim) via its own lookup, sidestepping CreateProcess PATH quirks.
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
            if not await _send(ws, {"t": "out", "d": data}):
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


# ─── Headless agent bridge (chat UI) ───────────────────────────────────────

async def chat_handler(request: web.Request) -> web.WebSocketResponse:
    """One WebSocket ⇄ one headless `claude` process in stream-json mode.

    Unlike /pty (a TTY running claude's TUI), this spawns claude with clean
    pipes and the structured streaming protocol, so the browser can render a
    custom chat UI instead of a terminal. Streaming-input mode keeps the
    process alive for a multi-turn conversation.

    Wire protocol:
      server → client : {"t":"session",...} once, then {"t":"event","ev":<claude
                        stream-json event>}, {"t":"stderr","d"}, {"t":"exit","code"}.
      client → server : {"type":"input","text":<user message>}.
    """
    ws = web.WebSocketResponse(heartbeat=30)
    await ws.prepare(request)

    session_id = str(uuid.uuid4())
    sid8 = session_id[:8]
    await _send(ws, {"t": "session", "sessionId": session_id, "sid8": sid8})

    args = [
        CLAUDE_EXE, "-p",
        "--input-format", "stream-json",
        "--output-format", "stream-json",
        "--include-partial-messages",
        "--verbose",
        "--permission-mode", "bypassPermissions",
        "--session-id", session_id,
    ]
    try:
        proc = await asyncio.create_subprocess_exec(
            *args,
            cwd=str(BRAIN_ROOT),
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            limit=8 * 1024 * 1024,        # init/assistant lines can be large
        )
    except Exception as exc:
        await _send(ws, {"t": "stderr", "d": f"failed to launch claude: {exc}"})
        await ws.close()
        return ws

    async def pump_stdout():
        try:
            async for raw in proc.stdout:
                line = raw.decode("utf-8", "replace").strip()
                if not line:
                    continue
                try:
                    ev = json.loads(line)
                except ValueError:
                    await _send(ws, {"t": "stderr", "d": line})
                    continue
                if not await _send(ws, {"t": "event", "ev": ev}):
                    break
        finally:
            await _send(ws, {"t": "exit", "code": proc.returncode})
            if not ws.closed:
                await ws.close()

    async def pump_stderr():
        try:
            async for raw in proc.stderr:
                s = raw.decode("utf-8", "replace").rstrip()
                if s:
                    await _send(ws, {"t": "stderr", "d": s})
        except Exception:
            pass

    out_task = asyncio.create_task(pump_stdout())
    err_task = asyncio.create_task(pump_stderr())

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
            if obj.get("type") == "input":
                payload = {
                    "type": "user",
                    "message": {"role": "user", "content": obj.get("text", "")},
                }
                try:
                    proc.stdin.write((json.dumps(payload) + "\n").encode("utf-8"))
                    await proc.stdin.drain()
                except Exception:
                    break
    finally:
        try:
            proc.stdin.close()
        except Exception:
            pass
        try:
            proc.terminate()
        except Exception:
            pass
        out_task.cancel()
        err_task.cancel()

    return ws


async def _send(ws: web.WebSocketResponse, obj: dict) -> bool:
    try:
        await ws.send_str(json.dumps(obj))
        return True
    except Exception:
        return False


def _qint(request: web.Request, key: str, default: int) -> int:
    try:
        return int(request.query.get(key, default))
    except (ValueError, TypeError):
        return default


# ─── Static files (GET-only, traversal-guarded) ────────────────────────────

async def static_handler(request: web.Request) -> web.StreamResponse:
    rel = request.match_info.get("path", "") or "index.html"
    root = SWITCHBOARD_DIR.resolve()
    target = (root / rel).resolve()
    if root != target and root not in target.parents:
        return web.Response(status=403, text="forbidden")
    if target.is_dir():
        target = target / "index.html"
    if not target.is_file():
        return web.Response(status=404, text="not found")
    return web.FileResponse(target)


def build_app() -> web.Application:
    app = web.Application()
    app.router.add_get("/pty", pty_handler)
    app.router.add_get("/chat", chat_handler)
    app.router.add_get("/", static_handler)
    app.router.add_get("/{path:.*}", static_handler)
    return app


if __name__ == "__main__":
    print(f"switchboard server on http://localhost:{PORT}/?live=1")
    print(f"  static root : {SWITCHBOARD_DIR}")
    print(f"  PTY cwd     : {BRAIN_ROOT}")
    web.run_app(build_app(), host="127.0.0.1", port=PORT, print=None)
