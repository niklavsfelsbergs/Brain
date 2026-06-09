# DPD-PL `dpd_pl_current` engine is export-only — the carrier-only slice is a model gap, not a misfit

**Context.** EU-tender routing report (`routing_2026q1`), DPD-PL card shows three product buckets: Dpd Direct Home 80,583 · Dpd Mix Home 6,515 · **carrier-only 1,887** (of 88,985 total).

## What "carrier-only" means here

A routed parcel with **null `service`** — the modeled rate engine produced no *named* product for it, so it renders as "carrier-only" and is costed at **actuals** (`today_eur`, real Q1 invoice) rather than a modeled rate. It is **not** a physical misfit: all 1,887 have `cur_inc = dpd_pl` (verified) — they actually shipped via DPD-PL. The routing *keeps* them on DPD at actual cost (the "keep" path, `build_final.py:96-107`), because DPD was their dominant incumbent and holding at actuals beat any qualifying engine bid.

## Why the engine can't price them (verified `reject_reason`, cost matrix)

The `dpd_pl_current` engine (`carriers/dpd_pl_current/calculate.py`) models only DPD's **two export HOME services**: `dpd_direct_home` (6 countries AT/DE/FR/BE/LU/NL) + `dpd_mix_home` (29 countries), eligibility capped at **33 kg billable**. The 1,887 split into exactly two reject cohorts:

- **1,806 (96%) — `country_not_served`, all destination PL.** **Poland-domestic is in neither rate table.** The engine is *export-only*; DPD-PL's home-turf domestic-Poland product is not modeled at all. These PL→PL parcels are the most natural DPD shipment there is, yet have no modeled rate.
- **81 (4%) — `over_max_weight`.** Light actual weight (median **4 kg**) but **dimensional weight 33.5–34.4 kg** — bulky-by-volume parcels where billable (L×W×H ÷ divisor) exceeds the engine's **33 kg cap**. Contract treats >33 kg as branch-collect/return.

Zero are `over_max_girth` / `over_max_length` / `no_rate_found`.

## Coverage gap (follow-up candidate)

**1,806 domestic-PL parcels have no modeled DPD rate** — a gap in the *engine* (export-scoped), not the operation. If domestic Poland becomes a lane to re-rate / model savings on, `dpd_pl_current` needs a **PL-domestic rate table** added. Until then this slice is honest-but-unmodeled (carried at invoiced cost; totals stay correct, only the service label is missing).

## Anchors

- `carriers/dpd_pl_current/calculate.py` `_decide_eligibility` (the 5 reject reasons) + `constants.py` (DIRECT_COUNTRIES / MIX_COUNTRIES / 33 kg cap).
- `routing_2026q1/build_final.py` keep-path (96-107) + per-parcel service join (168-177); `service_labels.py` (`None → carrier-only`).
- Verified 2026-06-09 against `cost_matrix_2026q1` + `routing_assignment.parquet`.

Related: [[2026-06-09-routing-cost-basis-decisions]] · [[eu-tender]] domain digest · [[2026-06-09-carrier-invoice-dimension-coverage]]
