# [[S150_e59202cf_carrier-overview-report-design|S150]] d7 — Hermes section (Carrier Overview Report)

Dwarf d7 for Jebrim. Building `2_analysis/carrier_overview/sections/hermes.md`.
Carrier slug `hermes`, label **Hermes**, confidence **provisional** (engine rebuilt but cost basis benchmarked vs PRE-Hermes Q1 baseline — Hermes added to matrix 2026-05-15 → apparent savings artificially favourable). LOAD-BEARING caveat: Hermes shows DE-cheapest; must not be read as firm in negotiation.

## Steps
- [x] Read PLAN.md §3 + §4
- [x] Read hermes constants.py + CLAUDE.md + technical/engines/hermes.md
- [x] Read REVIEW_CONCLUSIONS.md + ASSUMPTIONS.md Hermes block + 2026-05-22 cost-only/Q1-transition notes
- [x] Run cost_slices lib calls
- [x] Write hermes.md (7 §4 elements, provisional threaded through) — DONE at sections/hermes.md
- [x] Return summary

## Done
Wrote `2_analysis/carrier_overview/sections/hermes.md` — all 7 §4 elements, provisional caveat threaded through element 4 (cost position) + element 6 (badge) + element 7 (take). Coverage caveats noted (ROW 25.9% excluded; CH structural reject). DHL-incumbent reality-check line added (DHL €3.28 < Hermes €4.17 on DE). Read-only on sources; no writes outside my section + this quest-log.

## Numbers (from lib — single source of truth)
lane_position(hermes): DE rank1 cheapest avg €4.165 (q1 €4.076) cov 99.59%; Iberia rank2 €6.579; AT rank3 €5.602; FR rank3 €11.241; IT rank4 €8.467; Nordics rank4 €14.539; Benelux rank4 €10.114; ROW cov 25.9% → EXCLUDED (no rank). All priced lanes contender=true except ROW. within_band=true ONLY on DE.
DE pool (lane_position()): hermes €4.165 (1) < dpd_pl €4.480 (2) < gls €4.512 (3) < dhl_paket €7.050 (4) < maersk €8.887 (5) < fedex €10.693 (6). DE = 1.916M pop / €7.74M pop-spend (66.7% of book).
incumbent_baseline DE: DHL (current) €3.283/parcel — BELOW Hermes engine €4.165. UPS DE €5.644. So Hermes engine beats UPS but NOT today's DHL invoice on DE.
profile DE: Bulky-standard hermes cheapest €4.297 (cov 65.6%); Compact rank2 €3.645; Large rank3 €6.844.
cheapest_share_lane: DE 418,858 cheapest-count (dominant); also wins Iberia 16,131 / FR 8,698 / Benelux 6,840 count-of-cheapest pockets despite not leading avg there.
envelope_overlay DE: side>60 31.3%, side>120 (bulky trigger) 3.13%, lpg>300 3.37%, chargeable>30 0.95%, actual>31.5 0.004% (≈0 weight rejects).

## Progress
(streaming below)

## d7b — surgical profile-lens refresh (corrected chargeable-weight lens)
lib/lane_taxonomy.py neutral profile lens corrected: chargeable weight now `max(weight_kg, volume_cm3/5000)` (carrier-agnostic), not the matrix per-carrier dim_weight_kg — gross-only carriers (Hermes) no longer over-count Compact. Re-pulled cs.profile_position('hermes') + cs.cheapest_share_profile(). Updated ONLY §4 "Profile read (DE)" sentence (line 105). DE profile-lens now: Bulky-standard €4.092 (was €4.297), cov 100.0% (was 65.6%), rank 1 cheapest; Compact €3.607 (was €3.645), cov 100.0%, rank 2; Large €6.700 rank 3 (added). Qualitative story + PROVISIONAL caveat + lane table + anatomy + levers untouched. §3 "38%/3.1%" geometry overlays left as-is (envelope_overlay lens, out of brief scope).
