---
quest: S230_eu-tender-no-hermes-with-gull-report
sid8: b94d4675
ts: 2026-06-12 14:30
open_dep: bi-analytics commit pending principal (separate repo, their go); next thread = linehaul/density estimation
---

# Resume — EU Tender no-Hermes + Güll report (six-carrier)

**Status:** in-progress (deliverable SHIPPED; thread continues into the linehaul/density refinement)

**Where we are:** Built `final_report_no_hermes_with_gull/` (stats builder + JSON + report .py/.html) beside the 5-carrier `final_report_no_hermes_v2/`. Renders clean, headline €1,139,121/yr reconciles, Güll net marginal +€163,097/yr, 150-parcels/pallet flagged. bi-analytics edits left UNCOMMITTED per the brief.

**Next concrete step — the principal flagged it explicitly: next conversation is the linehaul (parcels-per-pallet / density) estimation again.** This is the **150-parcels/pallet** gate that firms Güll's marginal. The lever:
- `carriers/guell/constants.py` `PARCELS_PER_PALLET = 150` is a divisor on **three** always-on per-parcel costs: inbound sprinter €0.80 (955÷[8×150]), outbound AT €0.16 (24.50÷150), outbound CH €0.27 (40÷150).
- Sensitivity ~**±€40k per 50 parcels/pallet** on the marginal. 150→100 ≈ +€28–55k dearer.
- **Revising it = re-run Güll engine prices (cost matrix) + re-run this report's stats+report** — NOT just text; density is baked into per-parcel cost.
- Compounding cap: sprinter caps at **8 pallets OR 1,000 kg**; 1,200 parcels/sprinter assumes avg ≤0.83 kg/parcel — heavier Picanova product (canvas/frames) may hit the **weight** cap first → fewer parcels → higher allocation.
- **The gating data item:** logistics-manager's realistic operating **parcels-per-pallet (AT, CH separately)** + per-sprinter fill, and whether fill binds on volume or weight first. (Question framed in the S228 quest-log.)

**Open for principal:** (1) the bi-analytics commit (their go). (2) Want Güll fully *outside* the headline (5-carrier floor + Güll as separate additive line)? small edit. (3) Deck — template `deck_no_hermes_v2.py` the same way if wanted.

**Files to read first (next session):**
- `players/jebrim/bank/drafts/notes/projects/2026-06-12-guell-no-hermes-marginal-and-density-gate.md` — the density-gate writeup (assumptions that bias Güll's cost down; contract pallet mechanics; the logistics-manager question).
- `players/jebrim/inventory/guell-2.0.0-build-resume__9f716f1f.md` — the guell-2.0.0 engine build + locked calls (FX 1.08; ignore AT bulky; stated outbound rates 24.50 AT / 40 CH).
- bi-analytics: `carriers/guell/constants.py` (PARCELS_PER_PALLET + the line-haul surcharges), `carriers/guell/CLAUDE.md` (version history), `final_report_no_hermes_with_gull/build_stats_no_hermes_with_gull.py`.
- This session's quest-log: `quest-log/in-progress/S230_b94d4675_eu-tender-no-hermes-with-gull-report.md`.

**Locked calls (in guell-2.0.0, no engine change):** FX 1.08; ignore AT bulky shape; Güll's stated outbound per-pallet rates (24.50 AT / 40 CH). Non-blocking: Commerzbank strongest-of-month FX value pull.
