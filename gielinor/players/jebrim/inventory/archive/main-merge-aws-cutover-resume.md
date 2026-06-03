# Replace main with shipping-mart-cutover — resume

**Status:** parked. Captured 2026-05-22 at session close. No work started.

## Where we are

The shipping-mart-cutover branch in `bi-analytics/` carries 10+ commits of dashboard work that needs to become main:

- `dee0265` — dashboard cut over to shipping_mart gold tables (Phases A+B+C+E)
- `0660a52` — cost-basis vocab rename (Phase D)
- `0001b36` — audit.py + backtest.py rewrite (Phase G)
- `6233b4e` — shared CSV export helper + refactor existing paths
- `1d4004a` — CSV export to Breakdown / Deviations / AvgCosts
- `93a51ba` — CSV export to Cost Drivers + Benchmarks + Completeness
- `eb1c2ea` — pipeline.py guard against pandas dropping all-NULL cost_source
- (and earlier S028 prep commits from `dashboard gold cutover — handover queued for next session`)

Smoke 4 / parity check verified: April 2026 TCG invoiced-only avg = **€6.95 / 209,874 parcels**, matches the agent within rounding. Cost-basis convergence achieved.

## Next concrete step

Niklavs' note at session close: *"I will need to replace the current main version with this cutover version, which includes also getting AWS things right — S3, ECR, etc etc."*

The cutover branch is the *new* main. This is **not** a routine merge — the AWS-side infra (S3 paths, ECR images, the Airflow DAG, Docker entrypoint) needs to be updated in lock-step with the code cutover, otherwise the deployed dashboard breaks.

Suggested decomposition for the next session:

1. **Pre-merge audit** — diff `shipping-mart-cutover` vs `main`. Confirm every commit is wanted. Any pre-cutover hotfixes on main that the cutover doesn't carry?
2. **AWS state inventory** — what's in S3 right now (`s3://etl-poc-dev/nextjs_dashboards_data/shipping_costs_monitoring/`)? What's in ECR (`123038732324.dkr.ecr.eu-central-1.amazonaws.com/shipping_costs_monitoring:latest`)? Are they running pre-cutover code?
3. **DAG check** — the Airflow refresh DAG runs 08:00 Berlin daily (`dags/shipping_costs_monitoring_dag.py`). Verify it's pointed at the right ECR tag and won't blow up when the code shape changes.
4. **Docker build + ECR push** — `docker build -f NFE/dashboards/shipping_costs_monitoring_nextjs/docker/Dockerfile -t shipping-costs .` from repo root, then push to ECR. Tag carefully — keep the pre-cutover image around for rollback until the new one is validated in prod.
5. **S3 baseline sync** — Niklavs' local `data/` after the cutover refresh is the "fresh baseline." Upload to S3 so the next pod startup downloads the post-cutover state, not the pre-cutover one.
6. **Merge** — `shipping-mart-cutover` → `main`. Force-push if needed (with care), or fast-forward if the histories are clean.
7. **Smoke-test prod** — pod pulls fresh ECR image, downloads fresh S3 data, dashboard renders. Smoke 4 parity check against the deployed instance.
8. **Tomorrow's 08:00 Berlin DAG run** — should land on the merged main cleanly. Watch for the first run; root-cause anything that breaks.

## Files / paths to read first

1. This file.
2. `bi-analytics/NFE/dashboards/shipping_costs_monitoring_nextjs/CLAUDE.md` § Deployment — has the canonical S3 path, ECR image, DAG path, data-flow diagram.
3. `bi-analytics/NFE/dashboards/shipping_costs_monitoring_nextjs/docker/Dockerfile` — what's in the image.
4. `bi-analytics/NFE/dashboards/shipping_costs_monitoring_nextjs/docker/entrypoint.sh` — startup behavior (S3 download).
5. `bi-analytics/NFE/dashboards/shipping_costs_monitoring_nextjs/docker/refresh.sh` — what the refresh container runs.
6. `bi-analytics/dags/shipping_costs_monitoring_dag.py` — the Airflow DAG.
7. `inventory/dashboard-gold-cutover-resume.md` — full scope of what landed in the cutover.

## Constraints / watch-outs

- **Don't push --force to main blindly.** Even if histories diverge, validate the cutover branch is what you want before overwriting.
- **Keep the pre-cutover ECR image around** for rollback until the new one is validated.
- **The DAG runs at 08:00 Berlin daily** — pick a merge window that gives prod a clean first run. Avoid merging at 07:55.
- **Airflow user has broader grants than `ship_mart_ro`** (see `inventory/dashboard-gold-cutover-resume.md` Constraints). Don't change the DB user as part of the merge.
- **Branch is 10+ commits ahead of main.** All commits intended; none should be dropped. Verify before merge.
