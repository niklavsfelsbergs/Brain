# Isolating a cost component from a counterparty's concession ≠ removing its benefit from our own calc

**Observed:** [[S369_997395cd_uk-maersk-revenue-loss-100pct|S369]] (2026-06-25), UK Maersk revenue-loss-for-100%. The principal said "isolate the
truck cost — Maersk doesn't care about it, we pay it." I read that as *strip truck from both sides* and
computed the concession as the raw ex-truck parcel gap (349,948 − 288,058 = GBP 61,891/Q ≈ 297K/yr).
Wrong. The principal caught it: "why are the 3 options different from the now calculation?" — the
options each carve 45,251/Q, but I'd just claimed Maersk must lose 61,891. They can't both be right.

**The error.** "Isolate truck from Maersk's concession" means truck is not part of *what Maersk gives
up* (their revenue is parcel-only; truck is a separate DHL Freight leg). It does NOT mean delete the
truck *saving* from *our* 0%-neutrality calc. The truck saving (consolidation: 3,620→3,350) is real,
ours, and legitimately reduces how much Maersk must concede for our total to stay flat. I removed it
from both sides — out of Maersk's ask (correct) AND out of our own benefit (wrong) — double-counting
the isolation and inflating the concession by ~80K/yr.

**The rule.** When a principal says "isolate cost component X" in a counterparty negotiation, ask
*isolate it from whose ledger?* Isolating X from **their concession** (X isn't theirs to give) is a
different operation from isolating X from **our indifference point** (X's movement still helps or hurts
us). A component can be out of the counterparty's number while its delta stays fully inside ours. Keep
the two ledgers separate: their loss = the parcel-side cut; our neutrality = parcel cut ± every cost
that moves on our side, truck included.

**Tell.** Two figures that should be the same (Maersk's loss vs the gap the options close) diverging is
the bug signal — I should have suspected the framing the moment 297K ≠ the 45K the options were sized
to, not defended it. Reconcile-definition-before-numbers + disagreeing-totals-suspect-a-mismatch both
point here. [[2026-06-19-verify-inherited-analysis-claims]] is the sibling (echoing a committed number
before checking its basis).
