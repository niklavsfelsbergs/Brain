# S168 — UPS effective fuel-surcharge rate reconciliation (mart pull)

**Player:** Jebrim · **Session:** 1a9eb9d9 · **Date:** 2026-06-09
**Thread:** EU tender 2026 → UPS. Sibling to S168 rate-card-diff; this pull tests a rate-card *reading*.
**Agent:** shipping-agent emulation, gold-contract pull over `shipping_mart`.

## Ask
Measure UPS **effective fuel ratio = SUM(fuel) / SUM(base)** from real invoiced cost only, to
discriminate two readings of the contract line "Fuel Surcharge = 35, Percent Off - per Shipment":
- **Discount reading** — 35% off UPS's floating published index → effective ~18–21% of base.
- **Flat reading** — flat 35% fuel surcharge → effective ~35% of base.

## Scope used
- UPS = `UPPER(shipping_provider_group) = 'UPS'`. Total 2,389,396 shipments.
- Invoiced only = `cost_source = 'invoice'` → 1,729,087 rows (72.4% by count, 63.9% by euro).
- Fuel bucket = `fact_shipment_cost_summary.fuel_surcharge_eur`; base = `base_rate_eur`.
- Month axis = `shop_order_created_date` (near-complete; `received_by_carrier_date` NULL on ~20% of
  invoiced UPS rows, unusable). Service split = `shippingprovider_extkey`.
- Gold contract, no joins outside `shipping_mart`. No `CLAUDE.local.md` → gold-only perimeter.

## Findings
- **Overall effective fuel ratio = 19.34%** (fuel €1,684,043 / base €8,706,185). Squarely in the
  discount band (~18–21%), nowhere near 35%. → **discount reading confirmed.**
- Dominant service `UPS04STD` (road/standard) = **91.3% of invoiced shipments**, ratio 19.77%.
  Population is overwhelmingly road — not a blended air/road artifact.
- Air/Express services run higher (Express Saver 23–24%, plain Express 26%), Worldwide Economy lower
  (5–6%) — consistent with road vs air fuel indices differing. Doesn't move the headline.
- **Implied published index** (discount reading, STD): 0.1977 / 0.65 = **30.4%** — plausible UPS EU
  road fuel index for the period (~28–32% per the hypothesis brief).
- **Monthly drift:** stable 16–18% through 2025, rising to ~24.5% in Apr–May 2026. STD-only confirms
  the jump is real (19.9% Jan → 27.9% Apr 2026), not a mix shift. A floating index under a fixed 35%
  discount predicts exactly this kind of drift; a flat 35% would be capped and couldn't move.

## Checks (verified)
- Bucket invariant holds: `cost_summary.total_eur` == `fact_shipments.real_shipping_cost_eur`
  to the cent (€13,046,872.72 both sides).
- UPS discount/credit buckets entirely empty (0 rows) → contract discounts are baked into net
  `base_rate_eur`. Ratio = fuel-on-net-base, the correct denominator for the test.
- Negative base/fuel rows immaterial (217 / 226 of 1.73M; credit reversals).
- Service split sums to the 1,729,087 total; recent jump replicated on STD-only slice.

## Coverage caveat
- 72.4% of UPS shipments invoiced (by count). The fuel/base ratio rests on the invoiced subset only;
  expected/uncosted rows carry no bucket detail. The 63.9% euro-weighted invoiced share reflects
  estimate-heavy recent months still backfilling — recent-month ratios may firm as bills land.
- `Manual Bill` (UPS invoice `838*` = customs/duty/DDP) routes to excluded buckets, not base/fuel —
  no contamination.

## Conclusion
The measured ratio (19.34% overall, 19.77% on the road workhorse) supports the **discount reading**:
the "35" is a 35% discount off UPS's floating published fuel index, not a flat 35% surcharge. Implied
road index ~30% is plausible. Recent climb to ~24–28% is consistent with the published index floating
upward under a fixed discount.

## Deliverable
Chat-only (returned to principal). No chart requested. SQL recorded in this trace's findings.

## Knowledge saved
This trace. No bank draft yet — promote at alching alongside the S168 rate-card-diff note if the
fuel reading graduates into the tender model.
