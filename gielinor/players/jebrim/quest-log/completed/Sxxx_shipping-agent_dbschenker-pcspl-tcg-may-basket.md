# Shipping-agent pull — DB Schenker / PCS PL / TCG / May basket

**Actor:** shipping-agent (emulation), inherited player Jebrim
**Date:** 2026-05-28
**Tier:** gold-contract (full-access profile present but not needed; stayed on gold)

## Ask
Product baskets shipped via DB Schenker in May, TCG shops only, single origin PC SPL. Composition / volume mix.

## Scope resolved
- Carrier literal: `DB SCHENKER` (uppercase in data).
- Origin: brief said "PC SPL" — no such literal; resolves to `production_site = 'PCS PL'` (Polish PCS site, the only DB Schenker origin in May).
- Vertical TCG: `source_system IN ('Picturator','PicaAPI')`. Excluded the 1 internal-print (`PCS`) shipment.
- Period: May 2026, month-to-date through 2026-05-28 (mart's latest data = today; May is PARTIAL).

## Turn log
- Confirmed literals: DB SCHENKER carrier, PCS PL site, TCG = Picturator+PicaAPI. May data runs to 05-28.
- Total slice = 1,780 shipments (1685 Picturator + 95 PicaAPI). Reconciliation denominator.
- Order-items: all 1,780 have items; 9,728 items total. SKU prefix (3 chars) = product family.
- Category mix by item qty: Canvas 7,094 (72.9%), Aluminium 1,063 (10.9%), Acrylic 495 (5.1%), Forex/foam 464 (4.8%), Poster 291 (3.0%), Cushions 170 (1.7%), all others 151 (1.6%). Sums to 9,728 — ties.
- Basket shape: 1,608 single-category shipments, 172 multi-category. Mostly canvas-only parcels.

## Result
Canvas-dominated basket (~73% of items, in ~87% of parcels). Rest is a long tail of aluminium / acrylic / forex / poster / cushions.

## Checks
- Parts sum to whole: category qty sums = 9,728 = total items. Shipments-with-items = 1,780 = total shipments. Clean.
- Single vs multi-family split reconciles (1,608 + 172 = 1,780).

## Deliverable (outside brain)
- CSV: shipping-agent/scratchpad/dbschenker-pcspl-tcg-may2026-basket.csv
- Chart: shipping-agent/scratchpad/20260528-094834--db-schenker-shipments-from-our-polish-site-product-mix-may-2026-b2c-merchone-through-the-28th.html

## Open
- "PC SPL" in the brief vs `PCS PL` in data — mapped on best evidence (only DB Schenker origin). Worth a one-word confirm from Jebrim that PCS PL is the intended site.
- May is partial (through the 28th) — full-month numbers will be larger.
