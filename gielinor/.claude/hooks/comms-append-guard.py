#!/usr/bin/env python3
"""
comms-append-guard.py — PreToolUse gate (S127 plan.md section R.1).

Blocks raw Edit/Write/MultiEdit/NotebookEdit of either vault's
comms/active.md, forcing all appends through tools/comms_append.py (the atomic
locked-append path). This closes the truncation/lost-update class that fired
live in S127: the comms logs are append-only, but the agent posted entries by
read-modify-rewrite (Edit/Write), which clobbers concurrent writers and can
truncate the file to zero.

Why a hook and not discipline: born-linking (section O.9) was discipline-only
and did not hold; section O.10 had to add a commit hook. Same shape here -- the
S125 audit's standing lesson is "hook-blocking holds, discipline-WATCH drifts."

Design (mirrors require-open-on-entry.py):
- Only fires on Edit/Write/MultiEdit/NotebookEdit whose target ENDS WITH
  comms/active.md. Everything else -> allow. comms/_about.md, comms/archive/*,
  and all non-comms paths are untouched.
- ESCAPE: rotation legitimately rewrites active.md (bulk-move to archive). Set
  the env var COMMS_ROTATE=1 for that one action and the guard stands down.
- Fail-OPEN on any malformed payload -- a guard must never hard-block real work
  on a parse fluke.
- The tool itself runs via Bash, so it is never matched here.

Known, accepted gap: a raw Bash `>>` append bypasses this guard, but `>>` does
not cause the truncation-to-zero class (at worst minor interleaving, which the
comms protocol already tolerates). The rituals + _about point at the tool; this
hook stops the catastrophic Edit/Write rewrite path.
"""
import sys
import json
import os

# --- ritual analytics (item 11, S121); never let logging break the hook ---
try:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "switchboard"))
    from ritual_log import log_event
except Exception:
    def log_event(*a, **k):
        pass


def _sid8():
    sid = os.environ.get("CLAUDE_CODE_SESSION_ID", "")
    return sid[:8] if sid else ""


def _payload():
    try:
        return json.loads(sys.stdin.read() or "{}")
    except Exception:
        return None


def _path_from(payload):
    ti = (payload or {}).get("tool_input", {}) or {}
    for k in ("file_path", "path", "notebook_path"):
        v = ti.get(k)
        if v:
            return v
    return ""


def main():
    payload = _payload()
    if payload is None:
        sys.exit(0)  # malformed -> allow (fail-open)

    tool = payload.get("tool_name", "")
    if tool not in ("Edit", "Write", "MultiEdit", "NotebookEdit"):
        sys.exit(0)

    path = _path_from(payload)
    if not path:
        sys.exit(0)

    norm = path.replace("\\", "/")
    if not norm.endswith("comms/active.md"):
        sys.exit(0)

    # Rotation escape — a deliberate whole-file rewrite, opted into per action.
    if os.environ.get("COMMS_ROTATE"):
        sys.exit(0)

    log_event("comms-append-guard", "block", sid8=_sid8(), detail=norm)
    sys.stderr.write(
        "\n[comms-append-guard] Do not Edit/Write comms/active.md directly — a "
        "read-modify-rewrite clobbers concurrent sessions and can truncate the "
        "log to zero (the S127 bug).\n"
        "Append via the atomic locked tool instead:\n"
        "  printf '%s' \"$ENTRY\" | py tools/comms_append.py --vault dev|gielinor\n"
        "  (or --file <path>, or --entry \"...\")\n"
        f"  attempted: {norm}\n"
        "If this really is a rotation (bulk-move to comms/archive/), re-run with "
        "COMMS_ROTATE=1 set.\n"
    )
    sys.exit(2)


if __name__ == "__main__":
    main()
