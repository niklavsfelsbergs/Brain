# [[S026_2026-05-22_shipping-costs-nextjs-architecture-read|S026]] D3 — Frontend tabs & components

Read of `shipping_costs_monitoring_nextjs/src/` on branch `shipping-mart-cutover`. Paths in this note are relative to that root unless prefixed otherwise.

## Page orchestration (`src/app/page.tsx`, 871 lines)

`app/layout.tsx` is a 23-line shell: imports `globals.css`, sets metadata, preloads Inter. All UX lives in `Dashboard` (default export of `page.tsx`), a single client component holding the whole dashboard.

### State (lines 256–279)

| Group | State | Owner |
|---|---|---|
| URL-backed filters | `filters: Filters` (from `getInitialFilters` → `paramsToFilters` over `window.location.search`) | drives every fetch |
| Reference data | `meta`, `filterOptions`, `metaLoading` | one-shot `/api/meta`, then per-selection `/api/filter-options` |
| Overview KPIs | `overview`, `overviewLoading` | from `/api/overview?mode=kpi` |
| UI shell | `sidebarOpen`, `error` | local |
| Breakdown navigation | `bdDims`, `bdExpandTarget`, `bdExpandChartMode`, `bdExpandCostBasis`, `bdBucketTotals` | parent-owned because they cross alert/cost-driver → breakdown drill paths |
| Cross-tab navigation hints | `alertNavSeq`, `alertInnerTabHint`, `collapseSeq` | counter-style "ping" signals; child effects watch them |
| Changelog | `changelog` | one-shot at mount, reused by Breakdown + Changelog tab |
| Lazy-mount tracking | `visitedTabs: Set<TabKey>` | seeded with the initial-URL tab |
| Transit tab-local URL state | `transitDaysVariant`, `transitStat`, `transitSelection` | lifted to page so URL serializer can persist `td`, `ts`, `th` |
| URL sync guard | `prevKeyRef`, `prevTabRef`, `urlSyncRef` | skip-first-render guard, plus tab-change → `pushState` vs filter-change → `replaceState` |

### Fetch effect choreography

Five independent effects in `Dashboard`:

1. **Mount** (`useEffect` at 422) → `fetchMeta` → seeds `meta`, computes default `from/to/baselineFrom/baselineTo` if URL had none, bumps stale `tsTo`/`shiftTsTo` to `data_bounds.max`, and **pre-warms** `/api/breakdown?level=total` fire-and-forget so the first Breakdown visit hits a warm temp table (`page.tsx:381`).
2. **Cascading filter options** (430–451) — debounced 100ms, refetches `/api/filter-options` on any dim-selection change so the sidebar shows only valid options for the current intersection.
3. **Overview KPIs** (454–462) — `filters.activeTab === "overview"` gate, debounced 150ms. Calls `fetchOverview` with `mode=kpi`. KPIs use the *baseline* range as the prior comparison (`priorFrom/To = baselineFrom/To`) while YoY is auto-derived via `computeComparisonRanges` (line 42).
4. **URL sync** (316–338) — every render after the guard; tab change → `pushState`, anything else → `replaceState`. Skips persisting chart-range presets that match the auto default so old URLs don't pin charts at a stale data max (159–166).
5. **`popstate` handler** (341–349) — restores the tab from URL on back/forward.

Each tab does its **own** chart-data fetches inside its component, gated on `isActive` for the visible tabs that have expensive data (Overview, Breakdown). KPIs are the only cross-tab fetch in the page.

### URL param contract

`filtersToParams` (132–168) ↔ `paramsToFilters` (170–217). Short codes — the contract worth memorising:

| Param | Field |
|---|---|
| `from`, `to` | analysis range |
| `bfrom`, `bto` | baseline range |
| `tsf`, `tst` | main Chart Range (`tsFrom`/`tsTo`) — skipped when equal to auto default |
| `stsf`, `stst` | shift-chart Chart Range (`shiftTsFrom`/`shiftTsTo`) — Cost Drivers / Alerts |
| `countries`, `providers`, `products`, `sogs`, `sites`, `shops`, `order_srcs` | comma-joined dim selections |
| `cs`, `ps`, `pts`, `sogs_s`, `site_s`, `sh_s`, `os_s` | per-dim search box text (cascading filter UX) |
| `confirmed`, `hideLowVol` | bool flags |
| `tab` | active tab (omitted when `overview`) |
| `aq`, `al` | Alerts queue (`early_warning`/`confirmed`) + lookback (`8w`/`6m`) |
| `dm` | dismissed-mover keys, comma-joined |
| `bd` | Breakdown dimension order (`country,provider,package,product` etc.) — handled separately at 319–321 |
| `td`, `ts`, `th` | Transit Times tab-local state (days variant, stat, heatmap selection as `"<country>|<provider>"`) |
| `cdi` | Cost Drivers inner tab — written directly from `CostDriversTab` via `history.replaceState` (`CostDriversTab.tsx:114-122`) |

### `OLD_TABS` redirect

`paramsToFilters:192-204`. Legacy tab keys from the pre-cutover dashboard:

- `countries`, `corridor-costs`, `providers`, `packages`, `products` → `breakdown`
- `carrier-shifts`, `shifts`, `product-shifts` → `cost-drivers`

Unknown values fall through to the whitelist check; anything not on the whitelist silently drops (no error), and the dashboard opens on `overview`.

### `TAB_SCOPE` and `TAB_FILTERS` mechanics (`src/lib/types.ts:499-528`)

- `TAB_SCOPE: Record<TabKey, (f: Filters) => Filters>` — per-tab pure function that zeroes filter fields the tab can't honour. E.g. `outliers` zeroes `products` (it's a packagetype filter that doesn't apply to per-shipment outliers), `avg-costs` zeroes most low-level dims, `alerts/changelog/deviations` zero the SOG / sites / shops / order-source group.
- `TAB_FILTERS: Record<TabKey, Set<string>>` — visibility map keyed by sidebar section name (`dates`, `baseline`, `chartRange`, `shiftChartRange`, `countries`, `providers`, `products`, `sogs`, `sites`, `shops`, `sources`, `buckets`). `Sidebar.tsx:38` reads it via `TAB_FILTERS[filters.activeTab]` and conditionally renders each section.

In `page.tsx:299-307`, `tabFilters` is a memoised `Record<TabKey, Filters>` built by running every tab through `TAB_SCOPE` on top of `baseResolved`. Each tab receives its own correctly-scoped filter copy, so a tab kept alive via `display:none` doesn't get wrongly-scoped updates from a different active tab.

### `resolveSearchFilters` and the cascading-filter mechanism

Two layers:

1. **Cascading options** — when any dim selection changes, `/api/filter-options?countries=...&providers=...` returns the intersection (`filterOptions`). The sidebar prefers `filterOptions.<dim>` over `meta.<dim>` so options shrink as the user narrows.
2. **Live search** — typing in a dim's search box sets `filters.<dim>Search`. `resolveSearchFilters` (page.tsx:65-130) maps that text into an explicit item list **only when the user hasn't already picked items**: if `countries=[]` and `countrySearch="DE"`, it expands to `countries=[matches]`. If there are no matches, it sets `["__NOMATCH__"]` (sentinel that produces an empty result downstream — see "Gotchas"). Search text never overrides explicit selections; the search input just narrows the visible sidebar list in that case.

`resolveSearchFilters` runs before `TAB_SCOPE`, so per-tab zeroing happens on top of the resolved search. The two-stage pipeline lives in `baseResolved` (page.tsx:293) → `tabFilters` (299).

### Lazy mount & state preservation

Every tab is `lazy(() => import(...))` (page.tsx:12-22).

- `visitedTabs` starts with the initial-URL tab.
- A tab is mounted the first time it becomes active; it stays mounted forever via `style={{ display: filters.activeTab === "<key>" ? undefined : "none" }}` (lines 701-803).
- Each tab is wrapped in `<Suspense fallback={<TabLoadingFallback/>}>`.
- `Overview` and `Breakdown` receive an `isActive` prop and gate their heavy fetches on it — they remount-quiet but won't refetch while hidden (`OverviewTab.tsx:526`, `BreakdownTab` similar).
- Alert navigation (page.tsx:527) eagerly adds `"breakdown"` to `visitedTabs` *before* the render so the drill lands in a mounted breakdown in the same render cycle.

This is the centerpiece of "expensive UX state survives tab switches": expanded rows in Breakdown, granularity choices, pinned tooltips on cost charts, sort state — all preserved because the React subtree is never unmounted after first visit.

### Cross-tab navigation handlers

- `handleAlertNavigate` (page.tsx:468-546) — biggest handler. Computes `from/to/baselineFrom/baselineTo` from the alert's period (single ISO date → 7-day analysis window, range → start..start+6d capped at last full Sunday; baseline = 35 days before start). Picks a dimension order + chart mode by alert type (`product_shift` → `[country,product,provider,package]` with `share` chart; `routing_shift` → `[country,package,provider,product]`; `rate_spike` / `creep` → cost basis pinned to `real`). Clears all filter selections, bumps `alertNavSeq`, sets `alertGranHint:"weekly"`, and unsets `baselinePreset` (the alert overrides it).
- `handleBreakdownSetFilters` (548-574) — "See in Overview" reverse — translates a composite breakdown key (`"DE|DHL|PKT"`) into the matching dim filters using the current `bdDims` order.
- `handleDriverNavigate` (576-595) — Cost Drivers row click: pre-populates dim filters; routing shifts use `products` (packagetype), product shifts use `shopOrderGroups`.
- `handleDrillToBreakdown` (599-609) — Cost Drivers → Breakdown with pre-expanded rows.

## Tab components

### Overview (`OverviewTab.tsx`, 1320 lines)

Heaviest tab. Renders the big trend chart with multi-line cost / shipment-volume composition. Calls `/api/overview?mode=chart`. Local state controls: granularity Mo/Wk/Day (`gran`, auto-bumps to `weekly` on `alertNavSeq` rise, 471-476), metric type `total | avg | quota | buckets` (479, `metricType`), cost-basis visibility (`coalesce|real|expected`, multi-select with min-one invariant), Exp.(real)/YoY/Shipments/YoY-Shipments toggles, pinned tooltip snapshots (`pinnedPoints`), drag-zoom (`dragStartIdx/dragEndIdx` → `zoomRange`). When `metricType === "buckets"` it mounts `<BucketsTrend>`; when `"quota"` it switches the two visible lines to the dedicated `real_cost_quota` / `combined_cost_quota` data keys (lines 33-36) and renders `QuotaTooltipBody`. Period highlight bands rendered via shared `<PeriodBands>`.

### Alerts (`AlertsTab.tsx`, 1276 lines)

Two-queue incident system on top of `/api/alerts`. Fetches active + resolved (`?resolvedWeeks=26`) in parallel on mount (301-302), plus `/api/alerts/dismissed` for the persistent dismissed-issue map (205). Filters: priority bands (Critical/High/Medium/Low), alert-type multi-select with double-click-to-solo, confidence ≥ 75% toggle, creep lookback 8w/6m. Inline chart on expand — `CostTrend` for rate/creep/etc., `CarrierShareChart` for shift alerts (cost overlay + share lines), dual-line trend (`/api/deviations`) for deviation alerts. `onNavigate` callback is `page.tsx:handleAlertNavigate`.

### Changelog (`ChangelogTab.tsx`)

CRUD against `/api/changelog`. Owns no fetch; the parent (`page.tsx:278`) loads the list once at mount, passes it down with an `onUpdate` callback. Entries fed into Breakdown and CostTrend as reference lines when scope matches.

### Cost Drivers (`CostDriversTab.tsx`)

Wrapper with 4 inner tabs + top drivers/savers header. Calls `/api/cost-drivers-top` for the headline list (140) using **date-only params** (126-133) so clicking a driver to filter doesn't collapse the list. Inner tab is persisted in URL as `cdi=` via direct `history.replaceState` (114-122) — bypasses the page-level URL sync. Inner tabs:

- **Rate Changes** (`RateChangesTable.tsx`) — `/api/rate-changes`, expandable per country+provider to packagetype level (`level=package`).
- **Carrier Shifts** (`CarrierShiftsTable.tsx`) — `/api/carrier-shifts`, country-level provider share movement.
- **Routing Shifts** (`ShiftsTable.tsx`) — `/api/layer2`, country+packagetype provider share movement. (Note: endpoint name is `layer2` while the component / tab is `ShiftsTable` / "Routing Shifts".)
- **Product Shifts** (`ProductShiftsTable.tsx`) — `/api/product-shifts?basketSize=...`, product-mix composition with basket-size filter for order inclusion.

All four inner tables accept `costBasis`, `chartGran`, `onDrillToBreakdown`, `onSetFilters`, `collapseSeq` — uniform contract from the Cost Drivers wrapper.

### Breakdown (`BreakdownTab.tsx`, 1426 lines — the second-biggest component)

Hierarchical drill-down across 4 draggable dims: country, provider, package, product. Reads `dims` + `onDimsChange` from parent so the order survives tab switches. Owns `expanded: Set<string>` (composite-key set) with sessionStorage persistence (`ss` reads/writes at 302-329) so expanded state survives reloads. Data fetches:

- `/api/breakdown?level=total` + `/api/breakdown?level=0` in parallel for the headline + level-1 rows (509-510).
- `/api/breakdown-sparklines` for the 60-pixel SVG sparklines per row (557, 590, 637).
- `/api/breakdown?level=N` on row expand (621).

Per-row inline chart unmounts/mounts as `visibleCharts: Set<string>` toggles. Chart mode is one of `"cost" | "share" | "buckets" | "quota"` — `cost` mounts `CostTrend`, `share` mounts `DimensionShareChart` with `shareDimension` = next dim down, `buckets` mounts `BucketsTrend`, `quota` mounts `QuotaTrend`. Cost basis `real_expected | real`; column preset `cost | quota | share | all`. The total row across the top is collapsible (`totalExpanded`). Reports total-row bucket sums up to the parent via `onBucketTotalsChange` so the **sidebar can show live € per bucket** while Breakdown is the active tab.

### Deviations (`DeviationsTable.tsx`)

`/api/deviations` for the corridor table; expand-row fires a second request with `expandCountry`/`expandProvider` for the per-package breakdown + dual-line trend. Hidden from `TabNav` by default (`TabNav.tsx:6` `HIDDEN_TABS`).

### Outliers (`OutliersTable.tsx`)

`/api/outliers?thresholdScope=global|range` — provider groups with sortable detail tables, configurable max rows per provider.

### Avg Costs (`AvgCostsHeatmap.tsx`)

Per-corridor heatmap, `/api/avg-costs?gran=...&periods=...`. Hidden from `TabNav` by default.

### Benchmarks (`BenchmarksTab.tsx`)

`/api/benchmarks` — switching-opportunity rows with summary cards, priority/effort filters, confidence ≥ 75% toggle. Per-row expand mounts a `CostTrend` for the current provider's corridor. Hidden from `TabNav` by default.

### Completeness (`CompletenessGrid.tsx`)

`/api/completeness?gran=...&periods=...`. Per-cell click builds an `/api/export?...` URL for shipment-level CSV download (line 191).

### Transit Times (`TransitTimesTab.tsx`, 255 lines — new this branch)

The transit subtree is the cleanest split-out in the codebase. Three independent fetch effects in the tab (89-156):

1. **Heatmap** — `/api/transit/heatmap` on `baseQS` only. Deliberately *not* narrowed by the heatmap selection so all corridors stay visible when one is clicked.
2. **KPIs + Completeness + Histogram** — `Promise.all` against `/api/transit/kpis`, `/api/transit/completeness`, `/api/transit/histogram` on `scopeQS` (= `baseQS` + `th_country`/`th_provider` from heatmap selection). The histogram fetch alone gets `td=calendar|business`; the other two return both variants in one payload (`kpis.p50_calendar`, `kpis.p50_business`, ...).
3. **Trend** — `/api/transit/trend?gran=...&tsFrom=...&tsTo=...` on `scopeQS` + granularity + chart range.

Tab-local state (`daysVariant`, `stat`, `selection`) lifted to `page.tsx` so the URL serialiser persists it. `granularity` is purely local. Each panel is a small dedicated component:

- `TransitKPIRow` — selected stat | p99 | delivered % | est. unlogged %. `pickStat` switches on suffix `_calendar` / `_business`.
- `TransitCorridorTable` — country × provider rows with heatmap-coloured cells using a sequential blue→amber→rose ramp (`rampColor` at lines 32-49). Cells with `n < 30` are stripe-dimmed (`LOW_CONF_N = 30`). Click → `onSelect({country, provider})` → ANDs into all other panels.
- `TransitHistogram` — 0..13 day bins plus a `14+` tail bin, reference lines at the selected stat and p99.
- `TransitCompleteness` — stacked outcome bar (delivered / in-flight / est. unlogged / exception) over corridor calendar-p95 thresholds, plus a coverage bar (non-null transit_time_days).
- `TransitTrendStrip` — single-line trend with Mo/Wk/Day granularity toggle in the panel header.

The whole tab uses `DELIVERED`-only data for stats. Heatmap selection ANDs with the sidebar filters; clicking the selection badge clears it.

### Buckets / Quota (new this branch)

Not their own tabs — modes inside other tabs:

- **`BucketsTrend.tsx`** (636 lines, new) — multi-line composition chart over the 11 cost buckets (`bkt_base_rate`, `bkt_truck_charges`, `bkt_fuel_surcharge`, `bkt_remote_area`, `bkt_peak_demand`, `bkt_oversize_overweight`, `bkt_residential`, `bkt_other`, `bkt_unclassified`, `bkt_discounts`, `bkt_credit_note`). Discounts + credit-note flagged as reducers (`REDUCER_BUCKETS`). Metric type `total | avg | share`. Fetches `/api/breakdown-buckets`. Used inline by Breakdown's bucket-chart mode and by Overview's `metricType === "buckets"`.
- **`QuotaTrend.tsx`** (277 lines, new) — pair of lines (`real_cost_quota`, `combined_cost_quota`) with their own tooltip showing routing cost, real cost, revenue, coverage. `/api/breakdown-quota`. Used inline by Breakdown's quota chart mode.
- Both are lazy-imported by `BreakdownTab.tsx:10-11` and by `OverviewTab.tsx:8`, with identical filter-prop signatures so they slot in interchangeably.
- The **sidebar Cost Buckets filter** (`Sidebar.tsx:681-841`, gated by `visible.has("buckets")` — only Breakdown) lets the user pick a subset of buckets; subset filtering propagates as `buckets=` to the API. When a strict subset is active, `BreakdownTab` swaps the coloring of Real columns to emphasise that the values are "real cost minus excluded buckets" (`BreakdownTab.tsx:333-337`).

## Shared components

### `CostTrend.tsx` (1095 lines — the centerpiece)

Memoized component used by ~every tab that shows a single-corridor or single-scope cost trend. API routing at lines 342-349 picks one of `/api/generic-trend`, `/api/product-trends`, `/api/packagetype-trends`, `/api/trends`, `/api/country-trends` based on which dim props are set, and optionally fetches `/api/trend-shares` for the next-dimension share table that lives inside the tooltip. Headline features:

- **Drag-to-zoom** via `wasDrag` ref + `refAreaLeft/Right` (lines 581-619). Recharts-native, no pixel math — operates on data indices and slices `chartData` to `visibleData` via `zoomRange`. `Reset zoom` button + double-click both restore.
- **Click-to-pin tooltip** vs **click-to-export** disambiguation: same click handler; if a drag happened it zooms, otherwise it pops the export-confirm pill (`exportConfirm`, 555). Confirming hits `/api/export?...` (309).
- **Regression lines** (655-754). Linear OLS on visible indices; renders the fit as an extra Line plus a custom slope label via `<Customized>` showing `+0.xxx/<gran>`. Per-cost-basis (`coalesce`/`real`/`expected`).
- **Share tooltips** — when `shareDimension` is set, the tooltip extends with a per-period table of next-dimension shares (volume %, contribution, R+E, R%, Real, Exp, Weight) sourced from `/api/trend-shares` (line 360). `SharesSection` (103) does the rendering.
- **Period bands** — analysis range and baseline range overlaid via `<PeriodBands>` for visual context.
- **Changelog reference lines** — `changelogEntries` prop renders amber dashed verticals at matching dates.
- **End-of-line labels** via `<Customized>` to avoid overlap.

### `KPIRow.tsx` (446 lines)

Top-of-page 4-card KPI row + period-context header line + dismissible mover pills:

- Cards: Avg Cost, Total Cost, Shipments, Invoiced %. Cards 2 & 3 inverted-colour for "more shipments is good." Invoiced colour-bands at 85% / 50%.
- Period-context header: prints `"Period: <range>  Prior: <range>  YoY: <range>"` using `fmtRange` (31-48): same-month → `"Mar 1-27, 2026"`, cross-month → `"Jan 1 - Mar 27, 2026"`, cross-year → year-tagged both ends, no end → `"Mar 2026"`. KPIs include `period_label` + `period_end` etc. so the *server* date-matches incomplete periods (e.g. current month-to-date vs same-day-range last month) — the component just renders.
- Mover pills: filter to `impact > 0`, dismissed-aware. Per pill: arrow + `+Xk` EUR + short alert-type label + corridor. Click → `onMoverNavigate(tab, country, provider, product, period)` → goes through `handleAlertNavigate`. Dismiss → updates `dismissedMovers` → URL `?dm=`.

### `Sidebar.tsx` (842 lines)

Two top blocks always rendered (header, scrollable body), one sticky bottom (Collapse all rows / Reset all filters). Body contents are gated on `TAB_FILTERS[activeTab]`:

- **Period** + **Baseline** combined; baseline has a preset dropdown (`BASELINE_PRESETS`) plus custom date inputs when preset = "Custom". An effect (43-52) re-derives baseline from preset+from/to so changing the period re-derives baseline automatically unless the preset is null.
- **Chart Range** — single section, swaps backing fields per tab (`tsFrom/To` vs `shiftTsFrom/To`) based on `visible.has("chartRange")` vs `visible.has("shiftChartRange")`. Presets 1M..24M anchored on `meta.date_bounds.max`, plus a "Period" button that pins chart range to the analysis range.
- **Dim filters** — `FilterSection` (memoised at 478) per dim. Each section has its own collapse, search-icon → input toggle, select-all, and per-item checkboxes. Selection rendered as a count badge with an inline clear.
- **Cost buckets** (Breakdown-only) — `BucketsFilter` (681). Mirrors `FilterSection` structurally but adds per-row colour swatches and optional € totals (passed in as `bucketTotals` from Breakdown). Reducers (Discounts, Credit Note) rendered below a divider.

### `DateRangePicker.tsx`

Pop-over calendar (portal-rendered, UTC-anchored helpers at top of file). Used inside Period and inside the Baseline custom block.

### `PeriodBands.tsx`

`<Customized>` helper for Recharts that draws analysis + baseline shaded rectangles between data points (offset by half-bandwidth so they sit between, not on, points). Imported by `OverviewTab`, `CostTrend`, `BucketsTrend`, `QuotaTrend`, `TransitTrendStrip`-adjacent code.

### `DimensionShareChart.tsx`

Stacked-share line chart with a cost overlay (single neutral grey line). Reusable for any dimension via the `dimension` prop. Uses the shared `useChartZoom` hook (the same hook `CarrierShareChart` uses) — note the share-only/cost-overlay variants share scope-cost data keys `_scopeRE/_scopeR/_scopeE`. Muted palette to keep cost line readable.

### `CarrierShareChart.tsx`

Specialisation of the share-chart pattern for provider shares in alerts. Adds `er` (Expected-for-Real) as a fourth cost basis option vs `DimensionShareChart`'s three.

## Mart cutover delta (frontend)

| Surface | Change |
|---|---|
| New tab | **Transit Times** (`TransitTimesTab` + 5 sibling panels) — entire subtree new, 1000+ lines added. Reads `/api/transit/*` (heatmap/kpis/completeness/histogram/trend). |
| New chart modes | **Buckets** (`BucketsTrend`, 636 lines new) and **Quota** (`QuotaTrend`, 277 lines new). Used inline by Breakdown's per-row chart and by Overview's metric-type switcher. |
| Sidebar | **Cost buckets filter** added (`BucketsFilter`, 192-line diff to `Sidebar.tsx`). Live € totals fed up from `BreakdownTab` via `onBucketTotalsChange`. New `buckets` visibility flag in `TAB_FILTERS`. |
| Breakdown | +270 lines. New `chartMode = "buckets" | "quota"` branches, three new columns (`real_cost_quota`, `cost_quota`, `cost_quota_b`), a `colPreset` axis (`cost | quota | share | all`), bucket-aware Real-column coloring when a subset of buckets is active. |
| Overview | +297 lines. New `metricType = "quota" | "buckets"`, dedicated quota line config + tooltip, end-label resolver extended to fan out across both modes. |
| KPIRow | +183 lines. New `cost_quota` / `real_cost_quota` cards (current vs prior vs YoY) and revenue/avg-revenue derivations. |
| Page | +97 lines. `TransitDaysVariant` / `TransitStatKey` / `TransitSelection` lifted to page; `bdBucketTotals` plumbed through; new URL params `td`, `ts`, `th`. `getInitialTransitState` (225-243), `getInitialDims` (245-254). |
| Types | `src/lib/types.ts` +178 lines: `TabKey` adds `transit`; `TABS` array gains the Transit entry; `TAB_SCOPE`/`TAB_FILTERS` extended; bucket constants `ALL_BUCKETS`/`REDUCER_BUCKETS`/`BucketKey`; transit type bundle. |
| Lib | `src/lib/colors.ts` +44 lines (bucket palette + `bucketLabel`). `src/lib/db.ts` +13 lines (mart pivot to the new tables, not frontend-visible). |

No tabs were removed in the diff; the legacy tab keys live on only in `OLD_TABS` redirects.

## Gotchas / non-obvious bits

1. **`__NOMATCH__` sentinel.** `resolveSearchFilters` writes `["__NOMATCH__"]` into a dim list when a search query has zero matches and no explicit selection (`page.tsx:83`). API routes must treat this string as "definitely no rows." Easy to break if a future contributor refactors search without preserving the sentinel.
2. **`display:none` over conditional render.** Every tab is mounted on first visit and never unmounted. State (expanded rows, drag-zoom range, pinned tooltips, sort/granularity choices) is preserved by *React subtree continuity*, not by storage. Sessions store extras (`BreakdownTab`'s `ss`) but the primary mechanism is the `style={{display:...}}` swap at `page.tsx:702-803`. **Implication:** any tab that needs to re-fetch on `from/to` change must take `isActive` as a fetch-gate prop, else hidden tabs hammer the API on every filter tweak. Only `OverviewTab` and `BreakdownTab` currently honour `isActive`; other tabs assume their data fetches are cheap enough.
3. **`alertNavSeq` is a ping counter, not a state.** Children watch for it to **rise** (e.g. `OverviewTab.tsx:471`) and react once. Same pattern with `collapseSeq` and `localNavSeq` inside Cost Drivers. Don't read its value — only diffs matter.
4. **URL sync split brain.** Most params route through `filtersToParams` in `page.tsx`. But `cdi` (Cost Drivers inner tab) is written from *inside* `CostDriversTab` via direct `history.replaceState` (lines 114-122). This works because the page-level URL sync uses `replaceState` for filter-only changes too, so neither stomps on the other unless tab change is concurrent — which it can't be for `cdi` because `CostDriversTab` only writes while it's visible. Still worth knowing if a third party adds a third URL-writing site.
5. **Stale `tsTo` bump-forward on meta load.** `fetchMeta` (page.tsx:376-379) silently bumps `tsTo` / `shiftTsTo` forward to `data_bounds.max` if the URL pinned a now-stale value. Same logic applies to chart-range default-skip in `filtersToParams:158-167`. A user who deliberately wants a historical chart range needs to choose a `tsTo` strictly *below* the new data max, or the auto-default-skip will keep the URL clean.
6. **Tab-change → `pushState`, filter-change → `replaceState`.** Back/forward buttons navigate tabs only; they don't replay filter history. Intentional — the `popstate` handler at line 342 reads only `tab`.
7. **Pre-warming Breakdown.** `fetchMeta` fires `/api/breakdown?level=total&...` and ignores the response — purely to warm a server-side temp table so the first real Breakdown visit is fast. Removing this line would visibly slow the first drill (`page.tsx:381`).
8. **`HIDDEN_TABS` in TabNav.** `TabNav.tsx:6` hides Deviations, Avg Costs, Benchmarks from the visible tab strip. They're still routable via URL (`?tab=deviations`), still mounted on first visit, still functional — just intentionally not advertised. A reader who only reads `TabNav` could miss that those tabs exist at all.
9. **`/api/layer2` for Routing Shifts.** The endpoint name lags the rename. The UI says "Routing Shifts" (`ShiftsTable.tsx`); the API route is still `layer2`. Not a bug, but trip-up potential.
10. **`alertGranHint` is one-shot.** Alert nav sets `alertGranHint:"weekly"`, child tabs read it once (e.g. `CostDriversTab.tsx:85-86`) and then own the granularity locally. It's never re-cleared — but once `chartGran` has been set locally, the hint is moot. The string lives on in `filters` until the next reset.
11. **Cascading filter request is debounced 100ms; KPI fetch is debounced 150ms.** Different debounces for different cost surfaces. Anyone retiming these should keep KPI > filter-options, else a fast typist can refetch KPIs against an in-flight option set.
12. **Sidebar shows live € per bucket only when Breakdown is active.** `bdBucketTotals` is reported by `BreakdownTab` via `onBucketTotalsChange`; the Sidebar reads it via `bucketTotals` prop. If the user is on a different tab, those totals are stale — currently OK because the sidebar Buckets section is only visible on Breakdown anyway (`TAB_FILTERS["breakdown"]` is the only set containing `"buckets"`).
13. **`computeComparisonRanges` (page.tsx:42) vs `kpis.prior_*` from the server.** Two different "prior" concepts: page-level YoY uses the auto-derived `computeComparisonRanges` for the chart; KPIs use the user-controlled `baselineFrom/To` (passed as `priorFrom/To`) for the cards. Don't conflate.

## Component file index

| File | Lines | Role |
|---|---|---|
| `app/layout.tsx` | 23 | Shell |
| `app/page.tsx` | 871 | Dashboard orchestration |
| `components/TabNav.tsx` | ~110 | Tab strip + scroll fade + help tooltip |
| `components/Sidebar.tsx` | 842 | Filters, period, chart range, buckets |
| `components/KPIRow.tsx` | 446 | KPI cards + mover pills + period context |
| `components/OverviewTab.tsx` | 1320 | Main trend chart + composition |
| `components/AlertsTab.tsx` | 1276 | Two-queue incident table + inline charts |
| `components/BreakdownTab.tsx` | 1426 | 4-dim hierarchical drill-down |
| `components/CostDriversTab.tsx` | ~600 | Wrapper + Top Drivers/Savers |
| `components/RateChangesTable.tsx` | ~400 | Inner tab |
| `components/CarrierShiftsTable.tsx` | ~250 | Inner tab |
| `components/ShiftsTable.tsx` | ~250 | Inner tab (routing) |
| `components/ProductShiftsTable.tsx` | ~300 | Inner tab |
| `components/CostTrend.tsx` | 1095 | Shared trend chart, drag-zoom, regression, share tooltip, export |
| `components/DimensionShareChart.tsx` | ~700 | Shared share chart |
| `components/CarrierShareChart.tsx` | ~700 | Alert-specific share chart |
| `components/PeriodBands.tsx` | ~110 | Recharts customised band overlay |
| `components/DateRangePicker.tsx` | ~400 | Portal calendar |
| `components/DeviationsTable.tsx` | ~600 | Hidden by default |
| `components/OutliersTable.tsx` | ~350 | Per-provider outliers |
| `components/AvgCostsHeatmap.tsx` | ~400 | Hidden by default |
| `components/BenchmarksTab.tsx` | ~650 | Hidden by default |
| `components/CompletenessGrid.tsx` | ~450 | Per-provider real-cost coverage |
| `components/ChangelogTab.tsx` | ~400 | CRUD |
| `components/TransitTimesTab.tsx` | 255 | NEW — Transit subtree wrapper |
| `components/TransitKPIRow.tsx` | 139 | NEW |
| `components/TransitCorridorTable.tsx` | 197 | NEW |
| `components/TransitHistogram.tsx` | 142 | NEW |
| `components/TransitCompleteness.tsx` | 113 | NEW |
| `components/TransitTrendStrip.tsx` | 133 | NEW |
| `components/BucketsTrend.tsx` | 636 | NEW — used inline by Breakdown + Overview |
| `components/QuotaTrend.tsx` | 277 | NEW — used inline by Breakdown + Overview |
