# `received_by_carrier_ts` semantics + truck-scan coverage (timing signals on `fact_shipments`)

**Source:** [[S188_fad915ee_truck-scan-linehaul-dq|S188]] (2026-06-10). Domain: [[shipping-mart]] timing signals, feeds [[production-times]]. All numbers Q1/Jan 2026, gold contract.

## Truck-scan = internal PCS truckload chain
Surfaces on `shipping_mart.fact_shipments` as **`truckload_id`** (+ `truckload_assigned_ts` = onto-truck scan, `truckload_closed_ts` = truck closed/departed). NOT `fact_truck_charges` (that's linehaul *cost*). A non-null `truckload_id` = parcel scanned onto an internal truckload at its origin site. None of these three are in the stale `reference/tables.md` (2026-05-25) — they're live on the fact.

**Coverage by production site (Q1'26), = share with non-null `truckload_id`:** PCS PL (Szczecin) ~93% · PCS CMH ~29% (genuine partial, stable across months) · PCS PX ~0% (PCS-owned but effectively unwired — the DQ flag) · Wolfen + external producers (Allcop, LaserTryk) **0% by design** (no internal truck leg). Blended (~51%) is a mix artifact dominated by Wolfen's 0% denominator — **read per-site only**. Genuinely measured, not default-filled (the PX-0% vs PL-93% spread proves it; `truckload_id` and its timestamp are perfectly co-populated per site/month).

## `received_by_carrier_ts` — a real carrier scan, but an ORIGIN one, batch-shaped
**Lineage (bi-etl):** gold ← `dags/shipping_mart/fact_shipments/sql/insert_to_silver.sql` = `MIN(event_ts) WHERE event/status IN ('OUTBOUND','TRANSIT','PICKED_UP')` per trackingnumber ← bronze `enterprise_bronze.pict_shipmentlogs` (event/`timestamp`) + `picaapi_shipment_trackings` (status/`tracking_time`) ← Picturator / PicaAPI app shipment-event logs (federated app DBs).

- **NOT a label-print echo.** `LABEL_CREATED` is a distinct event in the same stream, **deliberately excluded** from the rule. If it were a label/manifest pseudo-event it would key off LABEL_CREATED — it explicitly doesn't.
- **It's an origin event.** `OUTBOUND` = "left origin facility" + `MIN` (earliest) → fires at our dispatch dock, clamped near `truckload_closed_ts`, *before* our linehaul to the carrier hub. Source doc: "first entered the carrier network / left the production site."
- **Population:** PICT + PicaAPI only. **ORWO/PCS/Rewallution NULL by design** (no carrier stream; ORWO `sentat` → routed to `order_produced_ts`, not here). Field only populates from **~2025-10-24** → inherently a 2026-forward metric.
- **Per-carrier event-nature** (the trust split — aggregate-OK, not per-parcel for batch carriers): **OnTrac** = genuine per-parcel scan (1.7 parcels/stamp, continuous, US-evening peak). **DPD UK** = hard daily manifest batch (2,153 parcels share one `07:50:50` stamp). DHL/UPS/DPD PL = near-origin handover, batched ingestion (~10/stamp). Maersk/DB Schenker/Yodel/Direct Link/USPS/FedEx = manifest batch. **Asendia USA = BROKEN** — received stamped before production on 100% of rows; do not use Asendia received/transit times.

## Why "linehaul time" as (received − truck-close) fails, and the SLA-comparability rule
`received_by_carrier_ts − truckload_closed_ts` = **99.3% negative** — the two timestamps **bracket the same physical moment** (origin handover at our dock), not the two ends of a leg. Join coverage 99.8%, tail bounded → definitional defect, not coverage. (Cross-check: `delivered − received` = clean +80h, 0.03% inversions, well-ordered.)

**Consequence for transit-vs-SLA:** received→delivered bundles **our linehaul + carrier transit** and **can't currently be split** — the mart collapses the intermediate `TRANSIT` ("between facilities") scan into the same `MIN` as OUTBOUND. So:
- vs **empirical percentile SLA** (`dim_carrier_sla_v1.xlsx`, built from our own received→delivered) → same basis → **comparable as-is**.
- vs **carrier contractual SLA** → typically clocked injection-at-carrier-hub → delivery → our number runs long by the linehaul → **not directly comparable**.

**Path to a true carrier-transit (contractual-comparable) number:** the raw streams likely carry a distinct downstream `TRANSIT` scan that the gold `MIN` hides. Probing `pict_shipmentlogs` / `picaapi_shipment_trackings` for a usable per-carrier between-facilities scan would let us split `received → [carrier injection] → delivered`, isolate linehaul, and clock carrier transit on the contractual basis — carrier precision permitting (only OnTrac is per-parcel).

## Generalizable
Before differencing two timestamps for a duration, confirm they sit at **different points in the process** — a near-zero/negative result is the tell that they bracket the *same* event (sibling of [[2026-06-09-populated-column-is-not-a-measurement|populated ≠ measured]]). And a populated, well-ordered carrier timestamp can still be a coarse daily batch, not a per-parcel scan — trustworthy in aggregate ≠ trustworthy per shipment.
