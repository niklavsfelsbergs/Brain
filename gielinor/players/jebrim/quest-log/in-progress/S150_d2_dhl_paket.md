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

## Done. Returning summary.
