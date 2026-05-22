# D2: CSV export for BreakdownTab, DeviationsTable, AvgCostsHeatmap

**Spawned by:** Jebrim (principal), 2026-05-22
**Branch:** `shipping-mart-cutover`
**Working dir:** `C:\Users\niklavs.felsbergs\Documents\GitHub\bi-analytics\NFE\dashboards\shipping_costs_monitoring_nextjs\`

## Brief

Add a "Download CSV" button to three table tabs using shared `@/lib/csv` helper + `TableExportButton`. Gold-vocab snake_case column convention. Mirror placement from `OutliersTable.tsx` (top-right of table area). No commits.

## Turn 1 — Reads

Loaded:

- `src/lib/csv.ts` — `rowsToCsv<T>(rows, columns)`, `downloadCsvBlob(csv, filename)`, `csvFilename(prefix, ...parts)`. `ColumnSpec<T>` = `{ key, header?, value?, forceQuote? }`.
- `src/components/ui/TableExportButton.tsx` — `<TableExportButton onClick={...} label?, disabled?, className? />`.
- `OutliersTable.tsx` lines 196–224 — placement pattern: `<div className="flex justify-end mt-2 mb-1"><TableExportButton ... /></div>`.
- Three targets: `BreakdownTab.tsx` (1434 lines), `DeviationsTable.tsx`, `AvgCostsHeatmap.tsx`.
- API routes: `/api/breakdown`, `/api/deviations`, `/api/avg-costs`.
- Types: `BreakdownRow`, `DeviationRow`, `DeviationPackageRow`, `AvgCostCell`.

## Row shape notes

- **BreakdownRow** carries no dimension-key per segment — only `dimension_value` (the leaf segment as string). The dim hierarchy is implicit from the `dims` prop and the row's nesting position. To flatten, walk the rendered tree and inject `country`/`provider`/`package`/`product` per row from the dim order.
- **DeviationRow** has `destination_country`, `shippingprovider`, `n_shipments`, `mean_deviation`, `mean_dev_pct`, `pct_over_20`, `pct_under_20`, `total_real` (invoiced sum), `total_expected` (estimated sum), `total_deviation_eur`. No corridor field — it's `country|provider`. Map: `total_real -> invoiced_cost_eur`, `total_expected -> estimated_cost_eur`, `total_deviation_eur -> deviation_eur`, `mean_dev_pct -> deviation_pct`.
- **AvgCostCell** has `destination_country`, `shippingprovider`, `week_start`, `avg_cost_per_order` (final), `avg_real`, `avg_expected`, `avg_diff`, `avg_diff_pct`, `n_orders`. Going with long format (one row per cell) so downstream consumers can reshape.

## Turn 2 — Edits

### DeviationsTable.tsx

- Added imports for `rowsToCsv`, `downloadCsvBlob`, `csvFilename`, `ColumnSpec`, `TableExportButton`.
- Added `downloadCsv()` callback inside the component after the loading guard. Walks `sorted` (the in-component sorted view of `rows`), 10 columns:
  - `destination_country`, `shippingprovider`, `shipments`, `mean_deviation_eur`, `mean_deviation_pct`, `pct_over_20`, `pct_under_20`, `invoiced_cost_eur`, `estimated_cost_eur`, `deviation_eur`.
- Wrapped the existing `<div className="overflow-auto ...">` in a parent `<div>` and added a `<TableExportButton>` row above it with `flex justify-end mt-2 mb-1`.
- Filename: `csvFilename("deviations", dateRange)` where `dateRange = "from_to"` if both present.
- File: `src/components/DeviationsTable.tsx`. Diff regions: imports (~lines 8-11), downloadCsv + button + wrapping div (~lines 127-160).

Note: did not include `corridor` as a single concatenated column — kept `destination_country` + `shippingprovider` as two columns since the underlying API and `DeviationRow` don't have a corridor field. Cleaner for downstream consumers.

Note: expanded-row package data (`DeviationPackageRow` per-corridor breakdown) is NOT included in the export — it's fetched only on row-click and is keyed to one corridor at a time. Scope per brief was the main table, so packages skipped.

### AvgCostsHeatmap.tsx

- Added same imports.
- Defined `METRIC_KEY: Record<Metric, string>` mapping the `Metric` union to snake_case column names: `final -> final_cost_eur`, `invoiced -> invoiced_cost_eur`, `estimated -> estimated_cost_eur`, `diff -> diff_eur`, `diff_pct -> diff_pct`.
- Added `downloadCsv()` callback. Long-format export: one row per (corridor, week) cell. Columns:
  - `destination_country`, `shippingprovider`, `week_start` (force-quoted as it's a date string), `metric` (the active metric's snake_case name), `value` (computed via `getValue`), then all per-cell metric values broken out (`final_cost_eur`, `invoiced_cost_eur`, `estimated_cost_eur`, `diff_eur`, `diff_pct`), and `n_orders`.
- Filters `rows` to only cells in the visible window (`corridors` ∩ `weeks` after the recent-activity filter) before exporting.
- Button placed between controls row and heatmap table, `flex justify-end mt-2 mb-1`.
- Filename: `csvFilename("avg_costs", metricKey, dateRange)` where `dateRange = "${gran}-${periods}_to_${filters.to}"`. The heatmap computes its own window from `gran + periods` ending at `filters.to`, so I encoded that rather than a from/to pair.
- File: `src/components/AvgCostsHeatmap.tsx`. Diff regions: imports (~lines 5-8), METRIC_KEY + downloadCsv (~lines 183-220), button (~lines 261-263).

Surprise: `AvgCostsHeatmap`'s `filterQS` doesn't include `from`/`to` — the route ignores date range and uses its own period window. Reflected this in the filename construction.

### BreakdownTab.tsx

- Added same imports.
- Defined `DIM_CSV_KEY: Record<DimensionKey, string>` mapping `package -> package_type` (snake_case rename per convention) and others 1:1.
- Added `downloadCsv()` callback. Walks the rendered tree in render order:
  1. Total row (level -1, no dim values).
  2. Sorted L0 rows via `sorted1` (preserves the stable row order the UI uses).
  3. For each expanded composite key in `expanded`, descends into `childData[key]` and uses `sortRows` to match UI sort.
  - Carries `ancestorDims` down the tree so each row's dim columns are filled in based on the active `dims` hierarchy.
  - Tracks parent's `total_cost` and `total_cost_b` so `ctb` and `base_ctb` get computed identically to the UI.
- Columns: `level`, then dim columns in active dim order (`forceQuote: true` since some dim values like postal codes start with digits/contain commas), then:
  - `shipments`, `total_cost_eur`, `total_cost_full_eur`, `total_cost_baseline_eur`, `avg_cost_eur`, `avg_cost_baseline_eur`, `delta_eur`, `pct_change`, `impact_eur`, `price`, `mix`, `invoiced_pct`, `share_pct`, `share_pct_baseline`, `ctb`, `base_ctb`, `real_cost_quota`, `cost_quota`, `cost_quota_baseline`, `cost_source` (=current `costBasis`: "final" | "invoiced").
- Button placed between the controls header and the table panel, mirroring the OutliersTable pattern.
- Filename: `csvFilename("breakdown", dimensionOrder, dateRange)` where `dimensionOrder = dims.join("-")` (e.g. `"country-provider-package"`) and `dateRange = "from_to"`.
- File: `src/components/BreakdownTab.tsx`. Diff regions: imports (~lines 7-9), downloadCsv (~lines 795-892), button (~lines 1379-1381).

Things I had to interpret:

- Brief's column list mentioned `ctb` and `base_ctb` (computed) plus `delta_eur` and `pct_change`. UI also has `cost_quota` / `real_cost_quota` / baseline variants which the brief said could be included optionally — included them all.
- `BreakdownRow` has no `cost_source` field but the dashboard tracks `costBasis` as UI state (`"final" | "invoiced"`). Emitted it as a constant column per gold-vocab convention so the consumer knows which basis the numbers reflect.
- `dimension_value` on `BreakdownRow` is just the segment at that level; not the full corridor. The walker rebuilds dim context from ancestor stack.

## Turn 3 — Verification

Ran `npx tsc --noEmit` from the dashboard root. EXIT:0. No type errors.

ESLint not runnable standalone (project uses Next's lint pipeline; standalone eslint v10 couldn't find the project's old-format config). Not a blocker — typecheck is clean and no new lint rules touched.

## Summary

| Tab | File | Columns exported | Filename pattern |
|---|---|---|---|
| Deviations | `src/components/DeviationsTable.tsx` | 10: country/provider + 4 stats + invoiced/estimated/deviation cost cols | `deviations_<from>_<to>.csv` |
| Avg Costs Heatmap | `src/components/AvgCostsHeatmap.tsx` | 11 (long format): corridor + week + active metric + all metric values + n_orders | `avg_costs_<metric>_<gran>-<periods>_to_<to>.csv` |
| Breakdown | `src/components/BreakdownTab.tsx` | level + dim cols (variable per `dims`) + ~20 numeric cols + cost_source | `breakdown_<dim-order>_<from>_<to>.csv` |

Files edited (no commits):

- `src/components/DeviationsTable.tsx`
- `src/components/AvgCostsHeatmap.tsx`
- `src/components/BreakdownTab.tsx`

No edits to helpers (`src/lib/csv.ts`, `src/components/ui/TableExportButton.tsx`) — used as-is per scope.

Flagged for principal:

- Deviations: dropped `corridor` concatenation. If a single `corridor` column is preferred, easy add via a synthetic `value: (r) => `${r.destination_country}|${r.shippingprovider}``.
- Deviations: expanded-row package-type breakdown is not exported. If desired, that's a separate per-corridor CSV button inside the expanded panel — out of D2 scope as written.
- AvgCostsHeatmap: chose long format (one row per cell). Wide format (provider × week matrix) was the alternative — flagged in brief as a judgment call.
- Breakdown: included `cost_source` constant column reflecting current `costBasis` UI toggle. If a separate provenance/route flag from the mart is wanted at row level, that field isn't currently in `BreakdownRow` shape.

