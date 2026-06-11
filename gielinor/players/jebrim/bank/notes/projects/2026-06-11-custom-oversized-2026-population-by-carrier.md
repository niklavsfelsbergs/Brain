# CUSTOM_OVERSIZED — the full-2026 population by carrier (counts, median dims, provenance) (2026-06-11)

> Draft (harvest, [[S207_4b987ab6_maersk-hermes-dims-db-schenker-reroute-consult|S207]] sid8 4b987ab6). Full-2026 empirical profile of the `CUSTOM_OVERSIZED` packagetype across all carriers — the broader population behind the Q1 DB Schenker reroute switch in [[2026-06-10-db-schenker-reroute-package-dims-and-savings]]. Live mart pulls via shipping-agent (gold `fact_shipments`). Promote at next Jebrim alch. Links: [[eu-tender]], [[shipping-mart]].

## 2026 shipment count per carrier (ship-date basis)
Scoped on `received_by_carrier_date` in 2026 (a ship/dispatch event), `LOWER(TRIM(packagetype)) = 'custom_oversized'`. Coverage: **88.4%** of the CUSTOM_OVERSIZED population carries a usable ship date (the 11.6% null-dated drop out of any ship-year filter; order-date basis would add only ~41 net to 2026 → immaterial).

| Carrier | 2026 count |
|---|---:|
| UPS | 6,949 |
| DB Schenker | 5,912 |
| DPD UK | 524 |
| Yodel | 89 |
| DHL | 33 |
| DPD Poland | 2 |
| **Total** | **13,509** |

**UPS — not DB Schenker — is the largest CUSTOM_OVERSIZED carrier.** Most of the oversized tail already isn't on DBS. The oversized-capacity question for carrier talks is as much a UPS-lane question as a DBS one.

## Median dims per carrier + the templated-vs-measured split (load-bearing)
Median (not mean) of the 2026 slice. Girth = L+2W+2H = the mart's `length_plus_girth_cm` (reconciles exactly on every carrier). Zero-dim sentinels excluded (UPS 19 rows, DPD UK 1 row).

| carrier | n | med L | med W | med H | med girth | med kg |
|---|---:|---:|---:|---:|---:|---:|
| UPS | 6,949 | 132 | 84 | 6 | 312 | 6.42 |
| DB Schenker | 5,912 | 163 | 95 | 8 | 369 | 6.91 |
| DPD UK | 524 | 132 | 84 | 6 | 312 | 6.38 |
| Yodel | 89 | 132 | 84 | 6 | 312 | 5.22 |
| DHL | 33 | 21.5 | 22.5 | 3.7 | 73.9 | 0.30 |
| DPD Poland | 2 | 42.3 | 58.8 | 4.9 | 169.5 | 2.57 |

- **UPS / DPD UK / Yodel are templated, not measured** — all three sit on the identical **132×84×6 / girth 312** footprint; one L×W×H tuple covers 62% / 57% / 33% of rows. Read these medians as "the source-system oversize default," not a real central parcel. Do **not** size capacity off them. (Same pattern as the zV templating in [[2026-06-10-db-schenker-reroute-package-dims-and-savings]] — dims are catalogue presets; weight is the only varying physical input.)
- **DB Schenker is the only genuinely measured distribution** — top tuple just 6%, 208 distinct girth values; median **163×95×8, girth 369** is a real central package. **369 > Hermes' 360 bulky ceiling AND > Maersk's 300** → the *median* DBS oversized parcel doesn't fit either reroute carrier. The reroutable subset is the **below-median (smaller-girth) half**; most DBS oversized is structurally freight-only by girth.
- **DHL (n=33, girth ~74) is a label misuse** — the CUSTOM_OVERSIZED tag applied to small parcels, not real oversize. Per [[categorical class needs a physical cross-check]]-style caution.

## Mart column provenance (for joins / examples)
- **Source system:** `source_system` distinguishes `'PCS'` (Picanova storefront; `shop` is null on these rows) from `'Picturator'` (13.2M rows). Match on `source_system`, not `shop`.
- **Production-system order number = `production_ordernumber`** (the `D`-prefixed printed reference, e.g. `D42791963`) — distinct from the storefront `shop_ordernumber`. Its numeric backing key is `production_orderid`. `production_ordernumber = 'D'||production_orderid` holds in ~92% of rows; the ~8% diverge on reorders/relabels — **so for a join, key on whatever representation the external system carries** (numeric `production_orderid` vs the `D…` string), not on the assumption they're interchangeable.
- `shop_ordernumber` and `source_order_id` are both shop-side, not production.

## Open / next
- The single most useful next pull: 2026 oversized counts **split by girth band** (≤300 / 300–360 / >360) per carrier — converts the median above into the actual reroutable-pool size (what fits Maersk's 300, what only Hermes' 360 can hold, what's freight-only).
