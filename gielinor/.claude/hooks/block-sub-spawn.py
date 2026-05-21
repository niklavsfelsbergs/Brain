#!/usr/bin/env python3
# Architectural guarantee #4: sub-agents cannot spawn further sub-agents.
# Active when the PreToolUse payload carries agent_type in ("dwarf", "gnome").
# Claude Code populates agent_id + agent_type in the JSON payload when a tool
# call originates inside a sub-agent context; env vars are NOT propagated, so
# gating on os.environ would leave the block silently inert.
# (Original implementation gated on CLAUDE_BRAIN_DWARF/GNOME=1; fixed
# 2026-05-21 in the [[S020]] dev-brain ratification pass.)
#
# See meta/modes.md.

import json
import sys


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except Exception as e:
        print(f"block-sub-spawn: bad payload: {e}", file=sys.stderr)
        sys.exit(0)

    agent_type = payload.get("agent_type")
    if agent_type not in ("dwarf", "gnome"):
        sys.exit(0)

    tool_name = payload.get("tool_name", "")
    if tool_name in ("Agent", "Task"):
        role = "dwarves" if agent_type == "dwarf" else "gnomes"
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
