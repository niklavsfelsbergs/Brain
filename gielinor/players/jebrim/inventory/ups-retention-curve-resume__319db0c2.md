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

## UPDATE — cell-grain version BUILT (S263, fd7bcba7, 2026-06-18)

The parked "cell-grain operational" next-step is done. **Live resume + full state →
`inventory/ups-retention-curve-resume__fd7bcba7.md`**; record → quest-log
`S263_fd7bcba7_ups-retention-cell-grain.md`. One line: 96% of the away pool retainable at
≈ the floor (€463k/yr); the last <1% is sliver-trapped (€1.94M to flip) → unretainable.
NFE committed `1e52a7a`.

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
