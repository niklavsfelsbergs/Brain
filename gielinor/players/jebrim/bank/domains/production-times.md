---
domain: production-times
title: Production times & fulfillment timing — throughput pillar (+ delivery-promise cutoffs)
patterns:
  - production time
  - production times
  - pcs production
  - fulfillment
  - delivery promise
  - promise cutoff
  - transit time
  - transit sla
  - lead time
  - pcs
corpus:
  - bank/notes/projects/2026-06-09-production-times-domain-census.md
specialist: null
freshness: 2026-06-09
synthesized: 2026-06-09
---

# Production times & fulfillment timing

Jebrim's **throughput / timing pillar** — how long an order takes through the system, *not* what it costs (same orders/carriers/sites as the shipping-cost domains, different question: **speed and on-time**). Niklavs will build on this; it **also owns delivery-promise cutoffs**. Full map: [[2026-06-09-production-times-domain-census]].

## Lifecycle stages (order → delivery, in time)
- **Queue:** `order_created` (sales_fact) → `pcs_created` (production start).
- **Production:** `MIN(pcs_created)` → `MAX(shipped_at)` — *the PCS production time the whole operations/ cluster measures*.
- **Handoff:** last `SHIPPED` → first carrier OUTBOUND scan.
- **Transit:** first OUTBOUND → last DELIVERED (the transit-SLA stage).

## Metrics
- Production in **working days (wd)** (primary; also fd calendar, sd scheduled=unreliable/excluded), per (site × product × date) in `order_flagging.pcs_production_times`: avg/median/min/max + **P85/P95**, all **volume-weighted**. Default target **3 wd** (`Flagging config.xlsx` → "Production Times Standard"; PL→"PCS PL", US→"PCS CMH").
- Transit in **business days (bd)**: per carrier × dest-country × weight-bracket → p85/p90/p95 + delivered-coverage % + 3-segment lead-time decomposition (produced→departure→received→delivered). Artifact `dim_carrier_sla_v1.xlsx`.
- **Delivery-promise cutoff** = a per-order **delivery-by deadline** attached when an order is flagged for a dated campaign. Source `order_flagging.order_delivery_promise_flags` (`flag_title`, `promise_cutoff`). Tracked as undelivered-exposure (`MAX(sl_delivered_ts) IS NULL`), DQ-separated.

## Sites (display ← PCS internal ← productionsite id)
- **SZZ** = PCS PL = Szczecin (id 2) — primary EU, broadest portfolio.
- **CMH** = PCS CMH = Columbus (id 6) — current US, since Jul 2025, systematically slowest.
- **PHX** = PCS PX = Phoenix (id 3) + **MIA** = PCS MI = Miami (id 1, **shut down Aug 2025**) — US legacy, combined as the CMH-YoY baseline. (Köln id 5 in the dim but out of PCS scope.)

## Data sources (Redshift)
`order_flagging.pcs_production_times` (**the anchor**) · `order_flagging.order_delivery_promise_flags` (promises) · `dw.sales_fact` · `dw.shipment_logs` · `dw.{production_items_fact,dim_products,dim_shops,dim_options}` · `enterprise_silver.fact_shipments` (`sl_shipped_ts`/`sl_delivered_ts`) · `poc_landing.pcs_*` / `enterprise_bronze.pcs_orderitems` (lifecycle source). Folder 22 uses older `bi_stage_dev_dbo.pcsu_*` — same PCS data, reconcile layer at next deepen.

## Surfaces (the corpus) + standing deliverables
- **LIVE PCS dashboard** — `dashboards/pcs_production_times_nextjs` (Next.js+DuckDB+AI commentary; Airflow `pcs_production_times_nextjs_dag` **7:30 AM Berlin Mon–Fri**). Streamlit `pcs_production_times` superseded.
- **Monthly PCS management report** — `operations/21_PCS_production_time_monthly_report` (PL YoY + CMH-vs-US-Legacy), refreshed by the `reports:refresh-monthly-pcs-production-times-report` skill (prev completed month).
- **LIVE fulfillment dashboard** — `dashboards/fulfillment_dashboard(_nextjs)` (end-to-end lifecycle decomposition).
- **Per-country static report** — `operations/20_..._per_country_v2` (current; 12/14/15/16 superseded; 25_ Streamlit superseded).
- **Promise-cutoff tracking** (seasonal/ad-hoc) — `shipping_topics/40_MD_2026` (the cutoff pattern). **Transit SLA** evidence — `shipping_topics/44_transit_time_sla` (data-only; purpose inferred from headers).
- `refresh-pcs-dashboard` skill drives the dashboard pipeline+commentary.

*Side cluster, NOT core:* `operations/{13_Lyto_late_orders,31_lyto_data_gather,32_lyto_us_export}` (Lyto — separate, rejected as its own domain 2026-06-09).
