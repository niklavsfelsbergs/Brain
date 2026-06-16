# OnTrac oversize "Feb onset" in SCM — verdict: dashboard classification gap (cause #2)

**Spawned by:** Jebrim, shipping-agent sub-agent. Investigation for the SCM dashboard.
**Date:** 2026-06-15
**Tier:** gold shipping_mart + (off-contract, per brief grant) enterprise_silver.shipping_charge_bucket_mapping, enterprise_bronze.ontrac source_table check.

## Ask
SCM shows OnTrac oversize/overweight bucket flat EUR0.00 avg/shipment Jun 2025–Jan 2026, then onset Feb 2026 (1.29→1.80→1.38→1.51→1.02 avg per shipment). Pre-Feb coverage 98–99%. Resolve: (1) real surcharge onset / (2) bucket-mapping change / (3) coverage artifact.

## Status trace
- OnTrac identity pinned: shipping_provider_group='ONTRAC', extkey='ONTRAC', invoice_source='ontrac'. Spans B2C 203K + MerchOne 78K + 263 internal print. Volume exists every month (ramps from 8 in Jun25 to 59K Dec peak, settles ~20-29K/mo 2026). Pre-Feb EUR0.00 is NOT zero volume.
- Gold trend (order-month, invoiced basis): oversize present EVERY month — 2.19(Jul) ... 7.85(Oct) ... 2.47(Dec) 2.08(Jan) 1.28(Feb) 1.80(Mar) 1.38(Apr) 1.51(May) 1.02(Jun). avg-over-INVOICED basis reproduces dashboard 1.29/1.80/1.38/1.51/1.02 exactly. KILLS the dashboard's EUR0.00-pre-Feb against gold.
- Invoice-line detail by invoice_date: oversize lines flow every month from Jul25 (737 lines/EUR8.3K) to Dec (EUR152K). Rules out cause #3 (ingestion). Raw never absent.
- Charge-descriptions by month (pull c, decisive): "Additional Handling Surcharge", "Over Maximum Limits Surcharge", "Large Package Surcharge" + Demand variants present every month Nov25→Jun26, all bucket=oversize_overweight, source_table=enterprise_bronze.ontrac. Same strings pre-Feb AND post-Feb — NOT first-appearing in Feb. (Demand* variants lapse after Jan — holiday peak surcharge, a reduction not an onset.)
- Re-bucketing test (pull d): total cost/invoiced shipment across Jan→Feb FALLS (9.45→8.54); oversize also falls (2.08→1.28). No step-up, no other bucket absorbing it. No re-bucketing in gold, no additive new cost.
- Off-contract silver check: shipping_charge_bucket_mapping has ONE dw_timestamp for all OnTrac rows (full reload 2026-04-23) — no version history, cannot date a historical mapping change. All 6 oversize descs route to oversize today.

## Verdict
Cause #2 — bucket-mapping / classification, located in the SCM DASHBOARD's own pipeline, NOT the gold mart. Gold has always classified these correctly across all months; dashboard's EUR0.00-pre-Feb is not reproducible from gold on any date axis. It's a dashboard-classification story, NOT a cost story — OnTrac did not start billing oversize in Feb; the charge has been ~EUR1-8/shipment since mid-2025.

## Caveats
- Cannot prove the dashboard-side mapping change directly from the mart (dashboard pipeline is out of mart reach; silver mapping has no version history). Confirm on the SCM/dashboard build side: when did its OnTrac oversize classification go live (~Feb 2026 commit/config).
- Jun 2026 partial (235 invoiced of 12,696 — invoice lag).
- Basis that reproduces dashboard = avg per INVOICED shipment (not avg-over-all).

## Deliverable
Chart: shipping-agent/workbench/investigations/ontrac-oversize-feb-onset/outputs/20260615-130955--ontrac-oversize-charge-per-shipment-present-every-month-in-the-source-data.html
SQL: .../sql/20260615-01_ontrac_oversize_trend.sql
