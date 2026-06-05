---
quest: S150_final-carrier-setups
sid8: 5aeaa18a
ts: 2026-06-05 18:30
open_dep: routing report built + overview smoothed; Phase C reconcile + Phase E overview-summary + final-setup scoring with principal still open; FR-extend decision pending
---

# Resume — EU-tender final carrier setups (decision report + operational routing table)

## Where we are
Phases A, B, D of `decision_report/PLAN_final_setups_2026q1.md` are built. The EU-tender decision is re-based onto a **2026-Q1 actual-invoice** basis, and the **operational routing table** is built bottom-up → **6 carriers (DHL Paket, Maersk FR+EU, Hermes, DPD-PL, UPS, DB Schenker), Q1 saving €399,750 (13.5%)**. The self-contained `routing_2026q1/routing_report.html` carries: the per-destination freight envelope, a per-carrier "what each carrier takes" overview (smoothed to contiguous weight bands, ~92.7% faithful to the packagetype routing), an interactive sortable/filterable routing table, and a descriptive dimension table. Routing runs on packagetype; the dimensional view is the overview/summary.

## Next concrete step (mostly principal-gated)
1. **Phase C** — reconcile the decision report vs the carrier-overview v2 (both now on the 2026-Q1 basis): overview "~89% beats today" ↔ scorer savings; FR / CH-ROW-bulky hollow ↔ scorer keeps incumbent; spot-check one lane.
2. **Phase D proper** — define + score the candidate FINAL setups WITH the principal (start from the 6 the routing landed on; vary it). The routing already implies the 6; this is the formal portfolio scoring + presentation.
3. **Phase E** — summarize the chosen setups in the carrier-overview (cross-ref, not a recompute) + the new-carrier-caveat reword.
4. **FR-extend decision (principal):** FR is only 55% Maersk today (37% UPS @ €8.66). The routing keeps Maersk on the FR cells it wins; extending the Maersk FR contract to ALL France @ €4.72 would save ~€60k more but assumes the flat rate applies to parcels Maersk never carried. His call.
5. **Optional cleanup:** the ~320 per-cell-consolidation DB Schenker parcels (route per-parcel to tighten to ~756); a switch-threshold to avoid moving a lane for pennies.

## Files / paths to read first
1. `bi-analytics .../2_analysis/routing_2026q1/routing_report.html` — the deliverable (open in browser).
2. `.../routing_2026q1/build_final.py` + `derive_envelope.py` + `carrier_envelopes.py` — the routing + envelope + overview pipeline.
3. `.../decision_report/PLAN_final_setups_2026q1.md` — the authoritative spec (5 phases).
4. `.../decision_report/report_2026q1.py` + `_decision_sets_2026q1.py` + `decision_scorer_2026q1.py` — the 2026-Q1 decision report + scorer.
5. This session's quest-log: `quest-log/in-progress/S150_5aeaa18a_final-carrier-setups.md`.

## Commits (bi-analytics main, NOT pushed)
- `6d211d0` Phase A (population_2026q1 + cost_matrix_2026q1).
- `47f7b0b` Phase D routing folder (build_final, derive_envelope, carrier_envelopes, report).
- This close: the overview rework (carrier_envelopes contiguity-smoothing + report + smooth_impact) committed pathspec-scoped at session close.
- Phase B scorer/report (`_decision_sets_2026q1.py`, `decision_scorer_2026q1.py`, `report_2026q1.py`) — at 2_analysis root; check if committed (may need a commit pass).

## No pending external actions.
