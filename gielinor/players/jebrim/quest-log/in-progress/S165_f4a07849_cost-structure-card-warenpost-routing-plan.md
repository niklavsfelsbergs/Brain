---
session: S165
sid8: f4a07849
player: jebrim
date: 2026-06-08
status: in-progress (card + Warenpost shipped & committed; routing = planned handoff)
---

# S165 — EU-tender carrier-overview Cost Structure card → Warenpost engine add → routing service-split plan

## Asked
Started as a design discussion: a per-carrier cost-structure overview ("open DHL Paket, see base rate + every charge + when it triggers"). Converged to a transparency card inside carrier_overview_v2, engine-only. Then it surfaced a real engine gap (Warenpost), which the principal had me size and then build. Then we turned to updating the routing report (service-level + a "Direct Link" anomaly), which we scoped into a handoff plan for the next session.

## Done
1. **Cost-structure card** (committed bi-analytics `d54836d`): each of the 9 carrier pages gains a hand-written `## Cost structure` prose overlay (eligibility + every position's trigger) + an auto-rendered "Rate-card ledger" (amount · fires-on incidence% · season/exclusivity/fuel-class tags · worked example · collapsible rate grids). Engine-introspected (`lib/cost_structure.py`); verified vs engine runtime output (`lib/_cost_structure_probe.py`) — **9/9 clean**. Fan-out: 9 dwarves wrote the prose overlays. Decisions: triggers in prose (no engine edits), incidence included, worked example yes, exec_brief untouched, internal-analyst register.
2. **Warenpost engine add** (committed in `d54836d`): sizing found DHL excluded Warenpost Intl (~169k parcels / 5.9% book / ~€0.5M/yr DHL overstated on light-EU); principal approved building it. Added Warenpost Std+Premium as the 5th/6th DHL service → **dhl_paket-2.0.0 → 2.1.0** (extract_rates, constants, calculate, toll_co2-exclusion). Tests **22/22**. Re-ran full-year matrix + carrier_overview_v2. Realized **168,753 Warenpost parcels, €475k/yr** — matched the sizing.
3. **Routing investigation + plan** (handoff, NOT built): traced the routing pipeline; solved the "Direct Link" anomaly (it's the `residual` family label — out-of-scope incumbents the 6 don't beat); confirmed every engine emits real named services; found the routing reads a SEPARATE `cost_matrix_2026q1` (still pre-Warenpost). Wrote the full spec → `bi-analytics .../routing_2026q1/PLAN_routing_service_split.md`.

## Decisions (routing, locked with principal)
- Residual removed → out-of-scope incumbents re-route to the next-cheapest active carrier (drop them from build_final's `keep`).
- Full service split in the **routing report only** (finest grain; dissolves mixed-service cells). Carrier-overview = annotate winning service only (not re-key).
- UPS/DB Schenker carrier-only (no engine service). Author a service→label map. No pre-routing commit (revert point = d54836d).

## Handoff (next session)
Read `routing_2026q1/PLAN_routing_service_split.md` + resume `inventory/cost-structure-card-resume__f4a07849.md`. 5-part change: regen Q1 matrix → remove residual (+ quantify/handle the unserved edge) → carry service through build_final → service_labels.py → service-split display. ⚠ The S150 decision_report + routing are stale vs the regenerated full-year matrix; decision_report disregarded per principal; routing update is this handoff.

## Cascade.
None pending in the brain rulebook. Engine-owner observations (stale docstrings in fedex/dhl_express) recorded in `carrier_overview_v2/PLAN_cost_structure.md`, not fixed (out of scope).

## Main-brain changes.
None — no meta/ritual/hook changes. Pure player-domain work (bi-analytics deliverable + brain trail).
