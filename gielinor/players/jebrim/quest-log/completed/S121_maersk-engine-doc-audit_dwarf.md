# S121 (dwarf) — Maersk engine doc + audit (document-as-audit pass)

**Role:** dwarf for Jebrim. **Task:** write `2_analysis/docs/technical/engines/maersk.md` per the technical README template, audit code vs REVIEW_CONCLUSIONS + ASSUMPTIONS as a byproduct.

## What I read
- `carriers/maersk/`: calculate.py, constants.py, CLAUDE.md, surcharges/{__init__,overpack,eu_oversize,row_oversize,row_overweight,peak,ch_zaz,at_toll,de_toll,dk_toll,at_handling}.py, tests/{test_engine,fixtures}.py (16 fixtures).
- `carriers/_base/`: surcharge.py (Surcharge ABC + in_period), supplement.py (add_sorted_dims/dim_weight/chargeable_weight), pipeline.py (apply_surcharges w/ F2 eligibility gate, lookup_rate_asof forward, apply_fuel_pct_of_base/_of_subtotal, stamp_version).
- `carrier_responses_to_open_questions/Maersk/REVIEW_CONCLUSIONS.md`; `FUEL_SUMMARY.md` (Maersk EU + ROW rows).
- `docs/ASSUMPTIONS.md` Maersk blocks (lines 13-25 strict-add, 134-199 post-reply table + [[S120_3760e65b_eu-tender-full-year-build|S120]] peak/ROW-demand entries).
- `docs/technical/README.md` (template).

## Engine snapshot
- Version `maersk-3.0.0` (S099/[[S120_3760e65b_eu-tender-full-year-build|S120]] cascade, PLAN §B.19). Two services HD-only: eu_hd (gross, 26 EU+adjacent, LI→CH), row_hd (FedEx Economy, max(gross,LWH/5000), ~150 ROW via zone map).
- Surcharges (10 in ALL, all BASE phase): OVERPACK 0.40 always-on; EU_OVERSIZE (joined per-country, 5-cap strict-add); ROW_OVERSIZE / ROW_OVERWEIGHT (max(billable*1.27, 31.56), stack); PEAK 0.25 EU Oct-Dec (flagged, peer-anchored Hermes); CH_ZAZ 0 (lit False); AT_TOLL 0.29 / DE_TOLL 0.19 / DK_TOLL 0.05 (always-on by lane); AT_HANDLING 0 (lit False, exception-class).
- Fuel: EU 6.6% base-only (locked); ROW 24.75% = Intl FSC×0.5 (interim snapshot). Both via base*pct in _apply_fuel.
- cost_total = base + fuel + all 10 cost_*; null on ineligible. Reject taxonomy: country_not_served → over_max_weight → oversize_no_surcharge → no_rate_found.

## Audit findings (detail in doc §10)
Engine constants reconcile cleanly to REVIEW_CONCLUSIONS + ASSUMPTIONS (fuel, tolls, oversize scalars, ROW 4th trigger, DE routing=0, peak/ROW-demand deferrals all match what S099/[[S120_3760e65b_eu-tender-full-year-build|S120]] specified). Discrepancies are doc drift + two substantive opens:

1. **ROW fuel scope mismatch (substantive).** FUEL_SUMMARY says Maersk ROW fuel = "base + listed transport surcharges"; engine applies FUEL_PCT_ROW to base only. Possible ROW fuel under-pricing. Small absolute (ROW base ~€238k). Recommend confirm + widen `_apply_fuel` for ROW (apply_fuel_pct_of_subtotal exists) or document base-only deliberately.
2. **ROW AHS exclusivity (substantive).** Engine stacks ROW_OVERSIZE + ROW_OVERWEIGHT (no exclusivity_group, Phase-1 reading); REVIEW Q11 VASS PDF says "only the highest of the three AHS applies" → should be max, not additive. Tiny tail. Recommend exclusivity_group unless Maersk EUR card overrides FedEx.
3. **FUEL_PCT_ROW=0.2475 is current-snapshot, not Q1.** Constants + ASSUMPTIONS both say correct Q1 = lower Jan-Mar weekly Intl FSC×0.5. Documented, non-blocking; flag so it's not read as settled.
4. **carriers/maersk/CLAUDE.md badly stale (biggest doc item).** Says 2.2.0, 13 fixtures, fuel 10% proxy, peak/CH_ZAZ/AT_TOLL/AT_HANDLING all "never 0", surcharge table omits DE_TOLL/DK_TOLL, version history stops at 2.2.0. Read-only here — flagged for principal.
5. **tests/fixtures.py docstring stale** (says 5% fuel + placeholders 0); fixture *data* is current so tests pass — only prose lede wrong.
6. **compare_to_phase1.py parity numbers predate 3.0.0.** Re-run vs unchanged Phase-1 replay.parquet now shows large *expected* deltas (tolls +~€60k, fuel -~€235k). Not a bug; the "architecture parity" guard needs a 3.0.0 baseline or retirement decision.
7. **ES oversize single scalar for tiered surcharge** (€1.00 floor of >80/120/150/200cm ladder) — already documented Q8b. Minor.
8. **`length_plus_girth_cm` dual-purpose** (FedEx 266cm trigger + EU `_max_l2w2h` cap); mathematically identical (L+2W+2H), correct but name obscures dual semantics.

## Wrote
- `2_analysis/docs/technical/engines/maersk.md` — single file, §1-§11 per template. (Created the `engines/` subdir — first engine doc in the pass.)

## Status: doc written, single file. DONE. No code edits, no commit, no other carriers touched.
