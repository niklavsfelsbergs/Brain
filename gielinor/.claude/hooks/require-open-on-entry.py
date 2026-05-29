#!/usr/bin/env python
# require-open-on-entry.py — POSITIVE enforcement gate (Khaan-inspired, item 1 of
# the 2026-05-28 Khaan learnings catalogue; first obligation gate that BLOCKS a
# must-do step rather than a must-not-do one).
#
# WHAT IT ENFORCES
#   The OPEN-on-entry discipline — the brain's #1 recurring leak ("did not post an
#   OPEN; entered mid-conversation", S034/S037-S043/S046/S057/S060...). Respawn
#   steps 6-8 require posting an OPEN to comms/active.md before substantive work;
#   it was prompt-discipline only, so it leaked ~70% of sessions historically.
#   This makes it mechanical: a player or Braindead session cannot WRITE brain
#   content until it has posted an OPEN carrying its own sid8.
#
# MECHANISM (mirrors the existing PreToolUse boundary hooks)
#   Fires PreToolUse on Edit|Write|MultiEdit|NotebookEdit. Reads JSON from stdin.
#   exit 2 blocks (reason on stderr); exit 0 allows. FAILS OPEN on any error — a
#   bug here can never brick a session (every other brain hook holds this line).
#
# DECISION TABLE (principal-chosen 2026-05-28, hard-block scope)
#   non-brain target path .................................. allow
#   actor not an OPEN-poster (guthix/wisp/unknown) ......... allow
#   actor unresolved ('') after status + intent fallback ... allow + log skip-noactor
#   sub-agent (agent_type set) ............................. allow  (dwarves etc. don't post OPENs)
#   target is an escape path (comms/marker/intent/narration) allow  (so you CAN post the OPEN + set up)
#   OPEN with this sid8 already in the actor's comms ....... allow
#   otherwise .............................................. BLOCK
#
# ACTOR RESOLUTION (S125 fix for the S124 silent-fail-open hole)
#   _actor_for(sid8) reads ~/.claude/status/<sid8>.json, written by a SEPARATE
#   sidecar that can lag the first write of a 'Hey Jebrim'-straight-into-task
#   session -> '' -> the gate failed open with NO telemetry (invisible). Now we
#   fall back to the per-session intent file on disk, and if STILL unresolved we
#   fail open but emit a skip-noactor event so the hole is measurable, not silent.
#
# Escapes exist so the entry sequence itself is never gated: posting the OPEN
# (comms/active.md), the dev-brain marker (.claude/active-mode.txt), intent
# narration (.claude/intent/*), and narration (.claude/narration.txt).

import json
import os
import sys
from pathlib import Path

# Ritual analytics (Khaan item 11) — best-effort; never breaks the hook.
_SB = Path(__file__).resolve().parents[3] / "switchboard"
if str(_SB) not in sys.path:
    sys.path.insert(0, str(_SB))
try:
    from ritual_log import log_event, classify_path
except Exception:
    def log_event(*a, **k): pass
    def classify_path(p): return ""

BRAIN_ROOT = Path(__file__).resolve().parent.parent.parent.parent  # gielinor/.claude/hooks -> brain root
STATUS_DIR = Path(os.path.expanduser("~")) / ".claude" / "status"

# Actors that do NOT post an OPEN — never gated.
_NON_OPEN_ACTORS = {"guthix", "wisp", ""}

WRITE_TOOLS = ("Edit", "Write", "MultiEdit", "NotebookEdit")


def _rel(p: Path):
    """Brain-relative POSIX path, or None if the target is outside the brain."""
    try:
        return p.resolve().relative_to(BRAIN_ROOT).as_posix()
    except (ValueError, OSError):
        return None


def _is_escape(rel: str) -> bool:
    """Coordination/setup writes that must work before/around the OPEN."""
    if rel.endswith("comms/active.md"):
        return True
    if rel == ".claude/active-mode.txt" or rel == ".claude/narration.txt":
        return True
    if rel.startswith(".claude/intent/"):
        return True
    return False


def _actor_for(sid8: str) -> str:
    if not sid8:
        return ""
    try:
        data = json.loads((STATUS_DIR / f"{sid8}.json").read_text(encoding="utf-8"))
        return (data.get("actor") or "").lower()
    except (OSError, ValueError):
        return ""


def _actor_from_intent(sid8: str) -> str:
    """Disk fallback for actor resolution. The status file is written by a
    separate sidecar and can lag the first write of a session that opens
    'Hey Jebrim' straight into a task — so _actor_for returns '' and the gate
    used to fail open SILENTLY (the S124/61d62e21 hole). The per-session intent
    file `.claude/intent/<actor>-<sid8>.txt` is the documented on-disk session
    anchor (communication-protocol.md → Intent narration); recover the actor
    from its filename prefix. Actor names carry no hyphen, so rsplit is safe."""
    if not sid8:
        return ""
    try:
        intent_dir = BRAIN_ROOT / ".claude" / "intent"
        for f in intent_dir.glob(f"*-{sid8}.txt"):
            actor = f.name[:-4].rsplit("-", 1)[0].lower()  # drop '.txt', take prefix
            if actor:
                return actor
    except OSError:
        return ""
    return ""


def _player_names() -> set:
    try:
        base = BRAIN_ROOT / "gielinor" / "players"
        return {
            d.name.lower()
            for d in base.iterdir()
            if d.is_dir() and not d.name.startswith("_") and d.name != "inbox"
        }
    except OSError:
        return set()


def _comms_for(actor: str):
    """The comms file this actor is expected to have posted an OPEN to.
    Returns None if the actor is not an OPEN-poster."""
    if actor == "braindead":
        return BRAIN_ROOT / "developer-braindead" / "comms" / "active.md"
    if actor in _NON_OPEN_ACTORS:
        return None
    if actor in _player_names():
        return BRAIN_ROOT / "gielinor" / "comms" / "active.md"
    return None  # unknown non-empty actor — don't gate (fail-open posture)


def _has_open(comms: Path, sid8: str) -> bool:
    """True if comms holds an OPEN entry carrying this sid8.
    Any read failure raises — caller treats that as fail-open (allow)."""
    text = comms.read_text(encoding="utf-8", errors="replace")
    for line in text.splitlines():
        if sid8 in line and "OPEN" in line:
            return True
    return False


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (ValueError, OSError):
        return 0  # unparseable — never disrupt a real action

    if payload.get("tool_name", "") not in WRITE_TOOLS:
        return 0

    # Sub-agents don't post OPENs; their own write-boundary hooks govern them.
    if payload.get("agent_type"):
        return 0

    tool_input = payload.get("tool_input") or {}
    file_path = tool_input.get("file_path") or tool_input.get("notebook_path") or ""
    if not file_path:
        return 0

    rel = _rel(Path(file_path))
    if rel is None:
        return 0  # outside the brain — not our concern
    if _is_escape(rel):
        return 0  # the OPEN / setup surface is always writable

    sid = payload.get("session_id") or os.environ.get("CLAUDE_CODE_SESSION_ID") or ""
    sid8 = sid[:8].lower()

    actor = _actor_for(sid8) or _actor_from_intent(sid8)
    comms = _comms_for(actor)
    if comms is None:
        # Empty actor = unresolved (status file lagged AND no intent anchor on
        # disk). This is the silent-fail-open path that let S124 slip through.
        # Keep failing open (a hook bug must never brick a session), but log it
        # so the hole is VISIBLE — instrument, don't re-guess. guthix/wisp and
        # known-but-non-posting actors are legitimately ungated; don't log them.
        if actor == "":
            log_event("require-open", "skip-noactor", actor="", sid8=sid8,
                      path_class=classify_path(rel))
        return 0  # not an OPEN-posting actor (or unresolved — failed open)

    try:
        posted = _has_open(comms, sid8)
    except OSError:
        return 0  # can't read comms — fail open, never brick on infra

    if posted:
        log_event("require-open", "allow", actor=actor, sid8=sid8, path_class=classify_path(rel))
        return 0

    log_event("require-open", "block", actor=actor, sid8=sid8, path_class=classify_path(rel))
    sys.stderr.write(
        "BLOCKED: post your OPEN to comms/active.md before writing brain content.\n"
        f"  Actor: {actor}   Session: {sid8}\n"
        f"  Comms: {comms.relative_to(BRAIN_ROOT).as_posix()}\n"
        "  Respawn steps 6-8: announce your targets + check for live siblings first.\n"
        "  (This is the entry-OPEN gate — the #1 historical discipline leak, now enforced.)\n"
    )
    return 2


if __name__ == "__main__":
    sys.exit(main())
