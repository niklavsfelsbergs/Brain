# RESUME — S132 shipping cost-savings (parked 2026-05-31, daily limit)

**Quest:** `quest-log/in-progress/S132_32ff1025_shipping-savings-routing-optimization.md` (full gate + plan there).
**Project root:** `~/Documents/GitHub/bi-analytics-main/NFE/projects/5_shipping_savings/` (all work OUTSIDE the brain).

## Where we are
- **Phase 1 GATE: DONE, GREEN, verified live** (both MCP + harness). Population exported: `data/rerating_population.parquet` (785,330 rows / €5.12M, Feb1–May1 settled-invoice Picanova). Service codes profiled: `data/_service_profile.csv`.
- **Phase 2 (carrier engines): ALL 14 BUILT on disk** (workflow `wf_11cf8aeb-833` got further than expected before park). Every carrier has `specs/<key>.spec.md` + `specs/<key>/` rate tables + `engines/<key>.py` + `tests/test_<key>.py`: ups_eu, dhl_paket, maersk_eu, dpd_pl, db_schenker, dpd_uk, postnord, yodel, gls, ontrac, fedex, usps, asendia, maersk_us.
  - **ALL 14 ENGINES PASS:** `python -m pytest tests/ -q` → **134 passed in 2.12s** (the earlier "timeout" was the shell wrapper, not a real hang). Phase 2 effectively COMPLETE.
  - Scratch debris in specs/ and engines/ (`_*.py`, `_*.txt`, `_scratch`, `_trash`) — extractors' working files; harmless, ignore or sweep.
  - STILL TO CONFIRM at resume: engine ground-truth vs ACTUAL paid (validate_engines) — tests prove fixtures, NOT that re-rating matches reality. That's the real trust gate.
- **Downstream pre-built (ready, untested until engines land):** `lib/build_cost_matrix.py` (Phase 3+4 assembler), `lib/validate_engines.py` (engine ground-truth: each engine must reproduce ACTUAL paid cost on like-for-like before its re-rating is trusted).

## NEXT CONCRETE STEP (resume) — Phase 2 done, start at the honesty gate
1. `python lib/validate_engines.py` — **the real trust gate.** Each engine re-prices the shipments that carrier ACTUALLY carried; compare to actual paid (median + p90 error %). Tests only prove fixtures; THIS proves the rate logic matches reality. Any engine with large self-cost error → fix it before its re-rating of OTHER carriers' parcels is trusted. (No VPN needed — reads the local parquet.)
3. `python lib/build_cost_matrix.py` → `data/cost_matrix.parquet` + `cost_matrix_long.parquet`.
4. **Phase 5 — constraints-aware savings synthesis** (the deliverable's core, MINE not a dwarf): aggregate to actionable lane/segment patterns ranked by IMPLEMENTABLE annual savings. Apply volume-tier/minimum/lane constraints. GUARD the per-parcel mirage (tender lesson: drop-DPD €726k paper / ~€0 real). Each finding = concrete change + euro + constraint check.
5. **Phase 6 — HTML report** + data in `report/`; ground-truth a sample of re-rated shipments vs real invoices; assert cost invariants.

## Key locks (don't re-derive)
- Picanova entity = `source_system IN ('Picturator','PicaAPI') AND shop NOT ILIKE '%sendmoments%' AND shop NOT ILIKE 'ORWO%'`. US=`production_site='PCS CMH'`, EU=rest. (No company_code column — that was a fabricated-gate error.)
- Cost basis: settled-invoice only (orders ≥30d old), annualize ×~4. 'expected' rows excluded.
- EU tender offers EXCLUDED. Active contracts only. Reuse tender CODE patterns, not rates.
- Mart creds: shipping-agent harness (`tcg_nfe`), VPN-only (10.144.x.x).

## Integrity flags to harvest (examine drafts, next alch)
1. Hallucinated a "gate GREEN" from a subagent that returned BLOCKED — never assert subagent output without reading its actual return.
2. False-alarmed "data corruption" that was two different date windows — reconcile window/definition before crying corruption.
