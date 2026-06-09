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
# The GitHub workspace (parent of brain) — the click-to-open boundary. Brain plus
# its sibling repos (bi-analytics-main, shipping-agent, …) live here, so a report
# path emitted by a player session resolves regardless of which repo it's in.
WORKSPACE_ROOT = BRAIN_ROOT.parent
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

# S139 taxonomy. The board has a small set of MAIN statuses (the primary chip)
# and demotes liveness + secondary detail to SUB-bubbles. Rituals (alching /
# bankstanding) are promoted to main statuses; idle / stalled are demoted to
# sub-bubbles (a quiet row keeps its real main status + a sub, never relabels).
# Precedence (ball-state wins over ritual): ACTION NEEDED > YOUR MOVE > WRAPPING
# UP > ALCHING/BANKSTANDING > BUSY — so an urgent question is never buried under
# a ritual label. The ritual then rides as a sub-bubble on the ball-state chip.
MAIN_RANK = {
    "needs_you": 0,      # ACTION NEEDED
    "your_move": 1,      # YOUR MOVE
    "closing": 2,        # WRAPPING UP (mid-wrap) — per the documented precedence
    "alching": 3,        # ALCHING
    "bankstanding": 3,   # BANKSTANDING
    "busy": 4,           # BUSY
    "done": 8,           # WRAPPED UP (finished, lingering) — sinks below live work
    "ended": 9,
    "unknown": 10,
}
IDLE_SINK_RANK = 7       # an idle (quiet-parked) row sinks below live work

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

# A `busy` session whose action heartbeat freezes past this window is escalated
# to `stalled` (S134) — the crash / reopened-cockpit signal. Set GENEROUSLY: the
# heartbeat (max of last_event_ts and the latest state.ndjson action) ticks on
# every tool call, so only a single very long model generation or a genuinely
# wedged turn freezes it. The S083 lesson (a 90s busy→idle decay false-tripped
# live analytical turns) is why this is 15 min, not minutes — and why it escalates
# to a still-surfaced STALLED chip rather than greying/hiding the row. The board's
# rule is: a busy row never silently loses its highlight (it relabels, never dims).
STALL_AFTER_SEC = 900
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
HISTORY_LIST_CAP = 150      # /api/history: most-recent sessions returned
HISTORY_SCAN_LINES = 80     # lines head-scanned per file for title/first-prompt
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
        # Foreground crew still out → never `your_move` (S139). A Stop stamps
        # `your_move` (turn parked), but if the session spawned foreground
        # subagents that haven't returned, the turn is waiting on its *crew*, not
        # on the principal — the hook can't see that (the subagent→busy logic only
        # runs on the Task Pre/Post events, so a Stop firing mid-spawn wins). The
        # board already draws crew chips from this same pending list, so the
        # invariant is: a row with crew out can't read ball-in-your-court. Keep it
        # busy (and tagged crew below); it re-derives to your_move the poll after
        # the last subagent returns and `pending` empties. Trusts the same source
        # as the crew chip — a stale/orphaned trace would mislabel here exactly as
        # it already would the chip (reap via tools/reap.py); busy>STALL still
        # backstops a genuinely wedged row into `stalled`.
        pending = _pending_subagents(s.get("session_id"))
        if state == "your_move" and pending:
            state = "busy"
        # Liveness sub-flags (S139 — the S134 relabel is GONE). A quiet row keeps
        # its real semantic state and gets a sub-bubble, instead of being
        # relabelled to a main IDLE/STALLED chip:
        #   your_move quiet past IDLE_AFTER_SEC  → `idle` sub   (un-returned park)
        #   busy      quiet past STALL_AFTER_SEC → `stalled` sub (heartbeat frozen:
        #                                          crashed, or a reopened cockpit)
        # needs_you never goes quiet-flagged — a live mid-turn block stays hot.
        is_idle = state == "your_move" and quiet_sec > IDLE_AFTER_SEC
        # A `monitoring` row (the hook flipped a bg-task wait from your_move→busy,
        # S141) is intentionally quiet — it's waiting on a detached shell/monitor,
        # not a frozen heartbeat — so it must NOT escalate to `stalled`.
        is_stalled = (state == "busy" and quiet_sec > STALL_AFTER_SEC
                      and "monitoring" not in (s.get("tags") or []))

        # Flavor flags off the hook's `.mode` tags (+ crew from the live pending
        # list). Rituals: alching/bankstanding promote to a MAIN chip; consultation/
        # drafts stay sub-bubbles. (S134/S139)
        hook_tags = set(s.get("tags") or [])
        alching = "alching" in hook_tags
        bankstanding = "bankstanding" in hook_tags
        consultation = "consultation" in hook_tags
        drafts = "drafts" in hook_tags
        # Mid-wrap: close-session started but not finished. Promotes to the
        # WRAPPING UP main chip below (above busy/rituals), or rides as a sub when
        # the close pauses on a ball-state (e.g. your_move waiting for a commit
        # nod). The finished state is `done` → WRAPPED UP, set via the wrapped_up
        # marker. (S141 — finishes the two-phase the close rituals always documented.)
        closing = "closing" in hook_tags

        # MAIN status (the primary chip) — ball-state wins over ritual (S139):
        # ACTION NEEDED > YOUR MOVE > WRAPPING UP > ALCHING/BANKSTANDING > BUSY.
        # An urgent question/park is never buried under a ritual label; the ritual
        # rides as a sub-bubble in that case.
        if state == "needs_you":
            main = "needs_you"
        elif state == "your_move":
            main = "your_move"
        elif state in ("done", "ended"):
            main = state
        elif closing:
            main = "closing"
        elif alching:
            main = "alching"
        elif bankstanding:
            main = "bankstanding"
        else:
            main = "busy"

        # SUB-bubbles (secondary; can stack). Liveness first, then any ritual that
        # got demoted because a ball-state took the main chip, then the always-sub
        # rituals. Crew is shown via the kind-letter row (`subagents`), not here.
        subs: list[str] = []
        if is_idle:
            subs.append("idle")
        if is_stalled:
            subs.append("stalled")
        if main in ("needs_you", "your_move"):
            if closing:
                subs.append("closing")   # keep the wrap context while close waits on you
            if alching:
                subs.append("alching")
            if bankstanding:
                subs.append("bankstanding")
        if consultation:
            subs.append("consultation")
        if drafts:
            subs.append("drafts")

        # Greying: only an idle (quiet-parked) row dims — an active main never does.
        stale = is_idle
        # Sort rank follows the MAIN status, except an idle row sinks below live work.
        rank = IDLE_SINK_RANK if is_idle else MAIN_RANK.get(main, 99)
        sessions.append({
            "sid8": sid8,
            "session_id": s.get("session_id"),
            "actor": s.get("actor", "unknown"),
            "name": names.get(sid8, ""),   # /rename label (S073)
            "instance": s.get("instance", 1),
            "state": state,                # semantic state (busy/your_move/needs_you/done) — kept for compat + ping transitions
            "main": main,                  # the primary chip token (S139 taxonomy)
            "subs": subs,                  # sub-bubbles: idle / stalled / demoted-ritual / consultation / drafts (S139)
            "stale": stale,                # an idle (quiet-parked) row dims (S139)
            "quiet_sec": quiet_sec,        # seconds since the last heartbeat (for the age chip)
            "tags": subs,                  # legacy alias → subs, so any old reader still gets the flavor list
            "host": s.get("host", "unknown"),
            "age_sec": max(0, int(now - started)),
            "idle_sec": idle_sec,
            # Last action heartbeat (unix ts) — the same-status sort key: rows in
            # one state order most-recently-active first. Sent to the client so the
            # merged board (manifest + cockpit-own terminals) sorts on one axis. (S134)
            "last_action_ts": heartbeat,
            "first_prompt": s.get("first_prompt", ""),
            # Claude Code's auto-title (the VSCode session-list text); board.js
            # prefers it over first_prompt for the row subheader. Written by the
            # status-sidecar hook off the session transcript's ai-title records.
            "ai_title": s.get("ai_title", ""),
            "doing": s.get("latest_action") or s.get("subtitle") or s.get("intent") or "",
            "intent": s.get("intent", ""),
            # ACTION NEEDED + YOUR MOVE drive the pings — but an idle (quiet-parked)
            # row never counts, so a parked session can't inflate the tally (S074).
            "attention": main in ("needs_you", "your_move") and not is_idle,
            "subagents": pending,
            # Rank follows the MAIN status (S139), with an idle row sunk below
            # live work (computed above).
            "rank": rank,
        })
    # Sort: attention rank first; within a status, most-recently-active on top
    # (last_action_ts desc — the S134 fix; was age_sec asc = oldest-launched first);
    # age as the final stable tiebreaker.
    sessions.sort(key=lambda x: (x["rank"], -x["last_action_ts"], x["age_sec"]))
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


async def api_open_path(request):
    """Open a brain-repo file/folder on the host from a cockpit click (S160).

    Sibling of api_open_vscode (the server-side os.startfile click→host-action
    bridge) + api_file (the repo-scoped path-safety envelope). A path token in the
    transcript prose or the terminal grid becomes clickable; clicking it opens the
    file in its default app (HTML→browser, …) — or, with reveal=1, opens the
    containing folder in Explorer with the file selected — so you never hand-
    navigate to it.

    Path-safe: the requested path is resolved and required to sit under
    WORKSPACE_ROOT (the GitHub workspace = brain + its sibling repos), so a report
    path in a sibling repo (e.g. bi-analytics-main/NFE/…) opens too. A relative
    path is tried against the brain repo first, then the workspace; resolve()+
    relative_to rejects traversal/symlink escape outside the workspace. A trailing
    :line[:col] (the file_path:line shape) is stripped. The backend is
    127.0.0.1-bound by default, so this opens only what the local user could
    already open. Windows-only (os.startfile / explorer); a clean no-op elsewhere.
    """
    raw = (request.query.get("path") or "").strip().strip('"')
    reveal = request.query.get("reveal") in ("1", "true", "yes")
    if not raw:
        return web.json_response({"ok": False, "error": "no path"}, status=400, headers=NO_STORE)
    # Drop a trailing :line[:col] (file_path:line) and normalize separators.
    cleaned = re.sub(r":\d+(?::\d+)?$", "", raw).replace("\\", "/").strip()
    p = Path(cleaned)
    # Resolve an absolute path as-is; a relative one against the brain repo first
    # (the common cockpit/gielinor case), then the workspace (sibling repos). The
    # first candidate that exists wins; else fall back to the first for a clean 404.
    candidates = [p] if p.is_absolute() else [BRAIN_ROOT / cleaned, WORKSPACE_ROOT / cleaned]
    target = None
    for cand in candidates:
        try:
            r = cand.resolve()
        except OSError:
            continue
        if r.exists():
            target = r
            break
    if target is None:
        try:
            target = candidates[0].resolve()
        except OSError:
            return web.json_response({"ok": False, "error": "bad path"}, status=400, headers=NO_STORE)
    try:
        target.relative_to(WORKSPACE_ROOT)
    except ValueError:
        return web.json_response({"ok": False, "error": "outside workspace root"}, status=403, headers=NO_STORE)
    if not target.exists():
        return web.json_response({"ok": False, "error": "not found"}, status=404, headers=NO_STORE)
    try:
        if reveal and target.is_file():
            # explorer /select,<path> opens the folder with the file highlighted.
            # explorer returns exit 1 even on success — don't check the return code.
            import subprocess
            subprocess.run(["explorer", "/select,", str(target)])
        else:
            # A file → its default app (HTML→browser); a directory → Explorer there.
            os.startfile(str(target))  # noqa: S606 — Windows ShellExecute, repo-scoped
    except (OSError, AttributeError) as e:  # AttributeError: os.startfile is Windows-only
        return web.json_response({"ok": False, "error": str(e)}, status=500, headers=NO_STORE)
    return web.json_response({"ok": True, "path": str(target)}, headers=NO_STORE)


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


async def api_handoff(request):
    """Hand a cockpit-launched session off to the calling client: terminate the
    PTY driving it (on whatever client currently owns it), so the caller can then
    resume the conversation on its own connection. Token-gated like /pty since it
    terminates a live process. Query: ?sid8=&token=. Returns {ok, found}; found is
    False when no live cockpit PTY drives that session (a VS Code session, or one
    already gone) — the client must NOT resume then, to avoid a second writer on
    the same transcript."""
    if request.query.get("token") != request.app.get("cockpit_token"):
        return web.json_response({"ok": False, "error": "forbidden"}, status=403,
                                 headers=NO_STORE)
    sid8 = (request.query.get("sid8") or "").strip().lower()
    if not _is_sid8(sid8):
        return web.json_response({"ok": False, "error": "bad sid8"}, status=400,
                                 headers=NO_STORE)
    from ptybridge import terminate_session
    return web.json_response({"ok": True, "found": terminate_session(sid8)},
                             headers=NO_STORE)


# ─── transcript replay: .jsonl → visual turns (Phase 2) ─────────────────────

def _find_session_file(key: str):
    try:
        return next(iter(PROJECTS_DIR.glob(f"*/{key}*.jsonl")), None)
    except OSError:
        return None


def _safe_mtime(path) -> float:
    try:
        return path.stat().st_mtime
    except OSError:
        return 0.0


def _session_summary(path):
    """Cheap per-session summary for the history list — title (the ai-title
    record if present, else the first user prompt) from a bounded head-scan, so
    /api/history doesn't full-parse every transcript on disk. Returns
    (session_id, title, first_prompt) or None on read error."""
    title = None
    first_prompt = ""
    try:
        with path.open(encoding="utf-8", errors="ignore") as fh:
            for i, line in enumerate(fh):
                if i >= HISTORY_SCAN_LINES:
                    break
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
                elif not first_prompt and t == "user" and r.get("isSidechain") is not True:
                    content = (r.get("message") or {}).get("content")
                    if isinstance(content, str):
                        first_prompt = content.strip()
                    elif isinstance(content, list):
                        first_prompt = "\n".join(
                            b.get("text", "") for b in content
                            if isinstance(b, dict) and b.get("type") == "text"
                        ).strip()
                if title and first_prompt:
                    break
    except OSError:
        return None
    return path.stem, title, first_prompt


async def api_history(request):
    """All sessions on disk (~/.claude/projects), newest-first — the restore
    list behind the cockpit's history view. Read-only: each row carries the full
    session_id + sid8 + last-active mtime + a title (ai-title or first prompt) +
    any disk-backed rename. The frontend filters out sessions already live on the
    board and offers reopen (claude --resume) on the rest. Bounded to the
    most-recent HISTORY_LIST_CAP files (sorted by mtime before the head-scan, so
    cost tracks the cap, not the size of the projects dir)."""
    names = _read_json(NAMES, {})
    if not isinstance(names, dict):
        names = {}
    try:
        files = list(PROJECTS_DIR.glob("*/*.jsonl"))
    except OSError:
        files = []
    files.sort(key=_safe_mtime, reverse=True)
    out = []
    for path in files[:HISTORY_LIST_CAP]:
        summ = _session_summary(path)
        if summ is None:
            continue
        session_id, title, first_prompt = summ
        sid8 = session_id[:8]
        out.append({
            "session_id": session_id,
            "sid8": sid8,
            "last_active": _safe_mtime(path),
            "title": (title or "")[:120],
            "first_prompt": (first_prompt or "")[:200],
            "name": names.get(sid8, ""),
        })
    return web.json_response({"sessions": out}, headers=NO_STORE)


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


# Per-kind reservation for the feed window. A flat tail-of-N let high-volume
# `action` lines (tool calls fire far faster than prose) evict `say`/`intent`/
# checkpoints before the client ever sees them — so the client-side `actions`
# toggle couldn't bring the prose back; it was already gone. We instead read a
# big raw tail, then keep the most-recent slice of EACH bucket independently so
# prose survives an action flood. `think` (opt-in, off by default) gets its own
# small bucket so it can't crowd `say`. Tunables — bump if a busy fleet still
# evicts prose. (S132)
FEED_RAW_TAIL = 1500
FEED_KEEP = {"action": 110, "think": 70}   # noisy buckets — capped
FEED_KEEP_PROSE = 220                       # say / intent / picked_up / needs_you / done — protected
FEED_FINAL_CAP = 360


async def api_feed(request):
    """Merged cross-fleet stream: chat.ndjson lifecycle + comms mirrors,
    sorted by ts. Per-kind reservation keeps prose from being evicted by action
    spam; the client filters buckets on top (actions / prose / thinking)."""
    raw = _ndjson_tail(CHAT_NDJSON, FEED_RAW_TAIL)
    # Bucket by kind, newest-last preserved (raw is already chronological).
    buckets: dict = {}
    for it in raw:
        buckets.setdefault(it.get("kind") or "", []).append(it)
    items = []
    for kind, lst in buckets.items():
        cap = FEED_KEEP.get(kind, FEED_KEEP_PROSE)
        items += lst[-cap:]
    for src, path in COMMS_FILES.items():
        items += _parse_comms(path, src)
    items = [i for i in items if i.get("ts")]
    items.sort(key=lambda x: x["ts"])
    return web.json_response({"items": items[-FEED_FINAL_CAP:]}, headers=NO_STORE)


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


async def api_file(request):
    """Read a brain-repo file as text, for the brain-graph node popup (brain.js).

    Path-safe: the requested path is repo-root-relative (matches graph.json node
    ids); resolve() + relative_to(BRAIN_ROOT) rejects traversal/symlink escape, so
    only files inside the brain repo are readable. Text only, size-capped. The
    backend is 127.0.0.1-bound, so this exposes nothing the local user can't read.
    """
    rel = (request.query.get("path") or "").strip().replace("\\", "/")
    if not rel:
        return web.json_response({"ok": False, "error": "no path"}, status=400, headers=NO_STORE)
    target = (BRAIN_ROOT / rel).resolve()
    try:
        target.relative_to(BRAIN_ROOT)
    except ValueError:
        return web.json_response({"ok": False, "error": "outside brain root"}, status=403, headers=NO_STORE)
    if not target.is_file():
        return web.json_response({"ok": False, "error": "not a file"}, status=404, headers=NO_STORE)
    if target.stat().st_size > 512 * 1024:
        return web.json_response({"ok": False, "error": "too large"}, status=413, headers=NO_STORE)
    text = target.read_text(encoding="utf-8", errors="replace")
    return web.json_response({"ok": True, "path": rel, "text": text}, headers=NO_STORE)


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


# Read-only guard for the dev/preview backend (--dev). Lets you run a SECOND
# backend on another port (e.g. 8771) that reads the SAME fleet state files as
# the live cockpit on 8770 — so it mirrors the board/feed/brain map — but can
# never mutate the live fleet: /pty (spawning a real claude session) and POST
# /api/rename (writing the shared session-names file) are refused. Everything
# read-only (sessions, feed, history, file, static, clipboard) works, so you get
# a full visual preview of frontend/backend changes in isolation. No-op when not
# in dev mode (the live cockpit passes through untouched).
@web.middleware
async def _dev_guard(request, handler):
    if request.app.get("dev_mode"):
        p = request.path
        if p == "/pty" or (request.method == "POST" and p in ("/api/rename", "/api/handoff")):
            return web.json_response(
                {"ok": False, "error": "read-only dev backend: session driving + state writes are disabled"},
                status=403)
    return await handler(request)


def make_app(dev=False):
    app = web.Application(middlewares=[_dev_guard])
    app["dev_mode"] = dev
    # Per-process secret gating /pty (ptybridge reads request.app["cockpit_token"]).
    # Minted fresh each launch; baked into the served HTML by static_handler.
    app["cockpit_token"] = secrets.token_urlsafe(18)
    app.router.add_get("/api/sessions", api_sessions)
    app.router.add_get("/api/open-vscode", api_open_vscode)
    app.router.add_get("/api/open-path", api_open_path)   # click a path → open file/reveal folder (S160)
    app.router.add_post("/api/rename", api_rename)
    app.router.add_post("/api/handoff", api_handoff)  # cross-client session takeover (kill-then-resume)
    app.router.add_get("/api/feed", api_feed)
    app.router.add_get("/api/history", api_history)   # all sessions on disk → restore list (reopen via claude --resume)
    app.router.add_get("/api/clipboard", api_clipboard)
    app.router.add_post("/api/clipboard", api_clipboard_write)
    app.router.add_get("/api/file", api_file)           # brain-graph node popup (path-safe, repo-scoped)
    from ptybridge import pty_handler  # real interactive claude over a PTY (S066 B)
    app.router.add_get("/pty", pty_handler)
    app.router.add_get("/history", history_handler)
    app.router.add_get("/", static_handler)
    app.router.add_get("/{path:.*}", static_handler)
    return app


def run(port=8770, dev=False):
    mode = "DEV (read-only preview)" if dev else "LIVE"
    print(f"cockpit backend :{port}  mode={mode}  ->  http://127.0.0.1:{port}/", flush=True)
    web.run_app(make_app(dev=dev), host="127.0.0.1", port=port, print=None)


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(
        description="Cockpit backend. Default :8770 drives the live fleet; --dev runs an "
                    "isolated read-only preview (use a different --port) that mirrors the live "
                    "state but can't drive sessions or write names.")
    ap.add_argument("--port", type=int, default=8770, help="port to bind (default 8770; e.g. 8771 for a dev preview)")
    ap.add_argument("--dev", action="store_true", help="read-only preview: refuse /pty driving + /api/rename writes")
    a = ap.parse_args()
    run(port=a.port, dev=a.dev)
