# D2 — Dashboard cutover, Phase D (UI labels + URL shim)

**Dwarf:** D2 spawned by Jebrim (principal) for the dashboard gold cutover.
**Repo / branch:** `bi-analytics/`, branch `shipping-mart-cutover` (already in flight, do NOT switch).
**Scope:** Phase D only. Cost-basis vocabulary rename + URL back-compat shim. No SQL, no pipeline, no audit/backtest.

## Vocab table

| Old (URL/internal) | New (URL/internal) | Old display | New display |
|---|---|---|---|
| `real_expected` | `final` | "Real + expected" / "Real (+ expected)" | "Final cost (invoiced + estimated)" |
| `real` | `invoiced` | "Real" / "Real only" | "Invoiced only" |
| `expected` | `estimated` | "Expected" / "Expected only" | "Estimated only" |

Alert badge: "real" → "invoiced".
URL shim: `?bs=real_expected` / `?bs=real` / `?bs=expected` map to new values at parse layer (single point).

## Turn log

### T1 — scoping reads + grep audit

Read resume note + D2 (API) + D3 (frontend) reference notes. Audit grep `real_expected` (case-sensitive, 13 files) + `"real"` (string-literal, 19 files) + `"expected"` (5 files).

Two distinct cost-basis vocabularies in the code:
- **Three-state Overview vocab** (`OverviewTab.tsx`): `coalesce | real | expected` — used for which lines are visible on the trend chart.
- **Binary shifts/breakdown vocab**: `real_expected | real` — used by BreakdownTab, CostDriversTab, shifts (carrier/routing/product), rate-changes, breakdown API, cost-drivers-top API. NOTE: no third value here (`expected` not used as a basis).

Mapping per brief:
- `real_expected → final`
- `real → invoiced`
- `expected → estimated` (only meaningful in Overview's 3-state vocab + 3-state generic-trend / `LINE_CONFIG`)

The third value also applies to:
- `CostTrend.tsx` LINE_CONFIG (`coalesce | real | expected` — used by the shared trend chart).
- `CarrierShareChart.tsx` has a 4-state extension: `re | r | e | er` — only the cost-basis ones rename (`re`, `r`, `e`).

URL shim observation: there is currently no `?bs=` URL param. `paramsToFilters` in `page.tsx` doesn't read `bs`. CostDriversTab only writes `cdi` (inner tab) to URL. BreakdownTab persists costBasis to sessionStorage, not URL. The shim will be a defensive read inside `paramsToFilters` that maps old `bs` values to new ones, ready to consume an old bookmarked URL even though no current write path emits them.

Touch-point list (planned):
- `src/lib/shifts.ts` — `CostBasis` type rename.
- `src/app/page.tsx` — `bdExpandCostBasis` state type; add URL shim for `?bs=`.
- `src/app/api/breakdown/route.ts` — `CostBasis` type, API param read, internal value flow.
- `src/app/api/cost-drivers-top/route.ts` — API param read.
- `src/app/api/carrier-shifts/route.ts` — API param read.
- `src/app/api/layer2/route.ts` — API param read.
- `src/app/api/product-shifts/route.ts` — API param read.
- `src/app/api/rate-changes/route.ts` — internal value (checked separately).
- `src/components/BreakdownTab.tsx` — type, state, display labels.
- `src/components/CostDriversTab.tsx` — state, toggle labels, API param write.
- `src/components/CarrierShiftsTable.tsx` — prop type.
- `src/components/ShiftsTable.tsx` — prop type.
- `src/components/ProductShiftsTable.tsx` — prop type.
- `src/components/RateChangesTable.tsx` — prop type.
- `src/components/OverviewTab.tsx` — 3-state `coalesce|real|expected` rename + display labels.
- `src/components/CostTrend.tsx` — 3-state `coalesce|real|expected` rename + display labels.
- `src/components/DimensionShareChart.tsx` — "Real" display label.
- `src/components/CarrierShareChart.tsx` — 4-state, "Real" label.
- `src/components/KPIRow.tsx` — "Real" display label.
- `src/components/QuotaTrend.tsx` — "Real" display label.
- `src/components/AlertsTab.tsx` — display strings, `defaultCostBasis` prop key (still 3-state), chart series.
- `src/components/DeviationsTable.tsx` — display strings if any.
- `src/components/AvgCostsHeatmap.tsx` — display strings if any.
- `src/lib/types.ts` — TAB docs strings.

Note: API endpoint route handlers consume `costBasis` query param. To preserve back-compat for any URL emitting the old `costBasis=real_expected` / `costBasis=real`, I'll add a small normalizer that maps both old and new values to the canonical new internal values.

### T2 — URL shim helper

Created `src/lib/cost-basis.ts`. Exports:
- `type CostBasisFinal = "final" | "invoiced"` — binary basis.
- `type CostBasisLine = "final" | "invoiced" | "estimated"` — three-line vocab.
- `coerceCostBasisParam(raw)` — single shim point. Maps old (`real_expected`/`real`/`expected`) and new (`final`/`invoiced`/`estimated`) values to the canonical new vocab. Returns `undefined` for unknown / missing.

Imported into `page.tsx` `paramsToFilters` (silently coerces `bs=` to keep future bookmarked URLs alive — no Filters field exists today; documented inline), and used inside every API route that reads `costBasis` (breakdown, cost-drivers-top, carrier-shifts, layer2, product-shifts, rate-changes).

### T3 — type/value renames across the binary-basis surface

- `src/lib/shifts.ts` — `CostBasis = "final" | "invoiced"`; default `"final"`; `isReal` → `costBasis === "invoiced"`.
- `src/app/api/breakdown/route.ts` — type, default values in `buildLevelQuery` + `buildTotalQuery`, URL-param read via `coerceCostBasisParam`. Comments updated.
- `src/app/api/cost-drivers-top/route.ts` — type, default param, internal `isReal` → `isInvoicedOnly`. URL shim added.
- `src/app/api/carrier-shifts/route.ts`, `layer2/route.ts`, `product-shifts/route.ts`, `rate-changes/route.ts` — URL-param reads route through shim; vars renamed.
- `src/components/BreakdownTab.tsx` — `CostBasis` type, `costBasis` state defaults to `"final"`, sessionStorage-read back-compat coerces legacy values, auto-switch on bucket filter uses new vocab, cost-basis toggle UI labels rewritten (Real+Exp -> Final, Real -> Invoiced with hover titles), API param send is `costBasis=invoiced`.
- `src/components/CostDriversTab.tsx` — state, button labels (Real+Exp -> Final, Real -> Invoiced).
- `src/components/CarrierShiftsTable.tsx`, `ShiftsTable.tsx`, `ProductShiftsTable.tsx`, `RateChangesTable.tsx` — prop type, API param send, "Real %" column header -> "Invoiced %".
- `src/app/page.tsx` — `bdExpandCostBasis` state type, `handleAlertNavigate` value `"real" -> "invoiced"`, URL shim added.

### T4 — three-state vocab rename (OverviewTab, CostTrend)

Internal vocabulary token rename only -- the API data field names (`avg_cost_real`, `total_cost_expected`, etc.) are kept as-is because they encode the backend column contract. The `costKey` helper in OverviewTab maps new vocab to legacy data-key suffixes; same idea via the `LINE_CONFIG.key` field in CostTrend.

OverviewTab changes:
- `type CostBasis = "final" | "invoiced" | "estimated"` (was `"coalesce" | "real" | "expected"`).
- `LINE_CONFIG` keys + labels updated ("Real + Expected" -> "Final cost (invoiced + estimated)", "Real" -> "Invoiced only", "Expected" -> "Estimated only").
- `QUOTA_LINE_CONFIG.real.label` "Real" -> "Invoiced".
- `costKey()` bridges new vocab to legacy data-keys (`avg_cost` / `avg_cost_real` / `avg_cost_expected`).
- `visible` state init keys, `vis.visible.<basis>` reads, every `basis === "..."` check, every `LINE_CONFIG.<basis>` access updated.
- Tooltip display strings: "Real+Exp" -> "Final", "Real" -> "Invoiced", "Exp. (real)" -> "Est. (invoiced)", "Expected" -> "Estimated", "Real quota" -> "Invoiced quota", "Real cost" -> "Invoiced cost", "Routing cost" -> "Final cost", "Real costs" %-row -> "Invoiced %".
- Share-table column headers: "R+E"/"R %"/"Real"/"Exp" -> "Final"/"Inv %"/"Inv"/"Est".
- Lines popover labels: "Real" -> "Invoiced", "Real + Expected" -> "Final cost (invoiced + estimated)".
- Comment block describing modes updated.

CostTrend changes:
- Same type rename + LINE_CONFIG entries with `key:` retaining legacy data-key names.
- `defaultCostBasis` prop type renamed (`{coalesce/real/expected}` -> `{final/invoiced/estimated}`).
- Visibility state, tooltip cell labels ("R+E"/"R %"/"Real"/"Exp" -> "Final"/"Inv %"/"Inv"/"Est"), all `basis === "..."` checks, all `LINE_CONFIG.<basis>` accesses, all `visible.<basis>` reads renamed.
- Callers of `defaultCostBasis` updated: `AlertsTab.tsx`, `BreakdownTab.tsx`, `RateChangesTable.tsx`.

### T5 — supporting components

- `KPIRow.tsx`: Cost Quota stack labels — "Real" -> "Invoiced", "Combined" -> "Final"; comment updated.
- `QuotaTrend.tsx`: tooltip rows and right-side legend "Real"/"Combined" -> "Invoiced"/"Final"; legend explanation copy reworded ("real cost" -> "invoiced cost", "routing cost" -> "routing cost").
- `DimensionShareChart.tsx`: 3-code type kept (`"re" | "r" | "e"`), `COST_BASIS_LABELS` now Final/Inv/Est, header row "R+E"/"R %"/"Real"/"Exp" -> "Final"/"Inv %"/"Inv"/"Est".
- `CarrierShareChart.tsx`: 4-code type kept (`"re" | "r" | "e" | "er"`), `COST_BASIS_LABELS` fully reworded; header row "R+E"/"R %"/"Real"/"Exp" -> "Final"/"Inv %"/"Inv"/"Est".
- `AvgCostsHeatmap.tsx`: hidden tab — `Metric` union renamed; switch arms + `setMetric` default; option labels.
- `DeviationsTable.tsx`: hidden tab — "Total Real"/"Total Expected" column labels (twice — main table and expanded package-type breakdown), legend formatter "Avg Real"/"Avg Expected" -> "Avg Invoiced"/"Avg Estimated".
- `AlertsTab.tsx`: deviations header subtext "real vs expected cost gaps" -> "invoiced vs estimated cost gaps", drill-in title "Real vs Expected" -> "Invoiced vs Estimated", deviation-trend chart legend/tooltip formatter.

### T6 — types.ts doc strings

Updated four `TABS` entry strings under steps/footnotes:
- Overview "Cost basis toggles" + "Exp. (real) toggle" + "Period average line".
- Breakdown "Real % (secondary)" + "Real+Exp / Real toggle".
- Avg Costs "Metric buttons".

### T7 — final sweep + cleanup

Found and fixed additional label sites:
- `BreakdownTab.tsx` column defs: `Real Q` -> `Inv Q`, `Combined Q` -> `Final Q`, `Real %` -> `Invoiced %`.
- `RateChangesTable.tsx` column def: `Real %` -> `Invoiced %`.
- `CompletenessGrid.tsx` tooltip rows: `Real Cost`/`Real Cost %`/`Real Count`/`Real Count %` -> `Invoiced *`.
- `KPIRow.tsx`: subtext "real cost coverage" -> "invoiced cost coverage".

Verified final state with grep:
- No remaining `"real_expected"` string literals outside comment/shim documentation.
- No remaining `"coalesce"` string literals.
- No `costBasis === "real"` / `costBasis === "expected"` patterns (only the deliberate back-compat sessionStorage reader in BreakdownTab line 314).

## Summary

### Files touched (line ranges via grep, not exact pre-edit lines)

**New file:**
- `bi-analytics/NFE/dashboards/shipping_costs_monitoring_nextjs/src/lib/cost-basis.ts` — single shim point (entire file new).

**Modified files:**
- `src/app/page.tsx` — added shim import; `paramsToFilters` shim call (~line 218); `bdExpandCostBasis` state type (~line 273); `handleAlertNavigate` value (~line 526).
- `src/app/api/breakdown/route.ts` — type + default at 137-147; `costFilter` literal at 155; `buildTotalQuery` defaults at 371-380; URL-param read at 588-590; import line 4.
- `src/app/api/cost-drivers-top/route.ts` — import 4; URL-param read 20; `isReal` rename 152-183; default 114.
- `src/app/api/carrier-shifts/route.ts` — import + URL-param read (lines 4, 10).
- `src/app/api/layer2/route.ts` — import + URL-param read (lines 4, 22-23).
- `src/app/api/product-shifts/route.ts` — import + URL-param read (lines 5, 27).
- `src/app/api/rate-changes/route.ts` — import + URL-param read 4, 23; `isInvoicedOnly` rename 86-87.
- `src/lib/shifts.ts` — CostBasis type 97, default 103, `isReal` rename 121-122.
- `src/components/BreakdownTab.tsx` — CostBasis type ~53; sessionStorage reader 311-318; bucket-filter auto-switch ~340-344; API param ~438; defaultCostBasis prop call ~1179; cost-basis toggle UI 1284-1306; column defs 86, 94.
- `src/components/CostDriversTab.tsx` — state 84; API param ~139; toggle buttons 205-219.
- `src/components/CarrierShiftsTable.tsx` — prop type 11; column def 54; API param ~72.
- `src/components/ShiftsTable.tsx` — prop type 11; column def 55; API param ~73.
- `src/components/ProductShiftsTable.tsx` — prop type 11; column def 56; API param ~82.
- `src/components/RateChangesTable.tsx` — prop type 10; column def 169; API param at 82+119; defaultCostBasis 327, 370.
- `src/components/OverviewTab.tsx` — CostBasis type 30; LINE_CONFIG 32-38; QUOTA_LINE_CONFIG 43; costKey 51-58; tooltip body strings 311, 315, 364-366, 393-417, 425-427; share-table headers 204-208; visibility state 494; quota row label 317; visibility/key references at 681-683, 713-715, 760, 876, 894-896, 1171; popover labels 996, 1002, 1026; comment 964.
- `src/components/CostTrend.tsx` — CostBasis type 78; LINE_CONFIG 80-89; share-table headers 120-123; tooltip headers 183-186, 199-202; defaultCostBasis type 59; visibility state init 247-251; all `basis === "..."` and `visible.<basis>` and `LINE_CONFIG.<basis>` at 519-521, 555, 631, 641-642, 663, 760, 810-811, 893.
- `src/components/AlertsTab.tsx` — defaultCostBasis call 1214; deviation header text 588; drill-in title 1167; deviation chart labels 1265, 1268, 1292.
- `src/components/DeviationsTable.tsx` — column defs 41-42, 324-325; chart label/formatter 285, 292.
- `src/components/AvgCostsHeatmap.tsx` (hidden tab) — Metric type 11; METRIC_OPTIONS 13-19; getValue 33-41; state default 58; logic 141-143.
- `src/components/CarrierShareChart.tsx` — CostBasis comments+labels 21-33; header row 601-604.
- `src/components/DimensionShareChart.tsx` — CostBasis label map 22-32; header row 503-506.
- `src/components/KPIRow.tsx` — Cost Quota labels 360, 367-370, 388-391; coverage subtext 440.
- `src/components/QuotaTrend.tsx` — tooltip rows 80-91; legend block 260-273.
- `src/components/CompletenessGrid.tsx` — tooltip rows 90-95.
- `src/lib/types.ts` — TABS doc strings: Overview cost-basis (~line 292-297), Breakdown Real % (~318), Breakdown Real+Exp/Real toggle (~324), Avg Costs Metric buttons (~387).

### URL-shim implementation location

Single file: `src/lib/cost-basis.ts`. Exports `coerceCostBasisParam(raw)`. Mapped from legacy values (`real_expected/real/expected`) and pass-through for new values (`final/invoiced/estimated`). Used at:
- `src/app/page.tsx:218` — `paramsToFilters` reads `?bs=` (defensive — no Filters field exists today).
- All 6 API endpoints that consume `?costBasis=`: breakdown, cost-drivers-top, carrier-shifts, layer2, product-shifts, rate-changes.

This is intentionally one helper. Tab-local state owners (BreakdownTab session-storage, CostDriversTab local state) coerce on read as well to handle pre-cutover persisted values — that one is inline in BreakdownTab line 314 because it's reading from `sessionStorage`, not URL.

### "real"-string hits skipped (and why)

- `real_pct` field name — kept as data-shape (API contract); only display labels (`Real %` -> `Invoiced %`) renamed.
- `real_cost_quota`, `real_cost`, `real_cost_pct`, `n_real`, `avg_cost_real`, `total_cost_real`, `_scopeR`, `_scopeRE`, `_scopeER`, `_total_real`, `_prev_total_real`, `has_real`, `sum_real` — all data field/column names; brief said "internal/URL value renames" referred to the cost-basis token values (`"real_expected"`, `"real"`), not data-column names. Renaming columns would touch SQL + parquet schema + many more files; outside Phase D scope.
- `real_cost_confirmed`, `confirmed_week` — alert-system data fields; left alone.
- API endpoint URL paths (e.g. `/api/rate-changes`, `/api/layer2`) — not renamed (not in scope).
- `OutliersTable.tsx` CSV download header `["...,"Cost","Expected",...]` — CSV column header consumed by downstream CSV parsers (line 197). Left intact to avoid breaking export consumers.
- `AlertsTab.tsx` lines 1235-1271 chart `dataKey="real"` / `"expected"` — those are React/Recharts internal `dataKey` strings tied to the response shape `{ real, expected }` from `/api/deviations`. The display *formatter* now produces "Avg Invoiced"/"Avg Estimated", but the dataKey strings themselves stay as data keys.
- `BreakdownTab.tsx` various `bcols` / `bd_state` field names that reference `real`-prefixed data — kept as data shape.

### UI strings that surprised me

1. **No `?bs=` URL param existed today.** The URL-shim is forward-looking (defensive). `costBasis` lives in tab-local React state (BreakdownTab uses sessionStorage, CostDriversTab uses pure useState). Nothing serializes cost-basis into URL — `CostDriversTab` only writes `cdi` (inner tab). The shim catches any externally-supplied `?bs=old_value` should it ever appear.

2. **Two distinct cost-basis vocabularies** in the same codebase:
   - Binary basis `final | invoiced` — used by BreakdownTab, CostDriversTab, shift tables, rate-changes (5 tabs + 5 API routes).
   - Three-line basis `final | invoiced | estimated` — used by OverviewTab/CostTrend chart-line visibility (multi-select).
   The shim helper exports both type aliases (`CostBasisFinal`, `CostBasisLine`).

3. **DimensionShareChart and CarrierShareChart use compact codes** (`"re"|"r"|"e"` or `"re"|"r"|"e"|"er"`) instead of full words. The type-level codes stay short; only the user-facing `COST_BASIS_LABELS` map updated.

4. **BreakdownTab auto-switches `costBasis` from `final` to `invoiced` when the bucket filter is active** (estimated rows have no bucket attribution). The comment was renamed but the auto-flip behavior is identical.

5. **Already-correct "Invoiced" / "Unverified" badges on shift alerts** (AlertsTab lines 922-927). These were renamed pre-D2 in an earlier pass — the brief mentioned "alert badge real -> invoiced" but on inspection there was no remaining "Real" badge label. The text in the brief was forward-looking but already-applied.

6. **`generic-trend` / `country-trends` / `packagetype-trends` / `product-trends` / `trends` / `dimension-share-trends` / `carrier-share-trends` API routes** do not consume the binary `costBasis` param — they emit all three cost lines (avg_cost / avg_cost_real / avg_cost_expected) as data columns. The "cost-basis" filtering happens client-side in CostTrend / OverviewTab through line visibility. So those endpoints were intentionally not touched for the cost-basis rename.

7. **`real_cost_confirmed` boolean on shift alerts** kept its name — it's a data flag whose vocab is the gold mart's `cost_source = 'invoice'` flag flowing through the dashboard. Renaming would touch the API/parquet shape and is outside Phase D.

8. **`/api/layer2` endpoint** still named `layer2` despite the UI label being "Routing Shifts". This is a known D3-noted gotcha; not in Phase D scope.

