# S002 D2 — bi-etl repo state for Shipping Data Mart V1

**Dwarf:** Jebrim-inherited. **Date:** 2026-05-21. **Scope:** `dags/enterprise_silver/Shipping_Data_Mart/` only (with cross-flag sweeps).

`git pull origin main` ran clean. Most-recent mart commit `c450d24fb` (Łukasz, 2026-05-20). Working tree clean.

---

## Headline findings (read first)

1. **Mart dir is `Shipping_Data_Mart/` (capitalized).** No lowercase `shipping_data_mart/` exists. D1's "case variation" question — resolved: only capitalized version is real.
2. **`dim_carrier_sla` does NOT exist in the repo.** Not as a folder, not as a DAG, not as SQL. The 8th table from the brief is **not built** and not even scoped on the bi-etl side. The name lives only in NFE design docs (`NFE/1_shipping_data_mart/model/design/08_dim_carrier_sla.md`) and is *referenced* by `dim_shipping_providers/README.md:65` as a planned consumer ("JOIN dim_carrier_sla via service_type"). SLA breach computation is **not feasible from this repo today.**
3. **`fact_shipment_cost_summary` exists and is fully wired** — DAG, SQL, README, orchestrator Phase 5. But the mart-level `README.md` (`Shipping_Data_Mart/README.md`, last commit 2026-05-05, Dexos21) **still lists it under "Not yet built (v2 / phase 2)"** at lines 73-78. Top-level README is stale by ~3 weeks against reality.
4. **Top-level README also omits `fact_shipment_cost_summary` from the schema table and from the orchestrator phase diagram** (only shows Phase 1-4; actual orchestrator runs Phase 1-5 with cost_summary as Phase 5). Refresh of `Shipping_Data_Mart/README.md` is itself a V1 task.
5. **Cross-flag check (D1):**
   - `orwo_open_pointers.html` — **NOT in repo currently.** Brief said it lives at `Shipping_Data_Mart/orwo_open_pointers.html`; it does not. The file present is `orwo_integration_walkthrough.html` (Satya, 2026-05-18, 31KB) — a different artifact.
   - `REPORT_NGE-7097.html` — **NOT in repo** anywhere (full-tree search). Engineer-attached only.
   - `REPORT_*.html` / `*_open_pointers*.html` — **none found** anywhere in bi-etl.
   - The two HTML reports that DO live in repo: `data_lineage_review.html` (Łukasz, 2026-05-04, 329KB; rendered companion to `data_lineage_review.md`) and `orwo_integration_walkthrough.html` (Satya, 2026-05-18).
6. **Extra subdir not in brief:** `dim_truck_costs/` — bronze-target table (not silver) feeding `fact_truck_charges`. SharePoint Excel ingestion. Listed in main README.

---

## Per-table state matrix

Table presence/freshness. `Last commit` = most-recent commit touching DAG file. `README freshness` = last commit on the per-folder README. **V1 flag** is my read from code + README narrative, not from ClickUp.

### 1. `map_shipment_key`

| Aspect | State |
|---|---|
| Folder | `Shipping_Data_Mart/map_shipment_key/` |
| DAG | `silver_map_shipment_key_dag.py` — `b45ec8a38` (2026-05-15, Satya) |
| SQL | `sql/insert_to_silver.sql` — `56949b806` (2026-05-15, Grzegorz) |
| README | `b45ec8a38` (2026-05-15, Satya) |
| HTML in dir | none |
| **V1 flag** | **production** — wired into orchestrator Phase 1; ORWO branch landed via NGE-6129 (Satya). Full UNION of 5 source systems (PICT / PicaAPI / PCS / Rewallution / ORWO). |

**TODO/FIXME markers:**
- `map_shipment_key/sql/insert_to_silver.sql:80` — `-- TODO (data platform team):` (block start; lists silver-layer ETL bugs to fix — pcs_orders rolling-window, empty rew_orders, etc.)
- `map_shipment_key/sql/insert_to_silver.sql:381` — `-- bypass PICT/PICAAPI. Uses bronze as silver is incomplete (see TODO above).`
- `map_shipment_key/sql/insert_to_silver.sql:412` — `-- Uses bronze as silver.rew_orders is empty (see TODO above).`
- `map_shipment_key/README.md:188` — references silver `pcs_*` rolling-window limitation
- `map_shipment_key/README.md:202` — `enterprise_silver.rew_orders is empty (ETL bug — see TODO)`
- `map_shipment_key/README.md:328` — section header `## Known v1 limitations (TODOs for the data platform team)`

### 2. `fact_shipments`

| Aspect | State |
|---|---|
| Folder | `Shipping_Data_Mart/fact_shipments/` |
| DAG | `silver_fact_shipments_dag.py` — `7e552464f` (2026-05-20, Łukasz; `refactor: rename fact_shipment_invoice_lines.shippingprovider to shippingprovider_extkey`) |
| SQL | `sql/insert_to_silver.sql` — `7e552464f` (2026-05-20, Łukasz) |
| README | `f03fb0cfb` (2026-05-15, Satya) — last meaningful was the ORWO production_site='Wolfen' commit |
| HTML in dir | none |
| **V1 flag** | **production** — 57-column wide fact; PICT + PicaAPI + PCS + Rewallution + ORWO branches all wired (scope filter relaxed iteratively, see README §"Stage 2 — here, v1 scope filter"). Still has open `[ ]` columns in spec table: row 21 `packagetype_group` (mapping TBD), row 48 `expected_shipping_cost_eur` (T-14 unresolved), row 49 `avg_shipping_cost_eur` (T-32 unresolved), row 53 `user_packing_order` (pcs_orderlogs not in bronze), row 54 `loading_unit_id` (pcs_loadingunits not in bronze), row 41 `is_returned` (no event vocabulary). Cost columns 44-47, 50 are **wired** as of 2026-04-27 — backfilled from Phase 5. |

**TODO/FIXME markers (DAG+SQL — README has dozens of `TODO(bronze-migration)` rows on the column-mapping table, treated separately):**
- `fact_shipments/sql/insert_to_silver.sql:255` — `-- TODO(Niklavs 2026-04-27): handling of orders-without-trackingnumber needs` (block start — discusses T-31 DQ flag for orders with no tracking yet)
- `fact_shipments/sql/insert_to_silver.sql:1145` — `'XXX',` — placeholder string literal in a CASE branch; cross-check if intentional or stray. (`XXX` here is in a string, not a code marker — likely a sentinel value, not a code-marker FIXME.)

**README TODOs (representative; full list ~25):**
- `fact_shipments/README.md:40-47` — five `TODO bronze-migration` lines on `poc_landing.*` reads for PICT events, PicaAPI addresses + regions + countries + shipment_trackings
- `fact_shipments/README.md:181-184` — PII column TODOs (forename / surname / email / address) — all blocked on bronze-migration
- `fact_shipments/README.md:311` — `Landing reads with TODO(bronze-migration).` (section header)
- `fact_shipments/README.md:523` — `## Realistic TODO` (top-level closure plan)
- `fact_shipments/README.md:651` — closure-summary section listing T-resolutions

### 3. `fact_shipment_orderitems`

| Aspect | State |
|---|---|
| Folder | `Shipping_Data_Mart/fact_shipment_orderitems/` |
| DAG | `silver_fact_shipment_orderitems_dag.py` — `dc9dd0589` (2026-05-20, Łukasz; `fix: Picturator REPLACEMENT exception for 8 shops matches silver.revenues`) |
| SQL | `sql/insert_to_silver.sql` — `c450d24fb` (2026-05-20, Łukasz; `fix: materialize anti-join lookups as TEMP tables for Redshift optimizer`) — **most-recent commit on the mart** |
| README | `93db4e084` (2026-05-15, Satya — `(NGE-6129)/feat: add ORWO items to fact_shipment_orderitems via M:N linker`) |
| HTML in dir | none |
| **V1 flag** | **production** — 4-source UNION (PICT + PicaAPI + PCS + Rewallution); ORWO items wired via M:N linker. NGE-6129 step 4 closed. |

**TODO/FIXME markers:**
- `fact_shipment_orderitems/silver_fact_shipment_orderitems_dag.py:17` — `dw.dim_products (legacy — TODO: replace)` (DAG docstring)
- `fact_shipment_orderitems/silver_fact_shipment_orderitems_dag.py:36` — `dw.dim_products (TODO: replace with enterprise-layer dim).`
- `fact_shipment_orderitems/sql/insert_to_silver.sql:155` — `-- TODO:` block (discusses dim_products replacement)
- `fact_shipment_orderitems/sql/insert_to_silver.sql:1165` — `articlenumber column. TODO: replace with a dedicated enterprise-layer`
- `fact_shipment_orderitems/README.md:98` — product_key row: **legacy dw.dim_products only resolves PICT+PCS; NULL for PicaAPI, Rewallution, ORWO (0.02% match rate measured 2026-05-15)** — explicit TODO to extend
- `fact_shipment_orderitems/README.md:223` — PicaAPI revenue allocation TODO (still product-line-only; shipping + discount allocation pending)
- `fact_shipment_orderitems/README.md:257` — `for PicaAPI and Rewallution. TODO: replace with a dedicated`

### 4. `fact_shipment_invoice_lines`

| Aspect | State |
|---|---|
| Folder | `Shipping_Data_Mart/fact_shipment_invoice_lines/` |
| DAG | `silver_fact_shipment_invoice_lines_dag.py` — `eb1e9dc61` (2026-05-20, Satya; `(NGE-6129)/feat: distribute ORWO bulk-mail invoice cost across tied shipments`) |
| SQL | 23 provider files under `sql/providers/` + `sql/post_processing/monthly_adhoc_adjustment.sql`. Most-recent provider commit `55e25d4d7` (2026-05-20, Łukasz; the `shippingprovider → shippingprovider_extkey` rename touched 18 provider files in one sweep). |
| README | `eb1e9dc61` (2026-05-20, Satya) |
| HTML in dir | none |
| Other docs in dir | `legacy_adhoc_corrections.md` — registry of legacy `bi_dw_dev_dbo.factshipmentcosts` ETL corrections NOT yet ported to silver. Tier-3 reconciliation log. |
| **V1 flag** | **production** — 23 active providers wired (14 aggregated + 9 granular). 4 deferred (`dhl_poland`, `hermes`, `ambro`, `dpd_poland_rewallution_2`) — no 2024+ source data. |

**TODO/FIXME markers:**
- `fact_shipment_invoice_lines/sql/providers/dhl_orwo.sql:41` — `-- TODO: confirm with finance — if mixed currency, add FX strategy.`
- `fact_shipment_invoice_lines/sql/providers/dhl_orwo.sql:42` — `-- TODO: billed_weight is kept at the invoice line's full weight (NOT divided`
- `fact_shipment_invoice_lines/sql/providers/dpd_poland_rewallution.sql:75` — `-- shipment_date in source — TODO: switch to COALESCE once available).`
- `fact_shipment_invoice_lines/sql/providers/gls.sql:45` — `-- shipment_date in source — TODO: switch to COALESCE once available).`
- `fact_shipment_invoice_lines/sql/providers/landmark_parcels.sql:5` — `-- TODO: migrate source to enterprise_silver once Landmark tables are added there`
- `fact_shipment_invoice_lines/sql/providers/landmark_taxes.sql:5` — `-- TODO: migrate source to enterprise_silver (currently only "_raw_historical"`
- `fact_shipment_invoice_lines/sql/providers/ontrac.sql:47, 81, 90, 99, 108` — 5 lines, all `shipment_date` fallback notes ("`-- 3rd col = shipment_date (fallback to invoice_date per Niklāvs 2026-05-11; TODO: replace with first_scan_datetime once silver adds it)`")
- `fact_shipment_invoice_lines/sql/providers/ups_orwo.sql:64` — `-- shipment_date in source — TODO: switch to COALESCE once transactiondate`
- `fact_shipment_invoice_lines/sql/providers/ups_orwo.sql:107` — `-- fallback per Niklāvs 2026-05-11, TODO: replace with transactiondate once silver adds it`
- `fact_shipment_invoice_lines/README.md:173, 175` — DHL / DHL Orwo currency `TODO: confirm with finance`
- `fact_shipment_invoice_lines/README.md:201-204` — `### Outstanding TODOs` section (currency + landmark silver migration)
- `fact_shipment_invoice_lines/README.md:212-216` — NGE-6426 partial-fill `shipment_date` per-provider TODO list
- `fact_shipment_invoice_lines/README.md:219-224` — NGE-6427 stale source pipelines (DPD / Landmark / GLS feeds not refreshing)
- `fact_shipment_invoice_lines/README.md:228+` — NGE-6428 per-provider reconciliation

**README stale reference:** `fact_shipment_invoice_lines/README.md:134` lists `sql/diagnostics/db_schenker_*.sql` files (5 of them). The `diagnostics/` directory **does not exist** in the current tree. Diagnostic queries were either removed or never committed.

### 5. `fact_shipment_cost_summary`

| Aspect | State |
|---|---|
| Folder | `Shipping_Data_Mart/fact_shipment_cost_summary/` |
| DAG | `silver_fact_shipment_cost_summary_dag.py` — `e87d12310` (2026-05-11, Łukasz; `feat: consolidate picaapi PCS-bridge rescue into single CTE`) |
| SQL | `sql/insert_to_silver.sql` — `e87d12310` (2026-05-11) + `sql/update_fact_shipments_cost.sql` — `c60fe8345` (2026-05-08, Dexos21) |
| README | `26602e237` (2026-05-11, Dexos21) |
| HTML in dir | none |
| **V1 flag** | **production** — DAG runs Phase 5 in orchestrator; pivots 12 bucket columns + truck_charges_eur. `truck_charges_local = NULL` in v1 by design (no source). README explicitly cites NGE-6125 ticket alignment, 1:1 column match. |

**TODO/FIXME markers:** none in DAG/SQL. README cites two upstream blockers (T-15 closed, T-17 partially closed — neither is a code marker).

### 6. `fact_truck_charges`

| Aspect | State |
|---|---|
| Folder | `Shipping_Data_Mart/fact_truck_charges/` |
| DAG | `silver_fact_truck_charges_dag.py` — `e87d12310` (2026-05-11, Łukasz) |
| SQL | `sql/insert_to_silver.sql` — `e87d12310` (2026-05-11) + `sql/update_allocation.sql` — `d583739bb` (2026-05-08, Łukasz; `feat: split fact_shipments.truckload_id into actual + allocated`) + `sql/update_rate_lookup.sql` — `e1bad4a0a` (2026-04-22, Łukasz) |
| README | `e8d538533` (2026-04-30, Łukasz) — relatively older |
| HTML in dir | none |
| **V1 flag** | **production** — session-dedupe rule landed (Niklāvs 2026-04-21), Step 6 UPDATE on `fact_shipments.allocated_truckload_id`, depends on `dim_truck_costs` SharePoint feed (which lives in sibling `dim_truck_costs/` subdir). Variant B allocation. |

**TODO/FIXME markers:** none found in DAG/SQL/README under this folder. Diagnostic SQLs referenced in README (`sql/diagnostics/check_*`) — **not verified to exist in tree**; same caveat as invoice_lines diagnostics.

### 7. `dim_shipping_providers`

| Aspect | State |
|---|---|
| Folder | `Shipping_Data_Mart/dim_shipping_providers/` |
| DAG | `silver_dim_shipping_providers_dag.py` — `4bd3df40f` (2026-05-13, Łukasz; `feat: scope dim_shipping_providers PK by source_system`) |
| SQL | `sql/upsert_to_silver.sql` — `4bd3df40f` (2026-05-13) |
| README | `c98681064` (2026-05-05, Dexos21) |
| HTML in dir | none |
| **V1 flag** | **production with caveat** — DAG runs Phase 1 (UPSERT-only, INSERT-where-not-exists). Manual enrichment per new extkey by hand (no SharePoint loader, Niklāvs 2026-05-04 decision). README §"Known limitations" line 225 flags **`service_type` semantics not aligned with `dim_carrier_sla` consumers** (since `dim_carrier_sla` doesn't yet exist). |

**TODO/FIXME markers:** none in DAG/SQL. README §"Known limitations / open questions" carries soft callouts (service_type semantics, NULL Rewallution extkey, no SCD2 history).

### 8. `dim_carrier_sla` — **DOES NOT EXIST IN REPO**

| Aspect | State |
|---|---|
| Folder | none |
| DAG | none |
| SQL | none |
| README | none |
| HTML | none |
| **V1 flag** | **not-started** — repo has no folder, no DAG file, no SQL, no schema-creation script. Only references are in NFE design doc `NFE/1_shipping_data_mart/model/design/08_dim_carrier_sla.md` (out of D2 scope per brief) and the forward-looking line in `dim_shipping_providers/README.md:65`. `dim_shipping_providers.service_type` is left NULL by design pending consumer alignment. **SLA breach computation cannot be derived from current mart.** |

---

## Source_system × table coverage (claimed by READMEs)

`Picturator` = PICT. `PicaAPI` = PICAAPI. `PCS` = production. `Rewallution` = PL Baselinker. `ORWO` = PTSLive production site.

| Table | Picturator | PicaAPI | PCS | Rewallution | ORWO |
|---|---|---|---|---|---|
| `map_shipment_key` | wired | wired | wired | wired | wired (NGE-6129 step 1, b45ec8a38) |
| `fact_shipments` | wired (spine) | wired (spine) | wired (enrichment CTE) | wired (`tmp_rewallution_orders_enriched`) | wired (`tmp_orwo_orders_enriched`, NGE-6129 step 3, 2026-05-15) — destination + PII + carrier events NULL by design (no source) |
| `fact_shipment_orderitems` | wired (priority 1) | wired (priority 2) | wired, `revenue_eur = NULL` by design | wired (PLN→EUR converted) | wired (NGE-6129 step 4, 93db4e084 2026-05-15), `revenue_eur = NULL` (ORWO revenue is in separate Navision `orwo_revenue` stream — follow-up) |
| `fact_shipment_invoice_lines` | n/a — carrier-grain not source-grain | n/a | n/a | n/a — but `dpd_poland_rewallution` provider feeds Rewallution-routed parcels | wired (NGE-6129; `dhl_orwo`, `ups_orwo` providers + bulk-mail distribution commit eb1e9dc61 2026-05-20) |
| `fact_shipment_cost_summary` | inherits from `fact_shipment_invoice_lines` per shipment_id (source-agnostic) | same | same | same | same |
| `fact_truck_charges` | n/a (PCS-only) | n/a | wired (depends on `pcs_truckloads` + `dim_truck_costs`) | n/a (no truck — dropshipping) | n/a — ORWO is external site, no PCS truck. README excludes Wolfen from PCS truck allocation. |
| `dim_shipping_providers` | wired (extkeys from PICT branch of MSK) | wired | wired | NULL extkey (filtered out — no provider column on Rewallution) | wired (ORWO `trackingservice` ingested as extkey via MSK; PK now `(source_system, shippingprovider_extkey)` post 4bd3df40f) |
| `dim_carrier_sla` | does not exist | does not exist | does not exist | does not exist | does not exist |

---

## Recent commit log (last 6 weeks)

**241 commits** touched `Shipping_Data_Mart/` since 2026-04-09 (6-week cutoff). Authors: Łukasz Sendecki (majority), SatyaVarma Rudraraju, Dexos21 (likely Łukasz on a different account or another dev), Miłosz Serej, Grzegorz Strawa (merges).

**Grouped by ticket prefix** (commits with explicit `(NGE-NNNN)/` prefix per NGE-6129 convention):

- **`(NGE-6129)`** — 9 commits (ORWO integration, Satya + Łukasz). All 6 steps merged per [[S001_2026-05-20_repo-orientation|S001]] carry-forward.
- **`(NGE-6125)`** — 5 commits (`fact_shipment_cost_summary` build-out).
- Remaining 227 commits use **conventional-commit prefixes without NGE token** (`fix:`, `feat:`, `refactor:`, `docs:`, `perf:`). Team does not consistently include ticket IDs in commit messages outside NGE-6129 / NGE-6125 — ticket→commit mapping for the other 227 requires comment-thread cross-referencing (out of scope for D2; D1 handles ticket side).

**Top-of-history (5 most-recent):**

| Hash | Date | Author | Subject |
|---|---|---|---|
| `c450d24fb` | 2026-05-20 | Łukasz | fix: materialize anti-join lookups as TEMP tables for Redshift optimizer |
| `150e8afb6` | 2026-05-20 | Łukasz | fix: Redshift CSQ decorrelation in fact_shipment_orderitems |
| `dc9dd0589` | 2026-05-20 | Łukasz | fix: Picturator REPLACEMENT exception for 8 shops matches silver.revenues |
| `5b48b63d4` | 2026-05-20 | Łukasz | fix: pcs_parcel_reorder_flags BOOL_OR -> BOOL_AND (mixed original+R parcels) |
| `9bcfda8b5` | 2026-05-20 | Łukasz | fix: PicaAPI orderitem net = product + shipping (mirror silver.revenues) |

Pattern: heavy `fix:` activity 2026-05-20, the day before this audit — late-stage hardening, not new feature work. Suggests V1 readiness is **rolling onto the runway** but reconciliation passes still surfacing source-specific bugs.

**Notable feature commits in window:**

- `eb1e9dc61` (2026-05-20, Satya) — `(NGE-6129)/feat: distribute ORWO bulk-mail invoice cost across tied shipments`
- `93db4e084` (2026-05-15) — `(NGE-6129)/feat: add ORWO items to fact_shipment_orderitems via M:N linker`
- `b45ec8a38` (2026-05-15) — `(NGE-6129)/feat: wire ORWO source branch into map_shipment_key spine`
- `09391ba6e` (2026-05-15) — `(NGE-6129)/feat: extend fact_shipments with ORWO enrichment branch`
- `ccfb27e12` (2026-05-14) — `feat: add Phase 0 time-window gate to shipping data mart orchestrator`
- `e60973bfc` (2026-05-08) — `feat: shipping mart orchestrator runs on 6h schedule with full upstream chain`
- `da4b6d3b4` (2026-05-13) — `feat: date-aware msk join for tracking-reuse carriers`
- `e1bc9edbc` (2026-05-06) — `perf: refactor fact_truck_charges allocation + add smoothed cost-per-parcel`

---

## Abandoned / half-built artifacts

Things in the tree that look incomplete or stale:

1. **`Shipping_Data_Mart/README.md` (top-level)** — stale by ~3 weeks. Claims `fact_shipment_cost_summary` is "Not yet built (v2)" (lines 73-78) while the folder is fully wired in Phase 5 of the orchestrator. The orchestrator-phase diagram (lines 152-178) shows Phase 1-4 only, omits Phase 5 entirely. Refresh is a V1 task in itself.

2. **`fact_shipment_invoice_lines/sql/diagnostics/`** — README cites `db_schenker_charge_codes.sql`, `db_schenker_empty_charge_code.sql`, `db_schenker_empty_pattern.sql`, `db_schenker_empty_signals.sql`, `db_schenker_bronze_inspection.sql` (5 files). **Directory does not exist.** Either removed in a cleanup commit or never committed to begin with.

3. **`fact_truck_charges` diagnostics** — README references `sql/diagnostics/check_same_plate_multi_truck.sql` and `sql/diagnostics/check_session_dedup_result.sql`. Same caveat — **not confirmed present in tree** (only the 3 main SQL files are committed: `insert_to_silver.sql`, `update_allocation.sql`, `update_rate_lookup.sql`).

4. **`legacy_adhoc_corrections.md`** under `fact_shipment_invoice_lines/` — empty registry (template only, no entries filled in). Created as Tier-3 reconciliation tracking surface; reconciliation work clearly underway (NGE-6428 cited in README) but findings have not landed in this file. Possibly tracked elsewhere (commit messages, ClickUp comments).

5. **`dim_carrier_sla`** — entirely absent from repo despite being a hard dependency for SLA-breach analytics. Either an explicit V1 deferral or a forgotten table.

6. **`fact_shipments` row 21 `packagetype_group`** — column in DDL, NULL until a SharePoint mapping is created. Spec status `[ ]` since the mart was scoped.

7. **`fact_shipments` rows 48 / 49 / 53 / 54** — four columns (`expected_shipping_cost_eur`, `avg_shipping_cost_eur`, `user_packing_order`, `loading_unit_id`) all `[ ]` in v1, all blocked on upstream sources not yet promoted to enterprise_bronze. T-14 (expected cost source) and T-32 (avg cost grain) are unresolved per README §"Realistic TODO."

8. **`fact_shipments` row 41 `is_returned`** — `[!]` in spec; no return-event vocabulary in the source tracking-log tables. Stays NULL in v1; design owes a separate return-items source.

---

## Summary counts

- **8 mart tables claimed by brief.** 7 built (`map_shipment_key`, `fact_shipments`, `fact_shipment_orderitems`, `fact_shipment_invoice_lines`, `fact_shipment_cost_summary`, `fact_truck_charges`, `dim_shipping_providers`). 1 not built (`dim_carrier_sla`).
- **1 extra subdir wired** in mart: `dim_truck_costs` (bronze-target SharePoint dim).
- **TODO/FIXME/HACK/XXX markers in code (.py + .sql, mart-only):** ~25 distinct (15 in `fact_shipment_invoice_lines/sql/providers/`, 4 in `fact_shipment_orderitems/`, 3 in `map_shipment_key/sql/`, 2 in `fact_shipments/sql/`, 1 in `data_lineage_review.md`). One stray `XXX` literal at `fact_shipments/sql/insert_to_silver.sql:1145` is a string sentinel, not a marker.
- **TODO markers in READMEs:** ~30+ (heavy concentration on `fact_shipments/README.md` bronze-migration rows for PII/event columns; `fact_shipment_invoice_lines/README.md` Outstanding-TODOs + NGE-6426/6427/6428 follow-up sections).
- **Commits on mart in last 6 weeks:** 241. Heavy late-stage activity (60+ commits in last 7 days).
- **Engineers active on mart:** Łukasz Sendecki (lead), SatyaVarma Rudraraju (NGE-6129 ORWO owner), Dexos21, Miłosz Serej. Grzegorz Strawa handles merges.

---

## Out-of-scope cross-refs (for principal-Jebrim synthesis, not for D2)

- D3 should probe Redshift for `dim_carrier_sla` existence — repo confirms NOT-in-repo, but the table could exist Redshift-side from an out-of-band DDL run.
- D3 should also confirm whether `fact_shipment_cost_summary` is populated in Redshift, since the main README disagrees with reality.
- D1 should look for a ClickUp ticket on the top-level README refresh (it's stale enough to be its own gap-list item).
- ORWO `orwo_revenue` stream (Navision) is flagged in `fact_shipment_orderitems/README.md:61` as a separate follow-up — neither built nor scoped on bi-etl side in this folder.
