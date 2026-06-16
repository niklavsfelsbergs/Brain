# A standalone cost estimator under-counts the hard cases — get the number from the real build

**Observation ([[S245_3172630e_eu-tender-no-hermes-routing-ops-coherence|S245]], sid8 3172630e).** I told the principal the routing-smoothing cost was
"~€6k/yr, basically free" off a standalone `cost_check_smoothing.py`. When I baked the smoother
into the real `build_final.py` and diffed `routed_total`, the authoritative figure was **~€39k/yr**
— 6× higher. The estimator had scored the cells it couldn't fold cleanly ("unservable") as €0;
the real serve-aware smoother actually moves them, at real cost. I'd green-lit the principal on the
cheap number before the real build existed.

**Why it matters.** A standalone estimator encodes its own simplifying assumptions (here: leave the
hard folds uncosted). Its number is a hypothesis, not the cost. The instrument that *is* the
decision — the production builder's own `routed_total` delta — is the only authoritative figure,
because it can't silently drop the cases it doesn't know how to price.

**How to apply.** When a change has a cost/impact number, prefer the figure from the *real* pipeline
run over a side-estimate — and when only the estimate exists, label it an estimate and flag that the
authoritative number comes from the build. If the estimate fed a principal decision, re-state the
real number the moment it lands, even if it changes the story (it did: "free" → "~4-5% of saving").

Instance of [[synthetic-pass-not-live-correct]] / verify-the-thing. Anchor: the cost-check vs
build-delta gap, [[S245_3172630e_eu-tender-no-hermes-routing-ops-coherence|S245]].
