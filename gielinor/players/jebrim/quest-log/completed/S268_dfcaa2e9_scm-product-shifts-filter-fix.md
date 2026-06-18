# S268 — SCM product-shifts tab errors under order-source / production-site filters

**Player:** Jebrim · **sid8:** dfcaa2e9 · **Status:** completed (shipped + committed + pushed)

## Ask

Principal: "in SCM the product shifts tab is not working if filters are selected" — narrowed mid-turn to **order source** and **production sites** specifically.

## What happened

Traced the bug in `bi-analytics-main/NFE/dashboards/shipping_costs_monitoring_nextjs`.

**Root cause (structural).** Selecting a processed-only filter — `order_source`, `production_site`, or `shop` — sets `hasProcessedOnly = true` in `src/lib/shifts.ts` (`grainConfig`), which swaps the shift query's FROM source to `processedAsDaily(...)`. That subquery emits the **daily** tier schema (`packagetype` + `shop_order_groups`), with **no `product` and no `basket_size` column**. The product-grain query references both (GROUP BY / SELECT / joins on `product`, the basket-size filter on `basket_size`), so DuckDB threw *column not found* → the `/api/product-shifts` route 500'd → the component's `.catch()` left `rows = []` → empty tab.

Only the **product** tab broke: routing groups by `packagetype` and carrier has no dim, both present in `processedAsDaily`. `product` is the SOG-exploded column that lives only in the `daily_product` tier.

**Fix (2 files).**
- `src/lib/db.ts` — new `processedAsDailyProduct(from, to)`: processed-tier fallback that explodes `shop_order_groups → product` and derives `basket_size = LEAST(3, len(string_split(sog, ' | ')))`, mirroring `_write_daily_product_summary` (pipeline.py:2500) so the on-the-fly result matches the `daily_product` tier.
- `src/lib/shifts.ts` — product grain uses `processedAsDailyProduct` when a processed-only filter is active; routing/carrier keep the plain `processedAsDaily`.

**Verified live** against the running dev server (:3000), May-vs-Apr 2026:

| case | result |
|---|---|
| no filter (control) | 1402 rows |
| `order_srcs=ORWO` | 208 rows, product + baseline populated |
| `sites=PCS CMH` | 92 rows |
| `order_src + site` | 65 rows |
| `basketSize=0` (All) + order_src | 248 rows |
| `shops=ORWO` | 208 rows |

All clean arrays, no 500s, `baseline_avg_cost` non-null (baseline window still read).

## Decisions

- Edited the `bi-analytics-main` tree (the live dev/build tree, dev server confirmed running there). Push remote is `picanova/bi-analytics` → push-to-main IS the SCM deploy.

## Pending external actions

None pending. Committed `5c3ca76` in bi-analytics-main, pushed to `picanova/bi-analytics` main (`a22ca52..5c3ca76`) on principal's explicit "commit and push". GitHub Actions rebuild + ship triggered.

## Next concrete step

None — quest closed.
