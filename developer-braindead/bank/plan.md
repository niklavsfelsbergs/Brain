# plan.md — living plan, developer-braindead

> One mission, one plan, iterated. Sections have stable IDs (§A, §B, …) referenced from other docs. Updated as decisions land; old items marked done rather than deleted.
>
> **Item status.** `[ ]` open, `[~]` in progress, `[x]` done, `[-]` declined / out of scope (reason inline).

---

## §A — Foundation: developer-braindead bootstrapped

**Status.** `[~]` in progress.

- §A.1 `[x]` Folder created, initial eight canonical files seeded ([[S001]], [[D-002]], [[D-003]]).
- §A.2 `[x]` Session-start brain-selection protocol set ([[D-005]]).
- §A.3 `[x]` Claude's `~/.claude` memory reconciled to hold pointers into this folder rather than duplicate content ([[S002]], [[R-002]]).
- §A.4 `[x]` Dev brain restructured around RuneScape-themed layers for coherence with the main brain ([[D-006]], [[S002]]).

## §H — Identity layer + working agreements

**Status.** `[~]` in progress. Co-designed with user during [[S002]].

Section started life as "development rules layer" (the collaboration-contract framing). User redirected during [[S002]] to two parallel surfaces: **identity** (`examine/`, postures — how I decide) and **working agreements** (`player/working-agreements.md`, constraints — what we agree to). Both stay; they answer different questions.

- §H.1 `[x]` `examine/` created with [[I-001]] (migrated from [[S001]]'s P-001). Further entries accumulate naturally as moments arise — not designed upfront.
- §H.2 `[x]` Working agreements stays as a separate file from identity ([[S002]] resolution).
- §H.3 `[ ]` Brain-zone taxonomy (different parts of the brain warranting different levels of care). Original framing from end-of-[[S001]]. Lands in `player/working-agreements.md`.
- §H.4 `[ ]` Decide how identity entries interact with main brain ([[D-001]]). Some [[I-NNN]] may export to main brain's personality file; some are dev-only.

§B is no longer gated on §H — both can progress in parallel.

## §B — Main-brain architecture decisions

**Status.** `[x]` done in [[S003]] via [[D-007]] (main brain [[D-001]]). Main brain Phase 1 scaffold landed at `Documents/GitHub/brain/gielinor/`.

- §B.1 `[x]` Retrieval mechanism: eager-at-respawn (bounded identity loads) + lazy-cued during session via `_about.md` per layer ([[Q-001]] resolution).
- §B.2 `[x]` Vault top-level structure landed as: `meta/`, `examine/`, `niksis8/`, `keepsake/`, `lorebook/`, `spellbook/`, `players/` (plus body files at root and `.claude/`). Renamed from "vault/" to `gielinor/` ([[D-007]]).
- §B.3 `[x]` Personalities loadable as **players**, not as personas of Niklavs ([[Q-003]] resolution).
- §B.4 `[x]` Self/principal split: `examine/` (agent-system) vs `niksis8/` (you-model) at both global and per-player scope ([[Q-004]] resolution).
- §B.5 `[x]` Loading: minimal `CLAUDE.md` `@import`s rulebook from `meta/`; respawn ritual handles the rest ([[Q-006]] resolution). [[Q-005]] (capabilities in main brain) remains open separately.

## §C — Pilot: morning shipping-data routing check

**Status.** `[ ]` open. Drives concrete architecture choices once §B has direction.

- §C.1 `[ ]` Define data source (TBD — likely Niklavs's BI/analytics work context).
- §C.2 `[ ]` Define "concerning" (judgment, posture-dependent — ties to [[Q-003]]).
- §C.3 `[ ]` Define output channel for the morning report.
- §C.4 `[ ]` Wire scheduled trigger. Phase 2 territory; Phase 1 = manual invocation only ([[A-001]]).

## §D — Body files

**Status.** `[ ]` open. Most items wait on §B direction.

- §D.1 `[ ]` `CLAUDE.md` initial draft.
- §D.2 `[ ]` `CLAUDE.local.md` (secrets pattern).
- §D.3 `[ ]` `.mcp.json` (tool wiring — wait for pilot to dictate which servers).
- §D.4 `[ ]` `CRONTAB.md` (when scheduled triggers exist).

## §E — Gates layer

**Status.** `[ ]` open. Blocked on [[Q-002]].

- §E.1 `[ ]` Tiered tool permissions (read-only / write / external / irreversible).
- §E.2 `[ ]` Plan-then-act gate.
- §E.3 `[ ]` Sub-agent verification for risky actions.
- §E.4 `[ ]` Dry-run mode.
- §E.5 `[ ]` HITL surface ([[Q-002]]).

## §F — Triggers layer

**Status.** `[ ]` open.

- §F.1 `[ ]` Manual (Phase 1, [[A-001]]).
- §F.2 `[ ]` Scheduled (Phase 2).
- §F.3 `[ ]` Event-driven (Phase 2/3).
- §F.4 `[ ]` Reactive / messaging bridge (Phase 3).

## §G — Substrate decision (Phase 2)

**Status.** `[ ]` open. Defer until pilot validates Phase 1 architecture.

- §G.1 `[ ]` Routines (scheduled-only) vs VPS+Docker (event-driven). Driven by real needs, not preference.
