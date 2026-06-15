# SCM Breakdown tab — filter-change load performance model

Source: `bi-analytics-main/.../shipping_costs_monitoring_nextjs/` route `src/app/api/breakdown/route.ts` + component `src/components/BreakdownTab.tsx`. Shipped [[S240_a7f855d6_scm-breakdown-filter-load-perf|S240]] (commit `c10818a`), building on [[S146_f20d7744_scm-serving-memory-review|S146]]/[[S147_dcb495a7_scm-perf-audit|S147]] memory work. Cross-link: [[scm]] digest.

## Where filter-change latency comes from (3 classes)
- **Sidebar dim filters** (country/provider/site/shop/order-source) + min/max cost → baked into the `bd_<hash>` cache-table fingerprint → **rebuild** = parquet scan within the wide date window. Expensive but largely unavoidable (the cache is what makes everything after cheap).
- **Date (within window) + cost-basis toggle** → cache reused; level queries re-run. Cheap, and now result-cached.
- **Bucket filter** → was a full refetch returning **identical** data (the breakdown table cost is cost-basis-driven, NOT bucket-driven — the route `buckets` param feeds `bucketSumExpr`, which is never called; bucket decomposition lives in the separate Buckets chart / `/api/breakdown-buckets`).

## The caching/memory architecture ([[S146_f20d7744_scm-serving-memory-review|S146]]/[[S147_dcb495a7_scm-perf-audit|S147]], do not regress)
- Filtered rows live in **fingerprint-named immutable catalog tables `bd_<hash>`** in the one shared in-memory DuckDB (visible to all per-request connections). Same filter-set → same table → reused across requests AND drill-downs; different filters → different table → no cross-request CREATE-OR-REPLACE race. **LRU-capped** (`BD_MAX_TABLES`, default 8) — that cap is the memory bound.
- Because `bd_<hash>` is immutable, level-query **results are result-cached** too (db.ts `runOn`): the `isUncacheable` guard skips only literal `BD_CACHE`, not `bd_<hash>`. So cost-basis toggles / re-expands hit the cache.
- **Memory constraint (principal, [[S240_a7f855d6_scm-breakdown-filter-load-perf|S240]]):** never cache multiple filter-sets beyond the LRU cap or raise DuckDB `memory_limit` — that undoes the pod-safe bounding. Speedups must be memory-neutral.

## The [[S240_a7f855d6_scm-breakdown-filter-load-perf|S240]] wins (memory-neutral)
- **Bucket independence:** `filterQS(f, includeBuckets=false)` for the table's `baseQS` → bucket toggles no longer refetch the table. Sparklines keep buckets.
- **One-request refresh:** `/api/breakdown?specs=<JSON[{level,expand,expand2,expand3}]>` returns `{total, level0, children}` in one call (mirrors the breakdown-sparklines `specs` batch). Client effect-1 fires it once and marks `fetchedRef` synchronously so the incremental-expand effect only handles new clicks. Filter change with N nodes open: **2+N → 1 request**, child waterfall removed.

## If more speed is needed later (not done)
Fan out the `specs` level queries onto their own connections (like the sparkline batch does) for parquet-scan parallelism; browser-side result cache keyed by full QS (client memory, not server).
