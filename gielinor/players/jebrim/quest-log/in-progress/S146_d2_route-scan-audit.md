# [[S146_f20d7744_scm-serving-memory-review|S146]] D2 — SCM serving-node route scan audit

**Player:** Jebrim · **Role:** read-only review dwarf · **Date:** 2026-06-02
**App:** `shipping_costs_monitoring_nextjs` (Next.js, in-process DuckDB over parquet, 512MB Node heap, OOM/502 symptom).
**Scope:** every `src/app/api/**/route.ts` (35 routes enumerated). Read-only — no app files edited.

## Verdict in one line

**11 routes can issue a full-history processed scan** (full `processed/*.parquet` glob, ~241MB) on the serving node — 4 of them **silently and with no date filter at all** (the worst class), the rest only when `from`/`to` are absent (a missing-guard hazard). On top of that, `breakdown` materializes per-shipment columns into a shared-connection TEMP TABLE, and `outliers`/`export` return unbounded per-shipment result sets. These are the memory/CPU drivers behind the OOMs.

## How a "full scan" happens (mechanics from `src/lib/db.ts`)

- `processedPruned(from,to)` (db.ts:140) returns `'<dir>/*.parquet'` (the FULL glob) when `from` **or** `to` is falsy (db.ts:142). Otherwise it month-prunes to overlapping files.
- `processedAsDaily(from,to)` (db.ts:183) wraps `processedPruned` in a per-shipment GROUP-BY aggregation. Called with **no args** → full glob, full-history aggregation in the request path.
- `dailyTier(params)` (db.ts:171) returns `"processed"` when **both** `products` (packagetype) **and** `shopOrderGroups` are active. `PARQUET[tier]` then resolves to `PARQUET.processed` = the full glob string. `dailyTierExpr` (db.ts:217) routes the processed tier through `processedAsDaily(params.from,params.to)`.
- `query()`/`rawQuery()` cache by 500-entry count, not bytes (db.ts:61-63,97) — a few big per-shipment result sets can dominate heap regardless of the entry cap.
- Single shared `Connection` (db.ts:10) — TEMP TABLEs (`bd_cache`) live on it and are visible/contended across all concurrent requests.

## Route scan-risk table (all 35)

Tier legend: **PRE-AGG** = daily/daily_product only (light) · **PRUNED** = processed but month-pruned by present dates · **FULL-GLOB?** = can scan whole processed history · **FILE** = JSON/meta file, no DuckDB · **SMALL-PARQUET** = pre-aggregated alerts/issues/filter_combos.

| Route | Source tier | Full-history scan possible? | Notes |
|---|---|---|---|
| `avg-costs` | processed via `processedAsDaily()` **no args** | **YES — always, by design** (line 20) | comment says "full history … intentionally". CRITICAL. |
| `trends` | `PARQUET[dailyTier]` | **YES — silent, no date filter** | processed tier + no `order_date` WHERE → full glob. Also `attachCountryShares` re-scans. |
| `country-trends` | `PARQUET[dailyTier]` | **YES — silent, no date filter** | same pattern; two scans (base + shares CTE). |
| `packagetype-trends` | `PARQUET[dailyTier]` | **YES — silent, no date filter** | same pattern. |
| `completeness` | `dailyTierExpr` | **YES — no range filter, recency-only** | period_list + latestComplete both scan with only `order_date <= to`; processed tier = full glob. |
| `trend-shares` | `processedAsDaily(from,to)` when site/shop/order_src active | YES if from/to empty | pruned when dates present. |
| `generic-trend` | `processedPruned(from,to)` when cost-range/processed-only filters | YES if from/to empty | D3-M6 fix bounds it when dates present. |
| `breakdown` | `processedPruned(wide range)` + TEMP TABLE | YES if no dates (falls to `["2024-01-01","2099-12-31"]`) | see Critical findings — also temp-table + per-shipment materialize. |
| `outliers` | `processedPruned(from,to)` | YES if from/to empty | per-shipment result set, no LIMIT. |
| `deviations` | `dailyTierExpr` (main) + `processedPruned` (trend) | YES if from/to empty (main, processed tier) | trend leg 12-mo capped + pruned. |
| `breakdown-sparklines` | `processedPruned(pruneFrom,endDate)` | partial — endDate falls back to "2099-12-31" | pruneFrom = end−11mo, so bounded to a 12-mo window even w/o dates (low risk). |
| `shifts` (carrier-shifts, layer2, product-shifts, cost-drivers-top) | `cfg.fromExpr` = daily/daily_product, OR `processedAsDaily(from,to)` when site/shop/order_src active | YES if from/to empty AND processed-only filter active | `fromExpr` referenced **4×** per request (tagged/baseline_weeks/baseline_period_count/baseline_weekly_vol) → 4 full scans. |
| `export` | `processedPruned(dateFrom,dateTo)` | NO (400s on missing dates, line 73) | but unbounded per-shipment CSV — see High findings. |
| `rate-changes` | `processedPruned(outer range)` | NO (400s on missing dates, line 28) | well-guarded. |
| `cost-drivers-top` | `processedPruned` + shifts | NO (returns empty on missing dates, line 16) | well-guarded. |
| `transit/kpis` | `processedPruned(from,to)` | YES if from/to empty | aggregates (bounded result). |
| `transit/heatmap` | `processedPruned(from,to)` | YES if from/to empty | aggregates. |
| `transit/histogram` | `processedPruned(from,to)` | YES if from/to empty | aggregates. |
| `transit/trend` | `processedPruned(tsFrom||from, tsTo||to)` | YES if all empty | aggregates. |
| `transit/completeness` | `processedPruned(from,to)` | YES if from/to empty | aggregates. |
| `carrier-share-trends` | daily/daily_product | NO | PRE-AGG, date-filtered. |
| `dimension-share-trends` | daily/daily_product | NO | PRE-AGG, date-filtered. |
| `breakdown-buckets` | daily/daily_product (tier coerced) | NO | `needsProduct` forces daily_product; processed unreachable. |
| `breakdown-quota` | daily/daily_product (tier coerced) | NO | same coercion. |
| `product-trends` | `PARQUET.daily_product` (hardcoded) | NO | PRE-AGG. |
| `benchmarks` | `query()` processed tier → `processedAsDaily(from,to)` | YES if from/to empty | pruned when dates present; `{{FILTER}}` binds range. |
| `overview` | `query()` processed tier → `processedAsDaily(from,to)` | YES if from/to empty | pruned when dates present. |
| `alerts` | `PARQUET.issues` | NO | SMALL-PARQUET. |
| `alerts/detail` | `PARQUET.alerts` | NO | SMALL-PARQUET. |
| `alerts/dismissed` | JSON file | NO | FILE (POST + `execFile aws`). |
| `changelog` | JSON file | NO | FILE (POST + `execFile aws`). |
| `filter-options` | `FC_TABLE` (in-memory) | NO | small. |
| `meta` | `meta.json` | NO | FILE, cached. |

**Count that can do a full-history processed scan: 11** routes (`avg-costs`, `trends`, `country-trends`, `packagetype-trends`, `completeness`, plus `trend-shares`, `generic-trend`, `breakdown`, `outliers`, `deviations`, the `shifts` family, and the 5 `transit/*`, `overview`, `benchmarks` — all gated on missing dates). Counting **distinct route files** the missing-date class adds many more; the **always/silent** class is the 5 named first.

## Severity-tagged findings (worst offenders)

### CRITICAL

**C1 — `avg-costs/route.ts:20` — unconditional full-history scan.**
`const fromExpr = tier === "processed" ? processedAsDaily() : ...` — `processedAsDaily()` with **no args** → full `processed/*.parquet` glob, full-history per-shipment aggregation, every request where packagetype+SOG are both active. The code comment explicitly chooses this ("Full history … so no date pruning here") because the heatmap window is computed from `to`. **Cost:** a 241MB scan + GROUP BY materialized in a 512MB heap = OOM under any concurrency. **Fix:** prune to the actual period window — pass `processedAsDaily(windowStart, params.to)` where `windowStart` = `to − periods*gran`; the `period_list` CTE already computes that window, so derive its lower bound and feed it to the prune. Reject empty `to` with 400. **Effort: M.**

**C2 — `trends` / `country-trends` / `packagetype-trends` — silent full glob via `PARQUET[dailyTier]` with no date filter.**
These build `'${pqPath}'` from `PARQUET[tier]`; when `dailyTier()` returns `"processed"` (packagetype + SOG both selected) `pqPath` = the full glob, and **none of these routes apply any `order_date` filter** (they filter only by dimension). Result: full-history per-shipment scan, often twice (main agg + a shares CTE that re-scans). `trends/route.ts:98,152`; `country-trends/route.ts:32,85`; `packagetype-trends/route.ts:48,87`. **Cost:** same 241MB scan, silent (no comment, looks like a daily-tier query). **Fix:** when `tier === "processed"`, route through `dailyTierExpr(params)` (pruned subquery) **and** push `order_date BETWEEN from AND to` into the WHERE; or block the processed tier for these endpoints and require the client to narrow. **Effort: M.**

**C3 — `completeness/route.ts:62-104` — processed-tier scan with recency-only (no range) filter, run twice.**
`fromSQL` can be the processed-tier subquery; the `period_list` CTE and the `latestComplete` query both scan with only `order_date <= to` (or `9999-12-31` when `to` empty) — i.e. **all history up to `to`**, no lower bound, no month-prune of the *query* (only `processedAsDaily`'s file-prune, which itself is full-glob when dates are absent). Two full scans per request. **Fix:** bound the lower edge to `to − periods*gran`; require `to`. **Effort: M.**

**C4 — `breakdown/route.ts` — per-shipment TEMP TABLE on the shared connection + unbounded date fallback.**
`ensureTempTable` (line 81) does `CREATE OR REPLACE TEMP TABLE bd_cache AS SELECT <~20 per-shipment cols incl. all 11 bucket cols> FROM processedPruned(wideFrom,wideTo) WHERE cost_for_routing IS NOT NULL` (lines 113-124). Three compounding hazards:
  1. **No-date fallback:** `wideDateRange` returns `["2024-01-01","2099-12-31"]` when no dates (line 71) → `processedPruned` full glob → the temp table materializes ~full-history per-shipment rows **into memory** on the shared `:memory:` DB.
  2. **Shared-connection temp table:** `bd_cache` lives on the one shared `Connection`; concurrent breakdown requests with different filters race on `CREATE OR REPLACE` (mutex `tempTableLock` serializes creation but a second filter-set still blows away the first user's cache → re-scan thrash, and the table's bytes sit on the shared DB for all sessions).
  3. **Wide window margin:** even with dates, `wideDateRange` pads −3mo/+1mo and covers baseline+main, so the materialized set is larger than the visible range.
**Cost:** the single biggest sustained heap consumer — a per-shipment table held resident on the in-memory DB. **Fix:** (a) require dates / reject the 2099 sentinel; (b) push the date range into the temp-table WHERE so it never materializes more than the wide window; (c) strongly consider dropping the temp table for a CTE/pruned-glob per request, or moving `bd_cache` off the shared connection (per-request connection or DuckDB `TEMP` scoped to a fresh conn) so concurrent users don't contend. **Effort: L.**

### HIGH

**H1 — `outliers/route.ts:16,69,114` — full glob on missing dates + unbounded per-shipment result.**
`processedPruned(params.from, params.to)` → full glob when dates absent. The query returns **individual shipment rows** (top-0.5% by p99.5) with **no LIMIT** — on a wide range that's a large materialized JSON array buffered in the response. **Fix:** require from/to (400); add a hard `LIMIT` (e.g. 5000) with a "truncated" flag. **Effort: S.**

**H2 — `export/route.ts:134` — unbounded per-shipment CSV in memory.**
Dates are required (good, line 73) and the glob is pruned, but `SELECT <13 cols> FROM processedPruned(...) ... ORDER BY ...` returns **every matching shipment** with no cap, fully materialized by `rawQuery` (BigInt-converted, cached!) then `rowsToCsv` builds the whole string in memory. A multi-month export = hundreds of MB of JS strings on a 512MB heap. Note it **also gets cached** in the 500-entry query cache (rawQuery doesn't skip cache for this SELECT), so a big export lingers. **Fix:** stream the response (DuckDB → chunked CSV via a ReadableStream), bypass the query cache for export (it's single-use), and/or cap rows with a "narrow your range" 413. **Effort: M.**

**H3 — `shifts.ts` — 4× full scan per request when a processed-only filter is active and dates are empty.**
`computeShifts` references `cfg.fromExpr` in four CTEs (tagged:152, baseline_weeks:240, baseline_period_count:281, baseline_weekly_vol:291). When `productionSites`/`shops`/`orderSources` are active, `fromExpr = processedAsDaily(from,to)` → full glob if dates empty → **four** full-history aggregations in one request. Hits `carrier-shifts`, `layer2`, `product-shifts`, `cost-drivers-top` (the last guards dates at the route, so safe; the other three do not require dates). **Fix:** require from/to in `carrier-shifts`/`layer2`/`product-shifts` (or make `computeShifts` reject empty bounds); ideally compute the processed aggregation once into a CTE and reference it 4× instead of re-emitting the subquery. **Effort: M.**

### MEDIUM

**M1 — transit/* (5 routes) — full glob on missing dates.**
`transit/kpis`, `heatmap`, `histogram`, `trend`, `completeness` all `processedPruned(params.from, params.to)` with no date guard → full glob if from/to empty. Results are aggregated (bounded output) so the hazard is the **scan**, not the result. **Fix:** require from/to (400) on all five; they're per-shipment scans of the heaviest tier and the dashboard's transit tab is exactly where wide ranges get selected. **Effort: S** (one guard each).

**M2 — `overview`/`benchmarks`/`trend-shares`/`generic-trend`/`deviations` — full glob on missing dates (processed tier).**
Each prunes correctly when from/to are present but falls back to full glob when absent (or when packagetype+SOG force the processed tier with empty dates). Lower likelihood than C-class (the UI usually sends a range) but no server-side guarantee. **Fix:** a shared guard — reject empty from/to with 400 before any processed-tier query, or make `processedPruned`/`processedAsDaily` throw instead of silently full-globbing (turn the silent fallback into a loud failure). **Effort: S** if centralized in db.ts.

**M3 — query cache is count-bounded, not byte-bounded (`db.ts:61-63,97-108`).**
`MAX_CACHE_ENTRIES = 500` by entry count. A handful of large entries (export CSV rows, outlier per-shipment arrays, big breakdown result sets) can pin tens/hundreds of MB while well under 500 entries. **Fix:** cap by approximate byte size (sum of JSON length) and/or skip caching results above a row/byte threshold; definitely skip caching `export` and `outliers`. **Effort: M.**

### LOW

**L1 — no `export const runtime/dynamic/maxDuration` on any route.**
None of the 35 routes set runtime/streaming hints. The big-payload routes (`export`, `outliers`) buffer the entire body before responding — candidates for `runtime`/streaming once H2/H1 are addressed. Not a direct OOM cause but compounds it. **Effort: S** per route, but only meaningful alongside streaming work.

**L2 — `changelog`/`alerts/dismissed` POST run `execFile("aws", …)` per write.**
Out of the memory-scan scope, but flagging: each write spawns an aws CLI child process (fire-and-forget). Not a heap driver; noted for completeness. **Effort: n/a (out of scope).**

## Highest-leverage fixes (order)

1. **C1 + C4** — kill the always-on full scan in `avg-costs` and bound/relocate `breakdown`'s per-shipment temp table. These two are the most likely sustained-OOM drivers.
2. **C2 + C3** — the silent processed-tier full scans in `trends`/`country-trends`/`packagetype-trends`/`completeness` (no date filter at all is the trap).
3. **M2 centralized guard** — make `processedPruned`/`processedAsDaily` **throw** on missing bounds instead of silently returning the full glob. One change in db.ts converts every M1/M2 latent hazard into a loud 500 you can see in logs, and surfaces any caller that was relying on the full scan (only `avg-costs` intentionally was).
4. **H1/H2** — cap/stream the unbounded per-shipment result sets and stop caching them.
