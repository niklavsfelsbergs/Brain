# plan.md — living plan, developer-braindead

> One mission, one plan, iterated. Sections have stable IDs (§A, §B, …) referenced from other docs. Updated as decisions land; old items marked done rather than deleted.
>
> **Item status.** `[ ]` open, `[~]` in progress, `[x]` done, `[-]` declined / out of scope (reason inline).

> **Reconciliation (2026-05-23, [[S060_brain_self_audit_and_plan_reconciliation]]).** This plan had not tracked reality since [[S003_main_brain_phase_1_scaffold]] — it described a foundation-and-pilot Phase 1 while ~55 sessions built a large, unplanned cognitive architecture instead. Reconciled this session per the [[S060_brain_self_audit_and_plan_reconciliation]] self-audit ([[D-027_inward_outward_build_imbalance]]). Headline: **the foundation (§A, §B) over-delivered; the operational half — §C pilot, §E gates, §F triggers, §G substrate — was never built. The agent is still manual-invocation-only.** The emergent pillars are now captured as §I–§M. The load-bearing next build is §C. See [[D-027_inward_outward_build_imbalance]] for the inward/outward imbalance this surfaced.

---

## §A — Foundation: developer-braindead bootstrapped

**Status.** `[x]` done. All four items landed ([[S001_dev_brain_architecture]]–[[S002_dev_brain_runescape_restructure]]).

- §A.1 `[x]` Folder created, initial eight canonical files seeded ([[S001_dev_brain_architecture]], [[D-002_folder_name]], [[D-003_initial_file_set]]).
- §A.2 `[x]` Session-start brain-selection protocol set ([[D-005_session_start_protocol]]).
- §A.3 `[x]` Claude's `~/.claude` memory reconciled to hold pointers into this folder rather than duplicate content ([[S002_dev_brain_runescape_restructure]], [[R-002]]).
- §A.4 `[x]` Dev brain restructured around RuneScape-themed layers for coherence with the main brain ([[D-006_dev_brain_restructure]], [[S002_dev_brain_runescape_restructure]]).

## §H — Identity layer + working agreements

**Status.** `[~]` in progress. Co-designed with user during [[S002_dev_brain_runescape_restructure]].

Section started life as "development rules layer" (the collaboration-contract framing). User redirected during [[S002_dev_brain_runescape_restructure]] to two parallel surfaces: **identity** (`examine/`, postures — how I decide) and **working agreements** (`player/working-agreements.md`, constraints — what we agree to). Both stay; they answer different questions.

- §H.1 `[x]` `examine/` created with [[I-001]] (migrated from [[S001_dev_brain_architecture]]'s P-001). Further entries accumulate naturally as moments arise — not designed upfront.
- §H.2 `[x]` Working agreements stays as a separate file from identity ([[S002_dev_brain_runescape_restructure]] resolution).
- §H.3 `[ ]` Brain-zone taxonomy (different parts of the brain warranting different levels of care). Original framing from end-of-[[S001_dev_brain_architecture]]. Lands in `player/working-agreements.md`.
- §H.4 `[ ]` Decide how identity entries interact with main brain ([[D-001_phase-1-scaffold]]). Some [[I-NNN]] may export to main brain's personality file; some are dev-only.

§B is no longer gated on §H — both can progress in parallel.

## §B — Main-brain architecture decisions

**Status.** `[x]` done in [[S003_main_brain_phase_1_scaffold]] via [[D-007_main_brain_phase_1_scaffold_landed]] (main brain [[D-001_phase-1-scaffold]]). Main brain Phase 1 scaffold landed at `Documents/GitHub/brain/gielinor/`.

- §B.1 `[x]` Retrieval mechanism: eager-at-respawn (bounded identity loads) + lazy-cued during session via `_about.md` per layer ([[Q-001]] resolution).
- §B.2 `[x]` Vault top-level structure landed as: `meta/`, `examine/`, `niksis8/`, `keepsake/`, `lorebook/`, `spellbook/`, `players/` (plus body files at root and `.claude/`). Renamed from "vault/" to `gielinor/` ([[D-007_main_brain_phase_1_scaffold_landed]]).
- §B.3 `[x]` Personalities loadable as **players**, not as personas of Niklavs ([[Q-003]] resolution).
- §B.4 `[x]` Self/principal split: `examine/` (agent-system) vs `niksis8/` (you-model) at both global and per-player scope ([[Q-004]] resolution).
- §B.5 `[x]` Loading: minimal `CLAUDE.md` `@import`s rulebook from `meta/`; respawn ritual handles the rest ([[Q-006]] resolution). [[Q-005]] (capabilities in main brain) remains open separately.

## §C — Pilot: morning shipping-data routing check

**Status.** `[ ]` open — **and the load-bearing gap ([[S060_brain_self_audit_and_plan_reconciliation]], [[D-027_inward_outward_build_imbalance]]).** This was the original mission core: the agent doing real work on a trigger. It has never been built; §B "had direction" by [[S003_main_brain_phase_1_scaffold]] yet the pilot kept deferring while the cognitive architecture grew. Reframed as the next build — pick one recurring job a player already does by hand, wire the thinnest scheduled run on the harness scheduler (sidestepping §G), produce one artifact without the operator in the loop, dry-run/worktree-safe. Input needed: *which* job (Jebrim's / principal's call).

**Scoped pilot ([[S060_brain_self_audit_and_plan_reconciliation]]) — daily shipping-mart freshness audit.** Read-only health check on the gold `shipping_mart`, run every morning after the ~08:00 load. Output: a dated GREEN / flags-with-numbers report. **Build splits in two:** Braindead wires the scheduled-trigger mechanism (the reusable "hands"); Jebrim writes the SQL checks in `shipping-agent/` (the content). Parked at [[S060_brain_self_audit_and_plan_reconciliation]] close — built next session.

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

> **Emergent pillars (§I–§M).** Built across [[S004_main_brain_corrections_post_s003|S004]]–[[S059_2de9789c_switchboard_alching_wrapped_up_states|S059]], none in the original plan. Captured here at the [[S060_brain_self_audit_and_plan_reconciliation]] reconciliation so the plan reflects what exists. Details live in the referenced [[D-NNN]] decisions; these are the index.

## §I — Player roster (emergent)

**Status.** `[x]` live. The characters the agent embodies.

- §I.1 `[x]` **Jebrim** — analytical/data player. Heavily used; bank, examine, skills, research all populated. Layer audit in [[D-015_jebrim_layer_audit_outcomes]].
- §I.2 `[x]` **Zezima** — reflective player. Went live 2026-05-23 ([[S056_e433ac17_switchboard-osrs-chatbox]]); first real session + first alching.
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
- §K.2 `[x]` **Gnomes** — structural housekeepers ([[D-016_gnomes_subagent]]); live in [[S021_visualizer_audit|S021]]/[[S030_penguins_subagent_and_research_folder|S030]]/[[S034_guthix_consultation_mode|S034]].
- §K.3 `[x]` **Penguins** — research operatives + per-player `research/` ([[D-021_penguins_research_subagent]]); live [[S040_ideas_folder_at_brain_root|S040]]/[[S056_e433ac17_switchboard-osrs-chatbox|S056]].
- §K.4 `[x]` No sub-spawning from sub-agents (hook-enforced).

## §L — Guthix / deities layer (emergent)

**Status.** `[~]` built; consultation under-used.

- §L.1 `[x]` **Guthix** — caretaker deity; two modes, consultation + bankstanding ([[D-022_guthix_consultation_mode]]).
- §L.2 `[~]` Consultation mode is **mechanism-only** — zero captured runs to date ([[D-027_inward_outward_build_imbalance]]). Guthix bank empty after four bankstanding passes.

## §M — Observability & parallel-session coordination (emergent — the largest unplanned build)

**Status.** `[x]` mature; the dominant effort sink [[S032_terminal_switchboard_phases_1_and_2|S032]]–[[S059_2de9789c_switchboard_alching_wrapped_up_states|S059]] ([[D-027_inward_outward_build_imbalance]] flags the imbalance).

- §M.1 `[x]` **Visualizer → switchboard** — live session/state surface; map era retired, surface promoted to `switchboard/` ([[D-008_iso_replay_v0_over_three_js]]–[[D-010_visualizer_intent_narration]], [[D-014_visualizer_chat_panel]], [[D-020_terminal_switchboard]], [[D-026_switchboard_promotion]]).
- §M.2 `[x]` **Status sidecar + hooks** — per-session state machine ([[D-020_terminal_switchboard]]).
- §M.3 `[x]` **Parallel-session coordination** — parallel instances ([[D-017_parallel_player_instances]]), substrate isolation ([[D-018_parallel_session_substrate_isolation]]), parallel Braindead + dev comms ([[D-019_parallel_braindead_and_comms_channel]]), parallel player coordination + `comms/` ([[D-024_parallel_player_coordination]]).

---

> **Forward-parked pillars (§N+).** Researched and planned but deliberately not built yet. Captured so they resurface; not competing with the load-bearing §C build until unparked.

## §N — Semantic retrieval / RAG layer (parked 2026-05-26)

**Status.** `[ ]` parked — researched, phased, **gated on the Obsidian revamp** (in progress, principal-led). Full survey + phased plan in `bank/research/2026-05-26-rag-for-the-brain.md`. Headline finding: the brain is **already an agentic-search retrieval system** (grep + `@`-imports + `[[links]]`) — the architecture Claude Code/Cursor/Devin converged on *after* dropping RAG. So RAG enters narrow + additive, never as a grep replacement.

## §O — Obsidian integration (in progress 2026-05-26, principal-led)

**Status.** `[~]` started — research + dev-brain `D-`/`S-` link migration + the gielinor link migration all landed ([[S098_b53fca39_obsidian_fit_and_dlink_migration]], [[S099_acf8fc80_obsidian_quest_link_migration]], [[S104_78e596a8_obsidian_gielinor_link_migration]]); cross-brain refs answered (leave dangling). gielinor vault **eyeballed ([[S104_78e596a8_obsidian_gielinor_link_migration|S104]])** — graph verified, but surfaced that gielinor under-links (76% of files isolated) → **§O.6 backlink-enrichment APPLIED ([[S105_7c91117c_obsidian_o6_backlink_enrichment|S105]])** — prose-ref wrap across **both brains** at the principal's maximal scope (~2,550 wraps). One follow-up surfaced (§O.7 — `Q-`/`A-`/`I-`/`R-` bracketed-link drift). The §C outward pilot remains the load-bearing next step (§O is inward, serves §N).

The brain is already an Obsidian-shaped vault (`.md` + `[[wikilinks]]`); Obsidian adds a read/navigate/tend lens (graph, backlinks, Dataview). Stock Obsidian resolves links by *exact filename*, so the `[[ID]]` convention needed migrating to full-stem ([[D-004_stable_ids]] amended). Topology = **per-brain vaults**. Spec + rationale: `bank/research/obsidian-fit-and-migration-spec.md`.

- §O.1 `[x]` Research + fit assessment; mechanism decided (Option A — full-stem, no plugin); [[D-004_stable_ids]] amended.
- §O.2 `[x]` **dev-brain `D-` decision links migrated** — 341 rewrites / 97 files ([[S098_b53fca39_obsidian_fit_and_dlink_migration]]). **Verified in Obsidian 2026-05-26** ([[S099_acf8fc80_obsidian_quest_link_migration]]): opened `developer-braindead/` as a vault — the graph wired into one connected web (hubs at [[D-027_inward_outward_build_imbalance|D-027]]/plan/respawn/build-lessons), only the expected orphans (code-refs, placeholders, no-link files).
- §O.3 `[x]` **dev-brain quest (`S-`) links migrated** — 357 rewrites / 87 files ([[S099_acf8fc80_obsidian_quest_link_migration]]): 327 clean `[[SNNN]]`→main-entry + 30 per-occurrence dupe disambiguations ([[S038_brain_underutilization_diagnosis|S038]]/[[S060_brain_self_audit_and_plan_reconciliation|S060]]/[[S086_e668ec7e_brain-technical-docs|S086]] resolved by the authors' own context tags, principal-signed-off; [[S049_17e701eb_visualizer_state_aware_motion_and_action_line|S049]] moot — 0 inbound links). `_dN/_pN/_gN` run-logs fold to the main; link-TEXT only, no renames. **Verified in Obsidian 2026-05-26** (same eyeball as §O.2 — the session graph + backlinks light up).
- §O.4 `[x]` **gielinor/ — APPLIED ([[S104_78e596a8_obsidian_gielinor_link_migration]]).** **43 rewrites / 18 files**, link-TEXT only, no renames; re-run dry-run → **0 remaining** (129 full-stem links resolve). Applied after Guthix's B-008 committed (`79359db`) freed the gielinor write surface. Re-ran the dry-run **fresh** first — B-008 had moved 2 of the targets (a godly proposal → `proposals/archive/`, a Jebrim bank draft → `bank/notes/`) and added 1 new `[[S069]]` ref in `last-alched.md`, so the stale 42/17 → 43/18. **Convention-doc check: 0 hits** — gielinor's `meta/` ID-links are all real "See [[D-NNN]]" / "([[S058]])" cross-references, not format illustrations, so no `CONVENTION_DOCS` extension was needed (acf8fc80's worry (b) didn't bite). The 3 flagged dupes ([[S014_visualizer_polish_and_aesthetics_pass|S014]]/[[S062_switchboard_lifecycle_feed_persistent_server_peek|S062]]/[[S076_322cb5c3_cockpit-vscode-rename-and-focus|S076]] — per-player `SNNN` collisions) all have **0 inbound links** → untouched. **Verified in Obsidian 2026-05-26 ([[S104_78e596a8_obsidian_gielinor_link_migration]])** — graph renders, links resolve; the sparse graph is the *true content shape* (→ §O.6), not a migration miss.
- §O.5 `[ ]` **Cross-brain refs — answered (leave dangling).** The gielinor dry-run found **18 explicit cross-brain links** ([[D-012]]×11, [[D-016]]×3, [[D-015]], [[I-003]], [[S018]], [[S083]] — all author-annotated "(dev brain)"); per the per-brain-vault model these *correctly* stay unresolved in gielinor's Obsidian (the annotation is the human signpost). Plus the 2 fuzzy [[D-001_two_brain_split|D-001]] calls (`plan.md:29`, `S003:13` in dev-brain) — both resolve, left as-set.
- §O.6 `[x]` **Backlink enrichment — APPLIED ([[S105_7c91117c_obsidian_o6_backlink_enrichment|S105]]).** Principal widened the narrow hand-off to the **maximal** scope: wrap *every* inline resolvable S/D-ref across **both brains**, quest-log prose included — not just the structured anchor field. New **`--mode prose`** in `obsidian-link-migrate.py` wraps UNbracketed resolvable IDs as `[[stem|ID]]` (display alias → prose reads identically; link-TEXT only, no renames, idempotent, git-reversible). **~2,422 clean wraps** (~241 files: knowledge layers + quest-log) + **129 dupe wraps** (10 ambiguous IDs disambiguated via a vault-local-guarded `PROSE_DUPE_RESOLUTION` table — same-session→canonical, `D-001/2` subtree rule for the `bank/decisions/` vs `main-brain-construction/` collision, topic rules for `S038`/`S062`/`S086`). Safety: resolve-to-real-file guard, prefix whitelist (kills `L2448`/`M365`/`T11` noise), self-ref skip, per-vault resolution (cross-brain stays dangling per §O.5). **Excluded** (valid targets, not sources): `inventory`/`archive`/`rejected` (volatile/dead), `comms`/`experiments`/`last-alched` (operational/runtime), `CLAUDE.md`/`meta/`/`spellbook/rituals` (user-only rulebook read as instructions). Verified: idempotent re-run 0 wraps/0 flagged, 0 renames, topic-exceptions spot-checked correct. *(Original scope note, for the record: bare anchors `**Observation (SNNN)**` / `## Anchor SNNN` / `Source: SNNN` were the seed; the maximal pass subsumes them.)*
- §O.7 `[ ]` **links-mode top-up — `Q-`/`A-`/`I-`/`R-` prefix drift (finding, [[S105_7c91117c_obsidian_o6_backlink_enrichment|S105]]).** dev links-mode reports **~103 bare `[[ID]]` bracketed links** still unmigrated — §O.2/O.3 only covered `D-`/`S-` prefixes, so `[[Q-001]]`/`[[A-002]]`/`[[I-003]]`/`[[R-001]]` are broken in Obsidian (no exact-filename match). Pre-existing in HEAD (NOT caused by §O.6 — prose mode only writes full-stem aliased links + skips already-bracketed). Fix = run `--mode links --apply` on dev with the prefix filter widened + the same per-occurrence treatment for the 7 flagged dupes it re-surfaces. Quick + safe (0 dangling) but re-opens dupe disambiguation, so deferred to a focused session. Inward; does NOT displace §C.
- §O.6-orig `[~]` *(superseded by §O.6 above)* The gielinor Obsidian graph is sparse (**350 files, 76% with zero `[[links]]`**) — NOT a migration miss (every resolvable ID-link resolves, 0 remaining) but because the convention was applied to *new* cross-refs, never to the **anchor field nearly every note already carries as plain text**: `examine/confirmed` entries open with `**Observation (SNNN, date)**` + close with `## Anchor SNNN`; `bank/notes` carry `Source: SNNN`. Those bare IDs are textbook backlinks to the source quest, just never wrapped. Jebrim sample: ~13 examine + ~6 bank = ~20 latent backlinks; pattern repeats across players. **Scope (recommended):** promote bare-text anchors → resolved `[[SNNN_full-stem]]` in `examine/confirmed` + `bank/notes` across all players; **SKIP `inventory`** (volatile/archived); **DEFER `quest-log` outbound** (80 isolated, bigger judgment lift). **Tooling:** a NEW script mode (or extend `obsidian-link-migrate.py`) that finds the *structured anchor refs* and wraps+resolves them — the existing migrator only rewrites *already-bracketed* `[[bare-ID]]`. **Caveat:** per-player `SNNN` dupes ([[S076_322cb5c3_cockpit-vscode-rename-and-focus|S076]]→5 files, [[S014_visualizer_polish_and_aesthetics_pass|S014]]/[[S062_switchboard_lifecycle_feed_persistent_server_peek|S062]]) need context disambiguation, exactly the dev-brain [[S038_brain_underutilization_diagnosis|S038]]/[[S060_brain_self_audit_and_plan_reconciliation|S060]]/[[S086_e668ec7e_brain-technical-docs|S086]] case acf8fc80 handled occurrence-by-occurrence. **Note:** touches `confirmed/` → mechanical + principal-led like the §O.4 migration ([[D-004_stable_ids]] amended). Primarily serves **§N (GraphRAG needs a graph to traverse)**; it is **inward — does NOT displace the §C outward pilot.**

- §N.0 `[ ]` **Gate — the Obsidian link migration applies** (NOT merely "Obsidian installed"). Speced live in `bank/research/obsidian-fit-and-migration-spec.md` (braindead-b53fca39): stock Obsidian resolves links by exact filename, so `[[D-027_inward_outward_build_imbalance]]`/`[[SNNN]]` links are ~91% phantom until a **one-time full-stem link-TEXT rewrite** (Option A, DECIDED 2026-05-26) runs. **Depends on b53fca39's forthcoming `D-NNN`.** Until then Obsidian's graph is unusable for retrieval.
- §N.1 `[ ]` **GraphRAG over `[[links]]`** (cheapest, first). Reads the *post-migration* resolved-link/backlink index for "N hops from X" in bankstanding + consultation. **Inherits the migration's classification semantics** (ID→main-entry; `_dN`/`_pN`/`_gN`/`-resume` = by-design clusters). **Per-brain vaults** ⇒ traversal can't cross the gielinor↔dev-brain boundary. Parse-only, no embeddings, no billing.
- §N.2 `[ ]` **Semantic-recall index** (only if §N.1 proves need). Local embeddings over `bank/notes/` + `research/` + `confirmed/`, scoped to bankstanding + consultation, metadata-filtered by layer/player/mode to respect the gates. Local model preferred (headless-billing). Eval Obsidian Smart Connections as build-vs-buy.
- §N.3 `[ ]` **Expose as MCP tool** — `semantic_recall` / `graph_neighbors` in `.mcp.json`; agent calls explicitly, grep stays primary.
