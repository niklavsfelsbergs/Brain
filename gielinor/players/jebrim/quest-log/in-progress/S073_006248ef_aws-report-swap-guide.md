# S073 — swap the live main-branch report on AWS (step-by-step guide + execution)

**Session:** 006248ef (birthed as a hand-off; not yet worked) · **Player:** Jebrim · **Opened:** 2026-05-25

## The ask (principal, verbatim intent)
"A full step by step guide for how to switch out the current main branch live report on AWS. It's gonna need S3 file exchanging, and everything else." Hand-off from S069 (the pipeline that feeds this report is now fixed + runs at full volume on the `shipping-mart-cutover` branch).

## What "switch out" means here
The live report is currently served from `main`. The `shipping-mart-cutover` branch carries the new gold mart + the S069-fixed pipeline (new cost buckets / columns / schema). Swapping = get the cutover code AND freshly-regenerated data into the live AWS deployment, replacing the main-branch version. Two moving parts: the **Docker image** (code) and the **S3 parquet data** (the "S3 file exchanging").

## Deploy model — FACTS (from docs/reference.md + dashboard CLAUDE.md, 2026-05-25)
NOT a static S3 site. It's a Dockerized Next.js + DuckDB server that reads parquet files synced from S3.
- **Image:** ECR `123038732324.dkr.ecr.eu-central-1.amazonaws.com/shipping_costs_monitoring:latest` (region **eu-central-1**).
- **Runtime:** K8s pod (KubernetesPodOperator), scheduled by Airflow DAG `dags/shipping_costs_monitoring_dag.py` (weekday 08:00 Berlin). Refresh container runs `docker/refresh.sh` (= `pipeline.py --refresh` + S3 sync), auto-deletes pod after.
- **S3 data path:** `s3://etl-poc-dev/nextjs_dashboards_data/shipping_costs_monitoring/` — summary + processed parquets here; **raw caches separately under `raw_cache/`**.
- **Data flow:** refresh container downloads raw caches from S3 → runs pipeline → uploads summary+processed parquets back to S3. Dashboard pod downloads parquets from S3 on startup via `docker/entrypoint.sh`; **falls back to baked-in data if S3 unreachable.**

## Open questions to resolve BEFORE writing the final guide
1. **Image build/deploy trigger.** Is the ECR image built+pushed by CICD on main-merge, or manually (`docker build` → `docker push`)? Find the CICD config (look for `.gitlab-ci.yml` / GitHub Actions / buildspec). This decides whether the swap is "merge cutover→main" or "manual build+push from cutover".
2. **Data exchange shortcut.** S069's `--refresh-full` produced fresh parquets LOCALLY (in the pipeline's DATA dir). Can we `aws s3 sync` those straight to the S3 data path to shortcut, or must the in-cluster refresh container regenerate them? Check `docker/refresh.sh` + `entrypoint.sh` for the exact S3 prefixes + sync direction.
3. **raw_cache staleness.** The cutover changed the source pulls — does the old `raw_cache/` on S3 need clearing so the new pipeline doesn't read stale caches? (`--refresh-full` ignores caches; `--refresh` uses them.)
4. **Rollback.** Before overwriting: snapshot current S3 data (copy to a `_backup_main/` prefix) + record the current ECR image digest, so revert is one command.
5. **Pod refresh.** Does the dashboard pod auto-restart to pull the new image + data, or is a manual rollout needed?

## Prereqs for the next session
- **AWS credentials** — needs S3 (etl-poc-dev) + ECR (eu-central-1) access. Use the `aws-creds` skill at session start.
- Read first: `docker/entrypoint.sh`, `docker/refresh.sh`, `docker/Dockerfile`, `dags/shipping_costs_monitoring_dag.py`, plus any CICD config at repo root.

## State
NOT STARTED — hand-off brief only. Next session: resolve the 5 open questions (read the docker/ + CICD files + confirm with principal where ambiguous), THEN write the full step-by-step swap guide and execute with principal sign-off at each AWS-mutating step (S3 overwrite, ECR push, pod rollout — all outward-facing, all gated).
