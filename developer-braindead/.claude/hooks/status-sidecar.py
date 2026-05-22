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
VIZ_DIR = DEV_BRAIN / "experiments" / "visualizer"
MANIFEST_PATH = VIZ_DIR / "state-switchboard.json"

# Same intent length cap as the visualizer hook so a sidebar can render
# sidecar intent inline without re-truncating.
INTENT_MAX_LEN = 100

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


def _detect_actor(project_dir: Path | None, sid8: str) -> tuple[str, str]:
    """Look for <project_dir>/.claude/intent/<actor>-<sid8>.txt. Returns
    (actor, intent_first_line). Falls back to ("unknown", "") when no
    per-session intent file exists yet — early in a session the sidecar may
    fire before the agent has written intent. The next event updates the
    status file with the resolved actor.

    Same actor enumeration as emit-event.py (players + non-player suffixed
    actors + guthix). Kept in sync by hand; if the visualizer's actor set
    grows, this list needs the addition too."""
    if not project_dir:
        return ("unknown", "")
    intent_dir = project_dir / ".claude" / "intent"
    if not intent_dir.exists():
        return ("unknown", "")
    candidates = ("jebrim", "zezima", "braindead", "guthix", "wisp")
    for actor in candidates:
        p = intent_dir / f"{actor}-{sid8}.txt"
        if not p.exists():
            continue
        try:
            raw = p.read_text(encoding="utf-8").strip()
        except Exception:
            raw = ""
        first = raw.splitlines()[0].strip()[:INTENT_MAX_LEN] if raw else ""
        return (actor, first)
    return ("unknown", "")


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


def _write_manifest() -> None:
    """Snapshot all live status files into a single manifest at VIZ_DIR.
    Browser polls this one file (fetch is cheap for one file, expensive for
    a glob). Excludes 'ended' entries by default — the sidebar can fetch
    those separately if it wants a "recent history" view.

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

    project_dir = _project_dir()
    actor, intent = _detect_actor(project_dir, sid8)

    now_ts = time.time()
    out_path = STATUS_DIR / f"{sid8}.json"
    prev = _load_existing(out_path)

    record = {
        "sid8": sid8,
        "session_id": sid,
        "actor": actor,
        "instance": prev.get("instance") or 1,
        "state": state,
        "last_event_kind": hook_event,
        "last_event_ts": now_ts,
        "started_at": prev.get("started_at") or now_ts,
        "intent": intent or prev.get("intent") or "",
        "project_dir": str(project_dir) if project_dir else (prev.get("project_dir") or ""),
        "cwd": os.getcwd(),
        "host": prev.get("host") or _detect_host(),
    }

    try:
        _atomic_write_json(out_path, record)
    except Exception as e:
        print(f"status-sidecar: write failed: {e}", file=sys.stderr)

    # Sweep runs after the write so a failure in the sweep can't prevent this
    # session's own status from landing.
    _sweep_stale()

    # Manifest mirror runs last — purely a snapshot for the browser; a failure
    # here can't affect the canonical per-session store.
    _write_manifest()

    sys.exit(0)


if __name__ == "__main__":
    main()
