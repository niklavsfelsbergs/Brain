---
quest: S217_eu-tender-final-report-savings-decomposition
sid8: 4e69b79c
ts: 2026-06-11 23:59
open_dep: bi-analytics final_report/ + final_report_no_hermes/ UNCOMMITTED (separate repo, commit-gated) — awaiting principal HTML review + commit go; + a pre-existing service-mix verify FAIL pending a fix decision
---

# Resume — EU-tender final report: savings decomposition

## Status
in-progress (deliverable built + reconciled to disk; awaiting principal review + commit go on the separate bi-analytics repo).

## Where we are
Added "what the savings consist of" to both final reports (`final_report/`, `final_report_no_hermes/`): §03 now carries total-cost before/after anchor → reprice/reroute split → the from→to carrier matrix with **Cost-now / Cost-after** columns. Removed the redundant §04 and Direct Link. All flow + cost reconciliations tie to 0.00; sections renumbered cleanly (full 01–07, no-hermes 01–06).

## Next concrete step
Niklavs to **open both HTMLs in a browser** and confirm the 7-column matrix reads at presentation width (visual NOT eyeballed by me — data + structure verified). Then two questions for him:
1. **Fix the pre-existing `verify_report.py` service-mix FAIL?** (one-line: point the `svc_rendered` check at a carrier total / share instead of the dropped raw service count `879,596`). It's the only red; unrelated to this session's work. → on his go, fix + re-verify (expect PASS).
2. **Commit go** for bi-analytics (separate repo, pathspec the final_report + final_report_no_hermes dirs; **never push**).

## Files / paths to read first
1. this file
2. quest-log `S217_4e69b79c_eu-tender-final-report-savings-decomposition.md`
3. bi-analytics `NFE/projects/2_EU_tender_2026/2_analysis/final_report/{final_report.py, build_final_stats.py, verify_report.py}`
4. bi-analytics `NFE/projects/2_EU_tender_2026/2_analysis/final_report_no_hermes/{report_no_hermes.py, build_stats_no_hermes.py}`
5. sibling resumes: `eu-tender-final-report-content-pass-resume__e0eb59c8.md`, `eu-tender-final-report-resume__907d4e63.md`

## Deferred (not this session's to land)
- The from→to savings-decomposition method (diagonal=reprice / off-diagonal=reroute + cost-before/after) is a reusable analytical pattern for carrier-tender cost reports — harvest into `bank/drafts/notes/` once the quest closes (per the "don't draft bank notes alongside an active quest" rule).
