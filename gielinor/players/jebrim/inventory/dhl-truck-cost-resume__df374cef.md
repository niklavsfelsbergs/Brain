---
quest: S172_dhl-truck-cost-warenpost-kleinpaket
sid8: df374cef
ts: 2026-06-09 15:00
open_dep: bi-analytics commit awaiting principal go (engine 2.2.0 + regenerated matrices/overview/routing — UNCOMMITTED, separate repo); S150 decision_report stale vs refreshed cost_matrix_2026q1 (S150's to rebuild)
---

# Resume — DHL Warenpost+Kleinpaket truck cost (S172)

## Status
**Engine work DONE + verified; cascade re-run DONE.** All bi-analytics changes UNCOMMITTED (separate-repo principal gate). Brain side committed at close.

## Where we are
`dhl_paket-2.2.0` adds €0.46/parcel truck cost to Kleinpaket + both Warenpost services, in the cheapest-eligible selection (all-in basis). 22/22 fixtures pass. Both tender matrices + carrier_overview_v2 (9/9 clean) + routing_2026q1 re-run. Q1 routing saving €411,344→**€377,753 (12.8%)**.

## Next concrete step
**Commit the bi-analytics changes?** — awaiting principal go (separate repo, never auto). Pathspec-scope to: `carriers/dhl_paket/` (incl. NEW `surcharges/truck_cost.py`), `docs/ASSUMPTIONS.md`, and the regenerated `data/cost_matrix/`, `data/cost_matrix_2026q1/`, `carrier_overview_v2/_data/` + `*.html`, `routing_2026q1/*.parquet|*.csv|*.json|*.html`. **EXCLUDE** all sibling-dirty paths (S150 decision_report/scorer/_decision_sets, S164 db_schenker validation, S171 UPS 1_offers/) — S144 sweep hazard. Then optionally push (separate explicit ask). Separately: the **S150 decision_report is stale** vs the refreshed Q1 matrix and needs an S150-coordinated rebuild to pick up the truck cost (~€34k weaker DHL Q1).

## Files to read first
- `gielinor/players/jebrim/quest-log/in-progress/S172_df374cef_dhl-truck-cost-warenpost-kleinpaket.md` (full record)
- bi-analytics `.../carriers/dhl_paket/constants.py` + `surcharges/truck_cost.py` + `calculate.py` (`_select_cheapest`)
- bi-analytics `.../docs/ASSUMPTIONS.md` → "2026-06-09 (S169) — Truck (linehaul) cost"

## Watch-outs
- Truck cost is the **Warenpost** lane rate applied to Kleinpaket too (real Kleinpaket has no dedicated truck lane). Revisit if a Kleinpaket-specific lane surfaces.
- `truck_provider` in `fact_truck_charges` = LANE names, not carrier services; Warenpost rides the misnamed "DHL Kleinpaket" lane; join via `allocated_truckload_id`.
- Re-running `cost_matrix_2026q1` also stales the S150 decision_report — coordinate, don't clobber.
