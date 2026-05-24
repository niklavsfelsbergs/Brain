"""Cockpit backend — the one session model + the agent driver.

Phase 1: reads the hook-written state files in ../switchboard/ (preserved
contracts, see D-028) and serves one shaped /api/sessions for the fleet board.

Phase 2: replays any session's on-disk transcript (/history). The live drive
path is the real interactive claude in a PTY (/pty, ptybridge.py — the S066 B
pivot, on subscription). The old headless `claude -p` /chat WS driver was
removed in S073: it was metered post-2026-06-15 and had become dead code (the
client placed every session through the PTY, never /chat).

All assets go out Cache-Control: no-store so the browser never serves stale code.
"""
from __future__ import annotations

import asyncio
import datetime
import json
import re
import shutil
import time
import uuid
from pathlib import Path

from aiohttp import web

COCKPIT_DIR = Path(__file__).resolve().parent
BRAIN_ROOT = COCKPIT_DIR.parent
STATE_DIR = BRAIN_ROOT / "switchboard"   # where the hooks write (D-026 VIZ_DIR)
WEB_DIR = COCKPIT_DIR / "web"
PROJECTS_DIR = Path.home() / ".claude" / "projects"
CLAUDE_EXE = shutil.which("claude") or "claude"

MANIFEST = STATE_DIR / "state-switchboard.json"
ROLE_FILES = {
    "dwarf": STATE_DIR / "state-dwarves.json",
    "gnome": STATE_DIR / "state-gnomes.json",
    "penguin": STATE_DIR / "state-penguins.json",
}
CHAT_NDJSON = STATE_DIR / "chat.ndjson"
COMMS_FILES = {
    "gielinor": STATE_DIR / "state-comms-gielinor.md",
    "braindead": STATE_DIR / "state-comms-braindead.md",
}

# Attention order — lower rank surfaces higher on the board.
STATE_RANK = {
    "waiting_for_answers": 0,
    "waiting_for_user": 1,
    "waiting_for_subagents": 2,
    "alching": 3,
    "working": 4,
    "wrapped_up": 6,
    "idle": 7,
    "ended": 8,
    "unknown": 9,
}

# Reader-derived idle. The status sidecar deliberately never stamps "idle" — the
# hook doesn't fire while a session sits parked, so the *reader* has to decay a
# stale waiting_for_user into idle (its docstring spells out this contract). A
# turn ends on Stop → waiting_for_user; once it's been quiet past this window
# it's no longer "needs you", so we drop it out of the attention tally + bell.
# Only waiting_for_user decays (an end-of-turn park); waiting_for_answers is a
# live mid-turn question and stays hot. 5 min matches the old switchboard.
IDLE_AFTER_SEC = 300

CTYPES = {
    ".html": "text/html",
    ".js": "text/javascript",
    ".mjs": "text/javascript",
    ".css": "text/css",
    ".json": "application/json",
    ".svg": "image/svg+xml",
    ".ico": "image/x-icon",
    ".png": "image/png",
    ".woff2": "font/woff2",
}
NO_STORE = {"Cache-Control": "no-store"}
HISTORY_RESULT_CAP = 4000   # per tool result, to bound the /history payload


def _read_json(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def _is_uuid(s: str) -> bool:
    try:
        uuid.UUID(s)
        return True
    except (ValueError, TypeError, AttributeError):
        return False


def _is_sid8(s: str) -> bool:
    return len(s) == 8 and all(c in "0123456789abcdefABCDEF" for c in s)


# ─── the one session model (Phase 1) ───────────────────────────────────────

def _pending_subagents(session_id):
    """Foreground subagents still out for a session (Pre seen, Post not yet)."""
    out = []
    if not session_id:
        return out
    for kind, path in ROLE_FILES.items():
        rec = (_read_json(path, {}).get("bySession") or {}).get(session_id)
        if not rec:
            continue
        for tuid, info in (rec.get("byToolUseId") or {}).items():
            ident = info.get("id") if isinstance(info, dict) else None
            out.append({"kind": kind, "id": ident or tuid})
    return out


def build_session_model():
    """The single normalized model the three views project from (D-028)."""
    manifest = _read_json(MANIFEST, {"sessions": []})
    now = time.time()
    sessions = []
    for s in manifest.get("sessions", []):
        state = s.get("state", "unknown")
        started = s.get("started_at") or s.get("last_event_ts") or now
        last = s.get("last_event_ts") or now
        idle_sec = max(0, int(now - last))
        # Decay a quiet end-of-turn park into idle (see IDLE_AFTER_SEC). Done
        # here, after idle_sec is known, so the attention flag + rank below read
        # the decayed state — a finished-but-open session stops counting as
        # "needs you".
        if state == "waiting_for_user" and idle_sec > IDLE_AFTER_SEC:
            state = "idle"
        sessions.append({
            "sid8": s.get("sid8"),
            "session_id": s.get("session_id"),
            "actor": s.get("actor", "unknown"),
            "instance": s.get("instance", 1),
            "state": state,
            "host": s.get("host", "unknown"),
            "age_sec": max(0, int(now - started)),
            "idle_sec": idle_sec,
            "first_prompt": s.get("first_prompt", ""),
            "doing": s.get("latest_action") or s.get("subtitle") or s.get("intent") or "",
            "intent": s.get("intent", ""),
            "attention": state in ("waiting_for_user", "waiting_for_answers"),
            "subagents": _pending_subagents(s.get("session_id")),
            "rank": STATE_RANK.get(state, 99),
        })
    sessions.sort(key=lambda x: (x["rank"], x["age_sec"]))
    return {"generated_at": now, "sessions": sessions}


async def api_sessions(request):
    return web.json_response(build_session_model(), headers=NO_STORE)


# ─── transcript replay: .jsonl → visual turns (Phase 2) ─────────────────────

def _find_session_file(key: str):
    try:
        return next(iter(PROJECTS_DIR.glob(f"*/{key}*.jsonl")), None)
    except OSError:
        return None


def _result_text(content) -> str:
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
    """Read a session's .jsonl into {sessionId, title, turns}. Visual turns:
    consecutive assistant records merge until a real user message; tool_result
    user records fill their tool card in place; sub-agent (isSidechain) records
    are skipped. Mirrors the old switchboard parser so live + replay match."""
    path = _find_session_file(key)
    if path is None:
        return None
    session_id = path.stem
    turns, title, cur_asst, tool_index = [], None, None, {}
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except ValueError:
                continue
            t = r.get("type")
            if t == "ai-title":
                title = r.get("aiTitle") or title
                continue
            if r.get("isSidechain") is True or t not in ("user", "assistant"):
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
                if joined:
                    cur_asst = None
                    turns.append({"role": "user", "blocks": [{"t": "text", "text": joined}]})
            else:
                if cur_asst is None:
                    cur_asst = {"role": "assistant", "blocks": []}
                    turns.append(cur_asst)
                for b in (content or []):
                    if not isinstance(b, dict):
                        continue
                    bt = b.get("type")
                    if bt == "text" and (b.get("text") or ""):
                        cur_asst["blocks"].append({"t": "text", "text": b["text"]})
                    elif bt == "thinking" and (b.get("thinking") or "").strip():
                        cur_asst["blocks"].append({"t": "thinking", "text": b["thinking"]})
                    elif bt == "tool_use":
                        inp = b.get("input")
                        tb = {"t": "tool", "id": b.get("id"), "name": b.get("name") or "tool",
                              "input": inp if isinstance(inp, (dict, list)) else {},
                              "result": None, "isError": False}
                        cur_asst["blocks"].append(tb)
                        if tb["id"]:
                            tool_index[tb["id"]] = tb
    return {"sessionId": session_id, "title": title, "turns": turns}


async def history_handler(request):
    sid = request.query.get("session", "").strip()
    if not (_is_uuid(sid) or _is_sid8(sid)):
        return web.json_response({"error": "invalid session id"}, status=400, headers=NO_STORE)
    loop = asyncio.get_running_loop()
    data = await loop.run_in_executor(None, parse_transcript, sid)
    if data is None:
        return web.json_response({"error": "not found", "sessionId": sid, "title": None,
                                  "turns": []}, status=404, headers=NO_STORE)
    return web.json_response(data, headers=NO_STORE)


# ─── the activity feed: lifecycle stream + comms (Phase 4) ──────────────────

def _ndjson_tail(path, limit):
    out = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()[-limit:]
    except OSError:
        return out
    for ln in lines:
        try:
            r = json.loads(ln)
        except ValueError:
            continue
        out.append({"ts": r.get("ts"), "kind": r.get("kind"), "actor": r.get("actor"),
                    "sid8": r.get("sid8"), "text": r.get("text", ""), "source": "ndjson"})
    return out


_COMMS_HEAD = re.compile(r"^\[([^\]]+)\]\s+([a-z]+)(?:-([0-9a-f]{8}))?\s+(.+)$")
_COMMS_DATE = re.compile(r"(\d{4}-\d{2}-\d{2})(?:\s+(\d{1,2}:\d{2}))?")


def _comms_ts(s):
    m = _COMMS_DATE.search(s)
    if not m:
        return 0
    stamp = f"{m.group(1)} {m.group(2) or '00:00'}"
    try:
        return datetime.datetime.strptime(stamp, "%Y-%m-%d %H:%M").timestamp()
    except ValueError:
        return 0


def _parse_comms(path, source, limit=25):
    """Best-effort parse of a comms mirror into feed items (header + first body
    line). Timestamps are coarse (date, sometimes +HH:MM) — fine for ordering."""
    items, cur = [], None
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return items
    for line in text.splitlines():
        h = _COMMS_HEAD.match(line)
        if h:
            if cur:
                items.append(cur)
            cur = {"ts": _comms_ts(h.group(1)), "kind": "comms",
                   "subkind": h.group(4).split()[0][:14], "actor": h.group(2),
                   "sid8": h.group(3), "text": "", "source": source}
        elif cur is not None and line.strip() and not cur["text"]:
            cur["text"] = line.strip()[:200]
    if cur:
        items.append(cur)
    return items[-limit:]


async def api_feed(request):
    """Merged cross-fleet stream: chat.ndjson lifecycle + comms mirrors,
    sorted by ts. The client filters raw actions off by default."""
    items = _ndjson_tail(CHAT_NDJSON, 250)
    for src, path in COMMS_FILES.items():
        items += _parse_comms(path, src)
    items = [i for i in items if i.get("ts")]
    items.sort(key=lambda x: x["ts"])
    return web.json_response({"items": items[-300:]}, headers=NO_STORE)


# ─── clipboard bridge ────────────────────────────────────────────────────────
# The terminal runs in WebView2 (pywebview), where the native Ctrl+V → paste-event
# path through xterm's textarea is unreliable and navigator.clipboard.readText()
# is permission-gated. The cockpit is bound to 127.0.0.1 and runs as a desktop
# app, so the *server's* clipboard is the user's clipboard — read it here and hand
# it to term.js, which feeds it through term.paste(). Windows-only via ctypes; any
# failure returns "" so a non-Windows host degrades to "paste does nothing."

def _read_clipboard_text() -> str:
    try:
        import ctypes
        from ctypes import wintypes
    except Exception:
        return ""
    CF_UNICODETEXT = 13
    try:
        u, k = ctypes.windll.user32, ctypes.windll.kernel32
    except AttributeError:
        return ""  # not Windows
    u.OpenClipboard.argtypes = [wintypes.HWND]
    u.OpenClipboard.restype = wintypes.BOOL
    u.GetClipboardData.argtypes = [wintypes.UINT]
    u.GetClipboardData.restype = wintypes.HANDLE
    u.CloseClipboard.restype = wintypes.BOOL
    k.GlobalLock.argtypes = [wintypes.HGLOBAL]
    k.GlobalLock.restype = wintypes.LPVOID
    k.GlobalUnlock.argtypes = [wintypes.HGLOBAL]
    if not u.OpenClipboard(None):
        return ""
    try:
        h = u.GetClipboardData(CF_UNICODETEXT)
        if not h:
            return ""
        p = k.GlobalLock(h)
        if not p:
            return ""
        try:
            return ctypes.c_wchar_p(p).value or ""
        finally:
            k.GlobalUnlock(h)
    finally:
        u.CloseClipboard()


async def api_clipboard(request):
    loop = asyncio.get_running_loop()
    text = await loop.run_in_executor(None, _read_clipboard_text)
    return web.json_response({"text": text}, headers=NO_STORE)


# ─── static files ───────────────────────────────────────────────────────────

async def static_handler(request):
    rel = request.match_info.get("path", "") or "index.html"
    target = (WEB_DIR / rel).resolve()
    if not str(target).startswith(str(WEB_DIR)) or not target.is_file():
        target = WEB_DIR / "index.html"
    ctype = CTYPES.get(target.suffix, "application/octet-stream")
    return web.Response(body=target.read_bytes(), content_type=ctype, headers=NO_STORE)


def make_app():
    app = web.Application()
    app.router.add_get("/api/sessions", api_sessions)
    app.router.add_get("/api/feed", api_feed)
    app.router.add_get("/api/clipboard", api_clipboard)
    from ptybridge import pty_handler  # real interactive claude over a PTY (S066 B)
    app.router.add_get("/pty", pty_handler)
    app.router.add_get("/history", history_handler)
    app.router.add_get("/", static_handler)
    app.router.add_get("/{path:.*}", static_handler)
    return app


def run(port=8770):
    web.run_app(make_app(), host="127.0.0.1", port=port, print=None)


if __name__ == "__main__":
    run()
