# [[S146_f20d7744_scm-serving-memory-review|S146]] · Dwarf D4 — SCM footprint review (Docker / k8s / data-volume / refresh)

**Role:** read-only review dwarf, Jebrim namespace. **Scope:** deployment & runtime footprint of `shipping_costs_monitoring_nextjs` (eating node memory + intermittent 502s). Serving-code review owned by other dwarves; this is image, runtime config, k8s resourcing, data volume, refresh job.

**Symptom under review:** SCM pod eats memory on its node + intermittently 502s. Cluster `bi-generic`, ns `shipping-dashboard`, deploy `shipping-costs-monitoring`, ECR `shipping_costs_monitoring`.

**Files read (read-only, no edits):**
- `docker/Dockerfile`, `docker/entrypoint.sh`, `docker/refresh.sh`
- `.github/workflows/deploy-shipping-costs-dashboard.yml`
- `dags/shipping_costs_monitoring_dag.py`
- `next.config.ts`, `package.json`
- `pipeline.py` L480–540 (`pull_raw` DuckDB), L2420–2480 (`_write_daily_product_summary` DuckDB)
- `src/lib/db.ts` L1–60 (serving DuckDB)
- bank note `projects/scm_nextjs_duckdb_oom_modes.md`

---

## TOP-LINE: the serving pod runs DuckDB in-process with NO memory_limit

This is the single most important footprint finding and it reframes the whole "node memory + 502" story.

- `package.json:19` — `duckdb-async` is a **runtime** dependency.
- `next.config.ts:6` — `serverExternalPackages: ["duckdb-async","duckdb"]` — DuckDB native addon ships in the serving image and runs **in the Node server process**.
- `src/lib/db.ts:22` — `db = await Database.create(":memory:")` — a singleton in-process DuckDB, **no `SET memory_limit` / `SET threads` anywhere** (grep confirms the only `memory_limit` settings in the repo are in `pipeline.py`, not the serving path).
- `src/lib/db.ts:28` + `query_for_range()` (L138–164) — each data request issues `read_parquet([...monthly files...])` over the processed glob.

**Why it costs memory:** DuckDB's default `memory_limit` is **~80% of detected system RAM** and default `threads` = core count. Inside a container *without* a cgroup-aware DuckDB build, "system RAM" = the **node's** RAM, not the pod limit. So a single analytical query can try to buffer up to ~80% of the *node* before the pod's cgroup OOM-kills it. `node --max-old-space-size=512` (`entrypoint.sh:14`) caps only the **V8 JS heap** — it has **zero** effect on DuckDB's native allocator. So the "512 MB" cap is a fiction for actual pod footprint: real RSS = V8 (≤512MB) + DuckDB native arena (potentially GBs) + the parquet mmaps. That is almost certainly the node-memory-eater, and a DuckDB allocation spike → OOM-kill / restart → in-flight requests 502 is a clean explanation for the *intermittent* 502s.

→ **D4-1 below is the headline fix.**

---

## FINDINGS

### D4-1 — Serving DuckDB has no memory_limit / thread cap (Critical)
- **Where:** `src/lib/db.ts:22` (`Database.create(":memory:")`), no `SET memory_limit`/`SET threads` in serving path; `docker/entrypoint.sh:14` caps only V8.
- **Issue:** in-process DuckDB defaults to ~80% of **node** RAM and N threads; the only memory cap in the pod (`--max-old-space-size=512`) doesn't govern it.
- **Why memory/502:** an analytical `read_parquet` over the monthly glob can spike native RSS well past the pod limit → cgroup OOM-kill → restart → 502 window. Concurrent requests multiply per-query arenas.
- **Fix (concrete):** on first connect set a hard cap sized to the pod limit, e.g. `SET memory_limit='1500MB'; SET threads=2; SET temp_directory='/app/.../data/_duckdb_tmp';` (size against whatever the pod's real memory limit turns out to be — see K8S checklist; rule of thumb DuckDB cap ≈ podLimit − V8(512MB) − ~256MB headroom). Spill dir lets big queries degrade gracefully instead of OOM-killing the pod.
- **Effort:** S (a few lines in `getConn()`), but sizing depends on the k8s memory limit (must fetch).

### D4-2 — Pipeline toolchain baked into the SERVING image (High — bloat + risk surface)
- **Where:** `docker/Dockerfile:19-20` (`pip3 install polars pandas pyarrow duckdb redshift_connector python-dotenv`), `:23-26` (full AWS CLI v2), `:36` (`pipeline.py`), `:31-34` (shared modules).
- **Issue:** the serving image carries the *entire* batch-pipeline stack (polars+pandas+pyarrow+duckdb+redshift_connector) and the AWS CLI, none of which `server.js` needs at runtime. polars+pandas+pyarrow+duckdb wheels alone are ~hundreds of MB.
- **Why it costs resources:** larger image = slower pulls / longer cold-start before readiness (a slow start can itself trip a too-tight readiness probe → 502 during rollout); bigger page-cache footprint; bigger attack/CVE surface. It does **not** by itself add steady-state heap, but it bloats the node.
- **Nuance:** the SAME image is reused by the refresh pod (DAG `ECR_IMAGE` = `shipping_costs_monitoring:latest`, runs `refresh.sh`→`pipeline.py`), so the Python stack *is* needed — but in the **refresh** pod, not the serving one. Right fix is a split, not deletion.
- **Fix (concrete):** two-target Dockerfile — a `serving` final stage (node + only `aws cli` for the startup `s3 sync`, no pip stack) and a `refresh` final stage (node-less or slim python + pipeline deps). Or at minimum a separate slim serving image; point the DAG at the refresh image. If splitting is too much now: confirm via the K8S checklist whether image-pull/cold-start is actually implicated before investing.
- **Effort:** M.

### D4-3 — Hardcoded Redshift credentials in image ENV (High — security, not memory)
- **Where:** `docker/Dockerfile:54-55` — `ENV REDSHIFT_USER=tcg_nfe`, `ENV REDSHIFT_PASSWORD=TcgNfe2024Pass!` (plaintext, baked into every image layer + ECR + git).
- **Issue:** live DB password in source control and in every pulled image layer. Same creds as `bi-analytics-main/NFE/.env` (the `tcg_nfe` full-access user). Out of memory scope but must be flagged.
- **Fix:** move to a k8s Secret + `envFrom`/`valueFrom: secretKeyRef`; rotate the password (it's compromised by being in git history). The serving pod arguably doesn't need Redshift creds at all (it reads parquet from S3, not Redshift) — only the refresh pod does, which strengthens the D4-2 image split.
- **Effort:** S (k8s secret) + rotation coordination.

### D4-4 — Refresh runs as a SEPARATE pod; serving & refresh do NOT contend (confirmed — this is good, but note the namespace mismatch)
- **Where:** `entrypoint.sh:14` runs **only** `node server.js` (no pipeline). `dag.py:62-93` runs refresh as a `KubernetesPodOperator` that spins a temp pod (`cmds=["bash"]`, `arguments=["./docker/refresh.sh"]`), `on_finish_action="delete_pod"`.
- **Confirmed:** refresh does **not** run in the serving pod — they never share pod memory. So the serving pod's footprint is *purely* server + in-process DuckDB (D4-1), not the 11.3GB pipeline peak. The 20Gi pipeline OOM history in the bank note is the **refresh pod**, a different blast radius.
- **Namespace mismatch to flag:** the refresh pod runs in `namespace="pcs-dashboard"` with SA `pcs-dashboard-sa` (`dag.py:68-69`), while serving is in `shipping-dashboard` (deploy CI) / the brief says `shipping-dashboard`. Refresh writes to S3; serving reads from S3 — they only couple through the bucket, so cross-namespace is fine functionally, but confirm the serving SA actually has S3 *read* on `etl-poc-dev/nextjs_dashboards_data/shipping_costs_monitoring/` (if `aws s3 sync` at startup fails or is slow, the pod is up but data-less → 502s; see D4-6).
- **Effort:** n/a (finding); verification only.

### D4-5 — Deploy CI carries NO resource spec, NO probes (High — root-cause candidate for both symptoms)
- **Where:** `.github/workflows/deploy-shipping-costs-dashboard.yml` — builds, pushes, `kubectl rollout restart`. **Never** applies a manifest. So requests/limits/probes/replicas/HPA live in an unversioned manifest applied out-of-band (not in this repo).
- **Issue:** if the serving Deployment has **no memory limit**, D4-1's DuckDB will happily eat the node (no cgroup ceiling to stop it) — that directly matches "eating memory on its node." If it has a limit but it's generous, DuckDB's 80%-of-node default still overshoots. Either way the manifest is the missing half of the sizing.
- **Why 502:** no/short readiness probe + a slow startup (big image pull D4-2 + `aws s3 sync` of ~240MB+ D4-6) means traffic hits the pod before it's ready, or a too-aggressive liveness probe restarts a pod that's merely busy in a long DuckDB query → 502.
- **Fix:** (1) version the k8s manifest into this repo and have CI `kubectl apply` it; (2) set memory request/limit explicitly and size D4-1's DuckDB cap to it; (3) readiness probe that only passes after `s3 sync` + first DuckDB connect; liveness probe with a generous `timeoutSeconds`/`failureThreshold` so a long query isn't read as a hang.
- **Effort:** M.

### D4-6 — Data volume: ~240MB+ processed glob synced to pod-local `./data` on every startup (Medium — depends on volume type)
- **Where:** `entrypoint.sh:11` `aws s3 sync "${S3_DATA_PATH}" data/ --exclude "raw_cache/*"`; `Dockerfile:58` `DATA_DIR=/app/.../data`. Serving reads `read_parquet` over `data/processed/*.parquet` (the whole-history monthlies, ~241MB+ per brief) plus `daily.parquet`, `daily_product.parquet`, `filter_combos.parquet`, alerts/issues/deviations.
- **Issue / why memory:** if the Deployment backs `./data` (or the whole rootfs) with `emptyDir: { medium: Memory }`, **every byte of that ~240MB+ counts against the pod's RAM** — on top of D4-1's DuckDB arena. DuckDB also `mmap`s the parquet on `read_parquet`, so the page cache for the working set adds RSS pressure. A memory-backed emptyDir here would be a large, fixed, invisible RAM tax.
- **Fix:** ensure `./data` is on **disk-backed ephemeral storage** (default `emptyDir` with no `medium`, or a small PVC), never `medium: Memory`. Size `ephemeral-storage` request/limit to fit the synced data + DuckDB spill dir. This is the #1 manifest fact to confirm (see K8S checklist).
- **Effort:** S once the manifest is in hand.

### D4-7 — Refresh-pod DuckDB memory_limit values (context — confirms bank note, refresh blast radius only)
- **Where (current values, confirmed this read):**
  - `pipeline.py:530` (`pull_raw` full-refresh DuckDB join) — `SET memory_limit='4GB'` + `temp_directory=_duckdb_tmp` + `preserve_insertion_order=false`.
  - `pipeline.py:2464` (`_write_daily_product_summary`, UNNEST(shop_order_groups)+9-dim GROUP BY) — `SET memory_limit='8GB'` + same temp_dir + insertion-order off.
- **Confirms** the bank note (4GB / 8GB). DAG sizes the refresh pod at `requests mem 10Gi / eph 12Gi`, `limits mem 20Gi / eph 20Gi` (`dag.py:79-80`), pipeline peak measured ~11.3GB RSS (`dag.py:75-77`).
- **Serving inheritance:** the serving image *contains* `pipeline.py` and its 4GB/8GB blocks, but `entrypoint.sh` never invokes them — so the serving pod does **not** inherit this RAM risk. The serving DuckDB risk is entirely D4-1 (uncapped), a *different* and currently *unmitigated* exposure.
- **Effort:** n/a (context).

### D4-8 — `aws s3 sync ... --delete` on refresh + app-state files (Low — data hygiene, minor)
- **Where:** `refresh.sh:24-29` syncs `data/` up with `--delete` but `--exclude dismissed_alerts.json --exclude changelog.json`. Startup sync (`entrypoint.sh:11`) pulls everything except `raw_cache/*`.
- **Note:** fine as-is, but the serving pod's local writes to dismissed_alerts/changelog are pod-ephemeral and only durable if the serving pod also pushes them to S3 (not seen in entrypoint — serving appears read-only on S3). Flag for the serving-code dwarf: confirm where app-state persistence happens; not a memory issue.
- **Effort:** n/a.

---

## K8S MANIFEST FACTS TO RETRIEVE (not in this repo — required to finish sizing)

The deploy CI never applies a manifest, so all of this lives out-of-band. Fetch before finalizing D4-1/D4-5/D4-6.

| # | Fact needed | Why it matters | Command |
|---|---|---|---|
| 1 | **Serving memory request + limit** | Sizes D4-1 DuckDB cap; if unset, D4-1 can eat the node | `kubectl describe deployment shipping-costs-monitoring -n shipping-dashboard` (Limits/Requests block) |
| 2 | **CPU request + limit** | DuckDB `threads` should track CPU limit; CPU throttle can slow startup → probe 502 | same `describe deployment` |
| 3 | **Replica count** | Per-replica DuckDB arena multiplies node RAM; 1 replica + restart = full outage window (502) | `kubectl get deployment shipping-costs-monitoring -n shipping-dashboard -o wide` |
| 4 | **Liveness/readiness probe config** (path, initialDelay, timeoutSeconds, failureThreshold) | Short/aggressive probe vs slow `s3 sync`+cold DuckDB = restarts/502; the prime 502 suspect after D4-1 | `kubectl describe deployment ... -n shipping-dashboard` (Liveness/Readiness lines) |
| 5 | **Volume type for `/app/.../data`** (emptyDir? medium: Memory? PVC?) | `medium: Memory` would make the ~240MB+ data a RAM tax (D4-6) | `kubectl get deployment shipping-costs-monitoring -n shipping-dashboard -o yaml` → inspect `volumes:` + `volumeMounts:` |
| 6 | **ephemeral-storage request/limit on serving pod** | Must fit synced data + DuckDB spill dir; too-low → evicted | `kubectl describe deployment ... -n shipping-dashboard` |
| 7 | **HPA presence/targets** | Scaling on CPU while the real pressure is memory = thrash | `kubectl get hpa -n shipping-dashboard` |
| 8 | **Actual OOMKills / restart reasons** | Ground-truth: is it OOM (→D4-1/D4-6) or probe (→D4-5)? | `kubectl get events -n shipping-dashboard --sort-by=.lastTimestamp \| grep -iE 'oom\|kill\|unhealthy\|backoff'` AND `kubectl describe pod -l app=shipping-costs-monitoring -n shipping-dashboard` (Last State: OOMKilled, exit 137) |
| 9 | **Node memory pressure / which node** | Confirms "eating its node" — is one pod dominating a node? | `kubectl top pod -n shipping-dashboard` and `kubectl top node` |
| 10 | **Refresh CronJob vs Airflow-only** | Confirm no in-cluster CronJob also invokes refresh.sh in the serving ns | `kubectl get cronjob -A \| grep -i shipping` (expect none — refresh is the Airflow KubernetesPodOperator in `pcs-dashboard`) |
| 11 | **Serving SA + S3 read perms** | If startup `s3 sync` fails/slow → up-but-dataless → 502 (D4-4) | `kubectl get sa -n shipping-dashboard`; check IRSA annotation; review startup logs `kubectl logs deploy/shipping-costs-monitoring -n shipping-dashboard \| grep -i sync` |

**Diagnostic order of attack:** run #8 first (OOMKilled exit-137 → it's memory, prioritize D4-1+D4-6+#1+#5; "Unhealthy"/probe events → prioritize D4-5+#4). Then #1/#5/#9 to size the cap.

---

## SUMMARY OF FIXES BY PRIORITY
1. **D4-1 (Critical, S):** cap serving DuckDB `memory_limit` + `threads` + spill dir — the headline memory-eater, currently uncapped.
2. **D4-5 (High, M):** version the k8s manifest, set explicit serving memory limit, fix probes — the 502 root-cause half that isn't in this repo.
3. **D4-6 (Medium→Critical-if-true, S):** confirm `/data` is NOT a memory-backed emptyDir; size ephemeral-storage.
4. **D4-2 (High, M):** split serving image from refresh image — image bloat / cold-start.
5. **D4-3 (High, S+rotation):** Redshift creds → Secret + rotate (security).
