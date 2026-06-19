# UPS volume-retention — cell-grain (operational) ceiling

**Drafted:** 2026-06-18 ([[S263_fd7bcba7_ups-retention-cell-grain|S263]] fd7bcba7, continues [[S248_319db0c2_ups-retention-curve|S248]]). EU Tender 2026, no-Hermes v2.
Companion to the parcel-grain floor ([[S248_319db0c2_ups-retention-curve|S248]]). Artifacts: bi-analytics-main
`2_analysis/ups_retention/{build_retention_curve_cell.py, build_report.py, ups_retention.html}`
(committed `1e52a7a`).

## The finding
Retaining UPS volume against the no-Hermes v2 plan is **operationally binary, not a smooth
curve**. The plan moves 373,395 parcels/yr off UPS. Dispatch is per **cell**
(`destination_country_code × packagetype × floor(weight_kg)`, one carrier per cell, per
`routing_report_ops_no_hermes`), so you can only keep a cell's UPS volume by flipping the
WHOLE cell to UPS — which drags its non-UPS cell-mates onto UPS (priced at the UPS offer,
mostly dearer on these lanes).

Three bands of the away pool:

| Cell band (UPS share of cell) | Cells | Retain/yr | Drag/yr | Cost/yr |
|---|---|---|---|---|
| UPS-dominated (≥50%) | 1,198 | 359,984 | 261 | €463,464 |
| Mixed (5–50%) | 59 | 10,613 | 62,237 | €175,943 |
| Sliver (<5%) | 107 | 2,798 | 1,179,560 | €1,938,613 |

- **96% of the lost volume (360k/yr) is operationally retainable at €463k/yr** — flip the
  UPS-dominated cells, near-zero drag. ≈ the parcel-grain floor (€493,488/yr at 100%).
- **The last <1% is sliver-trapped:** a handful of UPS parcels inside DE's biggest DHL/DPD
  mega-cells (e.g. STANZVERPACKUNG 30x20 Pizza box — a 25,773-parcel DHL cell holding 14
  UPS-incumbents/yr). Flipping those drags 1.18M cell-mates for €1.94M/yr. Unretainable
  under coherent dispatch → correctly ceded.
- **"Keep 100% = €2,578,021/yr"** (floor €493k + €2.08M drag) is real arithmetic but not a
  real option.

## Why floor ≈ ops up to ~80%
The parcel-grain floor (cherry-pick the UPS-incumbent parcels, leave cell-mates) and the
cell-grain ops curve are **within ±€2k per tier up to 80%**, diverge +€20k at 90%, then
cliff at 100%. Reason: the cheapest volume to retain lives in cells that are *already mostly
UPS* — there are no cell-mates to drag, so flipping the cell IS cherry-picking. The
operational "one carrier per cell" constraint is **free** until you run out of UPS-dominated
cells and start reaching for UPS volume that's a minority inside another carrier's cell.

## Method note (reusable)
- Built on the same `annual_2026.q1_base.build_pp` frame as the parcel floor (FINAL_6:=FINAL_5,
  DBS-origin pinned to freight, better-of{keep_ref, offer} UPS pricing). `build_pp` drops
  packagetype/weight → re-pull by `shipment_id` to form cells.
- **Validation trick:** the cell curve collapses onto the parcel floor exactly when the drag
  term is dropped (sum the premium over only the UPS-incumbent parcels) — asserted in the
  builder. A clean floor-as-subset check for any whole-cell-flip model. → relates to the
  re-rating / reconcile-against-a-floor discipline.

Cross-link: [[eu-tender]] digest (retention is a tender-result), [[carrier-contracts]]
(UPS offer-vs-current-contract on the away lanes — the offer is worse where UPS is losing).
The parcel-grain floor finding ("the offer isn't the lever on the away-lanes") is the [[S248_319db0c2_ups-retention-curve|S248]]
companion candidate.
