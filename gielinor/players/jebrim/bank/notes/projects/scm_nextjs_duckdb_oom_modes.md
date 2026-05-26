# SCM nextjs pipeline — DuckDB has two OOM modes (RAM vs temp-spill)

Source: `bi-analytics/NFE/dashboards/shipping_costs_monitoring_nextjs/pipeline.py`. Harvested S097 (2026-05-26); ties to [[S069_006248ef_pipeline-oom-hardening]].

The pipeline uses two `duckdb.connect(":memory:")` COPY-to-parquet blocks for the heavy joins/aggregations Polars segfaults on:
- **`pull_raw` ~L501** — full-refresh hash join. `memory_limit='4GB'`.
- **`_write_daily_product_summary` ~L2444** — UNNEST(`shop_order_groups`) + 9-dim GROUP BY. `memory_limit='8GB'` (was 2GB until S097).

Both set `temp_directory = DATA/_duckdb_tmp` and `preserve_insertion_order=false`.

**Two distinct OOM failure modes — read the traceback to tell them apart:**

1. **RAM OOM** — unconfigured (or too-high) `memory_limit`; the connection grabs most of the pod's RAM and the allocation fails. S069's fix: cap `memory_limit` + give a `temp_directory` so it spills.
2. **Temp-spill OOM** — `_duckdb.OutOfMemoryException: ... max_temp_directory_size`. The `memory_limit` is so low it forces heavy spill, but `temp_directory` rides the **DATA volume** which is near-full (raw.parquet + processed monthlies + intermediates), so `max_temp_directory_size` (defaults to free disk) is tiny. S097's case: 2GB cap → spill > 2.3 GiB free → OOM on disk.

**Key lesson:** a `memory_limit` cap that forces spill onto a constrained disk just **relocates** the OOM from RAM to disk. The deployed pod has a **20Gi memory limit** — size `memory_limit` to use that headroom (minus resident Polars frames like `df_sum` ~4-5GB) rather than spilling. RAM lever and disk lever (`ephemeral-storage` in the DAG spec, 20Gi→32Gi) are orthogonal; pick the one matching the traceback.

**Volume context:** mart roughly doubled (S068 floor 2023-01-01); full fact ~18M rows, ~13M shipments/refresh. The pipeline was originally sized for ~8M — both connections are volume-sensitive and may need re-tuning as it grows.
