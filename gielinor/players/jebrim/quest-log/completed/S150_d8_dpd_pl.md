# [[S150_e59202cf_carrier-overview-report-design|S150]] d8 — DPD PL carrier-overview section

Dwarf d8 for Jebrim. Building `sections/dpd_pl.md` (Carrier Overview Report).
Slug `dpd_pl`, label **DPD PL**, badge **firm** (incumbent — DPD POLAND, ~247k parcels).

## Steps
- [ ] Read PLAN §3/§4
- [ ] Read constants.py + CLAUDE.md + engine doc dpd_pl.md
- [ ] Read REVIEW_CONCLUSIONS + ASSUMPTIONS DPD PL block (CCD ~€484k)
- [ ] Run cost_slices
- [ ] Write section
- [ ] Return summary

## Findings
- Slices ran clean. DPD PL priced 8/9 lanes (ROW non-contender, 7.3% cov).
- Wins (cheapest avg, contender): **Benelux** €5.36 (rank1), **Nordics** €10.15 (rank2 but cheapest-flag true — Maersk Nordics non-contender 29% cov, so DPD PL is cheapest among contenders).
- Within-10%: **DE** €4.48 (vs Hermes €4.16), **FR** €8.47 (vs GLS €8.11).
- Off-pace: AT rank5 (€5.98 vs Güll €4.33), IT rank3 (€8.14 vs Maersk €6.21), Iberia rank3 (€8.06 vs Maersk €5.60).
- **CH disaster**: €52.94/parcel rank8 (worst) — driven by €44 option-1 individual customs. This is the CCD lever.
- avg-vs-count divergence: Benelux cheapest-share 113,798 parcels (huge); DE only 1,796 cheapest-of (Hermes/GLS take most) despite within-10% avg — DPD PL is *broadly close* on DE but rarely THE cheapest.
- Engine-vs-current-DPD-invoice: new offer runs ABOVE today's invoice on its live lanes — AT €5.98 vs €4.25, Benelux €5.38 vs €4.67, FR €7.33 vs €4.26 (+72%). Nordics exception: €15.88 vs €21.66 (cheaper). Current DPD book = 247,253 parcels, €1.12M invoiced.
- CCD lever: €484k Q1 (€42.76 × ~10k CH parcels) = €2.32M/yr full-year (~52.5k CH parcels × €44). Collapses CH ~€52.94 → ~€10/parcel.
- UPS baseline beats DPD PL on its overlap lanes (CH UPS €9.66, Benelux €9.44, DE €5.64).
- Envelope: 38.3% book side>60cm; DPD PL no 60cm cliff (its surcharges: non-sortable 0.50 @70×70 footprint rare, non-standard 3.70 @>150cm rare, zone fires ~0.29%). Structurally clean on this book.
- [x] Section written.
