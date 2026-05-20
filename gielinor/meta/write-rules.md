# Write rules

Per-layer write discipline. Hooks enforce the most critical lines (see `.claude/hooks/`); this file documents the full picture, including the layers where discipline is guidance rather than architectural guarantee.

## The table

| Layer | Auto-write | Draft-then-approve | User-only |
|---|---|---|---|
| `bank/` (per-player) | yes, freely | when overturning existing knowledge | — |
| `quest-log/` (per-player) | yes (sessions log themselves turn-by-turn) | — | — |
| `spellbook/skills/` | — | new skills, modified procedures | — |
| `spellbook/rituals/` (global and per-player) | — | — | yes — core rituals are user-edited |
| `inventory/` (per-player) | yes (volatile) | — | — |
| `examine/` (global and per-player) | drafts only | all promotions to `confirmed/` | direct edits to confirmed entries |
| `niksis8/` and `niksis8_character/` | drafts only | all promotions to `confirmed/` | direct edits to confirmed entries |
| `keepsake/` (global and per-player) | proposals only (`keepsake/proposals/`) | all pinning to `current.md` | all edits to `current.md` |
| `lorebook/decisions/` | — | proposed entries via `lorebook/drafts/` | all confirmed decisions |
| `lorebook/assumptions.md` | — | proposed changes via `lorebook/drafts/` | all edits |
| `lorebook/patch-notes.md` | yes (factual record of changes) | — | — |
| `meta/*.md` | — | — | yes |

## The principle

Anything that defines who the agent thinks I am, who the agent (or a player) thinks it is, or what has been decided about the system requires my sign-off.

Knowledge and observations accumulate freely. Identity and core decisions are gated.

## What's enforced vs guided

**Hooks enforce (architectural):**

- No writes to any `confirmed/` path. Applies across all scopes — global `examine/`, `niksis8/`, per-player `examine/`, `niksis8_character/`.
- No file deletes. The agent moves files into the corresponding `archive/`.
- Dwarf write boundary (see `modes.md`).

**CLAUDE.md guides (discipline):**

- The "draft-then-approve" rows above. Hooks don't distinguish a proposed promotion from a routine edit, so the agent has to follow the draft flow on its own.
- The "overturning existing knowledge" exception in `bank/`. New facts merge freely; contradicting existing facts means a draft to `lorebook/drafts/` first.
- Treating `meta/` as user-controlled. Hooks could enforce this; for now it's discipline.

## Related

- `drafts-mechanics.md` for how the drafts flow actually works.
- `archive-discipline.md` for what "archive only" means structurally.
- `modes.md` for the dwarf-mode subset.
- `lorebook/decisions/` for *why* any of this is the way it is.
