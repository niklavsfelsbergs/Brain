# Trace — Shipping-agent: UK Yodel Medium mid-cap knife-edge red-team

- Spawned by: Jebrim (principal). Date 2026-06-19.
- Tier: gold-contract (shipping_mart.fact_shipments only).
- Scope: UK Yodel standing cut — destination_country_code='GB', shop_order_created_date in [2026-01-01, 2026-04-01), cost_source='invoice', source_system IN ('Picturator','PicaAPI'), dims-present, mainland-only (offshore postcode exclusion per brief).

## Question
The 1,743 parcels that reclassify Yodel Large->Medium under a 64->70cm length cap EXCEPT they bust Medium's mid-side cap (d_mid>41). Are they bunched just over 41 (knife-edge) or spread?

## Population P (confirmed)
n = 1,743. d_mid: min 42.00, max 42.10, avg 42.096, median 42.10.

## Headline finding
Not a continuum at all. P is exactly TWO discrete carton SKUs:
- 66.0 x 42.0 x [20.5..27.0]  -> d_mid = 42.00, n = 64
- 66.1 x 42.1 x 8.5           -> d_mid = 42.10, n = 1,679 (single SKU)
d_mid == the box width in both. Long side = 66, mid = 42, short = the third dim.

## Histogram (integer cm bands)
(41,42]=64 ; (42,43]=1679 ; (43,44]=0 ; (44,45]=0 ; (45,50]=0 ; (50,60]=0 ; (60,inf]=0.
Everything is in [42, 42.10]. Nothing above 43.

## Cumulative capture if mid-cap 41->X (with 64->70 length)
<=42: 64 parcels (GBP 92.00/Q at 1.4375/parcel)
<=43: 1,743 (full) (GBP 2,505.56/Q)
<=44,<=45,<=50: 1,743 (no further — population exhausted by 43)

## Granularity
Non-integer d_mid: 1,679 of 1,743 (the 42.10 SKU). But this is NOT measurement noise -
the .10 is a declared catalogue box dimension (every parcel in the SKU is identical 66.1/42.1/8.5).
Only 2 distinct d_mid values exist. '41' is a hard catalogue wall, not a rounded measurement floor.

## Answer
KNIFE-EDGE, extreme form. All 1,743 sit within 1.1mm of each other at ~42cm, just 1cm over the 41 cap.
A mid-cap nudge 41->42(.1) captures the entire population. No spread, no tail.

## Caveats
Invoice cost-basis only; dims-present rows only; mainland only. GBP saving = Large->Medium delta 1.4375/parcel (fuel rides base), per brief.
