# Coverage-gate a calibrated estimate per segment — never fabricate from a global fallback where a segment has ~no actuals

Draft (2026-06-18, [[S266_e455d12d_orwo-box-grain-quota-estimator|S266]]). Self-observation, caught-in-build.

**What happened.** The first run of the box-grain quota estimator applied to *whole* ORWO produced a
quota HIGHER than the dashboard — the opposite of the intended correction. Diagnosing per carrier
family exposed it: **OTHER** carriers (GUELL/Maersk/etc.) have ~€572 of actual cost (production leaves
them uncosted by design, open-pointer 8), but my estimator fabricated **€26,750** for them — because
with no own-segment rate it fell through to a **global box-rate fallback**. **POST** (1% invoiced) was
similarly mis-calibrated from a biased 1%-sample. The fix was a **coverage gate**: apply box-grain only
to families with enough of their own invoiced data to calibrate (UPS, DHL), and **keep the production
estimate for segments that can't be calibrated from actuals** (POST needs a contracted rate; OTHER stays
uncosted).

**The lesson.** A calibration/estimation model run over a **heterogeneous population** is only valid per
segment where that segment has enough ground truth. A global/fallback rate applied to a near-empty
segment doesn't degrade gracefully — it **fabricates**. Always coverage-gate per segment and let
un-calibratable segments pass through unchanged rather than inventing a number.

**How to apply.** Before trusting an aggregate from a calibrated model, break it by segment and check
each segment's calibration coverage. Gate (don't fallback-fill) segments below the floor; surface them
as a separate structural gap. Ties to [[feedback_dont_generalize_from_single_verified_case]] and the
populated-column-is-not-a-measurement family. Anchor:
[[S266_e455d12d_orwo-box-grain-quota-estimator]] (per-family May table; OTHER €572 vs €26,750).
