# Shipping Costs Monitoring (nextjs) — vocabulary

**As of:** 2026-05-23 — full technical + mathematical review ([[S055_9837afe8_shipping-costs-dashboard-cutover-review|S055]]); cutover branch reviewed + fixed. Cost-basis and alert wiring verified. See **Post-cutover review ([[S055_9837afe8_shipping-costs-dashboard-cutover-review|S055]])** below for what changed.

> Term glossary for the `shipping_costs_monitoring_nextjs` app post-mart-cutover. The architecture lives in the app's own `CLAUDE.md` + `README.md`; this note pins the *language*. Deep references: `players/jebrim/quest-log/in-progress/S026_d{1,2,3}_*.md`.

## Routing

**App:** `bi-analytics/NFE/dashboards/shipping_costs_monitoring_nextjs/`. Self-contained — its own CLAUDE.md, README, docs/, pipeline, tests.

**Branch:** `shipping-mart-cutover` (worktree at `Documents/GitHub/bi-analytics/`). 13 commits ahead of main, additive. Main carries the pre-cutover version (PIF + factshipmentcosts fuzzy-join era). The cutover is one structural commit (`e892af7`) + a series of follow-ups adding Buckets, Quota, Transit Times, order_source split.

**Source of truth in the app:**

- `CLAUDE.md` — file map, runtime patterns, key invariants (~200 lines).
- `README.md` — stack, arch diagram, refresh modes (~200 lines).
- `docs/reference.md` — API routes table, parquet inventory, framework config.
- `docs/calculation_logic.html`, `docs/alert_system_guide.html`, `docs/tab_guide.html`, `docs/codebase_guide.html`, `docs/backtest_report.html` — generated HTML guides.

**Mart contract:** the cutover replaced five Redshift queries with two pulls against `enterprise_silver.shipping_data_mart`. Shipping-mart's own knowledge home is `bi-analytics/NFE/projects/3_shipping_data_mart/shipping-agent/` (pinned in shipping-data-mart routing keepsake).

## Cost columns (load-bearing)

Source: `query_mart.sql` + `pipeline.transform()` (`pipeline.py:533`).

| Term | Definition | Source |
|---|---|---|
| `shipping_cost` | Invoiced real cost. Null until the carrier invoice arrives. | `fs.real_shipping_cost_eur` |
| `expected_shipping_cost` | Modelled expected cost. Picturator/PicaAPI populated by mart; ORWO has a SQL-level `CASE` fallback (DHL/UPS country averages + seasonal Peak surcharges) — stand-in until ORWO procedure migrates. | `COALESCE(fs.expected_shipping_cost_eur, <orwo-wolfen fallback>)` |
| `shipping_cost_final` | Mart's own `COALESCE(real, expected, avg)`. | `fs.final_shipping_cost_eur` |
| `cost_for_routing` | **Default cost basis used everywhere downstream.** `COALESCE(shipping_cost_final, expected_shipping_cost)`. Pre-cutover this was the in-pipeline `COALESCE(real, expected)`; post-cutover it leans on the mart's `final_*` first, with pipeline's ORWO-aware expected as last resort. | `pipeline.py:552-564` |
| `has_cost` | `shipping_cost IS NOT NULL AND > 0`. The "real-cost coverage" flag. | `pipeline.py` |
| `has_expected` | Same shape for expected. | `pipeline.py` |

**Cost basis** in the UI: `real_expected` (uses `cost_for_routing`, the default) or `real` (uses only invoiced rows). `expected` exists as a visible-line toggle on Overview but not as a routing basis.

## The 11 cost buckets

Source: `fact_shipment_cost_summary`, server-cast to `float8`. New on cutover, aliased `bkt_*` everywhere.

| Category | Buckets | Note |
|---|---|---|
| Operational | `bkt_base_rate`, `bkt_truck_charges` | base rate + linehaul |
| Surcharge | `bkt_fuel_surcharge`, `bkt_remote_area`, `bkt_peak_demand`, `bkt_oversize_overweight`, `bkt_residential` | additive |
| Other | `bkt_other`, `bkt_unclassified` | catch-alls |
| **Reducers** | `bkt_discounts`, `bkt_credit_note` | **naturally negative**. `REDUCER_BUCKETS` in `types.ts`. UI renders as "-EUR X applied". |

**Invariant:** `cs.total_eur == fs.real_shipping_cost_eur` to the cent; the 11 buckets sum to `total_eur` for 100% of rows (`query_mart.sql:14-25`).

**Tax + customs duties excluded** (pass-through, not negotiable shipping cost).

**Bucket-filter mechanics:**

- Subset filter narrows the cost expression: avg/real lines recompute from `SUM(buckets)/SUM(invoiced)`.
- `avg_cost_expected` becomes `NULL` when a bucket subset is active — buckets exist only on invoiced rows; no bucket attribution for expected-only.
- Buckets always **materialized in `bd_cache`** so toggling subset doesn't invalidate the temp table.

## Quota / revenue

New on cutover (commit `d750f9f`). All routes carry these now.

| Term | Definition |
|---|---|
| `real_cost_quota` | `sum_real / sum_revenue_invoiced` — real cost as a share of revenue, restricted to invoiced rows. |
| `combined_cost_quota` (a.k.a. `cost_quota`) | `sum_routing / sum_revenue` — uses `cost_for_routing` across all rows. The "everywhere" quota. |
| `total_revenue` | Net revenue per shipment, split per-shipment in mart (no proportional split in pipeline). |
| `total_revenue_invoiced` | Revenue restricted to rows with `has_cost`. |

## Time / period machinery

| Term | Definition |
|---|---|
| `ANCHOR` | `2025-01-06` — Monday epoch for the `period_idx` numbering (`pipeline.py:105`). |
| `week_start` | Monday floor of `order_date`. |
| `period_start` | Week bucket anchored at `ANCHOR`. |
| **Current period** | The latest *fully completed* Monday-Sunday week (`_make_weekly_config`, `pipeline.py:116-133`). Today's incomplete week is excluded from alert detection. |
| `BASELINE_WEEKS` | Default `5` (`pipeline.py:69`). Configurable via `--baseline-weeks`. Anchored relative to current period. |
| `MAX_WEEKLY_PERIODS` | `26` — alert backfill cap, also caps `issues.parquet` lifetime past resolution. |
| `FRAMEWORK_MONTHS` | Default `6`. Limits trend/shift/deviation computation window. Tier-1 summaries still scan everything regardless. |
| Date-matched comparison | For incomplete periods (e.g. month-to-date), KPIs compare against the same day-range in prior + YoY (using `MAX(order_date)` to determine elapsed days), not full-month totals. Server-side; client just renders. |
| `tsFrom/tsTo` | Main **Chart Range** (URL `tsf`/`tst`). Separate from sidebar Period/Baseline. |
| `shiftTsFrom/To` | Shift-tab Chart Range (URL `stsf`/`stst`). |

## Alert / issue vocab

Two distinct surfaces:

- **`alerts.parquet`** — per-week, per-corridor, per-type rows. Two queues, 26-week history. Internal detail.
- **`issues.parquet`** — gap-and-island-ed islands across `alerts`. **The UI's primary surface** (`/api/alerts` returns issues, not alerts). One row per ongoing problem with frozen-baseline pinning.

### Two-queue mechanic

| Queue | Rule | Severity cap |
|---|---|---|
| `early_warning` | Runs every corridor every period regardless of coverage. Uses `cost_for_routing`. Fast surfacing, can fire on expected-only data. | — |
| `confirmed` | Same builder, filtered to corridors with weekly real-cost coverage ≥ `ALERT_REAL_COST_THRESHOLD = 65%`. | — |

Issue `confidence_level` becomes `"confirmed"` if the issue's key ever appears in the `confirmed` queue across the history window; otherwise `"estimated"`.

### Alert types

| Type | Trigger | Notes |
|---|---|---|
| `rate_spike` | Corridor cost: `|delta| > 0.20 EUR AND |pct_chg| > 10%`. Real coverage ≥ 65%, baseline vol ≥ 30, `total_impact > 0`. | UI ref_tab → `cost-drivers/rate-changes`. |
| `carrier_shift` | Gainers from `compute_carrier_shifts` (country+provider). | → `cost-drivers/carrier-shifts`. |
| `routing_shift` | Gainers from `compute_layer2` (country+packagetype+provider). | → `cost-drivers/routing-shifts`. Endpoint still named `/api/layer2`. |
| `product_shift` | Gainers from `compute_product_shifts`, **`basket_size==1` only** (avoid duplicates with multi-item baskets in alerts; UI has all basket sizes). | → `cost-drivers/product-shifts`. |
| `new_corridor` | Anti-join current vs baseline on `(country, provider)`, `n ≥ ALERT_MIN_VOL=30`. Medium if `n ≥ 50`. | — |
| `vanished_corridor` | Anti-join baseline vs current. Hardcoded `low`. <1 EUR impact dropped. | — |
| `creep` | `_detect_creep` CUSUM (`pipeline.py:1513`). Run twice: 8w + 26w lookback; shorter wins. Real-cost only. | → `cost-drivers/rate-changes`. |
| `deviation_blowout` | From `deviations.parquet`, thresholds on `total_dev`. Caps at medium. | → `deviations`. |
| `volume_anomaly` | `|z-score|` on `n_all` vs prior weeks ≥ 2.5 (med if ≥ 3.5). `eur_impact=0`. | — |

### Confirmation & suppression rules

| Rule | What it does |
|---|---|
| **`trend_confirmed`** (shifts) | `share_delta > 0 AND c_share > early_baseline_max` where `early_baseline_max` is the gainer's max share across the first half of baseline weeks. Confirmed shifts can stay `high`; unconfirmed cap at medium. |
| **`real_cost_confirmed`** + `confirmed_week` | For shift issues: does the gainer's invoiced real cost actually exceed the corridor's pre-shift baseline? If yes, set flag + week. UI shows a "real" badge. |
| **Frozen baseline override** | On the latest period only, `pipeline.main` loads prior `issues.parquet` and pushes active issues' baseline cost/share back into the next detection run, **replacing the rolling baseline**. Without this, a long-running shift gets absorbed into baseline and the alert silently resolves. (`pipeline.py:3562-3617`) |
| **Creep bounce-from-trough guard** | If long-term volume-weighted mean over `lookback_weeks*2` is *above* the latest week's cost, the "creep" is just recovery from a drop — skip. Also requires `consistency = weeks_above/n_analysis ≥ 0.6` and `|drift_pct| ≥ 10`. |
| **Creep baseline-volume guard** | Baseline vol must be ≥ 25% of current. Prevents creep on sparse baselines. |
| **Parent suppression** | Active `carrier_shift` whose same-direction `routing_shift` + `product_shift` children explain ≥ 70% (`SUPPRESSION_THRESHOLD`) of cumulative impact → `suppressed=True`. Opposite-direction children don't count. |
| **Creep ⊥ rate_spike** | If active `rate_spike` exists on same corridor, the `creep` is suppressed (rate_spike is the stronger signal). |
| **Drift monitor** | `_drift_monitor`: month vs `DRIFT_MONTHS=3` ago, slower than weekly creep. Only fires where no active rate_spike/creep covers the corridor. Higher impact threshold (`MIN_DRIFT_IMPACT = 1000 EUR`). |
| **Active-duplicate merge** | `_merge_active_duplicates`: if gap-and-island split an ongoing problem into two active issues for same `(type, country, provider, product)`, merge. |

### Issue lifecycle terms

| Term | Meaning |
|---|---|
| **Gap-and-island** | Consecutive weeks (gap ≤ 8 days) within `_issue_key` form one issue. |
| **`_issue_key`** | `type \| country \| provider` + product for routing/product shifts. Determines island grouping. |
| **`coverage_degraded`** flag | Set on an issue when real-cost coverage drops below the threshold mid-island. |
| **`status`** | `active` vs `resolved`. Resolved kept in `issues.parquet` for `resolvedWeeks` lookback. |
| **`headline`** | One-line human-readable summary per issue (formatted by `_issue_headline`). |
| **`cumulative_impact_eur`** | For rate_spike: recalculated against the frozen baseline (not summed island deltas). For creep/drift: sum of slope. |
| **`recurrence_count`** | How many times this `_issue_key` has reappeared. |
| **`dismissed`** | UI-only suppression. Stored in `data/dismissed_alerts.json`, S3-synced best-effort. Two storage shapes (string vs object) for back-compat. |

## Data tiers

| Tier | Files | Grain | Reader |
|---|---|---|---|
| **Tier 1** | `daily.parquet` (~300K rows) | `order_date × country × provider × packagetype × production_site × shop × order_source`. Sum of shipments, invoiced count, sum_real, sum_expected, sum_routing, sum_weight, sum_revenue, sum_revenue_invoiced, all 11 bucket sums. | Most routes via `dailyTier(params)`. |
| **Tier 1b** | `daily_product.parquet` (~2M rows) | Tier 1 + `product` (exploded from `shop_order_groups`) + `basket_size` (1/2/3-cap). Built via DuckDB UNNEST (Polars 1.33 segfaulted on the wide schema). | `breakdown-buckets`, `product-trends`, `product-shifts`, `carrier-share-trends`. |
| **Tier 2** | `processed/<YYYY-MM>.parquet` (monthly partitions, ~4.8M rows total, ~241 MB) | Full grain. | `processedPruned(from, to)` only — never globbed when avoidable. |
| Issues / alerts | `alerts.parquet`, `issues.parquet` | Per-week per-corridor (alerts); per-island (issues). | `/api/alerts/*`. |
| Deviations | `deviations.parquet` (corridor), `deviations_summary.parquet` (day × corridor × package) | `/api/deviations`. |
| Outliers | `outlier_thresholds.parquet` (per-provider p99.5, global) | `/api/outliers` (global scope). |
| Filter combos | `filter_combos.parquet` → `fc_mem` in-memory table on first connect | `/api/filter-options` cascading. |
| Meta | `data/meta.json` | All routes for sidebar / headers. mtime-cached. |

**Hot tricks:**

- **`processedPruned(from, to)`** (`db.ts:140-159`): enumerates `YYYY-MM` between dates, `fs.existsSync` filter, builds `read_parquet([...])`. Only this avoids full-glob scans of `processed/`.
- **`dailyTier(params)`** routes to the lightest tier: both packagetype+SOG → `processed`; SOG only → `daily_product`; otherwise → `daily`.
- **`processedAsDaily(from, to)`** wraps `processedPruned` in an aggregation subquery shaped like Tier 1 — used as fallback when filters require processed but the consumer wants Tier 1 columns.
- **`bd_cache`** (Breakdown only): temp table fingerprinted by filter clauses + wide date range (`from-3mo`..`to+1mo`), mutex-guarded creation, lost-table retry on HMR. Materializes all 11 bucket cols so bucket-subset toggles don't invalidate. Cache bypassed because text contains `BD_CACHE`.

## DuckDB query layer

| Term | Meaning |
|---|---|
| **`{{PARQUET}}`** template | Replaced with `'<file path>'` for Tier 1/1b, or `processedAsDaily(from, to)` subquery for processed. |
| **`{{FILTER}}`** template | Replaced with `buildFilterClause` output: `WHERE ...` for countries, providers, products, skus, shopOrderGroups, productionSites, shops, orderSources + optional date range + optional `trend_confirmed=true`. |
| **Query cache** | Module-level Map, `sha256(sql) + sha256(JSON.stringify(params))` key, **60s TTL**, 500-entry capacity, LRU eviction, 5min sweeper. DDL (CREATE/DROP/INSERT/DELETE) and anything containing `BD_CACHE` bypasses. |
| **Connection singleton** | Persistent `Connection` (not one-shot `Database.all`) so temp tables survive across requests. Mutex-guarded cold-start. |
| **`fc_mem`** | Pre-loaded in-memory table from `filter_combos.parquet` on first connect (~404 KB). |

## Tabs — old → new naming

The cutover consolidated tabs. Legacy URLs and alert refs still route via `OLD_TABS` / `REF_TAB_ALIASES`.

| Legacy tab | Current home |
|---|---|
| `countries`, `corridor-costs`, `providers`, `packages`, `products` | **Breakdown** (`/api/breakdown`, 4-dim drilldown) |
| `carrier-shifts`, `shifts`, `product-shifts` | **Cost Drivers** (with inner-tab `cdi` URL param: `rate-changes`, `carrier-shifts`, `routing-shifts`, `product-shifts`) |
| Pre-cutover individual tabs | Subsumed; nothing removed structurally. |

**Current tab list:** Overview, Alerts, Changelog, Cost Drivers, Breakdown, Deviations*, Outliers, Avg Costs*, Benchmarks*, Completeness, **Transit Times (new)**. `*` = hidden by default in `TabNav.HIDDEN_TABS` but URL-routable.

## Frontend state vocab

| Term | Meaning |
|---|---|
| `Filters` | Single source of truth for UI state. URL-backed via `filtersToParams`/`paramsToFilters`. |
| `QueryParams` | API-side projection of just the filter bits (no UI state). |
| **`TAB_SCOPE`** | Per-tab pure function that zeroes filter fields the tab can't honour (e.g. `outliers` zeroes `products`). Applied per-tab so a `display:none` tab doesn't get wrongly-scoped updates. |
| **`TAB_FILTERS`** | Per-tab visibility map for sidebar sections. |
| **`resolveSearchFilters`** | Expands per-dim search text into explicit selections — *only* when user hasn't already picked items. No-match → `["__NOMATCH__"]` sentinel (API treats as zero rows). |
| **Lazy mount + `display:none`** | Every tab `lazy()`-imported, mounted on first visit via `visitedTabs`, never unmounted. State (expanded rows, drag-zoom, pinned tooltips, sort) preserved by React subtree continuity. Tabs that re-fetch on filter change need `isActive` prop gate — currently only Overview and Breakdown honour it. |
| **`alertNavSeq`, `collapseSeq`, `localNavSeq`** | Ping counters (not state). Children watch for *rise* and react once. |
| **Pre-warm** | `fetchMeta` fires `/api/breakdown?level=total` fire-and-forget on mount to warm `bd_cache` before first drill. |
| **`bdBucketTotals`** | Live €-per-bucket totals reported up from Breakdown via `onBucketTotalsChange`, shown in Sidebar's Bucket filter. |

## Order source vocab

`order_source` derived in SQL from `fs.source_system`. Split in commit `7a86388` (were previously all bucketed as Picturator):

- `PicaAPI`
- `ORWO`
- `PCS`
- `Picturator`

**Picturator-Wolfen rows dropped at SQL** (`query_mart.sql:159-162`) — 98.3% duplicates of ORWO-Wolfen on same `trackingnumber`, weaker real-cost coverage.

## Things to verify when re-touching

- **`audit.py` / `backtest.py` are POST-cutover** (re-targeted in commit `0001b36`; verified [[S055_9837afe8_shipping-costs-dashboard-cutover-review|S055]]). `audit.py` loads `processed/*.parquet` + the full output set; `backtest.py` globs `processed/*.parquet` with a single-file fallback. No legacy `layer*` refs remain. *(The earlier "pre-cutover, will fail" note was stale — corrected [[S055_9837afe8_shipping-costs-dashboard-cutover-review|S055]].)*
- ~~**`order_date >= '2025-01-01'` floor** on `/api/carrier-share-trends` + `/api/dimension-share-trends`~~ **FIXED ([[S055_9837afe8_shipping-costs-dashboard-cutover-review|S055]])** — both now bind the sidebar `from`/`to`; pre-2025 history is reachable.
- **`cost_for_routing` is a straight pass-through of `shipping_cost_final`** (= mart `final_shipping_cost_eur` = `COALESCE(real, expected, avg)`, mart-internal) post-cutover — NOT the old in-pipeline `COALESCE(final, expected)`. NULL final = uncosted, carried as NULL.
- **ORWO `expected_shipping_cost`** comes from the SQL-level `CASE` fallback, not the mart's `expected_shipping_cost_eur` (which is null for ORWO source rows). Stand-in until ORWO procedure migrates to the mart.
- **Decimal → Float8 server cast** in `query_mart.sql` is non-optional. Polars schema inference dies on all-null Decimal chunks if the cast is removed.
- **Several Polars-segfault workarounds use DuckDB** (shipments+baskets join on full refresh, daily_product UNNEST, processed monthly-write filter+write loop). Reverting these to Polars likely re-introduces the segfaults on Windows.

## Open questions (for future asks)

- Coordination with the shipping data mart: when does ORWO expected migrate from the inline CASE fallback to a mart-side procedure? See keepsake pin for mart routing.
- ~~`audit.py` rewrite~~ DONE (re-targeted `0001b36`, verified [[S055_9837afe8_shipping-costs-dashboard-cutover-review|S055]]).
- The `corridor_costs_weekly.parquet` referenced by `_build_alerts` fallback path — is it actually written in main flow? Not seen in pipeline write path. (Still open.)
- ~~`/api/generic-trend` full-glob under cost-range~~ FIXED ([[S055_9837afe8_shipping-costs-dashboard-cutover-review|S055]]) — now bounds the read to the chart window + adds an `order_date` bind.

## Post-cutover review ([[S055_9837afe8_shipping-costs-dashboard-cutover-review|S055]], 2026-05-23)

Full technical + mathematical review of the cutover branch + fixes. Findings doc lives in-repo at `docs/cutover-review-2026-05-23/findings.md`. What changed (effective on the next pipeline refresh for the `pipeline.py` items):

- **Bucket invariant now reconciled.** The 11 buckets must sum to `real_shipping_cost_eur`; ~82k invoiced rows (237k EUR, 0.37%) had no `fact_shipment_cost_summary` row → buckets all 0 → read 0 on Breakdown. `transform()` now absorbs the residual `(real − Σbuckets)` into `bkt_unclassified` for invoiced rows. Where a summary row exists, buckets already tie to real to the cent.
- **Per-costed avg cost.** New `n_routing` column (count `cost_for_routing` non-null) in the daily/daily_product summaries + `processedAsDaily`; Overview + Avg Costs now divide by `SUM(n_routing)` (was `SUM(shipments)`) so they match Breakdown. ~7% of shipments are uncosted, which had diluted the old per-all average.
- **Shift metrics: Python is canonical.** `shifts.ts` now computes `eur_impact` vs the corridor `baseline_avg_cost` (not the losing counterpart), `trend_confirmed` over the first half of baseline weeks (not a fixed 42-day window), and `low_baseline_vol` over distinct baseline weeks present (not a nominal DATEDIFF). `issues.parquet` and the Shifts tab now agree.
- **Alert engine:** rate_spike merged-island impact no longer double-counts (takes the earliest island, which already spans the union window); issues **settle to a new normal** (resolve, flagged `settled`) after `BASELINE_WEEKS` flat weeks at the elevated level, so the frozen-baseline override stops re-arming a permanent step-change; drift monitor skips a partial latest month; `volume_anomaly` exempt from the global vol floor (collapses surface); `trend_confirmed` requires early-baseline presence; `sum_real` gated to the invoiced population.
- **Crash fix:** `avg-costs` + `deviations` 500'd on the packagetype+SOG combo (raw processed glob vs pre-agg columns) — now routed through `processedAsDaily`/`dailyTierExpr`.
- **Deploy model:** `pipeline.py` value changes only take effect on the next pipeline refresh (the DAG runs it before the pod serves). Landing the cutover branch on `main` triggers CICD — principal-gated. Next CVE bump `15.5.18` (CVE-2026-44578) is in.

## Related

- shipping-data-mart routing — keepsake pin for the underlying mart (the `shipping-agent/how_to.md` etc.).
- [[coverage-questions-time-and-source-axis]] — skill draft from [[S023_2026-05-21_shipping-mart-coverage-audit|S023]] on cost-coverage methodology.
- [[shipping_mart_coverage_audit_2026-05-21]] — bank draft, the four concentrated holes (ORWO POST, Picturator POST_DVF, MAERSK, ASENDIA).
