---
quest: S198_fr-incumbent-rebase
sid8: cbc40f78
ts: 2026-06-11 13:05
open_dep: principal review + commit go in bi-analytics (build fix + cascade artifacts uncommitted there)
---

# FR incumbent rebase — resume

- **Status:** in-progress (work done + verified; blocked on principal review/commit in bi-analytics)

## Where we are

The FR rebase build fix is DONE and verified: 3 approved changes landed in
`routing_2026q1/build_final.py` + replica `annual_2026/q1_base.py` (DPD-FR
cur_inc→maersk; March keep anchor `LATEST_MIN_N=10` with Q1 fallback — 763
cells anchored / 3,049 fallback; baseline untouched), plus a deterministic
tie-break fix the cross-asserts forced (latent 1-vs-1 dom tie, NL GEL klein).
Full cascade re-run, all asserts + verify_report PASS. Headline: **annual
€997,720 → €974,692 (−€23,028)**; Q1 €201,916 → €194,191. Findings + diff:
`result_investigation/q04f_fr_rebase.{py → _findings.md}` + README Q04f row.
ALL UNCOMMITTED in bi-analytics.

## Next concrete step

Two questions for Niklavs, then commit:
1. The handoff's existence proof did NOT reproduce — FR Poster 40 @0kg stays
   DPD under the approved March-blend spec (€4.587 vs €4.517; q04c's €4.09 was
   the Maersk-only mean). Does he want the keep representation revisited, or
   does the spec-as-built stand?
2. DE × Poster 40cm @0kg knife-edge flip — 21,858 parcels DHL→DPD at
   €0.04/parcel. Suppress via the Q01b switch-threshold machinery, or execute?
Then: commit go in bi-analytics (pathspec: routing_2026q1/build_final.py,
annual_2026/q1_base.py, result_investigation/q04f_* + README.md — README also
carries sibling 5733cb1d's uncommitted q05/q06 rows, coordinate — plus
regenerated stats JSONs/report HTMLs per repo convention). Never push.
After commit: eu-tender domain digest headline (€997,720) is stale → next alch
re-stamps it to €974,692.

## Files / paths to read first

- `result_investigation/q04f_fr_rebase_findings.md` (the full story)
- `routing_2026q1/build_final.py` (the 3 changes + tie-break)
- before-snapshot for the diff: `%TEMP%\fr_rebase_before\` (parquets not git-tracked — if gone, before-numbers live only in the q04f findings)
