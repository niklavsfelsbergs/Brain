# S121 (dwarf) — Hermes engine doc + audit (document-as-audit pass)

**Role:** dwarf for Jebrim. **Task:** write `2_analysis/docs/technical/engines/hermes.md` per the technical README template; audit engine code vs offer + REVIEW_CONCLUSIONS + ASSUMPTIONS as a byproduct. Write ONLY that one doc + this trace.

## What I read
- `carriers/hermes/`: calculate.py, constants.py, CLAUDE.md, surcharges/{__init__,maut,peak,bulky}.py, tests/test_engine.py (31 fixtures), rates.parquet (inspected: 156 rows, 26 countries x 6 bands).
- `carriers/_base/`: surcharge.py (Surcharge ABC + in_period), supplement.py (add_sorted_dims, add_chargeable_weight), pipeline.py (apply_surcharges + eligible-gate, lookup_rate_asof, stamp_version).
- `carrier_responses_to_open_questions/Hermes/REVIEW_CONCLUSIONS.md`; `FUEL_SUMMARY.md` (Hermes row); `FULL_YEAR_SCOPING_NOTE.md`.
- `2_analysis/docs/ASSUMPTIONS.md` Hermes block (L313-348); `1_offers/picanova/Hermes/CLAUDE.md` WA #1-11 table (L146-160).
- `cost_matrix.py` (Hermes wired L74; full-year partitioned build, [[S120_3760e65b_eu-tender-full-year-build|S120]]).

## Engine snapshot
- Version `hermes-2.0.0` ([[S103_d4f287de_eu-tender-engine-rebuilds|S103]], 2026-05-27, Round-1 reply rebuild). Services: paket_de_hd (DE, 31.5 kg cap), paket_intl_hd (25 EU, 30 kg cap). HD-only; CH excluded (country_not_served).
- Billable = gross only (mode="gross", WA #1 RESOLVED, no vol-weight). Base rate: forward-asof on (service, destination_country_code, weight_kg) keyed on weight_kg (NOT billable).
- Surcharges: MAUT 0.20/parcel (both lanes), PEAK 0.25/parcel Oct-Dec on shop_order_created_date, BULKY per-destination (DE 8.85 / named intl / 57.75 default) when 120<d_max<=170 & girth<=360.
- Fuel: per-month base-2021 Destatis ladder via FUEL_PCT_BY_MONTH {1:0.0, 2:0.0, 3:0.07}, default 0.0; base-only scope; inlined so null base -> null cost_fuel.
- cost_total = base + cost_fuel + cost_maut + cost_peak + cost_bulky (fill_null(0) sum), nulled on ineligible.

## Audit findings (detail in doc §10)
1. **Stale docstring in `_decide_eligibility` (calculate.py L173-174):** comment says "over_max_length: longest dim > 200 cm" and "over_max_volume ... per WA #4" — but constant is MAX_LENGTH_CM=170.0 (tightened in 2.0.0). Code is correct (uses the constant); the inline docstring drifted. Minor, but exactly the drift this audit catches.
2. **ASSUMPTIONS.md Hermes fuel row is STALE (L320, L331):** still states "Jan ~0% / Feb ~0.5% / Mar ~11%". The engine (constants.py), REVIEW_CONCLUSIONS, and FUEL_SUMMARY all now say Jan 0 / Feb 0 / Mar ~7% (the ~11% Mar was explicitly corrected as wrong on both index and arithmetic). The post-reply ASSUMPTIONS table row was not cascaded. Material doc drift — should be fixed by principal (I cannot write ASSUMPTIONS.md anyway). Also MAX_VOLUME row says "drop" but engine keeps 450,000 as a backstop.
3. **Jan index disagreement (cosmetic):** constants.py says Jan index 122.5; REVIEW_CONCLUSIONS + FUEL_SUMMARY say 122.3. Both -> 0% (band <=122.7), so no pricing effect. Pin one number when Feb/Mar exact arrive.
4. **The "11 working assumptions" framing is itself stale post-reply.** Offer-CLAUDE WA #1-11 table still shows v1 placeholder text (WA #2/#3 "skip bulky", #7 "flat 0%", #11 "2m/450L"). 7 of the 10 Qs are RESOLVED in 2.0.0; what remains genuinely provisional is narrower: Q6 pin Feb/Mar exact + series name, Q7 volume tiers, Q8 island auto-vs-opt-in. The headline "11 provisional assumptions await Q1-Q10" overstates current openness.
5. **Feb fuel knife-edge (load-bearing, documented):** Feb index 122.7 sits exactly on the <=122.7 0% edge; a hair higher flips Feb to 0.5%. Carrier promised the Feb figure. Silently load-bearing on the full-year total if the year has Feb-heavy volume — but small per-pp (~EUR 26k/pp).
6. **PEAK never fired in Q1 but DOES fire now (full-year build, [[S120_3760e65b_eu-tender-full-year-build|S120]]).** The Q4 peak (Oct-Dec, the headline differentiator per FULL_YEAR_SCOPING_NOTE) was dead code on the Q1-only matrix; the full-year replay is the first build to exercise it. Worth flagging that the peak value (0.25) has never been load-bearing on a scored number until this build.
7. **diesel_schedule.parquet is dormant/superseded** (base-2015 ladder, no longer loaded) but still on disk — a future index-lookup activation must regenerate it on base-2021 first. Documented in code; trap noted.
8. **Reconciliation otherwise CLEAN:** MAUT 0.20 (Q9 locked), 30 kg intl cap (Q4), gross-only (Q1), returns OOS (Q5), residential 0 (Q10), bulky trigger + per-country values (Q2/Q3), fuel base-only (Q6) — all match REVIEW_CONCLUSIONS. Eligible-gate (pipeline F2) correctly stops surcharges firing on rejected rows. test_f3 intentional xfail is a correct standing guard (lookup on weight_kg while gross-only).

## Status: doc written, single file. DONE.
