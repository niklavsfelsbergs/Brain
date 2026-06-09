# [[S150_e59202cf_carrier-overview-report-design|S150]] d2 — DHL Paket section (Carrier Overview Report)

Dwarf d2 for Jebrim. Carrier slug `dhl_paket`, label **DHL Paket**, badge **firm** (incumbent DE).
Deliverable: `2_analysis/carrier_overview/sections/dhl_paket.md`.

## Turn log
- Spawned. Read spec PLAN.md §3/§4, dhl_paket constants.py + engine doc + carrier CLAUDE.md, REVIEW_CONCLUSIONS Round-2, ASSUMPTIONS DHL Paket block.
- Ran cost_slices: lane_position/profile_position/cheapest_share_lane (dhl_paket), lane_position() DE all-carriers, incumbent_baseline, carrier_vs_invoice, envelope_overlay, lane_pop.
- Wrote `2_analysis/carrier_overview/sections/dhl_paket.md` — all 7 §4 elements filled.

## Load-bearing numbers (from lib — not recomputed)
- DE lane: vol-wtd avg €7.05, **rank 4 of 6** (Hermes 4.16 / DPD 4.48 / GLS 4.51 below; Maersk 8.89 / FedEx 10.69 above). BUT cheapest on **1,488,158 DE parcels** (cheapest_share_lane).
- DE profile split: Compact €3.08 **rank 1 (cheapest)**; Bulky-standard €10.32 rank 6; Large €23.06 rank 4. THE flip.
- Sperrgut catchment (side>60): **38.3% of full book** / 31.3% DE lane (envelope_overlay).
- Incumbent reality-check: engine €3.377 vs invoice €3.283 on 1,556,793 current DHL DE parcels = **+2.87%** (the ~+2.9% over-price bias; conservative).
- Sperrgut line worth €2.31M Q1 / €11.62M full-year (confirmed real). 83% of DE firings = thin-flat canvases.
- ROW: rank 4 but cheapest/within-band (only off-DE lane it wins).
- Coverage ≥95% all 9 lanes (widest clean footprint of roster).

## Profile-lens refresh (dwarf d2b, 2026-06-03)
- `lane_taxonomy.py` neutral parcel-profile lens corrected to carrier-agnostic chargeable weight `max(weight_kg, vol/5000)` (was matrix `dim_weight_kg`, over-counted Compact for gross-only carriers like DHL Paket). Shared slices rebuilt; re-pulled `profile_position` + `cheapest_share_profile`.
- Swapped stale profile figures in §4 (+ levers/take-adjacent prose). DE Compact €3.08→€2.98 (rank 1 holds); DE Bulky-standard €10.32 rank 6→€7.88 rank 5; DE Large €23.06→€21.80 (rank 4 holds). ROW Compact €18.93→€18.12; FR Compact €7.35→€7.32; Benelux Compact €5.20→€5.18. "sixth/rank-6 on bulky" → "fifth/rank-5" (×3 spots).
- Left untouched per brief: lane €/parcel table, cost-component anatomy, envelope overlay, Sperrgut-waiver €, confidence badge, Analyst take. DE total count-of-cheapest (1,488,158 = Compact 944,322 + Bulky 521,641 + Large 22,195) unchanged.

## vs-today lens integration (dwarf d2c, 2026-06-05)
- Carrier Overview **v2**: integrated "vs today" lens (best new offer vs actual 2026-Q1 invoiced UPS/Maersk). Verdicts taken verbatim from `carrier_overview_v2/_data/hands/dhl_paket_card.md` — not recomputed.
- Rewrote `carrier_overview_v2/sections/dhl_paket.md` "## Where it wins" (split real wins from hollow) + "## Analyst take" (lead with keep-vs-switch). Preserved Services / What it carries / Why-mechanic / lever intact.
- Verdict map (from card): REAL (beats today) — DE ≤1kg ✓ (UPS €3.47), DE 2–5kg ✓ (UPS €5.77), Benelux 2–5kg ✓ (UPS €6.16), ROW 2–5kg ✓ (UPS €27.81). HOLLOW — FR 1–2kg (+33% vs Maersk €5.73), FR 2–5kg (+20% vs UPS €6.99), ROW ≤1kg (+9% vs UPS €16.11), ROW Bulky 2–5kg (+57%), ROW Bulky 5–10kg (+80%). DE 1–2kg = win, no today-line on card (left unverdicted).
- Keep-vs-switch: DE core is a real switch (decisive beat); FR/ROW "wins" are hollow → keep the incumbent (UPS/Maersk), don't switch those slices.

## Done. Returning summary.

## Warenpost truck/linehaul sizing (shipping-agent pull, 2026-06-09)
Brief: size DHL Warenpost linehaul per-parcel to feed dhl_paket engine. Lane = 'DHL Kleinpaket' (Warenpost misnomer, resolved prior run). Tier: gold-contract (`shipping_mart.fact_truck_charges` only). FY2025 (departure_date 2025-01-01..12-31).
- FY2025 totals: 792 loads, €224,928 total truck charge, 487,354 allocated parcels. Vol-weighted per-parcel = €0.4615.
- DQ clean: 12/12 months present (Jan 2 → Dec 31), 0 NULL costs, 0 NULL parcel counts, 792 rows = 792 distinct truckload_id (one-row-per-load confirmed, no dupes).
- Monthly per-parcel (€): Jan 0.755, Feb 1.042, Mar 0.980, Apr 0.506, May 0.356, Jun 0.459, Jul 0.401, Aug 0.412, Sep 0.705, Oct 0.698, Nov 0.421, Dec **0.291**. Trough is Dec (peak ship volume, 150 loads / 146k parcels / 976 parcels-per-load) + the May–Aug mid-year fill window; the per-parcel HIGH is Feb (1.04, thin 272/load) and Sep/Oct (~0.70).
- Season split: Q4 (Oct-Dec) €0.3674/parcel vs rest-of-year €0.5436/parcel — Q4 ~32% cheaper, but Oct itself is high (0.698); the real peak drop is Nov+Dec.
- Reconciliation: Q4 €83,496 + RoY €141,432 = €224,928 ✓; 227,215 + 260,139 = 487,354 ✓; 294 + 498 = 792 ✓.
- Recommendation returned: single FY-weighted €0.46 as engine input (engine prices Q1, decision is full-year; season-aware adds fragility for ~€0.18 spread on a small linehaul component). Flag Q1-actual ≈ €0.93 if a conservative Q1-only sanity check is wanted.
