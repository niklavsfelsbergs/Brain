# S069 resume — shipping-costs pipeline OOM hardening

## Status
**done** — proposing move to `completed/` (deliverable shipped + validated by a real `--refresh-full` run).

## Where we are
Full refresh now finishes at ~18M/11M volume. Two surgical DuckDB fixes applied + committed branch-local on `shipping-mart-cutover` (not pushed). The two RAM-dependent Polars peaks held on the real run — fallbacks never needed.

## Fixes (committed branch-local, NOT pushed)
1. `pull_raw` ~L501 DuckDB conn: `memory_limit='4GB'` + `temp_directory` + `preserve_insertion_order=false` (was fully unconfigured).
2. `build_daily_product` ~L2453 DuckDB conn: added `preserve_insertion_order=false`.

## Next concrete step
None for S069 — quest closed pending the `completed/` move. The main-merge (CICD) of `shipping-mart-cutover` is NOT part of this quest; it folds into **S073 — swap the live report on AWS**.

## Files to read first
- `quest-log/in-progress/S069_006248ef_pipeline-oom-hardening.md` (full dwarf findings + documented fallbacks, if a peak ever regresses at higher volume).
