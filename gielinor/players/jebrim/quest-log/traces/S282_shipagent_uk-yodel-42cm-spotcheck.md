# Trace — shipping-agent: UK 42.1cm mid-side PCS spot-check

- **Player in scope:** Jebrim
- **Spawned:** 2026-06-19
- **Tier:** gold-contract (`shipping_mart.fact_shipments` only)
- **Ask:** red-team spot-check — pull example rows from population P so the principal can verify the 42.1cm mid-side himself in PCS; identify the PCS-lookupable order number.

## Scope (standing UK Yodel cut)
- destination_country_code='GB', shop_order_created_date in [2026-01-01, 2026-04-01), cost_source='invoice', source_system IN ('Picturator','PicaAPI'), dims-present, mainland-only (offshore-exclusion regex per brief).

## Turn log
- Inspected fact_shipments columns: 4 order-identifier candidates — shop_ordernumber, source_order_id, production_orderid, production_ordernumber.
- production_ordernumber = `D########` form (PCS production order) — the PCS-lookupable key. shop_ordernumber = storefront order ref (secondary). Coverage in scope: production_orderid/source_order_id/shop_ordernumber 100%; production_ordernumber ~95.5% (93,849/98,274).
- Pulled 10 example rows from P favoring 60x40 Box-in-the-Box. All are 66.10 x 42.10 x 8.50cm, vol 23,653.88 cm3, d_mid=42.1 = the width axis. Exactly one raw dim (~42.1) is the cap-buster.
- Verified P size = 1,743 (matches brief ~1,743); 1,679 are 60x40 BiB.

## Headline result
- 10 example PCS orders returned in-message (D-numbers + shop refs + raw L/W/H).
- d_mid=42.1 falls out of raw width_cm=42.10 on every 60x40 BiB row; d_long=66.10 (length), d_short=8.50 (height).

## Caveats carried
- Invoice-only, dims-present, mainland. Order-month lens.

## Open / flag to principal
- **P is NOT Yodel-dominated.** Carrier mix in P: DPD UK 1,563 / Maersk 171 / Yodel 8 / UPS 1. The "standing UK Yodel cut" is the named scope frame, but population P rides almost entirely on DPD UK. If the 42cm cap question is genuinely about Yodel's envelope, P may be the wrong carrier population — worth confirming with the principal whether the cut should be carrier-filtered to Yodel.
