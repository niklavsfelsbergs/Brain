# S026 D2 — API routes & DuckDB data layer

Read-only deep-read of the Next.js backend for `shipping_costs_monitoring_nextjs` on branch `shipping-mart-cutover`. Scope was: `src/lib/db.ts`, `src/lib/types.ts`, `src/lib/format.ts`, `src/lib/colors.ts`, and every `src/app/api/*/route.ts` (35 routes, all read). Diff vs `main` covers 18 files (+1297, -72) — see `Mart cutover delta` below.

App root: `C:/Users/niklavs.felsbergs/Documents/GitHub/bi-analytics/NFE/dashboards/shipping_costs_monitoring_nextjs/`

## DuckDB data layer (src/lib/db.ts)

### Connection singleton + first-connect priming

- `getConn()` returns a **persistent `Connection`** (not one-shot `Database.all`) so temp tables survive across requests. (`db.ts:16-37`)
- Connection construction is mutex-guarded by `connLock` so concurrent cold-start callers do not double-create the in-memory DB.
- On first connect, `fc_mem` is pre-loaded from `filter_combos.parquet` (~404 KB) into an in-memory table so `filter-options` queries never re-touch the file. Constant `FC_TABLE = "fc_mem"`. (`db.ts:14`, `db.ts:28`)
- `getFcColumns()` caches the column set of `fc_mem` in a module-level `Set<string>` so `filter-options` can branch on optional cols (`production_site`, `shop`, `order_source`) without `information_schema` lookups. (`db.ts:45-52`)

### Parquet registry

- `PARQUET` (`db.ts:119-128`) is the single source of truth for paths under `DATA_DIR` (env override, default `./data`).
- Keys: `daily`, `daily_product`, `processed` (glob), `filter_combos`, `alerts`, `issues`, `deviations_summary`, `outlier_thresholds`.
- `processedPath()` exposes the glob form `${DATA_DIR}/processed/*.parquet`.

### Template engine — `{{PARQUET}}` and `{{FILTER}}`

`query<T>(source, sql, params, opts)` in `db.ts:389-427`:

- `{{PARQUET}}` is substituted with either `'<file path>'` for `daily`/`daily_product`, or with the `processedAsDaily(from, to)` aggregation subquery for `source === "processed"`.
- `{{FILTER}}` is substituted with the `WHERE …` fragment built by `buildFilterClause` (`db.ts:292-370`), which composes: date-range (optional), `countries`, `providers`, `products` (packagetype), `skus` (ILIKE `basket_sku`), `shopOrderGroups` (either exact `product` or ILIKE `shop_order_groups`), `productionSites`, `shops`, `orderSources`, optional `trend_confirmed = true`.
- `opts` lets each caller override column names (e.g., `productCol: "product"` for tier 1b, `sogMode: "product"` for pre-exploded SOGs, `dateCol`, `includeConfirmed`, `includeDateRange`).
- `extraValues` is appended to the parameter list after the dimension values, so callers using `?` placeholders outside the canonical filter (CTE-level date binds, etc.) bind cleanly.

### Query cache (60 s, SHA-256 keyed)

- Module-level `Map<string, CacheEntry>` (`db.ts:61`).
- Key = `sha256(finalSql) + sha256(JSON.stringify(params))` (`cacheKey`, `db.ts:73-78`).
- TTL = 60 s. Capacity = 500 entries; LRU-by-timestamp eviction (linear scan; fine at this scale).
- Sweeper runs every 5 min via `setInterval(...).unref()` (won't block process exit).
- `invalidateQueryCache()` clears it (intended for data-refresh hook; not currently invoked).

### `rawQuery` and the DDL bypass

`rawQuery<T>(sql, ...params)` in `db.ts:431-454`:

- No source/filter replacement.
- **Cache bypass rule**: if the trimmed-upper SQL starts with `CREATE`/`DROP`/`INSERT`/`DELETE` *or* contains `BD_CACHE`, the cache is skipped entirely (both read and write). This is critical because `bd_cache`'s **contents** depend on filters not in the SQL text — same SQL+params can return different rows after the temp table is recreated for a different filter fingerprint.

### `processedPruned(from, to)` — month-pruned read trick

`db.ts:140-159`:

1. If either bound is missing → fall back to `'…/processed/*.parquet'` (full glob).
2. Otherwise enumerate `YYYY-MM` strings between `from` and `to` inclusive (calendar arithmetic on integer year/month, not Date math).
3. `fs.existsSync` filters to months that exist on disk (avoids DuckDB error for future months).
4. Returns `read_parquet(['…/2025-03.parquet', '…/2025-04.parquet', …])` — DuckDB reads only those files instead of the full glob (~241 MB worth in current data).
5. Empty intersection → fall back to full glob.

This is the workhorse for every route hitting `processed`. The processed tree is partitioned to one monthly parquet per file; the function exploits that partitioning at SQL build time.

Related: `processedAsDaily(from, to)` (`db.ts:177-205`) wraps `processedPruned` in an aggregation subquery whose SELECT list matches the Tier 1 (`daily`) schema — used as the "tier 1 fallback when both packagetype and SOG filters are active." `dailyTier(params)` (`db.ts:165-172`) picks `daily` / `daily_product` / `processed` based on which dimensions are filtered:

- both packagetype + SOG → `processed` (only tier with both dims)
- SOG only → `daily_product` (SOGs pre-exploded into a `product` col)
- otherwise → `daily`

`dailyTierExpr(params)` returns the FROM fragment (quoted path or aggregation subquery) for whichever tier `dailyTier` picked.

### `bd_cache` temp table + mutex pattern (breakdown only)

The Breakdown tab is the only consumer. Lives in `src/app/api/breakdown/route.ts:58-135`, *not* in `db.ts`. Mechanics:

- **Fingerprint** (`cachedFingerprint`) is `JSON.stringify({ filterClauses, filterValues, anyProductDim, dateRange: [wideFrom, wideTo], v: 6 })`. Date range is intentionally *wide* (`wideDateRange`, `route.ts:68-78`: earliest input minus 3 months, latest plus 1 month) so small date-picker shifts don't trigger re-creation.
- **Mutex** (`tempTableLock: Promise<void> | null`) prevents racing CREATE TEMP TABLE calls during cold start / HMR. A waiting caller awaits the in-flight `tempTableLock` *before* checking the fingerprint.
- **Existence probe**: when the fingerprint matches, a `SELECT 1 FROM bd_cache LIMIT 0` confirms the table is still there. On failure (HMR recreated the in-memory DB), the fingerprint is cleared and creation runs again.
- **Schema**: `bd_cache` materializes `destination_country, shippingprovider, packagetype, [shop_order_groups if anyProductDim], order_date, cost_for_routing, shipping_cost, expected_shipping_cost, weight_kg, revenue, <all 11 bkt_* cols>, has_cost, has_expected`. Reading from this is ~free vs scanning the 241 MB processed parquet on each filter/date toggle.
- **Bucket-aware**: all 11 bucket columns are always materialized so the client-side bucket filter only changes the cost expression (`bucketSumExpr`) without invalidating the temp table.
- **Lost-table retry**: every breakdown query has a `String(e).includes("bd_cache") && String(e).includes("does not exist")` catch that resets the fingerprint and rebuilds once.

The temp table is invisible to the cache (because `BD_CACHE` triggers the DDL bypass).

### Other db.ts utilities

- `parseFilters(req)` (`db.ts:251-267`) is the canonical querystring → `QueryParams` parser. Maps short URL keys (`sites`, `order_srcs`, `bfrom`, `bto`) to internal field names. `confirmedOnly` is `string === "true"`.
- `dateRangeClause` / `baselineClause` — small builders the few routes that need a bare date range (no dim filter).
- `convertBigInts` (`db.ts:373-384`) recursively converts every BigInt to Number on result rows; DuckDB returns counts as BigInt and JSON.stringify chokes otherwise.
- `CACHE_HEADER = { "Cache-Control": "private, max-age=30" }` (`db.ts:40`) — every data route returns this.

## Types (src/lib/types.ts)

### Filters contract

`Filters` (`types.ts:42-77`) is the UI-side state — adds search strings, `hideLowVol`, `activeTab`, alert/UI state. `QueryParams` (lives in db.ts) is the API-side projection of just the filtering bits.

URL alias mapping at the parse boundary (`parseFilters`):

| URL key | QueryParams field |
|---|---|
| `countries`, `providers`, `products`, `skus`, `shopOrderGroups` | same |
| `sites` | `productionSites` |
| `order_srcs` | `orderSources` |
| `confirmedOnly` ("true") | `confirmedOnly` |
| `from`, `to`, `bfrom`, `bto` | `from`, `to`, `baselineFrom`, `baselineTo` |

### Tabs

`TabKey` (`types.ts:116`) is the 11-tab union. `REF_TAB_ALIASES` (`types.ts:119-127`) maps legacy pipeline values:

- `corridor-costs`, `countries`, `avg-costs` → `breakdown` (the post-cutover unified tab)
- `carrier-shifts`, `shifts`, `product-shifts` → `cost-drivers`

`resolveRefTab(raw)` is the helper alerts use to route navigation to the correct surviving tab.

`TABS: TabDef[]` (`types.ts:278-494`) is the on-page documentation surface — `key`, `label`, `summary`, `steps[]` (each `{label, formula}`), optional `footnote`. Used by the inline tab-doc panel.

`TAB_SCOPE` (`types.ts:499-511`) zeros out filter arrays not relevant to a tab before querying (e.g., `outliers` strips `products`, `skus`, `shopOrderGroups`). `TAB_FILTERS` (`types.ts:516-528`) controls which sidebar sections are *visible* per tab.

### Buckets

`BucketKey` (`types.ts:8-19`) — 11 cost-composition columns: `bkt_base_rate`, `bkt_truck_charges`, `bkt_fuel_surcharge`, `bkt_remote_area`, `bkt_peak_demand`, `bkt_oversize_overweight`, `bkt_residential`, `bkt_other`, `bkt_unclassified`, `bkt_discounts`, `bkt_credit_note`. `ALL_BUCKETS` is the canonical UI order; `REDUCER_BUCKETS = [discounts, credit_note]` (subtract from total).

### Row shapes (load-bearing)

Quick index of what each tab's API returns:

- `BreakdownRow` (`types.ts:136-169`) — per-cell breakdown row; includes raw bucket columns alongside aggregates.
- `CostDriverSummary` / `RateChangeRow` / `TopDriverItem` (`types.ts:175-214`).
- `AlertRow` (`types.ts:219-236`) — raw per-alert. `IssueRow` (`types.ts:238-268`) — the issue/incident from `issues.parquet`.
- `CarrierShiftRow` / `ShiftRow` / `ProductShiftRow` (`types.ts:1059-1118`) — all share the `from_providers` JSON attribution field.
- `TransitHeatmapCell` / `TransitKPIs` / `TransitCompletenessRow` / `TransitTrendPoint` (`types.ts:1309-1372`).
- `OverviewRow` / `OverviewKPIs` / `OverviewSummary` / `TopMover` (`types.ts:956-1030`).
- `AvgCostCell` (`types.ts:1374-1384`).

### Date and period machinery

`types.ts:578-940` packs in: `DATE_PRESETS`, `BASELINE_PRESETS`, `computeDefaultDates(maxDate)`, `computeShiftTsDefaults`, `chartRangeFrom`, `computeAlertDates(periodMonday)`, plus the **cascading period picker** (`getYearRange`, `getQuarterRange`, `getMonthRange`, `getWeeksInMonth`, the multi-X `*RangeSpan` helpers, and `inferPeriodSelection` which reverse-engineers picker state from raw `from/to` dates).

These are pure helpers — no DB access. They live in types.ts because the same code is used by client-side React state and server-side request shaping.

## Format & colors

- `src/lib/format.ts` — `fmtEur`, `fmtEurUnit`, `fmtPct`, `fmtShare`, `fmtNum`, `fmtCompact` (1.5K / 1.01M), `fmtDate`. All null-safe ("-" on null). Compact format thresholds documented at `format.ts:43-44`.
- `src/lib/colors.ts` — dark-theme palette, `impactColor(value)` (red gradient for positive impact, green for negative — *cost increase is rose, savings is mint*), `coverageColor`, `avgCostColor` (continuous teal→yellow→red), `divergingColor` (green↔red around zero), 8-entry `CHART_COLORS` for series. **`BUCKET_COLORS`** (`colors.ts:96-112`) is the canonical per-bucket pastel palette grouped by category (operational / surcharge / other / reducer).

## API routes inventory

35 routes. Source parquet column shows the *primary* read; many also touch `bd_cache` or a secondary file noted in Notes.

### Meta / filters / config

| Route | Source | Params | Returns | Notes |
|---|---|---|---|---|
| `GET /api/meta` | `data/meta.json` (file, not parquet) | none | `MetaResponse` (countries/providers/.../date_bounds) | mtime-keyed in-memory cache; `Cache-Control: max-age=60` |
| `GET /api/filter-options` | `fc_mem` (in-memory from `filter_combos.parquet`) | `countries, providers, products, shopOrderGroups, sites, shops, order_srcs` | `{countries, providers, products, shop_order_groups, production_sites, shops, order_sources}` | **Cascading**: each dimension query *excludes* its own filter (so unselecting flows). SOG uses `UNNEST(STRING_SPLIT(..,' \| '))`. Optional cols branched on `getFcColumns()`. |

### Overview / KPIs / trends

| Route | Source | Params | Returns | Notes |
|---|---|---|---|---|
| `GET /api/overview` | Tier 1 (`dailyTier`); `alerts.parquet` for movers | full filter QS, `mode=full\|kpi\|chart`, `gran`, `priorFrom/To`, `yoyFrom/To` | `{rows, kpis, earlyWarningMovers, confirmedMovers, realCoverage}` | 3-parallel main+country shares+provider shares; KPIs delegate to `rangeAgg(tier, params, from, to)` for current/prior/YoY. Movers do `ROW_NUMBER() PARTITION BY country,provider ORDER BY current_period DESC` to dedupe across 6 most-recent confirmed periods. |
| `GET /api/trends` | Tier 1 (`dailyTier`) | `provider` (req), `country`, `countries`, full filter QS, `gran`, `buckets` | `TrendPoint[]` | Bucket-filtered avg/real/expected expressions; `attachCountryShares` post-merges JSON country-share strings per period when country isn't pinned. |
| `GET /api/trend-shares` | Tier 1 or `processedAsDaily` (if site/shop/order_source filter active) | `shareBy` (country/provider/package/product), full filter QS, `gran` | `[{week_start, shares: JSON}]` | DuckDB-built JSON via `STRING_AGG` of top-4 + "Other" per period. |
| `GET /api/country-trends` | Tier 1 | `country` (req), full filter QS, `gran`, `buckets` | `CountryTrendPoint[]` with `carrier_shares` JSON per period | Combined query: agg + per-provider shares in one SQL via window functions. |
| `GET /api/packagetype-trends` | Tier 1 | `packagetype` (req), `country`/`countries`, full filter QS, `gran`, `buckets` | `PackagetypeTrendPoint[]` (no carrier shares) | Simple agg; uses `product` col when on tier 1b. |
| `GET /api/product-trends` | `daily_product` always | `product` (req), `countries`, `providers`, `gran`, `buckets` | `TrendPoint[]` | Pre-exploded `product` col → no UNNEST. |
| `GET /api/generic-trend` | Tier 1, Tier 1b, OR `processedPruned("2024-01-01","2099-12-31")` | full filter QS, `country`/`provider`/`packagetype`/`product` single-value pins, `gran`, `buckets`, `minCost`, `maxCost` | `TrendPoint[]` | **Fallback path**: if `minCost`/`maxCost` set or processed-only filters (site/shop/source) active → reads processed directly with per-shipment AVG. Used by `CostTrend` in breakdown context. |
| `GET /api/carrier-share-trends` | Tier 1 (`daily`) or Tier 1b (`daily_product`) | full filter QS, `gran`, `sogProduct`, `basketSize` | `ShareRow[]` | Period share by provider; hardcoded `WHERE order_date >= '2025-01-01'`. Switches to `daily_product` when `sogProduct` is set; supports `basketSize=3` (≥3). |
| `GET /api/dimension-share-trends` | Tier 1 or Tier 1b | `shareBy` (country/provider/package/product), full filter QS + single-value pins, `gran` | `DimShareRow[]` | Parameterized carrier-share-trends. Same `>= '2025-01-01'` floor. |

### Breakdown

| Route | Source | Params | Returns | Notes |
|---|---|---|---|---|
| `GET /api/breakdown` | `bd_cache` (built from `processedPruned`); direct `processedPruned` for `level=total` | `dims` (4-CSV ordering), `level` (0..3 or `total`), `expand`/`expand2`/`expand3` pins, `hoverLevel`+`hoverValue` for tooltips, `costBasis=real\|real_expected`, `buckets`, `minCost`/`maxCost`, full filter QS | `{rows}` or `{total, level1, level2, level3, level4}` or `{summary, tooltip}` | The big one. Single-level, tooltip, and bulk modes. Lost-table retry path. SUB-CTEs for price/mix decomposition. Volume-share denominators use `COUNT(*) OVER ()`. |
| `GET /api/breakdown-sparklines` | `processedPruned(tsFrom or 12mo back, tsTo)` | `dims`, `level`, pins, `tsFrom`/`tsTo`, `buckets`, full filter QS | `{sparklines: {[dim_val]: number[]}}` | Last 12 months monthly avg cost per dim value; `MIN_MONTH_SHIPMENTS=10` threshold filters noisy months. Includes `__TOTAL__` row when `level=0`. Product dim does inline `UNNEST` on `shop_order_groups`. |
| `GET /api/breakdown-buckets` | Tier 1 or Tier 1b | single-value pins, `gran`, `tsFrom`/`tsTo`, `buckets`, full filter QS | per-period row with one column per bucket | **Stacked-area-ready**: zeros out non-selected buckets but always emits all 11 cols (stable Recharts schema). |
| `GET /api/breakdown-quota` | Tier 1 or Tier 1b | single-value pins, `gran`, `tsFrom`/`tsTo`, full filter QS | per-period `real_cost_quota` (sum_real/sum_revenue_invoiced) + `combined_cost_quota` (sum_routing/sum_revenue) | New (post-cutover). |

### Cost drivers / shifts

| Route | Source | Params | Returns | Notes |
|---|---|---|---|---|
| `GET /api/rate-changes` | `processedPruned(outer)` directly | full filter QS, `level=corridor\|package`, `country`/`provider` pins (for `level=package`), `costBasis`, `minCost`/`maxCost` | `RateChangeRow[]` | CTE: `src` tags rows as current/baseline by date, then `cur`/`base` aggregate, joined → impact = `(c_avg - b_avg) * c_n`. Sort by abs impact. |
| `GET /api/carrier-shifts` | (via `computeShifts("carrier", ...)`) | full filter QS, `costBasis` | `CarrierShiftRow[]` | Thin wrapper over `lib/shifts.ts:computeShifts`. Confirmed filter post-filters. |
| `GET /api/layer2` (routing shifts) | (via `computeShifts("routing", ...)`) | full filter QS, `costBasis`, `sortBy`/`sortDir` | `ShiftRow[]` | Force-clears `shopOrderGroups` (routing is at packagetype grain). Allow-listed sort columns. |
| `GET /api/product-shifts` | (via `computeShifts("product", ...)`) | full filter QS, `basketSize` (1/2/3/0), `costBasis`, `sortBy`/`sortDir` | `ShiftRow[]` | Tier 1b. |
| `GET /api/cost-drivers-top` | parallel `processedPruned` rate + 3 shift sources | full filter QS, `costBasis`, `topN` | `{drivers, savers}: TopDriverItem[]` | Fan-out 4 queries in parallel; merges into one ranked list split at zero. |

### Alerts / issues / changelog

| Route | Source | Params | Returns | Notes |
|---|---|---|---|---|
| `GET /api/alerts` | `issues.parquet` | `status=active\|resolved`, `resolvedWeeks` (1..26) | `{summary, incidents: IssueIncident[]}` | Issue-grain (not per-week alert). TS-side scoring: `issueScore` from impact + confidence + severity + duration; `issueConfidence` from type base + severity adj + confirmed bonus + log10 impact. "Last full week" computed as last completed Mon-Sun. |
| `GET /api/alerts/detail` | `alerts.parquet` | `type`, `country`, `provider`, `product`, `from`, `to` | `AlertRow[]` (per-week drill-down) | Dedupes across queues with `ROW_NUMBER() PARTITION BY current_period ORDER BY CASE alert_queue WHEN 'confirmed' THEN 0 ELSE 1`. |
| `GET /api/alerts/dismissed`, `POST` | `data/dismissed_alerts.json` | `issue_id`, `issue_end`, `comment?`, `undo?` | `DismissedMap` or `{ok, count}` | File-backed; best-effort `aws s3 cp` sync if `S3_DATA_PATH` set. Back-compat: old entries are bare strings, new are objects. |
| `GET /api/changelog`, `POST` | `data/changelog.json` | action=`add\|update\|delete`, entry, id | `ChangelogEntry[]` or `{ok, entry}` | Same JSON-file + S3-sync pattern as dismissed. |

### Cells / heatmaps / outliers / benchmarks

| Route | Source | Params | Returns | Notes |
|---|---|---|---|---|
| `GET /api/outliers` | `processedPruned` + `outlier_thresholds.parquet` | `thresholdScope=global\|range`, full filter QS | `{rows: OutlierRow[]}` | Global = JOIN against pre-computed p99.5 per provider; range = inline `PERCENTILE_CONT(0.995) WITHIN GROUP` over scope. |
| `GET /api/deviations` | Tier 1 (main + package) + `deviations_summary.parquet` + `processedPruned` (expand trend) | full filter QS, `expandCountry`/`expandProvider`, `gran` | `{rows, packages, trends}` | Main per-corridor from Tier 1, dev_pcts (`pct_over_20`, `pct_under_20`) pre-aggregated in `deviations_summary.parquet`. Trend caps to 12 months. |
| `GET /api/avg-costs` | Tier 1 | full filter QS, `gran=weekly\|monthly`, `periods` (≤52) | `AvgCostCell[]` | `period_list` CTE picks N most-recent periods ending at `to` (ignores `from`). |
| `GET /api/completeness` | Tier 1 or `dailyTierExpr` (processed-as-daily when needed) | full filter QS, `gran`, `periods` (≤52) | `{rows, latestComplete}` | Per-provider latest period with ≥85% coverage as a separate query. |
| `GET /api/benchmarks` | Tier 1 (`dailyTier`) | full filter QS | `{summary, opportunities: BenchmarkOpportunity[]}` | TS-side scoring (provider coverage, volume, capacity, gap → confidence); only best opportunity per corridor surfaced; min thresholds (`120` corridor ships, `30` source, `180` €/wk savings). |

### Transit Times

| Route | Source | Params | Returns | Notes |
|---|---|---|---|---|
| `GET /api/transit/heatmap` | `processedPruned(params.from, params.to)` | full filter QS | `{rows: TransitHeatmapCell[]}` | All stats (avg/p50/p85/p95, calendar+business) per country×provider over DELIVERED only. |
| `GET /api/transit/histogram` | `processedPruned` | `td=calendar\|business`, `th_country`/`th_provider` (heatmap-selected), full filter QS | `{rows: TransitHistogramBin[]}` (0..14, contiguous) | `LEAST(FLOOR(col), 14)`; empty bins back-filled in TS. |
| `GET /api/transit/kpis` | `processedPruned` | `th_country`/`th_provider`, full filter QS | `{kpis: TransitKPIs}` | All variants in one CTE. `unlogged_pct` = pre-corridor p95 join → `DATE_DIFF('day', order_date, CURRENT_DATE) >= p95_cal AND status != DELIVERED`. |
| `GET /api/transit/completeness` | `processedPruned` | `th_country`/`th_provider`, full filter QS | `{completeness: TransitCompletenessRow}` | Outcome mutually-exclusive counts (delivered/exception/unlogged/inflight) + separate `with_transit_ts_count` coverage axis. |
| `GET /api/transit/trend` | `processedPruned(tsFrom, tsTo)` | `gran`, `tsFrom`/`tsTo`, `th_country`/`th_provider`, full filter QS | `{rows: TransitTrendPoint[]}` | All stat variants per period; chart range may differ from sidebar `from`/`to`. |

### Export

| Route | Source | Params | Returns | Notes |
|---|---|---|---|---|
| `GET /api/export` | `processedPruned(dateFrom, dateTo)` | `dateFrom`/`dateTo` (req), single + multi pins for country/provider/packagetype/product, sites/shops/order_srcs | `text/csv` attachment | 12 fixed columns. Force-quotes `trackingnumber`/`ordernumber` for Excel; CSV-escapes commas/quotes/newlines elsewhere. Single-value param wins over multi-value. |

## Mart cutover delta (API layer)

Diff vs `main` for `src/app/api` + `src/lib`: 18 files, **+1297 / -72**. Three commits since main:

- `9ac4838` Shipping costs dashboard: cost-bucket filter + Breakdown Buckets view
- `68c5e40` Shipping costs dashboard: Buckets avg/total toggle + Transit Times tab
- `d750f9f` Shipping costs dashboard: revenue + cost quota everywhere, Share metric in Buckets

### New routes

- `src/app/api/transit/heatmap/route.ts` (+86)
- `src/app/api/transit/histogram/route.ts` (+99)
- `src/app/api/transit/kpis/route.ts` (+133)
- `src/app/api/transit/completeness/route.ts` (+125)
- `src/app/api/transit/trend/route.ts` (+104)
- `src/app/api/breakdown-buckets/route.ts` (+121)
- `src/app/api/breakdown-quota/route.ts` (+98)

That's the **whole Transit Times tab** + two new Breakdown sub-views (stacked-area buckets and quota time series). Nothing removed.

### Significantly modified routes

- `breakdown/route.ts` (+119/-?). Bucket-aware cost expressions, all 11 buckets materialized in `bd_cache`, per-bucket SUM cols on every row, quota CTEs (`quota_cur`, `quota_base`), 3-month wide-date-margin on the temp table fingerprint, lost-table retry paths in both single-level and bulk modes.
- `overview/route.ts` (+49). Added `total_revenue`, `cost_quota` (combined), `real_cost_quota`, `total_revenue_invoiced` to KPIs and chart rows. `rangeAgg` now returns the quota fields. The mover query gained the `alert_type != 'creep' OR lookback_weeks = 8` filter (so creep alerts only surface from the 8-week lookback).
- `country-trends` / `packagetype-trends` / `product-trends` / `generic-trend` / `trends` — all got the bucket-filter machinery: when `?buckets=...` is set, `avg_cost` and `avg_cost_real` are recomputed from per-bucket sums; `avg_cost_expected` becomes NULL (buckets are populated only on invoiced rows, no bucket attribution exists for expected-only rows).
- `breakdown-sparklines/route.ts` (+27). Added bucket-aware cost expression.

### Types / data layer

- `types.ts` (+178). New types: `BucketKey`, `ALL_BUCKETS`, `REDUCER_BUCKETS`, all `Transit*` shapes, `OverviewRow` revenue/quota fields, `BreakdownRow` per-bucket cols, `OverviewKPIs` quota fields, `TabKey` gains `"transit"`, `TABS` adds the Transit tab def, `Filters.buckets` field.
- `db.ts` (+13). `PARQUET` registry kept lean (the work was elsewhere). Bucket-related logic lives in routes, not db.ts.
- `colors.ts` (+44). New `BUCKET_COLORS` + `bucketLabel` helpers.

### What depended on the old SQL surface

Nothing visibly broken in the API layer. The cutover was additive (Transit + Buckets) plus universally adding revenue/quota fields to existing routes. `REF_TAB_ALIASES` already handles legacy `corridor-costs` / `carrier-shifts` / `shifts` / `product-shifts` aliases — alerts written before the breakdown/cost-drivers consolidation still route to the right tab.

## Gotchas / non-obvious bits

1. **The cache bypass triggers on text matching `BD_CACHE`**, not just on DDL. A user-written diagnostic query containing the literal "bd_cache" in a comment would skip the cache. Fine in practice but surprising.
2. **`bd_cache` fingerprint includes filter clauses verbatim** — including the *order* and *exact SQL fragments*. Reordering placeholders in `buildFilterClause` would invalidate every existing temp table on deploy.
3. **`dailyTier` doesn't honor `productionSites`/`shops`/`orderSources`** for the tier choice. The comment at `db.ts:166` says "production_site, shop, order_source now exist in all tiers" — meaning Tier 1 / Tier 1b parquets include these columns *after* the cutover. The `processedAsDaily` GROUP BY at `db.ts:202-204` confirms it. Worth verifying that the actual data files at deploy time really do carry these dims at Tier 1 — if a stale `daily.parquet` is in place, filters silently fail. (Confidence: high that the intent is correct; check at data-file mtime time.)
4. **`generic-trend` falls back to processed when `minCost`/`maxCost` *or* processed-only filters set** (`generic-trend/route.ts:44`). This is per-shipment scanning over the full `processedPruned("2024-01-01","2099-12-31")` glob — no month pruning when there are no date pins, and the date pins aren't read off `params.from`/`params.to` in this branch. Heavy if the user sets a cost range on a wide chart range.
5. **`carrier-share-trends` and `dimension-share-trends` hard-code `WHERE order_date >= '2025-01-01'`** at `route.ts:77` / `:107`. Anything before 2025 is silently excluded regardless of sidebar dates. Probably intentional (post-cutover data is what matters) but it's a quiet floor.
6. **Cost-basis "real" filters rows but bucket cost lines compute differently** — when buckets are filtered, real-cost lines use `SUM(buckets) / SUM(invoiced)` because buckets are populated only on invoiced rows; the comment at `trends/route.ts:107-108` (also `country-trends`, `packagetype-trends`, `product-trends`, `generic-trend`) explicitly notes this. Expected becomes NULL because buckets have no expected-only attribution.
7. **`alerts` (issues) endpoint's "last full week" math** uses `new Date()` (server clock) for the `dow` calculation but compares against `issue_start` strings. If the server is in a different TZ than the data, the boundary could shift by one calendar day. Probably fine in practice (issue_start is week-aligned by the pipeline) but a real edge.
8. **Overview's "movers" query swallows errors**: `try { ... } catch { /* alerts may not exist */ }`. If `alerts.parquet` is missing, you get an empty movers list with no error surfaced to the client. Good for partial-data tolerance, bad for debugging silent dropouts. Same pattern for `realCoverage`.
9. **`outliers` `global` scope ignores `params.from`/`params.to`** for *thresholds* (uses pre-computed all-time p99.5) but applies the date filter to the data scan. So switching between Global/Range can change outlier *count* dramatically — Global p99.5 might be cooler than Range p99.5 for a recent quiet window, surfacing more outliers from the recent range.
10. **`processedPruned` uses `require("fs")` at call time** (`db.ts:154`) instead of a module-level import. Fine in Node, but it's an unusual mix in an ES-modules TypeScript file.
11. **`dismissed_alerts.json` and `changelog.json` are file-backed** in `DATA_DIR`. The "best-effort" S3 sync is a fire-and-forget `execFile("aws", ...)`. On a multi-process deploy, two writers can stomp each other (no locking; not even mtime-checked load).
12. **`breakdown-buckets` always emits all 11 columns**, zeroing non-selected ones, specifically so Recharts has a stable schema. This wastes a few bytes per period but keeps the chart layer simple — the comment at `breakdown-buckets/route.ts:91-98` calls it out.

## Cross-reference

- `lib/shifts.ts` (referenced by carrier-shifts, layer2, product-shifts, cost-drivers-top) was *not* read in this slice — only its exported `computeShifts` and `CostBasis` are visible at the route boundary. Returns rows shaped by `CarrierShiftRow` / `ShiftRow` / `ProductShiftRow`.
- `lib/alerts.ts` (referenced by `/api/alerts`) was not read — only its exports `clamp`, `priorityBand`, `actionPlan`, `TYPE_CONFIDENCE_BASE`, `TYPE_IMPACT_WEIGHT`, `PriorityBand` are touched. The TS-side scoring lives there.

These two are the natural follow-ups for a future deep-read slice.
