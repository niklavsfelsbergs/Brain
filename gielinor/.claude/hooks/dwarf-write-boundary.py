#!/usr/bin/env python3
# Architectural guarantee #3: dwarves have a restricted write surface.
# Active only when the PreToolUse payload carries agent_type == "dwarf".
# Claude Code populates agent_id + agent_type in the JSON payload when a tool
# call originates inside a sub-agent context; env vars are NOT propagated, so
# gating on os.environ would leave the boundary silently inert.
# (Original implementation gated on CLAUDE_BRAIN_DWARF=1; fixed 2026-05-21
# in the [[S020]] dev-brain ratification pass alongside the gnome fix.)
#
# Dwarves may write to:
#   - bank/notes/...            (any player)
#   - quest-log/in-progress/... (any player)
#   - quest-log/completed/...   (any player)
#   - quest-log/traces/...      (any player — the sub-agent's own run-log trace; B-020)
#   - inventory/...             (any player)
#
# Identity-shaped layers (examine/, niksis8/, niksis8_character/, lorebook/,
# keepsake/) and the rulebook (meta/, spellbook/rituals/) are off-limits to
# dwarves entirely — those changes come from principal reflection, not from
# task-execution by a sub-agent.
#
# See meta/modes.md for the full picture.

import json
import os
import sys
from pathlib import Path

# Ritual analytics (Khaan item 11) — best-effort; never breaks the hook.
_SB = Path(__file__).resolve().parents[3] / "switchboard"
if str(_SB) not in sys.path:
    sys.path.insert(0, str(_SB))
try:
    from ritual_log import log_event, classify_path
except Exception:
    def log_event(*a, **k): pass
    def classify_path(p): return ""

BRAIN_ROOT = Path(__file__).resolve().parent.parent.parent

ALLOWED_PATTERNS = [
    "/bank/notes/",
    "/quest-log/in-progress/",
    "/quest-log/completed/",
    "/quest-log/traces/",
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
        print(f"dwarf-write-boundary: bad payload: {e}", file=sys.stderr)
        sys.exit(0)

    if payload.get("agent_type") != "dwarf":
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
        log_event("dwarf-boundary", "block", actor="dwarf", sid8=(payload.get("session_id") or "")[:8], path_class=classify_path(rel), detail=rel)
        print(
            f"BLOCKED: dwarves cannot write to {rel}.\n"
            f"  Allowed: bank/notes, quest-log/in-progress, quest-log/completed,\n"
            f"           quest-log/traces, inventory.\n"
            f"  Identity layers and the rulebook are principal-only.\n"
            f"  See meta/modes.md.",
            file=sys.stderr,
        )
        sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()
