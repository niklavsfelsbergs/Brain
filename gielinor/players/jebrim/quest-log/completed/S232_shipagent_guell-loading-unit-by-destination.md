# S232 — shipping-agent pull: Güll loading-unit parcel-count by DESTINATION COUNTRY

**Actor:** shipping-agent sub-agent (emulated), spawned by Jebrim
**Brief:** EU Tender 2026 follow-up to [[S231_shipagent_guell-pallet-fill-substitutes|S231]]. Re-pull the loading-unit (pallet-grain) parcels-per-unit distribution, scoped to DESTINATION COUNTRY, to test whether single-country (AT-only / CH-only) pallets pack DENSER than mixed-destination ones — a check on the borrowed PARCELS_PER_PALLET=150 guess in the Güll engine. Hand clean distributions; do NOT compute the fill recommendation.
**Tier:** gold-contract (no CLAUDE.local.md; gold perimeter absolute).
**Scope:** PCS PL (Szczecin) origin, loading units, 2026-Q1 (shop_order_created_date 2026-01-01 .. 2026-04-01). 2026-Q2 in progress today (2026-06-12), so Q1 = freshest FULL quarter (matches [[S231_shipagent_guell-pallet-fill-substitutes|S231]] base period).

## Status log
- Loaded how_to.md in full; confirmed loading_unit_id / production_site / destination_country_code on fact_shipments.
- PCS PL confirmed as Szczecin site (11.5M rows). Q1 = freshest full quarter.
- Validator blocks PERCENTILE_CONT...WITHIN GROUP (works as Redshift window fn but MCP rejects); computed percentiles via PERCENT_RANK ranking instead (discrete <= cut = nearest-rank, slight conservative bias on exact percentile but fine for distribution shape).
- Bucket split: AT-only / CH-only / single-other / mixed. Reconciliation ties exactly to all-units (11,739 units / 616,009 parcels).

## Headline (handed to Jebrim)
All-units baseline (mixed incl.): 11,739 units, mean 52.4, median 33, p90 127, p95 169.
Single-dest (all): 6,239 units, mean 63.8, median 40, p90 160, p95 210.  -> DENSER than mixed.
Mixed-dest: 5,500 units, mean 39.5, median 30, p90 78, p95 97.
AT-only: 249 units (THIN), mean 20.1, median 12, p90 48 -> SPARSE, below mixed.
CH-only: 139 units (THIN), mean 69.7, median 55, p90 132 -> DENSE, well above all-units mean.

## Key probe
AT parcels (24,493) ride 1,824 units but only 249 AT-only -> most AT volume goes on MIXED pallets; AT-only = small leftover partials (sparse).
CH parcels (11,378) ride only 334 units, 139 CH-only -> CH consolidates into dedicated single-country pallets (dense).
=> Single-country density is REAL but driven by CH, not AT. AT-only does NOT rescue 150.

## Caveats
- AT-only (n=249) and CH-only (n=139) are THIN samples; CH-only median 55 / p90 132 is directional, not robust.
- Percentiles via nearest-rank (validator blocks ordered-set aggregate); shape reliable, exact p-value approximate.
- Did NOT compute final fill recommendation per brief.

## Deliverable
Chat-only (distributions handed back).
