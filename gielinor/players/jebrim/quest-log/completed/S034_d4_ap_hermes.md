# S034 D4 — Austrian Post + Hermes audit
**Spawned by:** Jebrim, 2026-05-22

## TL;DR

Three sanctioned engine decisions (AP CH customs flip to 1.00 EUR, AP multi-service expansion, AP line-haul allocation — all dated 2026-05-18 in `DECISIONS.md`) **have not actually shipped to code**. The AP engine remains at `austrian_post-1.0.0` and prices exactly two services (`paket_at_hd` + `paket_ch_hd`) with `CH_CUSTOMS_INDIVIDUAL_EUR = 0.0` and no `ch_customs.py`/`line_haul_*.py` modules. The DECISIONS log and the engine are out of sync — anyone trusting the docs over the parquet output will under-state AP cost by ~EUR 220k / 6-mo (CH customs ~EUR 33k + line-haul ~EUR 187k) and over-state AT cost by an unknown ~3% (HD-only on shipments that should pick cheaper Kompakt). Hermes has one minor data-vs-code inconsistency (UK in `INTL_COUNTRIES` despite UK being structurally out of project scope) but is otherwise faithful to its provisional v1 framing. The two carrier-Q items most worth re-litigating in this slice: AP CH `Wechselkurs × 1.06` (silent in engine — if CHF rates not pre-converted, every CH total is 6% low) and Hermes vol-weight (still gross-only; documented elsewhere as the EUR 0.5-1.5M Q1 lever and the most plausible cause of the 0.588 bias ratio).

## Austrian Post — calc bugs / wrong assumptions / missing assumptions / OK

### CALC BUGS

**[HIGH] CH customs decision not actually wired.**
- File: `carriers/austrian_post/constants.py:81` — `CH_CUSTOMS_INDIVIDUAL_EUR = 0.0` (still placeholder).
- File: `carriers/austrian_post/surcharges/__init__.py:14-19` — `ALL` lists only `MautAT, SperrgutAT, DieselCH, Peak`. No `ChCustoms` module exists in `surcharges/`.
- Expected: per `DECISIONS.md` lines 245-255 (2026-05-18) and `ASSUMPTIONS.md` line 243, `CH_CUSTOMS_INDIVIDUAL_EUR = 1.00`, new `surcharges/ch_customs.py` firing on every `paket_ch_hd` parcel.
- Magnitude: +1.00 EUR × ~33k CH+LI parcels Q1 = **~EUR 33k Q1 / ~EUR 66k / 6-mo** systematically under-priced on every CH portfolio.
- Engine `ENGINE_VERSION` still `"austrian_post-1.0.0"` (constants.py:8), no bump despite the decision claiming it landed.

**[HIGH] Multi-service expansion not shipped.**
- File: `carriers/austrian_post/rate_tables/rates.parquet` — contains only `paket_at_hd` (35 rows) and `paket_ch_hd` (35 rows). Phase 1's `1_offers/picanova/Austrian Post/calculation/data/rates.parquet` has all five services (`HD`, `Kompakt`, `Kleinpaket`, `KleinpaketPlus`, `CH_HD`).
- File: `carriers/austrian_post/calculate.py:100-110` — `_supplement` routes only to `paket_at_hd` / `paket_ch_hd`. No cheapest-eligible picker exists.
- Expected: per `DECISIONS.md` lines 231-241 (2026-05-18) and PLAN.md §B.7.c, engine should price all four AT services (HD / Kompakt / Kleinpaket / Kleinpaket Plus) with per-service eligibility gates and pick cheapest. AP `open_questions/austrian_post.md` C6 marks this "RESOLVED 2026-05-18" but the resolution is doc-only.
- Magnitude: Phase 1's procedural calc had Kompakt winning ~40% of AT volume at ~7-8% cheaper. v1 engine therefore **over-prices AT lane by ~3% on average** (~EUR 60-80k Q1, AT-residual flip risk).

**[HIGH] Line-haul allocation not implemented.**
- File: `carriers/austrian_post/surcharges/` — no `line_haul_at.py` / `line_haul_ch.py` modules.
- File: `carriers/austrian_post/constants.py` — no `PARCELS_PER_PALLET_AT` / `LINE_HAUL_*` constants.
- Expected: per `DECISIONS.md` lines 217-227 (2026-05-18), per-pallet line-haul allocated as per-parcel surcharge. `ASSUMPTIONS.md` lines 244-246 list these constants as if they exist; they don't.
- Magnitude: ~EUR 1.50 / AT parcel + ~EUR 1.40 / CH parcel at 150 parcels/pallet = **~EUR 187k / 6-mo** systematically under-priced (AP `open_questions/austrian_post.md` B6).

### WRONG ASSUMPTIONS

**[MED] AT fuel held flat at D5 = 4% across replay window with no monthly index lookup wiring.**
- File: `carriers/austrian_post/constants.py:47` — `FUEL_PCT_AT = 0.04`.
- File: `carriers/austrian_post/calculate.py:227-234` — `_apply_fuel` multiplies AT base by single scalar `FUEL_PCT_AT`. No per-month index lookup; no `rate_tables/diesel_schedule.parquet` like Hermes has.
- Expected: per `open_questions/austrian_post.md` B1, monthly BMK Treibstoffmonitor lookup against shipment month. D-tier range 0%–32%; one month at D7 (8%) is +4 pp on AT base = ~+EUR 30k Q1.
- Magnitude: bounded by D-table range; if Q1 2026 BMK averages were higher than D5, AT lane systematically under-priced 1:1 with the pp gap.

**[MED] CH lane silent on CHF→EUR conversion (Wechselkurs × 1.06).**
- File: `carriers/austrian_post/calculate.py:118-155` — `_attach_rate_tables` reads `rate_eur` straight from parquet, no FX multiplier applied.
- File: `carriers/austrian_post/rate_tables/rates.parquet` — column is `rate_eur` (the rename to EUR happened during migrate); but Phase 1's source Excel `Preisblatt Paket AT_CH.xlsx` flags a `Wechselkurs × 1.06` line on the CH surcharge sheet.
- Per `open_questions/austrian_post.md` B5: ambiguous whether the CH rates were already converted into EUR at migrate-time or are CHF requiring × 1.06 to bill EUR.
- Magnitude: if CH rates are CHF, every CH total is ~6% low (~EUR 16k erosion of CH win on 33k shipments).

**[MED] Sperrgut groß fires on every cuboid-overflow AT parcel without considering Rollen Format.**
- File: `carriers/austrian_post/surcharges/sperrgut_at.py:33-46` — fires when `~cuboid_fit & within_hard_limit (L+girth ≤ 360)`. No carve-out for poster tubes that satisfy AP's "Rollen Format: L < 150 cm, Durchmesser < 40 cm" spec.
- Expected: per `open_questions/austrian_post.md` C2, AP factsheet lists Rollen Format as a valid native HD format alongside Quader, NOT as a Sperrgut trigger. A 130 × 10 × 10 cm poster tube currently fires Sperrgut groß (+7.80 EUR) but probably qualifies as Rollen → base rate.
- Magnitude: ~EUR 7.80 × poster-tube count per quarter; quantification blocked on mart shape signal. Phase 1 already observed "AP charges Sperrgut groß more aggressively than incumbents (+EUR 1.04/AT parcel avg)" — long-tube mis-classification likely contributes.

### MISSING ASSUMPTIONS

**[MED] Sperrgut klein (4.00 EUR for non-cuboid ≤ 100×60×60) not modelled.**
- File: `carriers/austrian_post/constants.py:58-60` (comment) and absence in `surcharges/`. Phase 1 WA #9 — no shape signal in mart.
- Magnitude: 4.00 EUR × non-cuboid-fit AT parcel count, currently 0; bounded by Picanova's square-tube fraction.

**[LOW] MAUT_AT rate-change-clause not modelled.**
- File: `carriers/austrian_post/constants.py:56` — `MAUT_AT_EUR = 0.29` is a single scalar, no temporal dimension.
- Expected: AT factsheet states "Änderungen werden mit einer Vorlaufzeit von 4 Wochen bekanntgegeben." `open_questions/austrian_post.md` C4 (NEW).
- Magnitude: small absolute; matters only for multi-year scoring.

**[LOW] 21-29 kg band rounds forward to 30 kg row (asof strategy="forward").**
- File: `carriers/austrian_post/calculate.py:138-148` — `lookup_rate_asof(strategy="forward")` rolls a 25 kg parcel up to the 30 kg band rate.
- Per `open_questions/austrian_post.md` C5, intra-band billing convention is undocumented.
- Magnitude: tail volume (>20 kg); ~EUR 2-4 per affected parcel over-pricing.

### OK (against current contract)

- AT cuboid spec 100×60×60 (`constants.py:26-29`) — factsheet match.
- CH cuboid spec 120×60×60 (`constants.py:32-34`) — factsheet match.
- LI on CH lane (`constants.py:16`) — factsheet match.
- MAUT_AT 0.29 always-on (`surcharges/maut_at.py:21-22`) — factsheet match.
- AT fuel scope: applies to base only, not Maut/Sperrgut (`calculate.py:227-234`) — matches factsheet footnote and cross-carrier rule (`ASSUMPTIONS.md` lines 46-55).
- DIESEL_CH 0.05 flat per CH/LI parcel (`surcharges/diesel_ch.py`) — factsheet match.
- Sperrgut accept band L+girth ≤ 360 (`sperrgut_at.py:39`) — factsheet match.
- MAX_WEIGHT_KG = 30, >30 hard reject — factsheet match.
- AT L+girth > 360 hard reject (`calculate.py:189-192`) — factsheet match.
- CH oversize hard reject (no Sperrgut on CH; `calculate.py:175-182`) — factsheet match.
- Gross-only billing (`calculate.py:97-98`) — Excel surcharge row "Volumengewicht = 0" on every service.

## Hermes — calc bugs / wrong assumptions / missing assumptions / OK

### CALC BUGS

**[LOW] UK leaks into engine despite being structurally out of scope.**
- File: `carriers/hermes/constants.py:17-20` — `INTL_COUNTRIES` ends with `"UK"`.
- File: `carriers/hermes/rate_tables/rates.parquet` — contains 6 UK rate rows.
- Expected: per `DECISIONS.md` 2026-05-12 "Phase 2 population scope locked" (lines 582-595), UK is structurally out of the population. The population SQL filters UK out before the engine ever sees a UK row, so this is dead code today — but it is a scope-misalignment trap (same shape as the Maersk DK-missing bug pre-2026-05-12). `open_questions/hermes.md` Internal #1 already flags this.
- Magnitude: 0 today (SQL pre-filter saves it); a real bug only if any future re-population path leaks UK to the engine.

**[MED — latent] Rate lookup keyed on `weight_kg`, not `billable_weight_kg`.**
- File: `carriers/hermes/calculate.py:139-148` — `lookup_rate_asof(weight_col="weight_kg", ...)` uses the raw input weight.
- File: `carriers/hermes/calculate.py:174-177` — same for eligibility checks (`over_weight` compares against `pl.col("weight_kg")`).
- Under v1 (`mode="gross"`), `billable_weight_kg == weight_kg`, so behaviour is correct today. But once Q1 vol-weight reply lands and `mode="max"` flips, **both rate lookup and eligibility will silently still use gross**, eliminating the entire effect of the vol-weight flip.
- Same latent bug exists in AP (`carriers/austrian_post/calculate.py:139-148`).
- Expected: once mode="max", rate lookup and eligibility should both reference `billable_weight_kg`.

### WRONG ASSUMPTIONS

**[HIGH] Vol-weight rule not modelled (gross-only).**
- File: `carriers/hermes/calculate.py:97` — `add_chargeable_weight(df, mode="gross")`. Per WA #1.
- Already extensively quantified in `open_questions/hermes.md` B1 and `bias_table.md`: 96.7% of Hermes-coverable parcels are dim-heavy at div=5000; mean billable would lift from 1.68 kg to 4.24 kg; estimated **EUR 0.5-1.5M Q1 engine-cost uplift** if confirmed. Single most plausible cause of the 0.588 bias ratio.
- Open carrier Q1 (Round 1 reset 2026-05-19).

**[HIGH] BULKY surcharge held at EUR 0 placeholder.**
- File: `carriers/hermes/surcharges/bulky.py:34-38` — `conditions()` returns `pl.lit(False) & pl.col("base_rate_eur").is_not_null()` (never fires). `constants.py:68` — `BULKY_DE_EUR = 0.0`. No `BULKY_INTL_EUR` constant.
- Expected: DE 8.85 EUR + per-destination intl 5.29-15.00 EUR per offer slide 4. Trigger spec undocumented (Q3 open). Trigger almost certainly depends on shape, which the mart lacks.
- Magnitude: bounded ~EUR 200k Q1 at 5% of 511k parcels firing × ~EUR 8 — quantification blocked on trigger spec.

**[MED] FUEL_PCT held at flat 0% across replay window, no monthly Destatis lookup.**
- File: `carriers/hermes/constants.py:47` — `FUEL_PCT = 0.0`. `_apply_fuel` (calculate.py:220-222) does `base * 0.0`.
- File: `carriers/hermes/rate_tables/diesel_schedule.parquet` exists (29-band Destatis ladder) but is **never read** by `calculate.py`. Dead artefact.
- Expected: per-month lookup against Destatis index per shipment month. Mar 2026 reference = 154.9 → 0% band, correct at the offer-issue moment but unverified for Q1 2026 months.
- Magnitude: ~EUR 26k Q1 per pp of fuel. If any month in Q1 hit a non-zero band, engine systematically low.

**[MED] Intl weight cap inferred at 30 kg (per-country variation unknown).**
- File: `carriers/hermes/constants.py:30` — `MAX_WEIGHT_KG_INTL = 30.0` (inferred from rate-band ceiling).
- File: `carriers/hermes/calculate.py:174-177` — over_weight gate.
- Open carrier Q4. Magnitude: ~885 marginal-reject envelope on Q1; coverage-percentage block, small absolute.

**[MED] DE limits (200 cm length / 450 L volume) applied as intl proxy.**
- File: `carriers/hermes/constants.py:31-32` — `MAX_LENGTH_CM = 200.0`, `MAX_VOLUME_CM3 = 450_000.0` applied uniformly.
- File: `carriers/hermes/calculate.py:179-180` — both lanes hit same gate.
- Per Phase 1 WA #4 / Q4. Magnitude as B4 above.

### MISSING ASSUMPTIONS

**[HIGH] Sub-country / island routing not modelled.**
- File: `carriers/hermes/calculate.py:117-155` — `_attach_rate_tables` keys on `(service, destination_country_code)`. Single rate per ISO2; no postcode lookup.
- Expected: per `open_questions/hermes.md` B5 (NEW), Italy / Spain / Portugal / France / NL / GR have island postcodes that likely uplift; slide 4 lists "Island delivery EUR 8.00" as an additional service.
- Magnitude: ~EUR 15-25k Q1 if 2-3% of IT/ES/NL/PT/GR/FR volume × EUR 8.

**[LOW] MAUT EUR 0.20 rate-change clause not modelled** — same pattern as AP C4. `constants.py:52`. ~EUR 25k/Q swing on a hypothetical mid-year change.

**[LOW] 20-30 kg / 20-31.5 kg top band forward-asof rounding.**
- File: `carriers/hermes/calculate.py:138-148` — `strategy="forward"` rolls 25 kg up to top-band rate.
- Per `open_questions/hermes.md` C4. ~433 parcels affected Q1; <EUR 1-2k.

**[LOW] Hermes not registered in `capability.py`.**
- File: `capability.py` — Hermes absent. `open_questions/hermes.md` Internal #6.
- Eligibility lives inline in `_decide_eligibility` instead of the canonical layer. Same shape as Maersk's not-yet-refactored state. No firing bug; structural debt.

### OK

- CH excluded structurally (CH not in `INTL_COUNTRIES`, line 17-20) — per `DECISIONS.md` 2026-05-15 line 305 ("CH excluded - Picanova does not ship to CH via Hermes").
- HD only (no ParcelShop) — per Picanova HD-only policy. `INTL_COUNTRIES` lists no PUDO service.
- MAUT EUR 0.20 always-on both lanes (`surcharges/maut.py:24-25`) — slide 3 match.
- PEAK EUR 0.25 in Oct/Nov/Dec on `shop_order_created_date` (`peak.py` + `in_period` helper handles year wrap correctly) — slide 9 match. Returns lane correctly OOS.
- DE caps 31.5 kg / 450 L / 200 cm — slide 9 T&Cs match.
- Fuel scope: applies to base only, not MAUT/PEAK/BULKY (`_apply_fuel` only touches base) — matches cross-carrier AT-lane rule.
- Returns OOS — `rate_tables/rates.parquet` carries `returns_flat_eur` column but engine doesn't read it. Correct per cross-carrier scope.
- DE 31.5 kg / intl 30 kg asymmetry is structural (per-service ceiling), not an arbitrary cap — correctly per-service in `_decide_eligibility`.

## Cross-observations

- **Doc drift, AP-specific.** Three `DECISIONS.md` entries dated 2026-05-18 (CH customs flip, multi-service expansion, line-haul scope reversal) are written as if they shipped to the engine. They didn't. `ASSUMPTIONS.md` lines 243-246 list constants (`CH_CUSTOMS_INDIVIDUAL_EUR = 1.00`, `PARCELS_PER_PALLET_AT/CH = 150`, `LINE_HAUL_STETTIN_CH_HOHENEMS_*`, `TRUCKING_DIESEL_PCT_AT`) that don't exist in `constants.py`. The engine VERSION is still `austrian_post-1.0.0` (PLAN.md §B.7.c targets a `2.0.0` / §B.7.e targets `3.0.0`). **All three are §B.7.c/d "open" items in PLAN.md, so the gap is acknowledged in PLAN but not in DECISIONS/ASSUMPTIONS.** A reader picking up DECISIONS.md cold will think AP is +EUR 200k worse than the engine actually reports.

- **Latent `weight_kg` vs `billable_weight_kg` bug in both AP and Hermes.** Rate lookup and eligibility key on raw `weight_kg`, not `billable_weight_kg`. Invisible under `mode="gross"`. Once any vol-weight flip lands (Hermes Q1, AP Q1 = B4) the fix has to touch lookup-key column AND eligibility column AND fixture — easy to miss. Worth a regression-guard fixture written now.

- **Hermes engine consumes `diesel_schedule.parquet` exists / never read.** If/when fuel becomes a monthly lookup, the loader is missing — `calculate.py` would need a per-month join, not just a constant flip.

- **Capability registration asymmetry.** Hermes and Maersk both still implement eligibility inline rather than calling `capability.evaluate()`. AP also implements inline. Not a bug, but the country-scope source-of-truth is split between `constants.<X>_COUNTRIES` and `capability.py` for the engines that *do* use the canonical layer (DHL Paket, DHL Express, GLS, Güll). Drift risk.

## Notes

- Did not run the engines or rebuild `cost_matrix.parquet`. Findings are static-read against engine source vs ASSUMPTIONS.md/DECISIONS.md/open_questions/*.md.
- Did not re-derive impact magnitudes; numbers in this report come from existing `open_questions/*.md` envelopes plus the `DECISIONS.md` 2026-05-18 entries.
- AT Sperrgut/Rollen classification is the cleanest example of a finding where the engine can be wrong in *either* direction — engine currently fires Sperrgut on long tubes (over-pricing if Rollen) and doesn't fire Sperrgut klein on short tubes (under-pricing if non-quader). Both blocked on AP carrier reply.
- The doc-drift finding (DECISIONS log running ahead of code) is mostly cosmetic IF the user knows to read PLAN.md §B.7 status flags as the truth. It's a real reproducibility hazard IF anyone treats DECISIONS.md as the operating source.
