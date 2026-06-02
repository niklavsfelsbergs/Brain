---
quest: S147_scm-perf-audit
sid8: dcb495a7
ts: 2026-06-02 13:45
open_dep: pipeline tranche (sort+stats + population-matched roll-up tiers) is the real headline build, queued for a fresh session; serving/frontend tranche queued after; landmine PR awaiting merge + manual open
---

# S147 — SCM dashboard speed/performance audit — resume

**Status:** in-progress. Audit COMPLETE + evidence-backed; landmine fix SHIPPED (PR pushed); two build tranches queued for fresh sessions.

**Where we are:** Ran a 5-dwarf perf audit on the post-fix SCM tree, then anchored the ranking with **live measurement** (network capture + in-pod DuckDB probes via principal AWS creds, session-only). Verdict: **the slowness is processed-tier scan BREADTH × per-shipment column width** (full 29-month glob = 268ms vs 10ms single-month, 26.8× breadth factor; row-group stats absent → no within-file pruning), **not** connection serialization (1–2 users) nor CTE re-scan (shifts only 1.6×). The serving layer is already mostly correctly routed — the remaining per-shipment scans can't be cheaply re-routed because **no existing pre-agg tier matches their query population** (proven: P2 deviations-trend fails an old-vs-new live compare). So the real build is the **pipeline regen**, not serving tweaks.

**SHIPPED this session:** the durability landmine — branch `fix/scm-duckdb-mem-default` (commit `025ca21`, pushed to `picanova/bi-analytics`). db.ts:35 default `4GB`→`512MB` + Dockerfile `ENV DUCKDB_MEMORY_LIMIT=512MB`/`DUCKDB_THREADS=2`. Stops a fresh image rebuild from re-triggering the S146 OOM. **PR not yet opened** (gh CLI absent locally) — open via https://github.com/picanova/bi-analytics/pull/new/fix/scm-duckdb-mem-default.

## Next concrete step — TRANCHE 2: the pipeline build (the real headline)

Fresh session. Repo: `bi-etl` (the SCM pipeline) — find `pipeline.py` for `shipping_costs_monitoring` (writes `daily`/`daily_product`/`processed`/summary parquet, then `docker/refresh.sh` S3-syncs). Three changes, each validated old-vs-new against live data (method proven below):

1. **Sort-on-write + row-group stats (effort S).** Every `write_parquet` is bare (no sort, no `row_group_size`). Confirmed live: `processed` month files have 4 row-groups at default 122880 and **zero order_date statistics** → no within-file pruning. Add `.sort("order_date")` (consider `(order_date, shippingprovider)`) + `row_group_size≈100–128k` before write so DuckDB can skip row-groups on date-filtered processed queries. Pipeline-only, serving-invisible.
2. **Transit roll-up tier (effort M).** All 5 `transit/*` routes scan per-shipment `processed` only to aggregate `transit_time_days`/`current_shipping_status`. `pipeline.py:50-52` already flags this as deferred. Percentiles aren't summable → bake daily **histogram-bin counts** per (date,country,provider,packagetype) (bins `LEAST(FLOOR(x),14)`, matches `transit/histogram`); serve p50/p85/p95 off the binned CDF (±1 day). Retires all 5 transit routes + `transit/histogram` off per-shipment. Then re-point those routes (tranche 3).
3. **Deviation-trend roll-up at the matching population (effort M).** P2 can't use existing tiers: the trend needs a dual line (`avg_real` + `avg_expected`) over shipments with **both** `shipping_cost>0 AND expected_shipping_cost>0`. `deviations_summary` carries only `sum_deviation`; the `daily` tier's population is broader (live compare diverged — Germany/DHLPKT: counts differ every week, recent weeks where costs haven't arrived deflate it badly). Bake a trend tier with `sum_real`, `sum_expected`, `n` over the both-costs-present filter at (order_date,country,provider) grain → then P2 becomes a safe serving swap.

After pipeline changes: a refresh run + S3 re-sync, then validate each old-vs-new before deploy.

**Live-validation method (proven this session — reuse it):** with principal AWS creds (`eu-central-1`, EKS cluster `bi-generic`, ns `shipping-dashboard`), `kubectl exec -i <pod> -c shipping-costs-monitoring -- python3 -` runs DuckDB 1.5.3 over the pod's parquet in `$DATA_DIR`. Cap probe memory (`SET memory_limit='350-450MB'`, `threads=2`) so you don't perturb the live pod. Run the OLD query and the NEW (pre-agg) query for a sample (country, provider, window) and compare row-by-row before trusting a re-route. **Creds are session-only — get fresh ones each session, never write them to a file.**

## Next — TRANCHE 3: serving/frontend (after tranche 2 lands)

Fresh session, `bi-analytics` repo, SCM app:
- Re-point `deviations` trend → new trend tier; `transit/*` → new transit tier (validated equivalent in tranche 2).
- D2-F2/F3: `breakdown-sparklines.ts:140/164` double-scans processed (per-dim + `__TOTAL__`) → GROUPING SETS; `breakdown.ts:406/448` `buildTotalQuery` double-scan → fold into the `src` CTE. Pure SQL, no population change.
- Trim the **5× `breakdown-sparklines` fan-out** (the network capture's biggest call-count driver) + the `filter-options`→data dependency waterfall.
- SWR / stale-while-revalidate caching keyed on `meta.run_timestamp`; lengthen `Cache-Control` (`db.ts:56`, currently `max-age=30`).
- **D1 per-request `db.connect()`** — deprioritized for latency (1–2 users) but it FIXES the `bd_cache` shared-connection race (the live Breakdown no-data bug deferred from S146) and parallelizes single-tab fan-out + future concurrency. Sizing: DuckDB `memory_limit` is **instance-wide, not per-connection** (verified), so a small pool doesn't multiply the cap; `threads × pool` is the pressure.

## Files / paths to read first
- This quest: `gielinor/players/jebrim/quest-log/in-progress/S147_dcb495a7_scm-perf-audit.md` (synthesis + revised ranking + T4/T5 live findings).
- Dwarf traces: `S147_d{1,2,3,4,5}_*.md` (same folder) — D3 (`parquet-layout-preagg`) is the tranche-2 spec.
- Landmine branch: `_scm-perf` worktree (`fix/scm-duckdb-mem-default`, `025ca21`).
- S146 (the OOM fix this builds on): `inventory/scm-serving-memory-resume__f20d7744.md`.

## Harvest candidates (defer to alching; S147 not finished, per the harvest-from-finished-quests rule)
- **bank note (project):** SCM perf characterization — breadth is the dominant cost (27×), row-group stats absent, daily/daily_product single-file pre-agg tiers near-instant, and **no existing pre-agg tier matches the per-shipment query populations** (the reason serving-only routing can't fix it). Anchor: S147 T4/T5.
- examine draft written this session (static-audit-ranking-is-a-hypothesis-until-measured).

## Worktree cleanup (optional)
`_scm-mem-fix` (S146 branch, now merged via PR#13) can be removed: `git worktree remove --force _scm-mem-fix`. `_scm-perf` stays until the landmine PR merges.
