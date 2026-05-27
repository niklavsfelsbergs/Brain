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
import os
import re
import secrets
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
# {sid8: label} — disk-backed session renames (S073). Written by the
# rename-intercept UserPromptSubmit hook so a session in *any* host (notably
# VSCode, which never touches the cockpit's own terminal) can relabel its
# board row. The cockpit's own terminals still use the browser-localStorage
# path in web/names.js; board.js prefers localStorage, then this, then actor.
NAMES = STATE_DIR / "state-names.json"
# The claude-focus VSCode extension's URI handler — focuses the terminal pane
# whose process appears in the session's claude_pid_chain (S037/S038).
VSCODE_FOCUS_URI = "vscode://niksis8.claude-focus/focus?sid8="
ROLE_FILES = {
    "dwarf": STATE_DIR / "state-dwarves.json",
    "gnome": STATE_DIR / "state-gnomes.json",
    "penguin": STATE_DIR / "state-penguins.json",
    "shipping-agent": STATE_DIR / "state-shipping-agents.json",
}
CHAT_NDJSON = STATE_DIR / "chat.ndjson"
COMMS_FILES = {
    "gielinor": STATE_DIR / "state-comms-gielinor.md",
    "braindead": STATE_DIR / "state-comms-braindead.md",
}

# Attention order — lower rank surfaces higher on the board. D-029 two-axis
# vocabulary: base states only; flavor (alching / crew / wrapped) rides in the
# `tags` list, not here. `stalled` sits just under the two ball-in-your-court
# states so a possible crash surfaces near the top.
STATE_RANK = {
    "needs_you": 0,
    "your_move": 1,
    "stalled": 2,
    "busy": 4,
    "idle": 7,
    "done": 8,
    "ended": 9,
    "unknown": 10,
}

# Reader-derived idle. The status sidecar deliberately never stamps "idle" — the
# hook doesn't fire while a session sits parked, so the *reader* decays a stale
# `your_move` into idle. A turn ends on Stop → your_move; once it's been quiet
# past this window it's no longer "needs you", so we drop it out of the attention
# tally. Only your_move decays (an end-of-turn park); needs_you is a live
# mid-turn question and stays hot. 5 min matches the old switchboard.
IDLE_AFTER_SEC = 300

# NOTE — do NOT re-add a timeout-based busy->idle decay here. S083 tried it
# (BUSY_IDLE_AFTER_SEC=90, for the "cancelled turn sticks at BUSY" report) and it
# FALSE-TRIPPED genuine work: a session thinking, writing a long response, or in a
# long single tool/MCP query fires no action for >90s and was wrongly flipped to
# IDLE while actively working (Jebrim's analytical turns hit this constantly).
# There is no server-side way to tell "cancelled" from "quietly working" — no hook
# fires on an Esc-interrupt. The cancel case is handled WITHOUT a timeout: the
# cockpit detects the Esc keystroke in its own terminal and clears busy->idle
# instantly (see term.js _interruptedAt / main.js termInterrupted). A busy session
# otherwise stays BUSY and only greys (not relabels) once quiet past IDLE_AFTER_SEC.

# Reserved (D-029) — NOT currently wired. The original two-axis plan derived a
# `stalled` chip for a `busy` session whose action heartbeat went silent past this
# window. S080 superseded that display-decay with stale-greying (see
# build_session_model's `stale`): the row keeps its last real state + a quiet age
# instead of being relabelled, which reads as more informative. Nothing assigns
# `stalled` today; this constant + the `stalled` STATE_RANK/label/CSS are kept so
# re-introducing a distinct STALLED signal is a one-liner if it's ever wanted.
STALL_AFTER_SEC = 300  # unused — see note above
STATE_NDJSON = STATE_DIR / "state.ndjson"

# Legacy → D-029 token aliases. A session that hasn't fired a hook since the
# vocabulary change still carries an old token in its status file; map it on
# read so the board renders correctly through the transition (it self-heals to
# the new token on the session's next event). Harmless once all sessions cycle.
LEGACY_STATE = {
    "working": "busy",
    "waiting_for_user": "your_move",
    "waiting_for_answers": "needs_you",
    "waiting_for_subagents": "busy",   # crew tag re-derives on next fire
    "alching": "busy",                 # flavor lost until next fire; state stays sane
    "wrapped_up": "done",
    "closing": "done",
}

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
# The clean-text transcript panel (term.js toggle) requests &full=1 so copied
# tool output isn't sheared at the cap above — a truncated copy is a broken copy.
# A generous ceiling still applies so one pathological result can't bloat the
# payload without bound. The read-only peek view keeps the tight default cap.
HISTORY_RESULT_CAP_FULL = 200_000


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


NAME_MAX = 40  # keep in lockstep with rename-intercept.py's NAME_MAX


def _sanitize_name(name: str) -> str:
    # Same shape as the rename hook: single line, printable, collapsed, capped.
    name = re.sub(r"\s+", " ", (name or "").replace("\r", " ").replace("\n", " ")).strip()
    name = "".join(c for c in name if c.isprintable())
    return name[:NAME_MAX].strip()


def _write_name(sid8: str, name: str) -> None:
    """Read-modify-write state-names.json — the SAME store + shape as the
    rename-intercept hook, so the board UI, /rename, and the backend all share
    one file. Empty name clears the entry (back to the bare actor label)."""
    names = _read_json(NAMES, {})
    if not isinstance(names, dict):
        names = {}
    if name:
        names[sid8] = name
    else:
        names.pop(sid8, None)
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    NAMES.write_text(json.dumps(names, indent=2), encoding="utf-8")


# ─── the one session model (Phase 1) ───────────────────────────────────────

def _pending_subagents(session_id):
    """Foreground subagents still out for a session (Pre seen, Post not yet)."""
    out = []
    if not session_id:
        return out
    for kind, path in ROLE_FILES.items():
        # Guard every level — a corrupt/truncated role file could parse to a
        # non-dict (or carry a non-dict byToolUseId), and an unguarded .items()
        # would 500 the whole /api/sessions. Mirrors the sidecar's isinstance
        # guards in _pending_subagents_by_session.
        data = _read_json(path, {})
        by_session = data.get("bySession") if isinstance(data, dict) else None
        rec = by_session.get(session_id) if isinstance(by_session, dict) else None
        by_tuid = rec.get("byToolUseId") if isinstance(rec, dict) else None
        if not isinstance(by_tuid, dict):
            continue
        for tuid, info in by_tuid.items():
            ident = info.get("id") if isinstance(info, dict) else None
            out.append({"kind": kind, "id": ident or tuid})
    return out


def _last_action_ts_map(max_bytes: int = 256_000) -> dict:
    """{sid8: latest_action_unix_ts} from a capped tail-read of state.ndjson.

    D-029 knob #3: the action heartbeat is re-read here per poll instead of
    trusting the manifest's frozen `latest_action_ts`. emit-event.py writes an
    action on EVERY tool call; status-sidecar (which rewrites the manifest)
    fires only on the tight matchers — so during an ordinary-tool working turn
    the manifest's stamp goes stale even though state.ndjson is fresh. Reading
    the stream directly is what lets `stalled` tell a wedged session from a
    busy one. Capped tail-read so ndjson growth can't crater poll latency."""
    out: dict = {}
    if not STATE_NDJSON.exists():
        return out
    try:
        with open(STATE_NDJSON, "rb") as f:
            f.seek(0, 2)
            size = f.tell()
            f.seek(max(0, size - max_bytes))
            tail = f.read().decode("utf-8", errors="ignore")
    except OSError:
        return out
    for line in tail.splitlines():
        if '"type":"action"' not in line:
            continue
        try:
            ev = json.loads(line)
        except ValueError:
            continue
        if ev.get("type") != "action":
            continue
        sid8 = (ev.get("sessionId") or "")[:8]
        if not sid8:
            continue
        ts_iso = ev.get("wallTime") or ""
        try:
            ts = datetime.datetime.fromisoformat(ts_iso).timestamp()
        except (ValueError, TypeError):
            continue
        if ts > out.get(sid8, 0):
            out[sid8] = ts
    return out


def build_session_model():
    """The single normalized model the three views project from (D-028)."""
    manifest = _read_json(MANIFEST, {"sessions": []})
    names = _read_json(NAMES, {})            # {sid8: label} — disk-backed renames (S073)
    if not isinstance(names, dict):
        names = {}
    now = time.time()
    action_ts = _last_action_ts_map()        # {sid8: latest action ts} — heartbeat (D-029)
    sessions = []
    for s in manifest.get("sessions", []):
        state = LEGACY_STATE.get(s.get("state", "unknown"), s.get("state", "unknown"))
        sid8 = s.get("sid8")
        started = s.get("started_at") or s.get("last_event_ts") or now
        last = s.get("last_event_ts") or now
        idle_sec = max(0, int(now - last))
        # Action heartbeat = freshest of last_event_ts and the latest action in
        # state.ndjson. A long real turn keeps ticking via the action stream
        # even though status-sidecar doesn't fire on ordinary tools; a wedged
        # turn freezes both. See _last_action_ts_map / STALL_AFTER_SEC.
        heartbeat = max(last, action_ts.get(sid8, 0))
        quiet_sec = max(0, int(now - heartbeat))
        # Staleness (S080). A session quiet past the threshold may not reflect
        # live reality — its hooks haven't fired recently (the cockpit was just
        # reopened, or the session is genuinely parked). Rather than FLATTEN it
        # to a generic idle/stalled — which made a reopened cockpit read all-idle
        # and erased what each session was last doing — keep the last real state
        # and mark it `stale`. The board greys a stale row and shows the quiet
        # age; the row drops out of the attention tally so a parked session never
        # inflates "N need you" (the S074 invariant); and it sinks in the sort.
        # Supersedes D-029's your_move→idle / busy→stalled display decay — same
        # intent (a quiet session reads as not-live), more informative.
        stale = quiet_sec > IDLE_AFTER_SEC
        sessions.append({
            "sid8": sid8,
            "session_id": s.get("session_id"),
            "actor": s.get("actor", "unknown"),
            "name": names.get(sid8, ""),   # /rename label (S073)
            "instance": s.get("instance", 1),
            "state": state,
            "stale": stale,                # quiet past IDLE_AFTER_SEC → grey + age, not live (S080)
            "quiet_sec": quiet_sec,        # seconds since the last heartbeat (for the stale age)
            "tags": s.get("tags", []),     # flavor: alching / crew / wrapped (D-029)
            "host": s.get("host", "unknown"),
            "age_sec": max(0, int(now - started)),
            "idle_sec": idle_sec,
            "first_prompt": s.get("first_prompt", ""),
            "doing": s.get("latest_action") or s.get("subtitle") or s.get("intent") or "",
            "intent": s.get("intent", ""),
            # The two ball-in-your-court states drive the count + the pings — but a
            # stale (not-live) row never counts, so a parked session can't inflate
            # the tally (S074 invariant preserved without flattening the state).
            "attention": state in ("needs_you", "your_move") and not stale,
            "subagents": _pending_subagents(s.get("session_id")),
            # Stale rows sink to the idle slot regardless of their last state, so
            # live sessions stay on top; the real state still shows (greyed).
            "rank": STATE_RANK.get("idle", 7) if stale else STATE_RANK.get(state, 99),
        })
    sessions.sort(key=lambda x: (x["rank"], x["age_sec"]))
    return {"generated_at": now, "sessions": sessions}


async def api_sessions(request):
    return web.json_response(build_session_model(), headers=NO_STORE)


async def api_open_vscode(request):
    """Focus a session's terminal pane in VSCode (S073).

    Fires the claude-focus extension's URI (vscode://niksis8.claude-focus/...).
    Done server-side via os.startfile rather than in-page navigation: WebView2
    won't reliably hand a vscode:// URI to the OS protocol handler, but
    ShellExecute (os.startfile) does, with no prompt. The extension matches the
    sid8 against the session's claude_pid_chain and show()s the right pane.
    """
    sid8 = (request.query.get("sid8") or "").strip().lower()
    if not _is_sid8(sid8):
        return web.json_response({"ok": False, "error": "bad sid8"}, status=400,
                                 headers=NO_STORE)
    try:
        os.startfile(VSCODE_FOCUS_URI + sid8)  # Windows: ShellExecute the URI
    except OSError as e:
        return web.json_response({"ok": False, "error": str(e)}, status=500,
                                 headers=NO_STORE)
    return web.json_response({"ok": True}, headers=NO_STORE)


async def api_rename(request):
    """Set/clear a session's board label from the board UI (double-click a row).

    Renaming is a board operation, not a session prompt — so unlike the /rename
    UserPromptSubmit hook (gated to turn boundaries; can't fire while a session
    is mid-turn), this works regardless of what the session is doing. Writes the
    same state-names.json the hook uses. Body: {sid8, name}; empty name clears.
    """
    try:
        body = await request.json()
    except (ValueError, TypeError):
        body = {}
    sid8 = (body.get("sid8") or "").strip().lower()
    if not _is_sid8(sid8):
        return web.json_response({"ok": False, "error": "bad sid8"}, status=400,
                                 headers=NO_STORE)
    name = _sanitize_name(body.get("name") or "")
    try:
        _write_name(sid8, name)
    except OSError as e:
        return web.json_response({"ok": False, "error": str(e)}, status=500,
                                 headers=NO_STORE)
    return web.json_response({"ok": True, "name": name}, headers=NO_STORE)


# ─── transcript replay: .jsonl → visual turns (Phase 2) ─────────────────────

def _find_session_file(key: str):
    try:
        return next(iter(PROJECTS_DIR.glob(f"*/{key}*.jsonl")), None)
    except OSError:
        return None


def _result_text(content, cap: int = HISTORY_RESULT_CAP) -> str:
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
    if len(text) > cap:
        text = text[:cap] + " …(truncated)"
    return text


def parse_transcript(key: str, result_cap: int = HISTORY_RESULT_CAP):
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
                                tb["result"] = _result_text(b.get("content"), result_cap)
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
    # The clean-text transcript panel passes full=1 for untruncated tool output
    # (clean copy); the read-only peek omits it and keeps the bounded default cap.
    cap = HISTORY_RESULT_CAP_FULL if request.query.get("full") else HISTORY_RESULT_CAP
    loop = asyncio.get_running_loop()
    data = await loop.run_in_executor(None, parse_transcript, sid, cap)
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


def _write_clipboard_text(text: str) -> bool:
    """Set the Windows clipboard to UTF-16 text. The mirror of _read_clipboard_text:
    the terminal's Ctrl+C copy goes through here because WebView2 gates the native
    navigator.clipboard write path. Returns False (never raises) on any non-Windows
    or API failure so the caller degrades to "copy does nothing"."""
    try:
        import ctypes
        from ctypes import wintypes
    except Exception:
        return False
    CF_UNICODETEXT = 13
    GMEM_MOVEABLE = 0x0002
    try:
        u, k = ctypes.windll.user32, ctypes.windll.kernel32
    except AttributeError:
        return False  # not Windows
    u.OpenClipboard.argtypes = [wintypes.HWND]
    u.OpenClipboard.restype = wintypes.BOOL
    u.EmptyClipboard.restype = wintypes.BOOL
    u.SetClipboardData.argtypes = [wintypes.UINT, wintypes.HANDLE]
    u.SetClipboardData.restype = wintypes.HANDLE
    u.CloseClipboard.restype = wintypes.BOOL
    k.GlobalAlloc.argtypes = [wintypes.UINT, ctypes.c_size_t]
    k.GlobalAlloc.restype = wintypes.HGLOBAL
    k.GlobalLock.argtypes = [wintypes.HGLOBAL]
    k.GlobalLock.restype = wintypes.LPVOID
    k.GlobalUnlock.argtypes = [wintypes.HGLOBAL]
    k.GlobalFree.argtypes = [wintypes.HGLOBAL]
    if not u.OpenClipboard(None):
        return False
    try:
        u.EmptyClipboard()
        buf = ctypes.create_unicode_buffer(text)  # UTF-16LE incl. trailing NUL
        size = ctypes.sizeof(buf)
        h = k.GlobalAlloc(GMEM_MOVEABLE, size)
        if not h:
            return False
        p = k.GlobalLock(h)
        if not p:
            k.GlobalFree(h)
            return False
        try:
            ctypes.memmove(p, buf, size)
        finally:
            k.GlobalUnlock(h)
        if not u.SetClipboardData(CF_UNICODETEXT, h):
            k.GlobalFree(h)  # ownership not transferred on failure
            return False
        return True  # system now owns h — must NOT free it
    finally:
        u.CloseClipboard()


async def api_clipboard_write(request):
    try:
        body = await request.json()
        text = (body or {}).get("text", "")
    except Exception:
        text = ""
    if not text:
        return web.json_response({"ok": False}, headers=NO_STORE)
    loop = asyncio.get_running_loop()
    ok = await loop.run_in_executor(None, _write_clipboard_text, text)
    return web.json_response({"ok": bool(ok)}, headers=NO_STORE)


# ─── transient terminal-fit diagnostic (issue #2: prompt below fold at open) ──
# The client (term.js._diag) posts its xterm fit/scroll geometry here so a
# relaunch + opening a session reproduces the cut-off straight to disk — no
# DevTools needed. The numbers tell H1 (over-fit: overfit>0) from H2 (scroll-
# desync: overfit~0 but viewportY/scrollTop disagree); the fix differs per case.
# STRIP this handler + its route + the term.js POST once the bug is fixed
# (S094 term-size-diag / S093 rename-diag precedent — debug-only, always-on
# while debugging). Pairs with ptybridge's server-side term-size-diag.log.
TERM_FIT_DIAG_PATH = BRAIN_ROOT / "switchboard" / "term-fit-diag.log"


async def api_termdiag(request):
    try:
        body = await request.json()
    except Exception:
        body = {}
    line = (body or {}).get("line", "")
    if line:
        try:
            with TERM_FIT_DIAG_PATH.open("a", encoding="utf-8") as f:
                f.write(f"{time.strftime('%H:%M:%S')} {line}\n")
        except Exception:
            pass
    return web.json_response({"ok": True}, headers=NO_STORE)


# ─── static files ───────────────────────────────────────────────────────────

async def static_handler(request):
    rel = request.match_info.get("path", "") or "index.html"
    target = (WEB_DIR / rel).resolve()
    if not str(target).startswith(str(WEB_DIR)) or not target.is_file():
        target = WEB_DIR / "index.html"
    ctype = CTYPES.get(target.suffix, "application/octet-stream")
    # Bake the per-process /pty token into the HTML document. A cross-origin page
    # cannot READ this response body (same-origin policy), so it can't learn the
    # token — which is exactly what gates the PTY bridge against drive-by RCE. The
    # legit page reads it from window.__CT and sends it on the /pty WS. (S085)
    if target.suffix == ".html":
        doc = target.read_text(encoding="utf-8")
        inject = f"<script>window.__CT={json.dumps(request.app.get('cockpit_token', ''))};</script>"
        doc = doc.replace("</head>", inject + "</head>", 1) if "</head>" in doc else inject + doc
        return web.Response(text=doc, content_type=ctype, headers=NO_STORE)
    return web.Response(body=target.read_bytes(), content_type=ctype, headers=NO_STORE)


def make_app():
    app = web.Application()
    # Per-process secret gating /pty (ptybridge reads request.app["cockpit_token"]).
    # Minted fresh each launch; baked into the served HTML by static_handler.
    app["cockpit_token"] = secrets.token_urlsafe(18)
    app.router.add_get("/api/sessions", api_sessions)
    app.router.add_get("/api/open-vscode", api_open_vscode)
    app.router.add_post("/api/rename", api_rename)
    app.router.add_get("/api/feed", api_feed)
    app.router.add_get("/api/clipboard", api_clipboard)
    app.router.add_post("/api/clipboard", api_clipboard_write)
    app.router.add_post("/api/termdiag", api_termdiag)  # transient (issue #2) — strip when fixed
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
