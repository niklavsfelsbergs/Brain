# RESUME — EU Tender 2026 full-year build (Option 1) — S120 (3760e65b)

**Status:** in-progress. Full-year build started this session (S120), continuing S118/S119.
**Repo:** out-of-tree `bi-analytics-main/NFE/projects/2_EU_tender_2026/2_analysis`. Tender HEAD at start = `f4b767d` (S119).
**Basis:** Option 1 — replay full-2025 actuals on 2026 rate cards. Plan = NEXT.md item 3; detail = DECISIONS.md 2026-05-28 + FULL_YEAR_SCOPING_NOTE.md.

## STEP 5 HANDOFF SPEC (the one remaining step — recommend a fresh session)
Steps 1–4 DONE + verified; the full-year pipeline produces sound numbers (`data/scenarios.parquet` current, 90×14). Step 5 = fuel band + report regen, a substantial precision-sensitive presentation-layer task:
1. **Fix report.py data load:** `report.py` line ~550 `cm = pl.read_parquet(DATA/"cost_matrix.parquet")` is BROKEN (we now write partitioned `data/cost_matrix/`). Switch to `from cost_matrix import load_cost_matrix` + lazy column-pruned `.collect()` of only what the report needs. (decision_scorer already does this — copy the pattern.)
2. **Convert Q1 prose → full-year (CAREFUL, many hardcoded numbers):** report.py was hardened for Q1 in S119. Every "Q1" figure must move to its full-year value or be relabelled: "96.5% of Q1 parcels", "€278.9k Q1" (gls EFTA), "€484k Q1" (dpd_pl CH customs), "Picanova-Stettin 2026 Q1", "Q1 invoiced post-OML/LPS", the §B.13 "real_total_eur (Q1 invoice)" explanation, the assumptions/sensitivity tables. Recompute the material-caveat figures (EFTA/CH-customs) on the full-year matrix.
3. **New framing to surface in prose:** baseline is now **baseline_2026** (re-priced do-nothing, €14.85M) vs **invoice_today** (€14.27M, +€581k delta) — explain the re-pricing + the switchable-only basis; flag **dhl_paket engine +5.5% over-prices the DHL book** (and dhl_paket/fedex/guell HELD = provisional); add the **maersk EU peak €0.25/parcel flagged assumption** (€250k/yr) + ROW-demand deferral to the caveats/assumptions section.
4. **Fuel band (step e):** fuel as a forward/stabilised low/mid/high band per `FULL_YEAR_SCOPING_NOTE.md` + `FUEL_SUMMARY.md` (Iran spike) — likely a sensitivity sweep (re-run scorer at low/mid/high fuel pct per engine) → a savings range, not a point. **May need a principal decision on the low/mid/high values.**
5. **Doc cascade:** NEXT.md, DECISIONS.md (add the S120 full-year-build-executed entry), ASSUMPTIONS.md (maersk peak + ROW-demand deferrals + revisit triggers), REPORT_NOTES.md, cross_carrier_view regen, stray `PEAK_PCT` refs in maersk report.py/migration_plan.html.
6. Regen `decision_report.html` + verify numbers ground-truthed (not pixel-eyeballed).

## Verified full-year headline (post-step-4, for the report)
- baseline_2026 (re-priced do-nothing) = **€14,851,018**; invoice_today (2025 actuals) = €14,269,584; delta +€581,434 (+4.1%).
- Trustworthy ≤6-carrier leader = **renew_maersk_plus_hermes €635,065/yr** mandatory saving (3 uncovered). do_nothing=0 (PASS).
- maersk EU peak now in-engine = €250,430/yr (Oct–Dec, flagged assumption).
- Top raw sets (~€2.2M) exceed 6-carrier cap + lean on HELD fedex/guell/dhl_paket → provisional ceilings.

## COMMIT SCOPE (HELD — principal "always ask before committing")
Tender (out-of-tree, `git commit -- <pathspec>`, local-only no push; ~80+ unrelated WIP files — NEVER bare `git add`):
- `2_analysis/sql/population.sql` (step 1)
- `2_analysis/cost_matrix.py` (step 2 chunking + load_cost_matrix)
- `2_analysis/carriers/maersk/{constants.py, surcharges/peak.py, tests/fixtures.py, tests/test_engine.py}` (step 3 peak + ROW-demand doc + fixtures)
- `2_analysis/decision_scorer.py` (step 4 re-pricing + lazy load)
- (step 5 report.py + docs when done)
- Data parquets (population/cost_matrix/scenarios) are gitignored — not committed.
Brain: jebrim quest-log S120 + this inventory + comms + intent.

## Where we are
**Steps 1–4 DONE + verified — the full-year computational pipeline is complete and produces sound numbers.** Only Step 5 (fuel band + report regen) remains; see the STEP 5 HANDOFF SPEC above. All code changes UNCOMMITTED (held for principal go; scope listed above).

## Build checklist (5 steps — NEXT.md item 3)
- [x] **Step 1 — repoint + widen population.sql.** DONE + verified (2.875M rows materialized).
- [x] **Step 2 — chunk cost_matrix.py by month.** DONE + verified (12 partitions, 25.88M rows, no OOM; `load_cost_matrix()` lazy helper added).
- [x] **Step 3 — seasonal peak/demand.** DONE. 5 carriers pre-wired by date; maersk EU peak wired (€0.25/parcel Oct–Dec flagged, 17/17 fixtures) + ROW demand documented deferral; matrix re-run (maersk peak €250k/yr verified Oct–Dec only).
- [x] **Step 4 — re-price do-nothing baseline on 2026 rates.** DONE + verified. Switchable incumbents (dhl_paket/maersk/dpd_pl) on 2026 engine; UPS/DB-Schenker at invoice. baseline_2026 €14.85M vs invoice_today €14.27M (+€581k). do_nothing=0 PASS. Scorer lazy-loads partitioned matrix.
- [ ] **Step 5 — fuel band + report regen.** SEE "STEP 5 HANDOFF SPEC" above. Substantial precision-sensitive presentation work (faithful Q1→full-year prose/number conversion + fuel sensitivity) — recommend fresh session.
- [ ] **Step 4 — re-price do-nothing baseline on 2026 rates.** 2025 real_* invoice buckets are 2025 prices, NOT the full-year baseline → baseline becomes an engine computation (the incumbent on its 2026 card).
- [ ] **Step 5 — fuel band + re-run scorer + report.** Fuel as a forward/stabilised band (FUEL_SUMMARY.md), not a point. Then decision_scorer.py + report.py on the full-year matrix.

## Next concrete step
1. **Step 5** (fresh session recommended) — fuel band + report regen per the STEP 5 HANDOFF SPEC above. Start by fixing report.py's `cost_matrix.parquet` single-file read → `load_cost_matrix()`, then the Q1→full-year prose/number conversion, then the fuel sensitivity band, then doc cascade + regen + verify.
2. **Commit** steps 1–4 (+ 5 when done) per the COMMIT SCOPE above — principal go required.

## Material flagged assumptions (carry forward — collapse under consolidated customs)
- dpd_pl CH customs €484k (€44/parcel opt-1; mainland-CH €45 now conditional → Campione/Samnaun only).
- gls EFTA €278.9k (€25/parcel CH/NO).

## Carrier-blocked (full-year build does NOT depend on these)
UPS (no offer); FedEx r2 (June ZOOM 2/9 Jun); DHL Paket r2 (Bulky €2.31M); Güll r1. HELD on old engines: fedex/dhl_paket/guell. Provisional in matrix, flagged downstream.

## Files to read first
- `2_analysis/docs/NEXT.md` (item 3 = the 5-step plan) + `docs/DECISIONS.md` (2026-05-28 full-year entry).
- `carrier_responses_to_open_questions/FULL_YEAR_SCOPING_NOTE.md` (the reframe + 3 options).
- `2_analysis/cost_matrix.py` (step 2 target) + `pipeline.py` (the pull runner) + `sql/population.sql` (edited).
- `carrier_responses_to_open_questions/FUEL_SUMMARY.md` (step 5 fuel band).

## Predecessor resume
`inventory/eu-tender-decision-scorer-report-regen-resume__4c2210ee.md` (S119 — report hardening + basis choice).
