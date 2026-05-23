#!/usr/bin/env python3
# Terminal switchboard status sidecar (D-020).
#
# Writes ~/.claude/status/<sid8>.json on every UserPromptSubmit, PreToolUse,
# PostToolUse, Stop, and SessionEnd. The file records the session's current
# state (working / waiting_for_user / ended) so an aggregator view can show
# which terminals are idle, working, or parked on a Stop waiting for the
# principal.
#
# Idle is *not* stamped by this writer — readers derive it from
# `state == "waiting_for_user" AND now - last_event_ts > 5 min`. The hook
# doesn't fire while idle, so writer-side stamping would require either
# polling or a timer.
#
# Never fails the tool call — any error is swallowed to stderr.
#
# Sibling of emit-event.py. Kept separate so visualizer logic and switchboard
# logic have isolated failure modes; both register independently in
# brain/.claude/settings.json.

import json
import os
import sys
import time
from pathlib import Path
from typing import Optional

# User-global so a single switchboard view sees every Claude Code session on
# the machine, regardless of which repo opened them. See D-020 §"The contract"
# for why per-project was rejected.
STATUS_DIR = Path.home() / ".claude" / "status"
STATUS_ARCHIVE_DIR = STATUS_DIR / "archive"

# Phase 2 (D-020): the browser-served visualizer can't reach STATUS_DIR
# directly (file:// + served-tree sandboxing), so the sidecar mirrors a
# manifest snapshot into the viz dir on every fire. The browser fetches one
# file at a known relative path; no custom server or symlink needed.
#
# HERE = .../brain/developer-braindead/.claude/hooks/status-sidecar.py
# HERE.parent.parent.parent = .../brain/developer-braindead/
# We derive the viz dir from the script's own location rather than the
# session's CLAUDE_PROJECT_DIR — the hook is registered under brain, so the
# brain-local viz path is always the right mirror target regardless of which
# repo the session was opened in.
HERE = Path(__file__).resolve()
DEV_BRAIN = HERE.parent.parent.parent
# S052: visualizer promoted to switchboard/ (brain root).
VIZ_DIR = DEV_BRAIN.parent / "switchboard"
MANIFEST_PATH = VIZ_DIR / "state-switchboard.json"
INSTANCES_PATH = VIZ_DIR / "state-instances.json"
ACTORS_PATH = VIZ_DIR / "state-actors.json"
# Sub-agent role-state files (written by emit-event.py). Read here to derive
# the "awaiting crew" state — a session with in-flight foreground spawns is
# blocked waiting for its dwarves/gnomes/penguins to return.
SUBAGENT_STATE_PATHS = (
    VIZ_DIR / "state-dwarves.json",
    VIZ_DIR / "state-gnomes.json",
    VIZ_DIR / "state-penguins.json",
)
# S052: chat-stream sidecar — mirrors the path emit-event.py writes to.
CHAT_PATH = VIZ_DIR / "chat.ndjson"
CHAT_TEXT_MAX = 320          # S058: was 200 — headroom above the 280 intent cap.
CHAT_SIZE_MAX = 1_000_000
CHAT_LINES_MAX = 5000
CHAT_TAIL_KEEP = 2000
# Subtitle freshness — intent_text wins as the subtitle when updated within
# this window, else latest_action prevails.
SUBTITLE_INTENT_FRESH_SEC = 300
SUBTITLE_MAX_LEN = 280       # S058: was 100 — longer in-voice narration (2–3×).

# S043 (D-024 visualizer wiring): mirror both comms channels into the viz dir
# so the COMMS panel can render inter-session dialogue. Same sandbox reason as
# state-switchboard.json — the browser cannot fetch outside the server root.
BRAIN_ROOT = DEV_BRAIN.parent
COMMS_MIRRORS = (
    (BRAIN_ROOT / "gielinor" / "comms" / "active.md", VIZ_DIR / "state-comms-gielinor.md"),
    (BRAIN_ROOT / "developer-braindead" / "comms" / "active.md", VIZ_DIR / "state-comms-braindead.md"),
)

# A session counts as "live" for GC purposes if its status file exists, isn't
# ended, and fired a hook within this window. Tight enough to GC promptly when
# Claude Code crashes (SessionEnd never fires); loose enough that a session
# parked on a Stop for a long lunch doesn't get its sprite swept. The sidebar's
# own idle threshold is 5 min — GC sits an order of magnitude beyond that so
# the two judgments don't collide.
LIVE_SESSION_SEC = 60 * 60

# Same intent length cap as the visualizer hook so a sidebar can render
# sidecar intent inline without re-truncating.
# S058: was 100 — bumped to 280 so in-voice intent lines run 2–3× longer and the
# COMMS feed/subtitle actually narrate what's happening. Keep emit-event.py's
# INTENT_MAX_LEN in lockstep.
INTENT_MAX_LEN = 280

# Reader-derives-idle threshold — 5 min matches the visualizer despawn timer.
# Carried here only for documentation; the writer never reads it.
# IDLE_SEC = 300

# Sweeper threshold — entries older than this move to archive/ on the next
# hook fire from any session. 24h gives plenty of room for slow-cadence
# sessions while keeping the active list scannable.
STALE_SEC = 24 * 60 * 60

# Hook events we care about, mapped to the state they imply. Anything not in
# this map is ignored — the script exits silently.
EVENT_STATE = {
    "UserPromptSubmit": "working",
    "PreToolUse": "working",
    "PostToolUse": "working",
    "Stop": "waiting_for_user",
    "SessionEnd": "ended",
}

# Interactive prompt tools park the session on the principal mid-turn (no Stop
# fires) → waiting_for_user. Sub-agent spawners block the session on its crew
# until the foreground Task returns → waiting_for_subagents ("AWAITING CREW").
# Both are registered with a tight Pre/Post matcher in settings.json so the
# fire-budget impact is ~0-2 per session each, not per tool call.
WAIT_TOOLS = {"AskUserQuestion", "ExitPlanMode"}
SUBAGENT_TOOLS = {"Task", "Agent"}


def _project_dir() -> Path | None:
    """Returns the project root from CLAUDE_PROJECT_DIR (set by Claude Code
    for every hook invocation). None if unset — without it we can't find the
    intent files."""
    p = os.environ.get("CLAUDE_PROJECT_DIR")
    if not p:
        return None
    try:
        return Path(p).resolve()
    except Exception:
        return None


def _actor_from_instances(session_id_full: str) -> str:
    """Read state-instances.json and find which actor's byId map registered
    this session. Used as a fallback when no intent file exists for the
    session — emit-event.py registers an instance for every action it
    attributes to an actor, so any session that's done any work will have an
    entry here even if it never wrote intent narration.

    Returns "" if no match or multiple ambiguous matches. The multi-match
    case picks the actor with the highest instance number — newer = more
    recently allocated = more likely to be the current actor — which is a
    heuristic that handles mid-session player switches without timestamps."""
    try:
        state = json.loads(INSTANCES_PATH.read_text(encoding="utf-8"))
    except Exception:
        return ""
    candidates: list[tuple[int, str]] = []
    for actor_name, entry in (state or {}).items():
        if not isinstance(entry, dict):
            continue
        by_id = entry.get("byId") or {}
        v = by_id.get(session_id_full)
        if v is None:
            continue
        try:
            inst = int(v)
        except (TypeError, ValueError):
            inst = 0
        candidates.append((inst, actor_name))
    if not candidates:
        return ""
    candidates.sort(reverse=True)
    return candidates[0][1]


def _detect_actor(project_dir: Path | None, sid8: str, session_id_full: str = "") -> tuple[str, str]:
    """Resolve `(actor, intent_first_line)` for a session, in priority order:

    1. Exactly one intent file `<actor>-<sid8>.txt` in the project's intent
       dir → that actor + the file's first line as intent.
    2. Multiple intent files → newest by mtime wins. Covers the window
       between a mid-session player switch and the mini-respawn's intent
       archive step (or the next periodic GC sweep).
    3. No intent file → fall back to `state-instances.json` byId lookup
       (`_actor_from_instances`). emit-event.py registers an instance on
       every action, so any session that's done any work is reachable from
       here even when intent narration is missing.
    4. Nothing matches anywhere → ("unknown", "").

    Empty `session_id_full` skips step 3 (the lookup needs the full id; sid8
    isn't enough). Callers that have only sid8 still benefit from steps 1+2.
    """
    if not project_dir:
        return ("unknown", "")
    intent_dir = project_dir / ".claude" / "intent"
    matches: list[tuple[str, Path, float]] = []
    if intent_dir.exists():
        try:
            for p in intent_dir.glob(f"*-{sid8}.txt"):
                if not p.is_file():
                    continue
                name = p.stem
                if not name.endswith(f"-{sid8}"):
                    continue
                actor = name[:-(len(sid8) + 1)]
                if not actor:
                    continue
                try:
                    mtime = p.stat().st_mtime
                except Exception:
                    mtime = 0.0
                matches.append((actor, p, mtime))
        except Exception:
            matches = []

    if matches:
        # Newest by mtime wins. Single-match case naturally collapses to the
        # one entry; multi-match takes the most recently written intent.
        matches.sort(key=lambda t: t[2], reverse=True)
        actor, p, _ = matches[0]
        try:
            raw = p.read_text(encoding="utf-8").strip()
        except Exception:
            raw = ""
        first = raw.splitlines()[0].strip()[:INTENT_MAX_LEN] if raw else ""
        return (actor, first)

    # No intent file — try the instance map as the last resort.
    if session_id_full:
        fallback = _actor_from_instances(session_id_full)
        if fallback:
            return (fallback, "")
    return ("unknown", "")


def _detect_instance(actor: str, session_id: str) -> Optional[int]:
    """S033 finding #2: read the visualizer's state-instances.json to surface
    the real instance number in the switchboard manifest. The previous
    behavior — `prev.get("instance") or 1` — meant two parallel Braindead
    sessions both rendered as 'Braindead' in the sidebar (instance 1) with
    no way to distinguish them.

    Returns `None` when we can't determine the instance positively — actor
    is non-instanced (wisp, guthix), the map can't be read, or this session
    isn't yet stamped in byId. Callers fall through to whatever prior value
    they have (S040 audit fix: the previous "return 1 on failure" version
    silently regressed real instance N→1 inside _write_manifest's per-row
    refresh, collapsing all parallel Braindeads to instance:1 in the
    sidebar). emit-event.py is the writer; this is a read-only consumer."""
    if not actor or actor in ("unknown", "wisp", "guthix"):
        return None
    try:
        state = json.loads(INSTANCES_PATH.read_text(encoding="utf-8"))
    except Exception:
        return None
    entry = state.get(actor)
    if not isinstance(entry, dict):
        return None
    by_id = entry.get("byId") or {}
    v = by_id.get(session_id)
    if v is None:
        return None
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def _detect_building(actor: str, session_id: str) -> Optional[str]:
    """Read state-actors.json to surface this session's current building, so
    the visualizer can render sprites at the right place straight from the
    manifest — no event-replay needed.

    Instanced actors (jebrim, zezima, braindead) store per-session buildings
    under `actors[actor].byId[session_id]`. Singletons (wisp, guthix) store
    their building as a top-level scalar under `actors[actor]`. Returns None
    when nothing is recorded (the visualizer falls back to the actor's
    default spawn building)."""
    if not actor or actor == "unknown":
        return None
    try:
        state = json.loads(ACTORS_PATH.read_text(encoding="utf-8"))
    except Exception:
        return None
    entry = state.get(actor)
    if isinstance(entry, dict):
        v = (entry.get("byId") or {}).get(session_id)
        return v if isinstance(v, str) and v else None
    if isinstance(entry, str) and entry:
        return entry
    return None


def _pending_subagents_by_session() -> dict:
    """Read the three sub-agent role-state files (state-dwarves/gnomes/
    penguins.json, written by emit-event.py) and return
    `{session_id: [sub_id, ...]}` of in-flight FOREGROUND spawns per session.

    Background spawns (`run_in_background`) are excluded: their PostToolUse
    fires when the parent gets its handle back, not when the work completes, so
    the parent isn't blocked on them — they shouldn't read as "awaiting crew".

    Shape consumed (D-018):
        { "nextId": N,
          "bySession": { "<session_id>": {
              "byToolUseId": { "<tui>": {"id": "D1", "background": bool, ...} },
              "pendingQueue": [ {"id": "D2", ...} ] } } }

    Both byToolUseId (the common path, tool_use_id known at Pre) and
    pendingQueue (the no-tool_use_id fallback) count. Errors per file are
    swallowed so one unreadable role file can't blank the others."""
    result: dict = {}
    for path in SUBAGENT_STATE_PATHS:
        try:
            state = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(state, dict):
            continue
        by_session = state.get("bySession")
        if not isinstance(by_session, dict):
            continue
        for sid, sub in by_session.items():
            if not isinstance(sub, dict):
                continue
            entries = list((sub.get("byToolUseId") or {}).values())
            entries += list(sub.get("pendingQueue") or [])
            ids = result.setdefault(sid, [])
            for entry in entries:
                if not isinstance(entry, dict) or entry.get("background"):
                    continue
                eid = entry.get("id")
                if eid:
                    ids.append(eid)
    # Stable, de-duplicated ordering for display (D1 D2 P1 …).
    for sid in list(result.keys()):
        result[sid] = sorted(set(result[sid]))
    return result


def _count_pending_subagents(session_id: str) -> int:
    """In-flight foreground spawn count for one session. Used by the PostToolUse
    path to decide whether a returning spawn leaves the session still awaiting
    others. Reads all three role files; cheap (files are tiny)."""
    if not session_id:
        return 0
    return len(_pending_subagents_by_session().get(session_id, []))


def _detect_host() -> str:
    """Best-effort terminal substrate detection from env. Phase 3 will use
    this to pick the focus mechanism. Unknown means "we'll figure it out
    later" — never blocks the status write."""
    if os.environ.get("TERM_PROGRAM") == "vscode" or os.environ.get("VSCODE_PID"):
        return "vscode"
    if os.environ.get("WT_SESSION"):
        return "windows-terminal"
    if os.environ.get("TERM_PROGRAM"):
        return os.environ["TERM_PROGRAM"].lower()
    return "unknown"


def _ppid_chain(start_pid: int) -> list[dict]:
    """Walk the process tree up from start_pid via Windows toolhelp32 snapshot.
    Returns [{"pid": N, "name": "exe.exe"}, ...] in child→ancestor order.
    Called once per session (cached afterwards) so the cost is bounded.

    Why walk here instead of in focus-window.ps1: Claude Code spawns hooks via
    a short-lived wrapper (cmd.exe / similar) whose PID is what os.getppid()
    returns. That wrapper exits seconds after the hook completes, so by the
    time the user clicks the switchboard row, the immediate parent PID points
    nowhere. Capturing the chain now, while every ancestor is still alive,
    lets the focus script skip past dead nodes."""
    chain: list[dict] = []
    try:
        import ctypes
        import ctypes.wintypes as wt

        class PE32(ctypes.Structure):
            _fields_ = [
                ("dwSize", wt.DWORD),
                ("cntUsage", wt.DWORD),
                ("th32ProcessID", wt.DWORD),
                ("th32DefaultHeapID", ctypes.c_void_p),
                ("th32ModuleID", wt.DWORD),
                ("cntThreads", wt.DWORD),
                ("th32ParentProcessID", wt.DWORD),
                ("pcPriClassBase", ctypes.c_long),
                ("dwFlags", wt.DWORD),
                ("szExeFile", ctypes.c_char * 260),
            ]

        TH32CS_SNAPPROCESS = 0x00000002
        kernel32 = ctypes.windll.kernel32
        kernel32.CreateToolhelp32Snapshot.restype = wt.HANDLE
        kernel32.Process32First.argtypes = [wt.HANDLE, ctypes.POINTER(PE32)]
        kernel32.Process32First.restype = wt.BOOL
        kernel32.Process32Next.argtypes = [wt.HANDLE, ctypes.POINTER(PE32)]
        kernel32.Process32Next.restype = wt.BOOL
        kernel32.CloseHandle.argtypes = [wt.HANDLE]

        snap = kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
        if not snap or snap == wt.HANDLE(-1).value:
            return [{"pid": start_pid, "name": ""}]
        try:
            pe = PE32()
            pe.dwSize = ctypes.sizeof(PE32)
            parent_of: dict[int, int] = {}
            name_of: dict[int, str] = {}
            if kernel32.Process32First(snap, ctypes.byref(pe)):
                while True:
                    parent_of[pe.th32ProcessID] = pe.th32ParentProcessID
                    try:
                        name_of[pe.th32ProcessID] = pe.szExeFile.decode("utf-8", "replace")
                    except Exception:
                        name_of[pe.th32ProcessID] = ""
                    if not kernel32.Process32Next(snap, ctypes.byref(pe)):
                        break
            cur = start_pid
            for _ in range(20):
                chain.append({"pid": cur, "name": name_of.get(cur, "")})
                ppid = parent_of.get(cur)
                if not ppid or ppid == cur:
                    break
                cur = ppid
        finally:
            kernel32.CloseHandle(snap)
    except Exception as e:
        print(f"status-sidecar: ppid chain walk failed: {e}", file=sys.stderr)
        if not chain:
            chain = [{"pid": start_pid, "name": ""}]
    return chain


def _capture_foreground_hwnd(chain: list[dict]) -> int:
    """Return the foreground top-level HWND iff its owning process is one of
    the ancestor pids in `chain`. Else 0.

    Called only on UserPromptSubmit. At that moment the user just submitted
    a prompt from inside this terminal, so the foreground window is the VS
    Code window hosting this session. Capturing it sidesteps the
    Electron-window-shares-one-pid problem that defeats the chain-walk
    disambiguator: with N VS Code windows of the same instance, every
    integrated terminal's process tree converges on the same Code.exe pid,
    and `Get-Process.MainWindowHandle` picks arbitrarily among the N HWNDs.
    Storing the foreground HWND directly avoids the guess.

    Sanity-check: the foreground window's owning pid must be in the
    ancestor chain. If the user happened to be looking at another app when
    they submitted (rare — submit requires keyboard focus in the terminal),
    return 0 instead of poisoning the status file with a wrong HWND."""
    try:
        import ctypes
        from ctypes import wintypes as wt

        user32 = ctypes.windll.user32
        user32.GetForegroundWindow.restype = ctypes.c_void_p
        user32.GetWindowThreadProcessId.argtypes = [ctypes.c_void_p, ctypes.POINTER(wt.DWORD)]
        user32.GetWindowThreadProcessId.restype = wt.DWORD

        hwnd = user32.GetForegroundWindow()
        if not hwnd:
            return 0
        owner_pid = wt.DWORD(0)
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(owner_pid))
        owner = int(owner_pid.value)
        if not owner:
            return 0
        ancestor_pids = {int(n.get("pid", 0)) for n in (chain or [])}
        if owner not in ancestor_pids:
            return 0
        return int(hwnd)
    except Exception as e:
        print(f"status-sidecar: hwnd capture failed: {e}", file=sys.stderr)
        return 0


def _atomic_write_json(path: Path, obj: dict) -> None:
    """Same pattern as emit-event.py's save_json — write to .tmp.<pid>, then
    os.replace onto destination. Crashes leave the previous file intact."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + f".tmp.{os.getpid()}")
    tmp.write_text(json.dumps(obj, indent=2), encoding="utf-8")
    os.replace(tmp, path)


def _load_existing(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _emit_chat_intent(actor: str, sid8: str, instance: Optional[int], text: str) -> None:
    """S052: append a `kind:"intent"` line to chat.ndjson. Called from main()
    only when the intent text actually changed from the previous fire, so the
    chat panel sees one line per intent update (not one per poll). Append-mode
    open; same atomicity story as state.ndjson."""
    if not text:
        return
    text = text[:CHAT_TEXT_MAX]
    event = {
        "ts": time.time(),
        "actor": actor or "wisp",
        "instance": instance,
        "sid8": sid8 or "",
        "kind": "intent",
        "text": text,
    }
    try:
        CHAT_PATH.parent.mkdir(parents=True, exist_ok=True)
        with CHAT_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event, separators=(",", ":")) + "\n")
    except Exception as e:
        print(f"status-sidecar: chat intent emit failed: {e}", file=sys.stderr)


def _sweep_chat_ndjson() -> None:
    """S052: keep chat.ndjson bounded. Mirror of emit-event.py's sweep — called
    once per UserPromptSubmit (low cadence, post-write so a failure can't
    affect the current turn's records)."""
    try:
        if not CHAT_PATH.exists():
            return
        size = CHAT_PATH.stat().st_size
        if size <= 200_000:
            return
        try:
            lines = CHAT_PATH.read_text(encoding="utf-8").splitlines()
        except Exception:
            return
        if size <= CHAT_SIZE_MAX and len(lines) <= CHAT_LINES_MAX:
            return
        tail = lines[-CHAT_TAIL_KEEP:]
        tmp = CHAT_PATH.with_suffix(CHAT_PATH.suffix + f".tmp.{os.getpid()}")
        tmp.write_text("\n".join(tail) + "\n", encoding="utf-8")
        os.replace(tmp, CHAT_PATH)
    except Exception as e:
        print(f"status-sidecar: chat sweep failed: {e}", file=sys.stderr)


def _derive_subtitle(j: dict) -> str:
    """S052 task 2: derive a ≤100-char subtitle per session record.
    Priority:
      1. intent (when last_event_ts is within SUBTITLE_INTENT_FRESH_SEC).
      2. latest_action.
      3. empty string.
    No timestamp field is recorded specifically for `intent`; we use
    last_event_ts as a proxy — intent typically updates at UserPromptSubmit,
    which also bumps last_event_ts, so the two move together."""
    intent = (j.get("intent") or "").strip()
    last_ts = j.get("last_event_ts") or 0
    try:
        last_ts = float(last_ts)
    except (TypeError, ValueError):
        last_ts = 0.0
    fresh = (time.time() - last_ts) <= SUBTITLE_INTENT_FRESH_SEC if last_ts else False
    chosen = ""
    if intent and fresh:
        chosen = intent
    else:
        la = (j.get("latest_action") or "").strip()
        if la:
            chosen = la
        elif intent:
            chosen = intent
    if not chosen:
        return ""
    if len(chosen) > SUBTITLE_MAX_LEN:
        chosen = chosen[: SUBTITLE_MAX_LEN - 1] + "…"
    return chosen


def _latest_action_for(sid8: str, ndjson_path: Path, max_bytes: int = 256_000) -> Optional[dict]:
    """Walk state.ndjson tail backward for the most recent 'action' event whose
    sessionId starts with sid8. Returns {'text': str, 'ts': float} or None.

    Action events are emit-event.py's canonical tool-use signal:
        {"type":"action","verb":"editing|searching|reading|running",
         "target":"<path-or-cmd>","sessionId":"<full-uuid>","wallTime":"<ISO>"}

    Used by _write_manifest to stamp the per-session heartbeat that the
    switchboard renders as the .sb-action line. Capped tail-read so unbounded
    ndjson growth doesn't crater hook latency. S049/D2."""
    if not ndjson_path.exists():
        return None
    try:
        with open(ndjson_path, "rb") as f:
            f.seek(0, 2)
            size = f.tell()
            f.seek(max(0, size - max_bytes))
            tail = f.read().decode("utf-8", errors="ignore")
        lines = tail.splitlines()
        for line in reversed(lines):
            if '"type":"action"' not in line:
                continue
            try:
                ev = json.loads(line)
            except Exception:
                continue
            if ev.get("type") != "action":
                continue
            ev_sid = (ev.get("sessionId") or "")[:8]
            if ev_sid != sid8:
                continue
            verb = ev.get("verb") or "action"
            target = ev.get("target") or ""
            if len(target) > 50:
                target = target[:47] + "…"
            text = f"{verb} {target}".strip() if target else verb
            ts_iso = ev.get("wallTime") or ""
            ts = 0.0
            try:
                from datetime import datetime
                ts = datetime.fromisoformat(ts_iso).timestamp()
            except Exception:
                pass
            return {"text": text, "ts": ts}
        return None
    except Exception:
        return None


def _write_manifest() -> None:
    """Snapshot live status files into a single manifest at VIZ_DIR. Browser
    polls this one file (fetch is cheap for one file, expensive for a glob).

    Excludes 'ended' entries — the sidebar shows live sessions only. Ended
    sessions are preserved on disk (one per session at STATUS_DIR/<sid8>.json,
    moved to archive/ after STALE_SEC) and can be surfaced via a future
    history view; they don't belong in the live switchboard. S033 finding #9
    aligned this code with the docstring promise.

    Manifest shape:
        {
          "generated_at": <unix-ts>,
          "sessions": [
            { ...same shape as <sid8>.json... },
            ...
          ]
        }

    Errors swallowed; the per-session file write is the load-bearing one,
    not the manifest."""
    try:
        sessions = []
        # Read the spawn role-files once per manifest write (not per row) — the
        # per-row override below classifies working <-> waiting_for_subagents.
        pending_map = _pending_subagents_by_session()
        if STATUS_DIR.exists():
            for p in STATUS_DIR.iterdir():
                if not p.is_file() or p.suffix != ".json":
                    continue
                try:
                    j = json.loads(p.read_text(encoding="utf-8"))
                except Exception:
                    continue
                if not isinstance(j, dict):
                    continue
                if j.get("state") == "ended":
                    continue
                # Real-time actor refresh. The status file's `actor` was set
                # by whichever sidecar fire wrote it last — typically
                # UserPromptSubmit, which fires BEFORE the agent has had a
                # chance to write its intent file for this turn. The result:
                # `actor=unknown` lands in the status file at the start of a
                # working turn and sticks until Stop fires at the end.
                #
                # The manifest, however, is rewritten on every fire from ANY
                # session — so we can re-detect each session's actor against
                # its intent dir at write-time and surface a freshly-resolved
                # value without touching the canonical status file (which
                # would race with the owning session's writes).
                #
                # Carry the prior `actor` if detection comes up empty — don't
                # regress a session from "braindead" back to "unknown" just
                # because the intent file briefly didn't match (e.g., during
                # a mid-turn dedupe).
                try:
                    proj = j.get("project_dir") or ""
                    s8 = j.get("sid8") or ""
                    sfull = j.get("session_id") or ""
                    if proj and s8:
                        refreshed_actor, refreshed_intent = _detect_actor(Path(proj), s8, sfull)
                        if refreshed_actor != "unknown":
                            j["actor"] = refreshed_actor
                            if refreshed_intent:
                                j["intent"] = refreshed_intent
                except Exception as e:
                    print(f"status-sidecar: manifest actor refresh failed for {j.get('sid8')}: {e}", file=sys.stderr)
                # S040 audit fix: also re-detect instance per row at write
                # time. The status file's `instance` was stamped at its own
                # sidecar fire — which for a session whose first event was
                # UserPromptSubmit (before emit-event.py ever wrote an
                # instance assignment) lands as 1. Without this refresh all
                # parallel Braindead sessions render as Braindead·1 in the
                # sidebar even after `state-instances.json` carries the
                # correct N. _detect_instance returns None when uncertain
                # (non-instanced actor / sid not in map yet), so we only
                # override when we have a positive answer.
                try:
                    sfull = j.get("session_id") or ""
                    actor_for_inst = j.get("actor") or ""
                    if sfull and actor_for_inst:
                        refreshed_inst = _detect_instance(actor_for_inst, sfull)
                        if refreshed_inst is not None:
                            j["instance"] = refreshed_inst
                except Exception as e:
                    print(f"status-sidecar: manifest instance refresh failed for {j.get('sid8')}: {e}", file=sys.stderr)
                # Stamp current building per session so the visualizer can
                # render sprites at the right place from the manifest alone
                # (manifest-driven sync, the S044 inversion). Falls through
                # silently when state-actors.json has no entry yet — the
                # visualizer's default-spawn-building fallback handles it.
                try:
                    sfull = j.get("session_id") or ""
                    actor_for_bld = j.get("actor") or ""
                    if sfull and actor_for_bld:
                        bld = _detect_building(actor_for_bld, sfull)
                        if bld:
                            j["building"] = bld
                except Exception as e:
                    print(f"status-sidecar: manifest building refresh failed for {j.get('sid8')}: {e}", file=sys.stderr)
                # S049/D2: latest action stamp — switchboard heartbeat. Read
                # fresh per row from state.ndjson tail so the row ticks at
                # hook-fire cadence even when intent doesn't change.
                try:
                    s8 = j.get("sid8") or ""
                    if s8:
                        act = _latest_action_for(s8, VIZ_DIR / "state.ndjson")
                        if act:
                            j["latest_action"] = act["text"]
                            j["latest_action_ts"] = act["ts"]
                except Exception as e:
                    print(f"status-sidecar: latest_action refresh failed for {j.get('sid8')}: {e}", file=sys.stderr)
                # S052 task 2: derived subtitle for the switchboard row.
                try:
                    j["subtitle"] = _derive_subtitle(j)
                except Exception as e:
                    print(f"status-sidecar: subtitle derivation failed for {j.get('sid8')}: {e}", file=sys.stderr)
                # Awaiting-crew override. The base event map stamps "working"
                # for every tool call, so a session blocked on a foreground
                # Task would otherwise read WORKING. Re-derive the
                # working <-> waiting_for_subagents pair here from the spawn
                # role-files: refreshes on ANY live session's fire (the blocked
                # parent emits nothing while waiting) and self-heals a missed
                # PostToolUse. Leaves waiting_for_user / ended untouched — those
                # are owned states, not the working pair.
                try:
                    if j.get("state") in ("working", "waiting_for_subagents"):
                        ids = pending_map.get(j.get("session_id") or "", [])
                        if ids:
                            j["state"] = "waiting_for_subagents"
                            j["subtitle"] = "awaiting crew — " + " ".join(ids[:6])
                        else:
                            j["state"] = "working"
                except Exception as e:
                    print(f"status-sidecar: awaiting-crew refresh failed for {j.get('sid8')}: {e}", file=sys.stderr)
                sessions.append(j)
        sessions.sort(key=lambda x: x.get("last_event_ts") or 0, reverse=True)
        out = {
            "generated_at": time.time(),
            "sessions": sessions,
        }
        VIZ_DIR.mkdir(parents=True, exist_ok=True)
        tmp = MANIFEST_PATH.with_suffix(MANIFEST_PATH.suffix + f".tmp.{os.getpid()}")
        tmp.write_text(json.dumps(out, indent=2), encoding="utf-8")
        os.replace(tmp, MANIFEST_PATH)
    except Exception as e:
        print(f"status-sidecar: manifest write failed: {e}", file=sys.stderr)


def _sweep_stale_tmp() -> None:
    """Sweep stale `.tmp.<pid>` files in VIZ_DIR and STATUS_DIR. Both this
    sidecar and `emit-event.py` use `path.with_suffix(".tmp.<pid>")` + atomic
    replace; on Windows, `os.replace` occasionally fails (file lock, AV scan,
    concurrent writer) and leaks the tmp file. No cleanup elsewhere — they
    accumulate. Sweep tmps older than 5 minutes; legitimate tmps are at most
    seconds old. Errors are swallowed."""
    cutoff = time.time() - 5 * 60
    for dir_ in (VIZ_DIR, STATUS_DIR):
        try:
            if not dir_.exists():
                continue
            for p in dir_.iterdir():
                if not p.is_file():
                    continue
                # `.tmp.<pid>` lives as path.suffix; e.g. `state.json.tmp.123`
                # → name ends with `.tmp.<digits>` after the canonical suffix.
                if ".tmp." not in p.name:
                    continue
                # Tighten: only sweep files whose name looks like atomic-write
                # leftovers — `<base>.<ext>.tmp.<digits>`.
                stem_parts = p.name.split(".tmp.")
                if len(stem_parts) != 2 or not stem_parts[1].isdigit():
                    continue
                try:
                    if p.stat().st_mtime > cutoff:
                        continue
                    p.unlink()
                except Exception as e:
                    print(f"status-sidecar: tmp sweep failed for {p.name}: {e}", file=sys.stderr)
        except Exception as e:
            print(f"status-sidecar: tmp sweep dir {dir_} failed: {e}", file=sys.stderr)


def _sweep_stale() -> None:
    """Move status files older than STALE_SEC to STATUS_ARCHIVE_DIR. Bounded
    to whatever fits in STATUS_DIR — typically ≤20 files even on a heavy
    multi-session machine. Errors are swallowed; one stale file that can't
    be moved doesn't block this session's write."""
    try:
        if not STATUS_DIR.exists():
            return
        now = time.time()
        for p in STATUS_DIR.iterdir():
            if not p.is_file() or p.suffix != ".json":
                continue
            try:
                age = now - p.stat().st_mtime
            except Exception:
                continue
            if age <= STALE_SEC:
                continue
            STATUS_ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
            dst = STATUS_ARCHIVE_DIR / p.name
            # Append suffix on collision instead of overwriting — keeps the
            # archive append-only in spirit.
            if dst.exists():
                dst = STATUS_ARCHIVE_DIR / f"{p.stem}.{int(now)}{p.suffix}"
            try:
                p.replace(dst)
            except Exception as e:
                print(f"status-sidecar: sweep move failed for {p.name}: {e}", file=sys.stderr)
    except Exception as e:
        print(f"status-sidecar: sweep failed: {e}", file=sys.stderr)


def _live_session_ids() -> tuple[set[str], set[str]]:
    """Walk STATUS_DIR and return (live_full_session_ids, live_sid8_prefixes).
    "Live" means the status file's state != "ended" and last_event_ts is within
    LIVE_SESSION_SEC. Status files for sessions that died without firing
    SessionEnd will linger as "working" or "waiting_for_user" until the time
    bound elides them — that's the safety net for crash-exit zombies.

    Returns empty sets on any read failure so GC callers fail safe (do nothing
    rather than over-prune)."""
    full: set[str] = set()
    short: set[str] = set()
    if not STATUS_DIR.exists():
        return (full, short)
    cutoff = time.time() - LIVE_SESSION_SEC
    try:
        for p in STATUS_DIR.iterdir():
            if not p.is_file() or p.suffix != ".json":
                continue
            try:
                j = json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                continue
            if not isinstance(j, dict):
                continue
            if j.get("state") == "ended":
                continue
            ts = j.get("last_event_ts") or 0
            try:
                ts = float(ts)
            except (TypeError, ValueError):
                ts = 0.0
            if ts < cutoff:
                continue
            sid = j.get("session_id") or ""
            sid8 = j.get("sid8") or sid[:8]
            if sid:
                full.add(sid)
            if sid8:
                short.add(sid8)
    except Exception as e:
        print(f"status-sidecar: live-set scan failed: {e}", file=sys.stderr)
    return (full, short)


def _gc_state_actors(live_full: set[str]) -> None:
    """Strip dead session_ids from `state-actors.json`. Targets:
      - any `byId` map whose key isn't in `live_full`;
      - top-level scalar keys (wisp, guthix) when no `_<actor>_session_id`
        owner is live;
      - `_mode_session_id` / `_guthix_session_id` when the named session is
        dead (emit-event.py's `handle_session_end` clears these on clean
        exit; the GC catches crash-exit cases).

    Skips the write entirely if nothing changes — cheap no-op on the common
    path. Errors swallowed."""
    if not ACTORS_PATH.exists():
        return
    try:
        actors = json.loads(ACTORS_PATH.read_text(encoding="utf-8"))
    except Exception:
        return
    if not isinstance(actors, dict):
        return

    dirty = False

    # Top-level session-id markers: drop if dead.
    for marker in ("_mode_session_id", "_guthix_session_id"):
        sid = actors.get(marker)
        if sid and sid not in live_full:
            actors.pop(marker, None)
            dirty = True

    # Top-level scalar actors (wisp, guthix at building). Only `guthix` is
    # GC'd here — it has an owner marker (`_guthix_session_id` set in
    # emit-event.py `_emit_guthix_transition`), so absence of the marker
    # after the session-marker pass above is unambiguous proof of a zombie.
    # `wisp` has no owner-marker concept (it's the global default actor); a
    # stale wisp scalar just gets overwritten on the next unscoped move
    # event and doesn't accumulate, so leave it alone.
    if isinstance(actors.get("guthix"), str) and "_guthix_session_id" not in actors:
        actors.pop("guthix", None)
        dirty = True

    # byId maps under each actor: drop entries whose session isn't live.
    # Drop the actor key entirely if its byId empties out.
    for actor_name in list(actors.keys()):
        if actor_name.startswith("_"):
            continue
        entry = actors.get(actor_name)
        if not isinstance(entry, dict):
            continue
        by_id = entry.get("byId")
        if not isinstance(by_id, dict):
            continue
        before = len(by_id)
        new_by_id = {sid: bldg for sid, bldg in by_id.items() if sid in live_full}
        if len(new_by_id) != before:
            entry["byId"] = new_by_id
            dirty = True
        if not new_by_id:
            actors.pop(actor_name, None)
            dirty = True

    if not dirty:
        return
    try:
        _atomic_write_json(ACTORS_PATH, actors)
    except Exception as e:
        print(f"status-sidecar: state-actors GC write failed: {e}", file=sys.stderr)


def _gc_state_instances(live_full: set[str]) -> None:
    """S040 audit fix: strip dead session_ids from `state-instances.json.byId`.
    `_gc_state_actors` already handles `state-actors.json`; this is its sibling
    for the instance map.

    Without this, the only path that cleans byId was emit-event.py's
    `handle_session_end` — which doesn't fire on crash. Dead sessions linger
    indefinitely, the `next` high-water drifts up over time, and slot reclaim
    (S039) operates against a polluted byId. Symptom: a fresh Braindead session
    spawns as instance·5 even though only one session is live, because byId
    still carries 1/2/3/4 from prior crashed sessions.

    Keeps `next` and the actor entry itself — only prunes byId. Skips the
    write if nothing changes. Errors swallowed."""
    if not INSTANCES_PATH.exists():
        return
    try:
        state = json.loads(INSTANCES_PATH.read_text(encoding="utf-8"))
    except Exception:
        return
    if not isinstance(state, dict):
        return

    dirty = False
    for actor_name, entry in state.items():
        if not isinstance(entry, dict):
            continue
        by_id = entry.get("byId")
        if not isinstance(by_id, dict):
            continue
        before = len(by_id)
        new_by_id = {sid: inst for sid, inst in by_id.items() if sid in live_full}
        if len(new_by_id) != before:
            entry["byId"] = new_by_id
            dirty = True

    if not dirty:
        return
    try:
        _atomic_write_json(INSTANCES_PATH, state)
    except Exception as e:
        print(f"status-sidecar: state-instances GC write failed: {e}", file=sys.stderr)


def _gc_intent_files(project_dir: Path | None, live_short: set[str], current_sid8: str) -> None:
    """Archive intent files for sessions that aren't live anymore. Bare files
    (`<actor>.txt` with no `-<sid8>` suffix) are also archived — they predate
    D-018's per-session mandate and are no longer load-bearing.

    Move into `<intent_dir>/archive/` — per archive-discipline.md nothing is
    deleted. The hook fires often enough that scanning the whole dir on each
    UserPromptSubmit is fine; the dir is tiny in practice."""
    if not project_dir:
        return
    intent_dir = project_dir / ".claude" / "intent"
    if not intent_dir.exists():
        return
    archive = intent_dir / "archive"
    try:
        for p in intent_dir.iterdir():
            if not p.is_file():
                continue
            if p.name == ".gitkeep":
                continue
            if p.suffix != ".txt":
                continue
            name = p.stem
            # Per-session pattern: <actor>-<8hex>
            sid8 = ""
            if len(name) >= 9 and name[-9] == "-":
                tail = name[-8:]
                if all(c in "0123456789abcdef" for c in tail):
                    sid8 = tail
            if sid8:
                # Always keep the current session's file even if it predates
                # the first hook fire (live_short may not include current_sid8
                # on the very first UserPromptSubmit of a new session).
                if sid8 == current_sid8 or sid8 in live_short:
                    continue
            # Move to archive.
            try:
                archive.mkdir(parents=True, exist_ok=True)
                dst = archive / p.name
                if dst.exists():
                    dst = archive / f"{p.stem}.{int(time.time())}{p.suffix}"
                p.replace(dst)
            except Exception as e:
                print(f"status-sidecar: intent archive failed for {p.name}: {e}", file=sys.stderr)
    except Exception as e:
        print(f"status-sidecar: intent GC failed: {e}", file=sys.stderr)


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    hook_event = payload.get("hook_event_name") or ""
    state = EVENT_STATE.get(hook_event)
    if state is None:
        sys.exit(0)

    sid = payload.get("session_id") or os.environ.get("CLAUDE_CODE_SESSION_ID") or ""
    if not isinstance(sid, str) or not sid:
        sys.exit(0)
    sid8 = sid[:8]

    # Pre/Post fire only for the two tight matchers in settings.json:
    #   WAIT_TOOLS — interactive prompts that park the session on the principal
    #     mid-turn (no Stop fires). Pre → waiting_for_user, Post → working.
    #   SUBAGENT_TOOLS — Task/Agent spawns. A foreground spawn blocks the parent
    #     until the crew returns. Pre → waiting_for_subagents; Post → re-derive
    #     (other foreground spawns may still be in flight after a parallel
    #     batch). Background spawns don't block the parent → ignore their Pre.
    if hook_event in ("PreToolUse", "PostToolUse"):
        tool_name = payload.get("tool_name") or ""
        if tool_name in WAIT_TOOLS:
            state = "waiting_for_user" if hook_event == "PreToolUse" else "working"
        elif tool_name in SUBAGENT_TOOLS:
            tool_input = payload.get("tool_input") or {}
            background = bool(
                tool_input.get("run_in_background")
                or tool_input.get("runInBackground")
            )
            if hook_event == "PreToolUse":
                if background:
                    sys.exit(0)   # background spawn — parent keeps working
                state = "waiting_for_subagents"
            else:
                # A foreground spawn returned. Stay awaiting if this session
                # still has other in-flight foreground spawns (parallel batch),
                # else back to working. The manifest per-row refresh is the
                # ultimate authority — any session's next fire re-derives this
                # pair — so a missed PostToolUse self-heals.
                state = ("waiting_for_subagents"
                         if _count_pending_subagents(sid) > 0 else "working")
        else:
            sys.exit(0)   # only registered Pre/Post for prompt + spawn tools

    project_dir = _project_dir()
    actor, intent = _detect_actor(project_dir, sid8, sid)

    now_ts = time.time()
    out_path = STATUS_DIR / f"{sid8}.json"
    prev = _load_existing(out_path)

    # Phase 3 (D-020): record the ancestor process chain from the hook's
    # parent up. focus-window.ps1 iterates this chain to find the first live
    # Code.exe with a MainWindowHandle. Cached after the first fire — the
    # chain is stable for the session's lifetime, and the toolhelp32 snapshot
    # is the most expensive thing this script does.
    claude_pid_chain = prev.get("claude_pid_chain")
    if not claude_pid_chain:
        claude_pid_chain = _ppid_chain(os.getppid())
    claude_pid = (claude_pid_chain[0].get("pid") if claude_pid_chain else os.getppid())

    # Intent carry-forward: only inherit prev.intent when prev.actor matches.
    # An unknown actor (early-fire before intent file exists) used to inherit
    # the previous actor's intent, pinning a stale line in the sidebar.
    carry_intent = ""
    if not intent and actor == (prev.get("actor") or ""):
        carry_intent = prev.get("intent") or ""

    # S033 finding #2: pull instance from the visualizer's instance map so the
    # sidebar can disambiguate parallel sessions of the same actor. Once the
    # session has been instance-stamped (any event with `actor` from
    # emit-event.py), the number sticks; previous fires that resolved to 1 get
    # promoted as soon as the map has a real entry.
    instance = _detect_instance(actor, sid) or (prev.get("instance") or 1)

    # Phase 3 HWND disambiguator (carried-forward field). Captured on
    # UserPromptSubmit only because that's the one event where we know the
    # user is looking at this terminal's window — keyboard focus in the
    # terminal is what fires the submit. Other events (PreToolUse / Stop /
    # SessionEnd) may fire while the user has already switched away.
    if hook_event == "UserPromptSubmit":
        claude_hwnd = _capture_foreground_hwnd(claude_pid_chain)
        if not claude_hwnd:
            claude_hwnd = int(prev.get("claude_hwnd") or 0)
    else:
        claude_hwnd = int(prev.get("claude_hwnd") or 0)

    record = {
        "sid8": sid8,
        "session_id": sid,
        "actor": actor,
        "instance": instance,
        "state": state,
        "last_event_kind": hook_event,
        "last_event_ts": now_ts,
        "started_at": prev.get("started_at") or now_ts,
        "intent": intent or carry_intent,
        "project_dir": str(project_dir) if project_dir else (prev.get("project_dir") or ""),
        "cwd": os.getcwd(),
        "host": prev.get("host") or _detect_host(),
        "claude_pid": claude_pid,
        "claude_pid_chain": claude_pid_chain,
        "claude_hwnd": claude_hwnd,
    }

    try:
        _atomic_write_json(out_path, record)
    except Exception as e:
        print(f"status-sidecar: write failed: {e}", file=sys.stderr)

    # S052: emit a chat.ndjson `intent` line whenever the resolved intent text
    # changes from the previous fire. The status sidecar runs once per Pre/Post
    # tool call AND on UserPromptSubmit/Stop/SessionEnd, so re-checking here
    # catches every intent update without the per-poll noise (write is gated
    # on actual change).
    try:
        prev_intent = (prev.get("intent") or "").strip()
        new_intent = (record.get("intent") or "").strip()
        if new_intent and new_intent != prev_intent:
            _emit_chat_intent(record.get("actor") or "wisp", sid8, instance, new_intent)
    except Exception as e:
        print(f"status-sidecar: chat intent dispatch failed: {e}", file=sys.stderr)

    # Sweep runs after the write so a failure in the sweep can't prevent this
    # session's own status from landing.
    _sweep_stale()
    _sweep_stale_tmp()

    # Cross-session zombie GC. Gated on UserPromptSubmit because it's the
    # lowest-frequency event we register (one per turn) and because by then
    # this session's own status file has just been refreshed — so the GC's
    # ground-truth scan can't accidentally classify the current session as
    # dead. Skip on Stop/SessionEnd: Stop fires twice per turn and SessionEnd
    # is already on the cleanup path for the ending session.
    if hook_event == "UserPromptSubmit":
        live_full, live_short = _live_session_ids()
        if sid:
            live_full.add(sid)
        if sid8:
            live_short.add(sid8)
        _gc_state_actors(live_full)
        _gc_state_instances(live_full)
        _gc_intent_files(project_dir, live_short, sid8)
        # S052: chat ndjson sweep — once per turn, cheap when file is small.
        _sweep_chat_ndjson()

    # Manifest mirror runs last — purely a snapshot for the browser; a failure
    # here can't affect the canonical per-session store.
    _write_manifest()
    _mirror_comms()

    sys.exit(0)


def _mirror_comms() -> None:
    """Copy comms/active.md from both brains into VIZ_DIR with stable names so
    the browser can fetch them inside the http.server sandbox. Skip-on-error per
    source; one missing file shouldn't break the other mirror."""
    for src, dst in COMMS_MIRRORS:
        try:
            if not src.exists():
                continue
            VIZ_DIR.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(src.read_bytes())
        except Exception:
            continue


if __name__ == "__main__":
    main()
