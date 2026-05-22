# D1 — Dashboard gold cutover: SQL + pipeline tranche

**Spawned by:** Jebrim principal, 2026-05-22.
**Scope:** Phases A (`sql/query_mart.sql`), B (`sql/query_mart_items.sql`), C (`pipeline.py:552-564`) of the dashboard gold cutover. Mechanical apply — decisions locked in `inventory/dashboard-gold-cutover-resume.md`.
**Branch:** `shipping-mart-cutover` (do not switch, do not commit, do not push).
**Pre-cutover baseline:** `meta.json` → `total_rows = 13,131,306`, `date_bounds = 2024-01-01..2026-05-21`. Last pipeline run completed in 112.9s.

## Turn log

- **T1** — `sql/query_mart.sql` rewritten end-to-end. Schemas flipped (`enterprise_silver.*` → `shipping_mart.*` on `fact_shipments` and `fact_shipment_cost_summary`); `dim_shipping_providers` JOIN dropped (alias preserved by reading `fs.shippingprovider_extkey` directly); ORWO inline CASE + `orwo_dhl_base`/`orwo_ups_base` CTEs dropped (expected col reduced to `fs.expected_shipping_cost_eur::float8 AS expected_shipping_cost`); Picturator-Wolfen dedup filter dropped; `order_source` CASE replaced with `fs.source_system AS order_source`. Header comment refreshed to match the new shape. File went from 163 → 92 lines.
- **T2** — `sql/query_mart_items.sql` schemas flipped (`enterprise_silver.fact_shipment_orderitems` → `shipping_mart.fact_shipment_orderitems`; `enterprise_silver.fact_shipments` → `shipping_mart.fact_shipments`). `dw.dim_products` LEFT JOIN preserved as-is per locked decision (waiting on `shop_order_group` migration into the mart).
- **T3** — `pipeline.py:552-564` `transform()` simplified: removed the `pl.coalesce(pl.when(...).then(shipping_cost_final), expected_shipping_cost)` fallback; `cost_for_routing` is now `pl.col("shipping_cost_final").cast(pl.Float64)` directly. Comment rewritten to match. `has_cost` / `has_expected` flags unchanged. The block shrank from 13 → 8 lines (lines 552-559 in the new file).
- **T4** — Spot-checked all 14 other `cost_for_routing` references in `pipeline.py`. All NULL-safe: `_cost_config` returns the col with a documented `is_not_null()` filter convention (line 237); `compute_corridor_costs` filters via `cost_filter = pl.col(cost_col).is_not_null()` (615); `compute_layer2` uses `has_col=None` matching the same convention (753-754); vanished-corridor mean filters NULLs (1478); `_write_outlier_thresholds` filters NULLs (2296); `daily.parquet` `sum_routing` uses `.sum()` which skips NULLs by default (2331); `SUMMARY_COLS` references at 2367/2443/3531/3687 are just column-name lists. No NULL-guard gaps. Nothing flagged for principal attention.

## Summary

**Files touched:**

- `bi-analytics/NFE/dashboards/shipping_costs_monitoring_nextjs/sql/query_mart.sql` — rewritten end-to-end. Whole-file replace (163 → 92 lines). The five Phase A edits land together: schema flips on `fact_shipments` + `fact_shipment_cost_summary`, `dim_shipping_providers` JOIN dropped (alias preserved via `fs.shippingprovider_extkey`), `orwo_dhl_base` / `orwo_ups_base` CTEs and inline ORWO CASE dropped (expected col now `fs.expected_shipping_cost_eur::float8`), Picturator-Wolfen dedup filter dropped, `order_source` CASE replaced with `fs.source_system`. Header comment updated.
- `bi-analytics/NFE/dashboards/shipping_costs_monitoring_nextjs/sql/query_mart_items.sql` — two-line edit on lines 17-18 (`FROM` and `JOIN` schemas flipped to `shipping_mart.*`). `dw.dim_products` LEFT JOIN preserved.
- `bi-analytics/NFE/dashboards/shipping_costs_monitoring_nextjs/pipeline.py` — `transform()` block at lines 552-564 (pre-edit) replaced with lines 552-559 (post-edit). `cost_for_routing` simplified from coalesce-with-pipeline-fallback to `pl.col("shipping_cost_final").cast(pl.Float64)`. Comment rewritten to reflect the new contract.

**Surprises:**

- None on Phase A line offsets — the resume-doc line numbers (36-120 for ORWO CASE, 159-162 for Wolfen filter, 128-131 for order_source CASE) all matched the file exactly.
- The `dim_shipping_providers` JOIN had no other references in `query_mart.sql` beyond the alias — clean to drop. No lingering `dim.*` references after edit.
- `expected_shipping_cost` reference at line 87 of the pre-edit SQL (inside the COALESCE) collapsed cleanly to the bare column. No related downstream references to the ORWO fallback existed outside the SQL.
- Picturator-Wolfen filter dropped at the end of the WHERE clause; the trailing newline is preserved. No other `source_system = 'Picturator'` filters remain in the file.

**Skipped / flagged:**

- Nothing skipped. All three phases applied as specified.
- No principal attention needed on NULL-guards in `pipeline.py` consumers of `cost_for_routing` — all sites already gate on `is_not_null()` or use NULL-skipping aggregations.

**Pre-cutover baseline (for principal's row-count smoke check):**

- `data/meta.json` last run: `total_rows = 13,131,306`, `date_bounds = 2024-01-01..2026-05-21`, current_period_start `2026-05-11`, baseline_start `2026-04-06`. Last pipeline completed in 112.9s.
- `_pipeline_run.log` tail: 2,485 alerts (1,395 early_warning, 1,090 confirmed) across 21 periods; 181 issues (49 active, 132 resolved, 5 suppressed); daily summary 1,281,937 rows; daily_product 2,700,034 rows; filter_combos 140,919 rows.
- Post-cutover row count should be **higher** by the previously-deduped Picturator-Wolfen count (filter removed, expecting more shipments through).
- Active-issue churn expected on first post-cutover run: ORWO-non-DHL/UPS corridors that previously had a SQL-level expected fallback will now show NULL `expected_shipping_cost` and fall through to `final_shipping_cost_eur` (mart's `COALESCE(real, expected, avg)`) or stay uncosted. `cost_for_routing` coverage may drop on those corridors. Principal's Phase F (`issues.parquet` reset) handles the resulting churn.
