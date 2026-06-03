# Resume — EU Tender austrian_post-2.0.0 rebuild (S114)

**Status:** in-progress · session db60ed8a · 2026-05-27
**Quest:** `quest-log/in-progress/S114_db60ed8a_eu-tender-austrian-post-rebuild.md`
**Repo:** out-of-tree `bi-analytics-main/NFE/projects/2_EU_tender_2026/2_analysis/carriers/austrian_post/`
**Picked up** as the next engine while S104 (e50113ed) finishes dhl_express-2.0.0.

## Where we are
- **maersk-3.0.0** — DONE + COMMITTED (tender `3b86d6a`, S102).
- **hermes-2.0.0** — DONE + COMMITTED (tender `990d61c`, S103).
- **dhl_express-2.0.0** — DONE + COMMITTED by S104 (tender `146e9ed`, now HEAD). Sibling finished.
- **austrian_post-2.0.0** — **DONE + COMMITTED (tender `e8ddc62`, S114).** 19/19 fixtures + full-pop smoke clean (€245,154.32, components reconcile). Pathspec-scoped, local-only.
- **FedEx** (`fedex-2.0.0`) + **DHL Paket** — HELD (round-2 pending).

All 4 deterministic-ready engines now rebuilt + committed: maersk 3b86d6a, hermes 990d61c, dhl_express 146e9ed, austrian_post e8ddc62.

## Next concrete step — review 2 NEW carrier replies, THEN cost_matrix
Principal (S114 Turn 3): "just commit" — **answers came in from 2 more providers**; cost_matrix re-run DEFERRED so the ranking reflects the fuller picture. Next thread:
1. **Review the 2 new replies** (Round-1-style: replies vs dispatched open questions → deterministic-ready? clear ASSUMPTIONS bar per S034 ≥5/7 off proxy). Which 2 TBD — candidates from S099 close: DPD PL / GLS / Güll / FedEx round-2 / UPS offer. Check `carrier_responses_to_open_questions/` + `1_offers/picanova/<carrier>/` for the new files; cascade docs (Step-8) in the same pass per the EU-tender doc-sync rule.
2. Rebuild any newly-deterministic engines (same build pattern below).
3. THEN `cost_matrix.py` re-run + ranking shift across ALL rebuilt engines → `decision_scorer.py` + report regen.

## Files to commit (pathspec — NEVER bare `git add`, tree has ~86 unrelated WIP files)
- 2_analysis/carriers/austrian_post/constants.py
- 2_analysis/carriers/austrian_post/calculate.py
- 2_analysis/carriers/austrian_post/surcharges/sperrgut_at.py
- 2_analysis/carriers/austrian_post/surcharges/customs_ch.py (new)
- 2_analysis/carriers/austrian_post/surcharges/linehaul.py (new)
- 2_analysis/carriers/austrian_post/surcharges/__init__.py
- 2_analysis/carriers/austrian_post/tests/fixtures.py
- 2_analysis/carriers/austrian_post/tests/test_engine.py
- 2_analysis/carriers/austrian_post/CLAUDE.md

## Build order — `austrian_post-2.0.0` (PLAN §B.7.c/d)
1. **constants.py** — ENGINE_VERSION 2.0.0; `CH_CUSTOMS_INDIVIDUAL_EUR 0.0→1.00`; CH FX monthly dict (prior-month EUR/CHF ÷ 1.06: Jan 1.011 / Feb 1.017 / Mar 1.032 from ECB Dec 1.0716 / Jan 1.0784 / Feb 1.0940); Sperrgut length>100 trigger const; keep FUEL_PCT_AT 0.04 (Q1 baseline, D-card not public — sensitivity 12%); Maut 0.29 (flag 0.27 early-Q1).
2. **Q4 Sperrgut** (`surcharges/sperrgut_at.py`) — change trigger to `d_max > 100` (longest dim >100cm), keep within L+girth≤360 hard limit. 7.80€.
3. **Q12 CH customs** — new `surcharges/customs_ch.py` (CH/LI lane, fires regardless of ZAZ, 1.00€) + register in `surcharges/__init__` ALL. Fuel-exempt (customs not in diesel base).
4. **Q3 CH FX** (`calculate.py`) — new `_apply_ch_fx`: multiply CH base (and CH surcharges? per review "CH cost carries FX re-scale" — confirm scope: base only vs base+surcharges) by per-order-month multiplier on `shop_order_created_date.dt.month()`. Keyed prior-month.
5. **Q9 CH rate** (`rate_tables/`) — replace Wolfen→CH proxy with Stettin→Salzburg card from offer line 139. Need to extract the actual rate card from `1_offers/picanova/Austrian Post/offer/`. Rebuild paket_ch_hd rows in rates.parquet (keep a builder script for provenance).
6. **Q10/Q11 line-haul** — per principal decision (model-as-ASSUMPTION vs hold). If model: population-allocated per-parcel adder (pallet 120×80×160, density ~150 est → ~€0.75–4.50/parcel; DSV diesel-floating uplift) flagged ASSUMPTION, like dhl_express pickup.
7. **fixtures** (`tests/fixtures.py` + `test_engine.py`) — add `shop_order_created_date` + (if needed) `shipping_zipcode`; new fixtures: CH-customs, CH-FX-by-month, Sperrgut length>100 boundary, line-haul (if modelled). Re-date any fuel-month-sensitive fixtures.
8. **doc** — `austrian_post/CLAUDE.md` refresh + version history.
9. **verify** — `PYTHONUTF8=1 python -m carriers.austrian_post.tests.test_engine` + full-pop smoke over `data/population.parquet` (no error + sane aggregate + new components populated + CH FX/customs fire correctly).
10. **commit** — pathspec-scoped (`git commit -- <explicit files>`, NEVER bare `git add` — tree has heavy unrelated WIP), local-only, "EU tender: austrian_post-2.0.0 rebuild (S114)" + Co-Authored-By trailer.

Downstream (NOT mine alone): `cost_matrix.py` re-run + ranking shift — runs once all rebuilt engines land; coordinate with S104.

## Open decisions / data needs
- **DECISION (surfaced to principal):** Q10/Q11 line-haul — model as flagged ASSUMPTION (dhl_express precedent, density ~150 est) vs hold at 0 pending Picanova ops density. Recommended: model-as-ASSUMPTION for consistency.
- **DATA:** Q9 Stettin→Salzburg rate card — extract from offer (`1_offers/picanova/Austrian Post/offer/`, line 139 ref). If not cleanly extractable, flag and keep proxy with a note.
- **CONFIRM:** Q3 FX scope — re-scale CH base only, or base + CH surcharges? (Review says "CH cost" — lean base + lane surcharges; confirm.)
- **CONFIRM (non-blocking):** Q12 import VAT 8% not refunded — Picanova cost vs consignee pass-through.

## Build pattern (proven hermes/maersk)
constants → surcharges → calculate (fuel/FX/eligibility) → fixtures (re-date + new-feature + boundary) → CLAUDE.md doc + version history → verify (test_engine + full-pop smoke) → commit pathspec-scoped local-only.

## Notes / residuals
- `tests/test_f3_billable_lookup.py` 1 intentional FAIL = standing gross-only guard, not a regression (carries across engines).
- Brain-side S114 records (quest-log/inventory/comms/intent) uncommitted — awaiting principal go (consistent with held S099/S102/S103/S104 brain records).
- Sibling: S104 (e50113ed) live on dhl_express — different carrier subdir; pathspec-scoped commits keep us non-colliding.
