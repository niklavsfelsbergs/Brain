# D-006 — 2026-05-20 — Restructure dev brain into RuneScape-themed layered folders

**Supersedes.** [[D-003_initial_file_set]] (the original flat eight-file set).

**Context.** A parallel session designed the main brain's architecture around RuneScape-themed cognitive layers (`bank/`, `quest-log/`, `spellbook/`, `inventory/`, `examine/`, `player/`, `keepsake/`, `lorebook/`). The dev brain's flat file set ([[D-003_initial_file_set]]) worked as v0 but shared no vocabulary with the main brain. Restructuring around the same metaphor creates coherence across both surfaces.

**Decision.** Reorganize `developer-braindead/` into layered folders mirroring the main brain — but **stripped down**, because a working notebook is not a cognitive system. Keep only the layers that map naturally to "accumulated dev knowledge"; cut layers that exist for runtime behaviour.

**Layers kept (and what moved in):**
- `bank/` — semantic. Holds `plan.md` (was `PLAN.md`), `why.md` (new), `decisions/` (was `DECISIONS.md`), `assumptions/` (was `ASSUMPTIONS.md`), `open-questions/` (was `OPEN_QUESTIONS.md`), `risks/` (was `RISKS.md`), `research/` (new), `drafts/` (new), `archive/`.
- `quest-log/` — episodic. Per-session files (was `SESSION_LOG.md`). Filename pattern `SNNN_descriptive_name.md`, named at session close.
- `spellbook/` — procedural. Dev rituals: respawn, session-close, entry-formats.
- `examine/` — self-model. `identity.md` (was `PERSONALITY_LEDGER.md`, [[P-NNN]] → [[I-NNN]]). Holds my evolving postures for dev work.
- `player/` — user-model. `preferences.md` and `working-agreements.md`.
- `respawn.md` at root — entry point (was `HANDOFF.md`).
- `_about.md` per layer documenting its job and conventions.

**Layers cut and why:**
- `inventory/` — no working memory; dev brain doesn't run a cycle.
- `keepsake/` — no runtime priority; the single "read first" doc is `respawn.md` at root.
- `lorebook/` — the dev brain *is* the lorebook from the main brain's perspective. Recursive.

**Conventions kept:**
- Per-entry files in `bank/` and `examine/`; stable IDs preserved in filenames (e.g., `D-001_two_brain_split.md`).
- `[[ID]]` wiki-link references unchanged; IDs are stable across the move.
- Nothing destroyed: superseded entries go to `archive/` mirroring active structure.

**Conventions adjusted:**
- Quest log files named `SNNN_descriptive_name.md` (named at session close, not start — you can't title a quest before completing it).
- `PERSONALITY_LEDGER` framing as "feeder to main brain personality" generalized to `examine/identity.md` as "dev-Claude's accumulated postures for working with Niklavs." Some entries may still export to main brain; others are dev-only.
- No layer-wide `drafts/` + `confirmed/` split. The main brain needs it for agent-generated content awaiting approval; dev brain doesn't. `bank/drafts/` exists as a single folder for Niklavs's half-formed sketches.

**Alternatives considered.**
- Extend the flat eight-file set — rejected; would diverge further from the main brain's vocabulary over time.
- Apply the main brain's full layer set 1:1 — rejected; forced mappings worse than dropping the metaphor (`inventory/`, `keepsake/`, `lorebook/` have no honest dev-brain role).
- Per-entry files everywhere including `plan.md` — rejected; one mission, one living plan, reads best as a single scroll.

**Consequences.**
- All existing wiki-link references ([[D-001]], [[S001_dev_brain_architecture]], etc.) preserve via stable IDs. Filename suffixes are descriptive, not load-bearing.
- The flat root files (`HANDOFF.md`, `SESSION_LOG.md`, `DECISIONS.md`, `ASSUMPTIONS.md`, `OPEN_QUESTIONS.md`, `PLAN.md`, `RISKS.md`, `PERSONALITY_LEDGER.md`) are removed in [[S002_dev_brain_runescape_restructure]].
- Claude memory (`~/.claude/.../memory/`) already updated in [[S002_dev_brain_runescape_restructure]] §A.3 to point at `developer-braindead/HANDOFF.md`; needs a follow-up to retarget at `respawn.md`.

**Session ref.** [[S002_dev_brain_runescape_restructure]].
