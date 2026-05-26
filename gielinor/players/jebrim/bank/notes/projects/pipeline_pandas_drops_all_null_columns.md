# pipeline.py — pandas drops all-NULL columns at the polars boundary

**Status:** draft (harvested [[S030_2026-05-22_dashboard-gold-cutover|S030]], 2026-05-22).
**Repo:** `bi-analytics/NFE/dashboards/shipping_costs_monitoring_nextjs/pipeline.py`.

## The bug class

When `pipeline._pull_query` chunks data out of Redshift via pandas and then converts to polars (`pl.from_pandas`), **pandas drops columns that are all-NULL in the chunk**. Polars therefore receives a frame without that column. The spilled parquet for the chunk lacks it. When later chunks have non-NULL data for the same column, their spills carry it. `pl.read_parquet(spill_paths)` then chokes on schema mismatch across chunks:

```
polars.exceptions.SchemaError: extra column in file outside of expected schema: <column>
```

## How it manifested ([[S030_2026-05-22_dashboard-gold-cutover|S030]], 2026-05-22)

D1's pipeline plumbing added `cost_source` (string, enum) to `RAW_KEEP_COLS` + `write_processed`. Older months had all-NULL `cost_source` upstream (mart only recently started populating); newer months had data. Pandas dropped the column for older-month chunks; polars choked on read-back.

Fix landed as commit `eb1c2ea` on `shipping-mart-cutover`. Pattern: in `_pull_query` (`pipeline.py:285-300`), **after** the existing all-NULL float bucket-cols cast, add an analogous block for `cost_source`:

- If `cost_source` not in the pandas df columns → materialize as a `pl.Utf8` NULL column on the polars side.
- If present → force-cast to `pl.Utf8` (in case pandas inferred `object` dtype).

Both branches needed; the cast-when-present guards against dtype drift across chunks even when the column survives.

## Why this is a class, not a one-off

The bucket-cols block already in `_pull_query` (~L285-290) does the same kind of force-cast for all-NULL float columns. Same pattern: any column that *might* be all-NULL in a chunk needs this guard at the pandas → polars boundary.

**Pattern to apply for any new column added to the projection:**

1. Decide the polars dtype (`pl.Utf8`, `pl.Float64`, `pl.Int64`, ...).
2. In `_pull_query` after the existing all-NULL casts, add a block: if column missing → materialize as that dtype NULL column; if present → force-cast.
3. Both branches; don't trust pandas dtype inference across heterogeneous chunks.

## Trigger conditions to watch

- Column was just added to the SQL projection.
- Column is null-prevalent in older time windows (gradual upstream rollout).
- Column appears in `RAW_KEEP_COLS` / `write_processed`.

If all three hold, the guard is mandatory before `--refresh-full` against historical data.

## Anchor turn

[[S030_2026-05-22_dashboard-gold-cutover|S030]] / T11 of `quest-log/completed/S030_2026-05-22_dashboard-gold-cutover.md`. Commit `eb1c2ea` on `bi-analytics` `shipping-mart-cutover`.
