# S026 D1 — SQL & pipeline read

Slice: `sql/` + `pipeline.py` + `audit.py` + `backtest.py` + tests, on branch `shipping-mart-cutover`.
App root: `NFE/dashboards/shipping_costs_monitoring_nextjs/`.

## SQL layer

Two files only on this branch — the cutover collapsed five legacy queries into two mart pulls.

- `sql/query_mart.sql` — **shipment spine**. Grain: one row per `shipment_id`. Source: `enterprise_silver.fact_shipments fs`, LEFT JOIN `dim_shipping_providers dim` (~195 rows; chosen over the 17M-row `map_shipment_key` after spot-check confirmed zero extkey divergence), LEFT JOIN `fact_shipment_cost_summary cs` for 11 EUR cost buckets. Filtered by `fs.shop_order_created_date >= {DATE_FROM} AND < {DATE_TO}`. Decimal cols server-cast to `float8` (mart numerics returned as Decimal blow up Polars schema inference on all-null batches). Output column names aliased to legacy `RAW_KEEP_COLS` so downstream pipeline is unchanged. Cutoff rule: drops `(source_system='Picturator' AND production_site='Wolfen')` — 98.3% duplicates of ORWO-Wolfen rows on same trackingnumber (`query_mart.sql:159-162`).
- `sql/query_mart_items.sql` — **line-grain basket pull**. Pre-aggregated to `(shipment_id, sku, articlenumber, shop_order_group)` SUM(quantity) in Redshift; baskets built in Polars. Joins `fact_shipment_orderitems oi` to `fact_shipments fs` for the date cutoff and to `dw.dim_products dp` (TODO marker — non-mart dim, awaiting migration; `query_mart_items.sql:10`).

### Cost composition (new on cutover, 19db6be)

Pulled from `fact_shipment_cost_summary`, aliased `bkt_*`: `base_rate`, `truck_charges`, `fuel_surcharge`, `remote_area`, `peak_demand`, `oversize_overweight`, `residential`, `discounts`, `credit_note`, `other`, `unclassified`. Server-verified property: `cs.total_eur == fs.real_shipping_cost_eur` to the cent across ~1M Q1-2025 rows, and the 11 bucket cols sum to `total_eur` for 100% of rows (`query_mart.sql:14-25`). `discounts_eur` and `credit_note_eur` are naturally negative — UI renders as "-EUR X applied", not as positive shares. Tax and customs duties intentionally excluded (pass-through, not negotiable shipping cost).

### Cost columns exposed to pipeline

- `shipping_cost` ← `fs.real_shipping_cost_eur` (invoiced; nullable until invoice arrives).
- `expected_shipping_cost` ← `COALESCE(fs.expected_shipping_cost_eur, ORWO-Wolfen fallback)`. The ORWO fallback is a CASE on `destination_country`/`shippingprovider_extkey`/`shop_order_created_date` season encoded inline in SQL (DHL country averages + UPS country averages + POST_DVF flat rate; Peak-in-Peak Nov 24–Dec 7 and Peak Nov–Dec surcharges). Stand-in until the ORWO procedure migrates into the mart (`query_mart.sql:36-43`).
- `shipping_cost_final` ← `fs.final_shipping_cost_eur` — the mart's own `COALESCE(real, expected, avg)`. Used as the primary `cost_for_routing` source by `pipeline.transform()`.

### Mart cutover delta — what the SQL replaced

Single commit `e892af7` ("cut over pipeline to shipping data mart") deletes:
- `sql/query.sql` — PIF-based shipment spine (`dw.production_items_fact pif` + `dw.dim_products dp`, LISTAGG-built baskets, fuzzy 120-day datediff join to `bi_dw_dev_dbo.factshipmentcosts` for cost).
- `sql/query_costs.sql` — separate factshipmentcosts pull.
- `sql/query_pif.sql` — secondary PIF pull (33 lines).
- `sql/revenue_sf.sql` — `dw.sales_items_fact` aggregated to `nettotal_eur` per ordernumber.
- `sql/schenker_costs.sql` — `asa.db_schenker` aggregated to `pcs_orderid`.

The mart already attaches real cost (cents-exact), expected cost, net revenue split per shipment, and Schenker invoices at shipment grain — so the cutover removes one fuzzy date-bounded join, three separate Redshift pulls, the Schenker fanout, and the proportional revenue split logic that all used to live in `pipeline.py`.

## Pipeline overview

**Entry point.** `pipeline.py:main()` (`pipeline.py:3418`). CLI flags:
- `--refresh [DATE]` — incremental pull from DATE (YYYY-MM-DD) or last 3 months if no date. Merges with cached older data.
- `--refresh-full` — full re-pull from `FULL_DATE_FROM = 2024-01-01` (`pipeline.py:258`).
- `--months N` — shortcut for `--refresh` with `today - N*30` cutoff floored to month start.
- `--rebuild-raw` — delete `raw.parquet` to force fresh pull.
- `--simulate-date YYYY-MM-DD` — pipeline acts as if today is that date; trims processed files beyond it.
- `--baseline-weeks N` — override `BASELINE_WEEKS = 5` (`pipeline.py:69`).
- `--framework-months N` — limit framework computation window (default 6; 0 = all). Tier-1 summaries still scan everything.
- No flag = `mode="cache"`, reuse `raw.parquet`.

### Redshift connection

Via `shared.database.pull_data()` (imported lazy inside `_pull_query`, `pipeline.py:275`). Uses `redshift_connector` underneath (inferred from the Decimal comment in `query_mart.sql:30-34`). Pull path is `pandas` first then `pl.from_pandas(pdf)` — `pull_data(..., as_polars=True)` was tried but failed: Polars' row-oriented schema inference can't append a real f64 value to a Null-inferred column from leading all-NULL chunks; pandas is forgiving with mixed types.

### Refresh chunking + memory discipline

`_pull_query_chunked` (`pipeline.py:306`) splits any date range into monthly chunks and pulls them sequentially, spilling each chunk to a per-chunk parquet under `data/_pull_spill/` immediately and dropping it from RAM. The final dataframe is built by `pl.read_parquet([list_of_paths])` — keeps in-flight working set at one chunk instead of accumulating in a Python list. Resume hook: if `_ship_temp.parquet` exists at `--refresh-full` start, skips the (slow) shipments pull and reuses it (`pipeline.py:434`).

### Shipments+baskets join — DuckDB-backed

Full-refresh path joins ship spine + baskets via DuckDB instead of Polars: `con.execute("COPY (... read_parquet ... LEFT JOIN ... ) TO raw.parquet")` (`pipeline.py:486-503`). Polars (eager and lazy `sink_parquet`) segfaulted on 10M+ shipments × 30+ cols × baskets under memory pressure; DuckDB hash-joins on parquet with automatic disk spilling. Refresh (3-month) path keeps the eager Polars join because the window is small.

### Processing chain

```
pull_raw → transform → write_processed (data/processed/<YYYY-MM>.parquet, monthly parts)
                    ↓ free df, reload subsets per stage
  framework window (last framework_months months, default 6):
    compute_trends(week_start) → corridor_trends_weekly.parquet (cost_types real/expected/coalesce)
    compute_deviations         → deviations.parquet
    for each of MAX_WEEKLY_PERIODS=26 weekly periods, latest first:
      compute_corridor_costs   (L1-equivalent, country+provider)
      compute_layer2           (L2 routing shifts, packagetype grain)
      compute_product_shifts   (basket sizes 1/2/3+/all via exploded shop_order_groups)
      compute_carrier_shifts   (country+provider, no packagetype split)
      _build_alerts queue=early_warning (always) + queue=confirmed (where real-cost coverage ≥65%)
    concat → alerts.parquet
    _build_issues(alerts_all) → issues.parquet
    write_meta → meta.json
  summaries (reload SUMMARY_COLS from processed):
    _write_daily_summary           → daily.parquet (Tier 1)
    _write_daily_product_summary   → daily_product.parquet (Tier 1b, DuckDB UNNEST)
    _write_deviations_summary      → deviations_summary.parquet
    _write_outlier_thresholds      → outlier_thresholds.parquet
    filter_combos (2025+ only)     → filter_combos.parquet
```

### Key transformations (`transform`, `pipeline.py:533`)

- Drops `shippingprovider IN ('DUMMY','XXX','STORNO')`.
- Drops rows with null `trackingnumber` if `order_date < today-14d` (recent orders may not have shipped).
- `has_cost` = `shipping_cost IS NOT NULL AND > 0`.
- `has_expected` = `expected_shipping_cost IS NOT NULL AND > 0`.
- **`cost_for_routing` = COALESCE(`shipping_cost_final` if not null and >0, `expected_shipping_cost`)** (`pipeline.py:556-564`). Pre-cutover this was the in-pipeline `COALESCE(real, expected)`. Now it leans on the mart's own `final_shipping_cost_eur` (which is `COALESCE(real, expected, avg)`), with the pipeline's ORWO-aware expected as last-resort fallback. Commit `7a86388`.
- Period columns: `week_start` (Monday floor), `period_idx` and `period_start` (week buckets anchored at `ANCHOR = 2025-01-06`), `month_start`.
- Categoricals: `shippingprovider`, `packagetype`, `destination_country`, `production_site`, `shop` cast to `pl.Categorical` (in-memory ID table). `_decat()` casts back to Utf8 before parquet write.
- Sidebar dims pulled through to processed: `production_site`, `shop`, `order_source` (the last derived in SQL: PicaAPI / ORWO / PCS / Picturator from `fs.source_system`; commit `7a86388` split out ORWO and PCS labels — were previously bucketed into Picturator).

### Period config (weekly + monthly)

`PeriodConfig` (`pipeline.py:105`) holds `mode`, `period_col`, `current_val`, `baseline_vals` (5 weeks back), `ref_vals` (same as baseline for weekly), `current_end`, `suffix`. `_make_weekly_config` picks current week as the latest **fully completed Monday-Sunday week** (last full Sunday rule, `pipeline.py:116-133`). `_all_weekly_configs` enumerates up to `MAX_WEEKLY_PERIODS=26` historical configs for backfilling alerts/issues. Monthly path uses `_make_monthly_config_for` — first-of-month current, prior month baseline, Mondays-in-prior-month for share reference.

## Alert system

### Two-queue mechanic (`_build_alerts`, `pipeline.py:1771`)

Every period gets two alert passes:
- **early_warning** — runs on every corridor regardless of real-cost coverage. Costs lean on `cost_for_routing` (the COALESCE column). Surfaces issues fast but can fire on expected-only data.
- **confirmed** — same builder, filtered by `eligible_corridors` from `_corridor_real_coverage()` — only corridors where weekly real-cost share ≥ `ALERT_REAL_COST_THRESHOLD = 65%`. The dedup in `_build_issues` prefers `confirmed` over `early_warning` when both fire for the same `(type, country, provider, product, period)`.

The pipeline persists both queues in `alerts.parquet` with an `alert_queue` column. Issue confidence_level becomes `"confirmed"` if the issue key ever appeared in the confirmed queue across the history window; otherwise `"estimated"` (`pipeline.py:2598-2600`, `2736`).

### Alert types (and what triggers each)

1. **`rate_spike`** — from `corridor_costs` `flagged=True` rows (`|delta| > 0.20 EUR AND |pct_chg| > 10%`). Requires real-cost coverage ≥65%, baseline volume ≥30, `total_impact > 0` (cost increases only). ref_tab `breakdown` (remapped to `cost-drivers/rate-changes`).
2. **`carrier_shift`** — gainers from `compute_carrier_shifts` (country+provider grain, no packagetype). Drops `low_baseline_vol` corridors; requires `eur_impact > 0`. ref_tab `carrier-shifts` → `cost-drivers/carrier-shifts`.
3. **`routing_shift`** — gainers from `compute_layer2` (packagetype grain). Same drops. ref_tab `shifts` → `cost-drivers/routing-shifts`.
4. **`product_shift`** — gainers from `compute_product_shifts` filtered to `basket_size == 1` (single-item baskets only — avoids duplicates with multi-item baskets). ref_tab `product-shifts` → `cost-drivers/product-shifts`.
5. **`new_corridor`** — anti-join current vs baseline on `(country, provider)`, `n_shipments >= 30` (`ALERT_MIN_VOL`). Severity boosted to medium if `n >= 50` (`ALERT_NEW_CORRIDOR_MIN_VOL`).
6. **`vanished_corridor`** — anti-join baseline vs current. Severity hardcoded `low`. `cumulative_impact_eur` < 1 EUR ones get dropped in `_build_issues` (`pipeline.py:2667-2672`).
7. **`creep`** — from `_detect_creep` (CUSUM, `pipeline.py:1513`). Run twice per period: `lookback_weeks=8` and `26` (long lookback). Shorter window wins; corridors already seen by 8w are skipped at 26w. Real-cost only. ref_tab `avg-costs` → `cost-drivers/rate-changes`.
8. **`deviation_blowout`** — from `deviations.parquet`. Severity uses `total_dev` thresholds (10K medium / 50K high) — capped at medium for deviations.
9. **`volume_anomaly`** — z-score on `n_all` per corridor vs prior weeks, |z| ≥ 2.5. Severity medium if |z| ≥ 3.5 else low. `eur_impact=0`.

### Severity tiers (`pipeline.py:1792-1817`)

Raw tier by `|eur_impact|` (≥500 high, ≥100 medium, ≥10 low) or by `|total_dev|` (≥50K / ≥10K) or by new_corridor vol (≥50 → medium). Then caps: **unconfirmed shifts cap at medium**; **deviation alerts cap at medium**. Below `ALERT_LOW_EUR = 10` → return None (drop).

### Confirmation / suppression rules

- **Trend confirmation (shifts).** `trend_confirmed = share_delta > 0 AND c_share > early_baseline_max` where `early_baseline_max` is the gainer's max share across the first half of baseline weeks (`pipeline.py:899-918`). Confirmed shifts can stay `high` severity; unconfirmed cap at medium.
- **Frozen baseline (issues).** On the latest period only, `pipeline.main` loads prior `issues.parquet` and rebuilds `_override_costs` / `_override_carrier_shares` / `_override_routing_shares` / `_override_product_shares` from active+unsuppressed issues. These get passed into `compute_corridor_costs` / `compute_layer2` / `compute_product_shifts` / `compute_carrier_shifts` and **replace the rolling baseline avg/share for the corridors that already have active issues** (`pipeline.py:3562-3617`, `compute_corridor_costs:640-660`, `_compute_shifts:844-865`). Without this, the rolling baseline absorbs a long-running shift and the alert silently resolves; the override pins detection against the original baseline until the shift truly reverses.
- **Creep `bounce-from-trough` guard** (`pipeline.py:1661-1672`). If the long-term volume-weighted mean over `lookback_weeks*2` is above the latest week's cost, the "creep" is just recovery from a drop — skip. Also requires `consistency = weeks_above / n_analysis >= 0.6` (`ALERT_CREEP_CONSISTENCY`) and `|drift_pct| >= 10`.
- **Creep frozen baseline volume guard.** Baseline volume must be ≥25% of current (`pipeline.py:1611`) — prevents noisy creep on sparse-baseline corridors.
- **Real-cost confirmation for shifts (issues).** `_build_single_issue` cross-checks: did the gainer's invoiced real cost actually exceed the corridor's pre-shift baseline cost? If yes → `real_cost_confirmed = True`, also sets `confirmed_week` (`pipeline.py:2828-2861`). Surfaces in UI as a "real" badge.
- **Parent suppression.** `_suppress_parents`: active `carrier_shift` issues whose same-direction `routing_shift` + `product_shift` children explain ≥70% (`SUPPRESSION_THRESHOLD`) of cumulative impact get `suppressed=True`. Opposite-direction children don't count (`pipeline.py:3253-3255`).
- **Creep ⊥ rate_spike.** `_suppress_creep_with_rate_spike`: if an active rate_spike exists on the same corridor, the creep gets suppressed (rate_spike is the stronger signal).
- **Drift monitor.** `_drift_monitor` (`pipeline.py:3042`) compares current month vs `DRIFT_MONTHS=3` ago, slower window than weekly creep. Only fires for corridors not already covered by active rate_spike/creep. Higher impact threshold (`MIN_DRIFT_IMPACT = 1000 EUR`).
- **Active duplicate merge.** `_merge_active_duplicates`: if gap-and-island split a single ongoing problem into two active issues for the same `(type, country, provider, product)`, merge into one (earliest start, latest end, sum impacts).

### Issue lifecycle (`_build_issues`, `pipeline.py:2535`)

1. Dedup per `(type, country, provider, product, period)` preferring `confirmed` over `early_warning`.
2. Group rows by `_issue_key()` (`type|country|provider` + product for routing/product shifts).
3. Gap-and-island within key: consecutive weeks (gap ≤ 8 days) form one issue.
4. `_build_single_issue` per island: computes frozen baseline cost/share, current cost/share (latest week with ≥65% real coverage for cost-types), cumulative impact (rate_spike recalculates against frozen baseline, not summed island deltas; creep/drift sum slope), status, coverage_degraded flag, headline.
5. `_drift_monitor` adds drift-type issues.
6. `_add_recurrence_count`, `_suppress_parents`, `_suppress_creep_with_rate_spike`, drop low-impact + vanished-zero-impact, `_merge_active_duplicates`.

## Outputs (parquet inventory)

All in `data/` unless noted. Reader column is best-guess from API filename + grep of `src/`.

| File | Grain / contents | Consumed by |
|---|---|---|
| `raw.parquet` | Shipment-grain from the mart, all RAW_KEEP_COLS. Source for everything downstream. | pipeline cache, audit |
| `processed/<YYYY-MM>.parquet` | Full-grain shipment rows partitioned by month. Cols include period, week_start, basket_sku, shop_order_groups, 11 bucket cols, lead-time cols. | Reloaded by pipeline per stage; not read directly by API (API hits the Tier-1 summaries) |
| `daily.parquet` | Tier-1 daily summary by `(order_date, country, provider, packagetype, production_site, shop, order_source)`. SUM of shipments / invoiced / sum_real / sum_expected / sum_expected_for_invoiced / sum_routing / sum_weight / sum_revenue / sum_revenue_invoiced + 11 buckets. | `lib/db.ts` central reader → most `/api/overview`, `/api/breakdown`, `/api/avg-costs`, `/api/trends`, `/api/transit`, `/api/country-trends`, `/api/packagetype-trends`, `/api/cost-drivers-top`, `/api/completeness` |
| `daily_product.parquet` | Tier-1b: same grain plus `product` (exploded from `shop_order_groups`) and `basket_size` (1/2/3-cap). Built by DuckDB UNNEST + GROUP BY. | `/api/breakdown-buckets`, `/api/product-trends`, `/api/product-shifts`, `/api/carrier-share-trends`, `lib/shifts.ts` |
| `corridor_trends_weekly.parquet` | Per-week per-corridor avg_cost / n_cost / n_all / share_pct / avg_weight, three rows per (corridor, week) for `cost_type` ∈ {real, expected, coalesce}. | Alerts (creep, volume anomaly, issues), `/api/trends`, `/api/avg-costs` |
| `deviations.parquet` | Corridor-level real vs expected deviation stats (mean_deviation, pct_over_20, pct_under_20, total_deviation_eur, mean_dev_pct). | `/api/deviations` (corridor view), alerts |
| `deviations_summary.parquet` | Per-day per-corridor per-packagetype deviation aggregates. | `/api/deviations` (drill-down replaces a processed/*.parquet scan) |
| `outlier_thresholds.parquet` | `p99.5(cost_for_routing)` per `shippingprovider`. Precomputed for global outlier scope. | `/api/outliers` |
| `alerts.parquet` | All per-period alert rows, both queues, last 26 weeks. | `/api/alerts/detail`, `_build_issues` |
| `issues.parquet` | Persistent issues from alert history (one row per gap-and-island island, plus drift). Carries frozen baseline, status, headline, suppression flags. | `/api/alerts` (issues are the UI surface; alerts.parquet is internal detail) |
| `filter_combos.parquet` | Distinct `(country, provider, packagetype, shop_order_groups, production_site, shop, order_source)` with row counts (2025+). | `/api/filter-options` cascading sidebar |
| `meta.json` | Run timestamp, date_bounds, current_period/baseline meta, ordered lists of countries/providers/products/skus/shop_order_groups, alert counters by severity, production_sites/shops/order_sources. | All API routes for sidebar population, headers |
| `corridor_costs_weekly.parquet` | (Implied by `_build_alerts` reads / referenced at `pipeline.py:1822`. Not currently written by main flow — may be produced by older runs or by a path I didn't see.) | Alerts (cc fallback) |

`carrier_shifts_weekly.parquet`, `layer2_shifts_weekly.parquet`, `layer2_product_shifts_weekly.parquet` are also referenced as fallbacks by `_build_alerts`; in the main path the dataframes are passed in-memory and the `read_parquet` fallback only triggers if the in-memory frame is None.

## Audit & backtest

### `audit.py`

Read-only verification harness, 603 lines. Loads outputs, runs PASS/FAIL/WARN checks. Covers:
- Transform basics (week_start/period_start types, 7-day period gaps, no DUMMY rows, cost vs routing fill rates).
- Completeness (row count sanity, coverage_pct in 0–100, `(provider, week_start)` uniqueness).
- L1 algebra (delta = avg − avg_b, pct_chg formula, eur_impact = delta × n_cost, flag threshold logic, weight decomp rate+weight ~= delta, avg_cost_per_kg formula).
- L2 (cost timing: gainer_cost from current period, baseline_avg_cost from baseline period; cost_premium algebra; eur_impact sign-consistency with shifted_vol × cost_premium; yoy_seasonal exists).
- L3 country rollup (`net_impact = increases + savings`; L3 sum ~= L2 sum within 1%).

**Stale.** `audit.py:48-53` opens `layer1_corridors.parquet`, `layer1_decomp.parquet`, `layer2_shifts.parquet`, `layer3_countries.parquet`, `layer3_providers.parquet`, `layer4_providers.parquet`, `avg_costs.parquet`, `completeness.parquet`, `outliers.parquet`, `corridor_trends.parquet`. None of these exist in current `data/`. The audit hasn't been updated to match the cutover-era output set (no `_weekly` suffix awareness, expects single-file processed.parquet not `processed/` partitioned dir — has a conditional fallback to the dir on line 46, but everything else assumes the old shape). **Treat audit.py as not-yet-rewritten for the mart cutover.**

### `backtest.py` + `backtest_report.py`

333-line harness that replays L1+L2 detection for the last N weeks (default 12). Loads `processed.parquet` (single-file path — also stale; needs `processed/`), iterates Monday-aligned period_starts with ≥`MIN_VOL_PERIOD=2500` shipments, computes L1 corridor rate changes vs 42-day rolling baseline and L2 routing shifts vs 3-week share reference, picks `TOP_N=10` per week by `|eur_impact|`, writes `data/backtest.parquet`. `backtest_report.py` renders an HTML report (horizontal bar charts per week, plotly) using `lib.style` + `lib.report`. Stricter thresholds than pipeline alerts (`MIN_ABS_CHANGE_EUR=0.50` vs 0.20, `MIN_SHIPMENTS=100`) — this is a simpler historical signal-quality check, not the production alert pipeline.

### Tests

- `tests/test_pipeline.py` (1302 lines). Covers nested `_severity` logic (locally mirrored — has explicit "kept in sync manually" comment), `_issue_headline` formatting (thousands/millions/negative/duration), `_issue_id` and `_issue_key` determinism, `_suppress_parents` (children explain ≥70%, opposite-direction not counted, product_shift children also suppress, resolved parent untouched), `_merge_active_duplicates`, `_drift_monitor` (thresholds, coverage gate, cost-decrease not flagged, low-volume skipped), `_build_single_issue` (active/resolved, frozen-baseline path, confidence_level confirmed/estimated, rate_spike cumulative recalc), `_empty_issues` schema.
- `tests/test_creep.py` (150 lines). Targets `_detect_creep` directly via injected `trends_df`: steady linear increase detects with right drift_pct, single spike no detection (consistency fail), gradual-then-reversal no detection (latest = baseline), sub-pct-threshold no detection.

## Mart cutover delta — slice-level

**SQL.**
- Five queries (`query.sql`, `query_costs.sql`, `query_pif.sql`, `revenue_sf.sql`, `schenker_costs.sql`) → two (`query_mart.sql`, `query_mart_items.sql`).
- Source tables changed: `dw.production_items_fact` + `dw.dim_products` + `bi_dw_dev_dbo.factshipmentcosts` + `dw.sales_items_fact` + `asa.db_schenker` → `enterprise_silver.fact_shipments` + `enterprise_silver.dim_shipping_providers` + `enterprise_silver.fact_shipment_cost_summary` + `enterprise_silver.fact_shipment_orderitems` (+ `dw.dim_products` still used for SKU lookup in items pull, TODO to migrate).
- Real cost arrives invoice-attached at shipment grain — no more 120-day fuzzy datediff join (`factshipmentcosts` LEFT JOIN with `ABS(DATEDIFF('day', f.invoicedate, d.order_date)) < 120`).
- Net revenue arrives split per shipment in `net_revenue_eur` — no more `sales_items_fact` aggregation + proportional split in pipeline.
- Schenker invoices arrive at shipment grain — no more `asa.db_schenker` SUM-by-pcs_orderid fanout.

**Pipeline.py.**
- `pipeline.py` shrank 591 → ~3700 lines net (the 591-line shrink in `e892af7` was the cost-source/revenue-split deletion; subsequent commits added bucket/lead-time pulls, frozen-baseline overrides, issue building, suppression layers).
- `pull_raw` rewritten — two queries instead of five; basket build moved from Redshift LISTAGG to Polars group_by; DuckDB-backed full-refresh join.
- `transform`'s `cost_for_routing` switched from in-pipeline `COALESCE(real, expected)` to `COALESCE(shipping_cost_final, expected_shipping_cost)` — leans on mart's `final_shipping_cost_eur` which is itself `COALESCE(real, expected, avg)` (commit `7a86388`).
- New columns added through to processed: 11 `bkt_*` cost buckets, `transit_time_days`, `transit_time_business_days`, `current_shipping_status` (commit `19db6be`).
- `daily.parquet` carries bucket sums; `daily_product.parquet` build path moved to DuckDB UNNEST (Polars 1.33 explode+group_by segfaulted on the wide schema, `pipeline.py:2356-2359`).
- `order_source` derived in SQL from `fs.source_system` (PicaAPI / ORWO / PCS / Picturator), three of those split out in commit `7a86388` (were previously all "Picturator").

## Gotchas / non-obvious bits

- **Decimal → Float8 server cast is non-optional.** `redshift_connector` returns mart numerics as `Decimal`; Polars schema inference dies on all-null chunks → real Decimal in later chunk → row builder explodes. Every numeric mart column in `query_mart.sql` is `::float8` cast server-side (`query_mart.sql:30-34`).
- **Bucket cols can arrive as String even with f8 cast.** When a pull chunk has all-NULL values for a bucket, pandas infers `object` dtype, which becomes `pl.String` after `from_pandas`. `_pull_query` force-casts `BUCKET_COLS` to `Float64` per chunk (`pipeline.py:288-290`) — without this, `pl.read_parquet([spilled_chunk_paths])` can't stitch a schema.
- **Polars segfault on wide-schema operations.** Multiple sites switched to DuckDB after polars 1.33 segfaulted on Windows with the 30+ col schema under memory pressure: (1) shipments+baskets join on full refresh (`pipeline.py:486`); (2) daily_product explode+group_by (`pipeline.py:2372`); (3) `write_processed`'s month iterator uses explicit `filter+write` rather than `group_by` tuple iterator because the latter hit access violations (`pipeline.py:2473-2475`).
- **The mart's `final_shipping_cost_eur` is `COALESCE(real, expected, avg)`.** Pipeline's `cost_for_routing` uses this as primary, with its own ORWO-aware `expected_shipping_cost` as last-resort fallback for rows where the mart has nothing (`pipeline.py:552-564`). The mart populates `expected_shipping_cost_eur` for Picturator/PicaAPI but **not** for ORWO source rows — ORWO expected lives in a separate procedure not yet migrated to the mart, hence the SQL-level Wolfen fallback CASE (`query_mart.sql:36-43`).
- **Picturator-Wolfen rows are dropped at SQL.** 98.3% are duplicates of ORWO-Wolfen on the same `trackingnumber` with weaker real-cost coverage. The SQL filter is `AND NOT (fs.source_system = 'Picturator' AND fs.production_site = 'Wolfen')` (`query_mart.sql:159-162`).
- **`product_shift` only uses single-item baskets in alerts.** `basket_size == 1` filter at `pipeline.py:1945` avoids duplicating the same product across multiple basket-size cuts when feeding alerts. The product_shifts table still carries all basket sizes (1/2/3+/all) for the UI to filter.
- **Frozen baselines only apply to the latest period.** In `pipeline.main` the override dicts are passed only when `i == 0` in the `_all_weekly_configs` loop (`pipeline.py:3614-3617`). Historical alert backfill uses rolling baselines — the freeze is for forward-looking detection of ongoing shifts, not for rewriting history.
- **`audit.py` and `backtest.py` are pre-cutover.** Both reference legacy single-file `processed.parquet` and the old `layer{1,2,3,4}_*.parquet` output names. They'll error or run against missing files unless someone rewrites them for the new output shape. README/CLAUDE.md may or may not reflect this — flagging here as the most likely source of "I ran the audit and it failed" surprises. *(Flagged per dwarf rules — contradiction with the actual cutover-era output set in `data/`.)*
- **`raw_cache` and `_pipeline_run.log`** exist alongside `raw.parquet` in `data/`. Not written by the read code paths above (probably the shipping-agent's harness / S3 sync). Outside this slice.
- **`MAX_WEEKLY_PERIODS = 26`** caps alert backfill at ~6 months. Issues older than 26 weeks past resolution get dropped (`pipeline.py:2910-2913`).
- **Frozen baseline + 6-month framework window can mismatch.** `--framework-months 6` trims the data feeding `compute_trends` / `compute_*shifts` to 6 months. Issues older than that can have a frozen baseline from a period no longer in the window — detection still works (overrides are applied at corridor level, not against raw history) but spot-checking by re-aggregating the window won't reproduce the override.
- **`shippingprovider` aliased from `dim.shippingprovider_extkey`, not from `fs.shipping_provider_id`.** The SQL specifically went through the dim table (~195 rows) rather than `map_shipment_key` (~17M rows) which carries `shippingprovider_extkey` directly — spot-checked zero divergence, big perf win (`query_mart.sql:9-12`).
