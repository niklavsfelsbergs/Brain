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

## Pending actions

*(none — awaiting smoke 1/2 verdict from Niklavs)*
