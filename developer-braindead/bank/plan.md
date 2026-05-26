# plan.md — living plan, developer-braindead

> One mission, one plan, iterated. Sections have stable IDs (§A, §B, …) referenced from other docs. Updated as decisions land; old items marked done rather than deleted.
>
> **Item status.** `[ ]` open, `[~]` in progress, `[x]` done, `[-]` declined / out of scope (reason inline).

> **Reconciliation (2026-05-23, [[S060]]).** This plan had not tracked reality since [[S003]] — it described a foundation-and-pilot Phase 1 while ~55 sessions built a large, unplanned cognitive architecture instead. Reconciled this session per the [[S060]] self-audit ([[D-027_inward_outward_build_imbalance]]). Headline: **the foundation (§A, §B) over-delivered; the operational half — §C pilot, §E gates, §F triggers, §G substrate — was never built. The agent is still manual-invocation-only.** The emergent pillars are now captured as §I–§M. The load-bearing next build is §C. See [[D-027_inward_outward_build_imbalance]] for the inward/outward imbalance this surfaced.

---

## §A — Foundation: developer-braindead bootstrapped

**Status.** `[x]` done. All four items landed ([[S001]]–[[S002]]).

- §A.1 `[x]` Folder created, initial eight canonical files seeded ([[S001]], [[D-002_folder_name]], [[D-003_initial_file_set]]).
- §A.2 `[x]` Session-start brain-selection protocol set ([[D-005_session_start_protocol]]).
- §A.3 `[x]` Claude's `~/.claude` memory reconciled to hold pointers into this folder rather than duplicate content ([[S002]], [[R-002]]).
- §A.4 `[x]` Dev brain restructured around RuneScape-themed layers for coherence with the main brain ([[D-006_dev_brain_restructure]], [[S002]]).

## §H — Identity layer + working agreements

**Status.** `[~]` in progress. Co-designed with user during [[S002]].

Section started life as "development rules layer" (the collaboration-contract framing). User redirected during [[S002]] to two parallel surfaces: **identity** (`examine/`, postures — how I decide) and **working agreements** (`player/working-agreements.md`, constraints — what we agree to). Both stay; they answer different questions.

- §H.1 `[x]` `examine/` created with [[I-001]] (migrated from [[S001]]'s P-001). Further entries accumulate naturally as moments arise — not designed upfront.
- §H.2 `[x]` Working agreements stays as a separate file from identity ([[S002]] resolution).
- §H.3 `[ ]` Brain-zone taxonomy (different parts of the brain warranting different levels of care). Original framing from end-of-[[S001]]. Lands in `player/working-agreements.md`.
- §H.4 `[ ]` Decide how identity entries interact with main brain ([[D-001_phase-1-scaffold]]). Some [[I-NNN]] may export to main brain's personality file; some are dev-only.

§B is no longer gated on §H — both can progress in parallel.

## §B — Main-brain architecture decisions

**Status.** `[x]` done in [[S003]] via [[D-007_main_brain_phase_1_scaffold_landed]] (main brain [[D-001_phase-1-scaffold]]). Main brain Phase 1 scaffold landed at `Documents/GitHub/brain/gielinor/`.

- §B.1 `[x]` Retrieval mechanism: eager-at-respawn (bounded identity loads) + lazy-cued during session via `_about.md` per layer ([[Q-001]] resolution).
- §B.2 `[x]` Vault top-level structure landed as: `meta/`, `examine/`, `niksis8/`, `keepsake/`, `lorebook/`, `spellbook/`, `players/` (plus body files at root and `.claude/`). Renamed from "vault/" to `gielinor/` ([[D-007_main_brain_phase_1_scaffold_landed]]).
- §B.3 `[x]` Personalities loadable as **players**, not as personas of Niklavs ([[Q-003]] resolution).
- §B.4 `[x]` Self/principal split: `examine/` (agent-system) vs `niksis8/` (you-model) at both global and per-player scope ([[Q-004]] resolution).
- §B.5 `[x]` Loading: minimal `CLAUDE.md` `@import`s rulebook from `meta/`; respawn ritual handles the rest ([[Q-006]] resolution). [[Q-005]] (capabilities in main brain) remains open separately.

## §C — Pilot: morning shipping-data routing check

**Status.** `[ ]` open — **and the load-bearing gap ([[S060]], [[D-027_inward_outward_build_imbalance]]).** This was the original mission core: the agent doing real work on a trigger. It has never been built; §B "had direction" by [[S003]] yet the pilot kept deferring while the cognitive architecture grew. Reframed as the next build — pick one recurring job a player already does by hand, wire the thinnest scheduled run on the harness scheduler (sidestepping §G), produce one artifact without the operator in the loop, dry-run/worktree-safe. Input needed: *which* job (Jebrim's / principal's call).

**Scoped pilot ([[S060]]) — daily shipping-mart freshness audit.** Read-only health check on the gold `shipping_mart`, run every morning after the ~08:00 load. Output: a dated GREEN / flags-with-numbers report. **Build splits in two:** Braindead wires the scheduled-trigger mechanism (the reusable "hands"); Jebrim writes the SQL checks in `shipping-agent/` (the content). Parked at [[S060]] close — built next session.

- §C.1 `[~]` **Data source** — gold `shipping_mart` via the `shipping-agent/` harness (`ship_mart_ro`, read-only, gold-only). Resolved.
- §C.2 `[~]` **What's "concerning"** — six checks: (1) recency vs the ~08:00 load, (2) volume vs trailing avg, (3) cost invariant `SUM(buckets)==total_eur==real_shipping_cost_eur`, (4) `cost_source` coverage vs baseline (invoice 65 / expected 24 / NULL 8 / avg 2), (5) order-item completeness, (6) cross-fact agreement. Thresholds: self-calibrate off a trailing window where possible; Jebrim sets the floors.
- §C.3 `[~]` **Output channel** — a dated report to a file first (zero side effect); Slack draft in Jebrim's voice only once trusted.
- §C.4 `[~]` **Scheduled trigger** — ~08:30 daily via the harness scheduler (sidesteps §G per [[D-027_inward_outward_build_imbalance]]); retires the manual-only [[A-001]] for this one job.

## §D — Body files

**Status.** `[~]` partial. §D.1 `CLAUDE.md` is live and substantial (brain-root router + `gielinor/` master + `developer-braindead/` + per-`meta/` rulebook). §D.3 `.mcp.json` exists at brain root and wires external servers (Slack confirmed; others as registered). §D.2 secrets pattern and §D.4 CRONTAB still open — CRONTAB waits on §F scheduled triggers.

- §D.1 `[ ]` `CLAUDE.md` initial draft.
- §D.2 `[ ]` `CLAUDE.local.md` (secrets pattern).
- §D.3 `[ ]` `.mcp.json` (tool wiring — wait for pilot to dictate which servers).
- §D.4 `[ ]` `CRONTAB.md` (when scheduled triggers exist).

## §E — Gates layer

**Status.** `[~]` partial — emerged differently than planned. The six hook-enforced write guarantees (no `confirmed/` writes, no deletes, dwarf/gnome/penguin write boundaries, no sub-spawning) are a *de facto* tiered-permission + gate layer (§E.1-adjacent). §E.2 plan-then-act lives as the Understanding/Plan preamble discipline. §E.3 sub-agent verification, §E.4 dry-run mode, §E.5 HITL ([[Q-002]]) still open.

- §E.1 `[ ]` Tiered tool permissions (read-only / write / external / irreversible).
- §E.2 `[ ]` Plan-then-act gate.
- §E.3 `[ ]` Sub-agent verification for risky actions.
- §E.4 `[ ]` Dry-run mode.
- §E.5 `[ ]` HITL surface ([[Q-002]]).

## §F — Triggers layer

**Status.** `[~]` only §F.1 (manual) lives, per [[A-001]]. §F.2 scheduled / §F.3 event-driven / §F.4 reactive never built — this is the operational gap §C is meant to break open. Retiring [[A-001]] is the trigger for the pilot.

- §F.1 `[ ]` Manual (Phase 1, [[A-001]]).
- §F.2 `[ ]` Scheduled (Phase 2).
- §F.3 `[ ]` Event-driven (Phase 2/3).
- §F.4 `[ ]` Reactive / messaging bridge (Phase 3).

## §G — Substrate decision (Phase 2)

**Status.** `[ ]` open. Still local Claude Code. [[D-027_inward_outward_build_imbalance]] proposes sidestepping this for the first pilot by using the harness's own scheduler as the Phase-1 substrate — defer the routine-vs-VPS call until a real need forces it.

- §G.1 `[ ]` Routines (scheduled-only) vs VPS+Docker (event-driven). Driven by real needs, not preference.

---

> **Emergent pillars (§I–§M).** Built across S004–S059, none in the original plan. Captured here at the [[S060]] reconciliation so the plan reflects what exists. Details live in the referenced [[D-NNN]] decisions; these are the index.

## §I — Player roster (emergent)

**Status.** `[x]` live. The characters the agent embodies.

- §I.1 `[x]` **Jebrim** — analytical/data player. Heavily used; bank, examine, skills, research all populated. Layer audit in [[D-015_jebrim_layer_audit_outcomes]].
- §I.2 `[x]` **Zezima** — reflective player. Went live 2026-05-23 ([[S056]]); first real session + first alching.
- §I.3 `[~]` Roster grows as need arises; no fixed cap.

## §J — Ritual system (emergent)

**Status.** `[x]` in force.

- §J.1 `[x]` **respawn** + **close-session** — session boundaries; close-session is the harvest pump ([[D-012_close_session_harvest_pump]]).
- §J.2 `[x]` **alching** — per-player tending; both players alched 2026-05-23.
- §J.3 `[x]` **bankstanding** — system-level cross-cutting tending (Guthix voice); four passes run (B-001…B-004).
- §J.4 `[x]` **drafts-triage** (`/drafts`) — lightweight promotion gate ([[D-023_close_the_promote_consult_loop]]). Built; not yet run standalone.

## §K — Sub-agent roles (emergent)

**Status.** `[x]` three roles shipped + live.

- §K.1 `[x]` **Dwarves** — task-local work within the repo.
- §K.2 `[x]` **Gnomes** — structural housekeepers ([[D-016_gnomes_subagent]]); live in S021/S030/S034.
- §K.3 `[x]` **Penguins** — research operatives + per-player `research/` ([[D-021_penguins_research_subagent]]); live S040/S056.
- §K.4 `[x]` No sub-spawning from sub-agents (hook-enforced).

## §L — Guthix / deities layer (emergent)

**Status.** `[~]` built; consultation under-used.

- §L.1 `[x]` **Guthix** — caretaker deity; two modes, consultation + bankstanding ([[D-022_guthix_consultation_mode]]).
- §L.2 `[~]` Consultation mode is **mechanism-only** — zero captured runs to date ([[D-027_inward_outward_build_imbalance]]). Guthix bank empty after four bankstanding passes.

## §M — Observability & parallel-session coordination (emergent — the largest unplanned build)

**Status.** `[x]` mature; the dominant effort sink S032–S059 ([[D-027_inward_outward_build_imbalance]] flags the imbalance).

- §M.1 `[x]` **Visualizer → switchboard** — live session/state surface; map era retired, surface promoted to `switchboard/` ([[D-008_iso_replay_v0_over_three_js]]–[[D-010_visualizer_intent_narration]], [[D-014_visualizer_chat_panel]], [[D-020_terminal_switchboard]], [[D-026_switchboard_promotion]]).
- §M.2 `[x]` **Status sidecar + hooks** — per-session state machine ([[D-020_terminal_switchboard]]).
- §M.3 `[x]` **Parallel-session coordination** — parallel instances ([[D-017_parallel_player_instances]]), substrate isolation ([[D-018_parallel_session_substrate_isolation]]), parallel Braindead + dev comms ([[D-019_parallel_braindead_and_comms_channel]]), parallel player coordination + `comms/` ([[D-024_parallel_player_coordination]]).

---

> **Forward-parked pillars (§N+).** Researched and planned but deliberately not built yet. Captured so they resurface; not competing with the load-bearing §C build until unparked.

## §N — Semantic retrieval / RAG layer (parked 2026-05-26)

**Status.** `[ ]` parked — researched, phased, **gated on the Obsidian revamp** (in progress, principal-led). Full survey + phased plan in `bank/research/2026-05-26-rag-for-the-brain.md`. Headline finding: the brain is **already an agentic-search retrieval system** (grep + `@`-imports + `[[links]]`) — the architecture Claude Code/Cursor/Devin converged on *after* dropping RAG. So RAG enters narrow + additive, never as a grep replacement.

## §O — Obsidian integration (in progress 2026-05-26, principal-led)

**Status.** `[~]` started — research + dev-brain `D-` link migration pilot landed ([[S098]]); the rest parked behind the §C outward pilot.

The brain is already an Obsidian-shaped vault (`.md` + `[[wikilinks]]`); Obsidian adds a read/navigate/tend lens (graph, backlinks, Dataview). Stock Obsidian resolves links by *exact filename*, so the `[[ID]]` convention needed migrating to full-stem ([[D-004_stable_ids]] amended). Topology = **per-brain vaults**. Spec + rationale: `bank/research/obsidian-fit-and-migration-spec.md`.

- §O.1 `[x]` Research + fit assessment; mechanism decided (Option A — full-stem, no plugin); [[D-004_stable_ids]] amended.
- §O.2 `[x]` **dev-brain `D-` decision links migrated** — 341 rewrites / 97 files ([[S098]]). Verify-pending: open `developer-braindead/` as a vault, confirm graph + backlinks light up.
- §O.3 `[ ]` Extend to **dev-brain quest (`S-`) links** — handle the `SNNN_dN/_pN` convention groups (→ main entry) + the 3 real dupes (S038/S060/S086 — human renumber-or-leave).
- §O.4 `[ ]` Extend to **gielinor/** (its own vault; the larger surface).
- §O.5 `[ ]` Resolve the 2 fuzzy D-001 judgment calls; decide on cross-brain (~4%) refs (root `docs/` describing both brains).

- §N.0 `[ ]` **Gate — the Obsidian link migration applies** (NOT merely "Obsidian installed"). Speced live in `bank/research/obsidian-fit-and-migration-spec.md` (braindead-b53fca39): stock Obsidian resolves links by exact filename, so `[[D-027_inward_outward_build_imbalance]]`/`[[SNNN]]` links are ~91% phantom until a **one-time full-stem link-TEXT rewrite** (Option A, DECIDED 2026-05-26) runs. **Depends on b53fca39's forthcoming `D-NNN`.** Until then Obsidian's graph is unusable for retrieval.
- §N.1 `[ ]` **GraphRAG over `[[links]]`** (cheapest, first). Reads the *post-migration* resolved-link/backlink index for "N hops from X" in bankstanding + consultation. **Inherits the migration's classification semantics** (ID→main-entry; `_dN`/`_pN`/`_gN`/`-resume` = by-design clusters). **Per-brain vaults** ⇒ traversal can't cross the gielinor↔dev-brain boundary. Parse-only, no embeddings, no billing.
- §N.2 `[ ]` **Semantic-recall index** (only if §N.1 proves need). Local embeddings over `bank/notes/` + `research/` + `confirmed/`, scoped to bankstanding + consultation, metadata-filtered by layer/player/mode to respect the gates. Local model preferred (headless-billing). Eval Obsidian Smart Connections as build-vs-buy.
- §N.3 `[ ]` **Expose as MCP tool** — `semantic_recall` / `graph_neighbors` in `.mcp.json`; agent calls explicitly, grep stays primary.
