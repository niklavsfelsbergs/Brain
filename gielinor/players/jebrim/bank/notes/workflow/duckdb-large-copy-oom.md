# DuckDB OOM on large COPY-to-parquet joins — config the connection, don't trust the comment

**As of:** 2026-05-25 (S069). **Source:** `Documents/GitHub/bi-analytics/NFE/dashboards/shipping_costs_monitoring_nextjs/pipeline.py`.

When a Polars pipeline offloads a big join/aggregation to DuckDB and writes it via `COPY (...) TO '...' (FORMAT PARQUET)`, an in-memory connection (`duckdb.connect(":memory:")`) will OOM (`OutOfMemoryException: Allocation failure`) at scale unless it's explicitly configured. Three levers:

1. **`SET temp_directory='<dir>'`** — without it the connection has no reliable spill target; the hash join + COPY buffer fight for RAM. This is the one that actually enables "disk spilling."
2. **`SET memory_limit='NGB'`** — bounds the build so it spills instead of grabbing ~80% of RAM and colliding with resident Python frames.
3. **`SET preserve_insertion_order=false`** — the specific lever for a large COPY-to-parquet. With it on (the default), DuckDB buffers the whole result to preserve row order — a known OOM amplifier on big exports. Safe to disable whenever the output parquet's row order isn't relied on downstream (read back by column / aggregated).

**The trap that bit us:** the connection had a comment claiming "DuckDB hash-joins on parquet files with automatic disk spilling and is rock-solid for this size" — but it set *none* of the above, while a sibling connection in the same file set `memory_limit` + `temp_directory`. A comment asserting a property is not the property. It survived until the source mart ~doubled ([[2026-05-23-disk-absence-needs-non-gitignore-aware-listing]] era / S068 reload: floor really 2023, ~18M-row fact) and crossed the threshold.

**Rule:** any `:memory:` DuckDB connection doing a large COPY/join in these dashboards gets all three SETs. When you find one that "spills to disk," verify it's *configured* to, don't trust the comment — and grep for sibling connections to copy the proven config.
