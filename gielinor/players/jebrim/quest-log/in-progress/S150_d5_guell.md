# [[S150_e59202cf_carrier-overview-report-design|S150]] d5 — Güll carrier-overview section

Dwarf for Jebrim. Build `sections/guell.md` (held / optimistic-ceiling badge).

## Progress
- [x] Read PLAN §3/§4/§9 — Güll held caveat confirmed (§9 line 149: ships with badge, not dropped; §4.6 confidence-badge element).
- [x] Read constants.py — AT 2-band (2.95/3.25) + Maut 0.30 + B2C 0.15 + bulky 7.00 @150L; CH PostPac 6.70 CHF / Bulky 22.00 CHF + energy 0.04 CHF; fuel AT 27.27% base-only; FX 1.05. Gross weight only (no dim weight).
- [x] Read engine doc guell.md (technical) — 3 services HD-only, AT/CH/LI scope, rejects everything else.
- [x] Read docs/technical/engines/guell.md (lite) — HELD: no reply, engine still guell-1.0.0, 14/14 fixtures only signal.
- [x] ASSUMPTIONS Güll block (L399-418) — placeholder, engine not rebuilt 2026-05-28, zero Round-1 reply. Levers: FUEL_PCT_AT 0.2727 (Q7, biggest AT lever), fuel scope base-only (Q6), PEAK 0, CHF_TO_EUR 1.05 (Q13, ±3% CH), line-haul NOT modelled (Q9), CH pallet fallback NOT modelled.
- [x] Run cost_slices — AT cheapest (€4.33 fy / €4.31 Q1, rank1, vs Maersk €5.41); CH rank2 (€9.62/€10.80 Q1) behind Austrian Post €8.66. CH incumbent UPS invoice €9.66 (53,399) ≈ Güll engine €9.62 — near parity. DB Schenker CH €248 freight tail. Coverage AT 96.7% CH 99.8%; all other 7 lanes NOT priced (rejected country_not_served).
- [x] Spill: AT bulky(>150L) 1.3%; CH PostPac→Bulky(dmax>100) ~10%, +15.8% W/H>60.
- [x] Write section → sections/guell.md (all 7 §4 elements, held/ceiling caveat threaded through every number). DONE.
- [x] d5b SURGICAL REFRESH (corrected carrier-agnostic chargeable-weight lens, coverage now ≤100): updated profile-lens €/parcel only — AT Bulky-standard €4.45→€4.29, AT Large €4.68→€5.01, CH Large €22.96→€22.13; added CH Compact €7.08 / Bulky-standard €9.63 anchors to §3 cliff sentence (~37%→~47%). AT Compact €4.20 + count-of-cheapest 128,359 unchanged. Lane-level table/anatomy/held badge/analyst take untouched. No >100% workaround text was in the section (section quoted profile €/parcel, not coverage); proper ≤100 coverage now backs every quoted profile figure.
