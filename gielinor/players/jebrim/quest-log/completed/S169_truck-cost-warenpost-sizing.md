# S169 — Warenpost truck-cost sizing (shipping-agent mart pull)

Shipping-agent sub-agent pull for Jebrim. EU-tender 2026 / dhl_paket engine (v2.1.0, Warenpost service added [[S165_f4a07849_cost-structure-card-warenpost-routing-plan|S165]]).
Task: SIZE the Warenpost linehaul/injection truck cost from the mart, 2026, as the truck-cost input to the engine.

## Scope
- Player: Jebrim. Vertical: implicit (truck lane is origin-side, PCS PL print site). Origin: PCS PL (Szczecin).
- Tier: **off the gold contract** — target table `shipping_mart.fact_truck_charges` is NOT one of the 4 documented gold facts. Queried via Redshift MCP (full-access tcg_nfe user); ship_mart_ro would deny it.

## Turn log
- Introspected fact_truck_charges: grain = 1 row per truckload_id (2,387 loads, no dupes, 2025-01-02 → 2026-06-08). Cost = cost_per_truck_eur (EUR, SharePoint-sourced flat tariff). Carrier id = truck_provider. Date = departure_date.
- **Brief premise broke:** LIKE 'DHL%W%' returns ZERO rows. truck_provider holds LANE names, not the parcel carrier service. Values: DHL Kleinpaket / UPS DHL Freight / UK DHL Freight / UK and FR DHL Freight / ORWO Consignment. No "Warenpost" lane.
- Found join key: fact_shipments.allocated_truckload_id → fact_truck_charges.truckload_id (NOT the bare truckload_id col — that returns 0 matches). Ground-truthed: 2026 Warenpost parcels ride the **DHL Kleinpaket lane** (110,705 parcels / 317 loads). That lane is 99%+ pure DHL54WARENPOST — lane name is a misnomer (named Kleinpaket, carries Warenpost). Freight lanes carry Maersk/DPD/Yodel/UPS, NOT Warenpost.
- Reconciled two methods: lane-level €85,200 / 109,050 = €0.781/parcel; parcel-attributed €81,716 / 106,815 = €0.765/parcel. Agree within ~2%.
- DQ: flat €284/truck tariff all 300 loads. Per-load cost_per_parcel_eur must NOT be averaged (unwtd €2.52, inflated by light loads); volume-weighted is correct. _smoothed col tames it (€0.83). June ~25% complete (13 loads through 06-08).

## Headline (cost basis: truck/linehaul cost, EUR, SharePoint-sourced, net flat tariff)
- **2026 YTD total Warenpost truck cost: €85,200** (DHL Kleinpaket lane, Jan–08 Jun).
- **Recommended engine input: €0.78/parcel** (volume-weighted). Monthly €0.70–0.95, no trend.
- Monthly (loads / €): Jan 58/16,472; Feb 51/14,484; Mar 56/15,904; Apr 62/17,608; May 60/17,040; Jun(part) 13/3,692.

## Open / needs principal
- Rulebook gap: fact_truck_charges is off-contract + truck_provider is lane-not-service + join key is allocated_truckload_id. Worth a reference/ note (maintainer-gated).
- Per-parcel denominator choice: lane parcels (109,050) vs engine's own Warenpost parcel base — engine should divide by ITS Warenpost count, not the lane's, if they differ.
