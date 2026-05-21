# S014-D2 — bi-etl repo walk (Shipping Data Mart, 2026-05-21)

## Summary
V1 mart is 7 tables wired (not 8 — `dim_carrier_sla` does not exist in the repo, never created). Folder uses PascalCase `Shipping_Data_Mart` only; no `shipping_data_mart` variant present. 23 carrier provider files under `fact_shipment_invoice_lines/sql/providers/` (14 aggregated + 9 granular per README). No gold layer under the shipping mart yet — sibling `dags/order_level/gold/` and `dags/Shop_Level/gold/` exist but nothing has landed under `Shipping_Data_Mart/`. Mart is active — last commit on `fact_shipments` was 2026-05-21 12:55 CEST (today).

## Step 0 — git pull result
- HEAD before: `3824f374d9a062d3b753f9529eac3fa2c7987bf8`
- HEAD after:  `2fc8befcf5538b869969c9f84549f0c4c394908b`
- 23 files changed, 1118 insertions, 613 deletions
- Notable in the pull: `orwo_integration_walkthrough.html` deleted; `orwo_open_pointers.html` added; ORWO articlenumber backfill landed in `fact_shipment_orderitems/sql/post_processing/update_orwo_articlenumber.sql`.

## Step 1 — mart folder location
- Real folder: `dags/enterprise_silver/Shipping_Data_Mart/` (PascalCase).
- `git ls-files` shows **no** `shipping_data_mart/` lowercase variant. No abandoned case variant on disk.

## Step 2 — per-table state

### map_shipment_key
- DAG: `dags/enterprise_silver/Shipping_Data_Mart/map_shipment_key/silver_map_shipment_key_dag.py` — last commit `b45ec8a38 | 2026-05-15 | SatyaVarma Rudraraju | (NGE-6129)/feat: wire ORWO source branch into map_shipment_key spine`
- SQL: `sql/insert_to_silver.sql` (last commit on folder `56949b806 | 2026-05-15 | Grzegorz Strawa | Merge pull request #1297 from picanova/shop_level`)
- README: same commit as DAG (2026-05-15) — describes it as the surrogate-key spine every other fact joins through; ORWO branch now wired.
- TODO/FIXME:
  - `map_shipment_key/sql/insert_to_silver.sql:80` — `-- TODO (data platform team):` (open block, referenced by lines 381 and 412)
  - `map_shipment_key/sql/insert_to_silver.sql:381` — `bypass PICT/PICAAPI. Uses bronze as silver is incomplete (see TODO above).`
  - `map_shipment_key/sql/insert_to_silver.sql:412` — `Uses bronze as silver.rew_orders is empty (see TODO above).`

### fact_shipments
- DAG: `silver_fact_shipments_dag.py` — last commit `966141618 | 2026-05-21 12:55 +0530 | SVR | (NGE-6129)/fix: ORWO sentat -> order_produced_ts in fact_shipments` (today)
- SQL: `sql/insert_to_silver.sql`
- README: last commit `f03fb0cfb | 2026-05-15 | SVR | (NGE-6129)/fix: set ORWO production_site to 'Wolfen'`; flagged as "v1 MVP", canonical design at `NFE/1_shipping_data_mart/model/design/02_fact_shipments.md`.
- TODO/FIXME:
  - `fact_shipments/sql/insert_to_silver.sql:255` — `-- TODO(Niklavs 2026-04-27): handling of orders-without-trackingnumber needs...` (open question)
  - `fact_shipments/sql/insert_to_silver.sql:1150` — `'XXX',` literal (sentinel; not a TODO marker — placeholder string)

### fact_shipment_orderitems
- DAG: `silver_fact_shipment_orderitems_dag.py` — last commit `293c6cbc3 | 2026-05-21 10:41 +0200 | Miłosz Serej | feat: implement ORWO articlenumber backfill process from Navision data` (today)
- SQL: `sql/insert_to_silver.sql` + new `sql/post_processing/update_orwo_articlenumber.sql` (added today)
- README: same commit as DAG (2026-05-21) — flagged "v1 MVP".
- TODO/FIXME:
  - `silver_fact_shipment_orderitems_dag.py:18` — `dw.dim_products (legacy — TODO: replace)`
  - `silver_fact_shipment_orderitems_dag.py:37` — `dw.dim_products (TODO: replace with enterprise-layer dim).`
  - `sql/insert_to_silver.sql:158` — block-level `-- TODO:` (post-2026-04-27 follow-ups)
  - `sql/insert_to_silver.sql:1307` — `articlenumber column. TODO: replace with a dedicated enterprise-layer`

### fact_shipment_invoice_lines
- DAG: `silver_fact_shipment_invoice_lines_dag.py` — last commit `eb1e9dc61 | 2026-05-20 11:30 +0530 | SVR | (NGE-6129)/feat: distribute ORWO bulk-mail invoice cost across tied shipments`
- SQL: `sql/post_processing/monthly_adhoc_adjustment.sql` + 23 carrier files under `sql/providers/` (see Carrier SQL section below).
- README: same commit as DAG (2026-05-20) — declares "Full TRUNCATE + parallel INSERT of 23 carrier-specific SQL files (14 aggregated + 9 granular)". Heavy doc — currency matrix, DB Schenker decision, bucket vocab.
- Notable file: `legacy_adhoc_corrections.md` documents the monthly DHL post-processing.
- TODO/FIXME (selected — full carrier-file TODOs are mostly fallback-date notes per Niklāvs 2026-05-11):
  - `providers/dhl_orwo.sql:41` — `-- TODO: confirm with finance — if mixed currency, add FX strategy.`
  - `providers/dhl_orwo.sql:42` — `-- TODO: billed_weight is kept at the invoice line's full weight (NOT divided...)`
  - `providers/landmark_parcels.sql:5` — `-- TODO: migrate source to enterprise_silver once Landmark tables are added there`
  - `providers/landmark_taxes.sql:5` — `-- TODO: migrate source to enterprise_silver (currently only "_raw_historical"...)`
  - `providers/ontrac.sql:81/90/99/108` — repeated `TODO: replace with first_scan_datetime once silver adds it` (invoice_date fallback per Niklāvs 2026-05-11)
  - `providers/ups_orwo.sql:64/107` — `TODO: switch to COALESCE once transactiondate ... silver adds it`
  - `providers/dpd_poland_rewallution.sql:75`, `providers/gls.sql:45`, `providers/ontrac.sql:47` — same fallback-shipment_date pattern
  - `providers/fedex.sql:105` — comment line about UPS-style/USPS-prefixed trackings (`XXX` literal in comment, not a marker)

### fact_shipment_cost_summary
- DAG: `silver_fact_shipment_cost_summary_dag.py` — last commit `e87d12310 | 2026-05-11 | Łukasz Sendecki | refactor: move TRUNCATE to end of SQL in shipping data mart facts`
- SQL: `sql/insert_to_silver.sql` (the pivot), `sql/update_fact_shipments_cost.sql` (cross-DAG backfill into fact_shipments cost columns).
- README: last commit `34d030a23 | 2026-05-20 | SVR | (NGE-6129)/docs: add ORWO diagnostics SQL + finalize mart docs` — flagged "v1", references NGE-6125 + blockers T-15 / T-17.
- TODO/FIXME: none in SQL/Python (clean).

### fact_truck_charges
- DAG: `silver_fact_truck_charges_dag.py` — last commit `e87d12310 | 2026-05-11 | Łukasz Sendecki | refactor: move TRUNCATE to end of SQL in shipping data mart facts`
- SQL: `sql/insert_to_silver.sql`, `sql/update_allocation.sql`, `sql/update_rate_lookup.sql`.
- README: last commit `34d030a23 | 2026-05-20 | SVR | (NGE-6129)/docs: add ORWO diagnostics SQL + finalize mart docs` — flagged "v1 MVP".
- TODO/FIXME: none.

### dim_shipping_providers
- DAG: `silver_dim_shipping_providers_dag.py` — last commit `4bd3df40f | 2026-05-13 | Dexos21 | feat: scope dim_shipping_providers PK by source_system`
- SQL: `sql/upsert_to_silver.sql` — last touched today via `356a565b6 | 2026-05-21 10:41 | Dexos21 | feat(dim_shipping_providers): derive shippingprovider_group at INSERT via source_system-aware CASE`
- README: last commit `c98681064 | 2026-05-05 | Dexos21 | feat: implement silver_dim_shipping_providers DAG and UPSERT logic for shipping provider dimensions`
- TODO/FIXME:
  - `sql/upsert_to_silver.sql:20` — `-- source_system-aware: ORWO uses an explicit allow-list per Niklāvs (NGE-XXXX),` (placeholder ticket — `NGE-XXXX`)

### dim_carrier_sla
- **Folder does not exist.** `git ls-files` returns nothing under `Shipping_Data_Mart/dim_carrier_sla/`. No DAG, no SQL, no README. Either deferred or never wired in v1.

### dim_truck_costs (bonus — not in expected 8 but exists)
- DAG: `bronze_dim_truck_costs_dag.py` — last commit `620f8386b | 2026-04-22 | Łukasz Sendecki | docs: sync dim_truck_costs README with today's changes`
- Bronze-layer dim (SharePoint Excel → enterprise_bronze.dim_truck_costs), feeds `fact_truck_charges`. Dockerized.
- TODO/FIXME: none in SQL/Python.

## Step 3 — source × table coverage matrix

Coverage derived from greping `(picturator|pict_|picaapi|pcs|rewallution|orwo)` in each table's `insert_to_silver.sql` / `upsert_to_silver.sql`. Y = source branch present and meaningful; N = not present; - = source-agnostic by design (table aggregates from upstream mart tables).

|              | MSK | fact_shipments | fact_orderitems | fact_invoice_lines | fact_cost_summary | fact_truck_charges | dim_shipping | dim_carrier_sla |
|--------------|-----|----------------|-----------------|--------------------|--------------------|---------------------|--------------|-----------------|
| Picturator   | Y   | Y              | Y               | (carrier-bound)    | - (agg from FIL)   | N (PCS-only)        | Y            | n/a folder      |
| PicaAPI      | Y   | Y              | Y               | (carrier-bound)    | - (agg from FIL)   | N (PCS-only)        | Y            | n/a folder      |
| PCS          | Y   | Y              | Y               | (carrier-bound)    | Y (truck join)     | Y                   | Y            | n/a folder      |
| Rewallution  | Y   | Y              | Y               | Y (dpd_poland_rewallution.sql) | -      | N                   | Y            | n/a folder      |
| ORWO         | Y   | Y              | Y               | Y (dhl_orwo.sql, ups_orwo.sql) | -          | N (commented)       | Y            | n/a folder      |

Notes:
- `fact_shipment_invoice_lines` is carrier-keyed, not source-keyed. Source-system attachment happens via `map_shipment_key` join. Carrier files that explicitly tag ORWO / Rewallution: `dhl_orwo.sql`, `ups_orwo.sql`, `dpd_poland_rewallution.sql` (per file names + the README ORWO bulk-mail "share_n" handling).
- `fact_shipment_cost_summary` aggregates from `fact_shipment_invoice_lines` + reads `fact_truck_charges` for PCS truck charges — source coverage is inherited.
- `fact_truck_charges` is PCS-internal-only (truck allocation Variant B). Single `orwo` mention is a one-line comment, not a branch.

## Step 4 — gold layer hunt
- No `gold/` directory under `dags/enterprise_silver/Shipping_Data_Mart/`. No `sg_*` files anywhere under the mart.
- Sibling gold trees exist but are **not shipping**: `dags/order_level/gold/{fact_order, lucanet_costs, order_marketings}/ol_gold_*.py` (order-level), `dags/Shop_Level/gold/{dim_shops, fact_shop_daily}/sl_gold_*.py` (shop-level). Top-level mart README references them downstream (`ol_gold.*`, `sl_gold.*`) but nothing in this V1 sprint adds an `sg_gold_*` for shipping.
- No DAG file repo-wide with `gold` + `shipping` in name.
- `git status`: clean main except untracked `.claude/` shadow dirs and unrelated AI_Automations docker scratch. **No uncommitted/staged gold-layer work.**
- Conclusion: V1 finishing-touch gold layer has **not landed yet**. Name placeholder by convention would be `sg_gold_*` under `dags/shipping_level/gold/` mirroring `sl_`/`ol_`, but that path doesn't exist.

## Step 5 — recent activity (last 7d, 2026-05-14 → 2026-05-21)
Grouped by ticket:

**NGE-6129 (ORWO integration — SVR / Satya):**
- `2fc8befcf 2026-05-21` Merge `NGE-6129` of bi-etl
- `f685b62bf 2026-05-21` docs: mark open-pointer #6 (ORWO sentat -> order_produced_ts) resolved
- `b0c10b157 2026-05-21` Merge `NGE-6129` of bi-etl
- `966141618 2026-05-21` fix: ORWO sentat -> order_produced_ts in fact_shipments
- `9af27d823 2026-05-21` docs: add ORWO open-pointers HTML to repo
- `a3b22f02d 2026-05-21` Merge main into NGE-6129
- `69b340239 2026-05-20` chore: remove walkthrough HTML and diagnostics SQL
- `34d030a23 2026-05-20` docs: add ORWO diagnostics SQL + finalize mart docs
- `eb1e9dc61 2026-05-20` feat: distribute ORWO bulk-mail invoice cost across tied shipments
- `886069c54 2026-05-19` Merge main into NGE-6129
- `c240956a7 2026-05-18` Report on progress
- `4d9c967ec 2026-05-15` Merge main
- `f03fb0cfb 2026-05-15` fix: set ORWO production_site to 'Wolfen'
- `293c6a794 2026-05-15` removing unwanted files
- `93db4e084 2026-05-15` feat: add ORWO items to fact_shipment_orderitems via M:N linker
- `09391ba6e 2026-05-15` feat: extend fact_shipments with ORWO enrichment branch
- `4e6cc530c 2026-05-15` Merge NGE-6129
- `294f07d4d 2026-05-15` temp files with details
- `7238c8a5b 2026-05-15` Merge NGE-6129
- `b45ec8a38 2026-05-15` feat: wire ORWO source branch into map_shipment_key spine

**Untagged — Łukasz Sendecki (PCS / Picturator / PicaAPI / DPD UK fixes):**
- `7d73e24c2 2026-05-21` feat: add picaapi_no_psi_no_pcs_pairs fallback CTE
- `5a665291f 2026-05-21` fix: PPEO DISCOUNT exclusion granular — only voucher pattern
- `a46404851 2026-05-21` fix: exclude DISCOUNT line items for PPEO shop in fact_shipment_orderitems
- `2ab3b432f 2026-05-21` fix: PICT tni.quantity=0 falls back to orderitem-level quantity
- `decc94be2 2026-05-21` fix: route Picturator items with empty-trackingnumber tn to pict_no_tni_pairs
- `c450d24fb 2026-05-20` fix: materialize anti-join lookups as TEMP tables for Redshift optimizer
- `150e8afb6 2026-05-20` fix: Redshift CSQ decorrelation in fact_shipment_orderitems
- `dc9dd0589 2026-05-20` fix: Picturator REPLACEMENT exception for 8 shops matches silver.revenues
- `5b48b63d4 2026-05-20` fix: pcs_parcel_reorder_flags BOOL_OR -> BOOL_AND
- `9bcfda8b5 2026-05-20` fix: PicaAPI orderitem net = product + shipping (mirror silver.revenues)
- `fd018cd65 2026-05-20` fix: Rewallution revenue fan-out — pre-divide per parcel_count
- `7440b3d41 2026-05-20` feat: rescue Picturator orderitems missing tni linker via equal-split fallback
- `55e25d4d7 2026-05-20` refactor: rename fact_shipment_invoice_lines.shippingprovider to shippingprovider_extkey
- `7e552464f 2026-05-20` fix: filter fact_shipments events by source_system to prevent cross-source leak
- `f9baa9269 2026-05-14` fix: use pcs_orders.createddate not po.created in production_order_created_ts
- `ccfb27e12 2026-05-14` feat: add Phase 0 time-window gate to shipping data mart orchestrator
- `97b45283c 2026-05-14` feat: refactor fact_shipments lifecycle timestamps
- `129b99bec 2026-05-14` fix: dedup fact_shipments pcs joins to remove 1588 duplicate shipment_ids
- `f5da9d731 2026-05-14` fix: add FedEx PCS bridge for 12-digit non-39/27 trackings

**Untagged — Dexos21 (Dawid; carrier-level fixes via shop_level branches):**
- `356a565b6 2026-05-21` feat(dim_shipping_providers): derive shippingprovider_group at INSERT via source_system-aware CASE
- `5a1654b5c 2026-05-19` fix(maersk): skip fuel_surcharge column UNION when native row exists
- `8adee4a7b 2026-05-18` feat(dpd_poland): enhance deduplication logic
- `06c45b3da 2026-05-18` fix: restore DPD PL prod target to poc_staging, add UPS_Orwo auto-trigger
- `6fcb41470 2026-05-15` feat(ontrac): add credit notes handling from poc_landing
- `ad129e9ee 2026-05-15` fix(usps): emit only final_postage_usd as base_rate; drop fee column unpivots
- `9328a34a6 2026-05-15` fix: update whitespace handling for shipping provider checks
- `77039ab74 2026-05-15` fix(dpd_poland_rewallution): drop false PLN->EUR conversion

**Grzegorz merges (PR gatekeeper):** #1297, #1298, #1299, #1306, #1309, #1319, #1351, all within the window.

## Step 6 — orchestrator
- File: `dags/enterprise_silver/Shipping_Data_Mart/silver_shipping_data_mart_orchestrator.py`
- Last commit on file: `ccfb27e12 | 2026-05-14 15:42 +0200 | Łukasz Sendecki | feat: add Phase 0 time-window gate to shipping data mart orchestrator`
- DAG id: `silver_shipping_data_mart_orchestrator`. Owner: `@lukasz.sendecki`. Ticket: NGE-6127. Tags: `Silver, Shipping, Data_Mart, Orchestrator`.
- **Schedule:** `0 4 * * *` (daily at 04:00 UTC). `catchup=False`, `max_active_runs=1`.
- **Connection id:** all child DAGs use `amazon_redshift_airflow_testing` (orchestrator itself only triggers, no conn).
- **Trigger rule:** `trigger_rule="all_success"` on every `create_dag_trigger` call (TRIGGER_KWARGS). Sentinel `phase_0_done` uses `trigger_rule="none_failed"` so it accepts the gate-skipped case. `end` uses `trigger_rule="all_done"`.
- **Phase count: 6 phases.** Distinct from the file's narrative "five phases" — the Phase 0 gate adds 0a + 0b. Confirmed structure:
  - **Phase 0 window gate** (`ShortCircuitOperator`, runs only when UTC hour ∈ {3,4}). Skips 0a/0b outside the window.
  - **Phase 0a — bronze ingestion (parallel):** triggers `bronze_picturator`, `bronze_picaapi`, `eb_pcs_ingestion`.
  - **Phase 0b — silver intermediates (parallel after 0a):** triggers `silver_shipping_pipeline_orchestrator`, `silver_revenues`, `silver_shipping_costs`, `silver_avg_shipping_costs` (sc → avg internal dep).
  - **Phase 1 — dim + mapping prep:** triggers `bronze_dim_truck_costs`, `silver_map_shipment_key`, `silver_dim_shipping_providers` (map_key → dim_providers).
  - **Phase 2 — shipment facts (parallel):** triggers `silver_fact_shipment_orderitems`, `silver_fact_shipment_invoice_lines`.
  - **Phase 3 — fact_shipments spine** (cost cols NULL on insert): triggers `silver_fact_shipments`.
  - **Phase 4 — truck allocation:** triggers `silver_fact_truck_charges`.
  - **Phase 5 — cost_summary + cost backfill:** triggers `silver_fact_shipment_cost_summary` (which then runs `update_fact_shipments_cost.sql` internally to backfill fact_shipments cost columns).
- **Gold-layer step in phases:** **No.** No Phase 6 / no `sg_gold_*` trigger / no reference to a shipping gold DAG anywhere in this orchestrator. The mart ends at silver.

## Step 7 — abandoned items
- **`dim_carrier_sla/`** — folder does not exist. Either deferred entirely from v1 or never picked up. Worth confirming whether the "8 expected" baseline was aspirational.
- **`dim_truck_costs/`** — present (bronze layer), but it's **not** in Jebrim's "8 expected" list. It's an active dim feeding `fact_truck_charges`, not abandoned. Just unaccounted for in the baseline.
- **`NGE-XXXX` placeholder ticket** in `dim_shipping_providers/sql/upsert_to_silver.sql:20` (`-- per Niklāvs (NGE-XXXX)`) — ORWO allow-list rule with no real ticket number wired in.
- **Top-level `data_lineage_review.html`/`.md`** in mart root — review docs co-located with code; not abandoned but unusual placement.
- **`orwo_open_pointers.html`** in mart root — new doc landed 2026-05-21; tracks remaining ORWO open pointers (1 just resolved per `f685b62bf`).
- **Carrier mapping table only carries 14 carriers** but DAG runs 23 provider SQLs — the 9 not in the mapping table are column-based unpivots (intentional, documented in README) so this is by design, not abandoned.
- **Repo-wide untracked files** (not mart-related but flagged by git status): `NFE/1_shipping_data_mart/.claude/` shadow dir, `dags/AI_Automations/order_flagging_pcs/.../docker/diagnose_queries.py` and Niklavs's local PCS scripts. Unrelated to the mart proper.

## Carrier SQL files (under fact_shipment_invoice_lines/sql/providers/)

23 files total. Classification per the DAG README (lines 358-414):

**Aggregated (14):**
1. `ups.sql`
2. `ups_orwo.sql` — ORWO bulk-mail distributive allocation
3. `dhl.sql`
4. `dhl_orwo.sql` — ORWO bulk-mail distributive allocation
5. `dhl_america.sql`
6. `gls.sql`
7. `dpd.sql`
8. `dpd_poland_struct1.sql`
9. `dpd_poland_struct2.sql` — 71 rows total v1
10. `dpd_poland_rewallution.sql`
11. `db_schenker.sql` — intentionally 100% `'unclassified'` per Niklāvs decision
12. `asendia_usa.sql`
13. `landmark_parcels.sql`
14. `landmark_taxes.sql` — hardcoded `customs_duties`

**Granular (9):**
1. `dpd_uk.sql` — joins `pcs_sentparcels` + `asa.v_truck_surcharges`
2. `colis_prive.sql`
3. `ontrac.sql`
4. `maersk.sql`
5. `yodel.sql`
6. `apg.sql`
7. `direct_link.sql`
8. `usps.sql`
9. `fedex.sql` — hybrid: bronze charge pairs unpivot + Base Charge residual + silver-only recovery branch

**Deferred (4, not wired, no SQL file):** `dhl_poland`, `hermes`, `ambro`, `dpd_poland_rewallution_2` — source covers only pre-2024.

## Surprises
- **`dim_carrier_sla` does not exist.** Baseline of "8 tables wired" is off-by-one against reality — only 7 wired (7th being `dim_shipping_providers`). Either drop SLA from v1 scope or confirm it's still on Jebrim's list.
- **`dim_truck_costs` exists but isn't in the expected 8.** It's a bronze-layer dim with a real DAG (`bronze_dim_truck_costs_dag.py`), Dockerized SharePoint extractor, README. Feeds `fact_truck_charges`. The "8 expected" list missed it.
- **Carrier count = 23 active, 4 deferred — matches baseline.** Aggregated/granular split is 14/9 (not the round numbers one might expect).
- **No gold layer landed yet, but the orchestrator has no placeholder for it either.** No empty `phase_6_gold` task group, no commented-out trigger. The mart genuinely stops at silver. If a gold layer is "in final stretches" it's not in this repo as of HEAD `2fc8befcf`.
- **`NGE-6129` (ORWO integration) is the dominant active ticket.** Last 7 days are >50% ORWO. Two threads working in parallel: SVR on ORWO source branches in MSK/fact_shipments/fact_orderitems, Łukasz on Picturator/PicaAPI/PCS quality fixes, Dawid (Dexos21) on per-carrier fixes via `shop_level` PR branch.
- **Orchestrator narrative says "5 phases" but the file has 6 (Phase 0 added 2026-05-14).** Doc drift in the docstring intro — the phase-by-phase narrative below it does cover 0a/0b correctly. Minor.
- **Connection id is `amazon_redshift_airflow_testing`** — name suggests this is the testing Redshift, not a `_prod` connection. Confirm whether that's intentional for v1 or whether prod connection rename is pending.
- **`fact_shipments/sql/insert_to_silver.sql:1150` has `'XXX'`** — a literal placeholder/sentinel string inside a `VALUES (...)` clause, not a TODO marker. Worth a glance to confirm intent.
- **`map_shipment_key` still reads bronze directly for Rewallution** (line 412: "Uses bronze as silver.rew_orders is empty") and partly for PICT/PICAAPI (line 381). Silver migration of those sources is still pending — open TODO addressed to "data platform team".
