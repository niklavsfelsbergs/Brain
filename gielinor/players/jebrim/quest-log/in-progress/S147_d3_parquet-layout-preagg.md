# [[S147_dcb495a7_scm-perf-audit|S147]] D3 — parquet layout & pipeline pre-aggregation

**Verdict:** The parquet tiers are written with stock polars defaults — no sort, no row-group tuning, no statistics-friendly ordering — so within-file row-group pushdown does nothing for the dominant `order_date` range WHERE; the *only* working prune is `processed`'s month-by-filename. Biggest serving leverage is two new pipeline-baked tiers (a transit roll-up and a deviation-trend roll-up) that retire the per-shipment `processed` scan off the entire Transit tab and the deviations trend — both pure pipeline additions, no serving-correctness risk.

Read root (post-fix == deployed main): `_scm-mem-fix/NFE/dashboards/shipping_costs_monitoring_nextjs/`. Read-only audit; no app file edited.

---

## Current layout facts

**Write path is all polars defaults — every `write_parquet` is bare.**
- `daily.parquet` — `pipeline.py:2419` `daily.write_parquet(DATA / "daily.parquet")`. No `row_group_size`, no `compression`, no sort. Grain `(order_date, destination_country, shippingprovider, packagetype, production_site, shop, order_source)` (`pipeline.py:2386`).
- `daily_product.parquet` — written by DuckDB `COPY ... (FORMAT PARQUET)` with `preserve_insertion_order=false` (`pipeline.py:2466,2505`), so output row order is explicitly *unordered*. No `ORDER BY`, no row-group hint.
- `processed/<YYYY-MM>.parquet` — `pipeline.py:2566-2569`. Partitioned by month via `out.filter(month_start==m).write_parquet(...)`. Within each month file: **no sort** (the source `df` order is whatever `transform`/reload produced), bare `write_parquet`. ~241MB glob, per-shipment grain (~40 cols incl. `transit_time_days`, `current_shipping_status`, buckets, `shippingzipcode`, dims) — col list `pipeline.py:2526-2538`.
- All summary tiers (`deviations_summary`, `outlier_thresholds`, `corridor_trends`, `alerts`, `issues`, `filter_combos`) — same bare `write_parquet`.
- `raw.parquet` join output explicitly notes order is *not* relied on (`pipeline.py:524-525`, `preserve_insertion_order=false`).

**Serving read path (`src/lib/db.ts`).**
- `PARQUET` map `db.ts:145-154`; `processed: path("processed/*.parquet")` `db.ts:148` (the full glob).
- `processedPruned(from,to)` `db.ts:170-216` — enumerates the `YYYY-MM` months overlapping the range and emits `read_parquet([...])` over only the existing month files (`db.ts:200-215`). **This filename-level month prune is the only pruning that actually fires.** Missing-bounds fallback now bounded to a 24-month trailing window + warns (`db.ts:180-193`); inverted-range swap `db.ts:199`.
- `dailyTier()` `db.ts:222-229` picks the lightest tier: `daily` (no SOG/pkg-both), `daily_product` (SOG active), `processed` only when **both** packagetype AND SOG filters are active.
- `processedAsDaily()` `db.ts:234-263` re-aggregates `processedPruned` to daily grain on the fly when forced to `processed`.
- DuckDB serving conn: `memory_limit` (default 4GB), `threads=2`, disk `temp_directory`, `preserve_insertion_order=false` (`db.ts:35-41`) — the [[S146_f20d7744_scm-serving-memory-review|S146]] OOM cap.

---

## Pushdown gaps (ranked)

1. **No `order_date` sort before write → zero row-group min/max pruning inside files.** Parquet writers record per-row-group column statistics, and DuckDB *will* skip row groups whose `order_date` min/max miss the WHERE range — but only if the data is **clustered** by `order_date`. The pipeline never sorts, so every row group in a month file spans (roughly) the whole month, and a query for "last 7 days" still decompresses every row group in the current month's file. The month-by-filename prune gets you to one ~month file; sort-on-write would get you to a handful of row groups *within* it. **Serving-invisible, pipeline-only fix.** Effort **S** (one `.sort("order_date")` per partition before `write_parquet`, or `ORDER BY order_date` in the DuckDB COPY for `daily_product`).

2. **Carrier / packagetype predicates get no help at all.** The typical WHERE is `order_date BETWEEN … AND (destination_country|shippingprovider|packagetype) IN (…)`. With no secondary sort and default row-group size, carrier/country filters scan every row group. A composite sort `(order_date, shippingprovider)` (or zone-map-friendly ordering) would let DuckDB skip row groups for single-carrier views (common on the carrier-drill routes). Effort **S–M** (sort key choice is a tradeoff: `order_date` first preserves the date prune; carrier-first would help carrier views but weaken date pruning — recommend `order_date, shippingprovider`).

3. **Default row-group size is large relative to the prune you want.** polars defaults to a big row-group (512K–1M rows depending on version); a `processed` month file with a few hundred K rows may be *one* row group, so even a perfect sort can't prune sub-file. Pair the sort with a smaller `row_group_size` (e.g. 100–128K) so per-group min/max are tight enough to skip. Effort **S**, only meaningful once sorted (gap 1 must land first).

4. **`processedPruned` month-set is recomputed per request, in JS, with `existsSync` per month** (`db.ts:211-212`). Minor, but on a wide range it stats N files every call (cache mitigates). Not a parquet-layout issue — noted for completeness; leave it.

---

## Pre-agg / layout-change candidates (ranked by leverage)

**P1 — Transit roll-up tier (`transit_daily.parquet`). HIGHEST LEVERAGE. Pipeline build.**
- Retires the per-shipment `processed` scan off the **entire Transit tab**: `transit/heatmap` (`route.ts:73` GROUP BY country,provider), `transit/trend` (`route.ts:92`), `transit/kpis` (`route.ts:90`), `transit/completeness` (`route.ts:79`). All four scan `processedPruned` purely to aggregate `transit_time_days` / `transit_time_business_days` / `current_shipping_status` over dim+date grain.
- The pipeline **already flags this**: `pipeline.py:50-52` — *"Lead-time + status fields … Pulled raw for now; aggregations into daily.parquet land when the lead-time UI is designed."* The UI now exists and still hits per-shipment.
- **Caveat (the reason it's a new tier, not a column on `daily`):** heatmap/trend/kpis use `quantile_cont(transit_time_days, 0.50/0.85/0.95)` (`transit/heatmap/route.ts:66-72`). Percentiles are **not summable**, so you cannot pre-sum them into `daily`. Options: (a) bake a transit tier at a coarser grain that still serves the percentile *approximately* via per-(date,country,provider) reservoir/t-digest — complex; or (b) bake daily per-(date,country,provider,packagetype) **histogram-bin counts** of `transit_time_days` (0..14+ bins, the same `LEAST(FLOOR(x),14)` bucketing `transit/histogram/route.ts:77`) plus delivered/exception/with-ts counts — percentiles then computed off the binned CDF at serve time (good to ±1 day, fine for a lead-time dashboard). **Recommend (b):** it also retires `transit/histogram` (currently the one route that genuinely needs per-shipment grain). Effort **M** (new pipeline step + 4-5 route rewrites to read bins).

**P2 — Deviation trend roll-up. Pipeline + serving. MEDIUM.**
- `deviations_summary.parquet` already exists at grain `(order_date, country, provider, packagetype)` with `sum_deviation`, `n_over_20`, etc. (`pipeline.py:2344-2354`). But the deviations route's **trend** block still scans `processedPruned` (`deviations/route.ts:211,219` GROUP BY `${tc}` over a wide trend window) instead of rolling up the existing summary tier. The summary tier carries everything the trend needs (it's summable). **Serving-only fix** — point the trend block at `deviations_summary` and `DATE_TRUNC`/roll-up there. Effort **S** (no pipeline change; the tier exists).

**P3 — `daily` already retires most routes; verify no route bypasses it. LOW / hygiene.**
- `overview`, `trends`, `avg-costs`, `country-trends`, `packagetype-trends`, `trend-shares`, `generic-trend`, `completeness` correctly route through `dailyTier`/`dailyTierExpr` or `daily`-tier sources. The genuine per-shipment holdouts beyond transit are: `outliers` (needs `trackingnumber`-grain rows + `PERCENTILE_CONT`, `outliers/route.ts:94` — inherently per-shipment, leave on `processed`), `export` (per-shipment CSV, must stay, `export/route.ts:159`), `breakdown`/`breakdown-sparklines`/`cost-drivers-top`/`rate-changes` (drill to shipment grain / SOG UNNEST — `processed` is correct for these, though they'd benefit most from the gap-1 sort). No mis-routing found.

**P4 — Outlier route could read the pre-baked threshold tier for its p99.5. LOW.**
- `outlier_thresholds.parquet` (all-time p99.5 per provider, `pipeline.py:2364-2372`) already exists, but `outliers/route.ts:94` recomputes `PERCENTILE_CONT(0.995)` over `processedPruned` for the range-scoped path. For the **global** scope the pre-baked tier is the intended replacement (per the pipeline docstring `pipeline.py:2361`); confirm the global path uses it. Range-scoped percentile still needs the scan. Effort **S** (serving-only, only the global branch).

---

## Distinguish serving-only vs pipeline

- **Serving-only (in this audit's commit scope):** P2 (deviation trend → existing summary tier), P4 (outliers global → existing threshold tier). Both reuse tiers the pipeline already bakes.
- **Pipeline build (outside this commit's scope — recommendations for a pipeline session):** P1 (new transit roll-up tier), gaps 1–3 (sort-on-write + row-group sizing). These touch `pipeline.py` write functions and require a refresh run + S3 re-sync (`docker/refresh.sh`).

---

## Needs live measurement

- **Row-group count per `processed` month file.** Confirm gap-1/3 leverage: `SELECT … FROM parquet_metadata('processed/2026-05.parquet')` — if a month file is a single row group, sort-on-write alone won't prune sub-file and you *must* pair it with `row_group_size` (gap 3). If already multi-group, sort is the cheaper win.
- **Actual per-route latency + bytes scanned.** Run `EXPLAIN ANALYZE` on the transit heatmap/trend queries against live `processed` to quantify P1's payoff (rows scanned, time) vs the binned tier. The audit asserts the scan is the cost; measure it.
- **Sort-key tradeoff (gap 2).** Measure date-range-only vs carrier-filtered query mix in real traffic before committing to `(order_date, shippingprovider)` — if carrier filters are rare, `order_date` alone is simpler and loses nothing.
- **`daily_product` / `processed` file sizes after a sort.** zstd on sorted (clustered) data usually compresses *better*; confirm the new files aren't larger and that the S3 sync stays within the refresh window.
- **Percentile fidelity of the binned transit tier (P1 option b).** Validate binned-CDF p50/p85/p95 vs exact `quantile_cont` on a live month — confirm ±1 day is acceptable for the Transit tab before retiring per-shipment.
