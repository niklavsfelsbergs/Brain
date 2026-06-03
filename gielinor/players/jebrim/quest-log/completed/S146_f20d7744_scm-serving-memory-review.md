# S146 — SCM serving-node memory review (502 / resource audit)

**Session:** f20d7744 · **Player:** Jebrim · **Opened:** 2026-06-02 · **Type:** read-only review (fan-out)

## Ask (principal)

> The SCM (cut over to the shipping mart) is eating a lot of resources on the node that runs it and crashes sometimes with 502. Review where we can save memory and what's not built optimally.

Resolved to the **serving node** (Next.js web process) of `shipping_costs_monitoring_nextjs`, not the batch pipeline. 502 = serving process crash/OOM, distinct from the [[S069_006248ef_pipeline-oom-hardening|S069]]/[[S097_1ce9fc1f_scm-daily-product-temp-spill-oom|S097]] pipeline OOMs.

Repo under review: `Documents/GitHub/bi-analytics-main/NFE/dashboards/shipping_costs_monitoring_nextjs/` (read-only).

## Scouting findings (principal, pre-fan-out)

1. **Node heap capped at 512MB** — `docker/entrypoint.sh:14` `node --max-old-space-size=512 server.js`. Likely direct 502 trigger.
2. **Query cache evicts by count not bytes** — `src/lib/db.ts:61-63`, `MAX_CACHE_ENTRIES=500` full result arrays.
3. **Serving DuckDB conn has no `memory_limit`/`temp_directory`** — `db.ts:16-37`. Pipeline lesson ([[S069_006248ef_pipeline-oom-hardening|S069]]/[[S097_1ce9fc1f_scm-daily-product-temp-spill-oom|S097]]) never ported. Native mem outside the 512MB → second OOM vector.
4. **Export materializes full result + CSV string, no streaming, and caches the giant array** — `src/app/api/export/route.ts:134-137` (rawQuery cache path).
5. **Full-history scans in request path** — `avg-costs/route.ts:20` calls `processedAsDaily()` with no date bounds → full `processed/*.parquet` glob.
6. `convertBigInts` deep-clones every result (transient 2× heap).
7. refresh.sh is a **separate** entrypoint (not co-run with the server) — refresh/serve contention likely NOT a factor; confirm it's a separate CronJob/pod.

**Unknown (not in repo):** pod resource request/limit, replicas, probes, HPA. Need `kubectl describe` + OOMKill events to confirm which vector fires.

## Fan-out (4 dwarves)

- **D1** — `db.ts` core + runtime memory model.
- **D2** — all ~38 API routes: scan/payload hazards.
- **D3** — export + CSV + large-payload builders.
- **D4** — pipeline.py footprint + Dockerfile/runtime + next.config + k8s resource expectations.

## Turn log

- T1 — Grounded via keepsake + prior quests ([[S055_9837afe8_shipping-costs-dashboard-cutover-review|S055]] cutover review, [[S097_1ce9fc1f_scm-daily-product-temp-spill-oom|S097]]/[[S069_006248ef_pipeline-oom-hardening|S069]] pipeline OOM, bank note `scm_nextjs_duckdb_oom_modes`). Scouted db.ts/Dockerfile/entrypoint/export. Confirmed 512MB heap cap. Principal chose fan-out review. Posted OPEN. Spawning 4 dwarves.
- T2 — All 4 dwarves returned (D1 db-core, D2 route-scan ×35 routes, D3 export/payload, D4 footprint/k8s). Findings in `S146_d{1,2,3,4}_*.md`.

## Synthesis — root cause + ranked fixes

**ROOT CAUSE (all 4 converge): the 502 is container OOM-kill (cgroup, exit 137), NOT JS-heap OOM.** The serving DuckDB `:memory:` connection sets no `memory_limit`; DuckDB native memory defaults to ~80% of *node* RAM (not pod-aware), lives entirely OUTSIDE the 512MB V8 heap, and a single heavy `read_parquet` over the processed glob spikes native RSS past the pod limit → SIGKILL → in-flight requests 502. `--max-old-space-size=512` caps only V8 and does nothing for DuckDB. Intermittent because it only OOMs when a heavy query (or two concurrent) lands.

**Confirmed good:** refresh does NOT run in the serving pod (separate Airflow KubernetesPodOperator, ns `pcs-dashboard`) — serving/refresh never contend.

**Ranked fixes:**
- **C1 (S) — cap the serving DuckDB conn** (`db.ts:16-37`): `memory_limit` + `temp_directory` + `preserve_insertion_order=false` + thread cap. The one fix that stops the OOM regardless of pod size. Port the pipeline's lesson (pipeline.py:530).
- **C2 (S→L) — `bd_cache` temp table** (breakdown route): ~20 per-shipment cols of a wide processed slice into a resident TEMP table on the SHARED conn, no TTL/LRU, 2024-2099 no-date fallback defeats pruning. Biggest sustained native-RAM driver + cross-request contention. Quick: bound the window. Proper: per-request connection.
- **C3 (S→M) — `/api/export`** (`export/route.ts:134`, `csv.ts:28`, `db.ts:438`): no-LIMIT per-shipment SELECT → ~0.9-1.2GB array for 3M rows + full CSV string + array ALSO cached 60s. Single biggest single-request bomb; 60s retention explains intermittent OOM. Quick: COUNT pre-check + 413 over ~500k + skipCache. Proper: stream via ReadableStream.
- **C4/H (S→M) — full-history scans in request path:** 11 routes can scan the full processed glob (~241MB). 5 always/silently (avg-costs no-args `:20`; trends/country-trends/packagetype-trends/completeness hit processed tier with NO order_date filter on pkg+SOG). Rest fall back to full glob on empty from/to (db.ts:142 silent full-glob). Fix: make `processedPruned`/`processedAsDaily` THROW on missing bounds (one change exposes every latent hazard) + prune avg-costs + add order_date filters.
- **H — query cache evicts by COUNT not bytes** (db.ts:61): few large arrays blow the heap. Byte-aware cap / don't cache export+outliers.
- **H — `convertBigInts` deep-clones every result** (db.ts:380): transient 2× heap, stacks under concurrency. In-place mutation.
- **H — `/api/outliers`:** per-shipment, no LIMIT, cached, held in client React state. LIMIT + skipCache.
- **M — image bloat:** full pip pipeline stack + AWS CLI baked into SERVING image (needed only by separate refresh pod). Split candidate.
- **M/Security — hardcoded Redshift password** in `Dockerfile:55` ENV; serving doesn't need it. Rotate + remove.
- **M — `/data` volume:** ~240MB+ s3-synced to pod-local each startup; IF `emptyDir{medium:Memory}` it's a fixed RAM tax on top of DuckDB. Confirm volume type.
- **Note — `--max-old-space-size`:** only raise after knowing pod limit; raising heap above the pod limit just converts a Node OOM into an OOMKill.

**MISSING HALF (not in repo) — k8s serving manifest. Run FIRST to confirm vector:**
- `kubectl describe pod -n shipping-dashboard -l app=shipping-costs-monitoring` → Last State / exit 137 (OOMKilled = memory path) vs Unhealthy (probe path).
- `kubectl get events -n shipping-dashboard --sort-by=.lastTimestamp | grep -iE 'oom|kill|unhealth'`
- `kubectl get deploy shipping-costs-monitoring -n shipping-dashboard -o yaml` → mem request/limit, replicas, probes, volume type, HPA.

Pending: principal next-step call (implement quick wins vs writeup vs confirm-vector-first).

- T3 — Principal chose **full fix pass on a branch**. Implemented on an isolated worktree off `origin/main` ([[S097_1ce9fc1f_scm-daily-product-temp-spill-oom|S097]] pattern; bi-analytics-main is dirty on `feat/fif-orwo-standalone`, untouched). Worktree: `C:/Users/niklavs.felsbergs/Documents/GitHub/_scm-mem-fix`, branch `fix/scm-serving-memory`, commit **abfbcdb** (LOCAL, not pushed). 9 files, +185/-33.

## Code changes shipped (branch fix/scm-serving-memory)

`src/lib/db.ts`:
- **C1** getConn: `SET memory_limit` (env `DUCKDB_MEMORY_LIMIT`, def 4GB) + `threads` (def 2) + `temp_directory` (def `DATA_DIR/_duckdb_tmp`, env `DUCKDB_TEMP_DIR`) + `preserve_insertion_order=false`. The crash fix.
- cache: `MAX_CACHE_ROWS=20_000` — never cache oversized results (kills the retained export/outliers copy).
- `convertBigInts` in-place (no per-query deep clone).
- `processedPruned` missing-bounds → bounded trailing window (`PROCESSED_FALLBACK_MONTHS`, def 24) + `console.warn` (chose bounded+logged over hard-throw since I couldn't runtime-verify no normal flow omits bounds; C1 backstops crash-safety).

routes: export (COUNT + 413 over `EXPORT_MAX_ROWS` def 500k + no-store); outliers (LIMIT `OUTLIER_MAX_ROWS` def 10k + truncated flag); avg-costs + completeness (prune processed to trailing N-period window, 400 if no `to`); breakdown (no-date bd_cache window 18mo, was 2024–2099); trends/country-trends/packagetype-trends (processed tier → `dailyTierExpr`, range-pruned + correct columns; daily tiers byte-identical).

**Verification:** `tsc --noEmit` exit 0 (clean). `next build` → "Compiled successfully" + passed lint/type validity; failed only at page-data collection on the missing `duckdb.node` native binary (local node-25 can't build it via `--ignore-scripts`; node:20 Docker image builds it). Runtime behavior unverified locally (needs the live pod). vitest binary absent in local install; untouched modules (`shifts.ts`/`alerts.ts`) carry the existing tests.

## Deploy-side TODO (NOT code — manifest/infra, principal/deploy owns)

These are the missing half — the serving k8s manifest is not in the repo (CI only `rollout restart`s):
1. **Confirm the vector + size the cap:** `kubectl describe pod -n shipping-dashboard -l app=shipping-costs-monitoring` (Last State exit 137 = OOMKilled) and read the pod **memory limit**. Set `DUCKDB_MEMORY_LIMIT` ≈ pod_limit − 512MB(node heap) − data-volume(if memory-backed) − ~512MB overhead.
2. **`/data` volume type:** if `emptyDir{medium: Memory}`, the ~240MB parquet sync is a RAM tax on top of DuckDB — switch to disk-backed emptyDir, and point `DUCKDB_TEMP_DIR` at real disk (else spill is still RAM).
3. **Probes:** check liveness/readiness timings vs the s3-sync + cold-DuckDB startup — aggressive probes are an independent 502 source.
4. **Hardcoded Redshift password** `Dockerfile:55` → move to a k8s Secret (refresh pod needs it; serving doesn't — do NOT just delete, it'd break refresh). Rotate the exposed credential.
5. **Image split** (optional): the serving image bakes the full pip pipeline stack + AWS CLI (only the separate refresh pod needs them). Slimmer serving image = faster cold start, smaller blast radius.
6. Consider raising `--max-old-space-size` (entrypoint.sh) only after the pod limit is known — above the pod limit it just converts a node OOM into an OOMKill.

Pending: principal review of branch abfbcdb → push + PR; run the kubectl confirm + deploy-side items; runtime validation on the pod.

- T4 — Branch pushed (`fix/scm-serving-memory` on `picanova/bi-analytics`); principal to merge + check live. **Live symptom reported:** clicking "View on alert" → Breakdown tab shows no data; 2nd alert click → "failed to load data"; hard reload → chart loads. **Diagnosed (grounded in code):** the `bd_cache` shared-connection temp-table race — `bd_cache` is one global temp table on the single shared DuckDB connection keyed by module-global `cachedFingerprint` (`breakdown/route.ts:64`); DuckDB temp tables are connection-scoped, so concurrent/rapid breakdown requests with different filters stomp each other's `CREATE OR REPLACE` → empty (wrong fingerprint's rows) / "bd_cache does not exist" mid-replace (the route's own retry blocks at :700/:740 confirm it recurs). Alert→breakdown fires several panel fetches at once + 2nd click overlaps. **This is the C2/C4 "proper" fix DEFERRED this session — the shipped branch only bounded the temp-table window, NOT the race.** Next fix: per-request `db.connect()` (connection-local temp tables) or `bd_cache_<fp>` or inline CTE. Logged in resume as the prioritized next step. Confirm via pod logs grep `bd_cache`.

- T5 — **Got cluster access (principal AWS creds) and confirmed the cause LIVE — it's the OOM, not bd_cache.** `kubectl describe pod`: serving container Last State Terminated / **Reason OOMKilled / Exit 137 / Restart Count 3** + a BackOff event (crash-loop). Pod memory **limit = 1536Mi**, request 768Mi (2 containers: app 1536Mi + `nginx-auth` sidecar 128Mi). `grep bd_cache` in current+previous logs returned **nothing** → the bd_cache race was NOT firing; the OOM was. My fix IS deployed (`DUCKDB_MEMORY_LIMIT` present in `/app/.next/server/chunks/2676.js`, image `:latest`) but the env var was unset → ran on the **4GB code default** > 1.5GB pod → OOM. Exactly the caveat I flagged at ship time. `/data` is container disk (not memory-backed) — temp spill is safe. **FIX APPLIED (principal said yes):** `kubectl set env deployment/shipping-costs-monitoring -n shipping-dashboard DUCKDB_MEMORY_LIMIT=512MB` → rolled out clean → new pod `7964d58f96-h74mr` **2/2 Running, 0 restarts**, env confirmed. OOM crash-loop resolved. (Lesson reinforced: instrument, don't re-guess — my chat-side bd_cache hypothesis was wrong; live evidence corrected it.)

- T6 — Close (2nd close of S146). Principal handed off the **next session: a general speed/performance audit of the SCM dashboard** — cutover likely left non-optimal loads. Brief captured at the top of the resume's Open items (request fan-out, repeat/double scans, tier+parquet layout, spill-vs-RAM, cold-start S3 sync, client caching; starting corpus = the 4 S146 dwarf findings). S146 stays in-progress (durability + perf tuning + bd_cache structural fix + the new perf-audit thread all open). Harvest: 1 examine draft (live-evidence-beats-a-confident-chat-diagnosis).
