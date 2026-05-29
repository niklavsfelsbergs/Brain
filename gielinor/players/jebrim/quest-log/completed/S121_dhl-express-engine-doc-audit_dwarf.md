# S121 (dwarf) — DHL Express engine doc + audit (document-as-audit pass)

**Role:** dwarf for Jebrim. **Task:** write `2_analysis/docs/technical/engines/dhl_express.md` per the technical README template, audit code vs REVIEW_CONCLUSIONS as a byproduct.

## What I read
- `carriers/dhl_express/`: calculate.py, constants.py, CLAUDE.md, surcharges/{__init__,demand,nonconveyable,remote_area,oversize,overweight}.py, tests/test_engine.py, fixtures.py (26 fixtures).
- `carriers/_base/`: surcharge.py (Surcharge ABC + in_period), supplement.py, pipeline.py (apply_surcharges, lookup_rate_asof, stamp_version).
- `carrier_responses_to_open_questions/DHL_express/REVIEW_CONCLUSIONS.md`; `FUEL_SUMMARY.md` (DHL air/road rows).
- `docs/ASSUMPTIONS.md` DHL Express block (lines 255-307).

## Engine snapshot
- Version `dhl_express-2.0.0` ([[S104_e50113ed_eu-tender-engine-rebuilds|S104]], 2026-05-27). Services: express_worldwide (TDI air), economy_select (DDI road), HD-only, fuel-aware cheapest-pick.
- Surcharges: OVERSIZE, OVERWEIGHT(never fires), NONCONVEYABLE(weight band, OSP excl), DEMAND(Jan1-Feb16 window), REMOTE_AREA + flat pickup-line-haul alloc + customs=0.
- Two-phase fuel: per-CW pct × (base + oversize/overweight/nonconveyable/remote/demand). Pickup excluded (road fuel baked in).

## Audit findings (detail in doc §10)
1. NONCONVEYABLE keys on ACTUAL `weight_kg`; over_max_weight reject keys on BILLABLE. A dim-dominant parcel (actual ≤70, billable >70) rejects before NC can fire — correct, but the asymmetry (NC=actual, overweight/cap=billable) is undocumented in code comments. Minor.
2. DEMAND window via `in_period` is month/day only (year-agnostic). Correct for the all-2026 replay; would MISFIRE if population ever spans years (e.g. CW2025 tail dates in fuel bands suggests cross-year data is contemplated). Latent bug if scope widens.
3. Shape-branch non-conveyable un-modelled (no mart shape signal) — documented/accepted, but a true gap (poster tubes). Re-confirm tail size.
4. Pickup denominator PICKUP_ELIGIBLE_PARCELS=184273 baked as a constant; couples the engine to one population snapshot. If population.parquet regenerates, allocation drifts silently. Flagged in code but worth a rebuild-trigger note.
5. CLAUDE.md cites remote list "108,755 rows" / "85,661 ranges / 317,414 points" but rate-tables README row says "317,414 points"; constants comment says "108k". Numbers are consistent across docs once you separate raw-list / ranges / expanded-points. No drift — clarified in doc.
6. Constants reconcile to REVIEW_CONCLUSIONS: fuel TDI ~30 / DDI ~18, scope base+surcharges, oversize 10/6, customs 0, emergency 0, residential 0, non-conv 20/12, remote 0.50 min 24 — all match. Clean.

## Status: doc written, single file. DONE.
