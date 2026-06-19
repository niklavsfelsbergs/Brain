# ORWO in the mart - weight is mis-grained + the dims capture gap

Draft (2026-06-19, [[S275_abfcf511_orwo-tender-contracts-coverage-weight-grain|S275]]). Durable mart/lineage fact - belongs in [[shipping-mart]] (+ [[bi-etl]] for the wiring). Anchor: bi-etl `dags/shipping_mart/fact_shipments/sql/insert_to_silver.sql` Step 8e; verified live 2026-06-19.

## ORWO is heavily consolidated
Many **order-grain shipment_ids share one physical tracking/parcel/carrier-charge**: ~**4.79 shipment_ids per UPS tracking** (April); the DAG documents 20.7% of trackings shared across 2+ orderingids, avg ~9. So any per-shipment_id weight/cost is at a finer grain than the physical shipping unit (the parcel/tracking).

## The mart's ORWO weight is per-ORDER packaging weight (mis-grained)
`fact_shipments.weight_kg` for ORWO comes from `orderdeliveryview.sendingorderingid -> orwo_usedpackaging.weightg` (per-order/sending), ~0.1-0.5 kg. That is **not** the parcel weight and is sparse (DHL 29% / UPS 25% present). `orwo_pts_parcelfinish` is joined in the same Step 8e query but used ONLY for PII - its `weight` (per tracking, ~100% all carriers) is unused.

The three weights are three grains (do NOT interchange):
- `usedpackaging.weightg` = per-order packaging (~0.1-0.5 kg) <- the mart's current weight_kg.
- `parcelfinish.weight` = per-tracking physical parcel (~2-3.4 kg, ~100% all carriers).
- invoice `billedweight`/`actualweight` = per-tracking carrier-charged weight = parcel weight rounded up to UPS 0.5 kg bands + dim weight on ~13% (+0.15 kg avg). Reconciles with parcelfinish at tracking grain.

**Consequence:** don't trust mart `weight_kg` for ORWO shipping weight. The real parcel weight is `parcelfinish.weight` ~= invoice billedweight. A naive `COALESCE(usedpackaging.weightg, parcelfinish.weight)` fix is INVALID (stamps parcel weight on order rows -> SUM over-counts ~5x). Fixing it is a per-parcel-grain weight-semantic redesign (+ SCM impact), not a source swap.

## Dims: DHL2 Paket is a true capture gap
Dims wire via `orderdeliveryview.sendingorderingid -> usedpackaging.packagingid -> orwo_packaging` (packagingid encodes L:W:H; 44-format catalog). usedpackaging match by product: **DHLKP 99%, DHL2 (Paket) 27%** - holds even allowing any sending-id. So ~73% of DHL2 Paket parcels have **no packaging-dims row at all** - a genuine upstream capture gap (Wolfen doesn't write a packaging row for that flow, or it isn't ingested), NOT a fixable warehouse join. POST/Warenpost/Kleinpaket/UPS DO have dims (wireable). Confirming whether DHL2 dims exist anywhere would need PTSLive (Oracle), no access.

Red herring corrected: `parcelfinish.sendingorderingid = fz<order#>_<ts>` is NOT the mart's key - the mart uses `orderdeliveryview.sendingorderingid` (numeric, 100% present). The drop is purely at the usedpackaging hop.

**Related:** [[shipping-mart]], [[bi-etl]], [[2026-06-19-orwo-tender-scope-and-cost-basis]], [[S266_e455d12d_orwo-box-grain-quota-estimator]], [[2026-05-28-ups-orwo-fif-data-quirks]].
