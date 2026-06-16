---
quest: S248_319db0c2_ups-retention-curve
sid8: 319db0c2
ts: 2026-06-16
open_dep: principal will read ups_retention.html later; no edits requested yet
---

# UPS retention curve — resume

**Status.** Deliverable built + committed (bi-analytics `6c30000`). Principal cued
wrap-up to read later.

## Where we are

- New folder `2_analysis/ups_retention/` in bi-analytics-main: curve script +
  HTML one-pager + JSON. Reconciles to the no-Hermes v2 card to the parcel.
- Basis = **better-of {2026 UPS offer, current GRI'd contract}** per parcel (the v2
  convention), annual, away-pool 373,395/yr.
- Headline answer: retain 50% → forgo €61,738/yr (€976k→€914k); 100% → €493,488/yr;
  cost back-loaded on the DHL-Paket light-EU tail; DPD-PL cheapest to reclaim.

## Next concrete step (only if principal asks after reading)

1. **Cell-grain operational version** — current curve is the parcel-grain floor
   (cherry-pick). Real implementation flips whole dest×packagetype×weight cells to
   UPS; costs somewhat more + drags non-UPS cell-mates. Would rebuild on cell grain.
2. **Screenshot** the HTML if he wants it inline / for sharing.
3. **5-tier cut** (20/40/60/80/100) if he prefers the original granularity over 10%.

## Files to read first

1. this file
2. `2_analysis/ups_retention/ups_retention.html` (the deliverable)
3. `2_analysis/ups_retention/build_retention_curve.py` (method + the better-of basis)
4. quest-log `S248_319db0c2_ups-retention-curve.md`

## Open flags

- The "**new offer is worse on the lost lanes**" finding is real + load-bearing
  (offer-only €945k vs better-of €493k vs current-contract €575k at 100%). Candidate
  bank-note at next alching.
- Possible bank-note harvest deferred (harvest-after-stable). No drafts written this
  session.
