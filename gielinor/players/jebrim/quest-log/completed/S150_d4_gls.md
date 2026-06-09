# [[S150_e59202cf_carrier-overview-report-design|S150]] d4 — GLS section (Carrier Overview Report)

Dwarf d4 for Jebrim. Building `2_analysis/carrier_overview/sections/gls.md`.
Carrier slug `gls`, label GLS, confidence **firm**. Low-cost economy contender; CCD lever ~€279k.

## Progress
- [x] Read PLAN §3+§4
- [x] Read gls constants + engine doc (BigParcel >150L, vol-weight)
- [x] Read REVIEW_CONCLUSIONS + ASSUMPTIONS GLS block (CCD lever)
- [x] Run cost_slices (lane_position, profile_position, cheapest_share_lane, incumbent_baseline, envelope_overlay, lane_pop) + BigParcel litres catchment from population.parquet
- [x] Write section → 2_analysis/carrier_overview/sections/gls.md
- [x] Return summary

## Findings
- **Cost position by lane (avg / Q1 €/parcel, rank):** FR 8.11/8.27 **rank 1 cheapest** (only outright win); Benelux 5.70/5.67 rank2 within-10% (dpd_pl leads 5.36); DE 4.51/4.49 rank3 within-10% (hermes 4.16, dpd_pl 4.48 — near dead-heat); Nordics 10.43/10.33 rank3 within-10% (dpd_pl 10.15); IT 7.45/7.17 rank2 off-pace (maersk 6.21); AT 5.94 rank4; Iberia 8.70 rank4; CH 34.15 rank7 (EFTA customs-dominated); ROW not a contender (25.7% cov, AU/NZ reject).
- **Wins/within-10%:** outright = FR. Within-10% = DE, Benelux, Nordics. Off-pace = IT/AT/Iberia/CH.
- **Avg-vs-count divergence:** GLS wins count-of-cheapest on Benelux (56,858) and Nordics (8,296) despite 2nd/3rd on avg — cheapest on most individual compact parcels there; headline loss is a mix effect. DE cheapest on only 634.
- **BigParcel >150L catchment:** 0.97% of book (€0.80/parcel) — benign. By lane AT 1.33% / Nordics 1.26% / FR 1.21% top; ROW 0.33% low. Overlength >120cm = 3.24% (€1.60). GTC dim reject ~5.6% (60cm shortest-side cap is load-bearing; Iberia 76% / IT 72% skew bulky).
- **Vol-weight rule:** EBP bills max(gross, L·W·H/6000) cap30; **DE gross-only** → structurally cheap on light-bulky DE book. Divisor-6000 = biggest EBP lever.
- **CCD lever (headline):** EFTA 25€/parcel → ~€278.9k Q1 / ~€1.32M/yr across 11,156 CH/NO parcels. CCD (per-day cohort) collapses to ~€1.9k Q1 / ~€7.6k/yr = **~€277k Q1 saving**, re-ranks CH entirely (€34→single-digit base, into contention vs UPS €9.66). Internal Picanova call (fiscal rep), not carrier ask. +fuel-scope flag (~€30–80k compounding sensitivity, held flat).
- **Incumbent:** GLS already invoiced live (DE €4.68, AT €4.50, Benelux €4.50, Nordics €6.11) — engine cost in same neighbourhood (not optimistic). UPS baseline: ~level FR, GLS slightly over IT, GLS uncompetitive CH unless CCD. DB Schenker = freight baseline only.
- **Confidence:** firm. Year-1 rates only. Two flagged inputs (fuel flat; EFTA/CCD) — firm in structure, soft in level.

## [[S150_e59202cf_carrier-overview-report-design|S150]] d4b — surgical profile-lens refresh (neutral ÷5000 chargeable-weight correction)
- Re-pulled `profile_position('gls')` + `cheapest_share_profile` under corrected lib/lane_taxonomy.py (carrier-agnostic max(weight, vol/5000), not GLS ÷6000 matrix dim_weight). Corrected DE per-profile: Compact 4.22, Bulky-standard 4.66, Large 5.58 — matches brief's stale-figure callout.
- **Finding: section quotes NO profile-lens numbers.** gls.md is written lane-level (§4 = lane × avg/Q1/rank from `lane_position`, NOT in scope). Only profile-keyed claim is line 5 "lane-winner on Benelux Large / DE Large / FR Large".
- Verified that claim still holds under corrected lens: Benelux Large (8.53, rank1 cheapest), DE Large (5.58, rank1 cheapest), FR Large (12.77, rank1 cheapest) all remain cheapest=true. Qualitative story intact.
- **No edit to gls.md** — no stale profile figures present; lane table / anatomy / BigParcel / CCD ~€277k / confidence / analyst take all out of scope and untouched. BigParcel >150L litres catchment (population.parquet, lens-independent) left as-is per brief.
