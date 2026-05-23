# S055 D4 — Frontend State + Cutover Hygiene + Tooling Review

**Role:** review dwarf (Jebrim-scoped), read-only. **Target:** `bi-analytics/NFE/dashboards/shipping_costs_monitoring_nextjs/` @ branch `shipping-mart-cutover`.

**Scope summary.** Read in full: `audit.py`, `backtest.py`, `backtest_report.py`, `dags/shipping_costs_monitoring_dag.py`, `docker/entrypoint.sh`, `docker/refresh.sh`, `src/app/page.tsx`, `src/lib/{cost-basis,format,csv,utils,useChartZoom,types}.ts`, `src/components/{KPIRow,TabNav,OutliersTable}.tsx`, the relevant slices of `BreakdownTab.tsx`/`OverviewTab.tsx`/`CostDriversTab.tsx`/`DeviationsTable.tsx`/`CostTrend.tsx`, `src/lib/types.test.ts`, and `src/lib/db.ts::parseFilterParams` (just to close the param-name loop). Cross-checked cutover commits `0660a52` (vocab rename) and `0001b36` (tooling re-target) against current file state, and `git log HEAD..origin/main` for the dashboard subtree. **Confidence: high** on the staleness verdict, vocab-rename completeness, TAB_SCOPE/TAB_FILTERS symmetry, and the isActive-gating map; medium on the runtime-only items flagged at the end.

---

## VERDICT on the audit.py / backtest.py staleness question — RE-TARGETED (prior bank note is now STALE/WRONG)

The prior bank note claiming `audit.py` and `backtest.py` are pre-cutover and reference legacy `layer{1,2,3,4}_*.parquet` / single-file `processed.parquet` and will FAIL is **no longer true**. Commit `0001b36` ("re-target audit.py + backtest.py to post-cutover output layout") is present on this branch and the working-tree files reflect it:

- **audit.py** — `_load_processed()` (audit.py:46-54) reads the partitioned set via `(DATA/"processed").glob("*.parquet")`. It loads exactly the post-cutover output set: `raw`, `processed/*`, `corridor_trends_weekly`, `deviations`, `deviations_summary`, `outlier_thresholds`, `daily`, `daily_product`, `alerts`, `issues`, `filter_combos`, `meta.json` (audit.py:64-75). No `layer{1,2,3,4}` references anywhere; the only `processed.parquet` mention is in the docstring describing what was removed (audit.py:8). Sections renumbered 1–10; L1/L2/L3/L4 algebra checks dropped.
- **backtest.py** — data-load (backtest.py:289-297) reads `processed/*.parquet` via glob with an explicit single-file fallback for unmigrated checkouts. The only `processed.parquet` references are the docstring (line 13) and that deliberate fallback (line 297). L1/L2 sim logic kept.
- **Runtime evidence** — `data/processed/` exists and is populated with monthly partitions (`2024-01.parquet`…), and every parquet `audit.py` loads is present in `data/` with recent mtimes (2026-05-22). The commit message records a clean smoke run (50 PASS / 0 FAIL).

**Action for the knowledge base:** archive/supersede the bank note that says these scripts are stale. They target the current output set.

---

## Findings

### Critical
*(none)*

### High

**[TECH] Missing Next.js CVE fix — branch is behind main on a security bump**
`package.json` (branch) pins `"next": "^15.1.0"`; `origin/main` commit `307b663` bumped it to `"next": "^15.5.18"` for **CVE-2026-44578**. The branch (20 behind main) has not merged this. The other dashboard-touching main commit, `ec88d00` (chart cut-off at stale upper bound), is **already present** on this branch (page.tsx:159-166 skip-persist + 384-386 bump-stale-forward), so the only real dashboard merge debt is the CVE bump.
**Why it matters:** ships a known-CVE Next version to production (the DAG deploys `:latest` image weekdays).
**Fix:** fix-now — merge/rebase `origin/main` (or cherry-pick `307b663`) before this branch lands; re-run `npm install` to refresh the lockfile.

### Medium

**[TECH] `coerceCostBasisParam` has zero test coverage — the central cutover shim is untested**
`src/lib/cost-basis.ts:43` is the single normalization point mapping legacy `real_expected`/`real`/`expected` → `final`/`invoiced`/`estimated`. `types.test.ts` imports and tests `resolveRefTab` (line 711) but never imports or exercises `coerceCostBasisParam`. A regression here silently applies the wrong cost basis (the highest-value cutover risk) with no test guard.
**Why it matters:** the one function whose correctness the whole vocab cutover hinges on is the one with no tests.
**Fix:** fix-now (cheap) — add a `describe("coerceCostBasisParam")` covering each old→new mapping, each new passthrough, and null/unknown→undefined.

**[TECH] Non-Overview/Breakdown tabs over-fetch while hidden (no `isActive` gate)**
`page.tsx` passes `isActive={...}` only to `BreakdownTab` (line 736) and `OverviewTab` (line 744). `CostDriversTab` (page.tsx:752), `DeviationsTable`, `OutliersTable`, `AvgCostsHeatmap`, `BenchmarksTab`, `CompletenessGrid`, `TransitTimesTab` receive no `isActive` prop and don't accept one. Their fetch effects fire on filter change regardless of visibility — e.g. `CostDriversTab.tsx:135-140` and `DeviationsTable.tsx:62-67` fetch in a filter-keyed `useEffect` with no gate. Because all tabs are kept mounted via `display:none` after first visit, changing the sidebar date range on Overview triggers background re-fetches in every previously-visited hidden tab.
**Why it matters:** redundant API/DuckDB load (matches the CLAUDE.md claim that only Overview+Breakdown gate). Not a data-correctness bug — each hidden tab still receives its own correctly-scoped `tabFilters[key]`, so no wrong-scope query results.
**Fix:** refactor — thread `isActive` into the remaining tabs' fetch effects (mirror the `if (!isActive) return;` guard already in OverviewTab:538 / BreakdownTab:492). Confirms the prior knowledge-base note; worth recording as still-open.

**[TECH] `filters.alertPeriod` / `?ap=` is documented as URL state but never serialized**
`Filters.alertPeriod` exists (types.ts:68, default at :105) and the Alerts tab footnote advertises `ap= (period)` as URL state (types.ts:478), but **neither `filtersToParams` nor `paramsToFilters` reads or writes `ap`** (page.tsx:133-225). Alerts week-navigation is internal-only; the documented deep-link/restore-on-reload of the selected week does not work.
**Why it matters:** broken/aspirational documented feature — a shared alert URL won't restore the week the sender was viewing.
**Fix:** document (drop the `ap=` claim from the footnote) OR fix-now (add `ap` to both serializers and have AlertsTab read it). Pick one; today the footnote lies.

### Low

**[TECH] Stale "Real"/"Expected" vocab in user-facing tab-help strings (incomplete display rename)**
Commit `0660a52` claimed display renames but missed the `TABS` help/`formula` strings rendered in the "How this tab works" expander and tab tooltips:
- types.ts:317 Breakdown help says secondary column "**Real %**" — actual rendered label is "Invoiced %" (types.ts:318).
- types.ts:359-361 Outliers help: "**Real** shipping cost", "**Expected** shipping cost".
- types.ts:428-429 Completeness help: "**Real cost** %", "Real Cost (EUR)…Real Count".
- types.ts:448-449 Deviations help: "**Total Real**", "**Total Expected**" — but the actual rendered column labels WERE renamed to "Total Invoiced"/"Total Estimated" (DeviationsTable.tsx:43-44, 349-350). So help-text and column-header now disagree.
**Why it matters:** user-visible inconsistency; help describes a column by its old name while the header shows the new name. No wrong-cost-basis applied (dataKey↔column mapping is internally consistent).
**Fix:** document/refactor — sweep the `TABS` `formula` strings for residual Real/Expected and align to invoiced/estimated/final.

**[TECH] OutliersTable column header still uses old vocab ("Expected")**
`OutliersTable.tsx:230` renders `<th>…>Expected</th>` (sorting `expected_shipping_cost`); the "Cost" header (line 229) is the invoiced cost. Sibling tabs renamed "Expected"→"Estimated" (DeviationsTable, OverviewTab toggles), so Outliers is the lone tab still showing the pre-cutover term in a real column header.
**Fix:** leave or refactor — cosmetic; rename "Expected"→"Estimated" for consistency if the rename is meant to be total.

**[TECH] `popstate` handler bypasses the old-tab redirect map**
`page.tsx:350-353` sets `activeTab` directly from `params.get("tab")` on browser back/forward, skipping the `OLD_TABS`/`OLD_SHIFT_TABS` redirect logic that `paramsToFilters` applies on initial load (page.tsx:196-204). Navigating back to a pre-cutover-shaped URL (`?tab=carrier-shifts`, `?tab=products`, etc.) sets an invalid `TabKey` with no matching render block → blank content pane until the user clicks a tab.
**Why it matters:** narrow (requires history entries with legacy tab keys, i.e. bookmarks/links from before the cutover), but a real dead-end.
**Fix:** refactor — route the popstate `tab` through the same redirect (ideally extract one shared `resolveTabParam()` used by both `paramsToFilters` and the popstate handler).

**[TECH] `useChartZoom` docstring references a return shape that doesn't exist**
`useChartZoom.ts:8-11` documents `zoom.bindChart` and `zoom.referenceArea`; the hook actually returns `chartHandlers` and `selectionRange` (useChartZoom.ts:92-101), which is what every consumer uses (CarrierShareChart:841, DimensionShareChart:708, DeviationsTable:270). Stale doc only.
**Fix:** document — update the usage example in the hook comment.

**[TECH] Two separate cost-basis coercion implementations can drift**
The 3-state shim lives in `coerceCostBasisParam` (cost-basis.ts:43); BreakdownTab independently re-implements binary coercion inline for sessionStorage reads (BreakdownTab.tsx:315-319). Both are currently correct (Breakdown is binary-only), but they're maintained separately.
**Fix:** leave/document — low risk; note for future consolidation.

**[TECH] `refresh.sh` uploads `data/raw_cache/` to S3 on every run**
`docker/refresh.sh:24-32` `aws s3 sync data/ … --delete` excludes the big raw caches and the user-state JSONs but NOT `raw_cache/`, so the pipeline's `data/raw_cache/` is pushed to S3 each refresh and then pulled by every dashboard pod via the full-tree sync in `entrypoint.sh:9`. Wasteful, not a correctness bug; the `--exclude` set already protects user-authored `changelog.json`/`dismissed_alerts.json` from `--delete`.
**Fix:** leave or refactor — add `--exclude "raw_cache/*"` if pod startup transfer size matters.

**[TECH] `changelog` initial fetch in page.tsx has no AbortController**
`page.tsx:286` fetches `/api/changelog` in a mount effect with `.catch(() => {})` and no abort/cleanup. Harmless (fires once, no deps) but inconsistent with the abort discipline used everywhere else in the file.
**Fix:** leave — cosmetic.

---

## Verified correct

- **Vocab cutover is consistent where it counts.** Remaining `"real"`/`"expected"` literals in components are intentional: raw API field names / Recharts `dataKey`s whose *display labels* are renamed (AlertsTab.tsx:1265/1270 `dataKey="real"` → legend "Avg Invoiced"; DeviationsTable.tsx:310/319 same; OverviewTab `QUOTA_LINE_CONFIG` "real"/"combined" keys). Commit `0660a52` explicitly kept data-column names (`avg_cost_real`, `sum_real`, `n_real`, …) as the API/parquet contract. No case found where a UI *cost-basis selection* applies the wrong basis.
- **`coerceCostBasisParam` logic** (cost-basis.ts:27-48) — old→new map and new-passthrough are correct; unknown/null → undefined.
- **TAB_SCOPE ↔ TAB_FILTERS symmetry** — checked all 11 tabs: every field a tab zeroes in `TAB_SCOPE` (types.ts:499-511) is hidden in `TAB_FILTERS` (types.ts:516-528), and every visible filter is preserved. Only soft asymmetry: `changelog` hides all filters (`TAB_FILTERS: {}`) but `TAB_SCOPE` leaves countries/providers/products populated — harmless because ChangelogTab takes `entries`/`meta` only, not `filters` (page.tsx:725).
- **`isActive` gating where present** — OverviewTab (`if (!isActive) return;` at :538) and BreakdownTab (:492) correctly skip fetches while hidden and re-fetch on re-activation.
- **URL round-trip** — `filtersToParams` (page.tsx:133) and `paramsToFilters` (:171) use a matching short-param vocabulary (`sogs`, `confirmed`, `order_srcs`, `tsf`/`tst`, `aq`/`al`, `dm`, …); round-trip is consistent. The *separate* `filterQS` (page.tsx:25, API-query serializer) uses camelCase names (`shopOrderGroups`, `confirmedOnly`) that match `db.ts::parseFilterParams` (db.ts:257/261). Two serializers, two purposes, each internally consistent.
- **`resolveRefTab("avg-costs") → "breakdown"`** is *intentional*, not a bug — asserted by types.test.ts:721. avg-costs is a hidden tab (TabNav HIDDEN_TABS), so movers are routed to breakdown instead of a dead-end. (Note: avg-costs remains reachable by direct `?tab=avg-costs` URL and renders fine; only mover ref-routing redirects away from it.)
- **`backtest_report.py`** reads only `data/backtest.parquet` (its docstring is downstream of the cutover); unaffected. Depends on `NFE/lib/{style,report}` via `sys.path` insert (line 13).
- **DAG + entrypoint.sh** are post-cutover-aware — DAG docstring (lines 15-19) names `data/processed/*.parquet`; entrypoint full-syncs `data/` then runs `node server.js`. Correct.

---

## Needs runtime check (can't confirm statically)

1. **`backtest.py` depends on a `has_cost` column** (backtest.py:73, `.filter(pl.col("has_cost"))`). `audit.py` does not assert `has_cost` exists in `processed/`. If the post-cutover pipeline renamed/dropped that column, backtest's L1 agg silently produces zero rows. Confirm `has_cost` is in the processed schema (the commit notes a `--weeks 2` smoke completed, so it likely exists, but it's unverified here).
2. **audit.py baseline_weeks check vs commit message mismatch.** Commit `0001b36` says the baseline check was "tightened to `== 5`", but the working-tree check is the soft band `bw in (5, 6)` (audit.py:528-531) with a comment still referencing the old `6`. Either the tightening was reverted or the commit message overstated it. Run `python audit.py` to confirm current PASS/FAIL behavior and decide whether to tighten to `== 5` per the pipeline contract (`BASELINE_WEEKS = 5`, noted at audit.py:533).
3. **Over-fetch impact** (Medium finding above) is a behavioral claim; a quick devtools network trace while changing a filter on Overview would confirm the hidden tabs re-fire.
