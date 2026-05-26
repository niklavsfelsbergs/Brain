# Q-004 — `principal/` (you-model) and `self/` — same vault or separate?

**Status.** `resolved` in [[S003_main_brain_phase_1_scaffold]] via [[D-007_main_brain_phase_1_scaffold_landed]] (main brain's [[D-001_phase-1-scaffold]]). Opened in [[S001_dev_brain_architecture]].

**Resolution.** **Separate**, as Claude's instinct guessed. The split landed as:

- **`examine/`** — the agent-system self-model. Patterns, failure modes, calibrations the agent has noticed about itself. Global at root; also per-player (`players/<name>/examine/`) for character-specific self-knowledge.
- **`niksis8/`** — the model of Niklavs-the-human. Universal facts at the global root; per-player as `players/<name>/niksis8_character/` for what each player knows about Niklavs through their relationship.

Both layers use the same drafts → confirmed → archive/rejected discipline. Both have `confirmed/current.md` as the read target at respawn. Both are hook-protected against direct writes to `confirmed/`.

The asymmetry between global and per-player versions matters: the agent-system's self-knowledge accumulates across all players; Zezima's self-knowledge is specific to Zezima. Same for Niklavs — universal facts are global; what each player knows through their relationship is per-player.

See `gielinor/examine/_about.md`, `gielinor/niksis8/_about.md`, and the per-player versions.
