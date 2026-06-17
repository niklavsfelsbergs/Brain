---
quest: S250_us-lucanet-vs-bi-reconciliation
sid8: 44773956
ts: 2026-06-17 10:35
open_dep: none
---
Status: in-progress

Where we are: US LucaNet-vs-BI reconciliation complete for cost/revenue/quota 2026 YTD (Jan–May). `findings.md` written and is canonical. Cost ties ~2%; revenue: BI mart ≈ ol_gold within ~1%/month, February −10% is LucaNet-side; quota BI 26.3% vs LucaNet 25.1%. QuickBooks explored — AP/cost-only, 2026 unbooked (LucaNet = accruals); QB connection saved to NFE/.env.

Next concrete step: pick up from findings.md "Open items / next steps" —
1. Validate the BI↔QB cost method on **2025** (QB fully booked): reconcile mart shipping cost vs QB `Fulfillment & Outbound Shipping:*` accounts. If it ties, the BI↔GL bridge is proven for when 2026 bills land.
2. Confirm with accounting how LucaNet **accrues** current-year shipping (QB bills not entered) — likely explains the cost ~2% and the February residual.
3. Chase the February revenue ~10% gap in `ol_gold` — test order-created vs delivery/invoice-date recognition; check deferred revenue + non-US/CA shipping_country US-entity orders.

Files to read first:
- `bi-analytics-main/NFE/shipping_topics/48_US_Lucanet_vs_BI/findings.md` (canonical — full numbers, schema map, queries)
- `US_LucaNet_vs_BI_2026YTD_comparison_v2.xlsx` + `build_comparison.py`
- QB connection: `bi-analytics-main/NFE/.env` (`QB_HOST/QB_PORT/QB_DATABASE/QB_USER/QB_PASSWORD`)

Pending drafts: none.
