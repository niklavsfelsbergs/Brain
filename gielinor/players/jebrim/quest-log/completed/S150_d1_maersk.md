# [[S150_e59202cf_carrier-overview-report-design|S150]] d1 — Maersk section (Carrier Overview Report)

Dwarf d1, Jebrim namespace. Building `carrier_overview/sections/maersk.md`. Carrier slug `maersk`, engine maersk-3.0.0, badge **firm** (thin current invoice base ~107 parcels).

## Run-log
- Read PLAN.md §3/§4 — template locked, 7 elements, winner = vol-wtd avg €/parcel, competitive = cheapest or within 10%.
- Read constants.py + engines/maersk.md — two branches (eu_hd gross / row_hd ÷5000). EU = GROSS-only billable (no divisor) → structurally cheap on bulky book; ROW = max(gross, LWH/5000). Surcharges: Overpack 0.40 always-on, AT/DE/DK tolls 0.29/0.19/0.05, EU peak 0.25 (flagged), CH ZAZ 0, customs in-base. >30kg reject. FR/SE/FI reject (not on card); DK on card.
- Read REVIEW_CONCLUSIONS + ASSUMPTIONS Maersk blocks. Levers: Overpack waiver (in-house sorting) -€188k Q1; EU fuel 6.6% ±€24k/pp; ROW fuel 24.75% interim over-states; ROW demand=0 deferred. Cross-carrier: CH ZAZ-waived (vs AP charges regardless), customs in-base.
- Pulled slices: lane_position, profile_position, cheapest_share, lane_position(ALL), incumbent_baseline, carrier_vs_invoice, envelope_overlay, lane_pop.
  - WINS (rank 1, cheapest): Iberia (5.60), IT (6.21). Strong #2 AT (5.41, but Güll cheaper). #3 CH/Benelux. OFF-PACE #5 DE (8.89 vs Hermes 4.16), #5 ROW (35.36 vs DHL Paket 28.09). FR REJECTS. Nordics 29% coverage = non-contender.
  - SHARP FLIP: DE avg-rank #5 but count-of-cheapest only 6,705 of 1.9M — vol-weight does NOT save Maersk on DE; it's genuinely mid-pack there. IT: cheapest on avg AND 88,432 count-of-cheapest = real win.
  - carrier_vs_invoice: Maersk's ONLY current invoiced lane is FR (107 parcels, €4.82) — and the new engine REJECTS FR. So new-offer doesn't even price the incumbent lane. Thin-base caveat is sharp.
  - Writing section now.
- WROTE `carrier_overview/sections/maersk.md` — all 7 §4 elements, Jebrim register. Tables: coverage, anatomy, envelope cliffs, lane cost position. Analyst take labelled. DONE.

## v2 vs-today pass (dwarf, carrier_overview_v2)
- Rewrote `carrier_overview_v2/sections/maersk.md` for the "vs today" lens, from the verified `_data/hands/maersk_card.md`. Preserved Services / What it carries / Why-mechanic / lever intact.
- **Two-Maersks note added** (prominent, top of page): NEW offer (maersk-3.0.0) does NOT price FR; CURRENT Maersk contract is FR's cost leader at €4.72/parcel actual Q1, 27,624 shp, and the whole tender fails to beat it on every FR segment → keep current Maersk on France. Two carriers, two decisions.
- **Where it wins** — tagged 14 wins from card: 13/14 ✓ beat today (UPS), 1 (Nordics-DK Bulky 1–2 kg) has no today-anchor. Nordics-DK gaps are the biggest (€2–3/parcel vs UPS). Also flagged 2 hollow ROW contenders (Std ≤1 kg +9%, Bulky 2–5 kg +57% over today) + 2 contenders that clear today (Iberia Std 2–5, ROW Std 2–5).
- **Analyst take** — new offer genuinely improves on today (13/14 real wins, switch those EU/Nordics-DK lanes); ROW hollow slices keep incumbent; FR held by current Maersk contract.
- DONE.
