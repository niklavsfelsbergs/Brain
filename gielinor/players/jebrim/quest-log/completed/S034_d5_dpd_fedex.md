# [[S034_2026-05-22_eu-tender-logic-review|S034]] D5 — DPD PL + FedEx audit (newest engines, high priority)
**Spawned by:** Jebrim, 2026-05-22

## TL;DR
Both engines are internally consistent and the heavy-lift open-question matter (fuel/customs/residential/vol-weight/zone-fee) is already fully captured in ASSUMPTIONS.md + walkthrough docs (`open_questions/dpd_pl.md` 18 entries, `open_questions/fedex.md` 16 carrier + 11 internal). Logic review surfaces **no fresh calc bugs of high severity**; engine-specific decisions (DPD PL NonSortable footprint reinterpretation, FedEx Approach B for 18 kg AHS-Dim lift) check out mechanically against the offer + AHS FAQ. The audit yields ~12 findings, mostly med/low — three are worth Jebrim's attention:

1. **DPD PL `constants.py` lines 71–72 contain a STALE comment** that says NonSortable is "interpreted as: the two smaller dims both >= 70 cm" — but `surcharges/non_sortable.py:30-33` actually keys on `d_max AND d_mid`. The CLAUDE.md + the surcharge file's own docstring agree the engine uses the footprint reading; only `constants.py` is stale. Risk = future reader confusion + audit-trail mismatch. **Med (doc-only, no behavior bug)**.
2. **FedEx service-selection boundary uses `weight_kg` (gross actual) not `billable_weight_kg`** (`calculate.py:171`). Currently consistent because WA #1 forces billable=gross. **If Q5 vol-weight reply lands and v2 activates max(gross, vol)**, a parcel with actual=50/vol=200 stays on parcel branch when arguably it should route to freight. **Low for v1; med to flag for v2 once Q5 closes**.
3. **FedEx freight `base_rate_eur = per_kg_eur * weight_kg`** (`calculate.py:262`) — uses gross weight, not billable. Same v1-correct / v2-watch posture as #2. If freight chargeable should be `max(gross, dim/5000)` once Q5 lands, freight totals re-scale too. **Low for v1; flag for v2**.

The walkthrough docs are unusually complete; this dwarf's value-add is **the three items above** (one stale comment, two v2-readiness watch flags). Everything else mirrors what the walkthroughs already capture.

## DPD PL — calc bugs / wrong assumptions / missing assumptions / OK

### Calc bugs
*(none of high severity — engine is mechanically faithful to the offer)*

- **[low] `cost_uplift_per_kg` evaluates to 0.0 (not null) on ineligible rows**, while `cost_fuel` is null on ineligible (`calculate.py:222-233` deliberately inlined for null-propagation; `pipeline.py:_apply_single` always uses `pl.lit(0.0)` on the False branch). Cosmetic inconsistency vs the documented "null when ineligible" convention. `cost_total_eur` is correctly nulled via `pl.when(eligible).then(total).otherwise(None)` (`calculate.py:250-252`), so downstream aggregations are unaffected. Same pattern present in every sibling engine that uses the shared `_apply_single`. Not worth fixing in DPD PL alone — would be a `_base/pipeline.py` change.

### Wrong assumptions
*(none — every working assumption in ASSUMPTIONS.md matches what the engine does)*

### Missing assumptions
*(none new — every gap I found is already documented as a B/C/F-tier item in `open_questions/dpd_pl.md`)*

### Doc/comment drift
- **[med] STALE COMMENT — `constants.py:71-72`**: "Non-sortable parcel (row 10): 0.50 EUR if base dim >= 70 x 70 cm (interpreted as: the two smaller dims both >= 70 cm)." The bracketed reinterpretation contradicts the actual engine logic in `surcharges/non_sortable.py:30-33` (which uses `d_max AND d_mid` — the footprint = two LARGEST dims reading). `surcharges/non_sortable.py:1-15`, `CLAUDE.md:99-100`, and `ASSUMPTIONS.md:391-401` all correctly document the footprint reading. Recommend a one-line constants.py comment fix to match. No behavior change.

### OK (logic verified against offer/AHS FAQ)
- **Forward-asof on billable_weight_kg** with max band = 31.5 kg matches the offer's "rates priced on billable weight" wording, and the eligibility `over_max_weight` check at 31.5 fires before `no_rate_found` (`calculate.py:194-201`). A 31.51 kg billable → `over_max_weight`, not `no_rate_found`. Verified ordering correct.
- **Volume formula `vol_kg = L*W*H/5000`** via `add_dim_weight(divisor=DIM_DIVISOR=5000.0)` + `add_chargeable_weight(mode="max")` (`calculate.py:99-101`, `_base/supplement.py:65-91`). Matches WA #1.
- **UpliftPerKg tier breakpoint at 20 kg** with 0.29 / 0.34 EUR/kg matches "blue table" rows 2-8 at the 6500-6999 PLN/m3 fuel band (`surcharges/uplift_per_kg.py:53-58`, `constants.py:56-58`). Per-kg multiplier on `billable_weight_kg` (not band ceiling) matches WA #2.
- **Surcharge gating via `base_rate_eur.is_not_null()`** suppresses every conditional surcharge on ineligible rows (`zone_fee.py:26-29`, `customs.py:34-39`, `non_sortable.py:30-33`, `non_standard.py:26-30`, `uplift_per_kg.py:48-49`). Combined with the `eligibility → null base` step (`calculate.py:207-213`), no surcharge can ever fire on a rejected parcel.
- **GB-NI customs = 0** (`constants.py:120`) but zone_fee = 5.50 (`constants.py:101`) — correctly separated; NI is in EU customs union but the per-parcel zone fee still applies per the Picanova rate sheet column K.
- **NonSortable uses `>= 70`** (not `> 70`) for both d_max and d_mid (`non_sortable.py:31-33`, `constants.py:74`). Matches offer text "base dim >= 70 x 70 cm".
- **NonStandard uses `> 150`** strict on `d_max` (`non_standard.py:28`, `constants.py:80`). Below the 175 cm hard reject. Matches Additional services row 11.
- **Migrate-time drops** (`rate_tables/migrate.py:39-50`): UA*/IM* suspended, CH option 2 / GB option 2 dropped per WA #5, option-1 destinations renamed to plain ISO2. ORWO filtered by `source_sheet == "Picanova"`. Faithful to WA #5 + WA #7.
- **Fuel column structural choice** (`calculate.py:222-233`, `constants.py:66`): FUEL_PCT=0.0 because DPD PL fuel is per-kg, bundled into UpliftPerKg. `cost_fuel` column kept for cost-matrix schema compatibility. Correct.
- **Zone-fee + customs join pattern** via `_zone_fee_value` / `_customs_value` scalar columns in `_supplement` (`calculate.py:111-126`), then surcharges read via `pl.col(...)`. Cleaner than per-destination expressions in the surcharge layer. Correct.

## FedEx — calc bugs / wrong assumptions / missing assumptions / OK

### Calc bugs
*(none of high severity)*

- **[low/med — v2 watch] Service-selection boundary `weight_kg > 68`** (`calculate.py:171`) uses gross actual, not `billable_weight_kg`. Currently consistent with WA #1 (billable=gross), but **if Q5 vol-weight reply lands and v2 enables `max(gross, vol)`**, the freight-boundary check would need to lift too — otherwise a 50 kg actual / 200 kg vol parcel routes to parcel branch and hits forward-asof rounding to 70 kg band (which exists on RE only) instead of routing to freight per-kg pricing. Flag for v2 cascade once Q5 closes. **Magnitude:** small subset of parcels — Picanova mean 1.65 kg gross / 3.92 kg vol per the walkthrough; <1% of parcels would exceed 68 kg vol-weight under div=5000.

- **[low/med — v2 watch] Freight rate computation `per_kg_eur * weight_kg`** (`calculate.py:262`) and forward-asof at `weight_col="weight_kg"` (`calculate.py:255`) both key on gross, not billable. Same v1-correct / v2-watch posture as the boundary item above. Freight totals would re-scale if vol-weight enables. Flag for v2.

- **[low] AHS-Dim 18 kg lift in `_supplement` fires before service is selected** (`calculate.py:129-141` runs in `_supplement` before `_attach_zones` and `_select_service`). On freight parcels (weight > 68), the dim_trigger condition could fire, but `max_horizontal(billable_weight_kg, 18)` is a no-op when actual ≥ 18 (which any freight parcel is). So no behavior bug — but the lift expression evaluates on every row regardless of branch. Cosmetic.

### Wrong assumptions
*(none — every WA documented in ASSUMPTIONS.md FedEx section + locked-via-Round-1-curation list matches engine behavior)*

### Missing assumptions
*(none new — every gap is already documented in `open_questions/fedex.md` Blocks/Changes/Clarifies)*

- The walkthrough's B5 (axis interpretation sorted vs literal L/W/H) is correctly surfaced as a fresh question; engine uses sorted dims consistently via `add_sorted_dims` + `length_plus_girth_cm = d_max + 2*(d_mid + d_min)` (`_base/supplement.py:49-53`). No silent assumption — the convention is documented in `_base/supplement.py:13-15`.

### OK (logic verified against offer/AHS FAQ)
- **EUR_PER_PLN = 4.30** applied at migrate to both parcel and freight rate sheets (`rate_tables/migrate.py:157-188`); calculate layer is EUR-only. Per WA + DECISIONS 2026-05-20.
- **REF Zone R-only enforced at migrate** (`migrate.py:208-215`) — nulls non-"R" zone_ref values. Without this, AT 100 kg → REF zone S → no_rate_found. Engine-specific Phase 1 data fix. Documented.
- **Vatican dropped at migrate** — not in `COUNTRY_TO_ISO2` (line 58-154), so inner join drops it (`migrate.py:209`). Engine never tries to price Vatican.
- **AHS-Dimension Approach B** (`calculate.py:129-141`): pre-compute `dim_trigger` in supplement, lift `billable_weight_kg = max(actual, 18)` before rate lookup. Trigger uses same constants as `surcharges/ahs_dimension.py:40-49` so the lift fires iff the surcharge would have fired (with multi-AHS exclusivity respected for the *cost* but not the *lift* — correct per AHS FAQ p.4/p.13: "subject to 18 kg minimum billable weight even if AHS-Dimension itself is not charged"). Verified against fixture `multi_ahs_weight_beats_dimension`.
- **Multi-AHS exclusivity** via `exclusivity_group="multi_ahs"` with priority 1/2/3 = Oversize(55) > AhsWeight(36) > AhsDimension(35). Implemented in `_base/pipeline.py:67-86` (`_apply_exclusive_group` with running `exclusion` flag). Highest-priority match per row wins. Matches AHS FAQ p.16/p.18 effective 2026-01-12.
- **AhsFreight standalone** (no exclusivity_group) for freight branch only via `service == SERVICE_IEF/REF` check (`ahs_freight.py:34-39`). Uses zone-tier-specific d_max thresholds (157 IEF / 178 REF). Matches PDF p.16.
- **AhsWeight uses `weight_kg` (gross)** not billable (`ahs_weight.py:29`). Matches AHS FAQ "actual weight > 25 kg". Note: the Approach B lift to billable=18 doesn't pollute AhsWeight because AhsWeight reads `weight_kg` directly.
- **Oversize uses `weight_kg` (gross)** for the >50 kg trigger (`oversize.py:44`). Consistent with AHS FAQ.
- **Parcel/freight hard caps** branch-aware in `_decide_eligibility` (`calculate.py:296-304`). Mutually exclusive reject ordering: country_not_served → over_max_weight_freight → unauthorized_freight → unauthorized_package → no_rate_found. Verified order is sane.
- **Forward-asof** on `(service, zone, billable_weight_kg)` for parcel (`calculate.py:232-242`) and on `(service, zone, weight_kg)` for freight (`calculate.py:250-260`). Parcel returns per-package EUR directly; freight returns per-kg multiplied by `weight_kg` to get base. Both use `strategy="forward"` (round-up).
- **`add_dim_weight` is NOT called** in FedEx supplement (correct — mode="gross" doesn't reference `dim_weight_kg`). But `lwh_product` is still set by `add_sorted_dims`, which the AHS-Dim and Oversize volume triggers need. Verified `_base/supplement.py:42-44` always populates lwh_product.
- **Inlined `_apply_fuel`** with FUEL_PCT=0.0 produces `cost_fuel = null * 0 = null` on ineligible rows (`calculate.py:332-340`). Matches Hermes/AP convention.
- **Non-mapped countries dropped at migrate** via inner-join with `COUNTRY_TO_ISO2`. 86 countries mapped; rest reject as country_not_served. PR sub-variants consolidated to SJU only (lines 119-120).
- **Vatican absent from COUNTRY_TO_ISO2** so the inner-join drop is the actual mechanism (`migrate.py:60-154`). Even if Phase 1 country_zones lists Vatican with zone "R", it never reaches the engine's `country_zones.parquet`.
- **CY/MT/IS route to IE zone V → no_rate_found** because rates_parcel has no Zone V column. Faithful representation of the offer gap. Verified by fixture per CLAUDE.md.
- **`replace_strict(SERVICE_MAP)` in migrate** (line 162) fails loudly if an unknown service code appears — correct guard.

## Cross-observations

- **Both engines null base_rate on ineligible rows then surcharges gate on `base_rate.is_not_null()`** — a robust pattern that prevents any surcharge firing on a rejected parcel. The cost columns evaluate to 0.0 on ineligible (not null), but `cost_total_eur` is nulled via the final `when(eligible)` gate. Downstream aggregations should treat null totals as the eligibility signal, not the individual `cost_<name>` columns.

- **Both engines preserve the `cost_fuel` column even when FUEL_PCT=0.0** — for cost-matrix schema compatibility. The DPD PL doc explicitly notes fuel is bundled into UpliftPerKg, not a percentage-of-base. FedEx fuel is genuinely unknown (Q1 open) and currently 0. The convention is "always emit cost_fuel, fill in the mechanic when carrier replies" — correct.

- **Both engines apply sorted dims via `add_sorted_dims`** in `_base/supplement.py`, with 1-decimal rounding to avoid floating-point boundary misfires. `length_plus_girth_cm = d_max + 2*(d_mid + d_min)` uses sorted dims consistently. **Picanova mart has ~6% width-as-longest rows** — the sorted-dim convention is necessary for both engines. FedEx walkthrough B5 (axis interpretation sorted vs literal) is the correct carrier-facing question.

- **Engine-specific decisions both check out:**
  - **DPD PL NonSortable footprint reinterpretation** (`d_max AND d_mid >= 70`) — mathematically justified by the 31.5 kg vol-weight cap making the literal "two smaller dims" reading unreachable (70×70×70 cube has vol_kg=68.6). The walkthrough's F1 carrier-confirmation question is correctly scoped.
  - **FedEx Approach B for AHS-Dim 18 kg lift** — single-pass equivalent to two-pass Approach A; AHS FAQ wording permits both. The `_supplement` lift uses identical constants to the AHS-Dim trigger, so behavioral parity with Approach A is preserved.

- **Both engines lack any explicit handling of the offer's "yellow-highlighted minimum-charge cells" (FedEx) or "tolerance band" (DPD PL Additional services rows 34-44)** — both are documented Phase 1 working assumptions (FedEx C3 / DPD PL B4 walkthrough). Engines pass the published rate through forward-asof without a `max(rate, minimum_charge)` floor or a tolerance-band re-lookup. Faithful to the documented WAs.

- **Single-service vs multi-service** — DPD PL is one service (`dpd_classic_outbound`) so service-selection is trivially correct. FedEx auto-dispatches across 4 services with branch-aware logic; the cheapest-eligible policy (RE > IE, REF > IEF) is documented and consistent across `_select_service` (`calculate.py:161-196`).

- **No peak/residential/customs surcharges modelled in either engine for v1.** DPD PL: no peak (offer silent), residential = no module (Picanova ~100% B2C but offer silent), customs only on CH/GB/NO/BA/RS at flat values from `CUSTOMS_EUR` dict. FedEx: no peak/residential/customs at all (all 4 are open Qs). The walkthrough docs correctly flag fuel/customs/residential/vol-weight as the four "blocks-the-cost-number" items on FedEx and zone-fee/fuel/customs-option/exceed-tech-limits/LNH on DPD PL.

## Notes

- Reviewed in this order: `ASSUMPTIONS.md` (DPD PL + FedEx + cross-carrier 2026-05-20/21 entries) → `open_questions/dpd_pl.md` (full 18 entries) → `open_questions/fedex.md` (full 16 carrier + 11 internal) → `carriers/dpd_pl/calculate.py` + constants + 5 surcharges + migrate → `carriers/fedex/calculate.py` + constants + 4 surcharges + migrate → `_base/supplement.py` + `_base/pipeline.py` + `_base/surcharge.py` → `1_offers/picanova/DPD PL/CLAUDE.md` + `FedEx/CLAUDE.md`.
- DECISIONS.md not fully re-read (already covered the 2026-05-20 dpd_pl-1.0.0 + fedex-1.0.0 + 2026-05-21 FedEx Round 1 curation entries via ASSUMPTIONS.md cross-refs).
- xlsx offers not opened directly — would require openpyxl pass, beyond the dwarf scope. Phase 1 transcripts in `offer_summary/*.parquet` are the source-of-truth that both engines load from. Walkthrough docs confirm the transcripts vs xlsx already during Phase 1 build.
- Spot-check fixtures (19 DPD PL / 25 FedEx) all pass per engine CLAUDE.md; not re-run from the dwarf since `tests/` was not in scope and shipping-engine pytest harness changes between Jebrim's sessions.
- **The walkthrough docs are unusually complete** — `open_questions/{dpd_pl,fedex}.md` re-litigate every Phase 1 working assumption, surface fresh items, and quantify impact in EUR. The dwarf's value-add is limited to the three top-of-file findings (stale constants comment + two v2-readiness watch flags) plus the OK validation that the engine logic survives a fresh logic review.

## Hand-off
Returning summary to Jebrim. No carrier-facing question changes; no rebuild required. The one mechanical fix worth queueing is the DPD PL constants.py stale comment (med, doc-only).
