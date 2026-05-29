# Shipping-agent pull: DB Schenker freight fit by package size

**Spawned by:** Jebrim · **Agent:** shipping-agent (emulated) · **Date:** 2026-05-28
**Tier:** gold contract for size classification; off-contract (`dw.dim_products`) for the product-category cut only — flagged.

## Question
Do DB Schenker baskets on the Polish print site actually belong on freight (>120cm any dim),
or could a chunk move to a parcel carrier (UPS, L+girth ≤ 325cm)? Break by product.

## Slice (locked, verified in data)
- Carrier `DB SCHENKER`, origin `PCS PL`, TCG = `source_system IN ('Picturator','PicaAPI')`, May 2026 MTD (max date 2026-05-28).
- Total 1,780 shipments / 9,728 items — matches prior-run anchor exactly. ~83% canvas by dominant subcategory (73% by item count, both consistent).

## Turn log
- Confirmed dimensions live on gold `fact_shipments` (`length_cm/width_cm/height_cm`, plus precomputed `length_plus_girth_cm`). Unit = cm. Stayed gold for classification.
- Verified literals + slice total = 1,780 / 9,728, max date 28th. Clean match.
- Size split: oversize (>120cm) 1,760 · within-parcel (≤120cm) 20 · of those, UPS-fits (L+girth≤325) 7. Reconciles to 1,780.
- DQ: zero NULL dims, zero zeros, precomputed girth column == my L+2W+2H on all 1,780 rows. No DQ haircut needed.
- Category requires `dw.dim_products` (off gold contract) — gold facts carry only product keys. Went upstream for the category cut, flagged off-contract.
- Off-freight candidates (the 7) scattered: canvas 2, aluminium 3, acrylic 1, carpet 1. Not concentrated.

## Headline result
- 1,760 of 1,780 (98.9%) correctly on freight. Only 20 (1.1%) within parcel range; only 7 (0.4%) physically fit UPS. Effectively zero misrouting. Canvas is almost entirely true-oversize by design (long flat panels).

## Deliverable (outside brain)
- Chart: `Documents/GitHub/shipping-agent/scratchpad/20260528-095435--db-schenker-freight-fit-by-product-polish-print-site-tcg-may-2026.html`
- CSV: `Documents/GitHub/shipping-agent/scratchpad/20260528-01_db-schenker-pcspl-freight-fit.csv`

## Open / for principal
- Category cut is off the curated gold contract (upstream `dw.dim_products`); won't carry gold's DQ/coverage guarantees. If category becomes a recurring need on this slice, worth flagging to the maintainer whether subcategory should surface on a gold fact.
