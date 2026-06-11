---
quest: S203_q09-baseline-bridge
sid8: 021047a4
ts: 2026-06-11 17:30
open_dep: bi-analytics report-chain rework uncommitted (principal eyeball + threshold call + commit go)
---

# Resume — q09 baseline bridge + switch threshold

## Status
built + verified (full chain PASS); blocked on principal review/commit in bi-analytics.

## Where we are
- Three-number bridge live through the whole chain: paid €2,955,020 → do-nothing
  €3,055,317 → plan €2,762,682 = €292,636 Q1 / **€1,442,782 annual (9.57%)**, rate moves
  separated (+€100,297 Q1 / +€483,133 ann). Savings basis = keep_ref − rcost everywhere;
  per-flow signs match the optimizer by construction.
- keep_ref grain = (cell × incumbent) per the q09d fix (principal-approved T7): each
  parcel's do-nothing price = its own carrier's March mean; kept cells' plan cost =
  dom's own mean; optimizer bid stays cell-grain (zero routing churn). The S199 UPS
  dimensioner fees no longer inflate DBS/module numbers (sit on UPS's own line, ~€21k).
- SWITCH_MIN_PCT = 0.02, cross-family only (build_final.py + q1_base.py lockstep);
  parks 81 cells / 17,626 Q1 parcels (€1,135 Q1 foregone). q08 cell still moves.
- S200 ordering guard: verify_report cross-asserts vs live annual_stats; prose claims
  computed, not hard-typed.

## Checklist (all done except principal-gated)
- [x] build_final.py keep_ref/do-nothing/flows/threshold  [x] q1_base lockstep
- [x] build_annual re-base  [x] build_final_stats bridge3 + S200 assert
- [x] renderers (final/routing/annual)  [x] q09 grid + threshold pinned
- [x] full chain rebuild + verify PASS  [x] q09 findings md
- [ ] principal: eyeball HTMLs, threshold value (2% rec / 1% / 3%), commit go
- [ ] README q09 row (87f50e88 owns README — suggested in comms)
- [ ] stale-basis consumers: management deck, eu-tender digest headline (alch), carrier_overview prose

## Next concrete step
Niklavs reviews final_report.html + routing_report.html + annual_report.html (headline
basis changed everywhere) and rules on the threshold value; then commit with the pathspec
in the quest entry (bundles the S198/S201 final_report/ artifacts already uncommitted).

## Files / paths to read first
- bi-analytics `2_analysis/result_investigation/q09_baseline_bridge_findings.md` (the record)
- `2_analysis/routing_2026q1/build_final.py` docstring (bridge + threshold semantics)
- quest-log `S203_021047a4_q09-baseline-bridge.md` (turn log + commit pathspec)
