# S231 — shipping-agent pull: Güll PARCELS_PER_PALLET=150 grounded substitutes

**Actor:** shipping-agent sub-agent (emulated), spawned by Jebrim
**Brief:** EU Tender 2026. Validate the borrowed `PARCELS_PER_PALLET=150` guess in the Güll carrier cost engine. Güll is a TENDER OFFER carrier (no observed Güll data in mart). Find grounded substitutes from `shipping_mart`. Two objectives: (1) does mart carry a loading-unit/pallet concept + benchmark it; (2) per-parcel physical distribution on Güll's lanes (PCS-PL Szczecin → AT, CH). Hand clean distributions, do NOT compute final fill recommendation.
**Tier:** gold-contract (no CLAUDE.local.md; gold perimeter absolute).
**Scope:** PCS PL production site, dest AT + CH, invoiced-only (cost_source='invoice'), base period 2026-Q1 (shop_order_created_date 2026-01-01 .. 2026-04-01).

## Status log
- Loaded how_to.md in full; no CLAUDE.local.md -> gold-only.
- Schema confirms a loading-unit concept EXISTS on fact_shipments: loading_unit_id, truckload_id, allocated_truckload_id. Physical fields all present (weight_kg, length/width/height_cm, volume_cm3, length_plus_girth_cm).
- OBJ1: loading_unit = pallet-grain (mean 50 parcels). truckload = linehaul-grain (mean 476). loading_unit is 96%-populated on PCS PL (Güll's origin site) — directly relevant benchmark.
- OBJ1 nuance: PCS PL loading units are single-CARRIER (95%) but mixed-DESTINATION-country (avg 2 countries/unit, only 53% single-country). So today's loading unit = carrier-consolidation pallet, not per-dest-country pallet.
- OBJ2: AT 25,018 parcels (24,774 invoiced); CH 11,490 (11,445 invoiced). Weight ~100%, vol/dims ~99.9% coverage. Clean population.
- Weight: AT mean 1.708kg median 1.022; CH mean 1.348kg median 0.632. Light, flat parcels (mean height ~8cm).
- Volume: AT mean 22.2L median 9.3L; CH mean 17.5L median 7.6L. volume_cm3 == L*W*H exactly (bounding-box, not volumetric weight).
- Checks: euro-pallet envelope (0.8x1.2x1.85m=1.776m3); 300kg weight-reachability ratio computed for handoff.

## Headline (handed to Jebrim; he does fill math vs contract caps)
- Loading-unit packing benchmark @ Szczecin: median 31 / mean 50 / p90 125 / p95 163 parcels per unit.
- Weight 300kg-reachability: AT 300/1.708 = ~176 avg parcels; CH 300/1.348 = ~223 avg parcels to hit weight cap.
- Volume binding (fill the 1.776m3 euro-pallet at mean parcel vol, geometric ceiling): AT 1,776,000/22,179 = ~80; CH ~102.

## Caveats
- Loading unit is mixed-destination today; the AT/CH-only pallet would pack differently. Number is a site-level packing-density benchmark, not an AT/CH-specific observed pallet.
- Volume ceiling ignores packing inefficiency / void; it's a geometric upper bound only.
- Güll has zero observed mart rows by construction; all figures are physical-population substitutes, not Güll actuals.
