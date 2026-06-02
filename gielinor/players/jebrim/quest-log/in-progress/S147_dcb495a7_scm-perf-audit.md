# S147 — SCM dashboard speed/performance audit

**Session:** dcb495a7 · **Player:** Jebrim · **Opened:** 2026-06-02 · **Type:** read-only review (fan-out)

## Ask (principal)

> Get back to the SCM. The ★ next-session handoff from [[S146_f20d7744_scm-serving-memory-review|S146]]: a general **speed/performance** audit of the dashboard. Hypothesis: the gold-mart cutover left things non-optimal → slow loads that can be tuned.

Distinct from [[S146_f20d7744_scm-serving-memory-review|S146]]'s **memory/OOM** angle. [[S146_f20d7744_scm-serving-memory-review|S146]] root-caused + fixed the 502 (uncapped serving DuckDB → container OOMKill); fix merged (**PR #13 / `d554c37`** into `origin/main`) + live (`DUCKDB_MEMORY_LIMIT=512MB` set in-cluster). This quest is the orthogonal **latency** angle on the now-stable serving node.

## Read surface (current, post-fix)

`C:/Users/niklavs.felsbergs/Documents/GitHub/_scm-mem-fix/NFE/dashboards/shipping_costs_monitoring_nextjs/` — the `fix/scm-serving-memory` worktree, content-identical to the SCM app in deployed `main`. Read-only; **no app edits, no commits there**. (The `bi-analytics-main` worktree is on `feat/fif-orwo-standalone`, which predates PR #13 — do NOT read SCM code from there.)

## Why a fan-out (5 dimensions)

Five independent hot-path classes; principal chose dwarf fan-out (the [[S146_f20d7744_scm-serving-memory-review|S146]] pattern). Each dwarf is read-only, returns ranked findings with `file:line` evidence + effort tag + concrete fix, and flags what needs **live measurement** vs what's decidable from code.

- **D1 — Connection model & request concurrency.** Single shared DuckDB `Connection` (`db.ts:10`) as a serialization point; per-tab fetch fan-out (`page.tsx`); per-request `db.connect()` / pooling to parallelize (also the deferred bd_cache fix).
- **D2 — Redundant scans within a request.** `attachCountryShares` re-scan, `shifts.ts` `fromExpr` ×4, `completeness`/`avg-costs` double scans → compute-once-into-CTE / materialize-once.
- **D3 — Parquet layout & pipeline pre-aggregation.** Row-group / sort-order / partitioning of `daily`/`daily_product`/`processed` for pushdown; per-shipment serving scans that a new pipeline pre-agg could retire.
- **D4 — Spill-vs-RAM & DuckDB runtime tuning.** `memory_limit` 512MB, `threads`, `temp_directory`, `preserve_insertion_order=false` — when do queries spill, latency cost, pod-limit headroom, what to measure before tuning.
- **D5 — Cold start + client caching.** ~770MB S3 sync blocking readiness, probes, `next.config`, `Cache-Control max-age=30` + no SWR, server-cache TTLs, staggered/lazy tab loads.

**Missing half (live):** ranking needs real timings — one network-tab capture of a slow tab load (call count + per-call duration) or pod query timings. Requested from principal in parallel with the fan-out.

## Turn log

- T1 — Grounded via [[S146_f20d7744_scm-serving-memory-review|S146]] resume + quest + D2 route-scan findings; verified PR #13 merged to `origin/main` (fetched) so the audit reads post-fix code. Posted OPEN. Principal chose perf-audit + dwarf fan-out. Spawning 5 dwarves.
- T2 — All 5 dwarves returned. Traces: `S147_d{1,2,3,4,5}_*.md`. Synthesis below.

## Synthesis — ranked perf findings

**Headline (D1):** every API query runs through a **single shared DuckDB `Connection`**, and the native `duckdb@1.4.2` binding **serializes statements per connection**. A tab's parallel `/api/*` fan-out (Transit fires 5, Breakdown ≤5) *looks* parallel in the browser but funnels to one serial DB queue → wall-clock ≈ **Σ(query times), not max**. `db.ts:10,493,512,520`. Fix: per-request `db.connect()` (or a 2–3 conn pool) off the shared `Database` — unlocks real DB parallelism **and** makes `bd_cache` connection-local, killing the breakdown race [[S146_f20d7744_scm-serving-memory-review|S146]] deferred. **This is the biggest structural lever IF the dashboard sees concurrent queries.**

**Pivotal unknown (D1 + D4 both flag it):** is this **high-concurrency or effectively single-user?** If single-user, the serialization (the headline) rarely bites and D1 drops down the ranking. This one fact re-ranks the whole audit → measure before committing the D1 rebuild.

**Cross-dwarf correction:** D1 initially assumed each connection carries its own `memory_limit`; **D4 corrected it — DuckDB `memory_limit` is database-instance-wide, not per-connection.** So pooling off one `Database` does NOT multiply the 512MB cap (good — no per-conn budget blowup); but `threads × pool_concurrency` is the real memory-pressure multiplier. Keep any pool small.

### Tier 1 — do regardless of measurement
- **D4 durability landmine (S, do now).** `DUCKDB_MEMORY_LIMIT=512MB` lives only as a live `kubectl set env`; the code default at `db.ts:35` is **`4GB`**. Next image rebuild without the env → 4GB DuckDB on a 1536Mi pod → **immediate OOM regression of the exact [[S146_f20d7744_scm-serving-memory-review|S146]] bug.** Fix: `ENV DUCKDB_MEMORY_LIMIT` (+`DUCKDB_THREADS`) in `docker/Dockerfile` AND change the `db.ts:35` default to a pod-safe value so the landmine is gone even if the env is dropped.

### Tier 2 — certain serving-side wins (this app's repo)
- **D2 F2/F3 (S each):** `breakdown-sparklines.ts:140/164` scans processed twice (per-dim + `__TOTAL__`) → GROUPING SETS / derive total from per-dim CTE; `breakdown.ts:406/448` `buildTotalQuery` double-scans → fold `real_pct_all` into the `src` CTE. Always-processed, unambiguous.
- **D3 serving-only (S each):** `deviations/route.ts:211` trend block re-scans `processed` instead of the existing `deviations_summary.parquet` (summable, right grain); `outliers` global path recomputes `PERCENTILE_CONT` instead of reading `outlier_thresholds.parquet`.
- **D5 caching (S→M):** no SWR anywhere (all 21 components plain `fetch`), `Cache-Control max-age=30` too short for daily-refreshed data. Adopt SWR keyed on `meta.run_timestamp` + lengthen `max-age` with `stale-while-revalidate`.

### Tier 2 — gated on `EXPLAIN ANALYZE`
- **D2 F1 (M):** `shifts.ts:152,240,281,290` inlines `cfg.fromExpr` **4×** → 4 processed re-scans when a processed-tier filter is active. Hoist to one named `WITH src AS (…)`/temp table → 4 scans become 1. **Gated:** confirm DuckDB doesn't already CSE identical *inline* subqueries (it de-dups *named* CTEs). If it CSEs them, the win evaporates.

### Tier 3 — pipeline build session (separate; not this app's commit scope)
- **D3 sort-on-write (S):** every `write_parquet` is bare (`pipeline.py:2419,2505,2566`) — no sort, no row-group tuning → month-file prune is the *only* pruning, no within-file row-group skipping for `order_date` ranges. `.sort("order_date")` + `row_group_size` before write enables real pushdown; serving-invisible.
- **D3 transit roll-up tier (M):** all 5 `transit/*` routes scan per-shipment `processed` just to aggregate transit-time/status (pipeline already flags this as deferred). Bake daily **histogram-bin counts** per (date,country,provider,packagetype) — percentiles off the binned CDF (±1 day) — retires all 5 transit routes + `transit/histogram` off per-shipment.

### Tier 3 — infra / deploy (manifest NOT in this repo)
- **D5 cold start (M):** `entrypoint.sh:11-14` does a **blocking, sequential `aws s3 sync` (~240MB+) before node binds** = restart/scale-up latency floor; a killed pod re-pays the whole sync. Best fix: shared read-only volume (EFS/PVC) populated by the refresh pod → serving pods skip the sync (ready in node-boot time), also lets the image slim (D5 C3: serving image bakes the refresh-only Python+AWS-CLI stack) and removes the probe-race surface.
- **D4 pod tuning (S→M):** Option A — pod 1536Mi→2560Mi + `DUCKDB_MEMORY_LIMIT`→1536MB + `threads`→4 (cuts spills, parallelizes 241MB scans; +1Gi). Option B — keep pod, cap→700MB (reclaim over-conservative margin) + move spill `temp_directory` off the S3-sync tree. Threads + memory must move together.

### Missing half — live measurement to anchor the ranking
1. **Concurrency / single-user?** (re-ranks D1 — the headline). 
2. Network-tab capture of the slowest tab: call count + per-call duration + waterfall vs parallel.
3. `EXPLAIN ANALYZE` on a processed-tier `shifts` query (gates D2 F1) + a transit query (sizes D3 P1).
4. Spill activity at the 512MB cap (`duckdb_temporary_files()`) + `bd_cache` resident size for the 18-mo window.

**Recurring across all 5:** the serving k8s manifest is not in this repo — the deploy-side items (cold-start volume, pod limits, probes) need the deploy repo.

Pending: principal — measurement-first vs ship-certain-wins-now; and where the deploy manifest lives.

- T3 — Principal chose **measure-then-build**. Implemented the Tier-1 do-now item immediately (measurement-independent): the D4 durability landmine. Worktree `C:/Users/niklavs.felsbergs/Documents/GitHub/_scm-perf`, branch `fix/scm-duckdb-mem-default` off `origin/main` (`d554c37`). 2 files, +12/-1: `db.ts:35` default `4GB`→`512MB` (+ why-comment); `docker/Dockerfile` adds `ENV DUCKDB_MEMORY_LIMIT=512MB` + `ENV DUCKDB_THREADS=2`. Defense-in-depth — pod-safe even if the deployment env is dropped; the env still overrides for tuning. Uncommitted (asking before commit/push). Did NOT touch the hardcoded `REDSHIFT_PASSWORD` (`Dockerfile:55`) — separate D5/security item (rotate→Secret), out of this fix's scope.
- **Measurement handed to principal** (anchors the ranking before the bigger build): (1) concurrency — many simultaneous users or ~single-analyst? (re-ranks D1); (2) network-tab capture of slowest tab (call count + parallel/stagger + slowest durations); (3) if pod/SQL access granted, I run the `EXPLAIN ANALYZE` for D2-F1 (shifts re-scan) + D3 (transit) myself.

- T4 — **Measurements in. Ranking rewritten on evidence.**
  - **Concurrency:** 1–2 users now, could grow → D1 (per-request conn) drops from headline to "do for the bd_cache race fix + growth," not urgent for latency.
  - **Network capture (Breakdown tab):** ~16 `/api` calls, **8.26s** to finish. Heavy hitters all processed-tier: `breakdown` 3.11s, **5× `breakdown-sparklines` 2.77–3.97s each**, `generic-trend`/`trend-shares` 1.7–3.2s. `filter-options` gates the data calls (dependency waterfall).
  - **Live in-pod probes (DuckDB 1.5.3, read-only, capped 350–450MB so as not to perturb the live pod):**
    - **Breadth is the dominant cost:** full 29-month glob agg **268ms vs 10ms single-month = 26.8× breadth factor**; 3-month agg ~59ms. The 3–4s app queries = wide month-window × wide per-shipment cols × the 5-sparkline fan-out.
    - **Row-group stats ABSENT** (`stats_min=0` across all 164 metadata rows; 4 row-groups/month at DuckDB default 122880; no sort) → **no within-file pruning** — a date filter still reads the whole month file. Confirms D3 sort+stats-on-write.
    - **`shifts` 4×-separate-inline re-scans only 1.6×** (41ms vs 25ms hoisted) — D2-F1 is a real but MODEST win (M), not the static audit's "highest leverage."
    - **Pre-agg tiers near-instant** (daily_product 127MB single file, metadata-fast). `deviations_summary.parquet` (9MB) + `outlier_thresholds.parquet` (2KB) **confirmed present on disk** → the two D3 serving quick-wins are pure routing changes.
  - Data layout: `processed/` = 29 monthly files (2024-01 → 2026-05), ~474k rows/month; `daily.parquet` 60MB + `daily_product.parquet` 127MB single files.
  - AWS creds were **session-only — not written to any file** ([[S146_f20d7744_scm-serving-memory-review|S146]] discipline).

## Revised ranking (evidence-backed)

**The slowness is processed-tier scan BREADTH × per-shipment column width — not connection serialization, not CTE re-scans.** Rank:

1. **Route off `processed` onto existing pre-agg tiers (D3 serving, S, do now).** `deviations/route.ts:211` trend → `deviations_summary.parquet`; `outliers` global → `outlier_thresholds.parquet`. Both files exist. Moves queries from 268ms-scaling to ~10ms. Highest confidence × leverage, in this app's repo.
2. **Sort-on-write + row_group_size + statistics (D3 pipeline, S).** Confirmed no within-file pruning today. Separate pipeline session.
3. **Transit roll-up tier (D3 pipeline, M).** Retires all 5 `transit/*` routes off per-shipment. Separate pipeline session.
4. **Trim the `breakdown-sparklines` 5× fan-out + tighten breakdown month-window (D2/frontend, M).** Breadth + call-count are most of the 8s.
5. **`shifts` 4× hoist to one CTE (D2-F1, M) — confirmed 1.6× only.** Modest.
6. **breakdown double-scan removals (D2-F2/F3, S).** Small confirmed wins.
7. **D1 per-request connection (M).** Deprioritized for latency (1–2 users); still worth it for the bd_cache race (correctness) + future concurrency.
8. **D4 pod sizing — HOLD.** Real driver is breadth not memory; at 1–2 users the 512MB cap is likely fine. Keep the durability landmine fix (already done).

- T5 — **Started tranche 1 (serving quick wins); live validation reshaped it.** Principal: "do it all — how to proceed (context loaded)?" Recommended 3 sequenced tranches; began tranche 1 on the warm context + live creds.
  - **P2 (deviations trend → pre-agg) FAILS validation as a serving-only swap.** `deviations_summary` carries only `sum_deviation` (not `sum_real`/`sum_expected` separately) → can't feed the dual-line chart. The `daily` tier HAS `sum_real`+`sum_expected_for_invoiced`+`shipments`, but a live old-vs-new compare (Germany/DHLPKT, 52 wks) shows **population mismatch**: counts differ every week (3533 vs 3695) and some weeks diverge hard (2026-05-18 OLD `3.30/3.23/n1413` vs NEW `1.35/1.32/n3454`; 2025-09-08 exp `3.58` vs `0.24`). The per-shipment trend filters `shipping_cost>0 AND expected>0`; `daily`'s population is broader invoiced (recent weeks: real costs not yet arrived deflate it). **Routing to `daily` = correctness regression.** → P2 moves to the **pipeline tranche** (bake a trend roll-up at the matching population). The live-validation method (old-vs-new per-period compare) is now proven for the pipeline session to reuse.
  - **Implication:** the serving layer is already mostly correctly routed ([[S146_f20d7744_scm-serving-memory-review|S146]] + prior work). The remaining per-shipment scans (transit, deviation trend, breakdown drill) can't be cheaply re-routed because **no existing pre-agg tier matches their population**. So the real high-leverage build is the **PIPELINE tranche** — regen parquet with sort+row-group stats (within-file pruning) AND new roll-up tiers populated to match each per-shipment query (transit binned-CDF, deviation-trend both-costs-present). Serving-only quick wins shrink to: D2-F2/F3 breakdown double-scan removals (pure SQL, no population change) + maybe P4 outliers-global (unverified).

## Revised sequencing recommendation (post-validation)

1. **Landmine fix — DONE this session** (branch `fix/scm-duckdb-mem-default`, uncommitted). The one solid serving deliverable. Ship as a small PR.
2. **PIPELINE session (now the real headline):** in `bi-etl`/`pipeline.py` — (a) sort `processed` on write + `row_group_size` + statistics → within-file date pruning (confirmed absent today); (b) transit roll-up tier (binned-CDF) → retires 5 transit routes; (c) deviation-trend roll-up at the both-costs-present population → makes P2 a safe serving swap. Each validated old-vs-new against live data (method proven in T4/T5). Needs a refresh run + S3 re-sync.
3. **Serving/frontend session:** D2-F2/F3 breakdown double-scan removals + trim the 5× `breakdown-sparklines` fan-out + SWR caching + D1 per-request connection (bd_cache race). Re-point the trend/transit routes at the new tiers from #2.

- T6 — Close (S147). Principal chose: commit+push the landmine, wrap, do the pipeline tranche fresh. **Shipped:** landmine branch `fix/scm-duckdb-mem-default` (`025ca21`, pushed to `picanova/bi-analytics`; PR not opened — `gh` absent locally, link handed to principal). Harvest: 1 examine draft (`static-audit-ranking-is-a-hypothesis-until-measured`). Resume + 3-tranche handoff in `inventory/scm-perf-audit-resume__dcb495a7.md` (tranche 2 = pipeline regen is the real headline). S147 stays **in-progress** (2 build tranches queued). AWS creds were session-only — not written to any file. No pending external actions (landmine committed+pushed; PR-open is a principal click). Stale Jebrim in-progress quests ([[S116_7f67fe48_shipping-agent-fif-monthly-skill|S116]]/S124/S145/S-shipping-agent orphan) left untouched — bankstanding's triage domain (flagged in [[B-013_2026-06-01_thirteenth-bankstanding|B-013]]), not this session's reach.

---

## Session 2 (sid e1918844, 2026-06-02) — Tranche 2, Change 1: sort-on-write + row-group stats

Principal: "continue on the SCM refactor." Mapped → the Tranche-2 PIPELINE build (the audit's headline). Principal chose scope = **Change 1 only** (sort-on-write + row-group stats; the ship-safe, serving-invisible lever) over the full tranche.

- **Repo correction:** the buildable `pipeline.py` + Dockerfile live in **bi-analytics** (`NFE/dashboards/shipping_costs_monitoring_nextjs/`), baked into the SCM image — NOT bi-etl (that holds only the orchestrating DAG, `dags/AI_Automations/nextjs_dashboard_dags/shipping-costs-monitoring-dag/`). The resume's "Repo: bi-etl" was a mis-recall; corrected.
- **Branch:** fresh `feat/scm-pipeline-rowgroup-sort` off `origin/main` (d554c37 = [[S146_f20d7744_scm-serving-memory-review|S146]] PR#13; landmine PR not yet in main → clean independence), isolated worktree `_scm-pipeline-sort`.
- **Edits (3, minimal):** (1) new const `PROCESSED_ROW_GROUP_SIZE = 122_880`; (2) `write_processed` — per-month `.sort(["order_date","shippingprovider"])` before write + `row_group_size=PROCESSED_ROW_GROUP_SIZE, statistics=True` (per-partition sort to avoid a full-frame OOM spike, [[S069_006248ef_pipeline-oom-hardening|S069]]/[[S146_f20d7744_scm-serving-memory-review|S146]] history); (3) `_write_daily_summary` — `.sort("order_date")` + `statistics=True`. Left the `daily_product` DuckDB-COPY path alone (memory-tuned streaming, near-instant aggregated tier, low leverage).
- **Verified (synthetic, mechanism-level — no creds):** `py`+polars 1.33/pyarrow/duckdb. Bare write of a 500k-row synthetic month = **1 row group spanning the whole month** (05-01..05-31) → a 7-day query reads 1/1 (100%). Sorted+`row_group_size` = **4 row groups, tight non-overlapping ranges** (g1 05-01..05-08) → 7-day query reads **1/4 (75% pruned)**. DuckDB result identical (112,903 rows both ways — pure layout, no correctness change).
  - **Finding that sharpens the audit:** statistics WERE present in the bare file (polars 1.33 default) but useless because the single row group's min/max span the whole month. And a clean single-frame write produces **one** row group, not the "4 at 122880" the live probe saw (that was the multi-chunk reload source). So **explicit `row_group_size` is load-bearing**, not a no-op — it's what guarantees multiple groups regardless of source chunking; the sort is what makes their ranges prunable.
- **Pending:** commit + push (principal-gated) → PR link. Live old-vs-new latency validation deferred to a refresh run + in-pod EXPLAIN ANALYZE at deploy (the proven T4/T5 method). Changes 2–3 (transit binned-CDF tier, deviation-trend both-costs-present tier) still queued.
