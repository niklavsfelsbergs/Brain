# [[S150_e59202cf_carrier-overview-report-design|S150]] d6 — Austrian Post section (Carrier Overview Report)

Dwarf d6 for Jebrim. Building `carrier_overview/sections/austrian_post.md`. Confidence: firm; AT-lane specialist.

## Progress
- Read PLAN §3/§4, constants.py, engine doc, REVIEW_CONCLUSIONS, CLAUDE.md, ASSUMPTIONS AP block.
- Key facts: gross-only weight (no vol-weight — huge advantage on bulky book); AT + CH/LI only (everything else country_not_served). Surcharges: Maut 0.29 AT, Sperrgut groß 7.80 (d_max>100), diesel_ch 0.05, customs_ch 1.00 (regardless ZAZ), line_haul ~0.83 (flagged ASSUMPTION, all eligible), peak 0. AT fuel 4% base-only.
- Note: ASSUMPTIONS §52 mentions "B2C" in fuel-scope row, but engine has NO B2C surcharge — brief's "B2C" maps to nothing in the modelled engine; will report only modelled components honestly.
- Levers: (1) parcels-per-pallet density 150 → line-haul denominator, ~€20-82k Q1 sensitivity, INTERNAL Picanova ops. (2) AT D-card / fuel 4% vs 12% spike. (3) Maut/VAT minor. Volume-tier OUT.

## Slice findings (KEY — inverts brief hypothesis)
- **CH is AP's win, not AT.** CH: rank 1, cheapest + within_band, avg €8.66 (Q1 €8.80), n_priced 45,318, coverage 84.2%. Next: Güll €9.62, Maersk €11.64. AP ~10% below Güll.
- **AT: rank 6 of 9, NOT competitive.** avg €6.68 (Q1 €6.80), coverage 99.3% (140k pop, full coverage). Winner = Güll €4.33; Maersk €5.41, Hermes €5.60, GLS €5.94, DPD PL €5.98 all beat AP. AP only cheapest on 72 AT parcels (vs CH 101).
- AT profiles: Compact rank6 €5.46, Bulky-std rank4 €5.97, Large rank6 €14.57 — off-pace everywhere on AT.
- CH profiles: Compact rank2 €8.55, Bulky-std rank1/cheapest €8.94, Large 2.8% cov (not contender).
- Full-year engine sizing: AT €930,692 (139,294 parcels), CH €392,261 (45,318). Other 7 lanes: not priced (country_not_served).
- **Incumbent baseline:** AT today = DPD PL €4.25 / GLS €4.50 invoice — AP €6.68 is ~50% ABOVE today's AT cost (uncompetitive vs incumbents too). CH today = UPS €9.66 invoice — AP €8.66 BEATS it by ~10% (€1/parcel). CH lane spend today €621k (pop).
- Envelope (AT): side>100 (Sperrgut) 12.0%; chargeable>30 (→30kg cap, near-reject) 1.3%; side>60 41.7%. CH: side>120 reject 2.2%; chargeable>30 0.9%.

## DONE
- Wrote `2_analysis/carrier_overview/sections/austrian_post.md` — all 7 §4 elements, firm badge, Jebrim register.
- Framed as CH-lane winner / AT-coverage-but-uncompetitive. Coverage caveats on CH (84.2%) and AT (rank-6) numbers. Incumbent reality-checks both lanes (AT vs DPD PL/GLS, CH vs UPS).
- Read-only on all sources. No writes outside section file + this quest-log.

## [[S150_e59202cf_carrier-overview-report-design|S150]] d6b — neutral-profile refresh (2026-06-03)
- Re-pulled `cost_slices.profile_position('austrian_post')` + `cheapest_share_profile` after neutral `max(weight_kg, vol/5000)` chargeable-weight fix in `lib/lane_taxonomy.py`. Only one quoted profile figure moved: **Bulky-standard CH €8.94 → €8.80** (8.7960). Compact CH €8.55 unchanged (8.5482), ranks unchanged (CH Bulky-std rank1, Compact rank2), counts unchanged (101 CH / 72 AT, both Large argmin). Profile coverages all clean (CH Bulky-std 84.11%, AT profiles 100%) — no coverage>100% anywhere in the section. AT profile avgs (Compact €5.44, Bulky-std €5.81, Large €13.86) not quoted in prose, untouched. Lane table / anatomy / levers / confidence / take left as-is per brief.
