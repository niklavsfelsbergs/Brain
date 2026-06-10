# EU tender — decision report vs routing report: why the headline savings differ (2026-06-09)

**Anchor:** [[S184_bc889f31_decision-report-routing-reconciliation-headline|S184]] (sid8 bc889f31), Niklavs's "why doesn't the decision report headline match the routing report?" The reconciliation is now headlined inside the decision report itself (`decision_report/report_2026q1.py`, live callout reading `routing_2026q1/routing_stats.json`).

Both reports sit on the **same €2,955,020 Q1 invoiced-actuals baseline** (the old full-year vs Q1 mismatch is gone — both HTMLs are 2026-06-09 on the Q1 basis; `REPORT_NOTES.md` €635k/yr line is stale). The savings differ because they answer **different questions**:

- **Decision report = selection leaderboard.** Ranks 82 candidate carrier sets by **mandatory saving** = every parcel to the cheapest *eligible bid in the set*, **no operational constraint** (near per-parcel cherry-pick). Leading ≤6 set = **€430,055 (14.6%)**. Use it to *compare candidate sets*.
- **Routing report = executed plan.** Takes one chosen forward-basis portfolio and routes every parcel under the real **one-carrier-per-cell** rule (a destination×packagetype cell commits to a single carrier — can't split parcel-by-parcel). Executed = **€377,471 (12.8%)**. Use it as the *operational* number.

**The gap decomposes cleanly:**
- Per-parcel theoretical floor €2,475,020 → committed routing €2,577,549 = **€102,529 "operational gap"** (the cost of one-carrier-per-cell).
- Plus the routing portfolio fixes each carrier's **forward basis** (e.g. DPD-PL kept on its *current* contract, not its new offer) and a **GRI-free baseline** — which the leaderboard's best-case sets don't.

**Rule:** a report's headline metric implies a routing assumption (selection-ceiling vs executed). When two same-domain reports disagree, reconcile the *assumption* before suspecting a bug — and headline the reconciliation *in the report* via a live cross-read so it can't drift. Sibling: [[2026-06-09-routing-cost-basis-decisions]], digest [[eu-tender]].
