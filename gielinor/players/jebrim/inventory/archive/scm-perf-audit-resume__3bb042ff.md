---
quest: S147_scm-perf-audit
sid8: 3bb042ff
ts: 2026-06-02 (sess-4)
open_dep: Tranche-3 serving re-point COMMITTED + PUSHED (2 stacked branches on picanova/bi-analytics). PRs to OPEN + MERGE (pipeline first, then refresh DAG regen, then serving — S098 deploy order). Then app-run session for item 7 + client useSWR. Pipeline branch gained a 3rd commit (inflight_n tier col) from the live-validation fix.
---

# S147 — SCM Tranche-3 (serving re-point) — resume (sess-4)

**Status:** Tranche-3 code-complete, typechecked, live-validated, **COMMITTED + PUSHED**.
- Pipeline branch `feat/scm-pipeline-rowgroup-sort` = 3 commits: `8b9a232` (sort+row-group), `9e109c0` (tiers Change-2/3), `93acb75` (inflight_n amend). Pushed.
- Serving branch `feat/scm-serving-repoint` = `65bf022` (items 1-6), stacked on `93acb75`. Pushed.
- PRs (gh absent — open manually): pipeline `compare/main...feat/scm-pipeline-rowgroup-sort`; serving (stacked) `compare/feat/scm-pipeline-rowgroup-sort...feat/scm-serving-repoint`.
- **Merge/deploy order FIXED:** pipeline PR merge → refresh DAG regenerates tiers (incl. `transit_daily.inflight_n`) → THEN serving PR (else routes 500 on the missing column — S098).

## What was built this session (sess-4, sid 3bb042ff)

Branch `feat/scm-serving-repoint` (stacked off `feat/scm-pipeline-rowgroup-sort`), worktree `_scm-pipeline-sort`.

**Serving branch (uncommitted):**
- **Item 1 — deviations trend → `deviations_summary`** (`deviations/route.ts`). Exact-by-construction (Change-3 sum_real/sum_expected).
- **Items 2+3 — transit tier re-point** (`db.ts` + 4 of 5 transit routes). `db.ts`: `transit_daily` source, `transitTierExpr`/`processedAsTransitDaily` (SOG fallback), `transitBinsList`/`transitBinTotal`, `binnedQuantileSelect` (binned-CDF percentiles == validated `pct_from_bins` to 1e-13). Re-pointed: **kpis, completeness, histogram, trend**. **HEATMAP REVERTED to per-shipment processed** (small-n binned divergence).
- **Item 4 — double-scan folds.** `breakdown-sparklines` __TOTAL__ → GROUPING SETS (non-product); `breakdown` `real_pct_all` → folded into `src` CTE (final basis only).
- **Item 5 — sparkline fan-out.** `breakdown-sparklines` `specs` batch mode (additive); `BreakdownTab.tsx` initial-load fan-out 1+N → 2.
- **Item 6 — HTTP SWR.** `CACHE_HEADER` → `max-age=300, stale-while-revalidate=86400`. (Client-library useSWR DEFERRED.)

**Pipeline branch (uncommitted, must move to `feat/scm-pipeline-rowgroup-sort`):**
- **`inflight_n` tier column** in `pipeline.py` `_write_transit_daily` — the live-validation fix. **Change-2 amendment**, belongs in the PIPELINE PR (deploy-order: tier regen precedes serving).

## Live-validation fixes (why the tier alone was insufficient)

Live old-vs-new on real 2025-12 + 2026-05 (cached `%TEMP%\scm_validate`, real fat tails) caught two bugs synthetic data hid:
1. **NULL `current_shipping_status` = 43% of rows.** Old SQL `status <> 'DELIVERED'` drops NULLs (3VL); tier's `shipments-delivered-exception` re-includes them → completeness/kpis unlogged wildly off. **Fix:** `inflight_n` tier col (status NOT NULL AND NOT IN DELIVERED/EXCEPTION); kpis uses `exception_n+inflight_n`, completeness uses `inflight_n`.
2. **Small-n corridor percentiles.** Binned-CDF can't match quantile_cont for tiny corridors (heatmap per-corridor p95 off up to 20d; large corridors n>=200: 0.58d). **Fix:** heatmap stays on processed; aggregate views on tier.

**Final live result (probe exit 0):** counts/avg/delivered_pct/histogram EXACT; kpis percentiles within ~0.2d; unlogged_pct EXACT; completeness off by 3/142860.

## DEFERRED to app-run follow-up (principal decisions)
- **Item 7** — per-request DuckDB connection / bd_cache race. App-wide load-bearing refactor; whole-app blast radius; needs app-run verification.
- **Item 6 client-library useSWR** (21 components) — high-risk blind churn; HTTP SWR already delivers the latency win.

## Next concrete steps
1. **Open + merge the 2 PRs** (links above), pipeline FIRST. After pipeline merges, confirm the refresh DAG regenerated parquet (incl. `transit_daily.inflight_n`) before merging serving.
2. **At deploy: capture the Change-1 live latency number** — refresh run + in-pod `EXPLAIN ANALYZE` old-vs-new on a date-range `processed` query (the still-pending number from sess-2/3).
3. **App-run follow-up session** (item 7 + client useSWR) — see handover prompt below.

## Handover prompt (next session — app-run follow-up)

> Hey Jebrim, resume S147 — the SCM **app-run follow-up**. Read `inventory/scm-perf-audit-resume__3bb042ff.md` first. Tranche-3 (items 1-6 + `inflight_n` tier col) is merged + deployed; confirm that before starting. This session needs the **app running** (Docker node:20 or the live instance — `duckdb` native binding won't build locally on Windows/node25; `npm install --ignore-scripts` is typecheck-only). Two tasks: (1) **item 7** — move `db.ts` off the single shared DuckDB `Connection` to per-request connections threaded through each route, so `bd_cache` is connection-local (kills the breakdown race) and the 5 sparkline scans parallelize (the Breakdown tab's real fix); verify with concurrent Breakdown requests. (2) **client-library `useSWR`** across the ~21 components keyed on `meta.run_timestamp`, on top of the HTTP SWR already shipped. Both deferred because they need app-run verification, not just typecheck.

## Gates passed
- TS typecheck: `tsc --noEmit` exit 0, 0 errors (worktree `npm install --ignore-scripts` — duckdb native build fails on Windows/node25, not needed for typecheck).
- Live SQL validation: `_verify_routes_sql.py <real-processed-dir>` exit 0.

## Housekeeping
- AWS creds NOT needed this session (reused cached `%TEMP%\scm_validate` real data). Still session-only discipline.
- Disposable probes (untracked, vanish with worktree): `_verify_binned_sql.py`, `_verify_routes_sql.py`, `_diag.py`, `_routes_work*/`. `node_modules` (gitignored) installed for typecheck.
