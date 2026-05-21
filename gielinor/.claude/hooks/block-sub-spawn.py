#!/usr/bin/env python3
# Architectural guarantee #4: sub-agents cannot spawn further sub-agents.
# Active when env var CLAUDE_BRAIN_DWARF=1 OR CLAUDE_BRAIN_GNOME=1.
# Fires PreToolUse on Agent/Task. Blocks any sub-agent spawn from within
# a dwarf or gnome session — only the principal spawns.
#
# See meta/modes.md.

import json
import os
import sys


def main() -> None:
    is_dwarf = os.environ.get("CLAUDE_BRAIN_DWARF") == "1"
    is_gnome = os.environ.get("CLAUDE_BRAIN_GNOME") == "1"
    if not (is_dwarf or is_gnome):
        sys.exit(0)

    try:
        payload = json.load(sys.stdin)
    except Exception as e:
        print(f"block-sub-spawn: bad payload: {e}", file=sys.stderr)
        sys.exit(0)

    tool_name = payload.get("tool_name", "")
    if tool_name in ("Agent", "Task"):
        role = "dwarves" if is_dwarf else "gnomes"
        print(
            f"BLOCKED: {role} cannot spawn further sub-agents.\n"
            f"  Return control to the principal to spawn the next agent.\n"
            f"  See meta/modes.md.",
            file=sys.stderr,
        )
        sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()
