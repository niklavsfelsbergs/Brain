#!/usr/bin/env python
# grounding-cue-reminder.py — make the grounding-precondition FIRE (B-009 land of
# the B-008 godly proposal; decision D-028).
#
# The grounding-precondition (read active context + confirm the referent before
# producing substantive output) is confirmed globally (examine "G1"), graduated
# at B-007 from two independent player instances, and stored in memory — yet it
# reproduced 3x (S066/S076/S095), every time on a session/turn that opened with a
# CONTINUATION CUE ("again", "back to", "the X I prepared earlier"). Capture is
# saturated; triggering was the gap. This UserPromptSubmit hook is the trigger:
# on a cue match it injects a short, NON-BLOCKING reminder to check the player's
# own bank/notes/research/quest-log before analyzing.
#
# Design (per the proposal + the brain's verify-enforcement-fires ethos):
#   - cue match is the LOAD-BEARING path; artifact detection is best-effort and
#     no-ops cleanly if the payload exposes no attachment field (UNVERIFIED — see
#     ARTIFACT_KEYS note; do not rely on it).
#   - advisory only: emits additionalContext, never blocks (exit 0 always).
#   - gielinor-scoped: skips dev-brain (actor == "braindead") via the per-session
#     status sidecar; everything else (players, Guthix, wisp) fires.
#   - defensive by construction: any parse/IO failure exits 0 silently. A missed
#     nudge costs nothing; a crash that ate a prompt would be the real harm.

import json
import os
import re
import sys
from pathlib import Path

STATUS_DIR = Path(os.path.expanduser("~")) / ".claude" / "status"

# Continuation-cue patterns (case-insensitive, word-boundaried where it matters).
# Narrow on purpose — a false positive costs one advisory line; over-firing makes
# the reminder wallpaper (the proposal's §6 over-trust risk).
_CUE_PATTERNS = [
    r"\bonce again\b",
    r"\bagain[,\s]",
    r"\bback to\b",
    r"\bsome more\b",
    r"\bafter\s?all\b",
    # prepared/earlier-content forms: "the report I prepared earlier", "the deck I built before"
    r"\bthe\b.{0,30}\b(prepared|made|wrote|built|created|drafted)\b.{0,25}\b(earlier|before|last time|already|previously)\b",
    r"\b(resum(e|ing)|continu(e|ing)|pick(ing)? up|where we left off)\b",
]
_CUE_RE = re.compile("|".join(_CUE_PATTERNS), re.IGNORECASE | re.DOTALL)

# Best-effort attachment keys. UNVERIFIED against Claude Code's real
# UserPromptSubmit payload — if none are present this half silently no-ops and
# the cue-match path carries all the value. Do not assume these fire.
ARTIFACT_KEYS = ("attachments", "files", "pasted_contents", "attached_files")


def _actor_for(sid8: str) -> str:
    """Read the per-session status sidecar to learn the active actor. '' if unknown."""
    if not sid8:
        return ""
    try:
        data = json.loads((STATUS_DIR / f"{sid8}.json").read_text(encoding="utf-8"))
        return (data.get("actor") or "").lower()
    except (OSError, ValueError):
        return ""


def _has_artifact(payload: dict) -> bool:
    for k in ARTIFACT_KEYS:
        v = payload.get(k)
        if v:  # non-empty list/str/dict
            return True
    return False


def _emit(matched: str) -> None:
    msg = (
        f'Grounding cue detected ("{matched}"). Before producing substantive output: '
        "search the active player's bank/notes/, research/, and quest-log/ for this subject; "
        "map any uploaded artifact to where prior work left off; confirm the referent's identity. "
        'Treat "this is new" as a hypothesis to disprove. '
        "(examine G1; recurred S066/S076/S095; D-028.)"
    )
    out = {
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": msg,
        }
    }
    sys.stdout.write(json.dumps(out))


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (ValueError, OSError):
        return 0  # can't parse — never disrupt a real prompt

    if payload.get("hook_event_name") not in (None, "UserPromptSubmit"):
        return 0

    prompt = payload.get("prompt") or ""

    sid = payload.get("session_id") or os.environ.get("CLAUDE_CODE_SESSION_ID") or ""
    sid8 = sid[:8].lower()

    # Scope: skip dev-brain (Braindead's construction work has different cue
    # semantics). Players / Guthix / wisp / unknown all fire.
    if _actor_for(sid8) == "braindead":
        return 0

    m = _CUE_RE.search(prompt)
    matched = m.group(0).strip() if m else None
    if matched is None and _has_artifact(payload):
        matched = "uploaded artifact"
    if matched is None:
        return 0  # ordinary prompt — fast, silent pass-through

    _emit(matched)
    return 0


if __name__ == "__main__":
    sys.exit(main())
