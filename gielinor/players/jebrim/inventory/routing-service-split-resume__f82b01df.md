---
quest: S166_routing-service-split
sid8: f82b01df
ts: 2026-06-09 00:00
open_dep: push awaiting principal go (bi-analytics f47098d, main ahead; not pushed)
---

# Resume — EU-tender routing report service-split (S166)

## Status
**DONE + COMMITTED, NOT pushed.** Parts 1–6 of `routing_2026q1/PLAN_routing_service_split.md` built + verified + committed (bi-analytics `f47098d`, pathspec-scoped). Awaiting principal go to push.

## Where we are
The routing now reads a Warenpost-aware Q1 matrix; residual/"Direct Link" is gone (8,396 PostNord-SE/DK parcels re-routed to the 6, 0 stranded); per-parcel `service` flows through `routing_rules.csv` (band-merged on carrier+service) + `routing_assignment.parquet`; the routing report + carrier_overview both render the service split. Q1 saving €411,344 (13.9%).

## Next concrete step
**Push?** main is ahead — `git push origin main` from bi-analytics-main, principal go required (never auto-push). Then S166 graduates → `completed/`. Optionally eyeball `routing_2026q1/routing_report.html` (Service column + Products) and `carrier_overview_v2/carrier_overview.html` (winner-service annotation) first.

## Files to read first
- `gielinor/players/jebrim/quest-log/in-progress/S166_f82b01df_routing-service-split-build.md` (full record)
- bi-analytics `.../routing_2026q1/PLAN_routing_service_split.md` (the executed spec)
- bi-analytics `.../routing_2026q1/build_final.py` (Part 2/3 logic)

## Watch-outs
- ⚠ `_decision_sets_2026q1.py` is imported by the committed `build_final.py` but is itself **untracked** (S150's uncommitted file) — a fresh clone can't run the routing until S150 commits it. Not mine to commit (S144 sweep hazard).
- Other tree-dirty work left untouched (excluded from f47098d): `decision_report/decision_report.html`, `validation/db_schenker/*` (S164), `decision_scorer_2026q1.py` / `report_2026q1.py` / `switch_list_2026q1/` (S150).
