# Shipping-costs dashboard — CSV export architecture

**Status:** draft (harvested [[S030_2026-05-22_dashboard-gold-cutover|S030]], 2026-05-22).
**Repo:** `bi-analytics/NFE/dashboards/shipping_costs_monitoring_nextjs/` on branch `shipping-mart-cutover`.

## What landed

Unified CSV export across every data-bearing table in the dashboard. Two-piece foundation + button component + per-table export functions.

### Foundation (principal-authored mid-session)

- **`src/lib/csv.ts`** — shared helper module:
  - `rowsToCsv<T>(rows, columns)` — typed CSV generator. RFC-4180-ish: auto-quotes cells containing `",\n\r`. Each column descriptor has `key`, `header`, optional `forceQuote: true` for ID-shaped columns (preserves leading zeros / scientific-notation collapse in Excel).
  - `downloadCsvBlob(csv, filename)` — triggers browser download via Blob URL.
  - `csvFilename(prefix, ...parts)` — composes `prefix_part1_part2.csv` filenames.
- **`src/components/ui/TableExportButton.tsx`** — standard button component (visual cloned from the pre-existing OutliersTable button). One JSX call, props: `onClick`, `disabled`.

### Coverage (D1 + D2 + D3 dwarves)

| Component / route | Cols | Filename pattern |
|---|---|---|
| `OutliersTable.tsx` | 8 | (existing, refactored to helper) |
| `/api/export/route.ts` | 13 | `shipments_<from>_<to>.csv` (+ `cost_source` added) |
| `BreakdownTab.tsx` | dynamic per `dims` | `breakdown_<dim-order>_<from>_<to>.csv` |
| `DeviationsTable.tsx` | 10 | `deviations_<from>_<to>.csv` |
| `AvgCostsHeatmap.tsx` | long fmt | `avg_costs_<metric>_<gran>-<periods>_to_<to>.csv` |
| `RateChangesTable.tsx` | 14 | `rate_changes_<from>_<to>.csv` |
| `CarrierShiftsTable.tsx` | 17 | `carrier_shifts_<from>_<to>.csv` |
| `ShiftsTable.tsx` | 18 | `routing_shifts_<from>_<to>.csv` |
| `ProductShiftsTable.tsx` | 19 | `product_shifts_<from>_<to>.csv` |
| `BenchmarksTab.tsx` | 22 | `benchmarks_<from>_<to>.csv` |
| `CompletenessGrid.tsx` | 9 | `completeness_<gran>_<firstWeek>_<lastWeek>.csv` |

13 components/routes total. 15 files modified across the 4 commits.

## Conventions (locked through this cutover)

- **Column names are snake_case in CSV** even where the UI uses camelCase or other casing. `invoiced_cost_eur`, `estimated_cost_eur`, `shipment_count`, etc.
- **Cost vocabulary follows the gold contract:** `final` / `invoiced` / `estimated` (not `real_expected` / `real` / `expected`). Data-column names like `avg_cost_real` are kept in API contracts but renamed in CSV output.
- **`cost_source` column** is included in `/api/export` (the only path with per-row provenance). Tabs whose rows are aggregates across mixed-basis input do *not* synthesize a `cost_source` value — that would mislead. BreakdownTab emits a constant reflecting the UI's `costBasis` toggle.
- **`forceQuote`** is used sparingly — only for ID-shaped columns (none currently in the dashboard's CSV outputs after D3 review).
- **Filenames carry the period bounds** (`<from>_<to>`) so the file is self-describing without opening it.

## Open / non-shipped variants

- **Deviations expanded-row package breakdown** — not exported. Would need a per-corridor button inside the expanded panel.
- **AvgCosts wide format** — could be added as an option; currently long-only.
- **CompletenessGrid per-cell `/api/export` link** — pre-existing, kept; the new full-grid button is additive.

## Cross-cutting

The shared `csv.ts` helper means future tables with new data shapes can ship a Download CSV button in 5-10 LOC (define columns array + filename + onClick). The button component (`TableExportButton`) keeps visual consistency without per-call styling.

## Anchor turns

[[S030_2026-05-22_dashboard-gold-cutover|S030]] / T7-T10 of `quest-log/completed/S030_2026-05-22_dashboard-gold-cutover.md`, dwarf siblings `S030_2026-05-22_d{1,2,3}_csv-*.md`. Commits `6233b4e`, `1d4004a`, `93a51ba` on `bi-analytics` `shipping-mart-cutover`.
