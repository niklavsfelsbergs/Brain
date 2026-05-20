#!/usr/bin/env python3
# Architectural guarantee #3: dwarves have a restricted write surface.
# Active only when env var CLAUDE_BRAIN_DWARF=1. The principal sets this when
# spawning a dwarf agent; the env propagates into the sub-agent's hook calls.
#
# Dwarves may write to:
#   - bank/notes/...            (any player)
#   - quest-log/in-progress/... (any player)
#   - quest-log/completed/...   (any player)
#   - inventory/...             (any player)
#   - lorebook/patch-notes.md
#
# See meta/modes.md for the full picture.

import json
import os
import sys
from pathlib import Path

BRAIN_ROOT = Path(__file__).resolve().parent.parent.parent

ALLOWED_PATTERNS = [
    "/bank/notes/",
    "/quest-log/in-progress/",
    "/quest-log/completed/",
    "/inventory/",
    "/lorebook/patch-notes.md",
]


def is_in_brain(p: Path) -> bool:
    try:
        p.resolve().relative_to(BRAIN_ROOT)
        return True
    except ValueError:
        return False


def main() -> None:
    if os.environ.get("CLAUDE_BRAIN_DWARF") != "1":
        sys.exit(0)

    try:
        payload = json.load(sys.stdin)
    except Exception as e:
        print(f"dwarf-write-boundary: bad payload: {e}", file=sys.stderr)
        sys.exit(0)

    tool_name = payload.get("tool_name", "")
    if tool_name not in ("Edit", "Write", "NotebookEdit", "MultiEdit"):
        sys.exit(0)

    tool_input = payload.get("tool_input") or {}
    file_path = tool_input.get("file_path") or tool_input.get("notebook_path") or ""
    if not file_path:
        sys.exit(0)

    p = Path(file_path)
    if not is_in_brain(p):
        sys.exit(0)

    rel = "/" + str(p.resolve().relative_to(BRAIN_ROOT)).replace("\\", "/")

    if not any(pat in rel for pat in ALLOWED_PATTERNS):
        print(
            f"BLOCKED: dwarves cannot write to {rel}.\n"
            f"  Allowed: bank/notes, quest-log/in-progress, quest-log/completed,\n"
            f"           inventory, lorebook/patch-notes.md\n"
            f"  See meta/modes.md.",
            file=sys.stderr,
        )
        sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()
