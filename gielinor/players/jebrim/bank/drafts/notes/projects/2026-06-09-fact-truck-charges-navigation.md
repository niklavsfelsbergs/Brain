# shipping_mart.fact_truck_charges — navigation traps

Off-contract table (NOT one of the 4 documented gold facts; `ship_mart_ro` denies it — query via full-access `tcg_nfe`). Sized the DHL Warenpost linehaul off it in [[S172_df374cef_dhl-truck-cost-warenpost-kleinpaket|S172]]. Three traps, all of which produce silent false-negatives if you trust names:

1. **`truck_provider` is a LANE name, not a carrier service.** Distinct values: `DHL Kleinpaket`, `UPS DHL Freight`, `UK DHL Freight`, `UK and FR DHL Freight`, `ORWO Consignment`. There is **no "Warenpost" value** — `LIKE 'DHL%W%'` returns zero rows.
2. **The "DHL Kleinpaket" lane actually carries Warenpost** (99%+ `DHL54WARENPOST`) — the lane name is a misnomer. Real Kleinpaket has no dedicated lane here. Resolve carrier→lane by **ground-truth join**, never by lane name.
3. **Join key is `fact_shipments.allocated_truckload_id = fact_truck_charges.truckload_id`** — the bare `truckload_id` on the shipment side does NOT match (returns 0).

Other facts: grain = one row per truckload; cost = `cost_per_truck_eur` (flat ~€284/load, SharePoint-sourced, net); period = `departure_date`; allocated parcel count = `shipment_count_allocated`. **Volume-weight** (Σcost / Σparcels); the per-load `cost_per_parcel_eur` unweighted average is inflated by light loads. Spans 2025-01-02 onward.

Worth a `reference/` note in the shipping-agent repo (maintainer-gated). Source: [[S172_df374cef_dhl-truck-cost-warenpost-kleinpaket|S172]] quest-log + [[S169_truck-cost-warenpost-sizing|S169]] sub-trace.
