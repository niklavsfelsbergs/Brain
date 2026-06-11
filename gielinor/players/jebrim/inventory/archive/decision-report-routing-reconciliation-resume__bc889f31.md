---
quest: S184_decision-report-routing-reconciliation-headline
sid8: bc889f31
ts: 2026-06-09 19:46
open_dep: bi-analytics-main decision_report commit gated on Niklavs's go (+ offered REPORT_NOTES.md stale-line update)
---

# Resume — decision report: decision-vs-routing reconciliation headline

**Status:** in-progress (deliverable shipped to working tree; external commit gated)

**Where we are:** Added a live-data headline callout to the decision report (`report_2026q1.py`) explaining why its mandatory saving (€430,055 / 14.6%) differs from the routing report's executed saving (€377,471 / 12.8%) — selection ceiling vs one-carrier-per-cell executed plan, €102,529 operational gap + forward-basis/GRI differences. Regenerated `decision_report.html`; figures verified.

**Next concrete step:** Two open items, both Niklavs's call —
1. Commit the `bi-analytics-main` decision_report edit (`report_2026q1.py` + regenerated `decision_report.html`)? Separate repo, gated. Scoped pathspec when greenlit.
2. Update the stale `REPORT_NOTES.md` €635k/yr full-year line to the Q1-actuals basis (offered, not yet actioned)?

**Files / paths to read first:**
- `bi-analytics-main/NFE/projects/2_EU_tender_2026/2_analysis/decision_report/report_2026q1.py` (the callout block + routing-stats live read, near lines 131 / 585)
- `bi-analytics-main/.../routing_2026q1/routing_stats.json` (the cross-read source)
- `players/jebrim/bank/domains/eu-tender.md` (domain digest)
- `players/jebrim/bank/notes/projects/2026-06-09-routing-cost-basis-decisions.md`

**Pending drafts:** 1 bank draft — `bank/drafts/notes/projects/2026-06-09-decision-vs-routing-savings-reconciliation.md`.
