# Dashboard gold cutover

**Opened:** 2026-05-22 (Jebrim, principal).
**Resume file:** `players/jebrim/inventory/dashboard-gold-cutover-resume.md`.
**Repo / branch:** `bi-analytics/` on `shipping-mart-cutover`.
**Companion:** S028 (`bi-analytics-main 7e74670`) landed the agent-side cutover. This dashboard cutover brings the dashboard into alignment.

## T1 — quest opened, dwarves spawned (principal)

Read inventory resume + S023/S026/agent-side context. Confirmed scope is locked (Niklavs framed three points + answered clarifications in S028 — decisions in resume file's Scope section).

Decomposition: three dwarves in parallel.

- **D1** — SQL + pipeline tranche (Phases A + B + C). Sibling: `2026-05-22_d1_dashboard-cutover-sql-pipeline.md`.
- **D2** — UI label rename + URL shim (Phase D). Sibling: `2026-05-22_d2_dashboard-cutover-ui-labels.md`.
- **D3** — audit + backtest rewrite (Phase G). Sibling: `2026-05-22_d3_dashboard-cutover-audit-backtest.md`.

Principal keeps phases E (doc one-liner), F (`issues.parquet` reset), H (`pytest`), all smoke tests, and the cost-basis parity check (€6.95 invoiced-only April-TCG avg vs agent).

Pending: 3 dwarf returns. No external action in flight at the principal level.

## T2 — D1 returned (principal)

D1 complete (Phases A + B + C applied, no commits). Headline:

- `query_mart.sql` rewritten 163 → 92 lines. All five subtasks landed: schema flips, `dim_shipping_providers` JOIN drop with alias preserved via `fs.shippingprovider_extkey`, ORWO CTEs + inline CASE dropped, Picturator-Wolfen dedup filter dropped, `order_source` CASE → plain `fs.source_system`.
- `query_mart_items.sql` two-line edit on `FROM`/`JOIN` schemas; `dw.dim_products` JOIN preserved per locked decision.
- `pipeline.py:552-564` simplified to `cost_for_routing = shipping_cost_final` directly. 14 other references spot-checked, all NULL-safe.

**Pre-cutover baseline (from `data/meta.json` + `_pipeline_run.log`):** `total_rows = 13,131,306`, `date_bounds = 2024-01-01..2026-05-21`, daily=1,281,937, daily_product=2,700,034, alerts=2,485, issues=181 (49 active). Reference for smoke 1.

D1 sibling: `2026-05-22_d1_dashboard-cutover-sql-pipeline.md`.

Still in flight: D2 (UI), D3 (audit+backtest).

## T3 — D3 returned (principal)

D3 complete (Phase G applied, no commits). Headline:

- `audit.py` rewritten 603 → ~360 lines. Dropped sections 2-6 + 9 wholesale (Completeness, L1, L2, L3, L4, Avg costs — parquets no longer produced). Kept + retargeted Transform basics / Deviations / Trends / Meta. Added Daily / Daily-product / Alerts / Issues / Filter-combos / Outlier-thresholds. **Smoke run: 50 PASS / 0 FAIL / 0 WARN** against current `data/`.
- `backtest.py` minimal data-load switch (`processed.parquet` single-file → `processed/*.parquet` glob + single-file fallback). L1/L2 sim logic verbatim. `--weeks 2` smoke completes in 1.7s, writes 20 rows.

**Classification:** 30 dropped / 16 retargeted / 16 new.

**Thresholds flagged for principal sign-off** (surface at synthesis):

1. `baseline_weeks` — pipeline now uses 5; old audit asserted 6. D3 set soft check `in {5, 6}` with actual printed. Tighten to `== 5`?
2. `backtest.py` constants (`MIN_ABS_CHANGE_EUR=0.50`, `MIN_SHIPMENTS=100`) — unchanged, but cost-basis distribution may have shifted post-cutover (ORWO NULLs where inline CASE used to fill). Sanity-check signal density when convenient. Not blocking.

D3 sibling: `2026-05-22_d3_dashboard-cutover-audit-backtest.md` carries the full classification table.

Still in flight: D2 (UI).

## T4 — D2 returned, all dwarves complete (principal)

D2 complete (Phase D applied, no commits). Headline:

- 25 files modified + 1 new (`src/lib/cost-basis.ts`). Renames: `real_expected → final`, `real → invoiced`, `expected → estimated` in token values and user-facing labels. Data-column names (`avg_cost_real`, `real_pct`, `real_cost_quota`, etc.) intentionally **kept** — they encode the backend API contract.
- Two vocabularies handled cleanly: binary basis (`final | invoiced`) on Breakdown/CostDrivers/shifts; three-line basis (`final | invoiced | estimated`) on Overview/CostTrend chart visibility.
- URL shim at `src/lib/cost-basis.ts::coerceCostBasisParam`, called from `paramsToFilters` in `page.tsx` + all 6 API routes consuming `?costBasis=`. **Defensive — no `?bs=` URL param exists today** (cost-basis lives in tab-local state / sessionStorage). Tab-local sessionStorage in BreakdownTab also coerces legacy values on read.
- Compact-code components (DimensionShareChart `re|r|e`, CarrierShareChart `re|r|e|er`) — codes kept short, only `COST_BASIS_LABELS` map updated.

**Notable D2 findings (no action needed unless flagged below):**

- The "Invoiced"/"Unverified" alert badges were already renamed pre-D2 — the brief's mention was forward-looking but already-applied.
- `generic-trend` / `country-trends` / `packagetype-trends` / `product-trends` / `trends` / `dimension-share-trends` / `carrier-share-trends` API routes emit all three cost lines as data columns and don't consume a `costBasis` param — filtering is client-side. Intentionally not touched.
- `OutliersTable.tsx` CSV download headers (`"Cost","Expected"`) left intact to avoid breaking downstream CSV consumers. **Surface to principal.**
- `real_cost_confirmed` boolean and `/api/layer2` endpoint name kept — out of Phase D scope.

D2 sibling: `2026-05-22_d2_dashboard-cutover-ui-labels.md` carries full file/line ranges + 8 surprise notes.

## Apply tranche — landed

| Phase | Owner | Status |
|---|---|---|
| A — `query_mart.sql` rewrite | D1 | ✅ applied |
| B — `query_mart_items.sql` schema flips | D1 | ✅ applied |
| C — `pipeline.py` `cost_for_routing` simplification | D1 | ✅ applied |
| D — UI label rename + URL shim | D2 | ✅ applied |
| E — dashboard `CLAUDE.md` doc note | principal | ⏳ pending |
| F — `data/issues.parquet` reset | principal | ⏳ pending (before first post-cutover pipeline run) |
| G — `audit.py` + `backtest.py` rewrite | D3 | ✅ applied, smokes pass (50/0/0) |
| H — `pytest tests/` sweep | principal | ⏳ pending (after smokes 1+2) |

## T5 — Phase E + D3 tighten + parking decisions (principal)

Niklavs running smokes 1 + 2. Decisions logged:
- **A (OutliersTable CSV header):** parked — broader export rework coming.
- **B (`?bs=` URL emission):** parked.
- **C (backtest constants):** keep as-is.
- **D3 `baseline_weeks`:** tighten to `== 5` (no objection).

Applied:

1. **Phase E** — `bi-analytics/NFE/dashboards/shipping_costs_monitoring_nextjs/CLAUDE.md` § Key Patterns:
   - Updated the now-stale `cost_for_routing` bullet (was `COALESCE(real_shipping_cost, expected_shipping_cost)` — now plain `final_shipping_cost_eur`, label "Final cost (invoiced + estimated)").
   - Added the naming-asymmetry one-liner: `real_shipping_cost_eur` column vs `cost_source='invoice'` flag, with the 0.5% `'invoice_estimate'` transient remnant guidance.
2. **D3 `baseline_weeks` tightening** — `audit.py` `check("meta baseline_weeks == 5", bw == 5, …)`. Dropped the soft-band comment.
3. **Parked items** logged in `inventory/dashboard-gold-cutover-resume.md` § Deferred — CSV export rework (A), `?bs=` URL emission (B), backtest signal-density tuning (C).

Still pending principal (interleaved with Niklavs running smokes):
- Smoke 1 verdict from Niklavs (pipeline + row counts).
- Smoke 2 verdict from Niklavs (dev server + labels + shim).
- Phase F (issues.parquet reset) — gates on smokes 1 + 2 passing.
- Next pipeline run + Smoke 4 / parity check.
- Phase H (pytest).
- Commits.
- DAG verification (tomorrow's 08:00 Berlin run).
- Quest closure + unblock convergence quest.

## T6 — committed; pivoting to CSV export rework (principal)

Niklavs authorized commit (smokes 1+2 verdicts not awaited; Phase H pytest kicked in background instead of pre-commit). Four commits landed:

- `bi-analytics` (`shipping-mart-cutover`):
  - `dee0265` — dashboard: cut over to shipping_mart gold tables (Phases A+B+C+E)
  - `0660a52` — dashboard: rename cost-basis vocab to match gold (Phase D)
  - `0001b36` — dashboard: re-target audit.py + backtest.py (Phase G)
- `brain` (`main`): `c41ce97` — dashboard gold cutover applied: quest log + resume

Phase H (`pytest tests/`) started in background. If failures surface, fix-up commit on top.

Still pending on the cutover (won't block CSV work):
- Smoke 1/2 verdicts from Niklavs
- Phase F (issues.parquet reset)
- Next pipeline run + Smoke 4 parity check (€6.95 / 209,874)
- pytest results triage
- DAG verification (tomorrow's 08:00 Berlin)
- Quest closure

**Pivoting to CSV export rework** — Niklavs unparked item A from § Deferred. Scope TBD; about to ask.

### Phase H — pytest

✅ 82 passed in 0.37s. Schema-agnostic; D1's `cost_for_routing` semantic change did not break any fixtures.

## T7 — CSV export rework: helper + dwarves (principal)

Niklavs picked "Unify + standardize" scope. Sub-decisions: snake_case all ID columns; add `cost_source` to `/api/export`.

Principal landed first:
- `src/lib/csv.ts` — shared helper: `rowsToCsv<T>(rows, columns)`, `downloadCsvBlob(csv, filename)`, `csvFilename(prefix, ...parts)`. RFC-4180-ish CSV. Auto-quotes cells containing `",\n\r`; `forceQuote` flag for ID-shaped cols.
- `src/components/ui/TableExportButton.tsx` — standard button (cloned from OutliersTable's existing visual).

Three dwarves in parallel:
- **D1** — refactor existing 2 paths (`OutliersTable.tsx::downloadCsv` + `/api/export/route.ts`) to use helper + gold vocab. Establishes the canonical column shape. Brief includes the full 13-col convention for `/api/export` (with `cost_source` added).
- **D2** — add Download CSV button to BreakdownTab + DeviationsTable + AvgCostsHeatmap (heavy / complex).
- **D3** — add Download CSV button to RateChangesTable + CarrierShiftsTable + ShiftsTable + ProductShiftsTable + BenchmarksTab + CompletenessGrid (smaller / repetitive).

Sibling quest-log files:
- `2026-05-22_d1_csv-refactor.md`
- `2026-05-22_d2_csv-add-breakdown-deviations-avgcosts.md`
- `2026-05-22_d3_csv-add-shifts-bench-completeness.md`

All on `shipping-mart-cutover`. No commits during dwarf runs.

## T8 — D1 (CSV) returned (principal)

D1 complete. Changes:
- `sql/query_mart.sql`: added `fs.cost_source AS cost_source` to SELECT (with enum-value comment).
- `pipeline.py`: added `cost_source` to `RAW_KEEP_COLS` (~L38) and `write_processed` (~L2440).
- `src/components/OutliersTable.tsx`: 8-col helper-based `downloadCsv`; inline button JSX replaced by `<TableExportButton>`.
- `src/app/api/export/route.ts`: full rewrite. SELECT aliases parquet columns to gold-vocab snake_case; CSV via `rowsToCsv`; filename via `csvFilename("shipments", …)`. ORDER BY updated to use alias.

**Pipeline refresh needed:** `cost_source` is now in the pipeline projection but won't populate in `data/processed/<YYYY-MM>.parquet` until next `python pipeline.py --refresh-full` (or `--refresh`). Until then the CSV column exists but is empty. Flag for the post-cutover pipeline run that's already pending (Phase F + smoke 4 territory).

Still in flight: D2 (Breakdown/Deviations/AvgCosts), D3 (shifts/bench/completeness).

## T9 — D2 (CSV) returned (principal)

D2 complete. CSV export added to three tabs (no commits). `npx tsc --noEmit` exits 0.

- `DeviationsTable.tsx` — 10-col main-row export incl. `invoiced_cost_eur` / `estimated_cost_eur` / `deviation_eur`. Filename `deviations_<from>_<to>.csv`.
- `AvgCostsHeatmap.tsx` — long format (one row per (corridor, week) cell). Filename `avg_costs_<metric>_<gran>-<periods>_to_<to>.csv`.
- `BreakdownTab.tsx` — tree-walking flatten that preserves UI sort + parent context. Dynamic dim cols per `dims` prop. Filename `breakdown_<dim-order>_<from>_<to>.csv`.

Flags surfaced (none load-bearing):
1. Deviations uses two cols (`destination_country` + `shippingprovider`) rather than concatenated `corridor` — no corridor field on `DeviationRow`. Easy switch later.
2. Deviations expanded-row package breakdown not exported (would need a separate per-corridor button inside the expanded panel).
3. AvgCosts defaulted to long format (per brief's "either / default to long").
4. Breakdown's `cost_source` column emits a constant reflecting UI's `costBasis` toggle value (`"final"` / `"invoiced"`) — `BreakdownRow` has no per-row provenance.

Still in flight: D3.

## T10 — D3 (CSV) returned, all CSV dwarves home (principal)

D3 complete. Six components got the Download CSV button (no commits). `npx tsc --noEmit` exits 0.

- `RateChangesTable.tsx` — 14 cols, `rate_changes_<from>_<to>.csv`
- `CarrierShiftsTable.tsx` — 17 cols, `carrier_shifts_<from>_<to>.csv`
- `ShiftsTable.tsx` — 18 cols, `routing_shifts_<from>_<to>.csv`
- `ProductShiftsTable.tsx` — 19 cols, `product_shifts_<from>_<to>.csv`
- `BenchmarksTab.tsx` — 22 cols, `benchmarks_<from>_<to>.csv` (respects priority/effort/confidence pills)
- `CompletenessGrid.tsx` — 9 cols, `completeness_<gran>_<firstWeek>_<lastWeek>.csv` (long format, filtered to providers passing min-shipments gate)

Decisions D3 made on the spot:
- No `cost_source` in shifts-family rows (cost columns are averages across mixed-basis rows). Used `gainer_cost_eur` / `from_cost_eur` snake_case rather than misleadingly forcing `invoiced_cost_eur`.
- No `forceQuote: true` needed (no ID-shaped columns in any of these six).
- CompletenessGrid's pre-existing per-cell "click to export" → `/api/export` left untouched (D1 territory).

## CSV rework — landed (full tally)

| Path | Owner | What |
|---|---|---|
| `src/lib/csv.ts` | principal | new helper |
| `src/components/ui/TableExportButton.tsx` | principal | standard button |
| `sql/query_mart.sql` | D1 | added `cost_source` to SELECT |
| `pipeline.py` | D1 | added `cost_source` to `RAW_KEEP_COLS` + `write_processed` |
| `src/components/OutliersTable.tsx` | D1 | refactor to helper |
| `src/app/api/export/route.ts` | D1 | full refactor + gold-vocab aliases + `cost_source` col |
| `src/components/BreakdownTab.tsx` | D2 | + Download CSV |
| `src/components/DeviationsTable.tsx` | D2 | + Download CSV |
| `src/components/AvgCostsHeatmap.tsx` | D2 | + Download CSV |
| `src/components/RateChangesTable.tsx` | D3 | + Download CSV |
| `src/components/CarrierShiftsTable.tsx` | D3 | + Download CSV |
| `src/components/ShiftsTable.tsx` | D3 | + Download CSV |
| `src/components/ProductShiftsTable.tsx` | D3 | + Download CSV |
| `src/components/BenchmarksTab.tsx` | D3 | + Download CSV |
| `src/components/CompletenessGrid.tsx` | D3 | + Download CSV |

15 files; 2 new, 13 modified. tsc-clean. No commits.

## Pending actions

*(none — CSV rework done; awaiting principal for smoke + commit cadence)*
