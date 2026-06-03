# HANDOVER → next session — EU Tender engine builds (DPD PL + GLS)

**From:** S114/S115 (session db60ed8a, 2026-05-27). **Repo:** out-of-tree `bi-analytics-main/NFE/projects/2_EU_tender_2026/2_analysis/carriers/`.
**Both carriers are reviewed + deterministic-ready.** Two engine UPDATES are queued (both engines already exist — these are rebuilds, same pattern as maersk/hermes/dhl_express/austrian_post, NOT from-scratch).

## Task A — `dpd_pl-2.0.0` (UPDATE of existing `dpd_pl-1.0.0`)
Spec: `carrier_responses_to_open_questions/DPD_PL/REVIEW_CONCLUSIONS.md` (→ "Engine to-do"). Existing engine `2_analysis/carriers/dpd_pl/` has `zone_fee.py`, `uplift_per_kg.py`, `customs.py`, `non_sortable.py`, `non_standard.py`.
Changes:
- **zone_fee.py** → CONDITIONAL by postcode (island/ferry/remote only), parse `carrier_responses_to_open_questions/DPD_PL/Table of zone surcharges…2021.pdf` → postcode ranges, match `shipping_zipcode`. (Was blanket per-destination = ~47% of the headline → collapses.)
- **uplift_per_kg.py** → mechanism corrected to `gross = base × (1 + fuel%) + 0.20 flat` (fuel = %·base, NOT per-kg; road+energy+security = flat 0.20/parcel). Reconciled exactly vs the offer "counted surcharges" columns.
- **fuel** = %·base by monthly Orlen band: Jan 4876 / Feb 5037 / Mar 5712 PLN → ladder %. (Ladder is PLN→percent; offer-issue 6771 = 9%.)
- **customs.py** → CH option-1 (44+45), GB option-2 (50/decl amortised + 5.5), NO/BA/RS option-1.
- billable = max(actual, vol/5000); exceed-tech: accept +22.50 for 31.5–~33 kg, reject gross; **line-haul INCLUDED** (no allocation); additional services ~0; tariff-codes ≤3 assumption.

## Task B — `gls-2.0.0` (UPDATE of existing `gls-1.1.0`)
Spec: `carrier_responses_to_open_questions/GLS/REVIEW_CONCLUSIONS.md`. Existing engine `2_analysis/carriers/gls/`.
Surcharge stack: `base → +Energy 20.5% +KlimaProtect 2.5% +Season% (each on base subtotal; Season=0 in Q1) → +Toll (DE national flat 0.38€ / export 5.70% on FULL net invoice) → +Dieselfloater ~4.1% → total`. Plus per-parcel: Delivery-private-address +0.15€ (DE B2C); Big Parcel +0.80€ (>150 L); EFTA clearance (25€ per-CCD/day if set up, else per parcel). **Pre-financing 0 (SEPA), WeighingService 0 (weights supplied).** Sub-region routing via `Postleitzahlen je Zone.pdf`. Oversized: reject girth>300. **Fuel held as a flagged assumption** (Energy 20.5% + Dieselfloater 4.1% flat for the year — principal call; needs review at shortlist). Engine currently assumes FUEL_PCT 0.28 → update to 20.5% + add Dieselfloater + the other surcharges.
Internal-only residuals (don't block): EFTA/CCD decision, Q13 Non-conveyable (offer page 14), GB sub-region (zone PDF GB rows blank).

## Task C — after both: cost_matrix
`python cost_matrix.py` → Q1 per-carrier totals + portfolio ranking shift across ALL engines (maersk-3.0.0 / hermes-2.0.0 / dhl_express-2.0.0 / austrian_post-2.0.0 [all committed] + dpd_pl-2.0.0 + gls-2.0.0). Then `decision_scorer.py` + report regen. **FedEx + DHL Paket still HELD** (round-2 pending). Watch the DPD PL headline — expect it to drop sharply (zone-fee + per-kg→%+flat corrections); GLS Energy 20.5% < old 28% assumption (lower).

## Build pattern (proven on AP/dhl_express)
constants → surcharges → calculate → fixtures (re-date + new-feature + boundary) → CLAUDE.md doc + version history → verify (`PYTHONUTF8=1 python -m carriers.<carrier>.tests.test_engine` + full-pop smoke over `data/population.parquet`) → commit pathspec-scoped local-only (tree has ~80+ unrelated WIP files — NEVER bare `git add`).

## State at handover
- Reviews: DPD PL committed (tender `cf0b6c4`); GLS finalized (committing this session). AP engine committed (`e8ddc62`). HEAD ~`146e9ed`+ (dhl_express S104).
- Brain-side S114/S115 records committed this session-close.
- Both engine builds NOT started — next session's job.
