# S166 — EU-tender routing report service-split BUILD (f82b01df)

**Quest:** Execute the routing service-split handoff spec (`routing_2026q1/PLAN_routing_service_split.md`, authored [[S165_f4a07849_cost-structure-card-warenpost-routing-plan|S165]] f4a07849). Build session — nothing was built before this.
**Status:** Parts 1–6 BUILT + verified + **COMMITTED** (bi-analytics `f47098d`, pathspec-scoped, NOT pushed). Part 6 (overview winning-service annotation) done per principal go.

## What was done (5 parts)

1. **Regenerated `cost_matrix_2026q1`** (`python cost_matrix_2026q1.py`) — the routing's Q1 matrix was pre-Warenpost (partitions dated 06-05, before the d54836d Warenpost engine add). 531,194 ships → 4.78M rows. Warenpost now present (27,810 eligible Q1 rows, mean €4.42). Re-ran `derive_envelope.py` (must-freight holds at 165).

2. **Removed residual / "Direct Link"** (`build_final.py`). Quantified first: **8,396 residual parcels** (PostNord SE — PNDSEMYPACKHOME 7,472 + PNDSEVAREKONOMI 919 + 5 MAERSKSE), **all standard, all with ≥1 in-scope engine bid, 0 genuinely unserved**. Fix = exclude out-of-scope incumbents from the std `keep` candidate (keep only if `dom_inc ∈ FINAL_6`) + drop residual from the `cand` filter. Simulated: **0 cells stranded, 0 parcels lost** — the plan's "no in-scope carrier" edge does NOT materialize (no dead code path added). All 8,396 re-route: dpd_pl 5,314 / maersk 1,566 / dhl_paket 1,505 / hermes 7 / ups 4 (SE 6,444 + DK 1,952).

3. **Carried `service` through** (`build_final.py`). Added `FAMILY_TO_ENGINE` map + a `with_service` helper joining each parcel's chosen-carrier engine `service` from the matrix. `routing_rules.csv` rebuilt per-parcel, band-merged on **(carrier, service)** so a band splits where the product changes; `routing_assignment.parquet` gains `service`. UPS / DB Schenker / Maersk-FR → null service = carrier-only (the two-Maersks split: maersk None=27,090 FR carrier-only + eu_hd 41,979 + row_hd 517). Band-merge did NOT explode: **1,985 rules (1,900 cell + 85 by-dims)**. DHL Warenpost lands in the 0–1 kg band (14,611 parcels).

4. **`2_analysis/service_labels.py`** (NEW, shared) — `SERVICE_LABEL` + `service_label(None→carrier-only, unmapped→title-case)`. **Keys verified vs the live Q1 matrix** (23 distinct services; plan's `fedex_ief` had 0 Q1 volume — included forward-compat). All routing services covered.

5. **Service-split display** (`carrier_envelopes.py` + `routing_report.py`):
   - Routing table: new **Service column** + filter; cells split by service; carrier-only shows "—".
   - Portfolio cards: per-service **Products** breakdown (actual routing).
   - What-each-takes: per-carrier **Products (routed)** line. *Kept carrier-level smoothing* (90.7% fidelity) rather than smoothing by (carrier,service) — that cost ~15pts fidelity (78%) and contradicts the locked "carrier top-level, service sub-split" decision; exact split lives in the routing table + dim table.
   - Dim table: **Service column**.
   - "Direct Link" removed everywhere except the **migration FROM** row (truthful current-incumbent source; 1 occurrence).

## Verification (all pass)
residual 0 (portfolio + assignment); service in rules+assignment; DHL ≤1kg→Warenpost (82 rows); UPS/DBS strictly carrier-only (0 svc rows); 1,985 rules no explosion; saving **€411,344 (13.9%)**, up from €399,750/13.5% pre-Warenpost (DHL light-EU + residual reroute); portfolio sums to 531,194; carrier-only parcels 75,707 reconciles (UPS 45,654 + DBS 1,076 + Maersk-FR 27,090 + DPD-PL incumbent-kept 1,887).

## Files (bi-analytics-main, on main @ dfe8bd1, UNCOMMITTED)
MOD: routing_2026q1/{build_final.py, carrier_envelopes.py, routing_report.py} + regenerated {envelopes.json, routing_report.html, routing_stats.json} (tracked). NEW: service_labels.py.
Gitignored (regenerated, not committed): data/cost_matrix_2026q1/*, routing_2026q1/{routing_rules.csv, routing_assignment.parquet, envelope_by_destination.*}.
⚠ S164's validation/db_schenker/* show modified+untracked on the tree — NOT mine; commit with explicit per-file pathspecs ([[S144_bd1a6513_picaapi-us-fathers-day-2025|S144]] sweep hazard).

## Part 6 — overview winning-service annotation (done)
competitive_map.q1_costs computes modal service per (segment, carrier) → segment_service.parquet (gitignored); build_summary attaches winner_service to competitive_summary; build_report renders it in the winner cell (e.g. "Maersk €4.72 · EU Home Delivery"). All 52 segments annotated, winner UNCHANGED (no re-key). Re-ran competitive_map → build_summary → build_report.

## Committed — bi-analytics `f47098d` (on main, NOT pushed)
14 files, explicit per-file pathspecs ([[S144_bd1a6513_picaapi-us-fathers-day-2025|S144]] sweep hazard — the tree carries non-mine dirty work): routing_2026q1/{build_final,carrier_envelopes,routing_report}.py + regenerated {envelopes.json, routing_report.html, routing_stats.json} + PLAN_routing_service_split.md ([[S165_f4a07849_cost-structure-card-warenpost-routing-plan|S165]] spec); service_labels.py; carrier_overview_v2/{build_report.py, lib/{build_summary,competitive_map}.py, carrier_overview.html, exec_brief.html, verification/phase3_reconciliation.md}.
EXCLUDED (not mine, left dirty): decision_report/decision_report.html, validation/db_schenker/* (S164), _decision_sets_2026q1.py + decision_scorer_2026q1.py + report_2026q1.py + switch_list_2026q1/ (S150 untracked).

## Open
- **Push** — awaiting principal go (main ahead 19, NOT pushed).
- ⚠ `_decision_sets_2026q1.py` is an import dependency of the committed build_final.py but is itself UNTRACKED (S150's uncommitted file) — pre-existing dangling state, not mine to commit. S150 should commit it.
