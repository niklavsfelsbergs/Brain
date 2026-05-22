# S034 D1 — Maersk engine logic audit

**Spawned by:** Jebrim, 2026-05-22
**Scope:** `carriers/maersk` + shared `_base` + offer files / rate-table parquets
**Engine version reviewed:** `maersk-2.2.0`
**Audit anchor:** `2_analysis/docs/ASSUMPTIONS.md` (Maersk + Cross-carrier), `DECISIONS.md` 2026-05-14 / 2026-05-18 cascade, `OPEN_QUESTIONS.md` Maersk, `docs/open_questions/maersk.md`.

## TL;DR

Engine `maersk-2.2.0` is internally consistent with `ASSUMPTIONS.md` for the lanes it prices, but it has **not yet been refreshed for the 2026-05-18 first-round reply** — the four confirmed-additive surcharges (DE Toll 0.19, AT DPD Toll 0.29, DK GLS Toll 0.05, plus the EU fuel midpoint 0.05) are documented as decided but constants still hold pre-reply values, leaving Maersk EU systematically **mispriced by ~+EUR 60k Q1 (tolls under) and ~–EUR 120k Q1 (fuel over)** until `maersk-3.0.0` ships. A latent join-multiplication bug exists in `eu_oversize.parquet` (Sweden and UK duplicated). Italy's oversize row is encoded in a way that makes the surcharge mathematically unreachable. ROW branch is missing one documented oversize trigger and the non-standard parcel surcharge entirely. Several large silent assumptions are not in `ASSUMPTIONS.md` (last-mile vendor mapping for Other Surcharges, remote-area module absence, ROW non-standard parcel).

## Findings — Calc bugs

### F1 — high — Italy oversize row encoded so the surcharge never fires

`rate_tables/eu_oversize.parquet`, row `Italy / GLS`: `max_length_cm=120`, `max_height_cm=170`, all others null, `oversize_surcharge_eur=null` (raw text `"2 € - Lenght 120-300 cm / Height 170-240 cm 2€"`).

- Surcharge value `null` means `_oversize_eur.is_null()` → engine path: any dim breach → `oversize_no_surcharge` reject (`calculate.py:235-251`). Documented as parked v2 in the IT fixture (`tests/fixtures.py:213-220`), but the encoding itself is wrong: `max_height_cm=170` is compared in `_decide_eligibility` against `d_min` (`calculate.py:240`) — the **shortest** sorted dim, which can never exceed 170 cm under the 30 kg / dim-weight envelope. The IT oversize trigger never fires *via height*. Length>120 does fire but rejects rather than pricing the offer's actual €2 charge. Same shape for ES/PAACK (`max_length=max_width=max_height=150, max_lwh=200`).
- Expected: model IT GLS as length-tiered (`>120cm = €2`) and ES PAACK as length-tiered (`>80 = €1.00 / >120 = €1.20 / >150 = €2.50 / >200 = €15.00`). Both feature in Q-DBS-1 of the dispatch (`docs/open_questions/maersk.md` C1).
- Suggested fix: either (a) keep parking but make the assumption explicit (`ASSUMPTIONS.md` lacks an IT/ES entry today); or (b) wire a tiered-by-`d_max` rate join. Today is "wrong assumption + the row that's there can't fire" — worst of both.

### F2 — medium — `eu_oversize.parquet` join multiplies rows on duplicate countries

`eu_oversize.parquet` contains **two rows for Sweden** (Bring + EarlyBird) and **two rows for United Kingdom** (EvriUK + Yodel Mini). `_attach_rate_tables` (`calculate.py:213`) does `df.join(oversize_lookup, on="eu_country", how="left")` with no de-dup. Any SE/UK parcel routed through the EU branch would be **duplicated** in the resulting frame.

- Today this is **latent only** — `EU_COUNTRY_NAME` (`constants.py:17-44`) doesn't include SE or UK, so no row reaches the join. The bug fires the moment SE / FI / UK is added — which is exactly what Q-DBS-2 was about until 2026-05-18 withdrew it. Still load-bearing if `maersk-3.0.0` wires DK Bring entries or any future per-vendor row variants.
- Suggested fix: dedupe at join-time, or restructure `eu_oversize.parquet` so `country` is the unique key (one row per country, multi-vendor handled differently). Add a `validate.py`-style sanity check at engine import that asserts `df.unique('country').height == df.height`.

### F3 — medium — `FUEL_PCT_EU = 0.10` stale vs DECISIONS.md 2026-05-18

`constants.py:61`: `FUEL_PCT_EU = 0.10`. `DECISIONS.md` 2026-05-18 says **0.05 midpoint, carrier-confirmed band 4-6%**. Engine still ships the pre-reply proxy.

- Cost impact: at ~EUR 4.7M EU base Q1, the 5pp over-stamp = **~+EUR 235k Q1 / +EUR 470k 6-mo** of phantom fuel on EU branch. Engine over-prices Maersk by exactly that amount until `maersk-3.0.0` lands per PLAN.md §B.19. Decision exists; engine just hasn't been rebuilt.
- Suggested fix: bump to `FUEL_PCT_EU = 0.05` and update fixtures (currently all reference `* 0.10`).

### F4 — medium — AT DPD Toll / DE DHL Toll / DK GLS Toll confirmed always-on, engine still placeholders

`DECISIONS.md` 2026-05-18 confirmed all three as additive per-shipment. Engine state:
- `surcharges/at_toll.py:18-19`: `pl.lit(False) & (eu_country == "Austria")` — never fires.
- No `surcharges/de_toll.py` exists; no `DE_TOLL_EUR` constant. Engine has zero DE toll uplift on ~280k DE parcels.
- No `surcharges/dk_toll.py` exists.

Cumulative engine **under-pricing** vs reality: +EUR 7k AT + EUR 53k DE + EUR 0.3k DK = **~+EUR 60k Q1 / +EUR 120k 6-mo**. Same `maersk-3.0.0` gate per PLAN.md §B.19, but documenting because today's `cost_matrix.parquet` reflects neither.

### F5 — low — `surcharges/overpack.py` trigger uses `base_rate_eur` after it's nulled on ineligible rows

`overpack.py:22-24`: fires when `base_rate_eur.is_not_null()`. In `_decide_eligibility` (`calculate.py:261-266`) the base rate is nulled for ineligible rows, so `is_not_null()` correctly excludes them. **Correct today**, but it couples the surcharge trigger to a post-eligibility side effect rather than to the `eligible` flag directly. If any future refactor moves the null-out, Overpack silently stops firing on every row. Suggested: switch to `pl.col("eligible") == True`.

### F6 — low — `ROW_OVERSIZE_RATE_PER_KG` / minimum applied to `billable_weight_kg`, but for the `ROW_MAX_L_PLUS_GIRTH_CM > 266` trigger there is no shape-only path

The ROW overweight + ROW oversize stack (no exclusivity group, as documented). When *only* L+girth triggers (small but long parcel, say 130x10x10, weight 1 kg), oversize charge = `max(1.27 × 1, 31.56) = 31.56 EUR`. This matches the rate card ("min 31.56 EUR"), so behavior is correct. Flagged here only because the engine treats "per-kg minimum on a 1 kg parcel" as the same as "per-kg with weight floor of 24.85 kg" — consistent with the offer reading, but a fixture should pin the L+girth-only path explicitly (current `ROW_oversize_and_overweight_stack` fixture combines both at 28 kg).

## Findings — Wrong assumptions

### W1 — high — `OVERPACK_PER_PARCEL = 0.40` always-on rests on Picanova-internal context that's not in code

`ASSUMPTIONS.md` 2026-05-18 documents this correctly: Overpack 0.40 fires today because **Maersk does the sorting for Picanova until in-house sorting deploys**. Engine matches reality. **But the engine code carries no signal of this dependency.** `surcharges/overpack.py` says "we treat it as always-on per the rate card", citing Q17. Once Picanova brings sorting in-house, the engine will silently over-price by **EUR 0.40 × ~470k EU eligible = ~EUR 188k Q1 / ~EUR 376k yr**. There is no in-code mention of the trigger condition (mis-sort signal vs. zero-out). The constant comment in `constants.py:67` says "always fires under customer-overpack model" — wrong framing post-2026-05-18.

- Suggested fix: rewrite `OVERPACK_PER_PARCEL` and `overpack.py` comments to reference the operating-model dependency; add a `_SORTING_IN_HOUSE: bool = False` flag and gate the conditional on it.

### W2 — medium — IT/ES oversize charges parked as "null surcharge → reject" but `ASSUMPTIONS.md` has no entry

`tests/fixtures.py:206-220` says this is parked v2 per PLAN.md §A. `docs/open_questions/maersk.md` C1 has it under "Changes". `ASSUMPTIONS.md` Maersk section has **only one entry** — the 5-cap cumulative reading — and contains no assumption stamp for "five EU lanes (BE, LU, IT, ES, CH) reject as `oversize_no_surcharge` rather than pricing the offer's published surcharge". Magnitude: 945 DBS-incumbent parcels EUR 87k Q1 + broader-population tail. Engine matches its own behavior, but the assumption is silent — meets the definition of "wrong assumption" if you consider the implicit assumption "if surcharge field is null, the lane has no surcharge" to be wrong (reality: surcharge exists, just unparsed).

### W3 — medium — `CH_ZAZ_EUR = 0` and `CH_CUSTOMS_EUR = 0` correct *conditional on Picanova holding ZAZ*; engine has no Picanova-ops gate

`DECISIONS.md` 2026-05-18 "Cross-engine ZAZ: Maersk leg confirms reading B" closes the carrier-side question but leaves Internal #1 (does Picanova hold ZAZ?) open. Engine assumes yes (`ch_zaz.py:20-21` returns `pl.lit(False) & ...` — never fires). If Picanova does NOT hold ZAZ, Maersk's reply was "more detailed review" — unspecified charge per CH parcel × ~11k Q1 CH parcels = unbounded. `ASSUMPTIONS.md` documents the dependency clearly; engine code doesn't.

### W4 — low — `ROW_MAX_L_PLUS_GIRTH_CM = 266`; offer text uses cm and FedEx PL spec is widely 330 cm

`constants.py:88`: `ROW_MAX_L_PLUS_GIRTH_CM = 266.0`. FedEx Polska public spec for IE/IP service is 330 cm L+girth (verified via the carrier's surcharges page referenced in the ROW Surcharges sheet). Phase 1's ROW analysis derived 266 cm from the offer's oversize trigger, not from the hard reject cap. The engine fires `ROW_OVERSIZE` at 266 cm correctly, but the 4th oversize trigger from the offer (`Row 21 of ROW Surcharges: 2xLxH < 169,901 CBM`, see `docs/open_questions/maersk.md` C14) is missing entirely. Net: engine under-prices ROW oversize on a non-cuboid tail (unknown size). Magnitude unknown.

## Findings — Missing assumptions

### M1 — high — Last-mile vendor mapping per Picanova lane is silent

The engine has no notion of *which* last-mile vendor handles a Picanova parcel per country. `Surcharges` sheet "Other Surcharges" lists Toll / Routing Code / Handling Fee entries **per vendor** (AT DPD vs AtPost; DK GLS vs Bring; DE DHL; etc.). `1_offers/picanova/Maersk/CLAUDE.md` lists the actual mapping (AT→DPD AT, DK→GLS, DE→DHL DE, IT→GLS, NL→DHL AMS …), but the engine and rate parquets carry no `vendor` column. Today this is hidden — the four placeholder surcharges (at_toll/at_handling/ch_zaz) are False, so vendor mismatch can't fire — but as soon as `maersk-3.0.0` wires `de_toll.py` etc., the engine has to know *which* DE row to fire (DHL DE Toll 0.19 vs theoretical alternates).

- Where to document: new `ASSUMPTIONS.md` Maersk entry "last-mile vendor mapping is hardcoded per `1_offers/picanova/Maersk/CLAUDE.md` table; rate parquets do not carry vendor". Magnitude: load-bearing for **every** post-2026-05-18 surcharge wiring (DE toll alone = EUR 53k Q1).

### M2 — high — DE DHL Routing Code 0.49 EUR not modelled (new in open_questions, no ASSUMPTIONS row)

`docs/open_questions/maersk.md` C5 / OPEN_QUESTIONS.md flags "Germany DHL DE Germany Routing Code 0.49 EUR" row 161 — engine has no module. If always-on DE → **+EUR 137k Q1 / +EUR 274k 6-mo** on ~280k DE parcels. `ASSUMPTIONS.md` has no stamp for "Routing Code = 0 in v1 pending Q reply". Sits in OPEN_QUESTIONS but the silent-assumption gap is real — the engine writes a cost number for DE that quietly assumes this is zero.

### M3 — medium — Remote-area module absent across all lanes

The Maersk `Remote Areas Surcharges` sheet defines per-kg + per-parcel uplifts for ES Canaries, PT Madeira/Azores, IT Sicily/Sardinia/Calabria, NL Wadden, MT Gozo, FR DOM/TOM, plus a DPD-vendor exception table. Engine has zero modules for any of this. `ASSUMPTIONS.md` has nothing. `docs/open_questions/maersk.md` C11 documents the gap as "~EUR 10-20k Q1 systematic Maersk under-pricing". Silent assumption: every Picanova parcel is in a non-remote postcode (which the mart can't currently verify — postcode column status is internal #7).

### M4 — medium — ROW non-standard parcel surcharge silent

`docs/open_questions/maersk.md` C12 / dispatch item 19: ROW Surcharges row 22 "Packaging | Non Standard Parcel | 1.27 EUR/kg min 31.56 EUR". Engine has no module. Trigger is ambiguous (carrier-Q'd), but engine implicitly assumes 0% firing rate. `ASSUMPTIONS.md` has no stamp.

### M5 — medium — Stettin pickup included silent assumption

Offer text says "Pickup Cost: Included" per `1_offers/picanova/Maersk/CLAUDE.md` line 36 — but no `ASSUMPTIONS.md` Maersk entry locks this. Cross-carrier note: every other engine (DHL Paket Q9, DHL Express Q11, GLS Q6, Güll Q11, AP §B.7.d) had this re-litigated and lifted out of "deferred to v2" once it became a 6-7-figure exposure. For Maersk it's *probably* genuinely in-base (the offer is unambiguous on this line), but the cross-engine asymmetry deserves an explicit stamp — "Maersk Stettin pickup confirmed in-base per offer line; no line-haul module needed". Missing today.

### M6 — low — `Peak` placeholder = 0 but no entry in ASSUMPTIONS.md placeholder table

The `ASSUMPTIONS.md` 2026-05-18 "v1 engine placeholders post Maersk first-round reply" table covers FUEL/OVERPACK/AT_TOLL/DE_TOLL/DK_TOLL/CH_ZAZ/AT_HANDLING/CH_CUSTOMS/MAX_WEIGHT — but **omits PEAK_PCT**. `surcharges/peak.py` is a never-fires placeholder; carrier reply was "share 2025 announcement as proxy pending receipt". Q4 2026 full-year exposure unscoped.

### M7 — low — ROW_DIM_DIVISOR = 5000 is the FedEx Economy default but not in ASSUMPTIONS

`constants.py:77`. Offer-locked per FedEx spec, but not stamped as a working assumption anywhere. Low risk (industry standard) but uncatalogued — flipping would silently reprice every ROW dim-heavy parcel linearly.

### M8 — low — Sorted vs physical L/W/H axes silently assumes sorted

`_decide_eligibility` (`calculate.py:235-244`) compares `_max_l → d_max`, `_max_w → d_mid`, `_max_h → d_min`. `docs/open_questions/maersk.md` B4 (NEW 2026-05-18) flags this as Q22b. `ASSUMPTIONS.md` doesn't stamp "engine reads sorted dims, not physical L/W/H" — affects ~6% of Picanova rows.

## Things checked and OK

- **`_max_l2w2h` strict-add (5th OR)** — both eligibility (`calculate.py:242`) and `EU_OVERSIZE.conditions()` (`eu_oversize.py:41`) consult it correctly against `length_plus_girth_cm`. Math identity (`d_max + 2*d_mid + 2*d_min` ≡ `L + 2W + 2H` on sorted dims) holds.
- **Forward-asof rate lookup** — `lookup_rate_asof` with `strategy="forward"` matches Maersk footnote 1 ("rounds up to next listed weight"). Fixture `AT_HD_1.2kg` validates 1.2 → 1.25 band.
- **Fuel applied to base only, not base+surcharges** — `_apply_fuel` (`calculate.py:274-283`) operates on `base_rate_eur`. Fixture `DE_HD_fuel_invariant_base_only` pins this.
- **`MAX_WEIGHT_KG = 30` hard reject** — matches the 2026-05-18 reply ">30 kg shipments not accepted, rejected". Correctly applied to both branches (`calculate.py:230-233`); ROW uses billable weight for the cap as documented.
- **EU country dict has DK + LI** — matches the 2026-05-12 rate-card verification decision. FR/SE/FI legitimately rejected as `country_not_served` per the existing-Maersk-arrangement carve-out.
- **ROW oversize + overweight stack** — no `exclusivity_group` on either class. Matches Phase 1 reading. Fixture `ROW_oversize_and_overweight_stack` pins it.
- **Capability registry matches engine** — `capability.py` `_MAERSK_EU_COUNTRIES` matches `EU_COUNTRY_NAME` keys; ROW countries derived from `row_zones.parquet`.
- **`CH_ZAZ_EUR = 0` consistent with Maersk 2026-05-18 reply (reading B = waiver)** — conditional on Picanova holding ZAZ (separately tracked).
- **`AT_HANDLING_EUR = 0`** — exception-class confirmed per 2026-05-18 reply; correct placeholder.
- **`CH_CUSTOMS_EUR = 0`** — in-base for B2C clearance per 2026-05-18 reply.
- **Sorted-dim derivation** — `add_sorted_dims` (`_base/supplement.py:23-54`) correctly computes `d_mid = lwh_sum - d_max - d_min` and rounds to 1dp; matches the ontrac-pattern boundary-safety convention.

## Notes

1. **`maersk-3.0.0` rebuild is the umbrella for F3 + F4 + M2 + part of M1.** Until it ships (PLAN.md §B.19), the engine is *consciously* mispriced — the decisions exist on paper, the code doesn't reflect them. Worth flagging in any v2 report that "current engine output trails the carrier-confirmed 2026-05-18 picture by ~EUR 175k Q1 net direction (+60k tolls - 235k fuel)".
2. **F1 (Italy `max_height=170`) is the only finding here that's genuinely a parse/encoding error rather than a deferred-work item.** The "Height 170-240 cm" string in the offer was extracted into a *max-cap* column when it's actually a *trigger-range* spec for the surcharge. This pre-dates the SANITY_CHECK (it's been wrong since `maersk-2.0.0`) and was missed by the §B.1 review which focused on the 5-cap reading.
3. **F2 (Sweden/UK duplicate rows)** has the smell of an extraction-side mistake (one-row-per-carrier rather than one-row-per-country with a vendor field). If Q-DBS-2 ever reopens via the existing-arrangement workstream (Internal #9), it bites immediately.
4. **Cross-engine asymmetry on line-haul**: every other engine has had Stettin pickup re-litigated in May. Maersk's "Pickup Cost: Included" is plausible but worth explicitly stamping in `ASSUMPTIONS.md` rather than leaving silent (M5).
5. **The audit did not find a single calc-bug in `_base` pipeline / supplement / surcharge ABC** — those modules are tight. Most issues sit in data files (parquets) and surcharge configuration, not the framework.
6. **Not covered in this audit:** I did not re-derive any specific lane × weight-band rate against the original xlsx (spot-check only via fixture values, which all use rate-table-sourced numbers); I assumed extraction at parquet boundary is faithful for non-oversize columns. The IT-row finding suggests a fuller extraction audit might find more.
