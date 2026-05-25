# S073 resume — swap the live report on AWS

## Status
**in-progress** (not started — hand-off brief from S069).

## Where we are
Principal wants a full step-by-step guide to switch the live main-branch report on AWS to the `shipping-mart-cutover` version, incl. S3 file exchange. The feeding pipeline (S069) is fixed + runs full-volume. Deploy model is captured; 5 open questions block a safe guide.

## Next concrete step
Start the session with the `aws-creds` skill (needs S3 etl-poc-dev + ECR eu-central-1). Then read `docker/entrypoint.sh`, `docker/refresh.sh`, `docker/Dockerfile`, `dags/shipping_costs_monitoring_dag.py`, and the repo-root CICD config to answer the 5 open questions in the quest-log (esp. #1 image build/deploy trigger and #2 whether local parquets can be `aws s3 sync`'d straight up). Then draft the guide; execute only with principal sign-off at each AWS-mutating step (snapshot for rollback FIRST).

## Key facts (don't re-derive)
- ECR image: `123038732324.dkr.ecr.eu-central-1.amazonaws.com/shipping_costs_monitoring:latest` (eu-central-1).
- S3 data: `s3://etl-poc-dev/nextjs_dashboards_data/shipping_costs_monitoring/` (+ `raw_cache/`).
- Dockerized Next.js+DuckDB pod; Airflow DAG runs refresh.sh; entrypoint.sh syncs S3→pod on startup, falls back to baked-in data.
- Repo/branch: `Documents/GitHub/bi-analytics`, branch `shipping-mart-cutover` (cutover code; main-merge = CICD = principal's call).

## Files to read first
- `quest-log/in-progress/S073_006248ef_aws-report-swap-guide.md` (full brief + 5 open questions + deploy facts).
