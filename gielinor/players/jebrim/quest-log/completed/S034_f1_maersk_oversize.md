# [[S034_2026-05-22_eu-tender-logic-review|S034]] / fix F1 -- Maersk EU oversize surcharge encoding

**Date:** 2026-05-22
**Role:** dwarf (Jebrim-spawned)
**Quest:** [[S034_2026-05-22_eu-tender-logic-review|S034]] -- EU tender remediation, fix F1
**Status:** completed

## Summary

Patched `eu_oversize.parquet` to populate `oversize_surcharge_eur` for the five Maersk lanes that shipped with null values (IT GLS, ES PAACK, BE/LU/FR ColisPrive). Engine previously rejected any dim-breaching parcel on these lanes as `oversize_no_surcharge` instead of pricing the offer's real charge. 3,400 parcels recovered; +EUR 37.5k Q1 Maersk total.

## Findings

- **No migration script exists for Maersk.** Unlike `hermes/`, `dpd_pl/`, `fedex/`, the Maersk parquet was authored by hand. Fix landed via a one-shot `_fix_eu_oversize.py` script (kept in place for reproducibility).
- **The IT trigger encoding was already correct.** `max_length=120`, `max_height=170` are oversize TRIGGER thresholds, not hard caps -- consistent with the engine's convention across every other carrier (AT/175 trigger + EUR 23.20 surcharge, BG/175 trigger + EUR 12.77, DE/120 trigger + EUR 21.00). The bug was purely that `oversize_surcharge_eur` was null. Offer raw `"2 € - Lenght 120-300 cm \n Height 170-240 cm 2€"` means EUR 2 flat whenever length > 120 OR height > 170; the upper band-edges (300 cm, 240 cm) are hard caps the engine doesn't model and never has (open Q logged).
- **ES PAACK is irreducibly ambiguous in the current schema.** Offer's tiered surcharge `"> 80 / 120 / 150 / 200 cm: 1.00 / 1.20 / 2.50 / 15.00 €"` cannot be expressed as a scalar. Encoded the smallest tier (EUR 1.00) as conservative best-guess; ES under-priced on the higher dim bands by EUR 0.20-EUR 14.00 per parcel. Carrier follow-up logged: which axis is the ladder measured against, longest dim or L+W+H?
- **CH SwissPost stays null.** Offer raw is literally `-`; the hard reject is the contract reality (already covered by B5 open Q).
- **UK Evri + IE ANPOST volume-tiered surcharges left null.** Both lanes are outside `EU_COUNTRY_NAME` today; volume-trigger semantics need a different mechanic (RemoteArea-style) -- out of F1 scope.
- **Q-DBS-1 in `OPEN_QUESTIONS.md` Maersk section status flipped to "half-resolved 2026-05-22"** with three sub-questions opened (ES tier axis, IT hard-cap clarification, CH intent).
- **Tests pre-existed** as Maersk's `python -m carriers.maersk.tests.test_engine` runner (not pytest). All 14 fixtures pass post-fix; the pre-existing `IT_HD_null_oversize_eur_rejects` xfail-style fixture flipped to `IT_HD_oversize_triggers_2eur`; new `ES_HD_oversize_triggers_1eur` fixture added.

## Magnitude shift (Q1 Picanova, Maersk-eligible 528,721 rows)

| Country | Pre-fix rejects | Post-fix rejects | Recovered parcels | Pre-fix elig EUR | Post-fix elig EUR | Delta EUR |
|---|---|---|---|---|---|---|
| IT | 824   | 0   | 824   | 158,066   | 166,014   | +7,948  |
| ES | 1,121 | 0   | 1,121 | 82,969    | 92,470    | +9,501  |
| BE | 1,267 | 0   | 1,267 | 31,320    | 48,327    | +17,007 |
| LU | 188   | 0   | 188   | 3,163     | 6,249     | +3,086  |
| **Maersk total** | 5,199 | 1,799 (CH only) | 3,400 | 4,286,127 | 4,323,670 | **+37,543** |

EU oversize surcharge alone contributes +EUR 11,645 Q1. Remainder is base + overpack + fuel on recovered parcels. Portfolio-scorer effect not computed (cost matrix is the input layer; whether these now-eligible parcels actually shift Maersk to/from "cheapest carrier" in any lane requires a `portfolio_scorer.py` re-run).

## Files touched

- `bi-analytics-main/NFE/projects/2_EU_tender_2026/2_analysis/_fix_eu_oversize.py` -- new, one-shot fix script with documented encoding rationale.
- `bi-analytics-main/NFE/projects/2_EU_tender_2026/2_analysis/carriers/maersk/rate_tables/eu_oversize.parquet` -- five rows updated.
- `bi-analytics-main/NFE/projects/2_EU_tender_2026/2_analysis/carriers/maersk/tests/fixtures.py` -- IT fixture flipped from xfail-style to expect-surcharge; new ES fixture added.
- `bi-analytics-main/NFE/projects/2_EU_tender_2026/2_analysis/data/cost_matrix.parquet` -- rebuilt via `python cost_matrix.py`.
- `bi-analytics-main/NFE/projects/2_EU_tender_2026/2_analysis/docs/DECISIONS.md` -- new 2026-05-22 entry above the doc-drift entry.
- `bi-analytics-main/NFE/projects/2_EU_tender_2026/2_analysis/docs/OPEN_QUESTIONS.md` -- Q-DBS-1 status flipped to half-resolved with three sub-questions.
- `bi-analytics-main/NFE/projects/2_EU_tender_2026/2_analysis/docs/open_questions/maersk.md` -- C1 status updated with the same.

## Test status

```
PASS  AT_HD_1kg_in_spec
PASS  AT_HD_1.2kg_rounds_up_to_1.25kg_band
PASS  CH_HD_5kg_in_spec
PASS  LI_priced_on_CH_lane
PASS  AT_HD_oversize_triggers_surcharge
PASS  AT_HD_35kg_over_max_weight
PASS  CH_HD_over_dim_no_surcharge_rejected
PASS  KP_country_not_served
PASS  AU_ROW_HD_8kg_in_spec
PASS  ROW_oversize_and_overweight_stack
PASS  BG_HD_l2w2h_triggers_oversize
PASS  IT_HD_oversize_triggers_2eur
PASS  ES_HD_oversize_triggers_1eur
PASS  DE_HD_fuel_invariant_base_only

14 / 14 passed
```

## Open questions logged

1. **ES tier axis** -- the "> 80 / 120 / 150 / 200 cm" ladder needs an axis (longest dim vs L+W+H). Currently engine uses lowest tier EUR 1.00, biasing ES under-priced on larger dim bands. (Q-DBS-1 sub-question, logged in OPEN_QUESTIONS.md + open_questions/maersk.md C1.)
2. **IT hard-cap clarification** -- "Length 120-300 cm" suggests 300 cm is a hard cap; engine ignores upper band-edge. Same for "Height 170-240 cm". Confirm carrier actually rejects > 300 / > 240 cm. (Same Q-DBS-1 bundle.)
3. **CH SwissPost intent** -- offer raw "-" is currently encoded as null = hard reject; B5 already covers this. No new question added.
4. **No PAACK / ColisPrive carriers patched elsewhere.** D1 audit mentioned "Same shape on ES/PAACK per D1 audit" -- ES is patched in this pass. No other carrier engine in the repo uses PAACK or ColisPrive as a sub-carrier (those are Maersk-specific last-mile vendors). No cross-carrier sweep needed.

## Out-of-F1 work I did NOT do

- Did not refactor `surcharges/eu_oversize.py` to express dim-banded tiers. Would require schema change (`oversize_surcharge_tiers` list-of-struct column) + engine logic for tier resolution. Out of F1 scope; logged as the route forward when ES tier-axis carrier reply lands.
- Did not run `portfolio_scorer.py` to compute downstream portfolio shift. Cost matrix rebuilt is the F1 deliverable per brief; portfolio re-run is a separate question.
- Did not touch UK Evri / IE ANPOST -- both lanes out of `EU_COUNTRY_NAME` today, volume-trigger semantics need a different mechanic. Bundle into the same v2 routing/mechanic refactor.
