# Non-ORWO SCM `expected`-vs-invoiced understatement — known + parked (engine-fill is the fix)

**Date:** 2026-06-19 · **sid8:** c1ecf686 · **Quest:** [[S278_c1ecf686_non-orwo-expected-understatement]] · traces: `quest-log/traces/S278_shipagent_non-orwo-expected-understatement.md`, `S278_shipagent_non-ups-may-residual.md`

## The finding (gold `shipping_mart`, non-ORWO/TCG, order-month lens)

On a **like-for-like** residual — real cost vs the `expected_shipping_cost_eur` the model assigned to the **same invoiced rows** — non-ORWO runs **+5% to +7.4% on mature months** (Jan–May; May 1.073×). It is real (grows on mature months, not a maturity-selection artifact) but **moderate, not "much higher"** — the "much higher" read comes from the immature-June or full-population blend.

**It's a tail, not a level problem.** The flat per-country `expected` model (`update_fact_shipments_cost.sql` Pass 2a.5 + the `AVG(real)/AVG(expected)` Pass 2a.6 calibration) is **dimension- and surcharge-blind by construction**, so it prices the ordinary ~97% essentially perfectly (0.997–1.01×) and misses on the dispersion:

- **Oversize / large-package + additional-handling surcharges** — ~3% of volume carries **88%** of the residual (April oversize slice 1.74×, May 1.98×). Canvas geometry (long/flat, busting envelope second-sides) is the physical driver.
- **Fuel surcharge** — rides the same surcharge-heavy parcels. **UPS alone = 42% of the residual** (fuel + oversize).
- **DPD UK lane** — broad under-pricing, **1.46×** even on plain (non-oversize) parcels; ~32% of the *non-UPS* May residual. A rate-card calibration miss, not a tail.
- **Missing-rate lanes** — Australia runs real/expected ≈ **21×** (no per-country rate entry); small money, structural.
- Market: **US is best-calibrated** (1.005×); the miss is EU + the rest-of-world rate holes.

## The decision (Niklavs, 2026-06-19)

**Keep `expected` as-is.** Do not patch it now — when the carrier tenders close, the **re-rating engine fills `expected`** with per-shipment, surcharge/dimension-aware costs, which kills the dispersion at the root. A flat scalar (×1.04 / ×1.07) is the **wrong shape**: it fixes the aggregate mean while leaving the hot tail (UPS oversize ~2×, DPD UK 1.46×) under-priced and pushing the already-correct 97% into over-estimating — and SCM is a per-corridor monitor + alert engine, so a right-total/wrong-parts estimate mis-baselines the alerts. The multiplier also isn't stable (Feb 1.026 → Apr 1.074), so no single constant is right even for the headline.

**Status: parked.** Trigger to revisit = tender close + engine-fill of `expected`.

## Open thread (non-blocking, for whoever builds the engine-fill)
- Verify whether Pass 2a.6's calibration writes back to the stored `expected` on **invoiced** rows or only the uninvoiced fallback rows — decides whether the live dashboard's expected-basis is already partly corrected or running raw.

## Related
- Sibling: [[2026-06-18-ups-carrier-expected-cost-multipliers]] (the per-carrier multiplier scan — same defect, scalar-fix framing the engine supersedes); the ORWO box-grain estimator ([[orwo-ups-de-cost-increase-resume__64902bef]] arc) is the ORWO-side analogue.
- Domain: [[scm]] (`expected` model + cost basis), [[shipping-mart]] (order-month quota lens, package-dim gate), [[carrier-contracts]].
- Lesson: [[2026-06-19-immature-month-mart-cost-is-estimate-dominated]] (split by `cost_source` before attributing a recent-month move).
