---
quest: S188_truck-scan-linehaul-dq
sid8: fad915ee
ts: 2026-06-10 00:00
open_dep: Niklavs to pick SLA basis (empirical percentile vs carrier contractual) — gates whether the raw TRANSIT-scan decomposition is worth running
---

# Resume — truck-scan / linehaul / `received_by_carrier_ts` DQ

**Status:** in-progress (core questions answered + delivered; one principal-gated follow-up open).

**Where we are.** Investigated truck-scan coverage per site (PCS PL ~93% / CMH ~29% / PX ~0% / Wolfen+external 0% by design) and the nature of `received_by_carrier_ts` (a real carrier OUTBOUND movement scan at our origin dock, NOT a label-print echo; batch-shaped for most carriers, true per-parcel only for OnTrac; Asendia USA broken). Linehaul-as-defined (received − truck-close) is 99.3% negative because both bracket the same origin handover. Delivered the SLA-comparability reasoning: received→delivered bundles linehaul + carrier transit and can't currently be split (mart collapses the intermediate `TRANSIT` scan into the `MIN`).

**Next concrete step (blocked on principal).** Ask Niklavs: **which SLA** — your empirical percentiles (`dim_carrier_sla_v1.xlsx`, same basis → already comparable) or the carriers' contractual promises (injection-based → not comparable, runs long by linehaul)? If contractual → spawn a probe of raw `pict_shipmentlogs` / `picaapi_shipment_trackings` to test whether a usable downstream between-facilities `TRANSIT` scan exists per carrier, so we can isolate linehaul and produce a contractual-SLA-comparable carrier-transit number (carrier precision permitting).

**Files / paths to read first.**
- `quest-log/in-progress/S188_fad915ee_truck-scan-linehaul-dq.md` (full findings + the 4 sub-agent traces)
- `bank/drafts/notes/projects/2026-06-10-received-by-carrier-scan-semantics-and-truck-scan-coverage.md` (harvested domain knowledge)
- domain digests: [[shipping-mart]], [[production-times]]
- maintainer doc fixes (shipping-agent repo + bi-etl `README.md:140`) noted in the quest entry

**Pending drafts:** none beyond the harvest note above.
