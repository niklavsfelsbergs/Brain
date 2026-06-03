# S149 — SCM Transit Times tab rework (ebe0a532)

**Player:** Jebrim. **Born + closed:** 2026-06-03 (single-session quest).
**Deliverable:** shipped + committed + pushed to `picanova/bi-analytics` main @ `ef71812`.

Reworked the Transit Times tab of the Shipping Costs Monitoring dashboard
(`bi-analytics-main/NFE/dashboards/shipping_costs_monitoring_nextjs`) across a
sequence of taste-iterations. All work in the external repo; this entry is the
brain-side record.

## What was asked / done (in order)

1. **Corridors table fills the gap down to the chart** — table was leaving blank
   space below it. First attempt (`flex-1` on the scroll area) was wrong: with grid
   `stretch`, the *table* became the tallest item and drove the row, so it grew
   long with no scrollbar. **Corrected** with the match-sibling-height trick: left
   cell `lg:relative`, corridor card `lg:absolute lg:inset-0` → table contributes
   zero intrinsic height, the distribution/outcome stack on the right drives the
   row, and the table's `flex-1 overflow-y-auto` now has a bounded parent (scrolls).
2. **Histogram defaults to % (density)** with a density/count toggle; Y-axis +
   tooltip switch accordingly. Pure client transform (`n/total`); no data change.
3. **Histogram reference lines** — dropped p99; added p85 + p95 lines alongside the
   selected-stat marker, deduped on overlap. Bumped chart top margin 12→22 after the
   percentile labels clipped at the top edge.
4. **Histogram tooltip** — added a cumulative-share line (running % over ascending
   bins) via a custom tooltip component.
5. **Trend strip** — gave it its own stat switch (Median/Avg/p85/p90/p95, default
   p85), decoupled from the tab-level STAT selector; added per-point value labels
   (`LabelList`); bumped top margin 8→16.
6. **Data layer** — p90 didn't exist anywhere. Added `{q:0.90}` to the trend route's
   binned-CDF set + `stat_p90_*` selects, the `stat_p90_*` fields on
   `TransitTrendPoint`, and a `TransitTrendStatKey` type. (Followed the existing
   inline-SQL-via-helper convention in the route; no separate sql/ file.)
7. **Business days = default** daysVariant (flipped default + URL read fallback + the
   non-default URL-write guard, 3 coupled spots in `page.tsx`).
8. **p85 = default stat**, then second KPI card swapped p99 → p85 → finally
   **Shipments (in scope)** per the last iteration.

## Idle-time question (parked, not built)

Asked whether the dashboard pulls a produced date to add an idle-time corridor
column. **Answer: no.** `query_mart.sql` pulls only `order_date`
(= `shop_order_created_date`, order-created not produced), `transit_time_days`,
`transit_time_business_days`, `current_shipping_status`. No produced or
carrier-received timestamp → idle (produced→carrier-received, per the S145 SLA
2-segment model) is a pipeline + parquet-regen + deploy change, not a FE column.
Offered to ground the mart fields first (shipping-agent), build now, or drop.
**Principal chose: drop idle, transit only.** Reachable later; parked, not blocked.

## Files touched (bi-analytics, committed ef71812)

`src/lib/types.ts`, `src/app/api/transit/trend/route.ts`, `src/app/page.tsx`,
`src/components/{TransitCorridorTable,TransitHistogram,TransitTrendStrip,TransitTimesTab,TransitKPIRow}.tsx`.
Verified clean `tsc --noEmit` after each change. `next lint` is not configured for
the project (drops into an interactive setup prompt) — tsc was the type signal.

## Pending external actions

None pending. Committed `ef71812` and pushed to `origin/main` on explicit principal
authorization. Dependabot vuln notice on push is pre-existing repo noise, unrelated.
