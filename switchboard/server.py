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

    Session persistence (S060): a fresh connection mints a new session uuid and
    spawns `claude … --session-id <uuid>`. A reconnect that carries `?resume=<id>`
    (a valid uuid) instead spawns `claude … --resume <id>`, continuing that
    session from its on-disk transcript — so a browser reload that lost the
    in-memory conversation can pick the same thread back up. claude saves
    sessions to disk by default (we never pass --no-session-persistence), so the
    process being gone is fine: --resume reloads context from disk. The transcript
    is NOT re-emitted as events on resume — the client owns replaying the visible
    history; the server just reattaches the live process to the same id.

    Wire protocol:
      server → client : {"t":"session","sessionId","sid8","resumed":<bool>} once,
                        then {"t":"event","ev":<claude stream-json event>},
                        {"t":"stderr","d"}, {"t":"exit","code"}.
      client → server : {"type":"input","text":<user message>}.
    """
    ws = web.WebSocketResponse(heartbeat=30)
    await ws.prepare(request)

    # `?resume=<uuid>` continues an existing session; otherwise mint a fresh one.
    # Validate as a real uuid before handing it to a subprocess arg (defensive
    # even on localhost) — a malformed value silently falls back to a fresh id.
    resume = request.query.get("resume", "").strip()
    if resume and _is_uuid(resume):
        session_id = resume
        resumed = True
    else:
        session_id = str(uuid.uuid4())
        resumed = False
    sid8 = session_id[:8]
    await _send(ws, {"t": "session", "sessionId": session_id, "sid8": sid8, "resumed": resumed})

    args = [
        CLAUDE_EXE, "-p",
        "--input-format", "stream-json",
        "--output-format", "stream-json",
        "--include-partial-messages",
        "--verbose",
        "--permission-mode", "bypassPermissions",
    ]
    args += ["--resume", session_id] if resumed else ["--session-id", session_id]
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

    async def send_stdin(payload: dict) -> bool:
        """Write one stream-json line to claude's stdin."""
        try:
            proc.stdin.write((json.dumps(payload) + "\n").encode("utf-8"))
            await proc.stdin.drain()
            return True
        except Exception:
            return False

    interrupt_seq = 0    # per-connection control_request id counter

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
                ok = await send_stdin({
                    "type": "user",
                    "message": {"role": "user", "content": obj.get("text", "")},
                })
                if not ok:
                    break
            elif kind == "interrupt":
                # Cancel the running turn without killing the process — claude
                # acks control_response{success} and stays alive for the next
                # message, so the conversation continues (probed live by the
                # terminal.js author, 3b367751). Best-effort: a failed write
                # means the pipe is already gone and the next input will break.
                interrupt_seq += 1
                await send_stdin({
                    "type": "control_request",
                    "request_id": f"int_{interrupt_seq}",
                    "request": {"subtype": "interrupt"},
                })
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


def _is_uuid(s: str) -> bool:
    """True if `s` parses as a UUID — gates the --resume arg and history lookup."""
    try:
        uuid.UUID(s)
        return True
    except (ValueError, TypeError, AttributeError):
        return False


def _is_sid8(s: str) -> bool:
    """True for an 8-char hex session prefix — the id form switchboard rows
    carry. Lets the chat panel open a session it only knows by sid8 (e.g. a
    VS Code session clicked on the board)."""
    return len(s) == 8 and all(c in "0123456789abcdefABCDEF" for c in s)


# ─── Session transcript → history replay (S060, option B) ───────────────────
#
# claude writes every session to ~/.claude/projects/<slug>/<session-id>.jsonl as
# it runs. /history parses that file into the visual turns the chat UI renders —
# so the browser persists only *which* sessions were open (their ids), never the
# transcript itself; the conversation content is re-read from disk on demand.
# This is what makes a page reload lossless without a parallel client-side copy.

PROJECTS_DIR = Path.home() / ".claude" / "projects"
HISTORY_RESULT_CAP = 4000   # per tool result, to bound the /history payload


def _find_session_file(key: str):
    """Locate a session transcript under any project dir, by full uuid OR by an
    8-char sid8 prefix (board rows only carry the sid8). The caller validates
    `key` as uuid/hex, so the glob can't escape PROJECTS_DIR."""
    try:
        return next(iter(PROJECTS_DIR.glob(f"*/{key}*.jsonl")), None)
    except OSError:
        return None


def _result_text(content) -> str:
    """Flatten a tool_result `content` (str | list-of-blocks | dict) to text —
    mirrors the client's toolResultText so history matches the live render."""
    if isinstance(content, str):
        text = content
    elif isinstance(content, list):
        text = "\n".join(
            b if isinstance(b, str) else (b.get("text", "") if isinstance(b, dict) else "")
            for b in content
        )
    elif isinstance(content, dict):
        text = content.get("text", "") or json.dumps(content)
    elif content is None:
        text = ""
    else:
        text = str(content)
    if len(text) > HISTORY_RESULT_CAP:
        text = text[:HISTORY_RESULT_CAP] + " …(truncated)"
    return text


def parse_transcript(key: str):
    """Read a session's .jsonl into {sessionId, title, turns}. `key` is a full
    uuid or an 8-char sid8; the returned sessionId is always the resolved full
    uuid (from the filename) so the client can resume with it. Returns None if no
    file is found. Turns are visual turns (one bubble each): consecutive assistant
    records merge until a real user message; tool_result user records fill their
    tool card in place rather than starting a turn; sub-agent (isSidechain)
    records are skipped so dwarf chatter stays out of the view."""
    path = _find_session_file(key)
    if path is None:
        return None
    session_id = path.stem   # full uuid, recovered from the filename

    turns = []
    title = None
    cur_asst = None             # open assistant turn, or None
    tool_index = {}             # tool_use_id → tool block (to fill its result later)

    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except ValueError:
                continue          # partial last line on a live file — skip

            t = r.get("type")
            if t == "ai-title":
                title = r.get("aiTitle") or title
                continue
            if r.get("isSidechain") is True:
                continue
            if t not in ("user", "assistant"):
                continue

            content = (r.get("message") or {}).get("content")

            if t == "user":
                user_text = []
                if isinstance(content, str):
                    user_text.append(content)
                elif isinstance(content, list):
                    for b in content:
                        if not isinstance(b, dict):
                            continue
                        if b.get("type") == "tool_result":
                            tb = tool_index.get(b.get("tool_use_id"))
                            if tb is not None:
                                tb["result"] = _result_text(b.get("content"))
                                tb["isError"] = bool(b.get("is_error"))
                        elif b.get("type") == "text":
                            user_text.append(b.get("text", ""))
                joined = "\n".join(p for p in user_text if p).strip()
                if joined:                       # a real typed message starts a turn
                    cur_asst = None
                    turns.append({"role": "user", "blocks": [{"t": "text", "text": joined}]})
                # tool_result-only user records keep the assistant turn open

            else:  # assistant
                if cur_asst is None:
                    cur_asst = {"role": "assistant", "blocks": []}
                    turns.append(cur_asst)
                for b in (content or []):
                    if not isinstance(b, dict):
                        continue
                    bt = b.get("type")
                    if bt == "text":
                        txt = b.get("text") or ""
                        if txt:
                            cur_asst["blocks"].append({"t": "text", "text": txt})
                    elif bt == "thinking":
                        th = b.get("thinking") or ""
                        if th.strip():            # empty/redacted thinking → skip
                            cur_asst["blocks"].append({"t": "thinking", "text": th})
                    elif bt == "tool_use":
                        inp = b.get("input")
                        tb = {
                            "t": "tool",
                            "id": b.get("id"),
                            "name": b.get("name") or "tool",
                            "input": inp if isinstance(inp, (dict, list)) else {},
                            "result": None,
                            "isError": False,
                        }
                        cur_asst["blocks"].append(tb)
                        if tb["id"]:
                            tool_index[tb["id"]] = tb

    return {"sessionId": session_id, "title": title, "turns": turns}


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


async def history_handler(request: web.Request) -> web.Response:
    """GET /history?session=<uuid> → the session's transcript as visual turns.
    Read-only; the parse runs in a thread so a big .jsonl doesn't stall the loop."""
    sid = request.query.get("session", "").strip()
    if not (_is_uuid(sid) or _is_sid8(sid)):
        return web.json_response({"error": "invalid session id"}, status=400)
    loop = asyncio.get_running_loop()
    data = await loop.run_in_executor(None, parse_transcript, sid)
    if data is None:
        return web.json_response(
            {"error": "not found", "sessionId": sid, "title": None, "turns": []},
            status=404,
        )
    return web.json_response(data)


def build_app() -> web.Application:
    app = web.Application()
    app.router.add_get("/pty", pty_handler)
    app.router.add_get("/chat", chat_handler)
    app.router.add_get("/history", history_handler)
    app.router.add_get("/", static_handler)
    app.router.add_get("/{path:.*}", static_handler)
    return app


if __name__ == "__main__":
    print(f"switchboard server on http://localhost:{PORT}/?live=1")
    print(f"  static root : {SWITCHBOARD_DIR}")
    print(f"  PTY cwd     : {BRAIN_ROOT}")
    web.run_app(build_app(), host="127.0.0.1", port=PORT, print=None)
