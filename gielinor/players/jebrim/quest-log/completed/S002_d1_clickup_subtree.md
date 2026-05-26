# [[S002_2026-05-20_shipping-data-mart-v1-gap-analysis|S002]] D1 — NGE-6120 subtree map

**Dwarf:** Jebrim (inherited), D1 of [[S002_2026-05-20_shipping-data-mart-v1-gap-analysis|S002]]
**Date:** 2026-05-21
**Scope:** ClickUp epic NGE-6120 + every subtask + every nested subtask + comments + attachments
**Out of scope:** repo reads, redshift queries, NFE docs

## Tree shape

```
NGE-6120  Shipping Data Mart (epic, in progress)
├── NGE-6009  Shipping Invoice Costs — Enterprise Pipeline Migration & Consolidation (staging)
│   ├── NGE-6020  Bronze Backfill from poc_landing and bi_stage (staging)
│   ├── NGE-6056  Silver Backfill from poc_staging and bi_asa (staging)
│   ├── NGE-6081  [Docs] Shipping Structures Report (HTML) (staging)
│   └── NGE-6082  [Docs] Update Shipping_Costs_ETL_Flow report (HTML) (in progress)
├── NGE-6427  cleaning up invoice pipelines (to do)
├── NGE-6121  Map Shipment Key (production)
├── NGE-6122  Fact Shipments (in progress)
├── NGE-6123  Fact Shipment Orderitems (in progress)
├── NGE-6124  Fact Shipment Invoice Lines (in progress)
├── NGE-6125  Fact Shipment Cost Summary (staging)
├── NGE-6126  Fact Truck Charges (staging)
├── NGE-6127  Dim Shipping Providers (production)
├── NGE-6128  Dim Carrier SLA (to do)
├── NGE-6129  Integrate Orwo data (in progress)
├── NGE-6299  Invoice table standardization (production)
├── NGE-7094  Comparison of fact_shipment_invoice_lines vs invoice sources and factshipmentcosts (in progress)
├── NGE-6428  comparing invoice lines table cost against source (in progress)
├── NGE-7096  Compare invoice allocation to orders (production)
├── NGE-7117  Compare final shipping cost between fact_shipments and dw.sales_fact (to do)
├── NGE-7097  Comparison of fact_shipments and orders gold layer (in progress)
├── NGE-6494  Refactor column types in bronze layer (to do)
├── NGE-6755  Fixes (in progress)
├── NGE-7093  Investigate why we have no recent costs for FXESPPS (production)
├── NGE-7100  Ensure POST_DVF shipments have shippingprovider_extkey + trackingnumber='untracked' (production)
├── NGE-7102  Implement ORPS data (to do)
├── NGE-7104  Migrate the data mart to the gold layer (to do)
├── NGE-7108  Develop a semantic layer for the data mart (to do)
├── NGE-7109  Ensure UPS refunds are allocated to orders (staging)
├── NGE-7105  Ensure cost_source in fact_shipments only has avg/expected/invoice/NULL (release)
├── NGE-7110  fact_shipments has 1588 duplicate shipment_ids (staging)
├── NGE-7106  Logic check for truckloads/loadingunits/allocated_truckloads (to do)
├── NGE-7107  Define ORWO truck consignment cost logic (to do)
├── NGE-7111  Define returned shipments (to do)
├── NGE-7112  Define packagetype group (to do)
├── NGE-7114  Define and implement archived date (production)
├── NGE-7115  fact_shipment_invoice_lines.invoice_source should contain exact source table name (to do)
├── NGE-7116  Change shippingprovider to shippingprovider_extkey in fact_shipment_invoice_lines (release)
├── NGE-7125  Billed weight logic in invoice lines (production)
├── NGE-7142  Alerts & DQ Checks (to do)
├── NGE-7146  Refactor shipment event timestamps and transit times (staging)
├── NGE-7269  Add archived date to fact_shipments (to do)
├── NGE-7273  implement ORWO expected shipping cost (to do)
└── NGE-7282  Implement Sendmoments data (to do)
```

**Total: 93 tickets** (epic + 40 direct subtasks + 4 nested under NGE-6009 + 24 nested under NGE-6020 [NGE-6031..6054] + 24 nested under NGE-6056 [NGE-6057..6080 + NGE-6106]). All 48 deepest leaves under NGE-6020/6056 are per-carrier backfill subtasks — all in `production` (done), except their parity-validate leaves (NGE-6054, NGE-6080) in `staging`. They are migration plumbing, not V1-blocking, and are captured as a group below rather than 1-by-1.

---

## Epic — NGE-6120 Shipping Data Mart

- **Status:** in progress | **Priority:** high | **Due:** 2026-04-29 | **Updated:** 2026-05-20
- **Assignees:** Grzegorz Strawa, Łukasz Sendecki, Davis Lozda, Miłosz Serej, Satya Varma Rudraraju
- **URL:** https://app.clickup.com/t/869cz54v3
- **Attachments:** `data_model.html` — https://t9012440763.p.clickup-attachments.com/t9012440763/baffb852-5a07-44ec-8fdf-618df59d20f2/data_model.html (canonical likely under `bi-etl/dags/enterprise_silver/Shipping_Data_Mart/`; D2 should verify path)
- **Comments:** 1 (just the attachment drop by Davis 2026-04-23)
- **Linked tasks:** none
- **State summary:** Epic carries the design (8 tables: 1 map + 5 facts + 2 dims; cost_source = invoice/expected/avg; SCD Type 1; data ≥2024-01-01). Description still lists open blockers T-14/T-15/T-16/T-17/T-20/T-32/T-34. No comment activity since the data_model.html drop.
- **V1-relevance:** `V1-blocking` (epic itself).

---

## NGE-6121 — Map Shipment Key

- **Status:** production | **Priority:** — | **Due:** 2026-04-23 | **Updated:** 2026-05-13 | **Done:** 2026-04-22
- **Assignees:** Grzegorz Strawa | **Watchers:** Davis Lozda, Łukasz Sendecki
- **URL:** https://app.clickup.com/t/869cz5c3q
- **Comments:** 6 (most recent 2026-05-13)
- **Attachments:** none | **Linked tasks:** none
- **State summary:** Built `enterprise_silver.map_shipment_key`. Currently 18.78M rows from 4 source branches (PICT 76.7%, PICAAPI 15.8%, PCS 7.5%, Rewallution 0.03%) — 0 dupes, 0 hash collisions. Surrogate `shipment_id = STRTOL(LEFT(MD5(tracking|order),15),16)::BIGINT`. Added `shippingprovider_extkey` column (2026-04-27) feeding all 23 fact provider SQLs. Latest comment (2026-05-13): normalized N-suffix carrier extkeys (`USPSN→USPS` + 26 auto-detected pairs; 17 pure-N extkeys left as natural endings). DAG at `dags/enterprise_silver/Shipping_Data_Mart/map_shipment_key/`.
- **Open / blocked:** Rewallution PL `dpd_poland_rewallution` invoices (4,245 rows) have 0% shippingprovider match — Rewallution source has no provider column (confirmed with Niklāvs). Open TODOs passed to ETL/platform: pict_orders filter relax 2024+→2022+; pcs_orders silver is 2-month rolling window; rew_orders silver empty; pcs_sentparcels silver ~65% of bronze.
- **Awaiting Niklavs:** dim_shipping_providers normalization via CASE WHEN pattern matching on extkey (called out by Grzegorz; that's NGE-6127 work).
- **V1-relevance:** `V1-blocking` (table is the spine; status is `production` but downstream cleanups are still open).

---

## NGE-6122 — Fact Shipments

- **Status:** in progress | **Priority:** — | **Due:** 2026-04-25 | **Updated:** 2026-05-12
- **Assignees:** Łukasz Sendecki | **Watchers:** 3
- **URL:** https://app.clickup.com/t/869cz5c83 | **Comments:** 11 | **Attachments:** none
- **State summary:** Spine fact (~60 cols, 1 row per shipment_id). Heavy iteration over 3 weeks. Recent: 2026-05-12 added `order_produced_ts/_date` from `pcs_orderlogs.action='SHIPPING_TRACKED'`; 2026-05-08 wired `pict_shipmentlogs` into bronze (was defined-but-never-instantiated); 2026-05-07 NULL guards on `transit_time_days` (~3.8K shipments had negatives from corrupt event logs); 2026-05-06 PICT `is_reorder` switched from `reorderof`→`reorderreason`; 2026-05-05 `service_type` → `shippingprovider_extkey` rename; 2026-05-04 PCS source migrated bronze→silver after `DISTSTYLE ALL` on 9.7M rows hung ALTER 5+min/col; 2026-04-30 `loading_unit_id` + `shipping_provider_group` denormalised; 2026-04-29 `temp_*` placeholder shipments + revenue allocation Phase 1+2; 2026-04-28 1.44M Picturator rows fixed (99.35% were `state='INVALID'`); 2026-04-27 VARCHAR overflow fixes refactor into 16 single-session steps; 2026-04-24 initial ship with 57 columns.
- **Open / blocked:** Per epic — T-10/T-11 (event sources/values), T-14 (expected cost), T-15 (real cost), T-32 (avg), T-34 (net_revenue scope).
- **Awaiting Niklavs:** none current; recent decisions (`reorderreason`, smoothed cost, FRP placeholder, source priority) consumed Niklavs input.
- **V1-relevance:** `V1-blocking` (still `in progress`).

---

## NGE-6123 — Fact Shipment Orderitems

- **Status:** in progress | **Priority:** — | **Due:** — | **Updated:** 2026-05-12
- **Assignees:** Łukasz Sendecki | **Watchers:** 3
- **URL:** https://app.clickup.com/t/869cz5ckp | **Comments:** 6 (most recent 2026-05-12) | **Attachments:** none
- **State summary:** Built. Grain `(shipment_id, source_order_item_id)`, unions 4 sources, FX-converts revenue, attaches `shipment_id` via map. Heavy recent fixes: 2026-05-12 documented ~28K Print-Logistics shop residual (Hey Dear/Persoking/FamShirt/Pfotengut) — accepted gap per Niklavs, no fix planned; 2026-05-11 consolidated picaapi PCS-bridge rescue (+40,910 picaapi items, 70 stripping-edge regressions = 0.002%), truncate-late refactor, attached R-suffix PCS reorder parcels (+28,321 R-parcel rows revenue=0); 2026-05-05 reorder logic deep-dive — 1.37M PICT `reorderreason` orders without flag were 97.86% empty strings, real defects ~30K already flagged correctly; PCS R vs reorderof 0% overlap; PicaAPI product_key 99.97% coverage; 2026-05-01 PCS dedup priority fix shrank PCS rows 1.49M→6,987 (−99.5%); 2026-04-22 initial ship — reshipment double-counting fixed (orderitem 38279099 case, Picturator revenue −3.4%, PicaAPI −2.3%).
- **Open / blocked:** Order-state filter scope decision (Niklavs to choose: mirror `enterprise_silver/revenues` filters or stay wider with `testorder=FALSE`). Missing-tracking fallback for ~1.27M PCS orders shadowed by shop-side `tracking_number IS NULL`. Replace `dw.dim_products` with enterprise product dim. Migrate `picaapi_shipment_items` poc_landing→enterprise_bronze. `option_key`/`format_key` still NULL pending warehouse dim def.
- **Awaiting Niklavs:** order-state filter decision; missing-tracking fallback approach.
- **V1-relevance:** `V1-blocking`.

---

## NGE-6124 — Fact Shipment Invoice Lines

- **Status:** in progress | **Priority:** — | **Due:** 2026-04-23 | **Updated:** 2026-05-13
- **Assignees:** Miłosz Serej, Grzegorz Strawa | **Watchers:** 4
- **URL:** https://app.clickup.com/t/869cz5cue | **Comments:** 11 | **Attachments:** none
- **State summary:** Per-carrier invoice unpivot (23 providers — UPS, FedEx, DHL America, DHL Orwo, GLS, Maersk, OnTrac, Yodel, USPS, APG, Asendia USA, Colis Prive, Direct Link, DPD UK, DPD Poland struct1/struct2/rewallution, UPS Orwo, etc.). Recent: 2026-05-13 date-aware MSK join for 19 tracking-keyed providers (old `PARTITION BY tracking ORDER BY source_order_id` collapsed on date); 2026-05-04 NULL cost_source gap diagnosis — 868K NULL-cost shipments, 442K (51%) match in `enterprise_silver.shipping_costs` by tracking but NOT in `fact_shipment_invoice_lines` (98% pre-2024, OUT of v1 scope); 2026-05-04 DPD UK phantom truck_surcharge fix (Niklavs-reported test parcel `15509993064406A` showed £5.12/€5.91 vs actual £2.91/€3.36 — phantom charge_bucket row); 2026-04-30 — Miłosz cleaned up 4,833 silver duplicates (941 groups), dropped frankenstein `bronze_dhl_prod` CTE (see NGE-6428); 2026-04-28 +`Prod` to insert + dedup on (Trackingnumber, InvoiceId, Prod), 99.99% coverage; 2026-04-27 23-carrier sanity check, DB Schenker classification gap €3.5M/195k rows all unclassified; 2026-04-24 Asendia USA per-charge split; 2026-04-23 5-thread silver_fact_shipment_invoice_lines ship; 2026-04-22 DPD Poland renames (`dpd_poland`→`dpd_poland_struct1`, `dpd_poland_customs_and_duties`→`dpd_poland_struct2`); 2026-04-20 initial unpivot to silver.
- **Open / blocked:** T-15 (per-carrier inspect), T-16 (currency per carrier), T-20 (gold vs silver layer). DB Schenker bucket classification (€3.5M unclassified). 868K NULL cost (51% pre-2024 — out-of-scope; 49% in-scope diagnostic still open). NGE-6428 split off for cost-vs-source comparison. NGE-7094 (vs `factshipmentcosts`), NGE-7115 (`invoice_source` exact name), NGE-7116 (`shippingprovider`→`shippingprovider_extkey`), NGE-7125 (billed weight) all spawn from this work.
- **Awaiting Niklavs:** DPD UK bucket validation pattern (precedent set on 2026-05-04 case).
- **V1-relevance:** `V1-blocking`.

---

## NGE-6125 — Fact Shipment Cost Summary

- **Status:** staging | **Priority:** — | **Due:** 2026-04-28 | **Updated:** 2026-05-13
- **Assignees:** Satya Varma Rudraraju | **Watchers:** 4
- **URL:** https://app.clickup.com/t/869cz5d4d | **Comments:** 9 (most recent 2026-05-13 Satya: "@Łukasz can we close this?") | **Attachments:** none
- **State summary:** Pivot of `fact_shipment_invoice_lines` to per-shipment buckets. 2026-05-13 ready-to-close prompt by Satya. 2026-05-12 `cost_per_parcel_eur_smoothed` consumption propagates Niklavs's smoothed-cost change into `fact_shipments.real_shipping_cost_eur`. 2026-05-10 3-tier cost waterfall on fact_shipments: Pass1 invoice (61% rows, 9.76M), Pass2 expected (32%, 5.13M), Pass3 avg (1%, 128K), NULL 5% (pre-2024). Excluded sentinel tracking `'164750000075'` (17M-row NULL artifact in `silver.avg_shipping_costs`). 2026-05-10 (Satya) bug: `total_eur`/`total_local` previously excluded truck_charges — fix wraps in CASE adding `truck_charges_*`. 2026-05-05 expected_shipping_cost wired via `asa.temp_expected_shipping_costs_pack`. 2026-05-03 alerting (3-min SLA) registered via Airflow Variables; removed no-op `validate_cost_summary` task. 2026-05-02 `discounts_eur`/`discounts_local` bucket added (~€3M FedEx/GLS/Ontrac contractual rebates). 2026-04-29 ticket-validation matrix in README. 2026-04-29 initial pivot ship.
- **Open / blocked:** `silver_avg_shipping_costs` not yet wired into mart orchestrator (uses last successful run, may lag hours). `truck_charges_local` always NULL in v1 per design until T-17. Awaiting Łukasz close.
- **Awaiting Niklavs:** none direct (Satya/Łukasz on this).
- **V1-relevance:** `V1-blocking` (in staging, close pending).

---

## NGE-6126 — Fact Truck Charges

- **Status:** staging | **Priority:** — | **Due:** 2026-04-24 | **Updated:** 2026-05-20
- **Assignees:** Łukasz Sendecki | **Watchers:** 3
- **URL:** https://app.clickup.com/t/869cz5d8t | **Comments:** 7 | **Attachments:** none
- **State summary:** Built. Per-truck-session grain (license plate + production site + session merge ≤12h). 2026-05-12 Step 4a allocation refactor — 10+min→1-2min via `#truck_window_alloc` pre-filter on `%ORWO%`, `#truck_countries` explode (replaces `POSITION(',' || ... ',' IN ',' || REPLACE(...))` per-row scan = billions of evals), `ANALYZE` on temp tables; added `cost_per_parcel_eur_smoothed` (Niklavs request, 10-row trailing window per truck_provider) to stabilize 5× swings in raw value. 2026-05-11 ORWO Consignment carve-out bug — UK DHL Freight truckload 15570 showed 41 alloc / 88.29 EUR vs actual ~1126 / 3.21 EUR; root cause: ORWO Consignment row in `dim_truck_costs` had empty country/provider = catch-all. 2026-05-05 truck 12391 anomaly investigation — Colis Prive €150 label, 8779 shipments allocated vs 542 real CPRHD/FR/Szczecin; root: license plate `PZ7T193` has multiple `pcs_truckloads` rows per day with different `name` (Yodel 11:08 + COLIS 11:29), session merge collapses to one canonical, both rate rows match in `dim_truck_costs` → `ROW_NUMBER ORDER BY valid_from DESC` ties → nondeterministic. Quantified: 315 plate-days, ~220 plates since Jan-2025 (Colis Prive + UK DHL Freight 141 plate-days, APG + UK DHL Freight 94, APG + Colis Prive 40). Niklavs resolved by consolidating UK DHL Freight + Colis Prive + APG into one "UK and FR DHL Freight" SharePoint rate row (87% of mixed cases). Code change: dropped placeholder license plates BŁĄD/DHL/USPS/DHL CONTAINER ("we do not end up paying for these trucks"). `transit_time_days` switched to `DATEDIFF(second, ts, ts)/86400.0::NUMERIC(6,2)` for fractional precision. 2026-05-01 allocation double-counting fix (16.1M allocated vs 313k real on Szczecin/CPRHD/FR), `rate_valid_from` leak fix (535k Colis Prive / 673k UPS dumped onto first truck of new rate period in Jan-2025). Side-by-side vs `asa.v_truck_surcharges`: UPS DHL Freight 87-120% match; Colis Prive/APG ±30%; UK DHL Freight 2025-11+ near-perfect. 2026-04-30 SharePoint dim_truck_rates wiring + session logic from `id`-grain to `licenseplate+productionsiteid+gap`. 2026-04-25 initial DAG ship.
- **Open / blocked:** Niklavs to refine `dim_truck_costs` patterns — DHL Kleinpaket `%DHL%W%` overinclusive (overstated cost), Colis Prive too narrow (understated), define ORWO Consignment SZZ↔ORWO split rule, confirm DHL Kleinpaket country scope. Then re-run + re-validate. Further perf: tighten `candidate_pairs` pairing window upper bound (~30d) on `departure_ts - sent_ts`.
- **Awaiting Niklavs:** `dim_truck_costs.truck_database_identifier` pattern refinement.
- **V1-relevance:** `V1-blocking` (staging, several Niklavs items hold it).

---

## NGE-6127 — Dim Shipping Providers

- **Status:** production | **Priority:** — | **Due:** 2026-04-29 | **Updated:** 2026-04-30
- **Assignees:** Niklavs Felsbergs, Grzegorz Strawa | **Watchers:** 3
- **URL:** https://app.clickup.com/t/869cz5dra | **Comments:** 4 | **Attachments:** none
- **State summary:** Standing in Redshift. DDL `DISTSTYLE ALL` SORTKEY on `extkey`, `MD5(source_system||'|'||TRIM(extkey))` PK (per 2026-05-13 update — was `MD5(extkey)` originally). Now scoped by source_system: same extkey under different source systems is a separate dim row (e.g. PCS/DHLPKT vs Picturator/DHLPKT). Initial load 188 providers / 24 groups (DHL 31, FEDEX 23, UPS 23, DPD 13, YODEL 11, DIRECT LINK 9, GLS 6, STANDARD 6, ASENDIA 5, MAERSK 5, ROYAL MAIL 4, DB SCHENKER 3, DPD POLAND 3, LANDMARK 3, APG 2, COLIS PRIVE 2, DPD UK 2, HERMES 2, AMBRO 1, ASENDIA USA 1, GEL 1, ONTRAC 1, USPS 1, OTHER 37 — incl. 'BRIEF', 'DUMMY', 'P2P', 'LETTER', 'ASB', 'ASN', 'RMTRACKEDHVNOSIG' for review). Coverage vs MSK: 14.75M/18.78M (78.5%); 4.03M NULL extkey (NGE-6121 known); 30 empty-string edge; 0 unmatched. ASENDIA rule fix (`LIKE '%ASENDIAUS%'` not `LIKE '%ASENDIA%' AND NOT '%US%'` — was excluding `ASENDIAEPAQPLUS` due to "PLUS" matching). DPD ordering: DPD POLAND and DPD UK moved above generic DPD catch-all.
- **Open / blocked:** 30 ORWO carrier extkeys auto-loaded by NGE-6129 Step 2 (2026-05-15) with NULL `shippingprovider_group`/`service_type`/`truck_provider`/`has_truck_cost` — **Niklavs to classify** (carriers: CIRRO, CPRHD, DBSCHENKER, DHL, DHL2, DHLKP, DHLX2, DPD, FKBRING, FKBRINGPARCEL, GUELL, MAERSKFR, POST, POSTAT, POSTAT_FR/_GB/_L/_P, POSTNL_AVG/_EU/_MB, POST_DVF, TD, UNITEDPRINT, UPS, UPSEXPRESS, UPSWEA, UPSWWE, WPOST3, WPOST4).
- **Awaiting Niklavs:** ORWO carrier classification (30 rows). One ticket comment 2026-04-25 Niklavs replied "Query already provided to @Grzegorz Strawa"; Davis Lozda asked "but isnt this on Niklavs to provide?" — context unclear but ticket then moved to production.
- **V1-relevance:** `V1-followup` (table is `production` but ORWO classification is V1-blocking — see NGE-6129 #1).

---

## NGE-6128 — Dim Carrier SLA

- **Status:** to do | **Priority:** — | **Due:** 2026-04-29 | **Updated:** 2026-05-14
- **Assignees:** Niklavs Felsbergs | **Watchers:** 3
- **URL:** https://app.clickup.com/t/869cz5e0h | **Comments:** 0 | **Attachments:** none
- **State summary:** Not yet started. Design locked: SCD Type 2 (`valid_from`/`valid_to`), grain carrier × service_type × destination_country_code. Source = SharePoint. SLA derived in reporting view (not stored on `fact_shipments`) — `sla_breach_flag = transit_time_business_days > sla.sla_business_days`. v1 limitation: `dim_date.isweekday` only, no per-country public holidays.
- **Open / blocked:** Entire ticket. Niklavs-owned, no movement on it; due date 2026-04-29 missed.
- **Awaiting Niklavs:** Build the SharePoint export + stand up the table. This is **the** SLA-breach gate for V1.
- **V1-relevance:** `V1-blocking`. The mart's SLA reporting view depends on this dim existing.

---

## NGE-6129 — Integrate Orwo data

- **Status:** in progress | **Priority:** high | **Due:** 2026-04-29 | **Updated:** 2026-05-21
- **Assignees:** Niklavs Felsbergs, Satya Varma Rudraraju | **Watchers:** 5
- **URL:** https://app.clickup.com/t/869cz6dkq | **Comments:** 14 (most recent 2026-05-21 = today) | **Attachments:** `orwo_open_pointers.html` (latest by Satya 2026-05-21; URL: https://t9012440763.p.clickup-attachments.com/t9012440763/296da0bd-50ec-4964-866a-377adf293836/orwo_open_pointers.html). **Canonical copy in repo: `bi-etl/dags/enterprise_silver/Shipping_Data_Mart/orwo_open_pointers.html` (commit `9af27d823`)** — prefer this over the ticket attachment per the team's HTML pattern. Note: a prior attachment `f4dfed68-…` is stale per Satya's 2026-05-21 comment.
- **State summary:** All 6 structural integration steps are merged (Steps 1-6 completed 2026-05-15 to 2026-05-20). Step 1 (MSK ORWO branch) — `dhl_orwo` pct_null 60.99→1.34% / 4.25%; `ups_orwo` 22.48→3.02% / 3.06%; ~1.74M invoice lines resolved. Step 2 (dim auto-extension) — 30 ORWO carriers added 2026-05-15 09:58, NULL classification awaiting Niklavs. Step 3 (`fact_shipments`) — 2.49M ORWO rows, 100% on shop/production_site/created_ts/received_by_carrier_ts/shipping_provider_id; weight_kg 53%, length_cm 46.6%, packagetype 46.1% (orwo_usedpackaging LEFT JOIN); destination_country/PII/production_order*/truckload_id 100% NULL by design. `production_site` renamed `'ORWO'`→`'Wolfen'` (Wolfen = physical facility). Step 4 (`fact_shipment_orderitems`) — 89.6M ORWO item rows via `orwo_orderdeliveryorderlinerelation` M:N linker; ~36 items/shipment (photo-print product mix); revenue_eur NULL (Navision join is follow-up), product_key NULL (`dw.dim_products` 0.02% match → dim extension follow-up). Step 5 (bulk-mail cost allocation) — DENSE_RANK by `sentat` + charge/share_n; total money preserved €3,045,760.03 bronze = distributed. Step 6 (diagnostics + docs) `34d030a23` — health-check SQL `diagnostics/orwo_coverage_crosscheck.sql`. 2026-05-21 update: bug #3 cross-source event-stream pollution **resolved** by Łukasz (commit `7e552464f`, NGE-7146, 2026-05-20 — auto-deployed by scheduler 2026-05-21 04:00 UTC) — ORWO `delivered_by_carrier_ts`/`current_shipping_status` 100% NULL (was 98.1%/98.2%); `received_by_carrier_ts` 99.9987% populated via `sentat` fallback.
- **Open follow-ups (4 from open-pointers HTML, 2026-05-21):**
  - ① **Carrier classification** — 30 ORWO carriers in dim need `shippingprovider_group`/`service_type`/`truck_provider`/`has_truck_cost` — **Niklavs-owned**.
  - ② **dim_products extension** — ORWO SKUs not in product dim — Data Platform-owned.
  - ④ **Missing destination_country** — needs Navision lookup — ENG-owned, next up (Satya picking up).
  - ⑤ **ORWO expected shipping cost formula port** — ENG-owned, blocked by ④.
- **Awaiting Niklavs:** ORWO carrier classification (30 rows in NGE-6127). POST_DVF expected-cost sentinel (NGE-7273).
- **V1-relevance:** `V1-blocking` (ORWO required for V1 per principal).

---

## NGE-6009 — Shipping Invoice Costs — Enterprise Pipeline Migration & Consolidation

- **Status:** staging | **Priority:** high | **Due:** 2026-04-29 | **Updated:** 2026-04-20
- **Assignees:** Grzegorz Strawa | **Watchers:** 2
- **URL:** https://app.clickup.com/t/869cxv4k1 | **Comments:** 0 | **Attachments:** none
- **State summary:** Sub-epic for migrating all 23 carrier-invoice pipelines from `poc_landing`/`bi_stage_dev_dbo` → `enterprise_bronze` and `poc_staging`/`bi_asa_dev_dbo` → `enterprise_silver`. Four direct subtasks (3 of 4 in staging, 1 in progress). All 48 deepest-level per-carrier backfill leaves under NGE-6020 and NGE-6056 are in `production` (done). Parity-validate tasks (NGE-6054, NGE-6080) are in `staging` — the only loose ends in this branch.
- **V1-relevance:** `V1-followup` (heavy lifting done; the rest carries epic-level state but no V1-blocking items beyond cleanup).

### NGE-6009 family (rollup — 4 children + 48 grandchildren)

| Ticket | Name | Status | Notes |
|---|---|---|---|
| NGE-6020 | Bronze Backfill | staging | 24 per-carrier backfill leaves (NGE-6031 DHL, NGE-6032 DPD Poland, NGE-6033 DHL Orwo, NGE-6034 Yodel, NGE-6035 Colis Prive, NGE-6036 DHL America, NGE-6037 Ontrac, NGE-6038 DB Schenker, NGE-6039 UPS Orwo, NGE-6040 DPD UK, NGE-6041 Asendia USA, NGE-6042 Maersk, NGE-6043 Direct Link, NGE-6044 USPS, NGE-6045 UPS, NGE-6046 FedEx, NGE-6047 APG, NGE-6048 GLS, NGE-6049 Hermes, NGE-6050 Landmark Global, NGE-6051 DPD generic, NGE-6052 Ambro, NGE-6053 DPD Poland Rewallution — all in `production`) + NGE-6054 parity-validate (`staging`) |
| NGE-6056 | Silver Backfill | staging | 24 per-carrier backfill leaves (NGE-6057 UPS, NGE-6058 DHL, NGE-6059 FedEx, NGE-6060 DHL Orwo, NGE-6061 Yodel, NGE-6062 DPD Poland 1st, NGE-6063 Colis Prive, NGE-6064 DHL America, NGE-6065 Ontrac, NGE-6066 USPS, NGE-6067 UPS Orwo, NGE-6068 DPD UK, NGE-6069 Asendia USA, NGE-6070 Maersk, NGE-6071 Direct Link, NGE-6073 GLS, NGE-6074 DPD generic, NGE-6075 Hermes, NGE-6076 APG, NGE-6077 Landmark Global, NGE-6078 Ambro, NGE-6079 DPD Poland Rewallution, NGE-6106 DB Schenker — all in `production`) + NGE-6080 parity-validate (`staging`) |
| NGE-6081 | [Docs] Shipping Structures Report (HTML) | staging | Docs deliverable. No comments. |
| NGE-6082 | [Docs] Update Shipping_Costs_ETL_Flow report (HTML) | in progress | Docs deliverable. No comments. |

All 48 backfill leaves: 0 comments, 0 attachments, no assignees, no priorities, no due dates. They are migration plumbing; treat as `out-of-scope` for V1 gap analysis (they're already done). The 2 staging parity-validate tickets are `V1-followup` cleanup.

---

## NGE-6427 — cleaning up invoice pipelines, ensure only enterprise layers are used

- **Status:** to do | **Priority:** normal | **Due:** — | **Updated:** 2026-05-18
- **Assignees:** Grzegorz Strawa | **Watchers:** 3 | **Comments:** 0 | **Attachments:** none
- **URL:** https://app.clickup.com/t/869d1u6kx
- **State summary:** Decommission plan — shut down Pentaho and delete `poc_*` / `asa.*` schemas without breaking the mart. No work started.
- **V1-relevance:** `out-of-scope` (post-V1 decommission).

---

## NGE-6299 — Invoice table standardization

- **Status:** production | **Priority:** low | **Due:** 2026-04-29 | **Updated:** 2026-05-13
- **Assignees:** Grzegorz Strawa | **Watchers:** 3 | **Comments:** 2 | **Attachments:** none
- **URL:** https://app.clickup.com/t/869d05ppt
- **State summary:** Done. 2026-04-25 silver renamed 23 tables to `{provider}_invoices`; bronze 20 renamed (DPD Poland 1st/2nd/Rewallution; Landmark `raw_historical` → `*_invoices`). 2026-05-13: DB Schenker refactor introduces `enterprise_silver.db_schenker_lines` (per-charge-line grain) as approved extension. Naming rule going forward: any new feed lands `{provider}_invoices` in bronze, propagates to silver.
- **V1-relevance:** `V1-followup` (cleanup-shaped; not blocking but worth tracking the `_lines` convention for new providers).

---

## NGE-7094 — Comparison of fact_shipment_invoice_lines vs invoice sources and bi_dw_dev_dbo.factshipmentcosts

- **Status:** in progress | **Priority:** high | **Due:** — | **Updated:** 2026-05-20
- **Assignees:** Niklavs Felsbergs, Grzegorz Strawa | **Watchers:** 3 | **Comments:** 5 | **Attachments:** none
- **URL:** https://app.clickup.com/t/869d9x5jd
- **State summary:** Mart vs legacy `factshipmentcosts` cost reconciliation. 2026-05-14 baseline `enterprise_silver.tmp_factshipmentcosts_no_truck` (1:1 of legacy proc, truck-surcharge stripped for apples-to-apples). 2026-05-15 reviewed all providers — 2 real mart bugs found+fixed (Yodel double-count, USPS provider FX), 2 missing credit notes (Asendia USA + ONTRAC, pattern was poc_landing manual loads). 2026-05-18 FedEx drift −€253k → −€5,632 (0.05%) — 3 mart fixes in `dags/enterprise_silver/Shipping_Data_Mart/fact_shipment_invoice_lines/sql/providers/fedex.sql`: removed silver-aggregate block, extended bronze-pairs bridge. 2026-05-19 DHL Nov/Dec 2025 — fuel rows collapsed by outer DISTINCT (+€75k drift fixed) — root cause in `dags/shipping_invoice_cost/FactShipmentCosts_DW_main_job/sql/fact_shipment_costs.sql` global outer `SELECT DISTINCT` dedupes on 8 business cols. 2026-05-20 **DB Schenker MATCH** — root cause: 2 stacked bugs (Bug 1: bronze loader dropped multi-row invoice updates due to `NOT EXISTS WHERE invoice_number`).
- **Open:** continuing carrier-by-carrier reconciliation.
- **V1-relevance:** `V1-blocking` (this is the validation gate for whether the mart cost data matches reality).

---

## NGE-6428 — comparing invoice lines table cost against source

- **Status:** in progress | **Priority:** high | **Due:** — | **Updated:** 2026-05-14
- **Assignees:** Miłosz Serej, Grzegorz Strawa | **Watchers:** 4 | **Comments:** 2 | **Attachments:** 1 image (per-month drift PNG)
- **URL:** https://app.clickup.com/t/869d1u6hp
- **State summary:** Per-carrier mart-vs-legacy parity. 2026-05-11 DB Schenker tier-2 deep dive: silver=fact 195,686 rows / €3,512,028.43; 100% unclassified bucket (waiting for new format from DBS, Niklavs decision); 2025 +5,129 rows / −€71k anomaly. 2026-05-14 DHL + UPS full legacy parity in `fact_shipment_invoice_lines` (within rounding noise). Net: monthly adhoc adjustment universalised via new bronze table `shipping_adhoc_provider_total_adjustment` (mirrors legacy `additional_costs(adhoc).sql`); DHL VAT branch now `charge_description='tax'` (per Niklavs); UPS RTS filter + 90-day returns redistribution from `bi_stage_dev_dbo.csv_ups_zip_invoicedata_temp1` (mirrors legacy `UPS_add_returns.sql`). Registry `legacy_adhoc_corrections.md` entries #1 (monthly adhoc) + #3 (UPS returns) marked IMPLEMENTED. Validation: DHL 2024H1 was −1.34% → ~0%; 2025 +1.24% remains (legacy `SELECT DISTINCT` data-loss bug, registry entry #2 — our fact is more correct, no port). UPS every month 2024-2026 within ±0.4% (was −€15k 2024H1, briefly +€24k after global adhoc, now ±€500/month).
- **Open:** Yodel Tier 3 reconciliation next, then GLS / DHL Orwo.
- **Awaiting Niklavs:** DBS new format decision (100% unclassified bucket).
- **V1-relevance:** `V1-blocking`.

---

## NGE-7096 — Compare invoice allocation to orders

- **Status:** production | **Priority:** high | **Due:** — | **Updated:** 2026-05-20
- **Assignees:** Niklavs Felsbergs, Łukasz Sendecki | **Watchers:** 3 | **Comments:** 1 | **Attachments:** none
- **URL:** https://app.clickup.com/t/869d9x5mz
- **State summary:** Done. Hunt for hidden Pentaho business logic in `factshipmentcosts → orders`. Found FedEx tracking rewrite missing in new pipeline → spawned NGE-7093. Date-window audit: current 30/60d forward vs legacy 120d ABS rule patterns: Pattern A (legacy never matches because `invoice_date` >120d from `order_created_date`: DPD, landmark_parcels/taxes, db_schenker — 93-99% only_current). Pattern B (both null: dhl_orwo 59-69%, ups_orwo 23%, fedex 17-31% — trackingnumber missing from msk — NGE-7093 PCS bridge addresses). Pattern C (DHL Q4-2024 reused trackings, 3,797 different_match in 2024, 3 in 2025+, 0 in 2026-Q1 — current rule correct). Pattern D (current ≈ legacy, 0.01-0.4% loss across UPS/yodel/gls/colis_prive/apg/asendia_usa/dhl_america/ontrac/dpd_uk/maersk/direct_link/dpd_poland_*).
- **V1-relevance:** `V1-followup` (work shipped, learnings flow into other tickets).

---

## NGE-7117 — Compare final shipping cost between fact_shipments and dw.sales_fact per month

- **Status:** to do | **Priority:** high | **Due:** — | **Updated:** 2026-05-18
- **Assignees:** Niklavs Felsbergs, Satya Varma Rudraraju | **Watchers:** 3 | **Comments:** 0 | **Attachments:** none
- **URL:** https://app.clickup.com/t/869d9x8dn
- **State summary:** Not started. Verify mart `final_shipping_cost_eur` matches `dw.sales_fact` per month before migrating reporting layers.
- **Awaiting Niklavs:** ticket assignment / kickoff.
- **V1-relevance:** `V1-blocking` (consumer-side validation; downstream reports depend on this).

---

## NGE-7097 — Comparison of fact_shipments and orders gold layer

- **Status:** in progress | **Priority:** high | **Due:** — | **Updated:** 2026-05-20
- **Assignees:** Niklavs Felsbergs, Satya Varma Rudraraju | **Watchers:** 4 | **Comments:** 3 | **Attachments:** `REPORT_NGE-7097.html` (2026-05-18 by Satya, URL: https://t9012440763.p.clickup-attachments.com/t9012440763/45653364-2a7e-4b31-8a5b-aa248d0eef99/REPORT_NGE-7097.html — self-contained sticky-nav HTML). May have a canonical copy in repo; D2 should check `bi-etl/dags/enterprise_silver/Shipping_Data_Mart/`.
- **URL:** https://app.clickup.com/t/869d9x5ny
- **State summary:** Order count + revenue parity vs `ol_gold.fact_order` (window 2024-01-01 → 2025-05-22, reorders excluded). 2026-05-18 baseline gap €7,232K. 2026-05-20 5 commits in `fact_shipment_orderitems` shipped 5 fixes — gap collapsed to €603K residual (−92%): (a) `pict_no_tni_pairs` fallback for external producers VR Print/Allcop/LaserTryk/PrintAndLogistics/MerchRocket/Elanders (+€937K rescued, commit `9ba83845`); (b) Rewallution fan-out fix (pre-divide by `msk parcel_count`, `14006196`) (−€108K over-count); (c) **PicaAPI revenue = product + shipping** (T-34 decision, mirrors `silver.revenues`, commit `43e35149`) (+€6.06M); (d) `pcs_parcel_reorder_flags: BOOL_OR → BOOL_AND` for mixed original+R parcels customer-paid (`eff462a2`) (+€165K); (e) Picturator REPLACEMENT exception for 8 shops (MFDE, BCNL, MXXLDE, CDUS, COS, BCCA, MONO, MPUK — Niklavs decision, `dc9dd058`) (+€57K); plus hotfix `c450d24f` (anti-join lookups → TEMP tables to bypass Redshift `queryVoltDecorrCSQ`). PicaAPI MATCH 0.27% → 89%; Picturator 99.34% → 98%; Rewallution 94% → 97%. Extended-window 2024-01-01 → 2026-04-30: PCS 0/27,925 (gold has 0 PCS), PicaAPI Δ +347,581, Picturator Δ +2,505,893, Rewallution Δ −29,309.
- **Open / blocked:** PicaAPI €286K residual (status whitelist edges, shopwise rates); Picturator €343K residual (per-shipment allocation drift in `pict_no_tni_pairs` — equal split vs gold per-item); Rewallution €29K residual (R9: extreme outliers with secondary inflation). PicaAPI ORDER_ONLY 2,008 = 1,820 `is_reorder` disagreement + 188 dropped via excluded extkey filter. PCS structurally unevaluable under `is_reorder=FALSE` (all PCS in `fact_order` are reorders).
- **Awaiting Niklavs:** Whether `fact_shipments` should apply PicaAPI status whitelist (would drop 49,908 SHIP_ONLY); `is_reorder` flag-disagreement root-cause direction; top-20 PicaAPI REVENUE_DIFF outliers triage.
- **V1-relevance:** `V1-blocking` (revenue parity is V1 acceptance criterion).

---

## NGE-6494 — Refactor column types in bronze layer

- **Status:** to do | **Priority:** low | **Updated:** 2026-05-14 | **Assignees:** Grzegorz Strawa | **Comments:** 0
- **URL:** https://app.clickup.com/t/869d2wkxj
- **State summary:** Dates as strings, numbers as text — needs casting. Not started.
- **V1-relevance:** `V1-followup` (quality-of-life; doesn't block V1).

---

## NGE-6755 — Fixes (bucket ticket for ad-hoc fixes)

- **Status:** in progress | **Priority:** high | **Due:** 2026-05-15 | **Updated:** 2026-05-19 | **Assignees:** Grzegorz Strawa | **Watchers:** 4 | **Comments:** 9
- **URL:** https://app.clickup.com/t/869d6je1r
- **State summary:** Rolling bug-fix log. 2026-05-19: Niklavs-reported tracking `LT1004192348` Maersk drift €13 (legacy) vs €11.94 (silver `maersk_invoices.unit_invoiced`) — diagnosed; 2026-05-18 `poc_staging.dpd_poland_invoices_firststructure` latest invoice = 2026-03-31 but newer invoices received and not picked up; `poc_staging.ups_orwo` latest also stuck — pipeline lag detected. 2026-05-14 Łukasz added `ShortCircuitOperator phase_0_window_gate` to `silver_shipping_data_mart_orchestrator.py` — Phase 0a (bronze) + Phase 0b (silver intermediates) only run 03:00-04:59 UTC; outside the window skipped. 2026-05-14 `map_shipment_key`: POST_DVF + other trackingless providers (~187K) land on spine with `trackingnumber='untracked'` (mirrors NGE-7100). 2026-05-12 USPS silver layer — `final_postage_usd = op.usps_calculated_total_postage − COALESCE(ca.pickup_charge, 0)` (was `COALESCE(pn.total_postage, op.usps_calculated_total_postage)`). 2026-05-11 FedEx two-feed root cause analysis (10% `base_rate_eur` NULL pre-July 2024 — bronze coverage gap). 2026-05-07 Picturator end-of-2024 cost NULL spike analysis (`fedex.sql` + `dhl.sql` two distinct root causes; duplicate-trackingnumber confirmed). 2026-05-06 DPD UK invoice ingestion stuck on 2026-04-05 — fixed via Docker image rebuild + manual DAG re-trigger. 2026-05-06 `avg_shipping_cost_eur` DQ followup — root cause analysis (~10% NULL across all sources).
- **Awaiting Niklavs:** none currently directly; team carries bugs through and asks when stuck.
- **V1-relevance:** `V1-blocking` (rolling bug fixes — V1 readiness depends on closing items here).

---

## NGE-7093 — Investigate why we have no recent costs for FXESPPS (FedEx SmartPost)

- **Status:** production | **Priority:** urgent | **Updated:** 2026-05-15 | **Assignees:** Niklavs Felsbergs, Grzegorz Strawa, Łukasz Sendecki | **Comments:** 2
- **URL:** https://app.clickup.com/t/869d9x4gu
- **State summary:** Done. 2026-05-15: SmartPost FXESPPS rows collapsed from ~50K/month (Jan-Jul 2025) → 132 in Sep 2025 → near-zero. Root: ~2026-08 Picanova switched to recording 20-digit USPS PIC (e.g. `61292013562327291271`) instead of FedEx tracking. Ticket's original fallback `COALESCE(crossreftrackingid_prefix, crossreftrackingid)` recovered 0 rows — prefix is constant 8-digit MID `61290126`. Correct fix: **CONCAT** `crossreftrackingid_prefix || crossreftrackingid` — match rate jumps 0% → 99%. Added secondary `LEFT JOIN map_shipment_key msk_fallback ON msk_fallback.trackingnumber = fl.crossreftrackingid_prefix || fl.crossreftrackingid` triggered only when primary misses. Per Niklavs's review: `fact_shipment_invoice_lines.trackingnumber` now sourced from MSK (`COALESCE(msk_trackingnumber, express_or_ground_tracking_id)`) so it matches `fact_shipments.trackingnumber` per `shipment_id` (53,239 match / 0 mismatch). Hotfix in same commit: removed duplicate `WITH` from PR #1291 bad merge (would have errored DAG at 05:00 UTC). Łukasz also added PCS bridge (NGE-7096 thread) for 12-digit non-39/27 FedEx trackings — rescues 99.15% of unmatched FedEx rows. **Next: "Something weird at the end of 2024, missing costs at the end of 2024" — NGE-6755 hotfix territory.**
- **V1-relevance:** `V1-followup` (shipped, but the EoY-2024 follow-up is V1-blocking detail; tracked in NGE-6755).

---

## NGE-7100 — Ensure POST_DVF shipments have shippingprovider_extkey + trackingnumber='untracked'

- **Status:** production | **Priority:** normal | **Due:** 2026-05-15 | **Updated:** 2026-05-15 | **Assignees:** Niklavs Felsbergs, Grzegorz Strawa | **Comments:** 1
- **URL:** https://app.clickup.com/t/869d9x5tp
- **State summary:** Done. PICT branch `pict_keys` CTE now COALESCEs to `'untracked'` when `shippingprovider IS NOT NULL`. 166,828 POST_DVF shipments end-to-end through `map_shipment_key` and `fact_shipments`. `fact_shipments/sql/insert_to_silver.sql` WHERE-clause confirmed not filtering `'untracked'` (drops only `DUMMY`/`CANCEL`/`STORNO`/`SUPPORT`/`XXX`/`Quality Check`). Follow-up: POST_DVF also in ORWO (~1M rows) — same `'untracked'` pattern reusable when ORWO branch lands.
- **V1-relevance:** `V1-followup` (shipped).

---

## NGE-7102 — Implement ORPS data

- **Status:** to do | **Priority:** low | **Updated:** 2026-05-14 | **Assignees:** Niklavs Felsbergs, Davis Lozda | **Comments:** 0
- **URL:** https://app.clickup.com/t/869d9x5w0
- **State summary:** Forward-looking. New shipping platform rolling out, mart must be ready before rollout so no data gap. Not started.
- **V1-relevance:** `out-of-scope` (post-V1; readiness for next platform).

---

## NGE-7104 — Migrate the data mart to the gold layer

- **Status:** to do | **Priority:** high | **Updated:** 2026-05-14 | **Assignees:** Niklavs Felsbergs, Satya Varma Rudraraju | **Comments:** 0
- **URL:** https://app.clickup.com/t/869d9x5z6
- **State summary:** Forward-looking. Target schema name agreed: `shipping_mart`. Migrate all tables to gold except `dim_trucks`, `dim_shipping_providers`, `map_shipment_key`. Stakeholder access scope.
- **V1-relevance:** `V1-followup` (gold layer is the V1 endpoint per epic design `shipping_gold (provisional)`; this is the ship gate).

---

## NGE-7108 — Develop a semantic layer for the data mart

- **Status:** to do | **Priority:** high | **Updated:** 2026-05-14 | **Assignees:** Niklavs Felsbergs | **Comments:** 0
- **URL:** https://app.clickup.com/t/869d9x60r
- **State summary:** Forward-looking. Need a set of `.md` files instructing AI exactly how to use the mart.
- **V1-relevance:** `V1-followup` (consumer-side; V1 mart can ship without semantic docs but enablement suffers).

---

## NGE-7109 — Ensure UPS refunds are allocated to orders once new shipment_id logic is implemented

- **Status:** staging | **Priority:** normal | **Updated:** 2026-05-20 | **Assignees:** Niklavs Felsbergs, Łukasz Sendecki | **Comments:** 0
- **URL:** https://app.clickup.com/t/869d9x64j
- **State summary:** Verify UPS refunds attach via `shipment_date` 60-day lookback after new `shipment_id` assignment logic lands. No comments yet — has moved to staging.
- **V1-relevance:** `V1-followup`.

---

## NGE-7105 — Ensure cost_source in fact_shipments only has avg, expected, invoice, NULL

- **Status:** release (closed 2026-05-20) | **Priority:** low | **Updated:** 2026-05-20 | **Assignees:** Niklavs Felsbergs, Grzegorz Strawa | **Comments:** 0
- **URL:** https://app.clickup.com/t/869d9x63b
- **State summary:** Done. DHL Dec-2024 €237k `invoice_estimate` workaround relabelled to `invoice`.
- **V1-relevance:** `out-of-scope` (closed).

---

## NGE-7110 — fact_shipments has 1588 duplicate shipment_ids

- **Status:** staging | **Priority:** high | **Updated:** 2026-05-14 | **Assignees:** Niklavs Felsbergs, Łukasz Sendecki | **Comments:** 1
- **URL:** https://app.clickup.com/t/869d9x61y
- **State summary:** 2026-05-15 root cause: `pcs_sentparcels` multiple rows per trackingnumber (re-scans/re-sends), `shop_ordernumber` matches multiple `pcs_orders` after `_N` strip → fanned out fact_shipments 1:N (1,588 distinct ids, up to 20 copies, 3,688 rows, 99% PicaAPI, 1% PCS, span 2023-04 to 2026-05). Spine clean — fan-out during fact build. Fix: wrapped `tmp_pcs_data` (a)+(b) and `tmp_pcs_production_site_for_temp` in `ROW_NUMBER() PARTITION BY shipment_id` dedup. Verified no analogous bug elsewhere. `fact_shipment_invoice_lines` apparent dups (~12M on weak key) are legitimate multi-VAT lines (FedEx 100 excess/2.2M; DHL/UPS shrinks with `charge_amount_eur` in key).
- **V1-relevance:** `V1-blocking` until staging closes.

---

## NGE-7106 — Logic check for truckloads, loadingunits, allocated_truckloads

- **Status:** to do | **Priority:** low | **Updated:** 2026-05-14 | **Assignees:** Niklavs Felsbergs | **Comments:** 0
- **URL:** https://app.clickup.com/t/869d9x656
- **State summary:** Self-audit ticket on truck/loading-unit logic in `fact_shipments`. Not started.
- **V1-relevance:** `unclear` (could be V1-blocking validation; low priority + Niklavs-owned suggests post-V1).

---

## NGE-7107 — Define ORWO truck consignment cost logic

- **Status:** to do | **Priority:** low | **Updated:** 2026-05-14 | **Assignees:** Niklavs Felsbergs | **Comments:** 0
- **URL:** https://app.clickup.com/t/869d9x65j
- **State summary:** Define how to find shipments where ORWO→SZZ consignment cost applies (orders jointly produced Wolfen+SZZ ship ORWO→SZZ first). Mentioned in NGE-6126 truck-charges thread as ORWO Consignment was removed from `dim_truck_costs` pending Niklavs decision.
- **V1-relevance:** `V1-followup` (since the consignment line is removed from active allocation, mart works without it but truck-cost completeness suffers).

---

## NGE-7111 — Define returned shipments

- **Status:** to do | **Priority:** low | **Updated:** 2026-05-20 | **Assignees:** Niklavs Felsbergs, Grzegorz Strawa | **Comments:** 0
- **URL:** https://app.clickup.com/t/869d9x660
- **State summary:** Define source for `is_returned` data point (likely invoices where available). Not started.
- **V1-relevance:** `V1-followup` (mart has `is_returned` column per design; logic not wired).

---

## NGE-7112 — Define packagetype group

- **Status:** to do | **Priority:** low | **Updated:** 2026-05-14 | **Assignees:** Niklavs Felsbergs | **Comments:** 0
- **URL:** https://app.clickup.com/t/869d9x66f
- **State summary:** Define grouping rule for cryptic packagetype codes. Not started.
- **V1-relevance:** `V1-followup` (analytical convenience).

---

## NGE-7114 — Define and implement archived date

- **Status:** production | **Priority:** normal | **Updated:** 2026-05-20 | **Assignees:** Niklavs Felsbergs, Justus Kaiser, Davis Lozda, Łukasz Sendecki | **Comments:** 0
- **URL:** https://app.clickup.com/t/869d9x67n
- **State summary:** Done. Archived date added to `fact_shipments`. No comments.
- **V1-relevance:** `V1-followup` (done).

---

## NGE-7115 — fact_shipment_invoice_lines.invoice_source should contain exact source table name

- **Status:** to do | **Priority:** low | **Updated:** 2026-05-14 | **Assignees:** Niklavs Felsbergs, Grzegorz Strawa | **Comments:** 0
- **URL:** https://app.clickup.com/t/869d9x697
- **State summary:** Rename `invoice_source` values to be exact source table (e.g. `enterprise_silver.fedex_invoices`) for AI-traceability. Not started.
- **V1-relevance:** `V1-followup`.

---

## NGE-7116 — Change shippingprovider to shippingprovider_extkey in fact_shipment_invoice_lines

- **Status:** release (closed 2026-05-20) | **Priority:** low | **Updated:** 2026-05-20 | **Assignees:** Niklavs Felsbergs, Łukasz Sendecki | **Comments:** 0
- **URL:** https://app.clickup.com/t/869d9x6az
- **State summary:** Done. Mart-wide consistency rename.
- **V1-relevance:** `out-of-scope` (closed).

---

## NGE-7125 — Billed weight logic in invoice lines

- **Status:** production | **Priority:** low | **Updated:** 2026-05-20 | **Assignees:** Niklavs Felsbergs, Grzegorz Strawa | **Comments:** 0
- **URL:** https://app.clickup.com/t/869d9xgp4
- **State summary:** Done. If billed_weight missing/0 in invoice source, NULL in invoice lines (fixes avg-weight analysis).
- **V1-relevance:** `V1-followup` (done).

---

## NGE-7142 — Alerts & DQ Checks

- **Status:** to do | **Priority:** normal | **Updated:** 2026-05-14 | **Assignees:** Davis Lozda | **Comments:** 0
- **URL:** https://app.clickup.com/t/869d9xn5e
- **State summary:** Catch-all for alerting/DQ. Not started.
- **V1-relevance:** `V1-blocking` (V1 mart should not ship without DQ checks at minimum; Davis is owner).

---

## NGE-7146 — Refactor shipment event timestamps and transit times

- **Status:** staging | **Priority:** high | **Updated:** 2026-05-14 | **Assignees:** Niklavs Felsbergs, Łukasz Sendecki | **Comments:** 1
- **URL:** https://app.clickup.com/t/869d9yfx2
- **State summary:** Done (in staging). 2026-05-15: renamed `sl_shipped_ts/date → received_by_carrier_ts/date`; `sl_delivered_ts/date → delivered_by_carrier_ts/date`. Added 3 new lifecycle timestamps: `production_order_created_ts` (`pcs_orders.created`), `truckload_assigned_ts` (`pcs_truckloads.created`), `truckload_closed_ts` (`pcs_truckloads.closedtimestamp`). Added `PICKED_UP` to received-by-carrier event filter. **This is the commit (`7e552464f` per NGE-6129's 2026-05-21 comment) that incidentally fixed ORWO's cross-source event-stream pollution bug #3.**
- **V1-relevance:** `V1-followup`.

---

## NGE-7269 — Add archived date to fact_shipments

- **Status:** to do | **Priority:** normal | **Updated:** 2026-05-19 | **Assignees:** none | **Comments:** 0
- **URL:** https://app.clickup.com/t/869dc0j59
- **State summary:** Likely a duplicate of NGE-7114 (which is `production`). New ticket created 2026-05-19. No description, no assignees.
- **V1-relevance:** `unclear` (probably duplicate — flag for Niklavs to triage).

---

## NGE-7273 — implement ORWO expected shipping cost

- **Status:** to do | **Priority:** — | **Updated:** 2026-05-19 | **Assignees:** Niklavs Felsbergs | **Comments:** 0
- **URL:** https://app.clickup.com/t/869dc1zkb
- **State summary:** Port `asa.sp_expected_shipping_costs_orderitems` procedure logic to ORWO source. Matches NGE-6129 follow-up ⑤ (blocked by ④ Navision destination_country lookup).
- **Awaiting Niklavs:** ownership / kickoff.
- **V1-relevance:** `V1-followup` (ORWO is V1-required but the expected-cost branch is an enrichment).

---

## NGE-7282 — Implement Sendmoments data

- **Status:** to do | **Priority:** low | **Updated:** 2026-05-20 | **Assignees:** Davis Lozda | **Comments:** 0
- **URL:** https://app.clickup.com/t/869dcavz4
- **State summary:** New ticket. Mentioned in NGE-7097 pending follow-ups: "Sendmoments integration into `fact_shipments`, then re-run comparison with ORWO/Sendmoments added to scope."
- **V1-relevance:** `unclear` (depends on whether Sendmoments is V1 source — principal said only PICT/PicaAPI/PCS/Rewallution/ORWO so likely post-V1).

---

## Action items assigned to Niklavs across the tree

Direct Niklavs assignments with action-shape (not just watcher/co-owner):

1. **NGE-6128 Dim Carrier SLA** — Build the SharePoint export and stand up the table. **V1-blocking. No movement.**
2. **NGE-6127 Dim Shipping Providers** — Classify 30 NULL ORWO carrier extkeys (`shippingprovider_group` / `service_type` / `truck_provider` / `has_truck_cost`). List: CIRRO, CPRHD, DBSCHENKER, DHL, DHL2, DHLKP, DHLX2, DPD, FKBRING, FKBRINGPARCEL, GUELL, MAERSKFR, POST, POSTAT, POSTAT_FR/_GB/_L/_P, POSTNL_AVG/_EU/_MB, POST_DVF, TD, UNITEDPRINT, UPS, UPSEXPRESS, UPSWEA, UPSWWE, WPOST3, WPOST4. **V1-blocking.** (Tracked in NGE-6129 #1 too.)
3. **NGE-6126 Fact Truck Charges** — Refine `dim_truck_costs.truck_database_identifier` patterns: DHL Kleinpaket `%DHL%W%` overinclusive (overstated cost), Colis Prive too narrow (understated), define ORWO Consignment SZZ↔ORWO split rule, confirm DHL Kleinpaket country scope (currently DE only, legacy doesn't filter). **V1-blocking.**
4. **NGE-6123 Fact Shipment Orderitems** — Decide order-state filter scope (mirror `enterprise_silver/revenues` filters or stay wider with `testorder=FALSE`); decide missing-tracking fallback for ~1.27M PCS orders shadowed by shop-side `tracking_number IS NULL`. **V1-blocking.**
5. **NGE-7097 fact_shipments vs orders gold** — Decide on (a) whether `fact_shipments` should apply PicaAPI status whitelist (would drop 49,908 SHIP_ONLY), (b) `is_reorder` flag-disagreement direction (1,820 PicaAPI parcels), (c) triage top-20 PicaAPI REVENUE_DIFF outliers. **V1-blocking.**
6. **NGE-6428 vs source** — DB Schenker decision: 100% unclassified bucket awaiting new format from DBS. **V1-blocking.**
7. **NGE-6129 Integrate Orwo data** — Open follow-up ② dim_products extension (Data Platform), ④ destination_country Navision lookup (ENG), ⑤ ORWO expected shipping cost (NGE-7273) — Niklavs to confirm sequencing.
8. **NGE-7117 fact_shipments vs dw.sales_fact per month** — Kick off. **V1-blocking; not started.**
9. **NGE-7104 Migrate to gold layer** — Owner; the V1 endpoint (target schema `shipping_mart`).
10. **NGE-7108 Semantic layer** — Owner; ship `.md` files. **V1-followup.**
11. **NGE-7102 ORPS** — Owner; post-V1 readiness.
12. **NGE-7273 ORWO expected shipping cost** — Owner.
13. **NGE-7106 / NGE-7107 / NGE-7111 / NGE-7112** — Owner; low-priority self-research items.
14. **NGE-7115** — Owner with Grzegorz; cosmetic `invoice_source` rename.

## Cross-cutting flags worth surfacing

- **HTML attachment pattern confirmed.** Engineers (Satya, Łukasz) attach `.html` reports to comments AND commit canonical copies into `bi-etl/dags/enterprise_silver/Shipping_Data_Mart/`. NGE-6120 (`data_model.html`), NGE-6129 (`orwo_open_pointers.html` — canonical at `dags/enterprise_silver/Shipping_Data_Mart/orwo_open_pointers.html` commit `9af27d823`; ticket attachment `f4dfed68-…` is stale per Satya 2026-05-21), NGE-7097 (`REPORT_NGE-7097.html` — D2 should verify if a canonical copy exists in repo).
- **Tickets `release` and effectively closed:** NGE-7105, NGE-7116. They show as direct children of the epic but no longer move.
- **Possible duplicate:** NGE-7269 vs NGE-7114 — both are "add archived date to fact_shipments"; NGE-7114 is `production`, NGE-7269 was newly created 2026-05-19 with no assignees / no description. Flag for triage.
- **`fact_shipment_invoice_lines` apparent dups (~12M)** were investigated under NGE-7110 — legitimate multi-VAT lines, NOT a bug.
- **Phase-window gating** (NGE-6755 2026-05-14): Phase 0a (bronze) + Phase 0b (silver intermediates) only run 03:00-04:59 UTC. Reruns outside that window skip these phases — relevant for D3 if redshift queries find stale silver/bronze.
- **Pipeline lag (NGE-6755 2026-05-18):** `poc_staging.dpd_poland_invoices_firststructure` and `poc_staging.ups_orwo` were stuck — Niklavs reported, fix unknown from comments alone. D2/D3 should check current pipeline freshness.
- **ORWO carrier classification (#1) is a chokepoint** — touches NGE-6127, NGE-6129, downstream of any analytics that depend on `shippingprovider_group`/`truck_provider`/`has_truck_cost` for ORWO traffic (2.49M shipments / 89.6M items).
- **NGE-6128 Dim Carrier SLA has 0 movement.** SLA-breach reporting is a V1 epic-design feature. Without this dim, the reporting view that computes `sla_breach_flag` and `days_vs_sla` cannot exist. Single biggest **V1-blocking** silent risk on the tree.
- **The 4 NGE-6129 open follow-ups (carrier classification, dim_products, destination_country, expected shipping cost)** all live in the open-pointers HTML — the canonical document for ORWO V1 gap. Principal-Jebrim should triage these against the synthesis as the most concentrated ORWO V1 surface.


