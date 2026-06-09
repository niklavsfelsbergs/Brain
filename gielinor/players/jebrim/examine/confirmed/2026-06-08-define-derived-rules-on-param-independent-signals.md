# Define derived rules on param-independent signals (or defer them)

**Observed:** S163 UPS Phase-2 build (2026-06-08). The principal decided WW-Economy-stays:
lanes the new offer can't beat stay on the current contract, costed at invoiced actual. My first
implementation made it a cost comparison — `stays = (quoted calc > invoiced actual)`, `go_forward
= min(calc, actual)`. Ran it: **96% of parcels "stayed."** That wasn't a finding — it was an
artifact: fuel was held at the provisional 35% placeholder (real effective ~20%), which inflates
the quoted calc above actual for nearly every lane, so the min() trivially picked "stay" almost
everywhere. I caught it on the run, not from the principal, and rescoped the rule to a
**fuel-independent** definition: stays = destinations UPS Standard doesn't serve (= the overseas
WW-ECO tail, AU/US/CA/Channel Islands/CY/MT/IS/GI). That gave the intended ~6,776-parcel tail.

**The lesson:** when a derived rule (switch-vs-stay, a `min()`, a threshold, a ranking) keys off a
metric that still contains a **provisional/placeholder input**, the rule's output is an artifact of
the placeholder, not a result. Two ways out: (1) define the rule on a signal that is independent of
the provisional input (here: serviceability, not cost), or (2) defer the rule until the input is
real. Don't ship the artifact and reason from it.

**Why it matters:** this is a sibling of keepsake risk #1 (the 2026-05-14 provisional-fuel headline
collapse) and of "validate refinement through the downstream constraint" — the same failure family:
a provisional number quietly driving a conclusion. The tell here was a too-clean extreme result
(96%) that should trigger "what placeholder is producing this?" before believing it.

**How to apply:** before building a comparison/selection rule, ask which inputs are still
placeholders; if the rule's verdict moves with a placeholder, re-anchor it on a stable signal or
hold it until the real value lands.
