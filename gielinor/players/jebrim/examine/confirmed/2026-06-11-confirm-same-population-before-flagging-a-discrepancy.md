# Confirm two figures are the same population before flagging a discrepancy

**As-of:** 2026-06-11 · **Session:** [[S211_dcd18cfd_ups-savings-dbschenker-reroute-investigation|S211]] (dcd18cfd) · **Player:** Jebrim · draft (self-observation, correction-anchored)

## The moment

In the [[S211_dcd18cfd_ups-savings-dbschenker-reroute-investigation|S211]] UPS investigation I twice reversed an *alarming* conclusion built on a population mismatch — within the same session:

1. Saw mart zV-DBS cost ~€48 vs the tender's keep_cost €66.65 and concluded **"the tender overstates DB Schenker by ~€20 → the €401k contingent is inflated → the saving is largely illusory."** Even built a "knife-edge, break-even ~34% LPS incidence" story on it.
2. Niklavs said "investigate." The €48 is the **blend of ALL zV** (DE €34 bulk + EU-intl €60-72); the optimizer moves **only the expensive EU-international cells** to UPS, whose real mart cost is **€76.38** — *higher* than the €66.65 keep_cost. No overstatement. Break-even is ~58%, robust. Both alarming claims withdrawn.

## The pattern

The two figures were never comparable: one was a **parent blend**, the other an **optimizer-selected subset**. Selection guaranteed the subset was pricier — the optimizer moves cells *because* they're expensive-on-DBS. That's a selection effect, not a contamination. I read a structural property as a bug, and led with the scary conclusion before checking the population.

## How to apply

- When two same-labeled figures disagree and the gap would imply *something is broken/inflated/illusory*, the **first hypothesis is population/selection mismatch**, not error — especially when one side is a blend and the other a *selected* subset (top-N, optimizer-chosen, threshold-filtered). A selected subset differs from its parent **by construction**.
- Verify same-population (same filter, same grain, same parcels) **before** voicing the alarming read. The cheap check (join on the exact IDs, group by destination) would have caught both reversals pre-emptively.
- Don't lead the principal with "X is inflated / the saving is illusory" off an unverified cross-population compare. A wrong alarm costs more trust than a held one.

Sibling of [[2026-06-11-zv-dbschenker-ups-reroute-economics]]. Generalizes the existing grain-mismatch + reconcile-definition reflexes to the *selection-effect* case.
