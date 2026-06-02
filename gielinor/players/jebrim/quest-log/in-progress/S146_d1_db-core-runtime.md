# [[S146_f20d7744_scm-serving-memory-review|S146]] · D1 — SCM serving core + runtime memory audit (read-only)

**Dwarf:** D1 (review-only) · **Player:** Jebrim · **Session:** [[S146_f20d7744_scm-serving-memory-review|S146]]
**Scope:** `shipping_costs_monitoring_nextjs` SERVING node — DuckDB core (`src/lib/db.ts`), runtime memory model, Docker launch (`--max-old-space-size=512`), `next.config.ts`, `package.json`. Reviewed `csv.ts`, `utils.ts`, `cost-basis.ts`, and the two heaviest routes (`export`, `breakdown`) for result-size/native-memory pressure.
**Symptom under investigation:** pod eating memory + intermittent 502 (serving process crashing/OOM).
**Caveat / unknown:** pod RAM limit + requests are NOT in this repo (K8s manifests not in scope). Sizing recommendations below are conditional on that number — flagged explicitly.

---

## The one-paragraph model (read this first)

The 502s are almost certainly **container OOM-kill, not JS-heap OOM.** Two memory pools live in this pod and only one is bounded:

1. **JS heap** — capped at 512MB by `--max-old-space-size=512`. If *this* overflowed you'd see a V8 `FATAL ERROR: Reached heap limit / JavaScript heap out of memory` and a clean Node crash, not a 502 from a half-dead process.
2. **DuckDB native memory** — a `:memory:` database, **completely outside** the JS heap, with **no `memory_limit`, no `temp_directory` (so no disk spill), and `preserve_insertion_order` left at its memory-hungry default.** Every query that scans the ~241MB processed parquet, plus the persistent `bd_cache` TEMP table and `fc_mem` table, accumulates here. This pool can grow until the **cgroup memory limit** kills the container (SIGKILL → in-flight requests 502). The pipeline side of the SAME codebase already learned this lesson and caps all three pragmas (`pipeline.py:530-532`, `:2464-2466`); the serving connection (`db.ts:16-37`) sets none of them. That asymmetry is the headline finding.

---

## CRITICAL

### C1 — Serving DuckDB connection sets no `memory_limit` / `temp_directory` / `preserve_insertion_order`
**`src/lib/db.ts:16-37` (`getConn`)** — the connection is created with `Database.create(":memory:")` and never issues a single `PRAGMA`/`SET`. Compare the pipeline, which explicitly does `SET memory_limit=...; SET temp_directory=...; SET preserve_insertion_order=false;` (`pipeline.py:530-532` for the 4GB path, `:2464-2466` for the 8GB COPY path).

**Why it costs memory / causes the 502:** DuckDB's default `memory_limit` is ~80% of *detected system RAM* — and inside a container DuckDB typically reads the **host node's** RAM, not the cgroup limit. So DuckDB believes it may use (say) 80% of a 32GB node = ~25GB, while the pod is limited to maybe 1-2GB. With **no `temp_directory`, DuckDB cannot spill to disk** — it has nowhere to go but RAM, blows past the cgroup limit, and the kernel OOM-kills the container. `preserve_insertion_order=true` (the default) forces DuckDB to buffer full result/intermediate sets to preserve row order, which is pure overhead for an aggregation dashboard that re-sorts in SQL anyway. This is the single most likely root cause of the intermittent 502.

**Concrete fix** — in `getConn`, immediately after `db.connect()` and before the `fc_mem` create, run:
```sql
SET memory_limit='<budget>';      -- see C5 for value; e.g. '768MB' on a 2GB pod
SET temp_directory='/tmp/duckdb'; -- enables disk spill instead of OOM
SET preserve_insertion_order=false;
SET threads=<N>;                  -- cap to pod CPU limit; default = host cores
```
`memory_limit` is the hard guard (DuckDB errors the one offending query instead of OOM-killing the whole pod); `temp_directory` is the safety valve (spill > crash); `preserve_insertion_order=false` is free savings. **Effort: S** (≈5 lines). Highest ROI change in the audit.

> Note: also set `threads` — DuckDB defaults thread count to *host* cores, and each thread carries its own morsel buffers, multiplying native memory on a many-core node where the pod only gets 1-2 vCPU.

---

### C2 — `bd_cache` persistent TEMP table is an unbounded native-memory resident
**`src/app/api/breakdown/route.ts:107-136` (`ensureTempTable` / `doCreate`)** — `CREATE OR REPLACE TEMP TABLE bd_cache AS SELECT ... FROM <pruned processed parquet> WHERE cost_for_routing IS NOT NULL <dim filters>`, over a **wide date window** (`wideDateRange`: earliest−3mo … latest+1mo, default `2024-01-01..2099-12-31` when dates absent — `route.ts:69-79`). The table is keyed by a *dimension-only* fingerprint and **lives in the singleton `:memory:` DB across requests**.

**Why it costs memory:** this materializes a large, wide row set (15+ columns incl. all 11 bucket cols) entirely in DuckDB native RAM and *keeps it resident* between requests. When filters are empty/broad and dates absent, it can be the bulk of the 241MB parquet decompressed into memory — easily several hundred MB native, on top of every concurrent query's working set. Combined with C1 (no `memory_limit`), this is the accumulation that tips the pod over. The `CREATE OR REPLACE` only replaces on *fingerprint change*; a broad first query plants a large table that sits there until the next distinct filter set.

**Concrete fix (in priority order):**
1. C1's `memory_limit` + `temp_directory` makes this *survivable* (spills instead of OOM) — do that first.
2. Tighten `wideDateRange` defaults — the `2024-01-01..2099-12-31` fallback (`route.ts:71`) should clamp to the actual data max, not 2099; the +1mo/−3mo margin is reasonable but the no-date branch defeats month-pruning entirely.
3. Consider dropping `bd_cache` on a TTL / LRU (it has neither) so a broad one-off query doesn't pin native memory indefinitely. Even a `DROP TABLE IF EXISTS bd_cache` after N seconds of idle would bound it.

**Effort: S** for (1)+(2), **M** for (3). This is a real finding independent of C1 — flagging to the breakdown-route reviewer too, but it's load-bearing here because it's the largest native resident.

---

## HIGH

### H1 — Query result cache evicts by ENTRY COUNT, not bytes — 500 large arrays is unbounded heap
**`src/lib/db.ts:61-109`** — `queryCache` caps at `MAX_CACHE_ENTRIES=500` and evicts the single oldest entry when full (`setCache`, `:95-109`). Entries are the **fully-converted result arrays** (`setCache(ck, converted)` from `query`/`rawQuery`, `:432`,`:459`).

**Why it costs memory:** the cap is on *cardinality*, not *size*. 500 small filter-option lookups cost ~nothing; but 500 large result sets (e.g. `breakdown` bulk fetches, `export`-shaped pulls, trend matrices) at even a few hundred KB each is 100s of MB of **JS heap** — and the heap is only 512MB (C5). One burst of varied large-result requests can fill the cache with heavyweights and the count-based eviction won't notice. This is a plausible secondary contributor (heap-side) on top of the native-side C1/C2.

**Concrete fix:** make the cache **byte-aware**:
- Track an approximate byte size per entry (cheap: `JSON.stringify(data).length` at insert, or row-count × an estimated row width) and evict on a **total-bytes budget** (e.g. 64-128MB) rather than entry count.
- **Skip caching results above a per-entry threshold** (e.g. don't cache any result whose array length or estimated bytes exceeds N) — large one-off pulls (export-shaped) shouldn't evict 50 useful small entries and shouldn't sit in heap for 60s.
- The TTL design is otherwise fine (60s + 5min sweep); keep it.

**Effort: M.** Note the export route bypasses the cache implicitly? No — `export` calls `rawQuery` which DOES cache (the SQL starts with `SELECT`, not CREATE/DROP/INSERT/DELETE/BD_CACHE — `db.ts:447-451`). So a large CSV export's full row set **is cached for 60s in heap**. That's a concrete instance of this bug → see H2.

### H2 — `/api/export` caches its full shipment row set in heap
**`src/app/api/export/route.ts:136`** → `rawQuery<ExportRow>(sql, ...values)`. The export SQL is `SELECT ... FROM <pruned processed> WHERE <date+dims> ORDER BY ...` with **no LIMIT** — it returns *every matching shipment row* (potentially tens/hundreds of thousands). Because it starts with `SELECT`, `rawQuery` routes it through the cache (`db.ts:453-460`), so the entire materialized array is **held in the 512MB heap for 60s** under cache key, in addition to the transient `convertBigInts` copy (H3) and the CSV string built by `rowsToCsv`.

**Why it costs memory:** a single large export can spike heap by (raw result array) + (deep-cloned copy) + (CSV string) simultaneously, and then *retain* the array for 60s. Concurrent exports stack. With a 512MB heap this is a credible OOM/502 trigger on its own.

**Concrete fix:** mark export (and any other unbounded full-row pull) as `skipCache: true` — but `rawQuery` has no such param despite the doc comment at `db.ts:437` claiming it does (the param was never implemented — see M1). Minimum fix: add a `skipCache` option to `rawQuery` and pass it from export; ideally also stream the CSV rather than building the whole string in memory. **Effort: S** (skipCache) / **M** (streaming).

### H3 — `convertBigInts` deep-clones every result (transient 2× copy), recursive, per-row-per-field
**`src/lib/db.ts:380-391`**, called on every `c.all(...)` result in both `query` (`:431`) and `rawQuery` (`:450`,`:458`). It builds a brand-new array of brand-new objects (`obj.map(...)` + `Object.entries` rebuild per row).

**Why it costs memory / CPU:** for the duration of conversion both the original DuckDB-returned array AND the converted copy are live → **transient ~2× peak heap** for that result. Under concurrency (multiple large results converting at once on the shared event loop) these transient peaks overlap and stack. For a wide result with many rows it's also CPU-heavy (allocates an object per row + walks every field), blocking the single Node event loop and contributing to slow/timing-out requests that can present as 502 behind a proxy.

**Concrete fix:** mutate in place instead of deep-cloning — walk the rows and convert BigInt fields on the existing objects (`for (const row of result) for (const k in row) if (typeof row[k]==='bigint') row[k]=Number(row[k])`). Eliminates the 2× copy and most allocations. Even better: have DuckDB return numbers directly where possible. **Effort: S.** Material under concurrency + large results; minor for small results.

### H4 — Single shared connection serializes all routes through one DuckDB session (+ shared mutable temp-table state)
**`src/lib/db.ts:9-37`** — one `db` + one `conn` for the whole process, all ~34 API routes. DuckDB-async runs statements on this single connection.

**Why it matters for memory/correctness:**
- **Concurrency/serialization:** heavy queries (breakdown bd_cache rebuild, export full-scan) contend on the one connection; a slow scan can head-of-line-block lighter requests, inflating tail latency and the in-flight request count (each holding its own result memory) → memory pressure spikes under load, the classic precursor to an OOM burst.
- **Shared mutable temp state:** `bd_cache` is a single global temp table on the shared connection; concurrent breakdown requests with *different* fingerprints race to `CREATE OR REPLACE` it. The route has a `tempTableLock` mutex (`route.ts:65,130`) and recreate-on-loss guards (`:690`,`:730`), which mitigates correctness — but it means concurrent distinct-filter breakdown calls **serialize on temp-table rebuild**, each rebuild re-materializing a large native table. Worst case: thrashing the largest native object repeatedly under concurrent varied filters.

**Concrete fix:** lower-priority than C1/C2 but worth noting — a small connection *pool* (e.g. 2-4 connections) for read queries would parallelize scans, BUT `bd_cache`/`fc_mem` are per-connection temp/in-memory tables, so a pool needs those promoted to a shared catalog or per-connection re-creation. Given the bd_cache design, the cleaner path is: keep one connection but ensure C1's `memory_limit`+`threads` bound the blast radius, and treat the serialization as acceptable for a low-QPS internal dashboard. **Effort: L** to pool properly; **flag, don't rush.** The memory guardrails (C1) matter more than parallelism here.

---

## MEDIUM

### M1 — `rawQuery` doc promises a `skipCache` param that doesn't exist
**`src/lib/db.ts:437-438`** — JSDoc says *"Pass `skipCache: true` for DDL / temp table operations"* but the signature is `(sql, ...params)` with no options object. Skip behavior is instead *inferred* from SQL keywords (`db.ts:447-451`). The doc is misleading and, more importantly, there's **no way for a caller to opt a large `SELECT` (like export) out of caching** — which is exactly what H2 needs. **Fix:** implement the `skipCache` option for real. **Effort: S.**

### M2 — `fc_mem` table held for process lifetime; `fcColumns` set cached forever
**`src/lib/db.ts:28`** (table) + **`:43-52`** (`fcColumns`). ~404KB table + a Set, both never invalidated. Small in absolute terms, but note: on a data **refresh** (`invalidateQueryCache` exists, `:81-83`) `fc_mem` is NOT rebuilt and `fcColumns` is NOT reset — stale filter combos can persist until pod restart. Memory cost is minor; correctness/staleness is the real note. **Fix:** rebuild `fc_mem` + clear `fcColumns` inside `invalidateQueryCache`. **Effort: S.**

### M3 — `existsSync` + `require("fs")` on the hot `processedPruned` path
**`src/lib/db.ts:160-161`** — `const { existsSync } = require("fs")` inside the function (re-required each call) and an `existsSync` per candidate month. Not a memory issue; a minor sync-FS-on-event-loop + repeated-require smell on a path hit by most queries. **Fix:** hoist the import to module top. **Effort: S.**

---

## LOW

### L1 — `--max-old-space-size=512` is likely too low *given* the workload, but the real fix is bounding native memory first
**`docker/entrypoint.sh:14`.** 512MB JS heap for a server that caches up to 500 result arrays (H1) and full CSV exports (H2) is tight. BUT raising it blindly is wrong: the heap and DuckDB-native pools share the **same cgroup limit**, so giving Node more heap leaves *less* for DuckDB native and can make C1's OOM *worse*. The correct relationship (the answer to scope Q5):

```
pod memory limit (cgroup)  ≥  node_heap + duckdb_memory_limit + overhead
                                  (512MB)   (C1 value)        (~150-250MB:
                                                               Node base, parquet
                                                               mmap, OS buffers)
```
So: **set the pod limit explicitly, then partition it.** Example for a **2GB pod limit**: `--max-old-space-size=640` (heap) + DuckDB `memory_limit='768MB'` + ~600MB headroom for native scan working set, mmap, and overhead. For a **1GB pod** this app is uncomfortable — `--max-old-space-size=384` + DuckDB `memory_limit='384MB'` and accept that broad bd_cache queries will spill to `/tmp` (hence C1's `temp_directory` is mandatory at that size). **The 512 isn't a misconfiguration per se — the missing DuckDB cap is. Fix C1 first, then size the heap to whatever's left under the pod limit.** **Effort: S** (config), but requires the pod RAM number (UNKNOWN — must be confirmed from the K8s manifest, out of this repo's scope).

### L2 — `serverExternalPackages` correct; no other next.config memory levers
**`next.config.ts:6`** correctly externalizes `duckdb-async`/`duckdb` (native addon must not be bundled). `output: "standalone"` is right for the slim image. Nothing here is causing the leak — noting it's *correct* so the next reviewer doesn't chase it. **No action.**

### L3 — `duckdb-async@^1.4.2` floating caret
**`package.json:19`.** Caret range on a native-addon dep means image rebuilds can pull a newer 1.x with different memory behavior. Minor supply-chain/reproducibility note; pin if memory behavior must be stable across rebuilds. **Effort: S.**

---

## Answers to the 5 scoped questions (direct)

1. **Should serving DuckDB set `memory_limit`+`temp_directory`+`preserve_insertion_order=false`? YES — this is C1, the top finding.** Values depend on the (unknown) pod limit. Conditional recommendation: on a 2GB pod → `memory_limit='768MB'`, `temp_directory='/tmp/duckdb'`, `preserve_insertion_order=false`, `threads=2`. The pipeline already proves the pattern (`pipeline.py:530-532`). `temp_directory` is non-negotiable at any size — it converts OOM-kill into a recoverable spill.

2. **Is the query cache safe? NO — count-based, not byte-aware (H1).** 500 large arrays in a 512MB heap is unbounded relative to heap. Make it byte-budgeted (≈64-128MB total), skip caching oversized results, keep the 60s TTL. Export caching its full row set (H2) is the concrete worst case.

3. **`convertBigInts` 2× copy — material under concurrency? YES (H3).** Transient peaks overlap and stack on the shared event loop for large results; also CPU-blocking. Fix: mutate in place.

4. **Single shared connection (H4):** serializes heavy scans (head-of-line blocking → in-flight memory spikes) and forces a single global mutable `bd_cache` that concurrent distinct-filter requests thrash. Pooling is **L effort** and complicated by per-connection temp tables — prefer bounding native memory (C1) over pooling.

5. **Is 512MB heap appropriate (L1)?** It's not the root misconfiguration — the missing DuckDB native cap is. Right relationship: `pod_limit ≥ node_heap + duckdb_memory_limit + ~200MB overhead`. Set the pod limit explicitly and partition it; raising heap without capping native makes OOM worse.

---

## Ranked fix order (for the principal)
1. **C1** (S) — set the 4 DuckDB pragmas on the serving connection. Single highest-ROI change; most likely stops the 502.
2. **C2 step 2** (S) — clamp `wideDateRange` no-date fallback off 2099; **C2 step 1** is subsumed by C1.
3. **H2 + M1** (S) — implement `skipCache` and use it for `/api/export` (+ ideally stream CSV).
4. **H1** (M) — byte-aware cache with per-entry skip + total-bytes budget.
5. **H3** (S) — in-place BigInt conversion.
6. **L1** (S, blocked on pod RAM number) — partition pod limit between heap and DuckDB.
7. **H4** (L) — only if QPS justifies; bounding memory matters more than parallelism.

## Unknowns flagged
- **Pod memory limit + CPU limit** (K8s manifest, not in repo) — needed to pick concrete `memory_limit` / `--max-old-space-size` / `threads` values. All numeric recommendations above are conditional examples (2GB pod).
- Whether DuckDB inside this container reads cgroup or host RAM for its default `memory_limit` — version-dependent; setting `memory_limit` explicitly (C1) makes it moot, which is *why* C1 is the safe move regardless.
- Actual row counts behind `/api/export` and broad `bd_cache` queries — not measurable from a repo with no local `data/` (pulled from S3 at runtime). Sizing of H1/H2/C2 risk is therefore qualitative; the mechanism is certain, the magnitude needs a live pod metric (`duckdb_memory_usage` / RSS).
