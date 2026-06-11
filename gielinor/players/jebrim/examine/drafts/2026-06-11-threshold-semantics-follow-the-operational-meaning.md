# Threshold semantics follow the operational meaning, not the mechanical comparison

**Observed:** [[S203_021047a4_q09-baseline-bridge|S203]] (q09). First cut of the minimum-saving switch threshold gated every
keep-vs-engine comparison. The grid then showed 90% of "parked" parcels at T=1% were
**same-family flips** (DHL keep → DHL tender terms) — no parcel physically moves there, so
gating them foregoes savings while reducing zero churn. The rule the principal wanted
("don't move thousands of parcels for pennies") is about *carrier switches*; the mechanical
keep-vs-bid comparison is wider than that. Fixed to cross-family-only before pinning the value.

**Companion catch, same session:** the sensitivity grid estimated the 2% threshold's cost
at €5.6k/yr, but the live build showed €11.4k — the grid priced only the peak-free margin
and missed that parked UPS parcels keep paying UPS's Q4 peak. A sensitivity estimated on
one component is a hypothesis; the build's own diagnostic is the ground truth to report.

**Rule:** before pinning a threshold/gate parameter, restate the rule in operational terms
(what physically changes when it fires?) and check the gated set for members where nothing
changes — those don't belong under the gate. And cost the gate through the full pipeline
(all cost components), not just the term the gate compares on.
