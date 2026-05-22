#!/usr/bin/env python3
# Architectural guarantee #5: penguins have a restricted write surface.
# Active only when the PreToolUse payload carries agent_type == "penguin".
# Claude Code populates agent_id + agent_type in the JSON payload when a tool
# call originates inside a sub-agent context; env vars are NOT propagated, so
# gating on os.environ would leave the boundary silently inert.
# (Same payload-field gating as dwarf-write-boundary.py and gnome-write-boundary.py.)
#
# Penguins are functional research operatives. They gather external information
# (web, vendor docs, regulatory state, news) and produce research writeups.
# They write into the active player's research/ folder freely; everything else
# is off-limits, including bank/ — bank notes are *picked* from research during
# alching, not authored by the penguin.
#
# Penguins may write to (under brain root):
#   - /research/                (any player's; cross-player discipline is in the brief)
#   - /quest-log/in-progress/   (any player's — sibling run-log entry)
#   - /quest-log/completed/     (any player's — when penguin finishes)
#   - /quest-log/archive/       (any player's — housekeeping)
#   - /inventory/               (any player's — working state during research)
#
# Penguins may NOT write to:
#   - /confirmed/                  (architectural guarantee #1; also block-confirmed-writes.py)
#   - /bank/                       (research stays in research/; bank notes are picked during alching)
#   - any /drafts/                 (examine/, niksis8_character/, lorebook/, spellbook/, etc.)
#   - any /proposals/              (keepsake/)
#   - any /rejected/               (drafts triage is principal/gnome work)
#   - /keepsake/, /lorebook/, /examine/, /niksis8_character/   (introspective layers)
#   - /meta/                       (rulebook — user-only)
#   - /spellbook/rituals/          (rituals — user-only)
#   - any CLAUDE.md / CLAUDE.local.md (body — user-only)
#   - .mcp.json / ticks.md / .claude/settings* / .claude/agents/ / .claude/hooks/
#
# Penguins also cannot spawn further sub-agents — see block-sub-spawn.py.
#
# See meta/modes.md and spellbook/skills/spawning-penguins.md.

import json
import sys
from pathlib import Path

BRAIN_ROOT = Path(__file__).resolve().parent.parent.parent.parent

ALLOWED_PATTERNS = [
    "/research/",
    "/quest-log/in-progress/",
    "/quest-log/completed/",
    "/quest-log/archive/",
    "/inventory/",
]

# Explicit blocklist — checked first, takes precedence over allow-list matches.
# These are paths that could otherwise match an allow pattern (e.g., a stray
# /research/ subfolder under a forbidden tree) but should still be blocked.
BLOCKED_SUBSTRINGS = [
    "/confirmed/",
    "/bank/",
    "/drafts/",
    "/proposals/",
    "/rejected/",
    "/keepsake/",
    "/lorebook/",
    "/examine/",
    "/niksis8_character/",
    "/niksis8/",
    "/meta/",
    "/spellbook/rituals/",
    "/CLAUDE.md",
    "/CLAUDE.local.md",
    "/.mcp.json",
    "/ticks.md",
    "/.claude/settings",
    "/.claude/agents/",
    "/.claude/hooks/",
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
        print(f"penguin-write-boundary: bad payload: {e}", file=sys.stderr)
        sys.exit(0)

    if payload.get("agent_type") != "penguin":
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

    for blk in BLOCKED_SUBSTRINGS:
        if blk in rel:
            print(
                f"BLOCKED: penguins cannot write to {rel}.\n"
                f"  Hit blocked substring: {blk}\n"
                f"  Penguin write surface: research/, quest-log/, inventory/.\n"
                f"  Bank notes are picked from research/ during alching, not authored by penguins.\n"
                f"  Identity layers, drafts, rulebook, rituals, and body files are off-limits.\n"
                f"  See meta/modes.md and spellbook/skills/spawning-penguins.md.",
                file=sys.stderr,
            )
            sys.exit(2)

    if not any(pat in rel for pat in ALLOWED_PATTERNS):
        print(
            f"BLOCKED: penguins cannot write to {rel}.\n"
            f"  Path is outside the penguin write surface.\n"
            f"  Allowed: research/, quest-log/in-progress/, quest-log/completed/,\n"
            f"           quest-log/archive/, inventory/.\n"
            f"  See meta/modes.md and spellbook/skills/spawning-penguins.md.",
            file=sys.stderr,
        )
        sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()
