#!/usr/bin/env python3
# Write boundary for the shipping-agent sub-agent type (S101 /
# .claude/agents/shipping-agent.md). Active only when the PreToolUse payload
# carries agent_type == "shipping-agent". Same mechanism as the dwarf/gnome/
# penguin boundary hooks — Claude Code populates agent_type in the JSON payload
# for tool calls originating inside a typed sub-agent; env vars are NOT
# propagated, so gating on os.environ would leave the boundary silently inert.
#
# The shipping-agent is a talk-to-your-data emulation: it queries the live mart
# (read-only, via the Redshift MCP) and writes its real deliverables — charts,
# CSVs, saved SQL — OUTSIDE the brain (the picanova/shipping-agent repo's
# workbench/, or the NFE work folder). Those paths are not under BRAIN_ROOT, so
# is_in_brain() returns False and this hook allows them. The only brain-internal
# write it should make is its quest-log trace (+ inventory working state).
#
# Shipping-agent may write (inside the brain) to:
#   - quest-log/in-progress/... (any player)
#   - quest-log/completed/...   (any player)
#   - inventory/...             (any player)
#
# NOT bank/ — mart findings are picked into bank during *alching*, not authored
# by the agent (same rule as penguins). All identity layers, drafts, keepsake,
# lorebook, meta, and spellbook/rituals are off-limits. confirmed/ and deletes
# are blocked by the global hooks on top of this one.
#
# See meta/modes.md (Shipping-agent role).

import json
import sys
from pathlib import Path

BRAIN_ROOT = Path(__file__).resolve().parent.parent.parent

ALLOWED_PATTERNS = [
    "/quest-log/in-progress/",
    "/quest-log/completed/",
    "/inventory/",
]


def is_in_brain(p: Path) -> bool:
    try:
        p.resolve().relative_to(BRAIN_ROOT)
        return True
    except ValueError:
        return False


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except Exception as e:
        print(f"shipping-agent-write-boundary: bad payload: {e}", file=sys.stderr)
        sys.exit(0)

    if payload.get("agent_type") != "shipping-agent":
        sys.exit(0)

    tool_name = payload.get("tool_name", "")
    if tool_name not in ("Edit", "Write", "NotebookEdit", "MultiEdit"):
        sys.exit(0)

    tool_input = payload.get("tool_input") or {}
    file_path = tool_input.get("file_path") or tool_input.get("notebook_path") or ""
    if not file_path:
        sys.exit(0)

    p = Path(file_path)
    # Deliverables outside the brain (shipping-agent workbench/, NFE) are the
    # agent's real output surface — not governed here.
    if not is_in_brain(p):
        sys.exit(0)

    rel = "/" + str(p.resolve().relative_to(BRAIN_ROOT)).replace("\\", "/")

    if not any(pat in rel for pat in ALLOWED_PATTERNS):
        print(
            f"BLOCKED: the shipping-agent cannot write to {rel} inside the brain.\n"
            f"  Allowed (brain-internal): quest-log/in-progress, quest-log/completed,\n"
            f"           inventory.\n"
            f"  Charts / CSVs / SQL belong OUTSIDE the brain (the shipping-agent\n"
            f"  workbench/ or the NFE work folder). Mart findings reach bank/ via\n"
            f"  alching, not by direct write.\n"
            f"  See meta/modes.md.",
            file=sys.stderr,
        )
        sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()
