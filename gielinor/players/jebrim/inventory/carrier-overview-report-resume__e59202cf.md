---
quest: carrier-overview-report (EU tender — manager-facing carrier report)
sid8: e59202cf
ts: 2026-06-03 14:30
open_dep: SPEC LOCKED, build queued for next session — one dwarf per carrier + synthesis
---

# Resume — Carrier Overview Report (EU tender, manager-facing)

**Status:** SPEC LOCKED (designed with principal this session), BUILD NOT STARTED. New deliverable, distinct from the decision_report.
**Canonical spec:** `bi-analytics-main/NFE/projects/2_EU_tender_2026/2_analysis/carrier_overview/PLAN.md` (thorough, executable — read it first). All build work is self-contained under `2_analysis/carrier_overview/` (plan, sections/, lib/, build_report.py, the HTML). `docs/CARRIER_OVERVIEW_REPORT_PLAN.md` is just a pointer.

## What this is
A carrier-centric report for the **shipping & logistics manager** (negotiation + lane-routing lens): per carrier — what they service, cost-component anatomy (what's charged + what triggers it), native dim/weight envelope, cost position by lane, negotiation levers that change the story, confidence badge. Complements the decision_report (which answers "which 6 to sign"); this answers "tell me about each carrier as a counterpart."

## Decisions locked (10 clarifying Qs answered by principal 2026-06-03 — full list in PLAN.md "Decisions locked")
Headline: new-offer engine cost is the competitive basis (+ invoice-compare line for current carriers); full-year for volume / Q1-unit-cost for head-to-head; raw engine cost (bias caveated); winner = vol-weighted avg €/parcel; dims assumed correct; freight folded per-carrier; NO separate UPS/DB Schenker sections (baseline only); volume-tier OUT of scope; facts + labelled "Analyst take" line; TWO deliverables (full HTML + 1-2pg exec brief). Güll held-badge; year-1 rates only.

## Locked design (from this session's discussion + data pull)
- **Data findings (don't re-derive — in the plan §1):** 2.875M-shipment full-year population; **vol-weight dominates 96.2%** (median bill 2.2× actual) → light-but-bulky book, chargeable weight is the axis that matters; **side >60cm on 38.3%** = the single most decisive dim line (DHL Sperrgut trigger); 17 destinations, top-7 = 95.7%; DQ clean.
- **9 lanes (LOCKED):** DE 67% · FR 10% · Benelux(NL/BE/LU) 7% · AT 5% · IT 4% · Iberia(ES/PT) 2.4% · CH 1.9% (only material customs lane) · Nordics(SE/DK/FI) 1.8% · ROW(AU+tail) 1%. **UK skipped** (zero priced volume — DPD UK out of scope).
- **Parcel profiles:** carrier-NATIVE geometry in each carrier section (his explicit ask — carriers differ); neutral shared-parcel slice (Compact / Bulky-standard / Large on chargeable×60cm) only as the cross-carrier reading lens. Comparison runs the same real parcels through every engine — no shared profile needed for the math.
- **"Competitive" = cheapest OR within 10%** of the lane's cheapest (principal confirmed).
- **Per-carrier template (6 elements):** services/coverage · cost-component anatomy (component→trigger→amount) · native envelope + vol-weight rule + clean-vs-cliff volume overlay · cost position by lane · negotiation levers (→ lanes flipped → € value) · confidence badge.
- **Deliverable:** HTML (match decision_report.html), exec summary → master lane×carrier matrix → per-carrier sections. (Confirm form if principal prefers an excerptable doc.)

## Next concrete step — the build (one agent per carrier)
1. Read the plan doc (above) + this resume.
2. Spawn **one dwarf per carrier** (background): Maersk, DHL Paket, DHL Express, GLS, Güll, Austrian Post, Hermes, DPD PL, FedEx (full deep-dive) + UPS + DB Schenker (lighter). Each fills the §4 template from its engine constants + REVIEW_CONCLUSIONS + ASSUMPTIONS + its cost-matrix slice; writes to `2_analysis/decision_report/carrier_overview/<carrier>.md`; streams to a quest-log sibling. (Or use the Workflow tool if principal opts into harness orchestration.)
3. **Synthesis (principal):** master lane×carrier matrix (cheapest + within-10% per lane×profile) · cross-carrier flip narrative · 3-profile lens · exec summary. Render to HTML.
4. Validate: spot-check 2–3 carrier sections' cost positions against the matrix directly (don't trust the agent summaries blind — verify-the-thing).

## Files to read first (next session)
- `2_analysis/docs/CARRIER_OVERVIEW_REPORT_PLAN.md` (the spec — everything is in it).
- `2_analysis/carriers/<carrier>/constants.py` (per-carrier triggers) + `carrier_responses_to_open_questions/<carrier>/REVIEW_CONCLUSIONS.md` (levers).
- `2_analysis/cost_matrix.py::load_cost_matrix()` (the priced matrix) + `data/population.parquet` (volume).

## Kickoff prompt (paste to start next session)
> Hey Jebrim, build the EU-tender Carrier Overview Report for the shipping & logistics manager. The spec is locked in `2_analysis/carrier_overview/PLAN.md` (resume: `inventory/carrier-overview-report-resume__e59202cf.md`) — data findings, 9-lane taxonomy, carrier-native profiles, within-10% competitiveness, and the 6-element per-carrier template are all in it. All work is self-contained under `2_analysis/carrier_overview/`. Spawn one dwarf per carrier (roster in §5), each doing the thorough deep-dive into its `sections/<carrier>.md`; then synthesise the master lane×carrier matrix + cross-carrier flip narrative + exec summary into the HTML report. Thorough, not quick.

## Notes
- Spec doc is UNCOMMITTED in bi-analytics (principal-gated). Engine rebuilds (fedex-2.0.0 etc.) are committed (be4a393).
- Service-quality overlay (transit/claims) is OUT of cost scope — optional sidecar, not core.
