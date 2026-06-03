# S073 resume — swap the live report on AWS

## Status
**in-progress** — all code/data/deploy done; one open dependency: validate the scheduled refresh end-to-end.

## Where we are
Shipping Costs Monitoring dashboard is **live on the cutover version** (gold mart). Today (2026-05-26), all shipped via cutover→main→CICD on picanova/bi-analytics:
- Cutover swap (merge `4793a50`, S3 data synced) — img `2b7af1b`.
- ORWO source-system unselected by default (`page.tsx`) — img `b3eb570f`.
- Incremental-refresh fix: `refresh.sh` syncs combined `raw.parquet` ↔ `raw_cache/`, drops dead split-cache; `entrypoint.sh` excludes `raw_cache/*` from pod sync — img `0608a755`.
- **duckdb added to Docker image** (`Dockerfile` pip) — img **`137472e3`** (12:28). Fixed the first test run's crash.
- bi-etl DAG: `execution_timeout` 30→60min + schedule 08:00→07:00 Berlin — pushed `44de63c37`.
- S3 rollback backup at `s3://etl-poc-dev/nextjs_dashboards_data/_backup_shipping_costs_monitoring_2026-05-26/`. Old image rollback = `sha256:06e14cd` (`f217719c`).

First manual DAG test run (12:07, on img `0608a755`) **failed**: `ModuleNotFoundError: No module named 'duckdb'` at pipeline.py L496 (full-pull DuckDB join). Pull of 13.2M rows succeeded; crashed at the join. Root cause = image missing duckdb (now fixed in `137472e3`).

## Next concrete step
**Awaiting principal:** re-trigger the `shipping_costs_monitoring_nextjs` DAG in Airflow on the new image (`137472e3`). Expect ~8min full pull → DuckDB join (now works) → uploads + seeds `raw_cache/raw.parquet`. **Then verify from S3** (creds: `aws --profile bi-account --region eu-central-1`): `raw_cache/raw.parquet` exists (proves join+seed) AND summary parquets (`daily.parquet` etc.) re-timestamped. After this run, every refresh is incremental (3-month merge, polars-only — no duckdb path).

## Cleanup (after verify)
- Remove throwaway worktree `~/Documents/GitHub/_bi-analytics-deploy` + local branch `deploy-cutover-2026-05-26` (origin/main has all its commits).
- Stale docs (non-blocking): `CLAUDE.md` claims entrypoint falls back to baked-in data (it doesn't); `reference.md` `--refresh` split-cache desc; both pre-date these fixes.
- Old split caches still on S3 `raw_cache/` (raw_pif/raw_costs/raw_revenue/schenker) — vestigial, harmless; optional cleanup.

## Files to read first
- `quest-log/in-progress/S073_006248ef_aws-report-swap-guide.md` (full execution log + recon findings + 5 Qs answered).
- `gielinor/comms/active.md` tail (jebrim-dcf97c7a CLOSING).
