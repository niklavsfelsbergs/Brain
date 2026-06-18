# SCM shift-query tiering & the processed-only fallback trap

**Source:** [[S268_dfcaa2e9_scm-product-shifts-filter-fix]] (product-shifts tab fix).

## The tiers (shift query, `src/lib/shifts.ts` + `src/lib/db.ts`)

The routing/product/carrier **shift** queries pick a FROM source by grain + active filters:

- **routing / carrier grain** → `daily.parquet` (has `packagetype`).
- **product grain** → `daily_product.parquet` (SOG-exploded `product` + `basket_size`).
- **any grain + a processed-only filter** → `processedAsDaily(...)` on-the-fly aggregation of `processed/*.parquet`.

**Processed-only filters = `production_site`, `shop`, `order_source`.** These columns are what flips `hasProcessedOnly = true` and forces the per-shipment fallback. (`country` / `provider` / `packagetype` / SOG do *not* — they exist in the Tier-1 files.)

## The trap

`processedAsDaily` emits the **daily** schema (`packagetype` + `shop_order_groups`), **not** `product` / `basket_size`. So the **product** shift query, run against that fallback, referenced columns that didn't exist → DuckDB *column not found* → route 500 → empty tab. Routing/carrier were fine (they only need `packagetype`).

Fix: `processedAsDailyProduct(from, to)` — a product-grain fallback that explodes `shop_order_groups → product` (`UNNEST(string_split(sog, ' | '))`) and derives `basket_size = LEAST(3, len(...))`, mirroring `_write_daily_product_summary` (pipeline.py). Keep the two fallbacks matched to the tier they stand in for.

## Reusable rule

When a route swaps to a per-shipment **fallback** source, the fallback must reproduce the **exact schema of the tier it replaces** — same exploded dims, same measure semantics — or the consuming query breaks the moment the fallback path is taken. The bug only surfaces under the specific filter combo that triggers the fallback, so it hides from default-view testing. Test each tab under a filter from the **processed-only** class, not just the default view.
