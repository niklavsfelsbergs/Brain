# `developer-braindead/` — about

The **dev brain**. A working notebook for building the agent. Not a cognitive system — no agent runs cycles over this. Read primarily by Niklavs; occasionally referenced by the main brain on explicit cue.

Distinct from the main brain (`vault/`, TBD). See [[D-001_two_brain_split]] for the two-brain split rationale.

## Layers

Structured around RuneScape-themed cognitive layers for coherence with the main brain — but **stripped down**, because a notebook is not a cognition. See [[D-006_dev_brain_restructure]] for the restructure decision and what was cut and why.

| Layer | Holds | Metaphor |
|---|---|---|
| `bank/` | Semantic: decisions, assumptions, open questions, risks, the plan, research, drafts | Items sorted, kept, withdrawn on demand |
| `quest-log/` | Episodic: per-session entries with quest names | Quest journal — time-bound narrative arcs |
| `spellbook/` | Procedural: dev rituals (respawn, session-close, entry formats) | Invoked, not just read |
| `examine/` | Self-model: my (dev-Claude's) evolving postures for this work | The "examine" verb — agent inspecting itself |
| `player/` | User-model: your preferences and our working agreements | Character info; the principal I work with |

**Cut from main-brain analogue:** `inventory/` (no working memory), `keepsake/` (no runtime priority), `lorebook/` (the whole dev brain *is* the main brain's lorebook). See [[D-006_dev_brain_restructure]].

## Conventions

- **Entry point.** `respawn.md` at root. Read first.
- **Per-entry files** inside `bank/` and `examine/`. Each entry has a stable short ID ([[D-NNN]], [[A-NNN]], [[Q-NNN]], [[R-NNN]], [[I-NNN]]) — IDs never reused, filename adds descriptive suffix (e.g., `D-001_two_brain_split.md`). See [[D-004_stable_ids]].
- **Quest log files** named `SNNN_descriptive_name.md`, named at session close (you can't title a quest before completing it). See `spellbook/session-close.md`.
- **Wiki-links** for cross-references, load-bearing across docs. Use the **full filename stem** with an optional `|ID` display alias (`[[D-001_two_brain_split|D-001]]`), not the bare `[[ID]]` — per the [[D-004_stable_ids]] amendment, so links resolve in Obsidian / any markdown tool. The ID prefix stays the stable anchor. Applies to **new** entries too, not just the one-time migration; see `spellbook/entry-formats.md`.
- **Plan is single-file** at `bank/plan.md` — one mission, one living plan, iterated.
- **Nothing destroyed.** Superseded entries move to the layer's `archive/`. Decisions are marked `**Status.** superseded by [[D-NNN]].` Pattern from main brain.
- **`drafts/`** inside `bank/` holds Niklavs's half-formed sketches before promotion. No layer-wide `drafts/` + `confirmed/` split — that's a main-brain concept for agent-generated content awaiting approval, which doesn't apply here.
- **Every layer has an `_about.md`** stating its job and conventions.
