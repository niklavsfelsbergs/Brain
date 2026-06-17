# Shipping-agent pull: 2026 all-sites monthly shipping-cost quota (Picturator+PicaAPI)

**Spawned by:** Jebrim (principal) | **Agent:** shipping-agent (mart specialist, emulated)
**Scope:** order source Picturator+PicaAPI, ALL production sites (NULL site excluded), order-month lens. Off gold contract: no dw.sales_fact reached — brief's `archivedtime`/`shipment_date` resolved to mart columns instead. All work stayed inside `shipping_mart.*`.

## Ask
Build the all-sites 2026 monthly quota. Prior run stalled on a soft revenue gate — ignore it; use ONE revenue construction self-validated against the HARD anchor (excluded-sites Jan 2026 = EUR 7,152,452).

## Turn log
- Loaded how_to.md (full) + mart-contract.md. No CLAUDE.local.md present; brief is the principal scope override for the off-contract reach.
- STEP 1 grain test: anchor reproduced EXACTLY (EUR 7,152,452) with **Grain A = SUM(net_revenue_eur) across shipment rows**, order-month = DATE_TRUNC('month', shop_order_created_date), production_site NULL excluded. Grain B (one-row-per-order) undershot at 7,030,422 -> ruled out.
- STEP 2 all-sites Jan revenue (same construction, no site filter, NULL excluded) = EUR 10,819,044 (~10.9M, in band).
- STEP 3 cost numerator = hybrid: invoiced-cost shipments -> invoice-line charge_amount_eur ex tax+customs by shipment_date; else expected_shipping_cost_eur by COALESCE(order_produced_date, shop_order_created_date) [archivedtime analog; coalesce avoids the ~14% produced-date NULL gap].
- STEP 4 excluded-sites quota reproduced 21.2/18.7/15.7 vs prior 20.9/18.5/15.5 (within ~0.3pt; drift = invoices backfilled since prior run). Validates cost pipeline.

## Quota table (all sites, EUR)
| month | total cost | revenue | quota % | fallback share % |
|---|---|---|---|---|
| 2026-01 | 2,414,944 | 10,819,044 | 22.3 | 5.4 |
| 2026-02 | 1,882,305 | 9,241,733 | 20.4 | 3.8 |
| 2026-03 | 1,558,659 | 8,806,505 | 17.7 | 4.0 |
| 2026-04* | 1,709,104 | 8,604,469 | 19.9 | 7.4 |
| 2026-05* | 1,921,859 | 9,715,159 | 19.8 | 16.4 |
| 2026-06* | 1,128,147 | 4,607,559 | 24.5 | 64.3 |
*partial (loading frontier ~mid-June); rising fallback share is the partial tell — real spike starts May.

## Jan-Mar: all-sites vs excluded-sites quota
- Jan: 22.3% vs 20.9% (+1.4pt) | Feb: 20.4% vs 18.5% (+1.9pt) | Mar: 17.7% vs 15.5% (+2.2pt)
- Adding Wolfen + US sites (CMH/MI/PX) lifts quota ~1.4-2.2pt — those sites ship at a higher cost-to-revenue ratio.

## Checks
- Anchor reproduced to the euro under Grain A.
- Excluded-sites quota reproduced prior run within 0.3pt.
- FLAG: invoice-line freight runs ~6% BELOW fact real_shipping_cost_eur / cost_summary.total_eur on the same shipments (Jan: 2.016M vs 2.135M per-shipment, date-agnostic). Contract invariant (real==total==sum-of-buckets, verified 2026-05-25) does NOT hold in current live mart. Brief specified invoice-line basis, so honored it; quota would be ~1.3pt higher on cost_summary basis. Rulebook/mart-state gap to surface.

## Deliverable
Chat-only (brief said chat-only, no files).
