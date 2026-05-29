#!/usr/bin/env python3
# Architectural guarantee #5: gnomes have a restricted write surface.
# Active only when the PreToolUse payload carries agent_type == "gnome".
# Claude Code populates agent_id + agent_type in the JSON payload when a tool
# call originates inside a sub-agent context; env vars are NOT propagated, so
# gating on os.environ would leave the boundary silently inert.
# (Original S019 implementation gated on CLAUDE_BRAIN_GNOME=1; fixed
# 2026-05-21 in the [[S020]] dev-brain ratification pass.)
#
# Gnomes are system-namespace structural housekeepers. They run session-close,
# per-player alching, and drafts-triage. They write across players when the
# ritual demands it (e.g., a bankstanding-spawned gnome alching player N).
#
# Gnomes may write to (anywhere under brain root that matches):
#   - /bank/drafts/           and  /bank/notes/
#   - /quest-log/in-progress/, /quest-log/completed/, /quest-log/archive/
#   - /inventory/
#   - /examine/drafts/        (global and per-player)
#   - /niksis8/drafts/        (global)
#   - /niksis8_character/drafts/
#   - /keepsake/proposals/    (global and per-player)
#   - /spellbook/drafts/      and  /spellbook/skills/
#   - /lorebook/drafts/
#   - /players/inbox/
#   - /last-alched.md           (per-player alching stamp; gnomes run alching, so they close it — B-010)
#   - any /archive/ or /rejected/ path (housekeeping moves)
#
# Gnomes may NOT write to:
#   - /confirmed/                 (same line dwarves hold; also block-confirmed-writes.py enforces this)
#   - /lorebook/decisions/        (principal canonicalizes; gnomes draft)
#   - /keepsake/current.md        (user-only pin surface)
#   - /meta/                      (user-only rulebook)
#   - /spellbook/rituals/         (user-only at every scope)
#   - any CLAUDE.md / CLAUDE.local.md (principal-edited body)
#   - .mcp.json / ticks.md / settings.json / .claude/agents/ / .claude/hooks/
#
# See meta/modes.md and spellbook/skills/spawning-gnomes.md.

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
    "/bank/drafts/",
    "/bank/notes/",
    "/quest-log/in-progress/",
    "/quest-log/completed/",
    "/quest-log/archive/",
    "/inventory/",
    "/examine/drafts/",
    "/niksis8/drafts/",
    "/niksis8_character/drafts/",
    "/keepsake/proposals/",
    "/spellbook/drafts/",
    "/spellbook/skills/",
    "/lorebook/drafts/",
    "/players/inbox/",
    "/last-alched.md",
    "/archive/",
    "/rejected/",
]

# Explicit blocklist — paths that might match an allowed pattern but should
# still be blocked. Checked after the allow-list match.
BLOCKED_SUBSTRINGS = [
    "/confirmed/",
    "/lorebook/decisions/",
    "/keepsake/current.md",
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
        print(f"gnome-write-boundary: bad payload: {e}", file=sys.stderr)
        sys.exit(0)

    if payload.get("agent_type") != "gnome":
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

    # Hard blocks take precedence over allow-list matches.
    for blk in BLOCKED_SUBSTRINGS:
        if blk in rel:
            log_event("gnome-boundary", "block", actor="gnome", sid8=(payload.get("session_id") or "")[:8], path_class=classify_path(rel), detail=rel)
            print(
                f"BLOCKED: gnomes cannot write to {rel}.\n"
                f"  Hit blocked substring: {blk}\n"
                f"  Identity layers, rulebook, rituals, and body files are principal-only.\n"
                f"  See meta/modes.md and spellbook/skills/spawning-gnomes.md.",
                file=sys.stderr,
            )
            sys.exit(2)

    if not any(pat in rel for pat in ALLOWED_PATTERNS):
        log_event("gnome-boundary", "block", actor="gnome", sid8=(payload.get("session_id") or "")[:8], path_class=classify_path(rel), detail=rel)
        print(
            f"BLOCKED: gnomes cannot write to {rel}.\n"
            f"  Path is outside the gnome write surface.\n"
            f"  Allowed: drafts/, proposals/, inventory/, quest-log/, archive/,\n"
            f"           rejected/, players/inbox/, bank/notes/, spellbook/skills/.\n"
            f"  See meta/modes.md and spellbook/skills/spawning-gnomes.md.",
            file=sys.stderr,
        )
        sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()
