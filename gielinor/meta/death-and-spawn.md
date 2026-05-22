# Death and spawn

What happens when a session ends — cleanly or otherwise — and what is recovered when the next one begins.

## Death-as-crash

The session is interrupted unexpectedly. The agent's runtime context is gone; recovery depends entirely on what was committed to disk.

**Recovery discipline:**

- The session log appends to `quest-log/in-progress/` (of the active player) **every turn**, not at session end. Each turn writes its narrative update to the same file.
- Every external action is logged as `pending` before execution and updated to `completed` or `failed` after. The pending marker is the recovery signal: an in-progress quest-log entry with an unresolved `pending` action means a crash happened mid-action.
- A fresh session that finds an in-progress quest-log entry runs a **reconciliation prompt**: surface what was in flight, ask the principal how to proceed (resume, abandon, mark complete by hand). Exact shape of the prompt is deferred to real use.

## Death-as-reset

Deliberate fresh start. The principal chooses to begin again — possibly to test the system from cold, possibly because the working state has gotten incoherent.

**What persists across reset:**

| Layer | On reset |
|---|---|
| `inventory/` (all) | lost (volatile by design) |
| `quest-log/in-progress/` (all) | principal's choice — lose or carry forward |
| `quest-log/completed/` (all) | preserved |
| `bank/` (all) | preserved |
| `spellbook/` (all) | preserved |
| `examine/confirmed/`, `niksis8/confirmed/`, `niksis8_character/confirmed/` | preserved |
| All `drafts/` | lost (never canonical) |
| `keepsake/` (all) | always preserved |
| `lorebook/` | always preserved |
| `meta/` | always preserved |
| Body files (`CLAUDE.md`, `CLAUDE.local.md`, `.mcp.json`, `ticks.md`) | principal's choice |

The asymmetry is deliberate: confirmed knowledge and history survive; working state and unapproved proposals don't. Identity is durable; mid-thought is not.

Reset is rare. There's no `/reset` command yet — when the time comes, the action is "delete the listed layers, leave the rest."

## Death-as-migration

The agent moves to a new substrate — local Claude Code → VPS, or one host → another. This is Phase 3 work; the ritual is `spellbook/rituals/ascension.md` and does not exist yet.

When designed, ascension will preserve all layers (the whole brain travels) and update only the body — substrate-specific config in `.mcp.json`, scheduling in `ticks.md`, and possibly `CLAUDE.local.md`.

## Spawn

Session-start. Handled by `spellbook/rituals/respawn.md`. See that file for the load order.

## Related

- `spellbook/rituals/respawn.md` for the session-start ritual.
- `archive-discipline.md` for why "lost" still doesn't mean "deleted" anywhere it can be helped (in-progress quest logs that are abandoned move to `quest-log/archive/in-progress/`, not nowhere).
- `lorebook/confirmed/` for the choice to make confirmed/ durable and drafts/ ephemeral.
