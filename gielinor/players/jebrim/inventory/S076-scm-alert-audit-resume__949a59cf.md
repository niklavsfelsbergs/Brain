# S076 — SCM alert-engine audit — resume

**Session:** 949a59cf · **Quest:** `quest-log/in-progress/S076_949a59cf_scm-alert-engine-audit.md`
**Repo:** `Documents/GitHub/bi-analytics` (branch `shipping-mart-cutover`) — out-of-tree. Clean bar unrelated `?? NFE/trading/`.

## Where we are
Diagnosis + A5 verification done (read-only, no edits). Three connected root causes confirmed: deviation_blowout broken (×24 inflation + permanent-active + capped medium; numbers REAL but **structural**, not anomalous — DHL2 net-real 0.87 vs gross-expected 3.37, likely gross-vs-net basis), nothing clears (active off the stale last-*available* week), severity off the latest week not cumulative. Principal authorized the fix batch (option A) and picked the deviation direction.

## Next concrete step
Implement the batch in `NFE/dashboards/shipping_costs_monitoring_nextjs/pipeline.py`, then validate **offline**: `python pipeline.py` runs the full transform→alerts→issues chain from cached `raw.parquet` (NO Redshift — default reads raw_path L419/533). Diff `issues.parquet` before/after. `pytest`. Present diff for review. **NO commit/push without principal go (main = CICD).**

## Fix checklist (harness tasks #1-6)
- [ ] C1 — severity on cumulative for cost issues (stop inheriting `last["severity"]` ~L3084; rank on cumulative_impact_eur)
- [ ] B2 — weeks_active single basis (`_merge_active_duplicates` ~L3482 → start→global-latest like L3077)
- [ ] B1 — stale-active recency gate (active-status off data recency; `current_cost` L2850-57 / status block L2960-3015)
- [ ] DEV — re-base deviation on CHANGE + static-gap diagnostic + de-inflate ×24→×1 + drop medium cap. Weekly basis = `dev_trends` (L1506-15). `compute_deviations` L1461, deviation alert block in `_build_alerts` ~L2106-2132, `_build_single_issue` else-branch L2961-64, `_issue_headline` deviation branch, `_severity` L1845 / cap L1867.
- [ ] Validate offline (run pipeline from cache, diff issues.parquet; pytest)
- [ ] Present diff for principal review

## Pending design (after clear wins)
- Full unified severity scheme (D3 proposal: cumulative-realized-EUR basis, tiers ~25K/5K/500, confidence as a modifier not a cap, volume_anomaly on a separate axis).
- Drift lifecycle (status hardcoded active L3294; `_drift_monitor` concat'd after the resolution path; never resolves) — carry-forward/resolve.

## Files to read first
- `pipeline.py` regions above.
- Dwarf findings: `quest-log/in-progress/S076_d{1,2,3}_*.md`.
- Vocab map (what S055 already fixed — don't re-flag): `bank/notes/projects/shipping_costs_monitoring_nextjs_vocab.md`.

## Discipline
`git commit -- <pathspec>` only (shared-index hazard, per 006248ef). polars prints on Windows need `PYTHONIOENCODING=utf-8` (cp1252). Live effect needs a pipeline refresh (principal-gated).
