---
quest: S147_scm-perf-audit
sid8: 6595ae02
ts: 2026-06-02 17:30
open_dep: Changes 1+2+3 committed LOCAL on feat/scm-pipeline-rowgroup-sort (ahead of origin/main by 2) but push + PR HELD by principal; Tranche-3 serving re-point queued (separate session); live latency number pending at deploy
---

# S147 — SCM dashboard speed/performance — resume

**Status:** in-progress. Audit COMPLETE; landmine fix SHIPPED (sess-1). **Pipeline Tranche-2 ALL THREE changes BUILT + VALIDATED + committed local** (Change-1 sess-2, Changes 2&3 this session). Push/PR HELD by principal. Tranche-3 (serving re-point) queued.

**Where we are:** The pipeline refactor is code-complete and live-validated.
- **Change-1** (`8b9a232`): `processed` per-month sort `(order_date, shippingprovider)` + `row_group_size` + `statistics`; `daily` sort + stats. Synthetic-verified (7-day window reads 1/4 row groups vs 1/1). Live latency number still pending at deploy (refresh + in-pod EXPLAIN ANALYZE).
- **Change-2** (`9e109c0`): new `transit_daily.parquet` (`_write_transit_daily`, pipeline.py STEP 9d) — 7-dim daily grain (= `daily`), DELIVERED-gated calendar+business transit bins `LEAST(FLOOR(x),45)` + exact-avg sums + status counts. Retires the whole Transit tab's per-shipment scan. Built via streaming DuckDB COPY off the processed glob (memory-safe; never touches `df_sum`). **LIVE-validated** (real 2025-12 + 2026-05): all percentiles p50/p85/p95/p99 within ±0.63 day, 0 corridors floored. `TRANSIT_BIN_TAIL` was 14 in the spec → live cap sweep showed 14 floored p95 on 12/59 + p99 on 29/59 (real p99 reaches 42d) → raised to **45** (size flat: tail bins sparse-zero, ~35MB full-history).
- **Change-3** (`9e109c0`): added `sum_real` + `sum_expected` to `_write_deviations_summary` (already at the both-costs-present population). **LIVE-validated**: rolled-up `avg_real`/`avg_expected`/`n` match the per-shipment deviations trend EXACTLY (0.000000). Makes the trend a safe serving swap.

Branch `feat/scm-pipeline-rowgroup-sort` ahead of `origin/main` by 2 commits, **NOT pushed** (principal chose: stack all three, commit local, hold push/PR). Isolated worktree `_scm-pipeline-sort`.

## Next concrete step
**First (principal action, HELD this session): push + ONE stacked PR (Changes 1+2+3).**
`git -C C:/Users/niklavs.felsbergs/Documents/GitHub/_scm-pipeline-sort push -u origin feat/scm-pipeline-rowgroup-sort` then open the PR (gh absent locally → manual link). Pipeline-only, additive (new/extended parquet tiers), zero serving-correctness risk — the route re-points are Tranche-3, not in this PR. Deploys via the daily refresh DAG on merge. At deploy, capture the **live latency number**: refresh run + in-pod `EXPLAIN ANALYZE` on a date-range processed query, old-vs-new (the proven T4/T5 in-pod DuckDB-probe method), to confirm Change-1's within-file pruning actually moves wall-clock.

**Then TRANCHE-3 serving/frontend (separate session):** re-point the deviations trend at `deviations_summary` (now carries `sum_real`/`sum_expected`) + the 5 `transit/*` routes at `transit_daily.parquet` (reconstruct percentiles from the binned CDF — see `_write_transit_daily` docstring for the serve-time contract incl. the dynamic unlogged/inflight split). Then: breakdown double-scans → GROUPING SETS (`breakdown-sparklines.ts:140/164`, `breakdown.ts:406/448`); trim the 5× sparkline fan-out; SWR caching; D1 per-request `db.connect()` (also fixes the bd_cache race).

## Files / paths to read first
- This resume + `quest-log/in-progress/S147_dcb495a7_scm-perf-audit.md` (Session-3 section = this session).
- **The changes:** worktree `C:/Users/niklavs.felsbergs/Documents/GitHub/_scm-pipeline-sort`, branch `feat/scm-pipeline-rowgroup-sort` (`8b9a232` Change-1, `9e109c0` Changes 2&3). Source: `bi-analytics` `NFE/dashboards/shipping_costs_monitoring_nextjs/pipeline.py` (`_write_transit_daily` STEP 9d; `_write_deviations_summary`; `TRANSIT_BIN_TAIL`).
- Tranche-2 spec + transit-route contract: `S147_d3_parquet-layout-preagg.md` (P1 transit tier + P2 deviation trend).
- Disposable verify probes (vanish with the worktree, untracked): `_verify_transit_tier.py` (synthetic), `_verify_transit_live.py` (live old-vs-new), `_verify_transit_capsweep.py` (cap sweep).

## Housekeeping carried
- AWS creds session-only — not written to disk.
- `%TEMP%\scm_validate` (~85MB real shipping data downloaded for validation) couldn't be rm'd (block-deletes hook) — clear manually.
- Prior resume `scm-perf-audit-resume__e1918844.md` → `inventory/archive/`.

## Harvest candidates (defer to alching; S147 not finished — harvest-from-finished-quests rule)
- **bank note (project):** SCM transit roll-up tier design — binned-CDF percentile serving off histogram-bin counts (cap chosen by the live p99 distribution, not the UI display cap); exact avg via sum/bincount; dynamic unlogged/inflight rolls up because (today−order_date) is constant within an order_date. + the Change-1 row-group note from sess-2.
- **examine draft (this session):** `2026-06-02-revalidate-borrowed-constants-for-new-use` (TAIL=14 borrowed from the histogram display cap was wrong as a percentile-fidelity cap). + sess-1 `static-audit-ranking-is-a-hypothesis-until-measured` still pending.
