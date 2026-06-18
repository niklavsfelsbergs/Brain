# ORWO cost-quota bridge — May 2026 vs April 2026 (why it went up)

Spawned by Jebrim as shipping-agent. Quota basis LOCKED: final_shipping_cost_eur / net_revenue_eur, both on shipping_mart.fact_shipments, order-month lens (shop_order_created_date). Tier: gold-contract.

## Status trace
- Contract reread (how_to §0, mart-contract, known-dq). Confirmed ORWO source_system = 'ORWO', carries BOTH cost (2.08M of 2.26M ships) and revenue (rev 100% populated per V1-freeze). Order-anchor = shop_order_created_date.
- Headline: Apr quota 15.54% (cost €217,794 / rev €1,401,294, 65.4% inv); May 16.57% (cost €265,619 / rev €1,602,425, 58.9% inv). Delta +1.03pp.
- Num/den split TIES OUT (residual 0): cost-driven +3.41pp (cost +€47,825 / +22.0%), rev-driven −2.38pp (rev +€201,131 / +14.4% pulls quota DOWN). Quota up only because cost outran revenue.
- Like-for-like invoiced-only quota: Apr 12.70% → May 13.25% = +0.55pp (~half the headline). Other half = estimate-mix/coverage (May leans more on higher estimate).
- Carrier (DHL3/DHLKP3 folded back into DHL — they group as OTHER, dim quirk like DHL2/DHLKP trap): volume mix STABLE. DHL 130.9k→130.9k, POST 39.2k→39.8k, UPS 26.3k→30.9k. NOT a mix-to-expensive-carrier shift. Rate effect: DHL €/ship €0.88→€0.97 (+11%, 96% inv both = solid). UPS €/ship €1.16→€1.82 but May UPS only 57% inv + invoiced subset over-weights pricey parcels (€2.78 inv vs €1.24 est) = coverage-contaminated, uncertain. POST flat €2.83 (~1% inv, estimate, structural ORWO-POST bulk-mail hole).
- Bucket split (invoiced per-ship): base_rate €0.749→€0.878 (+€0.129, 66% of move), other €0.089→€0.140 (+€0.051, 26%), fuel +€0.011, oversize +€0.005. Base-rate-led (GRI-shaped). Caveat: May invoiced pop is coverage-biased subset.
- Lane: ~92% Germany both months, no geography shift. DE cost €213k→€258k.

## Headline answer
ORWO May quota rose +1.03pp (15.54%→16.57%) entirely on the cost side: cost +22% outran revenue +14%. ~half is a real DHL base-rate rise (€0.88→€0.97/ship, well-invoiced); the other half is coverage — May only 58.9% invoiced, leaning on the pricier estimate, so the quota can still move as May UPS/DHL invoices land.

## Caveats
- May 58.9% invoiced — under-complete for a closed month past 30d. UPS May 57% inv with a high-cost selection bias in landed invoices. Quota is provisional; will likely move as invoices land.
- Bucket detail invoiced-only; May invoiced pop is a biased subset.
- DHL3/DHLKP3 carrier-group dim quirk (rolls to OTHER) — flagged as rulebook/known-dq gap candidate.

Deliverable: chat-only (bridge returned to Jebrim). SQL in the report.
