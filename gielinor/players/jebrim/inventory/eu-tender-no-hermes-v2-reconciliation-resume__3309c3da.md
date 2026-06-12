---
quest: S222_eu-tender-no-hermes-v2-headline-reconciliation
sid8: 3309c3da
ts: 2026-06-12 01:50
open_dep: bi-analytics report_no_hermes_v2.{py,html} edit uncommitted — awaiting Niklavs review + commit go (separate repo, commit-gated, never push)
---

# no-Hermes v2 headline reconciliation — answered + one-line bridge added

## Where we are

Answered why `final_report_no_hermes_v2`'s split table (€1,064,523) overshoots the €976,024 headline by €88,500 — by design: Direct Link exit (−€47,305) + Q4 peak differential (−€41,194), both netted into the headline but excluded from the peak-free kept-carrier split. Added a one-line on-page reconciliation under the §03 split table in `report_no_hermes_v2.py`, regenerated the HTML. Principal decided NOT to fold the netting into the total. Full finding logged to a bank draft.

## Next concrete step

Principal-side: review the regenerated `report_no_hermes_v2.html` and decide whether to commit the bi-analytics edit (it sits inside the broader still-uncommitted `final_report_no_hermes_v2/` dir from S219/S221 — pathspec the `*_v2/` dir; always-ask; separate repo from the brain close commit; never push). Otherwise the reconciliation question is closed.

## Files / paths to read first

1. this file
2. `bank/drafts/notes/projects/2026-06-12-eu-tender-no-hermes-v2-headline-vs-flow-split-reconciliation.md` (the full finding + the math)
3. `bi-analytics-main/NFE/projects/2_EU_tender_2026/2_analysis/final_report_no_hermes_v2/report_no_hermes_v2.py` (the bridge line, under `split_table`)
4. sibling resume `inventory/eu-tender-final-report-content-pass-resume__e0eb59c8.md` (the S219 content pass that built the v2 reports)
