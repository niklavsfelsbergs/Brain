# Resume — EU Tender carrier reply-review (S099)

**Status:** in-progress · session 55ea7bc0 · 2026-05-27 · WRAPPED UP
**Quest:** `quest-log/in-progress/S099_55ea7bc0_eu-tender-carrier-reply-review.md`

## Where we are
Reviewed 5 carrier Round-1/2 replies — **Maersk, Hermes, DHL Express, Austrian Post = deterministic-ready for Q1 after engine rebuild; DHL Paket = BLOCKED on Bulky ~€2.31M → Round-2 drafted.** Each carrier has a `REVIEW_CONCLUSIONS.md` (open-questions block at top) in `bi-analytics-main/NFE/projects/2_EU_tender_2026/carrier_responses_to_open_questions/`. Cross-carrier overview + fuel summary + full-year scoping note written. Web research (3 penguins + 1 curl-dwarf) closed Hermes fuel (Destatis base-2021 ladder), AP FX, DHL Express demand values, Maersk ROW (FedEx International fuel index confirmed — 49.50% reconciles). **Docs cascade done** (status tables + ASSUMPTIONS/DECISIONS/OPEN_QUESTIONS/PLAN/REPORT_NOTES + NEXT.md). **Tender repo committed `74dabe3`** (main, NOT pushed).

**GOAL REFRAME:** decision basis = **full-year cost**; Q1 2026 = the unit-cost reference. Annualisation method **PARKED** (`FULL_YEAR_SCOPING_NOTE.md`).

## Next concrete step (recommended next session)
**Rebuild the 4 ready engines with the confirmed values + re-run the Q1 cost matrix to see the real ranking shift** (engines currently still price on the OLD proxies):
- `maersk-3.0.0` (§B.19): FUEL_PCT_EU 6.6%, ROW Intl-FSC×50%, AT/DE/DK tolls, oversize scalars, ROW 4th trigger (2·L·H>169,901 cm³), DE routing-code 0.
- `hermes-2.0.0` (§B.22): gross-weight (no change), bulky per-country + >120 cm trigger, base-2021 fuel ladder, residential 0.
- `dhl_express-2.0.0` (§B.23): TDI ~30%, DDI ~18%, customs 0, demand Jan1–Feb16, remote-area list, pickup line-haul.
- `austrian_post-2.0.0` (§B.7.c/d): gross-only, no-peak, Sperrgut>100 cm, Stettin→CH rate, CH customs 1.00 (regardless of ZAZ), CH FX, DSV trucking.
- DHL Paket rebuild HELD pending Round-2.

Then (later phase): full-year scoping — feasibility of a 2025 full-year population pull from the mart.

## Awaiting (no action)
DPD PL reply, GLS/Güll/FedEx replies, UPS offer → review each as it lands (its own `REVIEW_CONCLUSIONS.md`).

## Principal actions pending
Send DHL Paket round-2 (`questions_for_carrier_round2.md`) + small follow-ups (Maersk: FedEx service/index + Tier C + demand pass-through; DHL Express: demand zone-map + incoterm + pickup days/week; AP: diesel D-card + import-VAT treatment + parcels-per-pallet from ops).

## Files to read first
- `carrier_responses_to_open_questions/CROSS_CARRIER_OVERVIEW.md`
- `.../FUEL_SUMMARY.md` + `.../FULL_YEAR_SCOPING_NOTE.md`
- `.../<carrier>/REVIEW_CONCLUSIONS.md`
- `2_analysis/docs/PLAN.md` §B.7/19/22/23/24 (rebuild specs) + `docs/NEXT.md`

## Brain side
Uncommitted (awaiting principal go): jebrim quest-log S099, this inventory, keepsake proposal (full-year reframe), comms CLOSING, intent, + memory `feedback_eu_tender_track_doc_updates`. Triage at next alching: the keepsake proposal.
