#!/usr/bin/env python3
# Architectural guarantee #6: sub-agents cannot spawn further sub-agents.
# Active when the PreToolUse payload carries agent_type in ("dwarf", "gnome", "penguin").
# Claude Code populates agent_id + agent_type in the JSON payload when a tool
# call originates inside a sub-agent context; env vars are NOT propagated, so
# gating on os.environ would leave the block silently inert.
# (Original implementation gated on CLAUDE_BRAIN_DWARF/GNOME=1; fixed
# 2026-05-21 in the [[S020]] dev-brain ratification pass. Penguins added
# 2026-05-22 in the S030 penguin-role bundle.)
#
# See meta/modes.md.

import json
import sys
from pathlib import Path

# Ritual analytics (Khaan item 11) — best-effort; never breaks the hook.
_SB = Path(__file__).resolve().parents[3] / "switchboard"
if str(_SB) not in sys.path:
    sys.path.insert(0, str(_SB))
try:
    from ritual_log import log_event
except Exception:
    def log_event(*a, **k): pass

ROLE_PLURALS = {
    "dwarf": "dwarves",
    "gnome": "gnomes",
    "penguin": "penguins",
    "shipping-agent": "shipping-agents",
}


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except Exception as e:
        print(f"block-sub-spawn: bad payload: {e}", file=sys.stderr)
        sys.exit(0)

    agent_type = payload.get("agent_type")
    if agent_type not in ROLE_PLURALS:
        sys.exit(0)

    tool_name = payload.get("tool_name", "")
    if tool_name in ("Agent", "Task"):
        role = ROLE_PLURALS[agent_type]
        log_event("block-sub-spawn", "block", actor=agent_type, sid8=(payload.get("session_id") or "")[:8], detail=role)
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
