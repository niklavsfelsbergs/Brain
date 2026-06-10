# Production-times domain census — 2026-06-09

> Structured map of the **production-times / fulfillment-ops** surfaces as of 2026-06-09, built by a Jebrim-dwarf read-only recon (sid 91513c92). The **corpus anchor** for the [[production-times]] domain — Jebrim's throughput/timing pillar (distinct from shipping cost), which also owns **delivery-promise cutoffs** per Niklavs' scope statement.

## What the domain is
How long an order takes through the system — *speed and on-time*, not price. The order-to-delivery lifecycle **in time**: production lead time (core, PCS-side), carrier transit time / SLA, and delivery-promise-cutoff exposure. Primary unit **working days (wd)** for production, **business days (bd)** for transit. Same orders/carriers/sites as the cost domains, different question.

## Lifecycle stages (from fulfillment_dashboard + operations/22)
- **Queue:** `order_created` (sales_fact) → `pcs_created` (PCS order-created ts = production start).
- **Production:** `MIN(pcs_created)` → `MAX(shipped_at)` (last `SHIPPED` orderitemlog) — the PCS production time the 12/14/15/16/20/21/25 cluster measures.
- **Handoff:** `MAX(shipped_at)` → first carrier OUTBOUND scan.
- **Shipping/transit:** first OUTBOUND → last DELIVERED (topic-44 SLA stage).

## Metrics
- **Production** (per site×product×date in `order_flagging.pcs_production_times`): avg/median/min/max + **P85/P95**, in **wd (primary)**, fd (calendar), sd (scheduled, excluded as unreliable). All **volume-weighted**. Default target **3 wd** (`Flagging config.xlsx` → "Production Times Standard"; PL→"PCS PL" col, US→"PCS CMH" col).
- **Transit-time SLA** (topic 44): per carrier×dest-country×weight-bracket → p85/p90/p95 transit **bd**, delivered-coverage %, + 3-segment lead decomposition (seg1 produced→departure, seg2 departure→received, seg3 received→delivered). Artifact `dim_carrier_sla_v1.xlsx` + region/zone crosswalk. (Topic 44 is **data/evidence-only** — no code/md; purpose inferred from headers.)
- **Delivery-promise cutoff** (topic 40): a per-order **delivery-by deadline** set when an order is flagged for a dated campaign (e.g. Mother's Day). Source `order_flagging.order_delivery_promise_flags` (`flag_title`, `promise_cutoff`). MD_2026 tracked undelivered orders carrying the promise: how many still undelivered, where exposure sits (region/shoptype/shop/carrier), real vs DQ. Undelivered = `MAX(sl_delivered_ts) IS NULL`, sub-bucketed (delivered / shipped_no_deliver / in_mart_no_events / no_shipment_record). A `POST_CUTOFF_DATE` (2026-05-04) split the main promise from late campaign flags.

## Sites (display ← PCS internal ← productionsite id)
- **SZZ** = PCS PL = Szczecin (id 2) — primary EU, broadest portfolio (73 products).
- **CMH** = PCS CMH = Columbus (id 6) — current US, since Jul 2025, systematically slowest.
- **PHX** = PCS PX = Phoenix (id 3) — legacy US.
- **MIA** = PCS MI = Miami (id 1) — legacy US, **shut down Aug 2025**.
- US legacy (MI+PX) combined as the "US Legacy" baseline for CMH YoY. (Köln id 5 in the productionsites dim but out of PCS scope.)

## Data sources (Redshift, confirmed)
- `order_flagging.pcs_production_times` — **the anchor** for all PCS production-time work (grain: 1 row per production_site×product_mapping×calc_date).
- `order_flagging.order_delivery_promise_flags` — promise flags + `promise_cutoff` (topic 40).
- `dw.sales_fact` (order universe / shop-created ts; `data_source` = PicaAPI | Picturator), `dw.shipment_logs` (tracking events), `dw.{production_items_fact, dim_products, dim_shops, dim_options}`.
- `enterprise_silver.fact_shipments` (`sl_shipped_ts`, `sl_delivered_ts`, `shipping_provider_group` — topic 40).
- `poc_landing.{pcs_orderitemlogs, pcs_orders, pcs_sentparcels, pcs_productionsites}` / `enterprise_bronze.pcs_orderitems` (lifecycle source). Folder 22 uses older `bi_stage_dev_dbo.pcsu_*` — same PCS data, different layer; reconcile at next deepen.
- `fact_truck_charges` (`departure_ts` = truckload_closed; topic 40 borrows it for a timing field).

## Surfaces (the corpus)
**operations/ (PCS chain — progression):** `12_PCS_production_times` (earliest, PL weekly weighted-avg wd — superseded) · `14_..._cc` (3 sites — superseded) · `15_..._w_Miami` (4 sites + YoY — superseded) · `16_..._per_country` (superseded by 20) · **`20_..._per_country_v2`** (current static per-country report, overlap-weeks YoY fix) · **`21_..._monthly_report`** (standing monthly management report, `main_management.py`, PL YoY + CMH-vs-US-Legacy — live, skill-driven) · `22_picaapi_time_between_checkpoints` (one-off PicaAPI data-lag diagnostic; defines time-diff cols shop_to_pcs_h / pcs_to_production_h / production_to_carrier_h / carrier_to_delivered_h) · `25_..._monthly_presentation_interactive` (Streamlit — superseded by nextjs).
**dashboards/:** `pcs_production_times` (Streamlit — superseded) · **`pcs_production_times_nextjs`** (LIVE; Next.js 15 + DuckDB + AI commentary; Airflow `pcs_production_times_nextjs_dag` 7:30 AM Berlin Mon–Fri, S3 persistence) · `fulfillment_dashboard` (pipeline home; full lifecycle CTE) · **`fulfillment_dashboard_nextjs`** (LIVE; reads sibling parquets; phase decomposition per tab).
**.claude/skills/:** `reports:refresh-monthly-pcs-production-times-report` (6-phase, defaults `operations/21_*`, auto prev-completed-month) · `reports:refresh-pcs-dashboard` (4-phase pipeline→analyze→commentary, defaults `dashboards/pcs_production_times`).
**shipping_topics/:** `40_MD_2026` (promise-cutoff tracking, 8-sheet Excel, DQ separation + feed-freshness gate) · `44_transit_time_sla` (transit SLA evidence pack, data-only).
*Side cluster, NOT core:* `operations/{13_Lyto_late_orders, 31_lyto_data_gather, 32_lyto_us_export}` — Lyto (rejected as its own domain 2026-06-09).

## Standing deliverables
1. Monthly PCS production-time management report (folder 21, monthly via skill).
2. Live PCS production-times dashboard (nextjs, 7:30 AM Berlin Mon–Fri, AI commentary via company tcgpt gateway).
3. Live fulfillment dashboard (nextjs, end-to-end timing; no cron found).
4. Per-country static report (folder 20 v2, on demand).
5. Promise-cutoff campaign tracking (topic-40 pattern, on demand during a promise window).
6. Transit-SLA reference (`dim_carrier_sla_v1.xlsx`, one-off, no cadence found).

## Flags / open
- Folder 22's `bi_stage_dev_dbo.pcsu_*` vs the dashboards' `poc_landing.pcs_*`/`enterprise_bronze` — reconcile the canonical PCS lifecycle source at next deepen.
- Topic 44 purpose/grain is **inferred** (no author doc).
- AI-commentary confirmed for the PCS nextjs dashboard only.

## Provenance
Read-only dwarf recon. Anchor for the [[production-times]] digest. Niklavs flagged he'll build on this domain (incl. delivery-promise cutoffs) — expect the corpus to grow.
