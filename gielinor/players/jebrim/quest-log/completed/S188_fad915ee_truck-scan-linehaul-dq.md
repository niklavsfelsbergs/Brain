# S188 — Truck-scan coverage + linehaul-time / `received_by_carrier_ts` DQ investigation

**Player:** Jebrim · **Session:** fad915ee · **Opened:** 2026-06-10
**Shape:** investigation, delivered conversationally. 4 sub-agents (3 shipping-agent, 1 bi-etl-trace dwarf). No build artifact; findings harvested to a bank draft.

## Ask (evolved across the session)

1. Truck-scan data quality — parcel coverage of truck-scan data per production site.
2. If we incorporate linehaul time (truck close → carrier first scan), does the data make sense for 2026?
3. Operational reality check: do carrier tracking events fire at the carrier's hub, or when we print a label / at our facility? Is `received_by_carrier_ts` a real scan?
4. Reasoning toward: full transit (incl. linehaul) vs carrier SLA comparability.

## What we found (the picture, stable)

**Truck-scan = internal PCS truckload chain**, surfacing on `shipping_mart.fact_shipments` as `truckload_id` (+ `truckload_assigned_ts` = onto-truck scan, `truckload_closed_ts` = truck closed). Coverage by site, Q1'26: **PCS PL ~93%, PCS CMH ~29%, PCS PX ~0%** (the flag — PCS-owned but unwired), Wolfen + external producers 0% **by design** (no internal truck leg). Blended ~51% is a mix artifact (Wolfen's large 0% denominator) — read per-site only. Signal is genuinely measured (PX ~0% vs PL ~93% spread rules out default-fill).

**`received_by_carrier_ts` is a real carrier movement scan, but an ORIGIN one — and batch-shaped for most carriers.** Lineage (bi-etl trace, file:line proof): gold ← `insert_to_silver.sql` `MIN(event_ts) WHERE event IN ('OUTBOUND','TRANSIT','PICKED_UP')` ← bronze `pict_shipmentlogs` / `picaapi_shipment_trackings` ← Picturator/PicaAPI app shipment-event logs. `LABEL_CREATED` is a **distinct event deliberately excluded** → it is NOT a label-print echo (Niklavs' worry is unfounded). `OUTBOUND` = "left origin facility" + `MIN` = earliest event → it fires at our dispatch dock, before our linehaul to the carrier hub. PICT + PicaAPI only; **ORWO/PCS/Rewallution NULL by design** (no carrier stream; ORWO `sentat` routed to `order_produced_ts`).

**Per-carrier event-nature (behavioral probe, Jan'26):** OnTrac = genuine per-parcel scan (1.7 parcels/stamp). DPD UK = hard daily manifest batch (2,153 parcels on one `07:50:50` stamp). DHL/UPS/DPD PL = near-origin handover, batched ingestion (~10/stamp). Maersk/DB Schenker/Yodel/Direct Link/USPS/FedEx = manifest batch. **Asendia USA = broken** (received stamped *before* production on 100% of rows — do not use). Trustworthy in aggregate (cohort/carrier-level); not per-parcel for the batch carriers.

**Linehaul verdict (why the as-defined metric fails):** `received_by_carrier_ts − truckload_closed_ts` = **99.3% negative** because both timestamps bracket the *same* physical moment (origin handover at our dock). They are not the two ends of a leg. Join coverage is fine (99.8%), tail bounded — the defect is definitional, not coverage. Field only populates from ~2025-10-24.

**SLA-comparability reasoning (delivered, not yet verified):** received→delivered bundles **our linehaul + carrier transit** and can't currently be split (the mart collapses the intermediate `TRANSIT` "between-facilities" scan into the same `MIN`). Comparability depends on **which SLA**:
- Empirical percentile SLA (`dim_carrier_sla_v1.xlsx`, p85/p90/p95, built from our own received→delivered) → same basis → comparable as-is.
- Carrier *contractual* SLA → typically clocked injection-at-carrier-hub → delivery → our number runs long by the linehaul → **not** directly comparable.

## Sub-agent traces (this session)
- [[shipping-agent_truck-scan-coverage-by-site__dwarf]]
- [[shipping-agent_linehaul-time-sanity__dwarf]]
- [[shipping-agent_received-by-carrier-event-nature__dwarf]]
- [[dwarf_received-by-carrier-lineage-trace]]

## Harvest
- Bank draft: `bank/drafts/notes/projects/2026-06-10-received-by-carrier-scan-semantics-and-truck-scan-coverage.md` (the reusable domain knowledge — touches [[shipping-mart]] + [[production-times]]).

## Pending external actions
None pending. (Read-only mart pulls + repo trace; no writes outside the brain.)

## Open / next (the live thread Niklavs deferred at wrap)
- **Niklavs to answer: which SLA basis** — your empirical percentiles, or the carriers' contractual promises? Determines whether a linehaul mismatch even exists.
- If contractual: **test the raw `TRANSIT`-scan decomposition** — does `pict_shipmentlogs` / `picaapi_shipment_trackings` carry a usable downstream between-facilities scan per carrier, so we can split `received → [carrier injection] → delivered`, isolate linehaul, and produce a contractual-SLA-comparable carrier-transit number? (Carrier precision permitting — only OnTrac had per-parcel granularity.)
- Maintainer-gated doc fixes surfaced (shipping-agent repo, not the brain): `reference/tables.md` stale (missing `truckload_*`, `received_by_carrier` semantics); `reference/known-dq.md` should note the batch-vs-scan per-carrier split + the Asendia-USA-broken flag; bi-etl `README.md:140` stale (claims ORWO sources received from `sentat`).
