# S034 F2 -- surcharge eligibility gate (dwarf hand-off)

**Spawned by:** Jebrim (principal), S034 -- EU tender remediation
**Role:** dwarf
**Date:** 2026-05-22
**Status:** complete; ready for principal review

## What I did

Gated surcharge cost columns in `_base/pipeline.py` against the engine-emitted `eligible` flag so always-on surcharges no longer write their `cost_<name>` value on rejected rows.

## Design choice: 0.0, not NULL

Picked **0.0** for ineligible-row `cost_<name>`. Reasoning:

1. **Existing convention.** The pre-fix `_apply_single` already wrote `0.0` on `surcharge_<name> == False` rows (the `.otherwise(pl.lit(0.0))` branch). The per-carrier test fixtures (`carriers/<x>/tests/fixtures.py`) all default `expected_cost_<surcharge> = 0.0` for rejection rows. The gate just extends "didn't fire" to also mean "row is ineligible."
2. **Dtype stability.** Float64 stays Float64. NULL would mix null/float in the same column and force `fill_null(0.0)` calls on every downstream reader.
3. **Aggregation cleanliness.** Component-level sums (bias table, per-component pivots) sum 0.0 cleanly without nullable arithmetic.

`cost_total_eur` stays NULL on ineligible rows (unchanged -- that's `_finalize`'s contract per engine, and 0.0 there would falsely read as "this shipment cost zero").

## Empirical finding -- the bug was latent, not active

I scanned every always-on surcharge in the codebase. **All current always-on surcharges already self-gate via `pl.col("base_rate_eur").is_not_null()`**, and `_decide_eligibility` nulls `base_rate_eur` on rejection rows. So the engines were dodging the bug via a per-surcharge convention.

Pre-fix and post-fix per-carrier `sum(cost_total_eur)` are identical to sub-cent precision (`max |delta| = 0.000023 EUR` across 9 carriers, 528,721 shipments). The brain's `bias table over-counts` concern was real in the abstract, but the parquet on disk was already correct.

**The fix is therefore defensive.** It moves the `eligible` guard from a surcharge-author convention into the pipeline contract, so a future author who forgets the `base_rate_eur.is_not_null()` boilerplate doesn't reintroduce the bug. If `apply_surcharges` is called on a df without an `eligible` column, behaviour is identical to pre-fix (backward compatible).

## Files touched

- `2_analysis/carriers/_base/pipeline.py` -- added `_eligible_gate(df)` helper; `_apply_single` and `_apply_exclusive_group` now AND it into the surcharge condition; docstring on `apply_surcharges` updated.
- `2_analysis/carriers/_base/tests/__init__.py` -- new (empty) package marker.
- `2_analysis/carriers/_base/tests/test_eligible_gate.py` -- new. 4 tests, all pass via both `pytest` and the `python -m` script entry point. Tests cover: standalone always-on surcharge gated; exclusivity group resolves no winner on ineligible row; no-`eligible`-column back-compat; eligible-row sanity.
- `2_analysis/docs/DECISIONS.md` -- 2026-05-22 entry appended (newest at top, above the F1 entry).

## Ad-hoc verification scripts left in place

Two scratch scripts I wrote to verify totals; could not delete (the brain's `block-deletes` hook fires from this dwarf even though the path is outside `gielinor/`). They're harmless and underscore-prefixed:

- `2_analysis/_s034_f2_verify_totals.py` -- compares per-carrier `cost_total_eur` sums between the on-disk pre-fix parquet and in-memory post-fix engine output. Confirms `max |delta| = 0.000023 EUR`.
- `2_analysis/_s034_f2_verify_components.py` -- attempts to show a non-zero -> zero flip on `cost_overpack` for ineligible rows; ran and found old parquet already had 0.0 there (because of Maersk's self-gate). Documented the surprise rather than discarded it.

Principal can decide whether to keep or prune (these are not committed via me -- the dwarf doesn't commit).

## Test status

- **New `test_eligible_gate.py`:** 4 / 4 PASS via pytest; 4 / 4 PASS via `python -m`.
- **All 9 carrier engine fixture suites:** Maersk 14/14, GLS 21/21, Guell 17/17, DHL Paket 20/20, DHL Express 17/17, Austrian Post 14/14, FedEx 25/25, DPD PL 19/19, Hermes 19/19 -- **166 fixtures, zero regressions**.
- **No fixtures surfaced bugs.** Maersk's ineligible-row fixtures (`AT_HD_35kg_over_max_weight`, `CH_HD_over_dim_no_surcharge_rejected`, `KP_country_not_served`) already encoded `expected_cost_overpack = 0.0` -- they were green before and stay green now. The fixture set was already correct.
- **Pre-existing pytest failure unrelated to F2:** `carriers/austrian_post/tests/test_f3_billable_lookup.py::test_f3_regression_signal` fails by design (intentional regression signal for the F3 bug, separate work item). Confirmed it's not my problem to fix; left untouched.

## Cost matrix rebuild

`python cost_matrix.py` runs all 9 engines successfully and computes the 4,758,489-row matrix in memory, then OOMs at `sink_parquet` (a Polars allocation issue on this box, not caused by my change). The on-disk `data/cost_matrix.parquet` remains the pre-fix artefact. Per-carrier totals verified unchanged via the in-memory script -- the headline doesn't move. A clean rebuild can wait until the bias-table consumer actually needs it on a fatter box.

## Hand-off to Jebrim

Three things for principal review:

1. **Read DECISIONS.md 2026-05-22 F2 entry** -- the prose explains why the fix is defensive and why headline totals didn't move.
2. **Decide on the two `_s034_f2_*` scripts** in `2_analysis/` -- keep as reproducible verification, archive somewhere, or prune.
3. **The cost_matrix.py OOM is unrelated** but should probably be tracked separately (a polars `sink_parquet` memory issue) -- maybe a §9 follow-up.

Nothing surprising for the F1/F2/F3 audit narrative: F2 cleans the contract; the magnitude of `cost_total_eur` movement is zero because every current always-on surcharge already had the per-surcharge guard. The fix is a defensive tightening, not a number-changer.
