# S055 — Shipping Costs Monitoring dashboard, cutover-branch full review

**Session:** S055 (`jebrim-9837afe8`), 2026-05-23.
**Type:** Technical + mathematical review. No code changes — read-only on the target repo.

## Ask (principal, verbatim intent)

> Full technical + mathematical review of the "shipping cost monitoring cutover version."

Resolved to: the **Shipping Costs Monitoring** Next.js dashboard at
`Documents/GitHub/bi-analytics/NFE/dashboards/shipping_costs_monitoring_nextjs/`,
branch **`shipping-mart-cutover`** (the rebuild against gold `shipping_mart`).
Working tree confirmed clean (only untracked `NFE/trading/`, out of scope).
Branch state: **67 ahead / 20 behind `main`** — merge debt noted as a finding.

Two lenses:
- **Technical** — cutover correctness, query/pipeline structure, data-tier routing, scope discipline, fragility, tooling staleness.
- **Mathematical** — bucket invariant, `cost_for_routing`/`final` COALESCE, quota ratios, alert-detection statistics (thresholds, z-scores, CUSUM creep, frozen-baseline, suppression), period machinery.

## Approach

4 read-only review dwarves in parallel:

- **D1** — cost-math + SQL contract (`sql/*.sql`, `pipeline.py` transform/aggregation).
- **D2** — alert/issue detection statistics (`pipeline.py` alert engine, `src/lib/alerts.ts`, `shifts.ts`, tests).
- **D3** — DuckDB serving layer + API routes (`src/lib/db.ts`, `src/app/api/**`).
- **D4** — frontend state + cutover hygiene + tooling (`src/app/page.tsx`, components, `src/lib/*.ts`, `audit.py`, `backtest.py`, DAG, tests, cutover vocab rename).

Each writes severity-tagged findings to `quest-log/in-progress/S055_dN_*.md`. Synthesis re-cut by lens for the principal.

## Turn log

- T1 — Confirmed clean working tree on `shipping-mart-cutover` (67/20 vs main). Oriented on repo structure (pipeline.py 3753 LOC, 30 API routes, ~35 components). Created quest. Spawning 4 dwarves.
- T2 — All 4 dwarves returned. Findings in `S055_d{1,2,3,4}_*.md`. Tally: **2 Critical, 9 High, ~18 Medium, ~19 Low**. Synthesized for principal, grouped by lens.
  - Headline correctness bugs (numbers users see): D1-C1 bucket-invariant unenforced → Breakdown tab can show 0 cost for invoiced-but-no-summary-row shipments; D2-C1 rate_spike cumulative-impact double-count on merged islands → inflates the ranking number.
  - Hard crash path: D3-H2 avg-costs/deviations 500 on pkg+SOG filter combo (PARQUET[tier] raw glob vs pre-agg cols).
  - Security: D4-H1 branch behind main on Next.js CVE-2026-44578 bump (^15.1.0 vs ^15.5.18).
  - Python↔TS divergences (alert vs dashboard show different money/flags): D1-H2, D2-H1, D2-H2, D2-M3.
  - Clean: no SQL injection across 35 routes; reducer signs, div-by-zero guards, weighted aggregation, CUSUM/z-score/suppression math all verified sound; vocab rename consistent where it counts.
  - KB correction: D4 resolved the audit.py/backtest.py staleness contradiction — they were RE-TARGETED post-cutover (commit 0001b36); the vocab-note "things to verify" claim is stale. Flag for next Jebrim alching to fix `bank/notes/projects/shipping_costs_monitoring_nextjs_vocab.md`.
  - Open: principal to triage; offered to write up into repo and/or open fix-quests. ~13 verify-with-data items need a pipeline/data run to size.
- T3 — Principal rulings on the 3 Wave-C decisions:
  - #1 Breakdown basis: **buckets STAY** — the tab must be filterable by charge position, that's its purpose. Fix is reconciliation, not basis-swap: make `SUM(buckets)` total tie out with real cost / other tabs (data check confirms current gap; residual handling for invoiced-but-no-summary-row shipments). "Result should be the same" = totals reconcile.
  - #5 resolution policy: principal asked for my suggestion → proposing flatness-based "settle to new normal" (resolve + re-baseline + freeze cumulative impact when corridor flat for N=5 weeks), not a blind age cap. Awaiting approval of N + optional backstop.
  - #3 divergences: **Python is canonical.** TS (`shifts.ts`) adopts Python defs for shift `eur_impact` (corridor-baseline-avg), `trend_confirmed` (first-half-of-baseline), `low_baseline_vol` (distinct-periods denom). `shifts.test.ts` must be rewritten (it currently locks the old TS behavior). Note: shifts.ts work is file-disjoint from pipeline.py → parallelizable.
- Docs writeup home confirmed: `docs/cutover-review-2026-05-23/findings.md` (matches repo's `docs/<analysis>/findings.md` convention).
- T4 — **Wave A done** (branch-local, uncommitted). next ^15.1.0→^15.5.18 (resolved 15.5.18, CVE-2026-44578 patched), `npm install` clean (EPERM swc-cleanup warning only). #3 crash fix: avg-costs + deviations now route the processed tier through `processedAsDaily()`/`dailyTierExpr()` (rollup cols projected) + tier-aware SOG filter (was silently dropped in processed tier too). `tsc --noEmit` clean before and after install. 4 files changed (package.json, lock, 2 routes).
- T5 — **Data checks** (local DuckDB over 13.58M processed rows, 2024-01..2026-05-21):
  - **C1 LIVE, ~material:** 82,264 invoiced rows (0.69%) / **236,999.95 EUR (0.37%)** have real cost but ALL buckets = 0 → show **0 on Breakdown**, real elsewhere. Clean diagnosis: this is the ENTIRE C1 gap — where a cost-summary row exists, sum(buckets)==real to the cent (max non-zero-row drift 2.88 EUR, total drift == the C1a EUR exactly). Fix: residual→`bkt_unclassified` so Breakdown reconciles + stays bucket-filterable.
  - **H1 LIVE but negligible:** real≤0 when non-null = 2,024 rows (639 zero + 1,385 negative, −33k EUR) ≈ 0.017%. Quota skew immaterial; cheap consistency fix, low priority.
  - **H2 LIVE, material:** 7.1% of shipments are uncosted (cost_for_routing NULL) → Overview avg (÷all) sits ~7% below Breakdown avg (÷costed). Needs the definition call.
  - **H3 LIVE, bounded:** 6.1% multi-product baskets (max 22) → product-grain fan-out over-counts on those; doc/label fix.
- Decisions now all in hand: #1 buckets-stay+reconcile (confirmed by data), #5 N=5 settle-to-normal (taken as approved via "yes all good"), #3 divergences Python-canonical. Wave B unblocked.
- T6 — **Wave A committed** as c4718de (branch-local, not pushed). **Wave B in progress** (uncommitted):
  - **C1 reconcile** (pipeline.py transform): residual (real − Σbuckets) → bkt_unclassified for invoiced rows; runs on cache path too (closes M4 vintage coupling); logs the absorbed magnitude. Validated against 13.5M rows: 82,264 broken → 0; invoiced real == buckets exactly (63,521,407.16, diff 0.0000).
  - **#2 double-count** (pipeline.py _merge_active_duplicates): rate_spike merges now take the earliest island's cumulative_impact (already spans the union window) instead of summing; creep/drift/shift still sum. Test updated + creep-sums test added.
  - **#5 settle-to-new-normal** (pipeline.py _build_single_issue): cost issue flat for BASELINE_WEEKS(5) weeks at the elevated level → resolve as "settled" (flag added) so the frozen-baseline override stops re-arming and the rolling baseline takes over. Active/settled tests added.
  - **Divergences** (shifts.ts, by background dwarf ac9c75c6, reviewed): eur_impact → corridor baseline (whole-euro round), trend_confirmed → first-half-baseline, low_baseline_vol → distinct-weeks denom. shifts.test.ts rewritten. CAVEAT: shift SQL not executed end-to-end (unit tests don't hit it) — runtime smoke of Cost Drivers tab recommended.
  - Tests: **pipeline pytest 84/84 green** (82+2 new); shifts vitest 10/10; tsc clean. (3 pre-existing types.test.ts failures in computeAlertDates — unrelated, pre-existing on clean tree.)
  - **H2 NOT done** — per-costed Overview needs a new `n_routing` column (count of cost_for_routing-non-null) in daily/daily_product summaries + processedAsDaily + overview route. Unlike C1/#5 (value changes), H2 adds a SCHEMA column overview *requires* → overview would error against pre-refresh parquets. Surfaced to principal for implement-now-vs-defer call.
  - Diff so far: 4 files (pipeline.py, shifts.ts, shifts.test.ts, test_pipeline.py). Awaiting principal: commit Wave B? + H2 call.
- T7 — Principal: "commit before continue yes" + "H2 now". **Wave B committed 8b34a0a.** Then **H2 done + committed 165cc5e**: added n_routing (count cost_for_routing non-null) to daily + daily_product summaries + processedAsDaily; Overview (KPI+chart) and Avg Costs heatmap divide by SUM(n_routing). Extended to Avg Costs heatmap too (same metric — leaving it on /shipments would recreate the gap; told principal). Validated: per-costed 5.3867 == Breakdown raw-row 5.3867 (was 5.0022 per-all, 7.7% gap closed). pytest 84/84, tsc clean.
  - **All must-fix (5) + H2 COMPLETE.** Three commits on shipping-mart-cutover (branch-local, NOT pushed): c4718de (CVE+crash), 8b34a0a (C1/#2/#5/divergences), 165cc5e (per-costed avg).
  - Still open: (a) all pipeline.py changes take effect only on next pipeline refresh (C1 buckets, #2/#5 issue values, H2 n_routing) — DAG handles in prod; local needs `python pipeline.py`. (b) Runtime smoke recommended: Cost Drivers tab (shift SQL not executed) + Overview/Avg Costs against regenerated parquets. (c) Findings doc not yet written to docs/cutover-review-2026-05-23/. (d) Medium/Low findings from the review untouched (volume-drop blind spot, generic-trend full-glob, bd_cache concurrency, cache-invalidation, reference.md staleness, vocab-rename cosmetics, 3 pre-existing types.test.ts computeAlertDates failures, etc.). (e) KB: vocab note audit.py-staleness claim is wrong (re-targeted) — fix at next Jebrim alching.
- T8 — Principal: "you can do it all" (findings doc + remaining mediums + runtime smoke). Findings doc written to docs/cutover-review-2026-05-23/findings.md. Spawned 2 background fix-dwarves (file-disjoint, not committing): a0acf03d alert-engine mediums (pipeline.py: D2-M1 drift partial-month skip, D2-M4 volume-drop floor, D2-M5 trend_confirmed early-presence, D1-H1 sum_real gate); ae368e19 serving-layer mediums (D3-H1 share-trend date floors, D3-M5 processedPruned from>to guard [landed], D3-M6 generic-trend window bound, D3-M4 reference.md). After both: review + tests, pipeline regen (python pipeline.py cache) + dev-server smoke, finalize doc, commit mediums. Documented-only: D2-M2, D3-C1/M2/M3, D1-M1/M2/M3.

- T9 — **"Do it all" COMPLETE.** Both medium dwarves reviewed; combined suite green (pytest 89/89, tsc clean). Regenerated local parquets via `python pipeline.py` (cache mode, 260s, exit 0) — confirmed n_routing present in both summaries, processed bucket mismatches 82,264→0, per-costed avg 5.3867. Dev-server smoke (Next 15.5.18, port 3007): Overview/Avg Costs/Breakdown/layer2/carrier-shifts/product-shifts/carrier-share-trends(2024 data)/generic-trend/deviations ALL 200; Breakdown bucket total reconciles to invoiced real cost exactly. Findings doc finalized. Medium fixes + doc committed **75df9c4**.
  - **Final state: 4 commits on shipping-mart-cutover (branch-local, NOT pushed):** c4718de (CVE+crash), 8b34a0a (C1/#2/#5/divergences), 165cc5e (per-costed avg), 75df9c4 (mediums + review doc). Working tree clean (only gitignored data/).
  - Remaining (principal's call): (a) **landing the branch on main triggers CICD** — his decision, not done. (b) pipeline.py value changes need a refresh to take effect (DAG handles in prod). (c) documented-only items: D2-M2 impact weighting (needs data), D3-C1/M2/M3 (cache invalidation/bd_cache concurrency/bypass heuristic), D1-M1/M2/M3, Lows (vocab cosmetics, popstate redirect, simulate-date drop, raw_cache S3, err leak), 3 pre-existing computeAlertDates test failures. (d) KB: fix the vocab-note audit.py-staleness claim at next Jebrim alching.

## Notes / hypotheses to verify

- Vocab note `bank/notes/projects/shipping_costs_monitoring_nextjs_vocab.md` claims `audit.py`/`backtest.py` are pre-cutover and will fail — but commit `0001b36` says they were re-targeted post-cutover. **Vocab note may be stale** — D4 verifies.
- Known issues flagged in the vocab note (hardcoded `order_date >= '2025-01-01'` floors, `/api/generic-trend` full-glob fallback, ORWO inline CASE fallback, Decimal→Float8 cast) — treat as hypotheses, confirm against current code.
