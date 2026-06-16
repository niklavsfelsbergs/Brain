# SCM refresh model: stale cached partitions → full-refresh (2026-06-16)

Source: S247 (OnTrac oversize "Feb onset" investigation + fix). App: `bi-analytics-main/NFE/dashboards/shipping_costs_monitoring_nextjs`.

## The stale-partition mechanism (the OnTrac bug)
The SCM pipeline's default daily `refresh.sh` ran `pipeline.py --refresh` = **incremental**: re-pull only the last 3 months (`INCREMENTAL_MONTHS=3`) and **merge onto cached `raw.parquet` older rows kept verbatim** (`pull_raw`, `pipeline.py:521` `df_old.filter(order_date < cutoff)`). Bucket columns are pulled **per-shipment from the gold mart**, so every cached month is frozen at *the mart's classification when that month was last pulled*.

Consequence: a **backdated mart correction never reaches the cached older months.** OnTrac's silver `shipping_charge_bucket_mapping` was rebuilt 2026-04-23 → gold re-derived oversize for all history. The rolling window re-pulled only recent months from the corrected mart → those showed the (always-present) oversize charge; older cached months stayed €0. The apparent "Feb 2026 onset" = the oldest month the rolling window had re-touched since the mart fix. **Not a cost event; a cache-staleness artifact.**

**Diagnostic heuristic:** a metric that "onsets" exactly at the rolling-refresh-window boundary, with the source (gold mart) showing the value present all along, is **stale cached partitions**, not a real change. Check the mart directly across the full history before believing a dashboard onset.

## The fix
- One-off flush: delete `s3://etl-poc-dev/nextjs_dashboards_data/shipping_costs_monitoring/raw_cache/raw.parquet` → next run's `cp ... || true` finds it gone → full pull from `FULL_DATE_FROM` rebuilds all partitions. (Bucket is versioned → soft delete.)
- Permanent: `refresh.sh` `--refresh` → `--refresh-full` (every run re-pulls all history). The mart pull is fast enough post-cutover; full refresh removes the freeze class entirely.

## Deploy topology (corrected this session)
- **`refresh.sh` (the pipeline behavior) deploys via the ECR image** — push to `picanova/bi-analytics` main → CI rebuilds `:latest` → DAG runs the new image.
- **The LIVE DAG is in the bi-etl repo**, not bi-analytics: `bi-etl/dags/AI_Automations/nextjs_dashboard_dags/shipping-costs-monitoring-dag/shipping_costs_monitoring_dag.py`. The copy under the app dir (`.../dashboards/.../dags/`) is a **stale source/reference copy** — at the time it read 30min timeout / 08:00 schedule while live was **60min / 07:00**. Verify DAG/timeout config against the bi-etl copy, never the bi-analytics copy. Live timeout (60min) already covers a full pull.

Links: [[bi_analytics_deploy_topology]] (push→ECR; the three worktrees), [[scm]] (digest), [[2026-06-12-scm-breakdown-cost-basis-not-buckets]].
