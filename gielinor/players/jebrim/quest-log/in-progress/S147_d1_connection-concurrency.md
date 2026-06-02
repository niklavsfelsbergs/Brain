# [[S147_dcb495a7_scm-perf-audit|S147]] D1 — DuckDB connection model & request concurrency

**Dwarf trace — read-only audit. SCM dashboard, post-S146-fix code (== deployed main).**
Read root: `_scm-mem-fix/NFE/dashboards/shipping_costs_monitoring_nextjs/`

## Verdict (one line)

The dashboard runs **every** API query through a **single shared DuckDB `Connection`** whose native binding **serializes statements on one job queue** — so a tab that fans out N parallel `/api/*` calls does not get N-way DB parallelism; the calls queue head-to-tail on one connection. This is the dominant latency structure, and it is a real (not theoretical) serialization point. The highest-leverage fix is a **bounded per-request / pooled connection model** sized against the 512MB cap.

---

## How the connection model actually works (mechanism, evidenced)

- `src/lib/db.ts:9-11` — module-level singletons: `db: Database`, `conn: Connection`, `connLock`. `getConn()` (`db.ts:16-53`) returns the **one** cached `conn` for every caller forever after cold start. The `connLock` mutex (`db.ts:19,48-52`) only guards *cold-start creation* — it does **not** serialize per-query; once `conn` exists, every `getConn()` returns it immediately.
- `db.ts:493` (`query` → `c.all(...)`) and `db.ts:512,520` (`rawQuery` → `c.all(...)`) — both helpers run on that shared `conn`. Every route in `src/app/api/**` goes through one of these two helpers, so **all queries share one connection**.
- **duckdb-async is a thin promisify wrapper** (`node_modules/duckdb-async/dist/duckdb-async.js:85-90` — `Connection.all` just calls `connAllAsync(this.conn, ...)`). No queue, no mutex, no parallelism of its own; it inherits the native binding's semantics.
- **Native `duckdb@1.4.2` binding queues per connection.** `node_modules/duckdb/lib/duckdb.js:435` comment: *"this queues up a job in the internals, which blocks the below close call"* — statements submitted on one connection run through that connection's **single internal task queue**, processed in submission order. Concurrent `conn.all()` calls therefore **do not execute concurrently inside DuckDB**; the second waits for the first to finish on the connection. (DuckDB's intra-query parallelism via `SET threads` — `db.ts:39`, default 2 — speeds up *one* query across cores, but does **not** make two queued statements on one connection overlap.)

**Net:** client-side `Promise.all` over several `/api/*` routes looks parallel in the browser and in Next's request handling, but the DB work **funnels to one serial queue**. Wall-clock for a tab ≈ sum of its queries' DB times, not the max.

---

## Request fan-out per load (client → API → shared conn)

Initial page load (`src/app/page.tsx`) fires, all landing on the one connection:
- `/api/changelog` (`page.tsx:286`, on mount)
- `/api/meta` (`page.tsx:363`)
- then post-meta, **fire-and-forget** `/api/breakdown?level=total` pre-warm (`page.tsx:401`) — kicks off a `processedPruned` parquet scan + `bd_cache`-adjacent total query *concurrently with* the next two
- `/api/filter-options` (`page.tsx:461`, 100ms-debounced; re-fires on every sidebar filter change, `page.tsx:449-470`)
- `/api/overview?mode=kpi` (`page.tsx:424`, Overview tab active)

Per-tab fan-out (each tab's calls are client-`Promise.all`/parallel `useEffect`s, but **all queue on one conn**):
- **Overview** — 1 heavy call (`/api/overview`, `OverviewTab.tsx:554`) + the page-level overview fetch.
- **Transit Times** — **5 calls**: `/api/transit/heatmap` (`TransitTimesTab.tsx:93`), then a 3-way `Promise.all` of `kpis`+`completeness`+`histogram` (`TransitTimesTab.tsx:116-119`), plus `/api/transit/trend` (`TransitTimesTab.tsx:144`). All fire near-simultaneously on tab open → 5 statements queued serially on the shared conn. **Worst fan-out tab.**
- **Breakdown** — bulk fetch issues a server-side `Promise.all` of total + level0..3 (`breakdown/route.ts:713-737`), i.e. up to 5 heavy CTEs queued on the same conn behind `ensureTempTable`.

The pre-warm (`page.tsx:401`) is well-intentioned but, because it shares the connection, it **competes** with `meta`/`overview`/`filter-options` for the same queue on first paint rather than running "in the background."

---

## Ranked findings

### F1 — Single shared connection serializes all concurrent queries · leverage HIGH · sev HIGH · effort M
**Evidence:** `db.ts:10,16-53` (one cached `conn`); `db.ts:493,512,520` (all queries use it); `duckdb-async.js:85-90` + `duckdb.js:435` (native per-connection job queue).
**Impact:** any tab/page that issues k concurrent API calls pays ~Σ(DB time) not max(DB time). Transit (5) and Breakdown bulk (≤5) are hit hardest. Under two users at once, their queries also interleave on the one queue — cross-user head-of-line blocking.
**Fix:** move to a **per-request connection** (`const c = await db.connect()` per request, closed in `finally`) OR a **small fixed pool** (e.g. 3–4 connections, round-robin/checkout). `Database` (the `:memory:` instance) is shared and supports multiple connections cheaply; only the `Connection` is the serialization unit. This unlocks real DB-side parallelism for a tab's fan-out.
**Caveat (sizing):** each DuckDB connection draws from the instance `memory_limit`. The [[S146_f20d7744_scm-serving-memory-review|S146]] cap is per *instance* via `SET memory_limit` (`db.ts:35,38`) — in DuckDB the limit is a **global/instance** setting, so multiple connections **share** that one budget (they do not each get a fresh 512MB), but they can **contend** for it: N heavy queries running truly in parallel can collectively approach the cap and spill/contend where today they ran one-at-a-time well under it. So a pool must be sized so that `poolSize × peak-query-working-set < cap`; with the prod cap ([[S146_f20d7744_scm-serving-memory-review|S146]] note: `DUCKDB_MEMORY_LIMIT=512MB` live; `db.ts:35` default is `4GB`), keep the pool **small (2–3)** and lean on `temp_directory` spill (`db.ts:40`) as the backstop.

### F2 — `bd_cache` shared temp table is a cross-request contention + correctness hazard · leverage HIGH · sev MED-HIGH · effort M
**Evidence:** `breakdown/route.ts:64-65` (module-level `cachedFingerprint` + `tempTableLock`), `:91-146` (`ensureTempTable` recreates one shared `bd_cache` keyed by a filter fingerprint), `:122` (`CREATE OR REPLACE TEMP TABLE bd_cache`), retry blocks `:698-709` and `:735-757`.
**Impact:** `bd_cache` is **one** temp table on the **one** shared connection, keyed by a single `cachedFingerprint`. Two requests with **different filters** racing → request B's `CREATE OR REPLACE` clobbers the table A is mid-query against, or A's fingerprint check passes then B recreates → A's level queries hit a table that no longer matches its filters (or `does not exist`, triggering the retry path `:700,740`). `tempTableLock` (`:101,140-145`) serializes *creation*, but the **subsequent level queries are not under the lock**, so an interleaved recreate between create and read is possible. The two retry blocks are evidence this race already bites in practice (HMR is cited, but a filter-divergent concurrent request is the same failure shape). Cost: under concurrent differing-filter use, repeated full `processedPruned` re-scans (the expensive part) thrash.
**Fix:** a **per-request connection** (F1) makes `bd_cache` a **session-local temp table** — each request creates its own `bd_cache` on its own connection, no cross-request clobber, no fingerprint race, and the retry blocks become dead code. This is the case where F1 fixes *both* the serialization and a latent correctness/contention bug, which is why F1+F2 should be done together. (If pooling instead of pure per-request, the fingerprint cache must become per-connection, not module-global.)

### F3 — First-paint pre-warm competes on the same queue · leverage MED · sev LOW-MED · effort S
**Evidence:** `page.tsx:401` fires `/api/breakdown?level=total` fire-and-forget immediately after meta, while `filter-options` (`:461`) and `overview` (`:424`) are also in flight — all on one conn.
**Impact:** the pre-warm's `processedPruned` scan + total CTE (`breakdown/route.ts:649-652`, `buildTotalQuery`) is heavy and now sits **ahead of or interleaved with** the queries that block first paint (overview KPIs), because they share the serial queue. Intended to help Breakdown's first visit; in practice can delay Overview's first render.
**Fix:** with F1 in place this self-resolves (pre-warm runs on its own connection). Without F1, gate the pre-warm behind `requestIdleCallback` / a short delay so it doesn't contend with first-paint queries. S effort either way.

### F4 — `threads=2` default caps single-query parallelism · leverage LOW-MED · sev LOW · effort S
**Evidence:** `db.ts:36,39` — `DUCKDB_THREADS` default `2`.
**Impact:** orthogonal to the connection issue — this bounds how fast *one* query runs across cores, not how many queries overlap. On a multi-core pod, 2 threads may under-use the box for a single heavy scan. But raising it multiplies per-query memory pressure against the 512MB cap, so it interacts with F1 sizing.
**Fix:** treat as a tuning knob *after* F1/F2 land and live timings exist; don't raise blindly under the tight memory cap. Note only.

---

## Needs live measurement (cannot confirm from code alone)

1. **Actual per-query DB time** for each route under the prod data volume — needed to know whether serialization is the *binding* latency (queries are slow enough that queueing matters) or whether queries are fast and the felt slowness is elsewhere (network, parquet cold read, client render). The serialization is structurally real; its *magnitude* needs timings.
2. **Concurrency level in practice** — how many simultaneous users/tabs hit one pod. With 1 user the serial queue still serializes a tab's own fan-out (5 Transit calls); with N users it's N× worse. Real concurrency determines F1's payoff.
3. **Queue wait vs execution split** — instrument time-from-`getConn()`-to-`c.all()`-start vs `c.all()` duration to directly measure head-of-line blocking on the shared conn. This is the one measurement that *proves* F1's value before doing the refactor.
4. **Pool-size memory ceiling** — empirically, how much working set a peak Breakdown/Transit query holds, to size the pool so `poolSize × working-set` stays under 512MB without thrashing spill. Confirm whether the [[S146_f20d7744_scm-serving-memory-review|S146]] cap is instance-global (expected) and how N parallel queries actually contend for it under load.
5. **`bd_cache` race incidence** — grep prod logs for the `[breakdown] bd_cache lost` / `does not exist` retry warnings (`route.ts:701,741`); their frequency tells whether F2's race is firing live today.
