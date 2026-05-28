# Resume — EU Tender DPD PL reply review (S115)

**Status:** in-progress · session db60ed8a · 2026-05-27
**Quest:** `quest-log/in-progress/S115_db60ed8a_eu-tender-dpd-pl-reply-review.md`
**Repo:** out-of-tree `bi-analytics-main/NFE/projects/2_EU_tender_2026`

## Where we are
- DPD PL Round-1 reply received (was mis-filed as "GLS"; renamed `carrier_responses_to_open_questions/DPD_PL/`). **Reviewed — all 11 answered, deterministic-ready for Q1 after a from-scratch `dpd_pl-2.0.0` build.**
- Deliverables done + **COMMITTED** (tender `cf0b6c4`, pathspec-scoped, local-only): `DPD_PL/REVIEW_CONCLUSIONS.md` + reply + DPD PL dispatch status flip. Zone PDF gitignored (`*.pdf`) — on disk, not in git.
- Both Phase-1 cost-inflators resolved FAVOURABLY (zone-fee conditional not blanket; surcharges = fuel%·base + flat 0.20/parcel, not per-kg) → DPD PL likely competitive once built.
- **dpd_pl-2.0.0 build HELD** (principal): GLS reply comes next ("add GLS after we are done with DPD"); build + cost_matrix run once GLS is also reviewed. Brain-side S115 records uncommitted.

## Engine context (important)
- **No `dpd_pl` engine exists in `2_analysis/carriers/` yet** — this is a FROM-SCRATCH build (the others were rebuilds). Phase-1 has a procedural calculator at `1_offers/picanova/DPD PL/calculation/` + extracted rate tables in `offer_summary/`.
- All 4 deterministic engines committed (maersk/hermes/dhl_express/austrian_post); FedEx + DHL Paket HELD (round-2). DPD PL would be the 5th.

## Status update (S115 final) — SEE THE HANDOVER NOTE
**Full handover for the next session: `inventory/eu-tender-engine-builds-handover__db60ed8a.md`.**
- **DPD PL** — reviewed + COMMITTED (cf0b6c4); deterministic-ready. Engine = **UPDATE of existing `dpd_pl-1.0.0`** (NOT from-scratch — corrected; the engine exists with zone_fee/uplift_per_kg/customs surcharges). Build delegated to next session.
- **GLS** — reviewed + FINALIZED (`GLS/REVIEW_CONCLUSIONS.md`); deterministic-ready, **no round-2** (fuel held as flagged assumption; round-2 file superseded). Engine = **UPDATE of existing `gls-1.1.0`**. Build delegated to next session.

## Next concrete steps (next session)
1. Build **dpd_pl-2.0.0** (UPDATE) + **gls-2.0.0** (UPDATE) per the handover note + the two REVIEW_CONCLUSIONS.
2. `cost_matrix.py` re-run + ranking shift across all engines; FedEx + DHL Paket HELD (round-2).
3. Optional doc cascade (Step-8) — cross-carrier CH-customs row (DPD PL opt-1 44+45; GLS 25€ per-CCD/day) + per-carrier status.

## Key engine-build facts (from REVIEW_CONCLUSIONS)
- billable = max(actual, vol/5000); fuel = %·base by monthly Orlen band (Jan 4876 / Feb 5037 / Mar 5712 PLN); road+energy+security = flat 0.20/parcel; zone fee conditional by postcode (parse `Table of zone surcharges…2021.pdf`); CH option-1 (44+45), GB option-2 (50/decl + 5.5), NO/BA/RS option-1; exceed-tech +22.50 for 31.5–~33 kg else reject; line-haul included; additional services ~0 for Picanova flow.
- ⚠️ Reconcile the surcharge mechanism (fuel% + flat 0.20) against the offer's "counted surcharges" columns N–S + Fuel-surcharge-table sheet before building.
