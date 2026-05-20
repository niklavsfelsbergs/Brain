#!/usr/bin/env python3
# Architectural guarantee #4: dwarves cannot spawn further dwarves.
# Active only when env var CLAUDE_BRAIN_DWARF=1.
# Fires PreToolUse on Agent/Task. Blocks any sub-agent spawn from within
# a dwarf session.
#
# See meta/modes.md.

import json
import os
import sys


def main() -> None:
    if os.environ.get("CLAUDE_BRAIN_DWARF") != "1":
        sys.exit(0)

    try:
        payload = json.load(sys.stdin)
    except Exception as e:
        print(f"block-sub-dwarf-spawn: bad payload: {e}", file=sys.stderr)
        sys.exit(0)

    tool_name = payload.get("tool_name", "")
    if tool_name in ("Agent", "Task"):
        print(
            "BLOCKED: dwarves cannot spawn further sub-agents.\n"
            "  Return control to the principal to spawn the next agent.\n"
            "  See meta/modes.md.",
            file=sys.stderr,
        )
        sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()
