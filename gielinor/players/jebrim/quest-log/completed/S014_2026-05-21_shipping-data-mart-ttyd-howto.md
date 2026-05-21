# S014 — 2026-05-21 — Shipping Data Mart TTYD how-to

**Status:** in-progress (Stream A landed, reference-set refresh landed S015, how_to.md §1–§4 authoring + closeout still ahead)
**Principal:** Niklavs
**Player:** Jebrim
**Born:** 2026-05-21
**External actions:** all completed across all sessions. S015 (this close) added: git fetch on bi-analytics-main (no pull needed, up-to-date) + 16 Edits across `overview.md` / `tables.md` / `sources.md`. **No pending external actions.**
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

**Stream A landed + reference-set refresh landed (S015). T11 NULL classification locked. ORWO dedup priority locked at last. how_to.md §1–§4 authoring still ahead, then DQ subsection + bi-analytics commit + bank-note harvest at quest close.**

**bi-analytics-main working-dir state at S015 close.** 3 files modified, **NOT YET COMMITTED**:

- `NFE/.claude/reference/shipping-data-mart/overview.md`
- `NFE/.claude/reference/shipping-data-mart/tables.md`
- `NFE/.claude/reference/shipping-data-mart/sources.md`

These will be folded into the single Stream B commit (task #10) once §1–§4 authoring is done. Next session: do NOT commit reference-set refresh as its own commit; bundle it with the §1–§4 work.

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

**No resume trigger — pick up directly.** S015 closed the hold (T11/T13 lifted it). D1 re-probe is deferred to a separate post-V1 quest per principal call ("mart wont update, we proceed with what is"). Authoring proceeds against T11 classification + refreshed reference set.

**Task list state at S015 close** (in TaskCreate slots #1–#11):
- ✅ #1 overview.md — done
- ✅ #2 tables.md — done
- ✅ #3 sources.md — done
- ⏳ #4 author §1 Pipeline Overview — **next step**
- ⏳ #5 author §2 Data Sources
- ⏳ #6 author §3 Data Structure
- ⏳ #7 author §4 Silver Layer Reference (per-table under existing gold-banner)
- ⏳ #8 spot-check per-AI entry points (CLAUDE/AGENTS/GEMINI/GROK)
- ⏳ #9 add Known DQ / Open Investigations subsection to how_to.md (carries T11 Bucket 4)
- ⏳ #10 single Stream B commit to bi-analytics-main (reference refresh + §1–§4 + DQ subsection bundled)
- ⏳ #11 close S014 + harvest bank notes (mart NULL classification rubric harvest candidate per principal's "harvest from finished quests" rule)

Stream B authoring order (tasks #4–#9):

1. **§1 Pipeline Overview** — replace TBD placeholder in `NFE/projects/3_shipping_data_mart_TTYD/how_to.md`. Source from refreshed `overview.md`: mart shape (7 silver + 1 bronze), 5 sources w/ dedup chain `Picturator > PicaAPI > PCS > Rewallution > ORWO`, business questions, 6 phases. No status blocks (T11 cost cols are canonical, not status).
2. **§2 Data Sources** — 5 source systems. Source from refreshed `sources.md`. ORWO documented as 5th but with **no status block** (empty-by-design per T11). Carrier inventory: 14 agg + 9 granular + 4 deferred.
3. **§3 Data Structure** — bronze/silver/(eventual)gold layers + transformation patterns + canonical join shape on `shipment_id`. Gold-banner already in §4.
4. **§4 Silver Layer Reference** — banner already in place. Per-table reference under it: 7 silver (MSK, fact_shipments, fact_shipment_orderitems, fact_shipment_invoice_lines, fact_shipment_cost_summary, fact_truck_charges, dim_shipping_providers) + 1 bronze (dim_truck_costs). Apply T11 empty-by-design notes per-source per-column.
5. **Open Investigations subsection** — carry T11 Bucket 4 verbatim: carrier-ts coverage anomaly (Picturator ~34%, PicaAPI ~78%) + mart-wide empty-column audit (with `is_return` as known do-not-use example) + ORPS creds-in-source side-issue placeholder.
6. **Spot-check per-AI entry points** — CLAUDE/AGENTS/GEMINI/GROK at the project root should all point at `how_to.md`. Stream A populated these; verify.
7. **Single Stream B commit to bi-analytics-main** bundling all of the above (reference refresh + §1–§4 + DQ subsection).
8. **Close S014 + harvest.** Per T11 rule, harvest the mart NULL classification rubric as a Jebrim bank draft once the quest closes (harvest from finished work, not in flight). Candidate slug: `bank/drafts/notes/mart-audit-null-classification-rubric.md`.

**Stream A scaffold committed to bi-analytics-main** (confirmed by principal at T10, 2026-05-21). Reference-set refresh NOT YET committed — bundles into task #7.

## Files / paths to read first — for next session

1. **This file** — resume context. T11 (NULL classification, principal-authoritative) and T12/T13 (reference-set refresh details) are the load-bearing turns.
2. **Stream B authoring target (only file to edit for §1–§4 authoring):**
   - `bi-analytics-main/NFE/projects/3_shipping_data_mart_TTYD/how_to.md` — §5/§6/§7/§8 + §4 gold-banner already written. §1/§2/§3/§4 carry `<!-- TBD: authoring by principal-Jebrim, Stream B -->` placeholders.
3. **Refreshed reference set (Stream B authoring source — already up-to-date as of S015):**
   - `bi-analytics-main/NFE/.claude/reference/shipping-data-mart/overview.md` ← §1 source
   - `bi-analytics-main/NFE/.claude/reference/shipping-data-mart/sources.md` ← §2 source
   - `bi-analytics-main/NFE/.claude/reference/shipping-data-mart/tables.md` ← §3/§4 source
4. **TTYD template (reference only — kept intact):**
   - `bi-analytics-main/NFE/projects/3_shipping_data_mart_TTYD/TTYD-template/how_to.md` — §1–§4 authoring style reference.
5. **S014 dwarf reports (background context — read only if a question requires it; reference-set refresh already encodes their findings):**
   - `S014_d1_redshift_probe.md`, `S014_d2_bi_etl_walk.md`, `S014_d3_template_map.md`, `S014_d4_connection_harness.md`, `S014_a_scaffold.md`.
6. **bi-etl repo (truth source — re-pull only if §3/§4 authoring needs to verify a specific transformation pattern not captured in reference set):**
   - `Documents/GitHub/bi-etl/dags/enterprise_silver/Shipping_Data_Mart/` (PascalCase).

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
- T9 (2026-05-21, resume → re-hold): Principal opened session "lets continue on shipping mart TTYD". Surfaced resume foreground. **Principal reversed T5 build-now stance:** mart refresh still incomplete, and D1's empty-column readings reflect mid-refresh state — authoring Stream B now would bake in transient nulls as documented truth. **Stream B on hold until mart refresh settles, then re-run D1 probe before any §1–§4 authoring.** Reference-refresh (steps 1–3) also on hold for the same reason. Stream A scaffold remains landed in `NFE/projects/3_shipping_data_mart_TTYD/` regardless. Next-session trigger: principal cues "mart refresh done" or equivalent → re-probe D1 → resume Stream B.
- T10 (2026-05-21): Principal confirmed Stream A scaffold is already committed to bi-analytics-main. T6 optional-commit item closed. Standing by — no further action this session until mart refresh trigger.
- T11 (2026-05-21, build-now restart): Principal reversed T9 stand-by — "mart wont update, we need to proceed with what is." Walked through D1's empty-column inventory together; principal supplied authoritative sort. **Working NULL classification for Stream B authoring (V1 snapshot, principal-authoritative, 2026-05-21):**

  **Bucket 1 — Will fill (document as canonical, no status block):**
  - `fact_shipments.real_shipping_cost_eur` / `final_shipping_cost_eur` / `cost_source` / `currency_code` — all sources. (Cost rollup IS intended on fact_shipments; current 100% NULL is mid-refresh state.)
  - `fact_shipments.destination_country` (ORWO)
  - `fact_shipments.net_revenue_eur` (ORWO)
  - `fact_shipment_orderitems.revenue_eur` (ORWO)

  **Bucket 2 — Empty by design for V1 (document as "this source does not carry this attribute"):**
  - `fact_shipments.received_by_carrier_ts` / `delivered_by_carrier_ts` / `truckload_id` (ORWO)
  - `fact_shipments.weight_kg` (ORWO 47% NULL — package dims imperfect, acceptable for V1)
  - `fact_shipment_orderitems.revenue_eur` (PCS — intended, cost-data-only source)
  - `fact_shipment_orderitems.product_key` (ORWO — NULL by design, expected. **No special sku-as-product_key rule** — principal retracted, would draw confusion; iterate later.)

  **Bucket 3 — Known but tolerated:**
  - `map_shipment_key.updated_at` / `dw_timestamp` 100% NULL — ETL bug, not vital. Use `order_created_date` for recency.
  - 168k MSK keys without `fact_shipments` row — OK now, should clear later.
  - `fact_shipment_invoice_lines.shipment_id` 0.82% NULL — expected (not every charge finds a clean join).

  **Bucket 4 — Open investigations (flagged in how_to.md open-questions section, NOT this artifact's scope):**
  - **Carrier-event timestamp coverage** — Picturator ~34% NULL / PicaAPI ~78% NULL on `received_by_carrier_ts` / `delivered_by_carrier_ts`. Expected lower; investigate.
  - **Mart-wide empty-column audit** — find all 100%-NULL columns mart-wide, classify each as (a) defined-intended, (b) deprecated, (c) bugged, (d) empty-for-V1, (e) undefined / don't-use. `is_return` is one known example (table TBD — possibly different name from `is_reorder` on `fact_shipment_orderitems`). Until this audit runs, the "do not use" list in `how_to.md` stays open-ended.

  **Bucket 5 — Structural:**
  - `dim_carrier_sla` — out of scope V1, do not reference anywhere.
  - Gold schema — name TBD, migration 2026-05-22 (tomorrow). §4 keeps the gold-banner.

  **Bank-draft NOT created** — principal correction: "the notes stem from the quest, we don't know enough about the mart yet." Notes are harvested from finished work, not drafted in flight. Lesson saved to memory. Stream B authoring proceeds against this quest-log-resident classification only.
- T12 (2026-05-21): Reference-set refresh complete. Three files updated in `bi-analytics-main/NFE/.claude/reference/shipping-data-mart/` against D1+D2 truth + T11 classification:
  - **overview.md** — 4→5 source systems (ORWO), fact_shipments col 57→64 + dropped "PICT+PICAAPI only" v1 filter, orchestrator 5→6 phases (Phase 0 window-gate detail + 0a/0b), schedule `None`→`0 4 * * *` UTC, gold-migration banner (2026-05-22 TBD). ORWO dedup priority left as TBD-confirm-with-mart-owner.
  - **tables.md** — MSK ORWO source CTE added + MSK updated_at/dw_timestamp 100% NULL gotcha. fact_shipments: scope filter dropped, ORWO source branch added (Wolfen production_site), full NULL classification (do-not-use/no-source/ORWO-won't/ORWO-partial buckets), carrier-ts coverage anomaly gotcha. fact_shipment_orderitems: ORWO branch + Navision articlenumber backfill, ORWO product_key NULL-by-design note, ORWO 73% row-dominance gotcha. fact_shipment_invoice_lines: `shippingprovider` → `shippingprovider_extkey` rename (2026-05-20), ORWO carrier-distributive notes, 0.82% shipment_id NULL acceptable. fact_truck_charges: `cost_per_parcel_eur_smoothed` col added. **New `dim_shipping_providers` section** (was missing).
  - **sources.md** — 4→5 source systems header. New ORWO H3 (~30 lines covering identity, articlenumber backfill, V1 attribute classification per T11, volume dominance, dim_providers landed, NGE-XXXX allow-list placeholder). dim_shipping_providers cross-cutting section synced with tables.md (PK includes source_system, full ref in tables.md).
  - Tasks #1/#2/#3 closed. **One open question for principal:** ORWO's position in the dedup priority chain (currently flagged TBD in both `overview.md` and `sources.md`).
- T13 (2026-05-21): Principal locked ORWO dedup priority = last. Chain is now `Picturator > PicaAPI > PCS > Rewallution > ORWO`. Patched both `overview.md` and `sources.md` to drop the TBD flag. Reference-set refresh fully closed.
- T14 (2026-05-21, S016 open): Principal cued "lets continue on the TTYD". Surfaced resume foreground (Where we are / Next concrete step / Files), confirmed proceed. **Task #4 — §1 Pipeline Overview authored** in `bi-analytics-main/NFE/projects/3_shipping_data_mart_TTYD/how_to.md`. Replaced TBD placeholder. Content: intro para (silver-layer mart, 5 sources, 23 providers, shipment-grain), 5 business questions verbatim from overview.md, dedup chain in code block, 6 numbered phases with parallel groupings called out, schedule + refresh-mode footnote, 8-table active-output list (7 silver + 1 bronze with the bronze exception flagged), gold-layer V1 banner as blockquote at the tail. No status blocks (per T11: cost cols canonical). Style: matches TTYD template §1 register — concise prose + bulleted lists. Next: task #5, §2 Data Sources, source from refreshed `sources.md`.
- T15 (2026-05-21): **Task #5 — §2 Data Sources authored** in same file. Replaced TBD placeholder. Structure: intro splitting sources into 3 families + pointer to `NFE/.claude/reference/shipping-data-mart/sources.md` for column-level depth; **order/parcel systems (5)** as compact 5-row table (role, bronze prefix, identifier, currency) followed by per-source quick-notes bullets (PICT prod-site LIKE map + poc_landing TODOs, PicaAPI item-level print_destination + polymorphic address join, PCS rolling-window silver gotchas + bronze fallback, Rewallution empty-silver gotcha + NULL shippingprovider_extkey, ORWO Wolfen hardcode + articlenumber backfill + distributive carrier allocation + V1 empty-by-design attrs); **carrier invoice providers (23)** as inline name-lists split aggregated/granular/deferred with per-mode brief explanation + currency footer; **cross-cutting refs** (dim_shipping_providers PK-includes-source_system gotcha, shipping_charge_bucket_mapping ownership, dim_truck_costs pointer, currency_rates); **ingestion methods** as bulleted list. **No status blocks** (per T11: ORWO empty-by-design is canonical not status). Compact-table-over-H3-per-source decision: avoid bloating the AI artifact when reference file already carries depth. Next: task #6, §3 Data Structure, source from refreshed `tables.md`.
- T16 (2026-05-21): **Task #6 — §3 Data Structure authored** in same file. Replaced TBD placeholder. Structure: **layered architecture** (bronze → silver → eventual gold) with ASCII diagram + bronze/silver/gold paragraphs + legacy-schema list; **mart in shape** = 8-row role/grain table (spine + 5 facts + silver dim + bronze dim) with pointer to §4 for column-level; **canonical join shape** = `shipment_id` formula in code block + standard fact→spine→dim diagram + "fact_shipments does not carry source_system" reminder (avoids repeating §5's SQL); **key transformation patterns** = 7 bulleted patterns (source-priority dedup, full-refresh-with-UPDATE-backfills explaining Phase 3 NULL → Phase 5 fill, 23-carrier UNION ALL, pivot-and-backfill for cost summary with total_eur exclusion rule, FX normalization (5 strategies), Variant B truck allocation PCS-only, ORWO distributive carrier allocation). No status blocks. Decision: §3 sticks to architecture + patterns, §4 will own per-table column reference — avoids overlap. Next: task #7, §4 Silver Layer Reference (per-table under existing gold-banner), source from refreshed `tables.md`.
- T17 (2026-05-21): **Task #7 — §4 Silver Layer Reference authored** in same file. Existing gold-migration banner preserved at top; added pointer to `NFE/.claude/reference/shipping-data-mart/tables.md` + per-table READMEs at `bi-etl/dags/enterprise_silver/shipping_data_mart/<table>/README.md` for deeper specs. Per-table H3 sections for all 8 tables (7 silver + 1 bronze) in spine-fact-dim order: MSK, fact_shipments, fact_shipment_orderitems, fact_shipment_invoice_lines, fact_shipment_cost_summary, fact_truck_charges, dim_shipping_providers, dim_truck_costs (bronze, with "one mart table outside enterprise_silver" callout). Each section covers grain + key cols + sources + refresh mode + NULL classification (where applicable) + gotchas. **T11 NULL classification applied verbatim per source per column**: fact_shipments — `is_returned` undefined-do-not-use, 5 no-source-in-V1 cols, ORWO empty-by-design (received_by_carrier_ts / delivered_by_carrier_ts / truckload_id), ORWO partial (weight_kg ~47%); fact_shipment_orderitems — PCS revenue_eur 100% NULL by design, ORWO revenue_eur in-progress, ORWO product_key 100% NULL by design, always-NULL option_key/format_key; fact_shipment_invoice_lines — shipment_id 0.82% NULL acceptable; MSK — updated_at/dw_timestamp 100% NULL known issue + 168K orphan keys. **No status blocks anywhere** (T11 rules these are canonical). Carrier-ts coverage anomaly flagged inline on fact_shipments with forward pointer to §9 (Known DQ / Open Investigations) — that subsection is task #9 still ahead. Next: task #8, spot-check per-AI entry points (CLAUDE/AGENTS/GEMINI/GROK).
- T18 (2026-05-21): **Task #8 — per-AI entry-point spot-check complete.** All four files exist at project root (`CLAUDE.md` / `AGENTS.md` / `GEMINI.md` / `GROK.md`); content is identical to TTYD-template `CLAUDE.md` modulo the per-AI assistant-folder slug (`claude` / `codex` / `gemini` / `grok` in the Step 5 storage path). All four contain `[how_to.md](./how_to.md)` link at top + "Read how_to.md first" expected-behavior block. No edits required. Stream A scaffold correct. Next: task #9, add §9 Known DQ / Open Investigations to how_to.md (carries T11 Bucket 4).
- T19 (2026-05-21): Principal correction — ORPS creds-in-source side-issue is **out of scope** for TTYD §9 (script-hygiene in a different project, not mart DQ). Drop from §9 plan. Bucket-4 §9 reduces to 2 items (carrier-ts anomaly + mart-wide empty-column audit). Principal then pivoted further — before writing §9, **probe the carrier-ts NULL rate by source × month** to see if the headline %s are misleading (clusters on a specific source like ORWO, or old 2024 data). **Probe completed** via `mcp__redshift__execute_sql` (source × month NULL-rate breakdown on `fact_shipments` since 2024-01-01). **The headline framing was wrong.** Three findings: (1) **PCS, Rewallution, ORWO all carry carrier-ts at 100% NULL across all months** — empty-by-design at-source, same bucket as ORWO. T11 had only flagged ORWO; PCS + Rewallution were silently in the same bucket. (2) **PicaAPI carrier-ts ingestion landed 2025-11** — 100% NULL through 2025-09, regime change to ~5-6% NULL Nov-2025+. The aggregate ~78% NULL was averaging across a bimodal regime — not an anomaly, just historical empty before ingestion went live. (3) **Picturator coverage degraded starting 2025-09** — was 0.7-4.9% NULL Jan-2024 through Aug-2025, jumped to 8-25% NULL Sep-2025+. Latest-month spikes (2026-05 PICT 26%/46%, PicaAPI 16%/36%) are in-flight artifacts (events lag the shipment), not the degradation.
- T20 (2026-05-21): Principal asked to drill PICT degradation by carrier. **Second probe completed** — PICT only, June 2025–April 2026, grouped by `shippingprovider_group` via `dim_shipping_providers`. **The "PICT pipeline degraded in Sep 2025" framing was also wrong — it's two specific carriers + a dim-coverage gap, not a PICT-wide issue.** Findings: (a) **DHL degraded Aug-2025 onward** — Jun-Jul 2025 ~0.4%/~1.0% NULL → Aug 3.7%/14.0% → Sep 9.5%/22.8% → Oct-Dec stabilized at 20-27%/20-27% → Jan-Apr 2026 plateaued ~15-24% NULL on both received + delivered. Roughly 73-100K PICT-DHL shipments per month. (b) **UPS degraded Nov-2025 onward** — Jun-Oct 2025 ~3%/~5% NULL → **Nov 20.3%/24.7% → Dec 26.0%/31.6%** → Jan-Apr 2026 plateaued at 15-26%/20-32%. ~40-130K PICT-UPS shipments per month. (c) **DPD UK (new carrier Nov 2025)** — delivered_null_pct is **100% across every month** since debut. Received ~3-6% (looks normal). **Delivered-event ingestion is not wired for DPD UK.** (d) **Unresolved `shippingprovider_group = NULL`** (carrier doesn't resolve into `dim_shipping_providers` for PICT) — appeared in volume from Sep 2025 (5K rows Aug → 17K Sep → 49K Nov → 104K Dec, stable ~25K Jan-Apr 2026) with ~50-65% NULL rates on both timestamps. Dim-coverage gap, partly overlapping the DHL/UPS degradation (some rows are likely unresolved variants of DHL/UPS extkeys). All other carriers (APG, ASENDIA, COLIS PRIVE, DB SCHENKER, DIRECT LINK, DPD POLAND, FEDEX, MAERSK, ONTRAC, YODEL) remain clean (<5% NULL on both). **Net: §9 narrows further from "PICT pipeline degraded Sep 2025" to four specific items: DHL ingestion degradation since Aug 2025, UPS ingestion degradation since Nov 2025, DPD UK delivered-events not wired, and dim-coverage gap on PICT carriers.** Worth flagging: the DHL/UPS degradation timing roughly overlaps with PicaAPI carrier-ts ingestion going live in Nov 2025 — hypothesis (unverified) that a tracking-system change in the carrier-event pipeline could be the shared root cause.
- T21 (2026-05-21): Principal asked to drill DHL+UPS by extkey. **Third probe completed** — PICT, DHL+UPS only, by `shippingprovider_extkey × month`, June 2025–April 2026, ≥500 rows/month threshold. **The DHL/UPS degradation is not "DHL/UPS broke" — it's "specific new extkey variants are missing carrier-event ingestion entirely."** Findings: (DHL group) **Workhorses stay clean throughout**: `DHLPKT` (50-160K rows/month, 0.2-1.5% NULL), `DHL54WARENPOST` (14-103K/month, 0.2-1.5% NULL), `DHLWP` (2-14K/month, ~0/~0.4% NULL). **Broken — bare `DHL` extkey is the culprit**: appeared in volume from Aug 2025 (3K→22K→53K→84K rows Aug-Dec), NULL rate jumped 6%→33%→80%→**96-99% by Oct 2025 and held**. **Broken — niche extkeys**: `DHLWPINT` (2K/mo Aug+, 100%/100% NULL since Aug 2025), `DHL54PREMIUM` (~500-2000/mo, 99-100% NULL since Sep 2025), `DHLWPKT` (single sparse Sep month, 100%). (UPS group) **Workhorse stays clean**: `UPS04STD` (35-94K/month, 0.6-4.1% received / 4.8-19.4% delivered — single Sep 19.4% delivered blip recovered). Other clean: `UPS04STDAP`, `UPS04EXPSAV`, `UPSWWECON`. **Broken — bare `UPS` extkey is the culprit**: ramped from <2K rows Aug-Sep to 12-24K rows Nov-Dec, **99%+ NULL on both throughout**. **Broken — new `UPSWWE` extkey**: appeared Nov 2025 in 1-9K rows/mo, **100% NULL on both, all months**. **Same pattern across both groups**: a new bare-carrier-name extkey (`DHL`, `UPS`) appeared in significant volume in Aug/Nov 2025, plus 1-2 niche extkeys (`UPSWWE`, `DHLWPINT`, `DHL54PREMIUM`) — all sharing the same trait: **carrier-event ingestion was never wired for these extkeys**. Service-code-specific extkeys (DHLPKT, UPS04STD, etc.) unaffected. **Net for §9**: ETL-team-actionable finding is "wire carrier-event ingestion for these 5 PICT extkeys" — not a pipeline-wide degradation, just missing per-extkey wiring on new variants. Probably routed to the no-source-found fallback in the carrier-event pipeline. ORWO/PCS/Rewallution are also a finding (they don't carry these at all, same as no-source classification).
- T22 (2026-05-21): Principal called stop on drilling. **Task #9 — §9 Known DQ / Open Investigations authored** in `how_to.md`. Appended after §8. Two subsections: **Carrier-event timestamp gaps** (decomposes the aggregate NULL %s into 5 distinct phenomena: PCS/Rewallution/ORWO no-source-by-design, PicaAPI carrier-ts ingestion landed 2025-11, PICT per-extkey gaps with 6-row table of broken extkeys + workhorse-clean contrast, PICT DPD UK delivered-events-not-wired, PICT dim-coverage gap for unresolved shippingprovider_group), unverified working-theory paragraph on PICT pattern-match routing, "For transit-time analysis today" 5-bullet practitioner guide. **Mart-wide empty-column audit (open)** subsection per T11 Bucket 4 — kept brief, lists the 5 classification buckets the ETL team should use, points back at §4 NULL classification as output target. **Also patched §4 fact_shipments** (T17 deliverable): (i) NULL classification — split the ORWO-only carrier-ts line into "No carrier-event source in V1 (PCS + Rewallution + ORWO)" multi-source line + "ORWO-only empty by design" line for truckload_id; (ii) Gotcha — replaced the misleading aggregate %s ("~78% PicaAPI / ~34% PICT") with specific per-extkey list of broken PICT extkeys + DPD UK delivered-events gap, pointing at §9 for full picture. **The fact_shipments §4 entry is now accurate**. Next: task #10, single Stream B commit to bi-analytics-main bundling reference refresh + §1-§4 + §9.
- T23 (2026-05-21): Principal asked about rubric design — surfaced the "drill one layer deeper to disprove" learning from the three carrier-ts probe rounds. Discussed reshape: rubric stops being a 5-bucket outcome taxonomy and becomes a **drill protocol** (source → time → dim_group → leaf) whose terminals are the 5 buckets. Two stop conditions (uniform-within-slice, slice-too-small). **Principal scoped both drafts as Jebrim-only**: bank-draft (rubric as procedural skill for mart audit) + Jebrim-`examine`-draft (meta-rule on publishing-aggregates-only-after-disprove-pass). Both deferred to #11 close. **Approved commit message for #10** and gave go-ahead. **External action completed:** `git commit` in `bi-analytics-main` landed as `48e0b44` ("S014: Shipping Data Mart TTYD §1–§4 + §9 + reference refresh"), 4 files changed, 487 insertions(+) / 51 deletions(-). Staged exactly the four planned files; unrelated working-dir state (playground deletions, 38_ups CLAUDE.md edit, untracked files) left intact and unstaged. **Task #10 closed.** Next: task #11, close S014 + harvest two Jebrim-scoped drafts (bank/notes mart-audit-null-classification-rubric + examine drill-to-disprove meta-rule).
- T24 (2026-05-21, S019 close): Principal cued session close + flagged that brain operating docs had been updated mid-session (S017/S018 dev-brain work landed `meta/layer-routing.md` + skill-drafts gate in `write-rules.md` + significantly evolved `close-session.md`). Reread the rulebook. Applied new routing to harvest: (a) the NULL classification rubric is procedural — **per `meta/layer-routing.md` "Procedure for how to do a class of work" row, it's a skill draft, not a bank note** — landed at `players/jebrim/spellbook/drafts/skills/mart-null-classification-by-drill-down.md`; (b) drill-to-disprove meta-rule landed at `players/jebrim/examine/drafts/2026-05-21-publish-aggregates-only-after-disprove-pass.md`; (c) added a third draft (`players/jebrim/niksis8_character/drafts/2026-05-21-methodology-scoped-to-analyst-character.md`) capturing the principal's "Jebrim is the analyst" signal as a methodology-scoping observation. All 3 drafts cite the specific S014 turn that produced them per `drafts-mechanics.md` observation-backed rule. **Task #11 completed.** S014 quest moves to `quest-log/completed/`. **Soft-block surfaced on commit:** S001 + S002 remain in `quest-log/in-progress/` from earlier sessions with their resume sections still in old-format quest-log top instead of `inventory/` — first-close-since-2026-05-21 migration deferred (they weren't touched this session, surfacing as deliberate-skip in the commit message). All 6 S014_* files (parent quest + 4 dwarf reports + 1 stream-A report) move together to completed/.
