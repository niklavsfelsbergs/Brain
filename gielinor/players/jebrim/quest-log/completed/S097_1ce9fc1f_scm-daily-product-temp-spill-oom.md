# S097 — SCM DAG: daily_product temp-spill OOM (prod fix, shipped to main)

**Session:** 1ce9fc1f · **Player:** Jebrim · **Opened+closed:** 2026-05-26

Continuation of the OOM-hardening thread from [[S069_006248ef_pipeline-oom-hardening]] — but a **distinct incident**: different connection, different failure mode, different runtime, and this one shipped to **production main** ([[S069_006248ef_pipeline-oom-hardening|S069]] was branch-local only).

Repo: out-of-tree `Documents/GitHub/bi-analytics/NFE/dashboards/shipping_costs_monitoring_nextjs/pipeline.py`. Three local clones are **git worktrees** of one repo (`picanova/bi-analytics`).

## The incident

Principal: `shipping_costs_monitoring_nextjs` DAG failed after "latest changes." Traceback:

```
pipeline.py:2448 in _write_daily_product_summary → con.execute(...)
_duckdb.OutOfMemoryException: failed to offload data block of size 256.0 KiB
(2.3 GiB/2.3 GiB used). This limit was set by 'max_temp_directory_size'.
```

## Root cause

**Not a RAM OOM — a disk-spill OOM.** The `_write_daily_product_summary` DuckDB connection sets `memory_limit='2GB'` (this cap predates [[S069_006248ef_pipeline-oom-hardening|S069]]; [[S069_006248ef_pipeline-oom-hardening|S069]] only added `preserve_insertion_order=false` here). At doubled mart volume (this run pulled **13.2M shipments**; df_sum ~18M rows), the 2GB cap forced the UNNEST + 9-dim GROUP BY to spill heavily. But `temp_directory` = `DATA/_duckdb_tmp` rides the **same near-full 20Gi pod volume** (raw.parquet + processed monthlies + the just-written `_dailyprod_input.parquet`), leaving only ~2.3 GiB free. DuckDB's `max_temp_directory_size` defaults to free disk = 2.3 GiB → OOM on spill, not RAM.

The deployed pod has a **20Gi memory limit** but DuckDB was told to use 2GB — forcing spill onto a constrained disk while 16+ GB of RAM sat idle. The S069-era 2GB cap (sound for avoiding a RAM fight with resident df_sum) over-corrected once volume grew: it relocated the OOM from RAM to disk.

Confirmed deployed code == `origin/main` @ `9d5985a` (line 2444 `2GB` / con.execute 2448 matched the traceback exactly).

## Fix (shipped)

`memory_limit='2GB' → '8GB'` at line 2444, + comment. df_sum (~4-5GB) + 8GB DuckDB + overhead stays under the 20Gi pod limit; the aggregation runs in RAM instead of spilling to a disk with no room. Single-line change, no other code touched.

## Deploy (the non-obvious part)

CI builds the ECR `:latest` image **on push to `main`**. Topology discovered this session:
- `bi-analytics` (worktree, branch `shipping-mart-cutover`) — active dev branch; was 0 commits ahead of `origin/main` before the fix (all prior work already merged in).
- `bi-analytics-main` (worktree, branch `main`) — the principal's WIP, **dirty** with a large unrelated changeset. Did NOT touch it.
- `_bi-analytics-deploy` (worktree, branch `deploy-cutover-2026-05-26`) — merges *from* cutover, not a build trigger.

Mechanics: committed fix on `shipping-mart-cutover` (`f0c86f4`), then — to avoid the dirty `main` worktree and a non-ff branch push — created a **throwaway detached worktree off `origin/main`**, merged `shipping-mart-cutover` into it (brought only `pipeline.py`, verified by `--stat`), pushed `HEAD:main` (`9d5985a → 4a76307`), removed the worktree.

## Outcome

Principal re-triggered the DAG → **"worked."** Verified in prod. Pending actions: **none** (commit pushed + image built + DAG validated).

## Future lever (not needed now)

If it recurs as the mart keeps growing, the durable fix is bumping the pod `ephemeral-storage` (20Gi→32Gi) in the DAG spec so the temp dir has real spill headroom — orthogonal to the RAM lever. 8GB clears it for current volume.

## Cross-refs
- [[S069_006248ef_pipeline-oom-hardening]] — prior OOM hardening (the join connection; RAM mode; branch-local).
- Bank drafts harvested: `scm_nextjs_duckdb_oom_modes`, `bi_analytics_deploy_topology`.
