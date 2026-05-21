# S014 — 2026-05-21 — Shipping Data Mart TTYD how-to

**Status:** in-progress (Stream A landed, Stream B + recheck pending)
**Principal:** Niklavs
**Player:** Jebrim
**Born:** 2026-05-21
**External actions:** all completed. 5 dwarf spawns this session (D1 Redshift probe, D2 bi-etl walk, D3 template map, D4 connection harness, A scaffold). All returned successfully. Scaffold smoke test (`python -c "import db"`) passed. **No pending external actions.**
**Relationship to S002:** explicitly **separated**. S002 stays parked; this quest does NOT inherit S002's open investigations. Any S002-overlap finding (destination_country, ORWO classification, dim_products extension) is re-derived from scratch here, and unfinished items are surfaced as drafts for principal triage — no implicit carry-over.

## The ask

Produce an AI-facing "how to talk to the Shipping Data Mart" artifact, modeled on the TTYD template at `https://github.com/kpndavi/TTYD` (cloned locally at `NFE/projects/3_shipping_data_mart_TTYD/TTYD-template/`).

Two-phase order of work:

1. **Refresh in place** — bring `NFE/.claude/reference/shipping-data-mart/{overview,tables,sources}.md` to current truth using bi-etl `main` + live Redshift via MCP.
2. **Reshape into TTYD form** — populate `NFE/projects/3_shipping_data_mart_TTYD/` with the per-mart AI scaffold (how_to.md + entry points + connection harness + optionally viz pipeline + optionally semantic layer).

## Template shape (read this turn)

TTYD-template = full AI scaffold, not just docs. Parts:

- `how_to.md` — single source of truth. 8 sections: Pipeline Overview · Data Sources · Data Structure · Gold Layer Reference · Query Reference · Connecting to Redshift · Output Modes & Visualization · Artifact Rules.
- `CLAUDE.md` / `AGENTS.md` / `GEMINI.md` / `GROK.md` — per-AI entry points, all point at `how_to.md`.
- `db.py` + `connect_redshift.py` — shared psycopg2 harness. All scripts must import from `db.py` (rule in §6).
- `build_light_html_presentation.py` + `create_timestamped_presentation.py` — viz scaffolding scripts.
- `sample_queries.sql` — starter queries.
- `semantic-layer-draft.json` — LLM-grounding schema descriptor (size ~12.6kb, content TBD).
- `visualization-studio/` — Next.js app with per-AI subdirs under `content/presentations/<ai>/` and `content/generated/<ai>/`, canonical palette in `app/globals.css`, rules in `STANDARDS.md`.

Original TTYD target = `sl_gold.{dim_shops, fact_shop_daily}` (Shop Level mart). Our target = `enterprise_silver.{map_shipment_key, fact_shipments, fact_shipment_orderitems, fact_shipment_invoice_lines, fact_shipment_cost_summary, fact_truck_charges, dim_shipping_providers}` + `enterprise_bronze.dim_truck_costs`. Section 4 "Gold Layer Reference" does not map directly — needs rename to "Silver Layer Reference" or "Mart Reference".

## Current state of NFE/.claude/reference/shipping-data-mart/ (pre-refresh, audited this turn)

3 files, ~1k lines total. **Known stale spots** (from S002 D2/D3 dwarves, but the refresh re-derives all of these from scratch — listed here as alerts, not facts to import):

- `overview.md` claims "7 mart tables". Reality (per dwarves) likely 7-of-8 with `dim_carrier_sla` named in design but absent in repo + Redshift. Re-verify.
- `tables.md` says `fact_shipment_cost_summary` "feeds `fact_shipments.real_shipping_cost_*`" — verify it's wired and fresh.
- `sources.md` lists 4 source systems (PICT, PicaAPI, PCS, Rewallution). **ORWO entirely absent.** Re-verify whether ORWO is now a 5th source in V1.
- `overview.md` v1 scope filter "PICT + PicaAPI only" on `fact_shipments` — verify against current `insert_to_silver.sql`.
- 23 carrier providers listed in `sources.md` — verify count + names + currency strategies against current bi-etl repo.

## Open questions for principal (before scope freeze)

1. **V1-state snapshot timing.** Snapshot today and patch post-launch (option a), OR wait for V1 to settle and snapshot once (option b)? My read: (a).
2. **Section 4 naming.** "Silver Layer Reference" vs "Mart Reference" vs adding a gold layer for shipping. My read: rename to "Mart Reference" — the silver-direct-to-consumer pattern is real for this mart.
3. **Connection harness.** Reuse TTYD `db.py` + `creds.env` + `mcp_test_user` verbatim? Or shipping-specific connection / role?
4. **Visualization studio scoping.** (i) copy as-is, (ii) skip entirely, (iii) lightweight HTML only.
5. **Semantic layer.** Author `semantic-layer-draft.json` for the shipping mart as part of this quest, or defer?
6. **Per-AI entry points.** Generate all four (CLAUDE / AGENTS / GEMINI / GROK) or just CLAUDE?
7. **Target date.** Is the artifact pre-V1-launch or post-V1-launch?

## Where we are

**Stream A landed clean. Stream B authoring still ahead. Mart still mid-update; ETL team behind schedule per principal.**

Scope fully locked. 5 dwarves returned this session (D1-D4 recon + A scaffold). All decisions confirmed (see T4 turn log). Stream A produced 18 working files in `NFE/projects/3_shipping_data_mart_TTYD/`: scaffold tree copied, `db.py`/`connect_redshift.py` adapted to pull creds from `NFE/.env`, `sample_queries.sql` rewritten, viz-studio retargeted (4 files), `how_to.md` skeleton with §5/§6/§7/§8 + §4 gold-banner. Smoke test passed.

Stream B = principal-Jebrim authoring work in main context. Authoring proceeds **without** waiting for mart refresh — write against today's truth with `> Status: in progress (2026-05-21)` blocks for unstable items. Re-probe D1 when mart settles (post-ETL-catch-up) and patch the status blocks in a single sweep.

**Decision summary (load this verbatim into next session's context):**
1. Cost rollup cols (`fact_shipments.{real_shipping_cost_eur, final_shipping_cost_eur, cost_source, currency_code}`) WILL be populated — current 100% NULL is treated as mid-update state, not deprecation. Doc Phase 5 UPDATE as intended-populated. If still NULL at recheck, flag inline.
2. ORWO = 5th source in `sources.md`, with attribute-level status blocks per V1-critical column (destination_country, revenue_eur, product_key, carrier timestamps, cost cols). Status format: `> **Status: in progress (YYYY-MM-DD).** ...`.
3. `how_to.md` §5 = join rules only. No CM1/CM2-style derived-metric centerpiece. Skip the "Margin definitions" subsection entirely.
4. §4 banner verbatim: *"V0 of the Shipping Data Mart documents the silver-layer contract. A Gold-layer promotion (schema name TBD) is a V1 finishing-touch landing 2026-05-22. This section will be regenerated against gold once the migration lands; treat current silver column names as transitional."*

**Self-decided (no principal input needed unless they object on review):**
- Shipping silver canonical names = current (`map_shipment_key`, `fact_shipments`, `fact_shipment_orderitems`, `fact_shipment_invoice_lines`, `fact_shipment_cost_summary`, `fact_truck_charges`, `dim_shipping_providers`, `enterprise_bronze.dim_truck_costs`).
- Grain language: "1 row per `shipment_id`" (per-table specifics in §4).
- No `dim_carrier`, `dim_lane`, `dim_source_system` — mart has no other dims at V0.
- Drop `connect_redshift.ps1` reference from §6 (template mentions it without shipping it).
- Visualization Studio title stays generic.
- `requirements.txt` polars NOT added (pandas pipeline-locked in `build_light_html_presentation.py`).
- `db.py` library choice: stay with template's psycopg2 (closer to upstream); hardcode HOST/PORT/DB to NFE convention (`bi.c5lrs7vtwcpl.eu-central-1.redshift.amazonaws.com`, `5439`, `bi_stage_dev`); pull USER/PASSWORD from `NFE/.env` via `dotenv.find_dotenv()`.

## Next concrete step — for next session

Stream B authoring, in this order:

1. **Refresh `NFE/.claude/reference/shipping-data-mart/overview.md`** against D1+D2 truth: 7 silver tables + 1 bronze dim (drop `dim_carrier_sla` references), 5 source systems (add ORWO with attribute-empty status block), orchestrator = 6 phases (correct docstring stale). Use D1 row counts + D2 commit hashes inline. Status blocks for: `fact_shipments` cost-rollup cols 100% NULL, ORWO attribute-empty cols, gold-layer pending.
2. **Refresh `NFE/.claude/reference/shipping-data-mart/tables.md`** — drop `dim_carrier_sla` section entirely. Per-table accuracy pass against D2's last-modified commits. Cost-rollup status block on `fact_shipments` table section.
3. **Refresh `NFE/.claude/reference/shipping-data-mart/sources.md`** — add ORWO as 5th source. Re-verify 23 carrier list against D2's `sql/providers/` count (14 aggregated + 9 granular + 4 deferred). Confirm currency strategies still 5 distinct.
4. **Author `how_to.md` §1 Pipeline Overview** at `NFE/projects/3_shipping_data_mart_TTYD/how_to.md` — replace the TBD placeholder. Source from refreshed `overview.md`. Mart shape + business questions + phases.
5. **Author `how_to.md` §2 Data Sources** — 5 source systems + ORWO status block + carrier inventory.
6. **Author `how_to.md` §3 Data Structure** — bronze/silver/(eventual)gold layers + key transformation patterns + canonical join shape.
7. **Author `how_to.md` §4 Silver Layer Reference** — banner already in place. Per-table reference under it (7 silver + 1 bronze), columns + grain + sources + status blocks for unstable cols.
8. **Recheck trigger.** When principal cues mart-update settled → re-run D1 Redshift probe → patch every `> Status: in progress (2026-05-21)` block with post-update facts. Single sweep.
9. **Side-issue surfacing.** Flag ORPS creds-in-source incident separately (task #6). Not in this quest's deliverable.

**Optional next step before Stream B starts:** ask principal whether to commit the `NFE/projects/3_shipping_data_mart_TTYD/` Stream A scaffold to the bi-analytics-main repo now, or wait until Stream B is done.

## Files / paths to read first — for next session

1. **This file** — resume context.
2. **Dwarf reports (recon — fresh from this session):**
   - `S014_d1_redshift_probe.md` — live mart state. **Key findings:** 7 silver tables + 1 bronze dim, `dim_carrier_sla` absent, `fact_shipments` cost-rollup cols 100% NULL across all 18.5M rows, ORWO is largest source by item count but attribute-empty.
   - `S014_d2_bi_etl_walk.md` — repo state. **Key findings:** `Shipping_Data_Mart` PascalCase canonical, no gold layer in repo, orchestrator actually 6 phases (Phase 0 window-gate added 2026-05-14), `dim_shipping_providers/sql/upsert_to_silver.sql:20` has NGE-XXXX placeholder.
   - `S014_d3_template_map.md` — per-file action verdicts on TTYD template.
   - `S014_d4_connection_harness.md` — `NFE/.env` has only USER+PASSWORD; host/port/db hardcoded per NFE convention. Bridge plan implemented in Stream A.
   - `S014_a_scaffold.md` — Stream A landing report.
3. **NFE current reference set (Stream B refresh targets, in this order):**
   - `bi-analytics-main/NFE/.claude/reference/shipping-data-mart/overview.md`
   - `bi-analytics-main/NFE/.claude/reference/shipping-data-mart/tables.md`
   - `bi-analytics-main/NFE/.claude/reference/shipping-data-mart/sources.md`
4. **Scaffold in place (Stream B authoring target):**
   - `NFE/projects/3_shipping_data_mart_TTYD/how_to.md` — §5/§6/§7/§8 + §4 gold-banner already written. §1/§2/§3/§4 carry `<!-- TBD: authoring by principal-Jebrim, Stream B -->` placeholders.
   - `NFE/projects/3_shipping_data_mart_TTYD/db.py` + `connect_redshift.py` + `sample_queries.sql` — adapted, smoke-tested.
5. **TTYD template (reference only — kept intact at `NFE/projects/3_shipping_data_mart_TTYD/TTYD-template/`):**
   - `TTYD-template/how_to.md` — section-by-section reference for §1-§4 authoring style.
   - `TTYD-template/semantic-layer-draft.json` — for future shipping semantic-layer authoring (deferred).
6. **bi-etl repo (truth source side 1 — git pull before reading):**
   - `Documents/GitHub/bi-etl/dags/enterprise_silver/Shipping_Data_Mart/` (PascalCase, confirmed by D2). Re-check for any gold-layer commit before Stream B authoring.
7. **Redshift live (truth source side 2 — re-probe when mart settles):**
   - Same 7+1 tables via `mcp__redshift__*`. Same probes as D1; capture deltas.

## Constraints (from principal, this session)

- AI-facing artifact, not human-facing.
- TTYD-template is the structural template. Cloned, no upstream push, no fork relationship.
- Refresh `.claude/reference/` files in place first, then reshape into the new project dir.
- **S002 parked.** No carry-over. Re-derive from scratch.
- Unfinished items become drafts for principal triage. Principal flags pre-V1 vs post-V1.

## Turn log

- T1 (2026-05-21): Principal opens quest. Asked clarification on 5 points; answered with: AI-facing, V1-final-stretches, refresh in place, pure (no S002), unfinished items as drafts. Read TTYD template files + NFE reference set this turn. Surfaced 7 follow-up questions on shape (V1 snapshot timing, section 4 naming, connection harness, viz scoping, semantic layer, AI entry points, target date). Awaiting answers.
- T2 (2026-05-21): Principal answered 7 questions. **Locked scope:** (a) markdown how_to.md first, semantic layer deferred; (b) §4 = "Silver Layer Reference" with gold-migration banner (gold is V1 finishing-touch, name TBD); (c) reuse template connection pattern pointed at `NFE/.env`; (d) **visualization studio KEPT** (correction from earlier drop); (e) all 4 AI entry points, only how_to.md is shipping-specific; (f) inline status block convention adopted for unfinished items. **Spawning 4 Jebrim-inherited dwarves in parallel.** D1 Redshift probe (mcp__redshift__*), D2 bi-etl repo walk, D3 TTYD template structural map, D4 NFE .env + connection harness audit. Each writes to sibling file `S014_dN_*.md`. Pending until dwarves return.
- T3 (2026-05-21): All 4 dwarves returned. **Findings:** (i) mart is 7 silver tables + 1 bronze dim — `dim_carrier_sla` does NOT exist anywhere; (ii) `fact_shipments.{real_shipping_cost_eur, final_shipping_cost_eur, cost_source, currency_code}` are 100% NULL across all 18.5M rows / all source_systems (Phase 5 UPDATE appears not running mid-V1); (iii) ORWO is LARGEST source by item count (2.5M shipments, 90M orderitems) but attribute-empty — 100% NULL on destination_country, revenue_eur, product_key, all carrier timestamps, all cost cols; (iv) no gold layer in Redshift or repo yet; (v) orchestrator is actually 6 phases not 5 (Phase 0 window-gate added 2026-05-14, docstring stale); (vi) TTYD-template = 39 files, biggest adapt = how_to.md (283 lines), viz-studio mostly copy-as-is (only 4 files need retargeting); (vii) NFE/.env carries only REDSHIFT_USER + REDSHIFT_PASSWORD (host/port/db must be hardcoded per NFE convention via `redshift_connector` or psycopg2 with find_dotenv). **Side-issue surfaced:** ORPS probe scripts at `NFE/projects/1_shipping_data_mart/investigation/ORPS_sources/{pull_samples.py,_probe.py}` embed Postgres DSN incl. password in source — creds-in-git, rotation candidate, NOT blocking this quest.
- T4 (2026-05-21): Surfaced 4 decisions to principal. **Locked:** (1) cost rollup cols WILL be populated (Phase 5 likely mid-update incident, not deprecated); (2) ORWO documented as 5th source with attribute-level status blocks (a lot closing today); (3) §5 = join rules only, no derived-metrics centerpiece; (4) gold-banner wording approved verbatim. Lower-priority opens self-decided: shipping silver canonical names = current, grain = 1 per shipment_id, no dim_carrier/dim_lane, drop `connect_redshift.ps1` reference, viz studio title stays generic, polars deferred. **HOLD STATE.** Mart is updating live; will recheck D1 (Redshift probe) once principal cues. No authoring this session until post-update state captured.
- T5 (2026-05-21): Principal pivot — ETL team's behind, can't wait for mart refresh. "We have to start building. We can correct later." Re-sorted work into 3 buckets: A) mart-state-independent (template copy, db.py adapt, viz-studio retarget, §5-§8 + §4 banner) — fully buildable now; B) mart-state-sensitive but buildable with status blocks (§1-§4 content, NFE reference refresh); C) genuinely blocked (final smoke test, gold-section regeneration, final ORWO %). Proposed A as one Jebrim-inherited dwarf, B as principal-Jebrim sequential authoring, C deferred. Principal approved.
- T6 (2026-05-21): Spawned Stream A dwarf. 18 files written into `NFE/projects/3_shipping_data_mart_TTYD/`. `db.py` smoke test passed. Dwarf judgment calls: `find_dotenv(filename=".env", usecwd=False)` for cwd-independent resolution, `:shipment_id_placeholder` psycopg2 bind syntax in sample_queries.sql query #5, deleted the shop-margin Codex JSON sample outside the brain (no-delete rule scopes to gielinor/). Tasks #1/#4/#5 closed; #3 advanced to "skeleton done, §1-§4 pending".
- T7 (2026-05-21): Principal asked clarifying questions on (a) creds source, (b) `:shipment_id_placeholder`, (c) what was dropped. Re-read `db.py` + `sample_queries.sql` + scaffold quest-log to answer precisely. All three answered.
- T8 (2026-05-21, close): Close-session ritual. Tightened resume sections. Harvested observations into drafts (see Pending drafts section). Committed brain side. bi-analytics commit deferred — pending principal call.
