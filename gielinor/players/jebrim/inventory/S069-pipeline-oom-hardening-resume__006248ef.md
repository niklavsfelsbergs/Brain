# S069 resume — shipping-costs pipeline OOM hardening

## Where we are
Full-refresh crashed at the DuckDB COPY join in `pull_raw`. Diagnosed + fixed. Audited the whole run via 3 read-only dwarves. Two structural DuckDB fixes applied (branch-local, uncommitted, py_compile clean). Two RAM-dependent Polars peaks remain, with fallbacks documented but not applied.

## Repo / branch
`Documents/GitHub/bi-analytics/NFE/dashboards/shipping_costs_monitoring_nextjs/pipeline.py`, branch `shipping-mart-cutover`. DISTINCT from the picanova/shipping-agent repo (sibling 363fdec7 / S068).

## Fixes applied (uncommitted)
1. `pull_raw` ~line 501 DuckDB conn: added `memory_limit='4GB'` + `temp_directory` + `preserve_insertion_order=false` (was fully unconfigured despite "spills to disk" comment).
2. `build_daily_product` ~line 2453 DuckDB conn: added `preserve_insertion_order=false` (had limit+tempdir, missing this).

## Residual risks (NOT fixed — RAM-dependent, need a real run to confirm)
- `main()` ~3620: `_extract_skus` + `transform` on full ~11M-wide `df_raw`. Fallback: lazy/streaming transform + extract SKUs after `del df_raw`.
- `main()` line 3832: `df_sum` = full-history eager concat (~18M × 22 cols), no spill, held across 4 summaries. Fallback: DuckDB COPY off processed/*.parquet, or scan_parquet+streaming (watch schema vs `vertical_relaxed`).

## Next concrete step
Principal runs `python pipeline.py --refresh-full` (live Redshift, ~20min).
- If it FINISHES → commit the 2 fixes (branch-local; main-merge = CICD = principal's call, same as S055).
- If it OOMs at transform or df_sum → apply the matching fallback above, re-run.

## Files to read first
- `pipeline.py` lines ~496-516 (fix 1), ~2444-2462 (fix 2), ~3603-3621 (transform peak), ~3822-3866 (df_sum peak).
- Quest-log: `quest-log/in-progress/S069_006248ef_pipeline-oom-hardening.md` (full dwarf findings).
