---
quest: S147_scm-perf-audit
sid8: e1918844
ts: 2026-06-02 14:15
open_dep: Tranche-2 Change-1 committed LOCAL only (push deferred by principal); Changes 2-3 (transit binned-CDF tier + deviation-trend both-costs-present tier) still queued + need live AWS creds; serving Tranche-3 after
---

# S147 — SCM dashboard speed/performance — resume

**Status:** in-progress. Audit COMPLETE; landmine fix SHIPPED (S147 sess-1); **Tranche-2 Change-1 (sort-on-write + row-group stats) BUILT + VERIFIED + committed local** (this session). Changes 2–3 queued; serving Tranche-3 after.

**Where we are:** The pipeline refactor's first lever is done. `pipeline.py` now sorts the `processed` per-shipment tier per-month by `(order_date, shippingprovider)` and writes explicit `row_group_size` + `statistics=True`; `daily` sorts by `order_date`. Verified synthetically (polars 1.33): a 7-day window over a 500k-row month reads **1/4 row groups after vs 1/1 before**, identical result rows. Committed LOCAL only on branch `feat/scm-pipeline-rowgroup-sort` (`8b9a232`), **not pushed** (principal chose commit-local).

## Next concrete step
**First: push + PR Change 1** (principal action, deferred this session):
`git -C C:/Users/niklavs.felsbergs/Documents/GitHub/_scm-pipeline-sort push -u origin feat/scm-pipeline-rowgroup-sort` then open PR (gh absent locally → manual link, same as the landmine). Independent of the unmerged landmine PR (`fix/scm-duckdb-mem-default`); deploys via the daily refresh DAG (`shipping_costs_monitoring_nextjs`, ECR `shipping_costs_monitoring:latest`) on merge. At deploy, get the **live latency number**: a refresh run + in-pod `EXPLAIN ANALYZE` on a date-range processed query, old-vs-new (the proven T4/T5 in-pod DuckDB-probe method).

**Then TRANCHE-2 Changes 2 & 3** (fresh session, need live AWS creds for old-vs-new validation):
2. **Transit binned-CDF roll-up tier** (effort M). New pipeline step: daily per-(date,country,provider,packagetype) histogram-bin counts of `transit_time_days` (bins `LEAST(FLOOR(x),14)`, matching `transit/histogram`) + delivered/exception/with-ts counts. Serve p50/p85/p95 off the binned CDF (±1 day). Retires all 5 transit routes + `transit/histogram` off per-shipment. Validate binned-CDF percentiles vs exact `quantile_cont` on a live month before retiring.
3. **Deviation-trend roll-up at the both-costs-present population** (effort M). Bake a trend tier with `sum_real`, `sum_expected`, `n` over `shipping_cost>0 AND expected_shipping_cost>0` at (order_date,country,provider) grain → makes P2 a safe serving swap (the `daily` tier's population diverges — proven in sess-1 T5 live compare).

**Then TRANCHE-3 serving/frontend** (after T2 tiers land): re-point `deviations` trend + `transit/*` routes at the new tiers; breakdown double-scans → GROUPING SETS (`breakdown-sparklines.ts:140/164`, `breakdown.ts:406/448`); trim the 5× sparkline fan-out; SWR caching; D1 per-request `db.connect()` (also fixes the bd_cache race).

## Files / paths to read first
- This resume + `quest-log/in-progress/S147_dcb495a7_scm-perf-audit.md` (Session-2 section = this session's build).
- **The change:** worktree `C:/Users/niklavs.felsbergs/Documents/GitHub/_scm-pipeline-sort`, branch `feat/scm-pipeline-rowgroup-sort` (`8b9a232`). Pipeline source: `bi-analytics` `NFE/dashboards/shipping_costs_monitoring_nextjs/pipeline.py` (NOT bi-etl — that's only the DAG).
- Tranche-2 spec: `S147_d3_parquet-layout-preagg.md` (P1 transit tier + P2 deviation trend specs).
- Prior resume (superseded): `inventory/archive/scm-perf-audit-resume__dcb495a7.md`.

## Harvest candidates (defer to alching; S147 not finished — harvest-from-finished-quests rule)
- **bank note (project):** SCM perf characterization — breadth is the dominant cost (27×); **explicit `row_group_size` is load-bearing, not a no-op**: a clean single-frame polars 1.33 write produces ONE row group regardless (the "4 at 122880" the live probe saw was the multi-chunk reload source); statistics ARE written by default but useless without `order_date` clustering. Sort + explicit rgs together = within-file date pruning. Anchor: S147 sess-2 synthetic verification.
- examine draft from sess-1 (`static-audit-ranking-is-a-hypothesis-until-measured`) still pending.

## Worktree cleanup (optional)
`_scm-pipeline-sort` stays until Change 1 merges. Untracked `_verify_rowgroup_prune.py` in it = the synthetic probe (disposable; couldn't rm — block-deletes; vanishes with the worktree). `_scm-mem-fix` (S146, merged PR#13) + `_scm-perf` (landmine, PR pending) removable per prior resume.
