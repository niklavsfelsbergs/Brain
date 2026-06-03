---
quest: S147_scm-perf-audit
sid8: 6e7ab36c
ts: 2026-06-02 (sess-5 + deploy/go-live)
open_dep: none — Tranche-3 (pipeline tiers + serving re-point + item 7 + useSWR pilot) is MERGED to main (a0902cc) and LIVE-confirmed (Transit + Deviations populate). Remaining are queued follow-ups, not blockers.
---

# S147 — SCM perf refactor — resume (sess-5, post go-live)

**Status:** core perf refactor SHIPPED + LIVE. Quest stays in-progress only for queued follow-ups (below). Nothing blocking.

## What's live on main (a0902cc, deployed :latest)
- **Tranche-1/2 pipeline** (`feat/scm-pipeline-rowgroup-sort`, merged via the stacked serving PR): sort-on-write + row-group stats, transit binned-CDF tier (`transit_daily` incl `inflight_n`), deviation-trend tier.
- **Tranche-3 serving re-point** (`65bf022`): deviations/transit routes onto pre-agg tiers, double-scan folds, sparkline batch, HTTP SWR.
- **Item 7** (`394b9d9`): fingerprint-named shared `bd_<hash>` tables (race 25/50→0/50, 50-way p50 14.9s→367ms, drill-down reuse 9ms) + per-scan-conn sparkline parallelization. `db.ts` `getDb`/`acquireConn`/`releaseConn`/`rawQueryOn`.
- **useSWR pilot** (`394b9d9`): `swr` + `Providers`(SWRConfig) + `useApiData` (keyed on meta.run_timestamp) + CompletenessGrid/OutliersTable converted.
- **2 deploy hotfixes** (direct to main): `cdc5568` spill-combine diagonal_relaxed; `a0902cc` transit_time_days/business_days post-pull Float64 cast.

## Open follow-ups (queued — not blockers; pick up when wanted)
1. **Browser-verified useSWR pass** — convert the remaining ~17 fetch components + BreakdownTab's coordinated fetch/abort/debounce to `useApiData`, and verify the client behaviors that can't be checked headlessly (cross-component dedup, focus/reconnect revalidation, run_timestamp cache-bust). Needs a real browser (or Playwright).
2. **Change-1 live latency number** — never captured (deploy went straight to live). If wanted: in-pod `EXPLAIN ANALYZE` old-vs-new on a date-range `processed` query post-refresh.
3. **Alert "view" → Overview breakage** (raised this session, undiagnosed): clicking an alert's "view" makes the Overview line lose its end-labels + filters get slow. Hypotheses (unconfirmed): narrow alert date-patch degenerates the Overview series (custom `EndLabels` returns null), + alert-nav mounts the heavy Breakdown tab (kept-alive) so its fetches re-run on every filter change. Likely NOT the useSWR layer (alert-nav/Overview untouched by it). Decisive datum = browser console after clicking view (`Maximum update depth exceeded` vs repeated network vs sparse-chart). A/B by toggling the `Providers` wrapper.

## Local-verification harness (untracked scaffolding in `_scm-pipeline-sort` worktree)
- `docker/Dockerfile.local` (lean node:20) + `.dockerignore`; `_gen_data_dir.py` (DATA_DIR from cached %TEMP%\scm_validate processed); `_verify_concurrency.py` (race probe + sparkline timing). Reusable for the browser pass.

## Repo state
- `bi-analytics-main` worktree → **`main` @ a0902cc** (latest, clean) — where to iterate.
- `feat/scm-serving-repoint` (`_scm-pipeline-sort`) → has item7+useSWR, behind main by the 2 hotfixes.
- `feat/fif-orwo-standalone` → `0e25905` (playground cleanup, pushed) + 1 local `wip:` commit (S124/project WIP, unpushed — big artifacts hit the pre-receive hook).

## Deploy mechanics (grounded, per bi_analytics_deploy_topology bank note)
- push to `main` → CI rebuilds `shipping_costs_monitoring:latest`. Refresh DAG (`shipping_costs_monitoring_nextjs`) runs the image, writes tiers to S3. Serving pod syncs S3 only at startup → **restart the serving pod** after a tier regen to pick up new tiers.
