# Shipping-agent dwarf — received_by_carrier_ts event-nature audit

**Spawned by:** Jebrim · **sid8:** fad915ee · **Date:** 2026-06-10
**Brief:** Empirical (behavior-first) audit of what `received_by_carrier_ts` on gold `fact_shipments` actually is per carrier — physical scan vs manifest/label echo. Gold contract, 2026 data. Parallel agent traces pipeline lineage; this trace = behavioral evidence.

**Scope used:** gold `shipping_mart.fact_shipments` only. Population = rows with `received_by_carrier_date` in 2026-01 (320k rows; used as the selective driver filter — `truckload_closed_ts >= '2026-01-01'` timed out the MCP, `received_by_carrier_date` did not). Per `shipping_provider_group`.

## Turn-by-turn
- Confirmed produced/label cols exist: `order_produced_ts`, `production_order_created_ts`, `truckload_assigned_ts`, `truckload_closed_ts`. known-dq already carries the linehaul precedent (truck departure modeled ~3.9h AFTER received).
- Test 1 (downstream): received vs truck-close is NEGATIVE for EVERY carrier (mean −0.9 to −2.2h on the EU workhorses), concentrated in the −6..0h bucket. NO carrier shows received as a genuinely-later hub/downstream event. Pattern holds across all 12.
- Test 2 (production tracking): received − order_produced is LOOSE (means 18–82h, wide spread 0→72h+). Received does NOT track production tightly → not a simple label-print echo. It tracks truck-CLOSE tightly (−1.6h), not production.
- Test 3 (granularity/batch): splits carriers into two regimes. DPD UK = hard manifest batch (24,669 rows / 43 distinct stamps; one stamp = 2,153 parcels; whole-second; 07:00–13:00 UK business window). USPS 67% whole-sec, FedEx 93% whole-sec = coarse/feed. Maersk/DB Schenker/Yodel/Direct Link = 18–25 rows/stamp (batch). OnTrac = 60 distinct sub-sec values/hr, evening-peaked = genuine per-parcel scans. Asendia USA = received BEFORE production on 100% of rows = broken/misaligned, values not trustworthy.

## Headline verdict
`received_by_carrier_ts` is NOT a downstream hub scan for any carrier — it is an at-origin event tied to truckload-close, and its SOURCING is carrier-heterogeneous: manifest/EDI batch for DPD UK + Maersk + DB Schenker + Yodel + Direct Link + (coarse) USPS/FedEx; per-parcel near-origin scan for OnTrac; intermediate (sub-second, ~10/stamp) for DHL/UPS/DPD Poland. Asendia USA suspect (pre-production stamps). Jebrim's hypothesis confirmed: an at-origin timestamp is unrealistic as a physical hub scan, and for the batch carriers it is demonstrably a manifest handover, not a scan.

**Deliverable:** chat-only (data returned to Jebrim).
**Open:** Asendia USA pre-production timestamps = a real DQ flag worth a known-dq note (maintainer-gated). Per-carrier verdict may warrant a known-dq addition on received_by_carrier provenance.
