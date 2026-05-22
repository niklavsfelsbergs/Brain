# D3 — CSV export buttons on six smaller table tabs

**Spawned:** 2026-05-22, dwarf under Jebrim.
**Working dir:** `bi-analytics/NFE/dashboards/shipping_costs_monitoring_nextjs/`
**Branch:** `shipping-mart-cutover` (no commits).

## Turn 1 — scope load and column planning

Read `src/lib/csv.ts`, `src/components/ui/TableExportButton.tsx`, `OutliersTable.tsx`
196–224, and all six target components. Read row interfaces in
`src/lib/types.ts` (RateChangeRow, CarrierShiftRow, ShiftRow, ProductShiftRow,
CompletenessRow). No `cost_source` field anywhere in scope, so omitting that
column. Cost columns map to `invoiced_cost_eur` only where a row genuinely
distinguishes invoiced from estimated — otherwise rendered numbers map to the
generic `avg_cost_eur` style names consistent with what the UI labels them.

**Mapping decisions per tab.**

- **RateChangesTable** — gold-vocab not directly applicable since `avg_cost` is
  a rendered period average (not invoiced/estimated/final). Using
  `avg_cost_eur` / `avg_cost_baseline_eur` etc. Filename uses
  `filters.baselineFrom` … `filters.to` as date range.
- **CarrierShiftsTable / ShiftsTable / ProductShiftsTable** — same column
  family (gainer_cost, from_cost, premium, eur_impact). `gainer_cost_eur`,
  `from_cost_eur`, `cost_premium_eur`, `eur_impact`. From-providers list
  flattened with `|` separator.
- **BenchmarksTab** — switching opportunities; expose current → target,
  realizable + raw weekly savings, confidence, effort, risk flags joined by
  `|`. Date range from filters.
- **CompletenessGrid** — long-format export from `rows` (already the
  raw `CompletenessRow[]` before pivot). Columns: provider, week_start,
  total, n_real, n_no_cost, total_cost_eur, real_cost_eur, real_cost_pct,
  coverage_pct.

Filename date-range parts use `filters.from`_`filters.to` per spec.

## Turn 2 — edits applied

All six components edited. `npx tsc --noEmit` passes (exit 0). Branch left dirty
on `shipping-mart-cutover`; no commits.

### Per-tab summary

| Component | Lines touched | Row source | Filename pattern | Columns |
|---|---|---|---|---|
| `RateChangesTable.tsx` | import line ~7, downloadCsv inserted after `sorted` memo (~155), button before table container (~282) | `sorted` (RateChangeRow[]) | `rate_changes_<from>_<to>.csv` | destination_country, shippingprovider, packagetype, n_shipments, n_shipments_baseline, avg_cost_eur, avg_cost_baseline_eur, delta_eur, impact_eur, avg_weight_kg, avg_weight_baseline_kg, cost_per_kg_eur, cost_per_kg_baseline_eur, invoiced_pct |
| `CarrierShiftsTable.tsx` | import ~7, downloadCsv after `rowKey` (~119), button at top of return (~155) | `sorted` (CarrierShiftRow[]) | `carrier_shifts_<from>_<to>.csv` | destination_country, shippingprovider, counterparts, counterpart_direction, total_vol, baseline_share_pct, current_share_pct, share_delta_pp, shifted_vol, gainer_cost_eur, from_cost_eur, cost_premium_eur, cost_premium_pct, eur_impact, invoiced_pct, trend_confirmed, low_baseline_vol |
| `ShiftsTable.tsx` (Routing) | import ~7, downloadCsv after `rowKey` (~119), button at top of return (~152) | `sorted` (ShiftRow[]) | `routing_shifts_<from>_<to>.csv` | destination_country, packagetype, shippingprovider, counterparts, counterpart_direction, total_vol, baseline_share_pct, current_share_pct, share_delta_pp, shifted_vol, gainer_cost_eur, from_cost_eur, cost_premium_eur, cost_premium_pct, eur_impact, invoiced_pct, trend_confirmed, low_baseline_vol |
| `ProductShiftsTable.tsx` | import ~7, downloadCsv after `rowKey` (~129), button on basket-control row (~165) | `sorted` (ProductShiftRow[]) | `product_shifts_<from>_<to>.csv` | destination_country, product, basket_size, shippingprovider, counterparts, counterpart_direction, total_vol, baseline_share_pct, current_share_pct, share_delta_pp, shifted_vol, gainer_cost_eur, from_cost_eur, cost_premium_eur, cost_premium_pct, eur_impact, invoiced_pct, trend_confirmed, low_baseline_vol |
| `BenchmarksTab.tsx` | import ~7, downloadCsv before `toggleEffort` (~145), button after pill bar (~240) | `filtered` (BenchmarkOpportunity[]) | `benchmarks_<from>_<to>.csv` | priority_band, priority_score, destination_country, packagetype, current_provider, target_provider, n_shipments, alt_shipments, total_corridor_shipments, current_avg_cost_eur, target_avg_cost_eur, savings_per_shipment_eur, benchmark_gap_eur, benchmark_pct, recommended_switch_pct, estimated_switched_shipments, expected_weekly_savings_eur, realizable_weekly_savings_eur, confidence, effort, risk_flags, rationale |
| `CompletenessGrid.tsx` | import ~9, downloadCsv before `handleCellEnter` (~338), button on controls row (~422) | raw `rows` (CompletenessRow[]) filtered to visible providers | `completeness_<gran>_<firstWeek>_<lastWeek>.csv` | provider (header overrides shippingprovider key), week_start, total_shipments, n_invoiced, n_no_cost, total_cost_eur, invoiced_cost_eur, invoiced_cost_pct, coverage_pct |

Six components, six rendered-row sources used (one each, no API re-fetches).

### Notes / decisions

- **No `cost_source` column.** None of these row interfaces expose
  `cost_source`. The shift family's cost columns are `gainer_cost`/`from_cost`
  which are *averages* across mixed-basis rows, not invoiced-vs-estimated
  picks, so `invoiced_cost_eur` would be misleading. Used `gainer_cost_eur` /
  `from_cost_eur` as the snake_case rendering of the visible column labels.
- **No ID-shaped columns** in any of these tabs (no tracking_number /
  order_number). All six can omit `forceQuote`. The shifts tables do have
  long `counterparts` strings which trigger auto-quoting via the regex
  (commas/pipes), so no explicit force needed there either.
- **`counterparts` joined with `|`** rather than `, ` to keep CSV consumers
  happy. Direction (from/to) encoded as a separate `counterpart_direction`
  column rather than baked into the providers string (matches the
  rendered "From: …" / "To: …" prefix in the UI).
- **CompletenessGrid uses long-format** as briefed — one row per
  (provider, week) cell, taken from the raw `rows` state filtered to providers
  that pass the min-shipments threshold. Excludes the synthesized "Total" row
  since it's a UI rollup, not source data.
- **BenchmarksTab exports filtered rows** (the priority/effort/confidence
  pills) rather than `opportunities`. Matches what the user sees.
- **Filename date range** uses `filters.from`/`filters.to` everywhere except
  Completeness, which uses the actual first/last week boundaries from the
  loaded data (the tab has its own gran/periods controls, not the global
  date filter). Completeness filename also includes the `gran` (mo/wk).
- **Cost columns kept as raw numbers** (no formatting). The user can format
  in Excel; CSV stays machine-readable.

### Surprises / out-of-scope flags

- The shift-family rows have `cost_per_kg`, `baseline_cost_per_kg`,
  `gainer_weight`, `weight_premium`, `weight_norm_impact` fields that the UI
  doesn't render in these tabs. Per "expose the same data the user already
  sees in the table", omitted. If principal wants them exposed via CSV, easy
  add later.
- BenchmarksTab has no shared `filters.from`/`filters.to` date-range usage in
  the rendered UI but the date is in scope of the filter. Filename gets it
  consistently with the rest.
- CompletenessGrid's existing per-cell "Click to export" tooltip path is
  untouched — it uses `/api/export` for the raw shipment list of one
  (provider, week) cell, which is the D1 territory. The new whole-grid
  Download CSV is additive.

### Out-of-scope / not done

- No commits, no pushes (per brief).
- `src/lib/csv.ts` and `src/components/ui/TableExportButton.tsx` not modified
  (principal-authored).
- AlertsTab / ChangelogTab / OutliersTable / BreakdownTab / DeviationsTable /
  AvgCostsHeatmap not touched (other dwarves' scope or out of scope).

