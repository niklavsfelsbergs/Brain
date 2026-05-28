#!/usr/bin/env python
# close-cue-reminder.py — make the CLOSE ritual hard to skip on a graceful end
# (S115 close-enforcement, layer 2; the exit-side symmetry of
# require-open-on-entry.py).
#
# The close ritual needs the model in the loop (quest-log narrative, respawn
# update, learnings harvest, a real commit) — a SessionEnd hook runs a script,
# not the model, and fires async/no-wait so it can't be relied on (see the
# layer-3 session-end-safety-net note). The reliable lever while the model is
# still here is this UserPromptSubmit nudge: when a message reads like the
# session is winding down, inject a NON-BLOCKING reminder to run the close
# ritual + its completeness gate before declaring wrapped.
#
# Design (mirrors grounding-cue-reminder.py):
#   - advisory only: emits additionalContext, never blocks (exit 0 always).
#   - fires for EVERY actor — the close ritual applies to players, Guthix, AND
#     dev-brain (the dev close is exactly what S115 botched), so no actor-skip.
#   - defensive: any parse/IO failure exits 0 silently. A missed nudge costs
#     nothing; a crash that ate a prompt would be the real harm.

import json
import os
import re
import sys

# Winding-down cues (case-insensitive). Narrow on purpose — a false positive
# costs one advisory line, but bare "close"/"done"/"bye" over-fire into
# wallpaper, so require the session-ending shape.
_CUE_PATTERNS = [
    r"\blet'?s\s+close\b",
    r"\bclos(e|ing)\s+(the\s+|this\s+)?session\b",
    r"\bend\s+(the\s+|this\s+)?session\b",
    r"\bwrap(ping)?\s+(this\s+|it\s+)?up\b",
    r"\bwrap\s+up\b",
    r"\bcall\s+it\s+(a\s+day|here|quits)\b",
    r"\bthat'?s\s+(all|it)\s+for\s+(today|now|the\s+day)\b",
    r"\bdone\s+for\s+(today|now|the\s+day)\b",
    r"\bsign(ing)?\s+off\b",
    r"\bhand\s+(this\s+|it\s+)?(over|off)\s+to\s+the\s+next\s+session\b",
    r"\bfinish\s+up\b",
]
_CUE_RE = re.compile("|".join(_CUE_PATTERNS), re.IGNORECASE)


def _emit(matched: str) -> None:
    msg = (
        f'Close / wind-down cue detected ("{matched}"). If the session is ending, '
        "run the CLOSE ritual before stopping — do NOT skip it: finish the quest-log "
        "(incl. the Cascade. / Main-brain changes. lines), update respawn, post the "
        "CLOSING to comms, commit, set active-mode, then VERIFY completeness before "
        "declaring wrapped (dev-brain: developer-braindead/verification/close_check.py "
        "--sid8 <sid8>; players: the gielinor close-session ritual). (S115 close-enforcement.)"
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
    m = _CUE_RE.search(prompt)
    if m is None:
        return 0  # ordinary prompt — fast, silent pass-through

    _emit(m.group(0).strip())
    return 0


if __name__ == "__main__":
    sys.exit(main())
