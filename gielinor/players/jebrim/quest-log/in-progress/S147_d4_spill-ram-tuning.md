# [[S147_dcb495a7_scm-perf-audit|S147]] D4 — spill-vs-RAM & DuckDB runtime tuning

**Verdict:** The 512MB cap is a *correct OOM guard but a latency liability* — at 512MB the resident `bd_cache` breakdown temp table + concurrent aggregations will spill to a container-disk temp dir, and `threads=2` caps scan parallelism. The high-leverage move is to **raise the pod limit and DuckDB limit together** (the cap is set far too conservatively against the 1536Mi pod) and to **bake `DUCKDB_MEMORY_LIMIT` into the Dockerfile** — right now it's a live `kubectl set env` that vanishes on the next image redeploy.

---

## Findings (file:line evidence)

### Connection setup — `src/lib/db.ts` getConn (lines 16–53)
- `memLimit = process.env.DUCKDB_MEMORY_LIMIT || "4GB"` (`db.ts:35`). **Code default is 4GB; live env override is 512MB** (`kubectl set env DUCKDB_MEMORY_LIMIT=512MB`). So the running cap is 512MB, but a fresh deploy *without* the env var would revert to a 4GB DuckDB limit on a 1536Mi pod → instant OOM. (This is the durability hole — see below.)
- `threads = process.env.DUCKDB_THREADS || "2"` (`db.ts:36`). Default **2 threads**. No live override observed → 2 is the running value.
- `temp_directory = DUCKDB_TEMP_DIR || join(DATA_DIR, "_duckdb_tmp")` (`db.ts:37,40`). DATA_DIR = `/app/.../data` (`Dockerfile:58`), which is **container disk, not memory-backed** (good — spills go to real ephemeral disk, not back into the cgroup). But it lives under the same dir the S3 data sync writes (`entrypoint.sh:11`), so spill I/O and the parquet read both hit the same ephemeral volume.
- `preserve_insertion_order=false` (`db.ts:41`) — already set; correct, lowers per-query memory for ORDER-free aggregations.
- One **singleton connection** for the whole pod (`db.ts:9–25`). The 512MB `memory_limit` is therefore a **single shared budget across all concurrent requests** on that connection, not per-query. Concurrency multiplies pressure against one fixed ceiling. (Relevant to D1 pooling — see below.)

### Memory math (pod budget)
- Pod: **1536Mi app container + 128Mi nginx-auth sidecar** (from brief; no serving manifest in-repo — only the *pipeline* DAG at `dags/shipping_costs_monitoring_dag.py:78–80`, which is the 10–20Gi ETL pod, unrelated to serving).
- Node heap cap: `node --max-old-space-size=512` (`entrypoint.sh:14`) → ~512MB V8 heap.
- DuckDB native allocator is **outside V8** (`db.ts:27–32`) → the 512MB DuckDB cap is *additive* to the 512MB node heap.
- **Budget formula:** `duckdb_limit ≈ pod_limit − node_heap − resident_overhead − spill_headroom`.
  - Current: `1536 − 512 (heap) − ~250 (node RSS baseline + libduckdb + fc_mem + bd_cache resident) − headroom` ⇒ the safe DuckDB working ceiling is ~**600–750MB**, *not* 512. The 512 cap was set defensively post-OOM and leaves ~250–400MB on the table.
- `temp_directory` on container disk does **not** count against the pod memory limit (it's ephemeral-storage), so spills relieve memory pressure but cost disk I/O + latency.

### Spill-prone query classes at 512MB
1. **`bd_cache` breakdown temp table** (`api/breakdown/route.ts:122–136`) — `CREATE OR REPLACE TEMP TABLE bd_cache` materializes per-shipment rows (13+ cols incl. 11 bucket cols) over a *wide* date window (main+baseline+3mo margin, or an 18-month default when unbounded — `route.ts:69–88`). This is the **biggest sustained resident object**. The whole-history version (~241MB per-shipment, `route.ts:73`) was the prior OOM driver; even the bounded 18-month version is large and **resident for the connection's life**, eating into the 512MB before any query runs → forces concurrent aggregations to spill.
2. **Export** (`api/export/route.ts:159–162`) — one row PER SHIPMENT, no LIMIT, materialized into a JS array + full CSV string on the 512MB *heap* (not DuckDB). Now guarded by a `COUNT(*)` pre-check + 413 over `EXPORT_MAX_ROWS=500000` (`route.ts:142–157`) and excluded from cache (`MAX_CACHE_ROWS=20000`, `db.ts:85,121`). DuckDB-side the scan itself can spill; heap-side the 500k-row CSV is the risk.
3. **processedAsDaily on-the-fly aggregation** (`db.ts:234–262`) — the dual-filter (packagetype + SOG) tier scans + GROUP-BYs pruned processed parquet inline per request; large groupings spill the hash aggregate to temp_directory at 512MB.

### Threads
- `threads=2` (`db.ts:36`). Low threads = **capped parallelism on the big processed scans** (241MB glob), so cold breakdown/export scans are slower than they need to be. But raising threads *multiplies* per-operator memory against the shared 512MB cap → at the current low limit, raising threads would *increase* spill frequency. Threads and memory_limit must move together.

---

## Tuning recommendations (arithmetic + effort)

**Option A (recommended) — raise both pod limit and DuckDB limit; raise threads.** Effort **M** (touches deploy manifest + Dockerfile; no app code).
- Pod app container `1536Mi → 2560Mi` (2.5Gi). Sidecar 128Mi unchanged.
- `DUCKDB_MEMORY_LIMIT 512MB → 1536MB`. Budget check: `2560 − 512 (heap) − ~300 (overhead) ≈ 1748` headroom ⇒ 1536MB cap is safe with ~200MB margin.
- `DUCKDB_THREADS 2 → 4`. With 1536MB the per-thread operator memory has room; 4 threads ~halves cold-scan latency on the 241MB processed glob.
- Net effect: `bd_cache` + concurrent aggregations stay in RAM (few/no spills), big scans parallelize. Cost: +1Gi pod memory (~+1Gi cluster cost on that pod).

**Option B (cheaper) — keep ~512MB cap, optimize spill path + modest thread bump.** Effort **S**.
- Keep pod at 1536Mi. Raise `DUCKDB_MEMORY_LIMIT 512MB → 700MB` (safe per budget above; reclaims the conservative margin).
- Keep `temp_directory` on container disk (already correct, `db.ts:37`) but consider a dedicated `DUCKDB_TEMP_DIR=/app/.../_duckdb_tmp` *outside* the S3-sync `data/` tree so spill I/O doesn't contend with data refresh.
- Leave `threads=2` (raising threads at this cap re-pressures it). Accept spills on the largest breakdowns/exports.
- Net: smaller latency win, no extra cluster cost, still spill-bound on the heaviest queries.

**Per-connection interaction (for D1 pooling):** the 512MB (or any) `memory_limit` is set on the *connection* (`db.ts:38`). DuckDB's memory_limit is actually **database-instance-wide**, not per-connection, so adding more connections off the same `Database` instance does NOT multiply the cap — but it DOES multiply concurrent in-flight operator memory competing for that one budget. If D1 introduces a pool, the budget arithmetic above is unchanged (one DB = one limit), but **threads × pool_concurrency** is the real pressure multiplier to size against. Don't raise threads and pool size at the same time without re-running the budget.

---

## Durability fix (version-control the live env)

`DUCKDB_MEMORY_LIMIT=512MB` is currently live **only** via `kubectl set env` — it is **not in any committed file**. Grep confirms the only in-repo references are the *code default* (`db.ts:35`, which is `4GB`) and comments; no Dockerfile `ENV`, no manifest in this repo.

**Risk:** the next image rebuild/redeploy ships a pod with no `DUCKDB_MEMORY_LIMIT` → `getConn` falls back to the **4GB** code default (`db.ts:35`) on a 1536Mi pod → immediate OOM regression of the exact bug [[S146_f20d7744_scm-serving-memory-review|S146]] fixed.

**Permanent fix — bake the env into the image.** Add to `docker/Dockerfile` alongside the existing `ENV` block (after `Dockerfile:61`, the `NODE_ENV=production` line):
```
ENV DUCKDB_MEMORY_LIMIT=...   # final tuned value
ENV DUCKDB_THREADS=...
```
Better: also change the **code default** at `db.ts:35` from `"4GB"` to a pod-safe value (e.g. the chosen cap) so the 4GB landmine is removed even if the ENV is ever dropped. If the serving pod has a k8s manifest outside this repo (likely — the deployment YAML wasn't found here), set it there too and keep the Dockerfile `ENV` as the floor. **Pick one source of truth and make the 4GB code default safe regardless.**

---

## Needs live measurement (before turning knobs)

1. **Spill activity at current 512MB cap.** Check for files appearing/growing in the temp_directory (`/app/.../data/_duckdb_tmp`) during a heavy breakdown + export. Or `PRAGMA database_size;` / DuckDB's `duckdb_temporary_files()` table function mid-query. Confirms spills are actually happening (the whole premise).
2. **Query timings at the cap** — instrument the slowest endpoints (breakdown cold-create, export, processedAsDaily dual-filter) with server-side timing logs. Compare cold (temp-table-create) vs warm (cached). Establishes the latency baseline to beat.
3. **Resident memory floor** — measure pod RSS at idle (after fc_mem + a populated bd_cache) to confirm the ~250–300MB overhead estimate in the budget formula before committing to 1536MB.
4. **Peak concurrency** — how many simultaneous heavy requests actually occur? Single-user dashboard → the shared-budget pressure may be theoretical; pooling (D1) may be unnecessary. Measure before sizing threads × pool.
5. **bd_cache resident size** — `SELECT estimated_size FROM duckdb_tables() WHERE table_name='bd_cache'` (or row count × row width) for the 18-month default window. This is the single number that decides how much of the 512MB is gone before any query runs.

---

## Open / needs principal
- Serving-pod k8s manifest is **not in this repo** — couldn't verify the live pod limit (1536Mi) or where to commit the env from source. Need the manifest location (likely a separate infra/deploy repo) to land the durable fix in the right place.
- Whether to raise the pod limit (Option A, costs cluster memory) is a cost/latency call for Niklavs.
