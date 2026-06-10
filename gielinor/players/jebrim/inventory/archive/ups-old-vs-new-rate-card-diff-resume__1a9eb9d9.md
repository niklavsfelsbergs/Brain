---
quest: S168_ups-old-vs-new-rate-card-diff
sid8: 1a9eb9d9
ts: 2026-06-09 13:40
open_dep: none
---

# UPS old-vs-new rate-card diff — resume

**Status:** in-progress (rate-card diff shipped; volume-weighting queued).

**Where we are.** Compared the current UPS contract card vs the 2026 tender offer at the base-net-rate
level. Headline: **~+5% on Standard light across EU**, PL −15%, DK/GB flat; Express/Saver ~97% identical;
zones unchanged; Expedited new; WW Economy absent. Artifact + findings in the bi-analytics repo
(`…/UPS/comparison/`), bank draft in the brain. Fuel/peak/LPS not compared (provisional pending UPS).

**Next concrete step.** Volume-weight it: price 2026-Q1 actuals through the **old** card and diff vs the
new-card replay already built (`…/UPS/calculation/`). Fuel/peak/LPS are identical params both sides, so
the **delta is clean of the placeholders** → a defensible relative €/yr number. Converts "~5% on the card"
into "€X/yr more on our actual mix." (Niklavs was asked if he wants this run; awaiting his go — he was
also waiting on UPS Round-1 replies.)

**Files to read first.**
- `bank/drafts/notes/projects/2026-06-09-ups-old-vs-new-rate-card-diff.md` (the finding)
- `bi-analytics-main/.../UPS/comparison/findings.md` + `compare_rate_cards.py` (artifact + repro)
- `bi-analytics-main/.../UPS/calculation/engine.py` (the new-card replay to mirror onto the old card)
- `inventory/ups-carrier-assessment-resume__7e303a70.md` (the S163/S164 Phase-2 engine state)

**Note.** The bi-analytics `comparison/` artifact is **uncommitted** (separate repo; needs a separate
principal commit ask). Brain bank draft is the durable record.
