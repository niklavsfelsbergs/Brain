---
quest: S263_fd7bcba7_ups-retention-cell-grain
sid8: fd7bcba7
opened: 2026-06-18
status: in-progress (deliverable shipped + committed; parked optional follow-ups)
parent: S248_319db0c2_ups-retention-curve (continues it)
---

# S263 — UPS retention curve: cell-grain (operational) version

**Ask.** Continue the EU-tender UPS retention investigation. Principal picked the parked
"cell-grain operational" next-step from [[S248_319db0c2_ups-retention-curve|S248]]: rebuild the retention curve the way the
no-Hermes routing is actually dispatched (per `routing_report_ops_no_hermes`), not the
parcel-grain cherry-pick floor.

## What happened (turn arc)

1. **Grounded** in [[S248_319db0c2_ups-retention-curve|S248]] (resume + quest-log + the live deliverable on disk), confirmed the
   parcel-grain floor (€493,488/yr at 100%, away pool 373,395/yr). Offered the cell-grain
   build via multiple-choice; principal: "build cell grain, according to how we finally did
   it in routing_report_ops_no_hermes."
2. **Nailed the grain** from `routing/build_final.py` + `annual_2026/q1_base.py`: cell =
   `(destination_country_code, packagetype, wkg=floor(weight_kg))`; **one carrier per
   standard cell**; variable packagetypes (gel/oversized/pallet) route per-parcel by dims.
   `build_pp()` drops packagetype/weight → re-pulled by `shipment_id` to form cells.
3. **Cost model.** Flip a whole away-cell to UPS → reprice every parcel: UPS-incumbents at
   better-of{keep_ref, offer}, dragged non-UPS cell-mates at the offer (null = WW-ECO tail,
   stays put — 0 such cells here). `flip_cost = Σ(ups_cost − rcost)·k`; rank cells
   cheapest-per-retained-parcel; 10% tiers of the away pool.
4. **Built** `ups_retention/build_retention_curve_cell.py` → `retention_curve_cell.json`.
   **Reconciled:** dropping the drag term reproduces the €493,488/yr parcel floor to the
   euro (asserted in builder); away pool 373,395 ✓.
5. **Diagnosed the tail** = sliver cells (107 cells, e.g. DE STANZVERPACKUNG 30x20 Pizza box:
   a 25,773-parcel DHL cell holding 14 UPS-incumbents/yr). Verified live — real structural
   fact, not a bug.
6. **Rewrote** `ups_retention/build_report.py` → unified `ups_retention.html` carrying BOTH
   curves (floor + operational) + the three-band spine + concrete sliver examples.
7. **Discussion turn:** confirmed for the principal that floor ≈ ops up to ~80% (drag
   negligible — retained volume lives in UPS-dominated cells with no cell-mates), +€20k gap
   at 90%, cliff at 100%. Intermediate-tier wobble (±€2k) is an ordering artifact (floor
   ranks parcels, ops ranks cells).

## Numbers (cell-grain, annual, better-of basis)

Three bands of the 373,395/yr away pool:

| Cell band (UPS share) | Cells | Retain/yr | Drag/yr | Cost/yr | €/retained |
|---|---|---|---|---|---|
| UPS-dominated (≥50%) | 1,198 | 359,984 | 261 | €463,464 | €1.29 |
| Mixed (5–50%) | 59 | 10,613 | 62,237 | €175,943 | €16.58 |
| Sliver (<5%) | 107 | 2,798 | 1,179,560 | €1,938,613 | €692.86 |

- Keep-100% ceiling = €2,578,021/yr = floor €493,488 + €2,084,533 drag.
- Floor vs ops per tier: within ±€2k to 80%; +€20,190 at 90%; +€2,084,533 at 100%.

**Headline.** 96% of UPS's lost volume is operationally retainable at ≈ the floor cost
(€463k/yr); the last <1% is sliver-trapped (a few UPS parcels inside DE's biggest DHL/DPD
mega-cells) and operationally unretainable — correctly ceded. The operational read is
binary, not a smooth curve.

## Artifacts (bi-analytics-main, committed 1e52a7a — pathspec-scoped, NOT pushed)

- `…/2_analysis/ups_retention/build_retention_curve_cell.py` → `retention_curve_cell.json`
- `…/2_analysis/ups_retention/build_report.py` (rewritten) → `ups_retention.html` (both curves)

## Leaving open (all optional, none blocking)

1. Finer resolution near the 90–100% knee (drag-gated or 1% cut) — the cliff is inside the
   last 10% tier.
2. Coarser lane-grain version (flip whole dest × packagetype lanes) if ops can't dispatch at
   weight-band grain.
3. Screenshot the HTML for sharing.

**Cascade.** None (analysis only; both scripts are read-only consumers of `build_pp` / the
cost matrix — no shared-engine code touched).
**Main-brain changes.** None.

Resume: `inventory/ups-retention-curve-resume__fd7bcba7.md`.
