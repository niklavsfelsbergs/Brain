# SCM shift tabs — processed-tier baseline-prune gotcha

**Source:** [[S264_17290ea4_scm-shift-tabs-baseline-prune|S264]] (sid8 17290ea4), bug fix `e452939` in `bi-analytics` `shipping_costs_monitoring_nextjs/src/lib/shifts.ts`.

## The mechanism

The shift query (`computeShifts`, feeds `/api/layer2` + carrier/product-shift routes) is a **current-vs-baseline** comparison: its `tagged` CTE reads rows from BOTH the analysis window AND the baseline window in one pass, tags each by role, and computes `gainer_cost` (current) vs `baseline_avg_cost` (baseline).

Data source is tier-dependent (`grainConfig`):
- **No site/shop/order-source filter** → reads the full-history `daily.parquet` (all months present → baseline always available).
- **Any Production Site / Shop / Order Source filter active** (`hasProcessedOnly`) → falls back to `processedAsDaily()` over the `processed/<YYYY-MM>.parquet` tier, which `processedPruned` prunes to the months overlapping the passed `[from,to]`.

**The bug (pre-`e452939`):** `grainConfig` passed only the CURRENT window (`params.from, params.to`) to `processedAsDaily`. So `processedPruned` loaded only the current month(s); the **baseline month was never read**. Baseline role empty → `baseline_avg_cost` null → Base Cost / Premium / % Premium / EUR Impact all `--`, and every share delta goes positive (baseline share = 0 for all → no "losers" → `from_cost` has no counterparts → falls back to the null baseline). `gainer_cost` (Avg Cost) survives because the current month IS loaded.

## Fingerprint (how to recognize it)

Shift tab with a site/shop/order-source filter active, showing: **Avg Cost populated but Base Cost / Premium / % Premium / EUR Impact all `--`, and every Share delta positive** (often many "+100.0pp"). The all-positive deltas = absent baseline. Default no-filter view is fine; Top Drivers/Savers (date-only params) is fine.

## The fix

Prune across the union of both windows: `processedAsDaily(min(from,baselineFrom), max(to,baselineTo))`. The `tagged` CTE re-filters by the two windows, so extra in-between months are harmless. Same `fromExpr` also feeds `baseline_weeks` / `baseline_period_count` / `baseline_weekly_vol` — all were silently empty too, all restored.

## General lesson for the tiered-DuckDB design

Any query that spans more than its nominal `[from,to]` (here: + a baseline window; also true of trend/YoY queries) must prune the processed tier across the **full date reach it actually reads**, not the headline window. Audit sibling callers of `processedPruned` / `processedAsDaily` / `processedAsTransitDaily` for the same single-window assumption.

→ digest [[scm]] · cf. the windowed-extract class of bug (a window opened too narrow drops history the computation needs).
