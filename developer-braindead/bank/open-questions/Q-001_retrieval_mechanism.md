# Q-001 — Retrieval mechanism for the main brain

**Status.** `resolved` in [[S003_main_brain_phase_1_scaffold]] via [[D-007_main_brain_phase_1_scaffold_landed]] (main brain's [[D-001_phase-1-scaffold]]). Opened in [[S001_dev_brain_architecture]].

**Resolution.** The retrieval mechanism is **layered, with explicit eager and lazy halves**:

- **Eager (at respawn).** `CLAUDE.md` (auto-loaded by Claude Code) `@import`s the rulebook from `gielinor/meta/`. The respawn ritual then reads `keepsake/current.md`, `examine/confirmed/current.md`, `niksis8/confirmed/current.md`, `lorebook/assumptions.md`, plus the active player's `CLAUDE.md`, `_about.md`, `persona.md`, and their per-player `keepsake/`, `examine/confirmed/current.md`, `niksis8_character/confirmed/current.md`. That's the bounded eager load.
- **Lazy (cued during session).** Everything else — `bank/notes/`, `spellbook/skills/`, rest of `lorebook/`, individual decisions — read on demand when the task requires. Each layer's `_about.md` is the entry point, read on first access.

Size budgets (~2k for keepsake/current.md, ~3k for examine and niksis8 current.md) keep the eager load bounded; bankstanding rotates stale content to archive.

The framing is exactly the brain-as-cascade noted in the original question: experience → reach into vault → next experience → next vault. Eager loads only what's needed to *act*; lazy loads what's needed to *answer specific questions*.

See `gielinor/spellbook/rituals/respawn.md` for the canonical load order.
