# S073 — swap the live main-branch report on AWS (step-by-step guide + execution)

**Session:** 006248ef (birthed as a hand-off; not yet worked) · **Player:** Jebrim · **Opened:** 2026-05-25

## The ask (principal, verbatim intent)
"A full step by step guide for how to switch out the current main branch live report on AWS. It's gonna need S3 file exchanging, and everything else." Hand-off from [[S069_006248ef_pipeline-oom-hardening|S069]] (the pipeline that feeds this report is now fixed + runs at full volume on the `shipping-mart-cutover` branch).

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
2. **Data exchange shortcut.** [[S069_006248ef_pipeline-oom-hardening|S069]]'s `--refresh-full` produced fresh parquets LOCALLY (in the pipeline's DATA dir). Can we `aws s3 sync` those straight to the S3 data path to shortcut, or must the in-cluster refresh container regenerate them? Check `docker/refresh.sh` + `entrypoint.sh` for the exact S3 prefixes + sync direction.
3. **raw_cache staleness.** The cutover changed the source pulls — does the old `raw_cache/` on S3 need clearing so the new pipeline doesn't read stale caches? (`--refresh-full` ignores caches; `--refresh` uses them.)
4. **Rollback.** Before overwriting: snapshot current S3 data (copy to a `_backup_main/` prefix) + record the current ECR image digest, so revert is one command.
5. **Pod refresh.** Does the dashboard pod auto-restart to pull the new image + data, or is a manual rollout needed?

## Prereqs for the next session
- **AWS credentials** — needs S3 (etl-poc-dev) + ECR (eu-central-1) access. Use the `aws-creds` skill at session start.
- Read first: `docker/entrypoint.sh`, `docker/refresh.sh`, `docker/Dockerfile`, `dags/shipping_costs_monitoring_dag.py`, plus any CICD config at repo root.

## State
EXECUTING (2026-05-26, session dcf97c7a/29565783). Recon complete, swap underway.

### Recon findings (all 5 Qs resolved against ground truth)
- **Q1 build trigger:** CICD on bi-analytics GitHub, keyed to **main** (images tagged with main commit SHAs; no CICD config in this repo — platform-side). Principal confirmed: push to main → rebuild `:latest` + restart pod.
- **Q2 data sync:** dashboard reads summary + `processed/` parquets from S3 → can `aws s3 sync` straight up. `sync_to_s3.sh` is STALE (expects top-level `raw_pif/raw_costs` the current pipeline no longer writes; current pipeline caches to combined `data/raw.parquet`).
- **Q3 raw_cache:** split `raw_*` caches are vestigial (pre-cutover); current pipeline ignores them. Left untouched on S3.
- **Q4 rollback:** old image `sha256:06e14cd` (main `f217719c`, pre-cutover, pushed 05-18). Live S3 backed up to `s3://etl-poc-dev/nextjs_dashboards_data/_backup_shipping_costs_monitoring_2026-05-26/` (1.1 GiB).
- **Q5 pod refresh:** dashboard pod = separate K8s Deployment; push-to-main CICD auto-restarts it (principal-confirmed). No manual rollout.
- **Stale docs found (post-swap fixups):** entrypoint.sh does NOT fall back to baked-in data (CLAUDE.md wrong); reference.md `--refresh` cache desc stale; sync_to_s3.sh file set stale.

### Topology / merge
- main (worktree `bi-analytics-main/`, dirty w/ unrelated playground deletions — NOT touched) diverged from `shipping-mart-cutover` at `32886ee`: ~70 main commits cutover lacks, 25 cutover commits main lacks.
- Merged in clean throwaway worktree `_bi-analytics-deploy` (off origin/main, branch `deploy-cutover-2026-05-26`): merge commit `4793a50`. Sole conflict `page.tsx` URL-sync useEffect deps → kept cutover's array (body uses transit state). PROOF: `git diff <merge> shipping-mart-cutover -- <dashboard>` empty ⇒ merged dashboard byte-identical to S055-tested cutover.

### Execution (principal go given "sounds like you got a plan")
- [x] STEP 3 DONE (10:07): `aws s3 sync data/ → live S3` — summary + processed/ now cutover-schema (daily 31→61MB, daily_product 63→126MB), dismissed_alerts.json preserved, nothing wrongly deleted. Verified via re-listing.
- [x] STEP 4 DONE (~10:1x): pushed `deploy-cutover-2026-05-26` (merge 4793a50) → origin/main, clean fast-forward 2406916..4793a50. CICD (GitHub Actions, picanova/bi-analytics) building :latest + pod restart.
- [x] STEP 5a DONE (10:16:45): CICD built + pushed NEW :latest = `sha256:2b7af1b2093af461683f2142bed6047c6593c66e76776087413edeed7ab0116a`, tagged `latest,4793a507...` (our merge commit) — confirms the GitHub Actions pipeline ran end-to-end (~3min build). Pod restarting onto it.
- [→] STEP 5b: final eyeball — load live dashboard URL (need from principal), confirm cutover render (Buckets/Transit tabs, gold-mart numbers) + no schema error. Rollback if broken = re-tag sha256:06e14cd + restore _backup_shipping_costs_monitoring_2026-05-26/ S3 prefix.
- CLEANUP (post-verify): remove throwaway worktree `_bi-analytics-deploy` + local branch `deploy-cutover-2026-05-26`; note dirty `bi-analytics-main` worktree (unrelated playground deletions) left as-found.

### FOLLOW-UP (post-demo) — refresh.sh / pipeline cache mismatch (found answering "does the DAG need changes?")
- DAG file itself = NO change (points at :latest, config valid; live copy in bi-etl dags/AI_automations/nextjs_dashboards/).
- BUG: cutover `docker/refresh.sh` still fetches/uploads old split caches (raw_pif/raw_costs/raw_revenue/schenker) which the cutover `pipeline.py` IGNORES — it caches to combined `data/raw.parquet`, which refresh.sh never syncs. Confirmed in pull_raw (pipeline.py L413-434, L476/490): `--refresh` with no raw.parquet → full pull from FULL_DATE_FROM.
- Effect: every scheduled 08:00 run = FULL Redshift pull (not 3-mo incremental). Works ([[S069_006248ef_pipeline-oom-hardening|S069]] OOM fix in image, 20Gi pod) but heavy. WATCH DAG `execution_timeout=30min` on first scheduled run vs ~18M-row mart; timeout = no refresh that day (dashboard keeps last-synced data, not fatal).
- Fix options: (a preferred) refresh.sh sync raw.parquet ↔ S3 + drop split-cache fetch → restore incremental; (b) accept daily full-pull + bump timeout 30→60min. Awaiting principal call.

### FOLLOW-ON CHANGE (principal-cued): ORWO source-system unselected by default
- The dashboard "source system" filter = `orderSources` (Filters/types.ts; data col `source_system AS order_source`; sidebar key "sources"; meta.json `order_sources` includes "ORWO"). Convention: empty array = all selected.
- Change in `src/app/page.tsx` meta-load init: when URL has no `order_srcs` and user hasn't picked sources, set `orderSources = meta.order_sources.filter(s => s !== "ORWO")` (explicit all-but-ORWO inclusion list). Computed from meta (new sources auto-include); URL-pinned sources override. +11 lines.
- Verified `tsc --noEmit` exit 0. Committed cutover `1658e60` (pushed 75df9c4..1658e60), merged to main `0561a43` (pushed 4793a50..0561a43 via deploy worktree, clean). CICD rebuilding :latest; polling ECR (bg) past prev image 2b7af1b.
- [x] ORWO build LIVE (11:49): :latest = `sha256:b3eb570f3196c674c365734bdcacbee184e75220f064a0f6936c4b1174c8a0d2`, tagged `latest,0561a43` — CICD built from main, pod restarting. Both deploys confirmed today: cutover swap (2b7af1b, 10:16) + ORWO default (b3eb570f, 11:49).
- refresh.sh/DAG incremental fix: RECOMMENDED option (a) to principal (fix refresh.sh raw.parquet sync + entrypoint raw_cache exclude; bi-etl timeout bump as insurance). Awaiting principal go — not urgent (live dashboard already correct).
- [x] Principal said go (do 1+2, prep bi-etl). Changes 1+2 shipped: refresh.sh (sync raw.parquet ↔ raw_cache/, drop dead split-cache) + entrypoint.sh (--exclude raw_cache/* on pod sync). Committed cutover `cebace4` (pushed 1658e60..cebace4), merged main `137b946` (pushed 0561a43..137b946, clean FF). CICD rebuilding; polling ECR past b3eb570f.
- bi-etl timeout bump: PREPPED (edited execution_timeout 30→60min in bi-etl/dags/AI_Automations/nextjs_dashboard_dags/shipping-costs-monitoring-dag/shipping_costs_monitoring_dag.py) — HELD uncommitted for principal review/push (separate repo, Airflow picks up on deploy). NOTE: bi-etl tree has unrelated untracked files (others' .claude/, order_flagging WIP) — commit MUST be scoped to the DAG pathspec only.
- [x] Changes 1+2 build LIVE (11:56): :latest = `sha256:0608a7556c66cfe1ce5a4a97a1591b5966ecabca69bff73589f66f8ac0500a6f`, tagged `137b946`. THREE deploys confirmed today: cutover 2b7af1b(10:16) / ORWO b3eb570f(11:49) / incremental-fix 0608a755(11:56). Tomorrow 08:00 refresh uses new refresh.sh (full pull seeds raw.parquet, then incremental).
- [x] bi-etl DAG PUSHED (principal: "bump it" + "1 hour earlier"): execution_timeout 30→60min + schedule 08:00→07:00 Berlin. Commit on bi-etl main, scoped to DAG pathspec only (tree had others' untracked WIP). Push initially rejected (concurrent push to origin/main fe1ece677); rebased clean (incoming commits didn't touch the DAG), pushed → origin/main 44de63c37.
- TEST: principal wants to test the new refresh — will manually trigger the DAG in Airflow UI (I have no Airflow access). Run uses :latest 0608a755 (fixed refresh.sh) → first run full-pull seeds raw_cache/raw.parquet. I can verify outcome from S3 (watch raw_cache/raw.parquet appear + summary re-timestamp) when he triggers it.
- TEST RUN 1 FAILED (12:07, manual trigger, ran on img 0608a755): `ModuleNotFoundError: No module named 'duckdb'` at pipeline.py L496 (pull_raw full-pull DuckDB join). NOT a timeout (8:15 total, <60min) — pull of 13.2M shipment rows succeeded, crashed at the join. ROOT CAUSE: Dockerfile pip install missing `duckdb` (the [[S069_006248ef_pipeline-oom-hardening|S069]] OOM-fix DuckDB join needs it; old in-cluster image ran pre-DuckDB pipeline so never surfaced). Incremental path = polars-only, wouldn't hit it; this run was full-pull (no raw.parquet seed).
- [x] FIX: added `duckdb` to Dockerfile pip install. Committed cutover `1fdbc51` (pushed cebace4..1fdbc51), merged main `eed2ef8` (pushed 137b946..eed2ef8, clean FF). CICD rebuilding; polling ECR past 0608a755. Did NOT seed raw.parquet — let the re-trigger full-pull (now w/ duckdb) verify the fix end-to-end + seed the cache; incremental thereafter.
- [x] duckdb-fix build LIVE (12:28): :latest = `sha256:137472e31027adb7f9c06ad10bf29d4705ebce2593481331ed392bc6242db525`, tagged `eed2ef8`.
- NEXT: principal re-triggers DAG → expect full-pull success (~8min pull + DuckDB join) → raw_cache/raw.parquet seeded → subsequent runs incremental. Verify from S3: raw_cache/raw.parquet exists + summary parquets re-timestamp.
- CLEANUP still pending (remove _bi-analytics-deploy worktree + deploy-cutover-2026-05-26 branch) — after test confirmed.
