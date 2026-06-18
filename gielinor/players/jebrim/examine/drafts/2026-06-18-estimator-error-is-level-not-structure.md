# An estimator's dominant error is the rate LEVEL (freshness), not the structure — validate out-of-sample before sizing a fix

Draft (2026-06-18, [[S266_e455d12d_orwo-box-grain-quota-estimator|S266]]). Self-observation, correction-backed.

**What happened.** Investigating the ORWO quota over-read, I twice asserted the immature-month cost
"reverts to ~€1.1–1.2" and the quota to ~April's level — confidently, from the mechanism. Niklavs'
"size it" then "test it" pushed me to actually validate. Out-of-sample (train one month, predict
another mature month vs ground truth) showed the **box-grain structure fix only cut the error from
~40–60% to ~28–42%** — the *dominant* residual was the **month-to-month rate level** (March ran ~30%
pricier than April), which no amount of getting the consolidation structure right touches. My
reversion-magnitude claims were over-optimistic; the locked solo cost + rate-level drift meant May
matures higher than I'd said.

**The lesson.** When proposing an estimator/model fix, separate two error sources: **structure** (does
it allocate across the population correctly?) and **level** (is the calibration anchored to the right
recent period?). A structure fix can be real and *still* leave the headline magnitude dominated by
level/freshness. Don't size the impact from the mechanism — **validate out-of-sample against ground
truth first**, and state which error source the fix actually addresses.

**How to apply.** Before claiming "this will move X by N," run a train-on-one-period / predict-another
test vs actuals. Report the residual and attribute it (structure vs level). Ties to
[[feedback_validate_refinement_through_pipeline]] / synthetic-pass-not-live-correct: a fix that
improves one stage is a hypothesis until tested through to the outcome. Anchor:
[[S266_e455d12d_orwo-box-grain-quota-estimator]].
