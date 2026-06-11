# "Noise" is a conclusion, not a default label for an unexplained residual

**Observed:** [[S203_021047a4_q09-baseline-bridge|S203]] (sid8 021047a4), the q09 rate-moves probe. After splitting the €501k
step per carrier, I labeled the DB Schenker €21k residual "likely month-mix noise — treat
as ±" and moved on. Niklavs pushed: *"no [rate-increase] message, so where did it come
from?"* One more group_by (month × incumbent inside the two cells) found a NAMED
mechanism: UPS's disputed S199 dimensioner fees contaminating the shared-cell keep mean —
which turned out to also inflate the gated module saving by ~€21k/yr. The "noise" label
was hiding a real, fixable defect one cheap probe away.

**The pattern:** I had decomposed the gap per carrier (good) but stopped at the first
unexplained residual and reached for "mix/noise" — a label that terminates investigation
without evidence. Sibling of the confirmed `2026-06-09-decompose-cost-gap-before-
attributing-cause` entry, one level deeper: the decomposition isn't done while any slice's
explanation is a shrug.

**Rule:** "noise" must be earned the same way a cause is — by a decomposition that shows
no structure (like-for-like flat, no concentration, no mechanism). If a residual is
concentrated (here: 2 cells, 1 packagetype, 1 month), it has a mechanism; go find it
before labeling.
