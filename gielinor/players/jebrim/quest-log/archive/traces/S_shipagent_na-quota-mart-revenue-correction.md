# NA shipping-quota — recompute on mart's OWN revenue (correcting topic 46)

**Actor:** shipping-agent (mart sub-agent), in Jebrim's namespace
**Date:** 2026-06-15
**Tier:** upstream maintainer profile available, but answer stayed on the GOLD contract (`shipping_mart.*` only). Finance-bound.
**Brief:** Prior topic-46 analysis wrongly took net product revenue from `dw.sales_fact`. Revenue lives IN the mart; SCM uses mart revenue. Re-anchor the NA quota analysis on the mart's revenue.

## Status log
- STEP 0: revenue column = `fact_shipments.net_revenue_eur` (shipment-grain order rollup of `fact_shipment_orderitems.revenue_eur`). Picturator = full customer-paid NET (product + allocated shipping − discount, reorders zeroed). API/Rew = product-line-only. PCS = NULL by design. This is the contract's quota denominator (`final_shipping_cost_eur / net_revenue_eur`). NOTE: for Picturator it includes allocated shipping revenue — not pure product — but it IS what SCM's quota uses (confirmed by tie-out below).
- STEP 1: SCM 26.5% REPRODUCED. US-only, May-2026, final cost / net_revenue, **order-month lens (shop_order_created)** = **26.52%**. Ship-month lens = 27.20%, produced-month = 27.40%. SCM lens = order-month. US May is ~all-TCG (only 9 PCS rows). pct invoiced 91.7%.
- STEP 2: corrected quota table (TCG, order-month, final/net_rev):
  - US:  Q1avg 24.50% → May 26.51%  (delta +2.01pp)
  - NA:  Q1avg 25.49% → May 27.14%  (delta +1.65pp)
- STEP 3: NA Q1→May bridge (+1.659pp total):
  - MIX (D2C→API share shift): **+1.85pp** (dominant)
  - within-channel net: −0.19pp = cost-per-parcel +1.76pp offset by revenue-per-parcel −1.95pp
  - API revenue share 16.5% → 33.9% (+17.4pp). API quota ~33-36% vs D2C ~23-24%.
  - vs prior WRONG denominator: mix was +1.83pp of +1.53pp total → corrected mix +1.85pp of +1.66pp. Mix barely moved; the TOTAL grew. Mix still dominant.
- DQ on denominator: null revenue 0.43% (May) / 0.59% (Q1) of NA TCG rows; handful zero/neg (reorders zeroed + credits). Negligible.
- Cost anchors as pp of May NA rev (€2.163M): USPS step €18.8k = +0.87pp; CMH reroute €23.4k = +1.08pp.

## Cost basis / lens
- final cost = COALESCE(real, expected, avg); pct invoiced 91.7% (May NA) / 98.9% (Q1 NA).
- denominator = net_revenue_eur (mart's own). lens = order-month (shop_order_created_date). scope = TCG (Picturator+PicaAPI), destination US / US+CA.

## Open
- net_revenue_eur for D2C includes allocated shipping revenue (not pure product). It reproduces SCM exactly, so it's the right denominator for "quota", but flag if a future ask wants a pure-product denominator — that would lower the denominator and RAISE quota.
