# [[S034_2026-05-22_eu-tender-logic-review|S034]] D3 — GLS + Güll engine audit
**Spawned by:** Jebrim, 2026-05-22

## TL;DR

Both engines were already exhaustively reviewed on 2026-05-18/19 — `docs/open_questions/gls.md` and `docs/open_questions/guell.md` between them list 11 Blocks/Changes and a Round-1 dispatch of 15 (GLS) + 12 (Güll) questions. This audit re-walked the engine code against current ASSUMPTIONS / DECISIONS / dispatch and surfaced only **new** items the existing review didn't already cover. Highest-severity new findings are mostly **interpretation / code-pattern bugs** rather than wholly new missing modules.

Newly surfaced (not in the open-questions docs as B/C/F/O entries):

- **GLS HIGH** — Airfreight EBP parcels with `dim_weight_kg > 40` reject as `over_max_weight` even when actual weight < 40, because `_decide_eligibility` checks `billable > 40` and airfreight `billable = max(gross, dim)` is **uncapped**. Rate card has a 40-kg top band, so the rejection is conservative but loses revenue-tail.
- **GLS MED** — GTC §4.2 `L+girth ≤ 300 cm` is enforced **universally** in `_decide_eligibility`, but the engine's own constants comment notes the GTC actually applies the cap **only above 30 kg**. Over-rejects ~0.5% per the comment.
- **Güll MED** — `AT_MAX_GIRTH_CM = 300` is interpreted as **L+girth ≤ 300** (`length_plus_girth_cm`), but the PDF wording is "girth measurement max. 300 cm" — could plausibly mean girth-alone `2*(W+H) ≤ 300` (industry default). If the second reading is correct, the engine over-rejects long/thin AT parcels.
- **Güll LOW** — `shipping_zipcode.is_in(AT_EXCLUDED_POSTCODES)` is `.fill_null(False)`'d in `_tag_service` but NOT in `_decide_eligibility`. Outcome happens to be correct, but the inconsistency is a latent regression risk if anyone refactors the boolean wiring.
- **Güll LOW** — `CH_ENERGY_CHF * CHF_TO_EUR` is evaluated at **class-load time** (`ch_energy.py:19`) and `rate_chf * CHF_TO_EUR` at **lookup time** (`calculate.py:196`). Both bake FX into outputs before any per-shipment context — would block any future per-date FX implementation without code change. Already in B2 cross-reference but the **dual-binding-site** detail is new.

Sub-LOW / non-findings: PEAK month/day window is correct for 2026 (CW48+CW49 = Nov 23-Dec 6); `extract.py` `RATE_CARD_TO_ISO2` map intentionally drops sub-region rows (already C5); CH service selection's first-match-wins is structurally cheapest-wins on Picanova mix (no bug today, latent if Bulky ever undercuts PostPac).

## GLS — calc bugs / wrong assumptions / missing assumptions / OK

### Calc bugs

- **HIGH — Airfreight EBP `over_max_weight` rejects dim-only-heavy parcels.**
  - `carriers/gls/calculate.py:250-256` — `over_weight = (... EBP & billable_weight_kg > 40)`; combined with `_supplement` lines 150-152 where airfreight billable = `max(weight_kg, dim_weight_kg)` **uncapped** (the 30-kg cap only applies to non-airfreight, lines 152-154).
  - **What's wrong:** A 5 kg actual / 60 kg dim parcel destined to AL/BA/FO/IS/MK/MT/ME/TR rejects as `over_max_weight`, even though actual weight is well within carrier-acceptable range. The rate card has a 40 kg top band, so any actual-weight ≤ 40 kg parcel should price at the appropriate band; the divisor-6000 dim weight should not gate eligibility on the airfreight branch.
  - **Expected:** Either (a) cap airfreight billable at 40 kg for over-weight purposes (still using uncapped billable for the rate-band lookup, which forward-asof would clamp to the top band anyway), or (b) gate over-weight on `weight_kg > 40` for airfreight EBP rather than `billable > 40`.
  - **Magnitude:** Airfreight countries (AL/BA/FO/IS/MK/MT/ME/TR) are a thin tail of Picanova volume; sub-EUR 5k Q1 likely, but worth a fixture to pin the behaviour either way.

- **MED — `length_plus_girth_cm > 300` reject applied universally; GTC says >30 kg only.**
  - `carriers/gls/calculate.py:258-261` — the code comment itself states *"Combined-length+girth rule applies only above 30 kg per the GTC, but treating it as universal is conservative (rejects ~0.5% more parcels) and matches the 'looser EU default' framing in DECISIONS.md."*
  - **What's wrong:** The constants comment in `constants.py:47` is explicit: `GLS_MAX_L_PLUS_GIRTH_CM = 300.0  # 3.00 m -- only applies above 30 kg per GTC`. Engine consciously over-rejects.
  - **Expected:** Gate the L+girth check on `weight_kg > 30` (or `billable > 30`) to match the GTC wording.
  - **Magnitude:** ~0.5% of population per the comment; combined with the existing under-pricing direction, this is a **coverage-loss** finding rather than a cost finding. Could flip 1-2k parcels into rejection vs eligibility in cost-matrix.

### Wrong assumptions

(All material wrong-assumption candidates already enumerated in `docs/open_questions/gls.md` B1-B6, C1-C8. None new in this pass.)

### Missing assumptions

(All material missing surcharges — WeighingService, ClimateProtect, Pre-financing, EFTA Clearance, Stettin line-haul, DE residential 0.15 EUR — already in B/C. None new.)

### OK

- Service routing DE→BP / 44 EU codes→EBP via `GLS_BUSINESS_PARCEL_COUNTRIES` / `GLS_EURO_BUSINESS_PARCEL_COUNTRIES` (`constants.py:22-30`).
- EBP billable weight = `max(gross, dim)` for non-airfreight, capped at 30 kg only when `dim > gross` (`calculate.py:145-158`). The 30-kg cap applies to the dim **uplift**, not the parcel weight itself — matches PDF p.6 footnote 1 exactly.
- PEAK Nov 23 - Dec 6 in `constants.py:107-108` correctly approximates CW48+CW49 for 2026 (BF 27 Nov falls in week 48 by ISO and week 47 by US convention; engine's window covers both readings).
- `_apply_fuel` runs AFTER `apply_surcharges` so fuel = base × FUEL_PCT applies to base only — matches the cross-carrier "fuel-on-base-only" convention (and is the conservative reading vs the PDF "net invoice" wording flagged in C8).
- TollInternational implemented as `base × 0.057` per-parcel (`surcharges/toll_international.py:28`); aggregate-identical to per-invoice when invoices are clustered (already documented C2).
- Overlength + NonConveyable exclusivity via `bulky` group with Overlength priority 1 — matches PDF p.9 footnote 2.

## Güll — calc bugs / wrong assumptions / missing assumptions / OK

### Calc bugs

- **MED — `AT_MAX_GIRTH_CM = 300` enforced as `length_plus_girth_cm > 300`; PDF wording is ambiguous.**
  - `carriers/guell/calculate.py:255` uses `pl.col("length_plus_girth_cm") > AT_MAX_GIRTH_CM` for AT dim-over rejection.
  - `carriers/guell/constants.py:34` documents `AT_MAX_GIRTH_CM = 300.0  # length + 2 * (width + height)`.
  - **What's wrong:** PDF p.2 wording is "girth measurement max. 300 cm". Industry-standard "girth" alone = `2*(W+H)`; "L+girth" = `L + 2*(W+H)`. The engine uses L+girth, which is the **stricter** reading. If the PDF means girth-alone, the engine over-rejects long/thin AT parcels (e.g., 180×40×40 has L+girth=340 → reject under engine; girth=160 → accept under the alternative reading).
  - **Expected:** Carrier confirmation. Comparable reading on AP factsheet's AT product is `L+girth ≤ 360` explicitly, and on GLS GTC §4.2 is `L+girth ≤ 300` explicitly — both unambiguous. Güll's wording sits in between.
  - **Magnitude:** Picanova canvases/posters near the 180-200 cm length boundary on AT lane could be affected. Sub-EUR 5k Q1 likely; depends on AT volume in the long-thin tail.
  - **Not in `open_questions/guell.md`.** New this review.

- **LOW — `shipping_zipcode.is_in()` lacks `fill_null(False)` in `_decide_eligibility`.**
  - `carriers/guell/calculate.py:237-240` builds `at_excluded = (destination_country_code == "AT") & shipping_zipcode.is_in(list(AT_EXCLUDED_POSTCODES))` with **no** `.fill_null(False)`.
  - Compare to `_tag_service` line 147 which does `.is_in(excluded_postcodes).fill_null(False)`.
  - **What's wrong:** When `shipping_zipcode` is NULL, `is_in` returns NULL, propagating into the reject_reason `pl.when` chain. NULL in `pl.when` does not match the True branch — so a NULL-postcode AT parcel falls through `at_excluded` and is correctly priced. Functional outcome correct, but the **asymmetry** between `_tag_service` (defensive) and `_decide_eligibility` (relying on NULL-propagation semantics) is fragile.
  - **Expected:** Add `.fill_null(False)` for consistency.
  - **Magnitude:** Zero today (Phase 1 PCS-PL data populates shipping_zipcode). Latent bug if any future input lacks the column.

### Wrong assumptions

(All material wrong-assumption candidates already enumerated in `docs/open_questions/guell.md` B1-B4, C1-C5. None new in this pass.)

### Missing assumptions

- **LOW — CH FX bound at module import + lookup time, not parameterised.**
  - `carriers/guell/surcharges/ch_energy.py:19` evaluates `list_price = CH_ENERGY_CHF * CHF_TO_EUR` at **class-load time**. Once Python imports `ch_energy`, the value is baked into the class attribute.
  - `carriers/guell/calculate.py:196` multiplies `rate_chf * CHF_TO_EUR` at **lookup time** (during `_attach_rate_tables`), baking the conversion into `base_rate_eur` before any per-shipment logic runs.
  - **What's wrong:** Both binding sites freeze FX before per-shipment context exists. To implement per-shipment FX (e.g., monthly average against `shop_order_created_date`), both sites need refactoring — class attribute → `cost()` expression, and lookup-time multiplication → per-row expression.
  - **Expected behavior:** Already captured as B2 in the audit doc (CH FX cadence carrier-question). What's **new** here is documenting that the engine has **two** FX binding sites, not one — any FX-cadence implementation is a two-touch change.
  - **Magnitude:** Already covered by B2's +/-EUR 7-8k Q1 envelope.

- **LOW — CH rate_table `weight_band_kg` column unused.**
  - `carriers/guell/calculate.py:194-197` selects only `service, rate_chf` for the CH join, dropping `weight_band_kg`. The rate parquet has a `weight_band_kg = 30.0` column (built in `_build_rate_tables.py:36`) that the engine never consults — flat rates per service.
  - **What's wrong:** Nothing today. Flagged for future-proofing: if Swiss Post ever introduces a weight-banded PostPac structure, this code needs a forward-asof rather than a service join.
  - **Magnitude:** Zero.

### OK

- AT base rate 2.95 (≤2 kg) / 3.25 (2-31.5 kg) loaded from `at_rates.parquet`, forward-asof on `weight_kg` (`calculate.py:181-191`).
- CH PostPac / Bulky service selection branches in `_tag_service` (lines 127-158): cuboid-fit → PostPac, weight-conditional length cap for Bulky (250 cm ≤10 kg / 200 cm >10 kg), girth ≤400. Matches PDF p.4-5.
- AT excluded postcodes (6691/6991/6992/6993) reject as `country_not_served` via the at_excluded branch.
- AT_MAUT 0.30 EUR + AT_B2C 0.15 EUR + AT_BULKY 7.00 EUR (volume > 150,000 cm³) — all fire on every eligible AT parcel for the always-on ones, AT_BULKY conditional on `lwh_product > 150_000` per D2.
- Fuel = `base_rate_eur * FUEL_PCT_AT` for AT parcels only (`calculate.py:300-309`); CH path returns 0.0 (CH uses flat `CH_ENERGY_CHF` instead). Matches WA6 base-only scope.
- `add_chargeable_weight(mode="gross")` — gross weight only, no dim weight. Matches PDF silence on vol-weight + cross-carrier convention.
- AT weight cap 31.5 kg (`MAX_WEIGHT_KG`); CH weight cap 30 kg (`CH_MAX_WEIGHT_KG`) — both correct per offer pages 2 and 4.

## Cross-observations

- **Engine-vs-comment drift.** GLS `calculate.py:258-261` flags its own L+girth-universal-cap behaviour as "conservative" in the comment, then implements it that way. The comment is correct that the GTC wording reads as ">30 kg only", so the engine is consciously divergent from the contract. Worth deciding whether to flip the engine (small coverage gain) or update the open-questions doc to ratify the conservative reading.
- **`fill_null(False)` discipline.** Güll `_tag_service` is defensive on `shipping_zipcode`, `_decide_eligibility` is not. Trivial to align; worth doing while touching the file for any other reason.
- **FX dual-binding.** Güll engine binds CHF→EUR at two distinct lifecycle points (class-load + lookup-time). Any future per-shipment FX work is a two-touch change. Comparable carriers (FedEx EUR_PER_PLN, FX handling) bind at migrate time only — single touchpoint cleaner.
- **Airfreight billable + over_weight interaction.** GLS engine's airfreight branch and EBP over-weight branch don't compose well: the uncapped billable design works for rate-band lookup (forward-asof clamps to 40 kg top band naturally) but then the over_weight gate rejects what the rate table would have priced. The same pattern would bite any carrier engine that uses uncapped billable + a billable-based over-weight check.
- **No structural drift from the 2026-05-19 dispatches.** Both engines match the assumptions/decisions on disk. The new findings here are code-pattern items, not contract-vs-engine drift.

## Notes

- Audit performed by reading both engines top-to-bottom (calculate.py, constants.py, all surcharge modules) plus `_base/supplement.py`, `_base/surcharge.py`, `_base/pipeline.py`. Rate tables inspected via the existing parquets and extract scripts.
- The pre-existing `docs/open_questions/gls.md` (6 Blocks / 8 Changes / 1 Clarify / 6 Out-of-engine + 17 confirmed-correct items) and `docs/open_questions/guell.md` (4 Blocks / 5 Changes / 3 Clarifies / 9 Out-of-engine) are comprehensive on contract-vs-engine drift; this audit consciously avoided recapitulating their findings and focused on engine-code shape issues.
- SANITY_CHECK 2026-05-13's GLS ~EUR 250-400k/yr legitimate-surcharge envelope is already fully decomposed in the open-questions B1-B6 entries (WeighingService EUR 250k Q1 + ClimateProtect EUR 67k Q1 + Pre-financing EUR 130k Q1 + EFTA Clearance up to EUR 286k Q1 + DE Residential EUR 49k Q1 + Stettin line-haul EUR 500k-1M / 6-mo) — the envelope is conservative if anything.
- Güll's 2026-05-19 sprinter correction (Picanova uses 955 EUR/sprinter inbound, not self-truck) is logged in `DECISIONS.md` and Q10 dispatch; engine still doesn't allocate, ~EUR 40k Q1 / EUR 80k 6-mo unmodelled (matches B4 in the open-questions doc + Internal #3).
- FX (Güll CHF→EUR) magnitude per the open-questions B2 envelope is +/-EUR 7-8k Q1 / +/-EUR 15k 6-mo — the dual-binding-site finding above doesn't change the envelope, only the implementation footprint of any fix.
