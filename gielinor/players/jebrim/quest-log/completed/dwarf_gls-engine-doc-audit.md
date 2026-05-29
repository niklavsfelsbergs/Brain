# Dwarf trace — GLS engine doc + audit (EU Tender 2026)

**Spawned by:** Jebrim (principal), document-as-audit pass (S121-style)
**Task:** Write `2_analysis/docs/technical/engines/gls.md` per the README template; audit GLS engine constants/order/drift against REVIEW_CONCLUSIONS + ASSUMPTIONS.
**Scope:** GLS only. Read-only on engine code. Write one doc file + this trace.

## What I read
- `carriers/gls/CLAUDE.md`, `calculate.py`, `constants.py`, all `surcharges/*`, `surcharges/__init__.py`
- `carriers/_base/` (pipeline.py, supplement.py, surcharge.py, __init__.py)
- `carrier_responses_to_open_questions/GLS/REVIEW_CONCLUSIONS.md`, `FUEL_SUMMARY.md` (GLS row)
- `docs/ASSUMPTIONS.md` (GLS section), `docs/technical/README.md` (template)
- `tests/fixtures.py`, `tests/test_engine.py` — ran: **12/12 PASS** (gls-2.0.0)

## Constants reconciliation (engine vs REVIEW_CONCLUSIONS) — MATCH
- ENERGY_PCT 0.205, KLIMA_PCT 0.025, SEASON_PCT 0.01 (months 4,5,10,11,12), DIESELFLOATER_PCT 0.041,
  TOLL_INTL_PCT 0.057, TOLL_NATIONAL_EUR 0.38, EFTA 25.0, EURO_DIM_DIVISOR 6000, EURO_DIM_CAP_KG 30, MAX_WEIGHT 40 — all match Q-resolutions.
- Compounding order matches calculator/Q10: base → +Energy/+Klima/+Season (on base) → net_base → +Toll (DE flat / EBP 5.70% on net_base) → +Dieselfloater (on net_after_toll). Verified in `_apply_pct_stack`.

## Audit findings (detail)
1. **[MED] Season gate uses `shop_order_created_date`; Peak uses `ship_date`** — two different date columns for two time-gated surcharges in the same engine. Season has **no column-existence guard** (`_apply_pct_stack` line 337 references `shop_order_created_date` unconditionally), unlike Peak which guards `ship_date` in `_supplement`. A frame without `shop_order_created_date` would raise. Fixtures always supply it so tests don't catch it. Population carries `shop_order_created_date` so prod is fine — but it's a latent crash + a semantic split (order-date vs ship-date) worth a one-line note.
2. **[LOW-doc] `carriers/gls/CLAUDE.md` output table still lists stale `cost_fuel = base*28%`** (lines ~52). That column no longer exists — replaced by the 5-component stack. Engine code is correct; the CLAUDE.md output-column table wasn't fully scrubbed in the 2.0.0 rewrite.
3. **[LOW-doc] CLAUDE.md "Earlier set" fixture list is stale** — claims Malta-airfreight, PEAK-fires-with-ship_date, NC/Big-placeholder-pinned-at-0, FR dim-cap-at-exactly-30 fixtures. None exist in current `fixtures.py` (12 fixtures, different set: DE 1/5kg + Nov season, FR/CH/IT/NO EBP, DE big-parcel/overlength, 3 rejects). Documentation describes coverage the tests don't have.
4. **[LOW-doc] `FUEL_SUMMARY.md` GLS row stale** — line 47 "GLS, Güll — replies not yet in this folder." GLS reply was reviewed [[S115_db60ed8a_eu-tender-dpd-pl-reply-review|S115]] and engine rebuilt gls-2.0.0; FUEL_SUMMARY not updated. Out of my write scope (cross-doc); flag for principal.
5. **[INFO] EFTA figure basis**: ASSUMPTIONS cites ~€278.9k Q1 (11,156 CH/NO parcels, per-parcel reading). Brief/README full-year basis ⇒ ~€1.32M/yr. CCD collapses it to ~€1.9k Q1 (≈€7.6k/yr). Documented both with the Q1-vs-full-year basis distinction.
6. **[INFO] TOLL_INTL modelled per-parcel as % of net_base** — offer states per-invoice; identical in aggregate when invoice=1 parcel. Known/documented (ASSUMPTIONS GLS.toll_grain).
7. **[INFO] Sub-region routing not wired** (IT→North, GB rows blank). Carried residual, refinement not regression.
8. **[INFO] NON_CONVEYABLE hard-off** (`pl.lit(False)`), exclusivity group `bulky` shared with Overlength (priority 1 wins). Document-and-skip per Q13.

## Wrote
- `2_analysis/docs/technical/engines/gls.md` (the deliverable; created `engines/` dir)

Status: COMPLETE. Doc written (11 sections per template); tests re-run 12/12 PASS.
