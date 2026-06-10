# Shipping-agent pull — "linehaul time" derived-signal sanity (2026)

**Spawned by:** Jebrim. Follow-on to the truck-scan coverage pass.
**Brief:** Construct linehaul_time = (carrier first scan) − (truck close); judge if it makes sense as usable data for 2026. DQ/sanity verdict, not a metric request.
**Tier:** gold-contract (no upstream reach needed — both timestamps live on the gold fact).
**Date:** 2026-06-10.

## Turn-by-turn
- Confirmed both timestamps live on the gold fact (`fact_shipments`). Truck-close = `truckload_closed_ts` (+ `truckload_assigned_ts` = onto-truck, `truckload_id`). Carrier first scan = `received_by_carrier_ts` — a SINGLE unified column, NOT the per-carrier heterogeneous set the warm context expected. Upstream per-carrier scans are already unified into this field in the mart.
- Anchored on `truckload_closed_ts` in 2026. Population = parcels with a truck-close (1,232,710).
- Join coverage: 99.8% of truck-closed parcels also have a carrier first scan. Coverage is NOT the blocker.
- CORE FINDING: 99.30% of computed durations are NEGATIVE (carrier scan recorded BEFORE truck close). Universal across every site (97–100% neg) and every carrier (95.5–100% neg). No usable subset.
- Diagnosed semantics: `received_by_carrier_ts` sits ~+1.7h after onto-truck-scan but before truck-close (close is +5.0h after assigned). It's an at-origin carrier intake/handover event, not a downstream linehaul-leg scan. `delivered_by_carrier_ts` − `received_by_carrier_ts` averages clean +80h with 0.03% inversions → confirms received_by_carrier is the early origin event.
- Robustness: anchoring on `order_produced_date` instead gives same picture (99.3% neg). Not an anchor artifact.

## Verdict
(c) NOT usable yet. The defect is a definitional/event-ordering mismatch, not coverage and not a clean fixable offset (negatives spread -1.5h to -1000h+). The two timestamps bracket the SAME origin handover; subtracting them is not a transit leg.

## Tools / SQL notes
- MCP validator rejects `DATEDIFF(<unqualified datepart>, ...)` and `MEDIAN()` (window-only). Workaround: `(EXTRACT(EPOCH FROM a) - EXTRACT(EPOCH FROM b))/3600.0` for hour deltas; bucket-count CASE sums for percentile-shaped reads. Direct `ts - ts` subtraction returns a corrupted interval — don't use.

Full report returned to Jebrim in chat (data for him, not a user-facing note).
