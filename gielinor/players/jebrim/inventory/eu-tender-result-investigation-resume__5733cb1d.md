---
quest: S196_eu-tender-result-investigation
sid8: 5733cb1d
ts: 2026-06-11 14:05
open_dep: bi-analytics result_investigation Q05/Q06 + conclusion edits uncommitted there (commit ask pending); review round continues on principal cue
---

# Resume — EU tender result investigation (final-report Q&A)

## Status
in-progress (multi-session: principal reviews the final report by question rounds; "thats all for now" = pause, not done)

## Where we are
- Q01–Q06 ALL CLOSED with principal conclusions recorded in each findings file in
  bi-analytics `2_analysis/result_investigation/` (README = index). Highlights:
  Q01 UPS→DPD = 22k–192k discretionary dial (logistics manager; re-decide on final DPD offer);
  Q02 Maersk = real −17%, stands; Q03 DHL CH clear / AU optional; Q04 FR was stale → q04f
  build-fix session rebased incumbents + re-ran cascade (headline €997.7k → **€974.7k/yr**);
  Q05 AT-to-Maersk trusted; Q06 variable-track cherry-pick real but small (~€78k/yr,
  count-limited), ops routing for variable parcels UNSOLVED (needs real dims at dispatch).
- Cross-cutting discoveries logged: packagetype LABEL CHURN (W80x60AE→ORWO_80x60, ST120x90→120x80;
  parallel session owns q04e), oversize DBS→UPS drift (module-gate add-on), the UPS oversize-fee
  pool (€140.9k Q1 / ~€675k/yr; ~€190k/yr recurring LPS unrescuable without dims — the quantified
  dims-infrastructure prize, in q06 findings §Q06c).
- bi-analytics committed 98cdd49 (final_report + annual_2026 + result_investigation through Q04d).

## Next concrete step
Ask Niklavs: commit the bi-analytics result_investigation updates (q05_*, q06_*, README + q04
conclusion edits — q04f_* files belong to the rebase session)? Then, on his next review round:
remaining unexamined report items = the three stays (UPS→UPS −€108.7k), residual→DPD (only
negative flow row, −€58.5k), DBS→Hermes as its own question (partly covered in q06b), tier split,
fuel band, do-nothing scenario.

## Files / paths to read first
- bi-analytics `2_analysis/result_investigation/README.md` (index of all questions + findings)
- `q06_ups_to_hermes_findings.md` (Q06+b+c — the dims/fee-pool thread)
- `q04f_fr_rebase_findings.md` (the other session's rebase — new headline basis)
- quest-log `S196_5733cb1d_eu-tender-result-investigation.md` (T1–T25 narrative)
