# [[S055_9837afe8_shipping-costs-dashboard-cutover-review|S055]] D3 — DuckDB Serving Layer + API Routes Review

**Scope.** Read-only technical review of the DuckDB serving layer for the shipping-costs dashboard (branch `shipping-mart-cutover`). Read in full: `src/lib/db.ts` (459 lines, the query engine), `src/lib/shifts.ts` (the `computeShifts` engine behind 4 routes), all 35 `src/app/api/**/route.ts` files, and `docs/reference.md`. High confidence on the SQL-injection surface (every route traced), the cache mechanics, and `processedPruned` enumeration. Medium confidence on tier-selection edge cases that depend on the actual parquet schemas (which I inferred from the SQL, not from the parquet files themselves — flagged where load-bearing).

Headline: **no SQL-injection vulnerability found** — all user values are parameterized; the only string-interpolated tokens are server-derived from fixed whitelists. The substantive findings are correctness/staleness bugs in the query-result cache and a confirmed hardcoded date floor, plus a tier-selection crash path.

---

## Critical

### C1. Query cache key is not stable across param key-ordering AND `processedAsDaily` bakes dates into SQL but `query()` caches on filter values only — wrong-data risk is low, but the cache **can serve stale rows after a data refresh within the TTL window** `[TECH]`
`src/lib/db.ts:73-78` (`cacheKey`), `:419-426` (`query`), `:446-453` (`rawQuery`).

The cache key is `sha256(sql) + sha256(JSON.stringify(params))`. Two real concerns:

1. **`JSON.stringify(params)` of the value *array* is fine** — params is `unknown[]` (positional bind values), so ordering is deterministic and this part is sound. (The hypothesis in the brief about "param object key-ordering" does not apply: the cache keys on the positional value array, not on a `QueryParams` object. Verified — `query()` passes `allValues` (array) and `rawQuery` passes `params` (rest array). Not a bug.)

2. **Real issue: data-refresh invalidation is manual and never wired up.** `invalidateQueryCache()` (`:81-83`) exists but **no route or file calls it** (confirmed by grep — only the definition exists). `docs/reference.md:116` claims "Call `invalidateQueryCache()` on data refresh," but nothing does. When the pipeline rewrites the parquets under a running server, every cached query keeps serving pre-refresh rows for up to 60s. The SQL text and bind values are identical before/after a refresh, so the key collides and the stale entry wins until TTL expiry. Low blast-radius (60s) but it *is* stale-data-serving. **Fix recommendation: document** that staleness ceiling is 60s OR wire a filesystem-watch / mtime check on the parquet dir to call `invalidateQueryCache()`. Not fix-now unless refreshes happen against a live server.

### C2. `processedAsDaily` / `dailyTierExpr` dates are NOT in the cache key for `query()` source=`processed` — cross-date-range cache collision `[TECH]`
`src/lib/db.ts:410-419`.

In `query()`, when `source === "processed"`, the FROM expression is `processedAsDaily(params.from, params.to)` which **embeds the month-file list directly in the SQL string** (`read_parquet([...])`). That SQL string *is* hashed into the key, so different date ranges that prune to different month sets produce different keys — **safe**. BUT the `{{FILTER}}` date-range clause uses bind *values* (`params.from`/`params.to` via `buildFilterClause`), which are in the value array — also keyed. So this path is actually correct. **Verified correct after tracing — downgrade from suspected Critical.** Documenting here because it was a brief hypothesis and the reasoning is non-obvious: the date pruning rides in the SQL text and the date filter rides in the values, both hashed. No collision.

(Net: C1's invalidation gap is the only true cache correctness issue. C2 cleared.)

---

## High

### H1. Hardcoded `order_date >= '2025-01-01'` floor in two share-trend routes — confirmed, sidebar dates below 2025 silently dropped `[TECH]`
`src/app/api/carrier-share-trends/route.ts:77`, `src/app/api/dimension-share-trends/route.ts:107`.

Both routes hardcode `WHERE order_date >= '2025-01-01'` in the `base` CTE and **never apply `params.from`/`params.to` at all** — there is no date-range bind from the sidebar on these two routes. Consequences:
- A user who sets the sidebar range to 2024 (or any sub-2025 window) gets 2025-onward data regardless. The chart silently lies about its window.
- The upper bound is also unbounded — the range end (`to`) is ignored, so these always run to the latest data.

This is interpolated as a literal, not user-controllable, so it's not an injection issue — it's a correctness/UX bug. **Fix recommendation: fix-now** if sub-2025 history is in the parquets and reachable elsewhere in the UI (inconsistent windows across tabs is a trust problem). Replace the literal with the standard `order_date BETWEEN ?::DATE AND ?::DATE` bind. If the 2025 floor is an intentional data-availability guard, **document** it in `reference.md` (currently undocumented).

### H2. `avg-costs` and `deviations` (and `benchmarks`) call `dailyTier()` which can return `"processed"`, then read `PARQUET[tier]` as a glob path — but the SQL references pre-aggregated columns that do not exist in processed parquet → query 500s `[TECH]`
`src/app/api/avg-costs/route.ts:15-16` (`tier = dailyTier(params); pqPath = PARQUET[tier]`), `:58-60` (SQL uses `sum_routing`, `sum_real`, `shipments`, `invoiced`).
`src/app/api/deviations/route.ts:18-19` (`tier = dailyTier(params); pqPath = PARQUET[tier]`), `:81-83` (SQL uses `sum_real`, `sum_expected_for_invoiced`, `shipments`).

`dailyTier()` returns `"processed"` when **both** a packagetype filter (`products`) and a SOG filter (`shopOrderGroups`) are active (`db.ts:169`). These two routes then do `PARQUET["processed"]` → `data/processed/*.parquet` and interpolate it as `FROM '<glob>'`. The processed parquet has *raw per-shipment* columns (`shipping_cost`, `cost_for_routing`, `weight_kg`), **not** the pre-agg rollup columns (`sum_routing`, `sum_real`, `shipments`, `invoiced`, `sum_expected_for_invoiced`). The query will error at execution → route returns 500.

Contrast: `overview`, `completeness`, `benchmarks` correctly use `dailyTierExpr()` / pass `tier` to `query()` so the processed tier goes through `processedAsDaily()` (which projects the rollup column names). `avg-costs` and `deviations` skipped that and grab the raw glob.
- `completeness` is the correct pattern (`db.ts` `dailyTierExpr` + `fromSQL` switch at route `:17-19`).
- `benchmarks` passes `tier` into `query(tier, ...)` so `processed` → `processedAsDaily` — **safe**.
- `avg-costs` and `deviations` use `PARQUET[tier]` directly — **broken on the pkg+SOG combination**.

**Fix recommendation: fix-now** — route through `dailyTierExpr()` (like `completeness`) or `query(tier,...)` (like `benchmarks`). Trigger is narrow (need both a packagetype AND a SOG filter simultaneously) which is why it's likely gone unnoticed, but it is a hard crash on a reachable filter combination.

---

## Medium

### M1. `bd_cache` fingerprint excludes `costBasis` and `buckets`, but those don't change cached *rows* — verified safe; the real gap is the fingerprint omits nothing that affects the stored columns `[TECH]`
`src/app/api/breakdown/route.ts:64-103` (`ensureTempTable` + fingerprint), `:113-126` (`CREATE OR REPLACE TEMP TABLE bd_cache`).

The fingerprint is `{filterClauses, filterValues, anyProductDim, dateRange:[wideFrom,wideTo], v:6}`. The temp table stores *all* 11 bucket columns, `order_date`, raw cost columns, and (conditionally) `shop_order_groups`. `costBasis` and `buckets` are applied at *query* time against the cached table (not at table-build time), so excluding them from the fingerprint is correct. `minCost`/`maxCost` **are** in `filterClauses`/`filterValues` (route `:627-634`), so they participate. **Verified the date-independent fingerprint cannot serve stale rows** because every filter that narrows the row set (`countries/providers/products/SOG/sites/shops/order_srcs/minCost/maxCost`) is in `filterClauses`, and the date window stored is a superset (wide range, then queries re-filter `order_date BETWEEN`). The brief's worry ("a filter that DOES affect rows isn't in the fingerprint") does not materialize — all row-affecting filters are present.

One genuine subtlety worth noting (not a bug, a fragility): `anyProductDim` is in the fingerprint, and it controls whether `shop_order_groups` is even *projected* into `bd_cache` (route `:115`). If two requests differ only in dims such that `anyProductDim` flips, the fingerprint changes and the table rebuilds — correct. **Leave / document.**

### M2. `bd_cache` is a module-level mutex + module-level fingerprint shared across ALL concurrent requests/users — wrong-result risk under interleaving `[TECH]`
`src/app/api/breakdown/route.ts:64-65` (`cachedFingerprint`, `tempTableLock` are module globals), `:81-136` (`ensureTempTable`).

`bd_cache` is a single DuckDB temp table on the shared singleton connection (`db.ts:9-37`). Two users with **different sidebar filters** hitting `/api/breakdown` concurrently both target the one `bd_cache`. Sequence: User A's request builds `bd_cache` for filter-set A and resolves `ensureTempTable`; before A runs its level queries, User B's request sees a *different* fingerprint, enters `doCreate()`, and `CREATE OR REPLACE`s `bd_cache` with filter-set B's rows. User A's subsequent `buildLevelQuery` now reads B's data. The mutex (`tempTableLock`) only serializes *creation*, not the create→read critical section, so A's read can interleave after B's recreate. **This is a real cross-request data-correctness hazard under concurrency**, distinct from the cache. It's masked in practice by (a) single-user dev usage, (b) the 60s query cache often short-circuiting, and (c) requests from the same client typically sharing a filter-set. **Fix recommendation: refactor** — either key the temp table name by fingerprint (`bd_cache_<hash>`) so concurrent filter-sets don't collide, or hold the lock across the whole create+read. Severity Medium only because the deployment is effectively single-user; bump to High if this ever serves concurrent users.

### M3. `rawQuery` DDL/`BD_CACHE` cache-bypass uses naive `.toUpperCase()` prefix + substring match — fragile, and a comment/CTE could defeat it `[TECH]`
`src/lib/db.ts:440-444`.

```
const trimmed = sql.trimStart().toUpperCase();
if (trimmed.startsWith("CREATE") || ...startsWith("DELETE") || trimmed.includes("BD_CACHE")) { ... bypass cache ... }
```
- A query that legitimately *should* bypass but starts with a `--` comment or a CTE (`WITH ... AS (...)` that then `SELECT`s from `bd_cache`) would NOT match `startsWith("CREATE")`. The `includes("BD_CACHE")` substring catch saves the `bd_cache` read path (the breakdown level/tooltip queries all contain `bd_cache`/`BD_CACHE` after upcasing) — verified those queries do reference `bd_cache` by name, so they bypass correctly today.
- Risk is a *future* query against `bd_cache` that aliases the table or wraps it such that the literal `BD_CACHE` token disappears (e.g., `FROM (SELECT * FROM bd_cache) x` still contains it — fine; but a view or renamed CTE would not). Also any *unrelated* table named with a `bd_cache` substring would be force-bypassed (none exist today).
- The prefix check ignores leading comments and is case-folded only, not tokenized.

**Fix recommendation: refactor** to an explicit `skipCache` flag on `rawQuery` (the JSDoc at `:430-431` already mentions "Pass `skipCache: true`" but the parameter was never implemented — the signature is `(sql, ...params)` with no opts). The doc and the code disagree; the substring heuristic is the actual mechanism. At minimum, **document** the discrepancy.

### M4. `reference.md` API-route/source table is stale vs. several routes `[TECH]`
`docs/reference.md:43-72` vs. actual route sources.
- `product-trends` (`reference.md:53`): doc says "Source: processed ... UNNEST." Actual (`product-trends/route.ts:38`) reads `PARQUET.daily_product` only, no UNNEST, no processed fallback. **Doc wrong.**
- `carrier-share-trends` (`reference.md:65`): doc lists params "country, provider." Actual route also reads `sogProduct`, `basketSize`, `gran`, and the full sidebar `products`/`countries`/`providers` (route `:24-60`), and has the hardcoded 2025 floor (H1) which the doc omits. **Doc incomplete.**
- `dimension-share-trends` (`reference.md:66`): same hardcoded-2025 omission (H1).
- `deviations` (`reference.md:55`): doc says main table "uses pre-aggregated deviations_summary.parquet"; actually the main table reads the daily/daily_product tier and *joins* `deviations_summary` for the dev-pct columns (route `:75-106`). Partially right, slightly misleading.
- `breakdown` (`reference.md:60`): `costBasis` documented as "(real/real_expected)" — the route now uses "final/invoiced" vocab via `coerceCostBasisParam` (route `:591`), legacy still accepted. Doc uses the old vocab.

**Fix recommendation: document** — reconcile the table. Low urgency, but it's the stated cross-check deliverable.

### M5. `processedPruned` with `from > to` silently falls back to a full-glob scan instead of returning empty / erroring `[TECH]`
`src/lib/db.ts:140-159`.

Month enumeration is correct for the normal cases (verified): inclusive bounds (`m <= tm`), year rollover (`if (m>12){m=1;y++}`), single-month range (from===to → one month). But when `from > to`, the `while` condition is immediately false → `months=[]` → hits the `months.length===0` guard (`:152`) → returns the **full glob** `'.../processed/*.parquet'`. So an inverted range doesn't return zero rows; it scans *everything* (the ~241MB/4.8M-row full set), then the `BETWEEN ?::DATE AND ?::DATE` value filter yields zero rows anyway — correct result, catastrophic scan cost. Most callers guard `from`/`to` ordering (`rate-changes:32-33`, `breakdown buildTotalQuery:375-376`, `cost-drivers-top:117-118` all compute `outerFrom = min, outerTo = max`), so this is mostly unreachable — but `outliers`, `export`, `transit/*` pass `params.from, params.to` straight through with no min/max guard. A malformed client request (`from` after `to`) on those routes triggers a full-table scan. **Fix recommendation: fix-now (cheap)** — add `if (from > to) return read_parquet of zero files` or swap-and-warn at the top of `processedPruned`. Currently the empty-months branch conflates "no months" with "inverted range."

### M6. `generic-trend` full-glob fallback under cost-range filter — confirmed hot path, scans all months `[TECH]`
`src/app/api/generic-trend/route.ts:44-45`.
```
const useProcessed = hasCostRange || hasProcessedOnly;
const pqPath = useProcessed ? processedPruned("2024-01-01","2099-12-31") : (...daily...);
```
Confirmed: when `minCost`/`maxCost` (or a processed-only dim) is set, it calls `processedPruned("2024-01-01","2099-12-31")` — i.e., **explicitly the full month range**, which enumerates every month from Jan-2024 to Dec-2099, `existsSync`-filters to the real files, and reads them all. The route's own `where` clause *does* still bind `order_date BETWEEN` if `params.from`/`to` are set via `buildFilterClause`? — **No**: this route builds its WHERE manually (`:52-97`) and **never adds an `order_date` range clause at all** (it only adds `cost_for_routing >=/<=`, dimension filters). So under a cost-range filter with a wide chart, this reads the entire processed history every call, cache-permitting. **Fix recommendation: refactor** — pass the actual chart window (`tsFrom`/`tsTo` or `params.from`/`to`) into `processedPruned` instead of the 2024–2099 sentinel, and add an `order_date` bind so the scan is bounded. This matches the brief's flagged hot path.

---

## Low

### L1. `outliers` global-scope threshold join can mismatch when date filters exclude a provider — `__NOMATCH__` sentinel not used here; behavior is correct but worth noting `[TECH]`
`src/app/api/outliers/route.ts:56-75`. Global scope joins `outlier_thresholds` on `shippingprovider`; providers absent from the precomputed thresholds parquet silently drop from results (INNER JOIN). Acceptable (a provider with no all-time p99.5 has no outliers by definition), but undocumented. **Leave.**

### L2. `__NOMATCH__` sentinel — searched, not present in serving layer `[TECH]`
Grep for `__NOMATCH__` across the route tree returned nothing in scope. The brief listed it as a thing to check; it does not exist in db.ts or any route. The empty-filter "all" semantics are handled by `.filter(Boolean)` on split params (empty array ⇒ clause omitted ⇒ "all"), which is **consistent across all 35 routes** (verified). No sentinel needed. **N/A.**

### L3. Inconsistent `tsFrom`/`tsTo` vs `from`/`to` window semantics across chart routes `[TECH]`
`breakdown-buckets:31-32`, `breakdown-quota:21-22`, `breakdown-sparklines:52-53`, `transit/trend:18-19` use `tsFrom ?? params.from`. Others (`generic-trend`, `country-trends`, `trends`, `product-trends`) ignore `ts*` entirely and either bind `from/to` or apply no date bound. Not a bug, but the chart-window contract differs route to route. **Document.**

### L4. `error` responses leak raw `${err}` to the client `[TECH]`
Every route's catch returns `` `... query failed: ${err}` `` (e.g., `db.ts` callers, all routes). DuckDB error strings can include SQL fragments and file paths. Low risk on an internal dashboard; **document / leave**. Not a 500-vs-`[]` problem — errors do 500 (good), missing-parquet on the alerts movers path is swallowed to `[]` deliberately (`overview:363` `catch {}`), which is the right call for an optional panel.

### L5. `meta` and `changelog`/`dismissed` use direct `fs` + their own caches, bypass the query cache entirely `[TECH]`
`meta/route.ts:6-16` (mtime-keyed JSON cache — sound), `changelog`/`alerts/dismissed` (read-through `fs`, write-through + fire-and-forget S3 via `execFile aws`). No DuckDB. The `execFile("aws", ...)` is argument-array form (not shell) so no command-injection. **Verified correct.**

---

## Verified correct (mechanisms checked and sound)

- **SQL injection: clean across all 35 routes.** Every country/provider/packagetype/SOG/SKU/site/shop/order-source value is bound via `?` placeholders (`buildFilterClause` in db.ts and the per-route inline equivalents). The only interpolated tokens are: (a) column names from server-side whitelists (`DIM_COL`, `allowedCols` in shifts routes, `ALL_BUCKETS`, tier names), (b) the `gran`→`trunc` ternary (always one of `day`/`week`/`month`), (c) `LIMIT ${periods}` / `LIMIT ${MIN_MONTH_SHIPMENTS}` which are `Number(...)`-coerced and clamped (`avg-costs:14`, `completeness:14`, `cost-drivers-top:97`), (d) the parquet path (server-derived). No user string reaches SQL text unescaped. `shareBy`/`dims`/`buckets`/`costBasis` are all validated against enums before use.
- **`processedPruned` month enumeration** — inclusive bounds, year rollover, single-month, and `existsSync` filtering all correct for `from <= to` (only the inverted-range fallback is suboptimal, M5).
- **Query cache TTL + LRU eviction** (`db.ts:85-109`) — get-time expiry check, size-cap eviction of oldest by timestamp, 5-min unref'd sweeper. Correct.
- **Connection singleton + cold-start mutex** (`db.ts:16-37`) — `connLock` promise prevents duplicate `Database.create`; persistent `Connection` so temp tables survive. The `finally { connLock = null }` is fine (lock only guards creation). Sound for the single-process Next.js model.
- **`bd_cache` HMR lost-table retry** (`breakdown:688-699`, `:729-746`) — catches `bd_cache ... does not exist`, clears fingerprint, rebuilds, retries once. Correct.
- **`dailyTier` selection logic** (`db.ts:165-172`) — pkg+SOG→processed, SOG-only→daily_product, else daily. Logic itself is right; the *consumption* of `processed` is where two routes break (H2).
- **`overview`, `completeness`, `benchmarks`** processed-tier handling via `query(tier,...)`/`dailyTierExpr` — correct pattern.
- **`computeShifts`** (shifts.ts) — parameter ordering across the 8 CTE bind sites traced and matches the assembled `allValues` array; provider deliberately post-filtered so corridor shares stay whole; whitelisted sort columns. Sound.

---

## Per-route coverage (all 35 scanned)

1. `alerts` — issues.parquet, params bound, scoring in TS. OK.
2. `alerts/detail` — alerts.parquet, all filters bound. OK.
3. `alerts/dismissed` — fs JSON, no DuckDB, execFile array-form. OK (L5).
4. `avg-costs` — **H2 (processed-tier crash on pkg+SOG)**; LIMIT clamped.
5. `benchmarks` — query(tier), processed-safe. OK.
6. `breakdown` — bd_cache; **M2 (concurrency), M1 (fingerprint verified safe)**.
7. `breakdown-buckets` — daily/daily_product, bound; tsFrom/tsTo. OK (L3).
8. `breakdown-quota` — daily/daily_product, bound. OK (L3).
9. `breakdown-sparklines` — processedPruned (12mo), bound, MIN clamp literal-but-constant. OK.
10. `carrier-share-trends` — **H1 (hardcoded 2025 floor, no date bind)**.
11. `carrier-shifts` — computeShifts. OK.
12. `changelog` — fs JSON + S3 execFile array. OK (L5).
13. `completeness` — dailyTierExpr (correct processed handling). OK.
14. `country-trends` — daily tier, bound, share JSON via STRING_AGG. OK.
15. `cost-drivers-top` — 4× computeShifts + fetchRateChanges, min/max guarded. OK.
16. `deviations` — **H2 (processed-tier crash on pkg+SOG via PARQUET[tier])**; trend uses processedPruned (guarded). 
17. `dimension-share-trends` — **H1 (hardcoded 2025 floor, no date bind)**.
18. `export` — processedPruned(dateFrom,dateTo), all bound, CSV. OK.
19. `filter-options` — fc_mem in-mem table, cross-filter bound, dynamic col-existence guard. OK.
20. `generic-trend` — **M6 (full-glob 2024–2099 under cost-range, no order_date bind)**.
21. `layer2` — computeShifts(routing), whitelisted sort. OK.
22. `meta` — fs JSON mtime cache. OK (L5).
23. `outliers` — processedPruned(from,to) unguarded (M5 surface); thresholds join (L1). OK otherwise.
24. `overview` — query(tier), movers from alerts (swallowed catch). OK.
25. `packagetype-trends` — daily tier, bound. OK.
26. `product-shifts` — computeShifts(product), whitelisted sort. OK.
27. `product-trends` — daily_product (doc says processed — M4). OK functionally.
28. `rate-changes` — processedPruned(min,max-guarded), bound, whitelisted via fixed SQL. OK.
29. `trend-shares` — daily/daily_product/processedAsDaily, bound. OK.
30. `trends` — daily tier, bound, country-share attach. OK.
31. `transit/heatmap` — processedPruned(from,to) unguarded (M5), bound. OK.
32. `transit/histogram` — processedPruned unguarded (M5), bound, TAIL literal. OK.
33. `transit/kpis` — processedPruned unguarded (M5), bound, CURRENT_DATE. OK.
34. `transit/completeness` — processedPruned unguarded (M5), bound. OK.
35. `transit/trend` — processedPruned(tsFrom/tsTo), bound. OK.

(Plus `src/lib/db.ts` and `src/lib/shifts.ts` — the shared engine — read in full.)
