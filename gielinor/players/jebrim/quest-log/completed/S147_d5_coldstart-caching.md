# [[S147_dcb495a7_scm-perf-audit|S147]] D5 — cold start & client/server caching

**Verdict:** Cold start is dominated by a single blocking, sequential ~240MB+ S3 sync before the server even binds — that's the restart/scale-up latency floor; caching is functional but conservative (30s `max-age`, no SWR anywhere, no client-side response cache/dedup, server cache lost on every restart). The image is also bloated with a full Python+AWS-CLI stack the serving pod doesn't need at runtime.

Read root: `_scm-mem-fix/NFE/dashboards/shipping_costs_monitoring_nextjs/` (== deployed main). Read-only audit; no app files edited.

---

## COLD START / STARTUP LATENCY

### C1 — Server readiness blocks on a full sequential S3 sync (HIGH, effort M)
`docker/entrypoint.sh:11-14`
```
aws s3 sync "${S3_DATA_PATH}" data/ --exclude "raw_cache/*"
echo "... S3 sync complete"
exec node --max-old-space-size=512 server.js
```
The node server is `exec`'d **only after** `aws s3 sync` returns. So on every cold start / restart / scale-up, time-to-ready = (S3 sync wall time of all dashboard parquet) + node boot. The synced set is the dashboard parquet — `processed/*.parquet` (~241MB per the `db.ts:172` comment) plus `daily`, `daily_product`, `filter_combos`, `alerts`, `issues`, `deviations_summary`, `outlier_thresholds`. `aws s3 sync` parallelizes object transfers internally (default 10 concurrent), so it's not strictly serial per-file, but it is **fully blocking** and there is **no readiness gate** — a pod that gets killed (OOM exit 137 was the [[S146_f20d7744_scm-serving-memory-review|S146]] story) re-pays the entire sync before serving a single request.
- **Fix (effort M):** the cleanest large win is to **not sync on startup at all** — mount the data as a shared read-only volume (EFS/PVC) populated by the refresh pod, so serving pods come up reading the volume directly (ready in ~node-boot time). If a volume isn't available, second-best: keep the sync but front it with a **readiness probe on the HTTP port** so K8s doesn't route traffic (or count the pod healthy) until node is actually up, and tune `aws s3 sync` concurrency (`AWS_CLI_S3_MAX_CONCURRENT_REQUESTS`) up for the many-small-`processed/` files.

### C2 — No in-repo readiness/liveness probe; sync vs probe race is unmeasurable here (HIGH to confirm, effort S)
No k8s manifest, no `readinessProbe`/`livenessProbe`/`startupProbe` anywhere in the repo (`grep` clean across `*.yaml`/`*.yml`/`*.py`). The refresh side is an Airflow `KubernetesPodOperator` (`dags/shipping_costs_monitoring_dag.py:28,65`, 10–20Gi memory — that's the *pipeline* pod, not serving). The **serving Deployment manifest lives outside this repo**, so probe config can't be audited from source.
- **Risk:** if a `livenessProbe` exists with a short `initialDelaySeconds`/`failureThreshold`, it can fire **during** the C1 sync (server not yet listening) → kill → restart → re-sync → loop. This is the classic "pod never becomes ready because the liveness probe races the long startup" failure, and it's invisible from this repo.
- **Fix (effort S, in the external manifest):** use a **`startupProbe`** with a generous `failureThreshold × periodSeconds` budget covering worst-case sync time, and keep `livenessProbe` lenient; gate `readinessProbe` on the HTTP port. Needs the deploy repo to confirm/fix.

### C3 — Serving image carries the full pipeline + AWS-CLI stack at runtime (MED, effort M)
`docker/Dockerfile:15-26`
```
apt-get install python3 python3-pip unzip curl
pip3 install polars pandas pyarrow duckdb redshift_connector python-dotenv
curl awscli... && /tmp/aws/install
```
The serving container needs **only** node + the AWS CLI (for the entrypoint sync) at runtime. `python3`, `pip`, and the whole `polars/pandas/pyarrow/duckdb/redshift_connector` stack (`Dockerfile:19-20`) plus `pipeline.py`+`sql/` (`Dockerfile:36-37`) are **refresh-pod only** — the same image is reused for both roles (one ECR image, `dag.py:35`). This bloats the serving image by hundreds of MB, which slows image pull on scale-up to a cold node (pull is part of cold-start latency too, alongside C1).
- **Fix (effort M):** split into two images (serving = node + aws-cli only; refresh = current full stack), or one multi-stage image where the serving stage drops the Python layers. If C1 moves to a mounted volume, the serving image can drop AWS CLI too and become a lean node-only image. The [[S146_f20d7744_scm-serving-memory-review|S146]] note already flagged this; it remains.

---

## CACHING

### K4 — Client uses plain `fetch` with zero response caching / dedup / SWR (HIGH, effort M)
`src/app/page.tsx` and all 21 fetching components use raw `fetch()` — confirmed no SWR / React Query / TanStack anywhere (`grep` for `swr|useSWR|react-query|@tanstack` returns nothing). Consequences:
- **No client-side cache:** revisiting a tab or toggling a filter back to a prior value re-hits the API every time (only the browser HTTP cache helps, and only within the 30s `max-age` window — K5).
- **No request dedup / coalescing:** filter changes fire debounced refetches (`page.tsx:460,476` use 100ms/150ms `setTimeout` + `AbortController`, which is good hygiene), but each tab manages its own fetches independently — a tab like Breakdown fans out 6 fetches (`BreakdownTab.tsx`), Transit 5 (`TransitTimesTab.tsx`); nothing dedups identical concurrent requests across components.
- **No stale-while-revalidate UX:** every refetch shows a loading spinner (`TabLoadingFallback`, `LoadingSkeleton`) instead of serving stale data instantly and revalidating.
- **Mitigations already present (good):** tabs are `lazy()` + `Suspense` and mount-once-keep-alive via `display:none` (`page.tsx:13-23,718-822`) — so a revisited tab keeps its React state and does **not** remount/refetch. Meta pre-warms the breakdown temp table fire-and-forget (`page.tsx:401`). Some components already use `sessionStorage` (`BreakdownTab`, `RateChangesTable`, `ChangelogTab`) but for UI state, not response caching.
- **Fix (effort M):** adopt **SWR** (smallest footprint, native stale-while-revalidate + dedup + focus-revalidate). Wrap the data fetches in `useSWR(key, fetcher, { dedupingInterval, revalidateOnFocus:false })`. Gets client dedup, an in-memory client cache, and instant stale render for free. Pair with K5.

### K5 — `Cache-Control: private, max-age=30` is short and has no SWR directive (MED, effort S)
`src/lib/db.ts:56` `CACHE_HEADER = { "Cache-Control": "private, max-age=30" }`, used by ~30 routes. Also inlined identically at `overview/route.ts:173`, `filter-options/route.ts:174`; `meta/route.ts:32` is `max-age=60`; `export/route.ts:169` correctly `no-store`.
- The data refreshes **daily** (refresh DAG → `refresh.sh`), so a 30s browser cache is far shorter than the data's actual freshness window. After 30s the browser refetches identical bytes.
- No `stale-while-revalidate` directive — the browser can't serve stale-then-revalidate at the HTTP layer either.
- **Fix (effort S):** raise to something like `private, max-age=300, stale-while-revalidate=86400` for the daily-refreshed data routes (keep `meta` similar; keep `export` `no-store`). Because data only changes once/day, a longer `max-age` + a long SWR window is safe and cuts repeat-fetch latency to ~0. Best paired with K6 (cache-busting on refresh) so a fresh daily refresh isn't masked by a stale client cache.

### K6 — Server query cache is correct but volatile + un-invalidated on data refresh (MED, effort S)
`src/lib/db.ts:70-135`: in-process `Map` cache, 60s TTL (`CACHE_TTL_MS=78`), 500-entry cap, 20k-row cap (`MAX_CACHE_ROWS=85`, the [[S146_f20d7744_scm-serving-memory-review|S146]] byte-cap fix to stop caching huge per-shipment export/outlier arrays). Sweep every 5min (`db.ts:88`). Solid for OOM-safety. Two gaps:
- **Volatile:** the cache lives in the node process heap, so it is **fully cold on every restart** (and every scale-up replica starts cold). Combined with C1, a restarted pod pays both the sync *and* a cold query cache → the first user of every distinct query eats the full DuckDB read. There's no warm-up beyond the single breakdown pre-warm in `page.tsx:401`.
- **Un-invalidated:** `invalidateQueryCache()` exists (`db.ts:103`) but nothing in-repo calls it (the refresh runs in a *separate* pod and writes to S3 → serving pods only see new data after their *own* next sync/restart, and the 60s TTL eventually ages entries out). So freshness is bounded by TTL, not by refresh — fine at 60s TTL, but becomes a correctness concern if K5 lengthens `max-age` without a refresh-triggered bust.
- **Fix (effort S):** key the client/HTTP cache on `meta.run_timestamp` (already returned by `meta/route.ts:28`) as a cache-buster query param or ETag, so a new daily refresh invalidates client caches deterministically — this is what makes a long K5 `max-age` safe. Server-side, a tiny `/api/admin/invalidate` hook the refresh DAG pings (or a watch on `meta.json` mtime, which `meta/route.ts:13` already does for its own cache) would let serving pods drop stale query-cache entries on refresh.

### K7 — Filter-options & overview fetch on a debounce but no shared cache key (LOW, effort S)
`page.tsx:449-470` (filter-options, 100ms debounce) and `page.tsx:473-481` (overview, 150ms debounce) both refetch on every filter tweak. The debounce + `AbortController` is correct, but with no SWR these never reuse a prior identical response (e.g. user toggles a filter off then on). Folds into the K4 SWR adoption — low standalone priority.

---

## NEEDS LIVE MEASUREMENT
- **Startup duration breakdown:** wall-clock of `aws s3 sync` in `entrypoint.sh` (the C1 floor) vs node boot. Pull from pod logs — the entrypoint already timestamps "Syncing data from S3..." and "S3 sync complete" (`entrypoint.sh:10,12`). Need the delta in prod and the total dashboard parquet size actually transferred.
- **Probe config (C2):** the serving Deployment manifest is **not in this repo** — read it from the deploy repo to confirm whether a `livenessProbe` can race the C1 sync, and whether `readinessProbe`/`startupProbe` exist. Highest-value external check.
- **Server query-cache hit rate:** `db.ts` has no metrics/logging on `getCached` hit vs miss. Add a counter (or temporary log) to measure hit rate in prod — quantifies how much K4/K6 actually save before investing in SWR + invalidation.
- **Image pull time on scale-up (C3):** measure serving image size and cold-node pull time to confirm the bloat is material to scale-up latency vs the C1 sync.
- **Replica count:** unknown from repo (Deployment is external). If >1 replica, each has an independent cold query cache (K6) and independent S3 sync (C1) — multiplies the cost and strengthens the shared-volume fix (C1).
