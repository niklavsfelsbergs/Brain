# D1 dwarf — CSV refactor for shipping_costs_monitoring_nextjs

**Spawned:** 2026-05-22 by Jebrim.
**Scope:** Refactor the two existing dashboard CSV paths to use the new `@/lib/csv` helper and gold-vocab column naming. Set the convention for D2/D3.
**Working dir:** `bi-analytics/NFE/dashboards/shipping_costs_monitoring_nextjs`, branch `shipping-mart-cutover`. No commits, no pushes.

## Turn 1 — recon

Read all required inputs:

- `src/lib/csv.ts` — helper exports `rowsToCsv<T>(rows, ColumnSpec<T>[])`, `downloadCsvBlob(csv, filename)`, `csvFilename(prefix, ...parts)`. `ColumnSpec` carries `key`, optional `header`, optional `value: (row) => unknown`, optional `forceQuote`. NEEDS_QUOTE regex is internal; helper handles escaping.
- `src/components/ui/TableExportButton.tsx` — props `{ onClick, label?, disabled?, className? }`. Visual cloned from current OutliersTable button; safe drop-in.
- `src/components/OutliersTable.tsx` — `downloadCsv` at L196-210 builds CSV inline; button JSX at L215-223 inline. Headers currently `["Tracking #", "Order #", "PCS #", "Date", "Country", "Cost", "Expected", "Deviation"]`.
- `src/app/api/export/route.ts` — 12-column export, raw mart names (`trackingnumber`, `shippingprovider`, `packagetype`), no `cost_source`. Force-quotes `trackingnumber`+`ordernumber` only.
- `sql/query_mart.sql` — pulls `real_shipping_cost_eur AS shipping_cost`, `expected_shipping_cost_eur AS expected_shipping_cost`, `final_shipping_cost_eur AS shipping_cost_final`. **Does not pull `cost_source`.**
- `pipeline.py` — `RAW_KEEP_COLS` (L35-53) does not include `cost_source`. `write_processed` cols list (L2435-2446) likewise omits it.

**`cost_source` status — not present in processed parquet today.** Per the project CLAUDE.md L137, `cost_source` is a valid `shipping_mart.fact_shipments` column (gold-vocab values `invoice` / `invoice_estimate` / `avg` / `expected` / NULL). Adding it is the one-line-per-stage change called for in the brief default. Plan:

1. Add `, fs.cost_source` to `sql/query_mart.sql` SELECT.
2. Add `"cost_source"` to `RAW_KEEP_COLS` and to the `write_processed` cols list.
3. Reference `cost_source` from the CSV export route SELECT (the column then resolves naturally via `processedPruned`).

No cast needed — it's a string enum, comes through fine.

**Convention being set** — CSV column names land in snake_case, gold-vocab cost terms (`invoiced_cost_eur`, `estimated_cost_eur`, `final_cost_eur`), `forceQuote: true` for tracking/order/pcs IDs. D2/D3 follow this.

## Turn 2 — pipeline + SQL edits for cost_source

Three additions:

- `sql/query_mart.sql`: added `, fs.cost_source` to the SELECT list (after `current_shipping_status`).
- `pipeline.py` L35-53: added `"cost_source"` to `RAW_KEEP_COLS`.
- `pipeline.py` L2435-2446: added `"cost_source"` to the `write_processed` cols list.

## Turn 3 — OutliersTable refactor

Replaced inline `downloadCsv` body with `rowsToCsv` + `downloadCsvBlob` + `csvFilename`. Replaced inline button JSX with `<TableExportButton onClick={downloadCsv} />`. Imports added at top.

8-col output matches the brief: `tracking_number`, `order_number`, `pcs_id`, `order_date`, `destination_country`, `invoiced_cost_eur`, `estimated_cost_eur`, `deviation_eur`. ID cols force-quoted.

## Turn 4 — /api/export refactor

Rewrote SELECT to alias columns into gold-vocab snake_case in the SQL itself, with `cost_source` added as the 12th column (13 total). Built CSV via `rowsToCsv` with explicit `ColumnSpec[]`; filename via `csvFilename("shipments", dateFrom, dateTo)`.

WHERE clauses unchanged — they reference the raw column names (`trackingnumber`, `shippingprovider`, etc.) which is what the parquet still stores; only the SELECT projects gold-vocab aliases.

## Summary

### Exact file changes

1. `bi-analytics/NFE/dashboards/shipping_costs_monitoring_nextjs/sql/query_mart.sql`
   - Added `, fs.cost_source` after `current_shipping_status` line.
2. `bi-analytics/NFE/dashboards/shipping_costs_monitoring_nextjs/pipeline.py`
   - L35-53 `RAW_KEEP_COLS`: added `"cost_source"`.
   - L2435-2446 `write_processed` cols list: added `"cost_source"`.
3. `bi-analytics/NFE/dashboards/shipping_costs_monitoring_nextjs/src/components/OutliersTable.tsx`
   - Added imports for `rowsToCsv`, `downloadCsvBlob`, `csvFilename`, `TableExportButton`.
   - Rewrote `downloadCsv` (was L196-210).
   - Replaced inline button JSX (was L215-223) with `<TableExportButton onClick={downloadCsv} />`.
4. `bi-analytics/NFE/dashboards/shipping_costs_monitoring_nextjs/src/app/api/export/route.ts`
   - Replaced `EXPORT_COLS` constant with `ColumnSpec`-driven SELECT alias list.
   - Built CSV via `rowsToCsv`; filename via `csvFilename`.
   - Filter/WHERE logic untouched.

### `cost_source` status
**Added by this dwarf** to the pipeline (SQL + `RAW_KEEP_COLS` + `write_processed`) so that `processed/<YYYY-MM>.parquet` carries it and the export route can select it. Mart column already exists per project CLAUDE.md L137. Requires a `pipeline.py --refresh-full` (or at least `--refresh`) run by the principal before the CSV's `cost_source` column will populate — until then it will be NULL in the processed parquet and surface as empty strings in the CSV.

### SQL / pipeline edge cases
- `cost_source` is a string enum, no `::float8` cast needed.
- WHERE clauses in the export route still reference raw column names (`trackingnumber`, `shippingprovider`, `packagetype`, etc.) — these are the parquet's actual stored names. Only the SELECT projects gold-vocab aliases for the CSV. This matches what the brief specified.
- `processed/*.parquet` won't have `cost_source` until pipeline re-runs. Brief said default to adding it (one-line change), which I did. Principal will need to refresh.

### OutliersTable button visual
Should be visually identical — `TableExportButton` was deliberately cloned from the inline button's class string (verified by reading `TableExportButton.tsx` L21-23 vs old inline button L217 in the original `OutliersTable.tsx`). Same `flex items-center gap-1.5 px-2.5 py-1 rounded text-[11px] ...` palette.

### Out of scope confirmed untouched
- BreakdownTab / DeviationsTable / AvgCostsHeatmap (D2 territory).
- RateChangesTable / CarrierShiftsTable / ShiftsTable / ProductShiftsTable / BenchmarksTab / CompletenessGrid (D3 territory).
- `src/lib/csv.ts` and `src/components/ui/TableExportButton.tsx` (principal-authored).
- No commits, pushes, or branch switches.
