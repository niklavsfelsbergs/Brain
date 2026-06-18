---
quest: S263_fd7bcba7_ups-retention-cell-grain
sid8: fd7bcba7
ts: 2026-06-18 00:00
open_dep: none
---

# UPS retention curve — cell-grain (operational) — resume

**Status.** Done for now. Deliverable built + committed (bi-analytics `1e52a7a`).
Continues S248; principal cued wrap-up after a discussion turn.

## Where we are

- Cell-grain (operational) retention curve built alongside the parcel-grain floor.
  Grain = cell (`dest × packagetype × floor(weight_kg)`), one carrier per cell, per
  `routing_report_ops_no_hermes`. Retaining a cell's UPS volume = flip the WHOLE cell,
  dragging non-UPS cell-mates onto UPS.
- **Finding (binary, not a smooth curve):** 96% of the 373,395/yr away pool lives in
  UPS-dominated cells → retainable at €463,464/yr, drag 261. The last <1% is sliver-trapped
  (107 cells, a few UPS parcels inside DE's biggest DHL/DPD mega-cells) → flipping drags
  1.18M/yr for €1,938,613 → operationally unretainable, correctly ceded.
- Floor ≈ ops up to ~80% (drag negligible); +€20k at 90%; cliff at 100% (€493k floor →
  €2.58M ops, the €2.08M gap = cell-mate drag). Reconciles: drop drag → €493,488 floor exactly.

## Next concrete step (only if principal asks)

1. **Finer tiers near the knee** — drag-gated or 1%-resolution cut across 90–100% (the cliff
   lives inside the last 10% tier).
2. **Lane-grain (coarser)** — flip whole `dest × packagetype` lanes; costs more still. Only
   if ops can't dispatch at weight-band grain.
3. **Screenshot** the HTML for sharing.
4. Bank-note harvest written this session (`bank/drafts/notes/projects/2026-06-18-ups-retention-cell-grain-operational-ceiling.md`) — promote at next alching.

## Files to read first

1. this file
2. `…/2_analysis/ups_retention/ups_retention.html` (the deliverable — both curves)
3. `…/2_analysis/ups_retention/build_retention_curve_cell.py` (the cell-grain method)
4. quest-log `S263_fd7bcba7_ups-retention-cell-grain.md` (+ parent `S248_319db0c2_*`)
