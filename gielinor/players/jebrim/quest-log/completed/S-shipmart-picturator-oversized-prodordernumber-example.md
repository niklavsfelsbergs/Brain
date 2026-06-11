# Shipping-agent pull — Picturator CUSTOM_OVERSIZED example w/ production-system order number

**Player:** Jebrim · **Tier:** gold-contract (`shipping_mart.fact_shipments` only)
**Brief:** EU-tender DB Schenker reroute continuation. One CUSTOM_OVERSIZED shipment from
source_system Picturator. Need the *production-system* order number (NOT shop_ordernumber)
— identify the right column. Plus dims + carrier + ~5 alternates.

## Turn log
- Casing confirmed: source value is `'Picturator'` (13.2M rows). Not 'PICT'/'PICTURATOR'.
- CUSTOM_OVERSIZED lives in `packagetype` (NOT packagetype_group, which is NULL for it).
  64,068 Picturator CUSTOM_OVERSIZED shipments.
- Candidate order/id columns on fact_shipments: shop_ordernumber (storefront),
  source_order_id (bigint, upstream shop order id), production_orderid (bigint, prod order id),
  production_ordernumber (varchar, human-readable prod ref, e.g. 'D42791963').
- Production-system order number = **production_ordernumber**. It's the `D`-prefixed string
  form of production_orderid; = 'D'||production_orderid in 59,121/64,068 (92%), the ~8%
  divergence (reorders/relabels) is why the distinct printed-reference column exists.
- All four id columns 100% populated on the slice.

## Headline example
- production_ordernumber **D42791963** (production_orderid 42791963)
- shop_ordernumber ESA59900788893 · trackingnumber 00390110170046521291 · shipment_id 26767313066227681
- 155 x 104 x 8 cm, L+girth 379 cm, 6.84 kg · DB SCHENKER (DBSCHENKERPLEUHOME) · dest ES · 2026-06-09

## Checks
- Picturator casing verified against distinct values. CUSTOM_OVERSIZED located in correct column.
- Column identity proven by the D-prefix equality test (92%), not inferred from one row.
- All ids non-null across the 64,068-row slice.

Deliverable: chat-only (no chart/CSV requested).
