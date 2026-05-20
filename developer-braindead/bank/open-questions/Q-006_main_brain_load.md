# Q-006 — How does the main brain get its current architecture/personality loaded?

**Status.** `resolved` in [[S003]] via [[D-007]] (main brain's [[D-001]]). Opened in [[S001]].

**Resolution.** Three-part load:

1. **`CLAUDE.md` (auto-loaded by Claude Code).** Minimal — explains what the agent is, points to rituals, lists the four hooks, indexes the layers. The rulebook itself isn't in `CLAUDE.md`; instead `CLAUDE.md` `@import`s from `gielinor/meta/` (write-rules, modes, archive-discipline, drafts-mechanics, death-and-spawn). Single source of truth per rule.
2. **Respawn ritual (`gielinor/spellbook/rituals/respawn.md`).** Canonical load order — runs at session start. Reads identity layers, asks which player to embody, scopes in per-player layers, checks for in-progress quest-log entries (crash recovery), runs reconciliation prompt if needed.
3. **Per-player `CLAUDE.md`.** When a player is active, Claude Code's hierarchy loads the player's `CLAUDE.md` in addition to the master. The player's `CLAUDE.md` overrides where it adds — tone, in-scope tasks, character-specific tool notes.

Personality lands via the active player's `persona.md` (read in step 7 of the respawn ritual). Not a separate "current personality" file at the brain root.

The retrieval mechanism for the rest is covered by [[Q-001]] resolution — lazy/cued retrieval during the session.

See `gielinor/CLAUDE.md` and `gielinor/spellbook/rituals/respawn.md`.
