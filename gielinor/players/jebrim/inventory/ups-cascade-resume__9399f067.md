---
quest: S208_9399f067_ups-cascade
sid8: 9399f067
ts: 2026-06-11 23:05
open_dep: carrier_overview_v2 re-derive queued (principal: fresh session)
---

# ups cascade — steps 1–7, 9, 10 DONE + committed; carrier_overview_v2 re-derive remains

**bi-analytics commits:** `5cc59a5` (UPS stack, step 1) + `19bc826` (S208 cascade: carriers/ups + wiring + chain regen incl. the q09-era chain scripts the regen ran through + re-rendered routing/annual HTMLs). Still uncommitted in bi-analytics (NOT S208's): result_investigation q04f–q09e scripts/findings, GLS comparison/, management_briefing/ — closed siblings' scopes, their commit asks remain with Niklavs.

**Status:** cascade core landed + verify PASS. One step open.

## Where we are

- Step 1: UPS stack committed in bi-analytics (`5cc59a5`).
- Steps 2–3: `2_analysis/carriers/ups/` built — port of gated ups-2.0.1, **exact per-shipment parity** (143,909 common parcels, 100% service agreement), 6/6 tests. Eligibility = Standard-served 31-country set; WW-ECO tail rejects (`country_not_served`, set-membership test); Q9 hard limits (70 kg / 274 cm / L+G 419).
- Steps 4–5: capability rows (4 services) + INCUMBENT-with-engine wiring on the 2026q1 track only (`_decision_sets_2026q1`: engine_slug ups, RENEWABLES += ups; full-year `_decision_sets.py` deliberately untouched — S120 reprice hack must not resurface). `build_final` FAMILY_TO_ENGINE += ups; GRI stays keep-side-only.
- Step 6 DECIDED (principal): **line-haul = engine +€0.75/parcel** → `carriers/ups/constants.py` + `docs/DECISIONS.md` 2026-06-11 entry. Flag: Q1 allocation, revisit on material UPS-volume shift.
- Step 7+9: comms UPDATE posted, then full regen: matrix (5.84M rows, 11 engines) → scorer (do_nothing=0 PASS; renew_ups −€50.9k wholesale) → routing → q1_base (reconcile OK) → annual (plan-side UPS peak = engine `ups_peak_if_in_window_eur` on switched cells, 0.269 elsewhere — new `ups_plan_peak_by_dest()` in build_annual.py) → final_report → **verify_report PASS**.
- **NEW CANON: paid 2,955,020 → do-nothing 3,055,317 → plan 2,660,120 = €395,197 Q1 (12.93%) / €1,908,707 ann (12.66%, band 1,882,470–1,934,944). Firm €990,225 / DBS-contingent €918,482. Rate moves €483,133 (unchanged — keep-side invariant verified).** Supersedes S203's 292,636 / 1,442,782.
- Step 8 half + 10: `carrier_responses/CROSS_CARRIER_OVERVIEW.md` UPS row re-written; `UPS/CLAUDE.md` phase status + `findings.md` §9 flipped.

## Next concrete step

**carrier_overview_v2 field-wide re-derive** (`2_analysis/carrier_overview_v2/`) — UPS-with-engine invalidates every carrier's relative claims (S185 rule):
1. Read `PLAN.md` + `verification/ledger.md` + `lib/build_*.py` to map the data pipeline (segments/competitive grid built from the cost matrix; `ups_current` exists as incumbent baseline — the tender UPS engine is NEW).
2. Rebuild `_data/` parquets with the ups engine column; add UPS to CARRIER_LABELS/BADGE/EXEC/EXEC_ORDER in `build_report.py`; write `sections/ups.md` + `_data/hands/ups_card.md`.
3. Re-derive EVERY carrier's prose claims (segment-win counts, superlatives, within-10% sets) from the new grid — reconcile prose to parquet, not to the old card (S180). Re-run report + verification ledger.

(S208 footprint committed — `19bc826`. The v2 re-derive's own footprint gets its own pathspec-scoped commit ask.)

## Open flags

- ⚠ **zV-on-UPS policy:** optimizer routes 1,086 zugeschnittene-Verpackung parcels TO ups (cost-aware — expected-LPS layer priced in and UPS still wins) but S205 ruled zV-on-UPS a routing mistake. Principal call: accept or exclude by policy.
- renew_ups −€50.9k (scorer, wholesale all-or-nothing) vs routing's selective +€103k — the offer wins per-cell, not per-book; report prose should carry this.
- Still open from S206: additional-services PDF (browser fetch), round-2 batch (LPS, OML 400-vs-419, Multi/zone, Express dim+fuel), CH/GB parked, Jebrim alch overdue (13+ examine, 2+ bank drafts).

## Files / paths to read first

1. this file
2. `2_analysis/carrier_overview_v2/PLAN.md` + `verification/ledger.md`
3. `2_analysis/carriers/ups/CLAUDE.md` (the port's contract + caveats)
4. quest-log `S208_9399f067_ups-cascade.md` (full turn log)
