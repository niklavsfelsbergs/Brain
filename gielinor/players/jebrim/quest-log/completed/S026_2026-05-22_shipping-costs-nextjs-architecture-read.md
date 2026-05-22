# S026 — shipping-costs nextjs architecture read

**Date:** 2026-05-22
**Player:** Jebrim
**Status:** in-progress

## Ask

Principal asked Jebrim to investigate the shipping-costs monitoring Next.js app in `bi-analytics-main/NFE` and accumulate knowledge of it. The mart-based version lives on branch `shipping-mart-cutover`. Goal is to seed Jebrim's bank with knowledge for future asks — not a deliverable today, no active cutover decision driving it.

## Decisions

- **Depth:** full architecture read (principal's pick).
- **Access:** worktree at `C:\Users\niklavs.felsbergs\Documents\GitHub\bi-analytics\` is checked out on `shipping-mart-cutover` — read the live tree there. `bi-analytics-main` stays on `main` with the existing S023 changes.
- **Purpose:** seed knowledge for future asks. Bank draft, not a deliverable.
- **App path:** `NFE/dashboards/shipping_costs_monitoring_nextjs/`.
- **Branch diff scope vs main:** 13 commits ahead. Big diff — `sql/query.sql` deleted, `sql/query_mart.sql` + `sql/query_mart_items.sql` added, `pipeline.py` rewritten (858 LOC change), Buckets / Quota / Transit Times views added, lots of new components & API routes.

## Turns

### T1 — orient

Located branch `shipping-mart-cutover` (13 commits ahead of main). Confirmed worktree is at `C:\Users\niklavs.felsbergs\Documents\GitHub\bi-analytics\` on that branch. Located app at `NFE/dashboards/shipping_costs_monitoring_nextjs/`. Read `CLAUDE.md` (~200 lines, dense file-map + patterns) and `README.md` (~200 lines, stack + arch). Top-level picture: Next.js 15 + DuckDB + Polars pipeline pulling from Redshift, deployed via Docker + Airflow DAG, S3-persisted parquets.

### T2 — spawn dwarves

Spawned 3 dwarves in parallel:

- **D1** — SQL + pipeline + audit/backtest + tests. Findings: `S026_d1_sql_pipeline.md`. Big find: cutover collapsed 5 legacy queries → 2 mart pulls; `audit.py` and `backtest.py` are stale (still reference legacy `layer*_*.parquet` and single-file `processed.parquet`).
- **D2** — API routes + DuckDB data layer + types. Findings: `S026_d2_api_and_data_layer.md`. Read all 35 routes (the dashboard has 35, not the 28 the README mentions). Cutover delta vs main: 18 files, +1297/-72, three commits. Whole Transit Times subtree new (5 routes), Breakdown gained Buckets + Quota sub-views, every existing route extended with bucket-aware cost expressions + revenue/quota fields.
- **D3** — Frontend: page orchestration, tabs, shared components. Findings: `S026_d3_frontend.md`. Page is single 871-line `Dashboard` client component; URL is single source of truth via `filtersToParams`/`paramsToFilters` with short codes; lazy mount + `display:none` preserves state across tabs.

### T3 — vocab draft

User intent shifted to "shipping cost vocab". Synthesized the three dwarf findings into a **glossary-shaped** bank draft instead of a full architecture dump (the dwarves' files in `quest-log/in-progress/` are the deep reference; the bank note pins the *language*).

Draft landed: `players/jebrim/bank/drafts/notes/projects/shipping_costs_monitoring_nextjs_vocab.md`.

Covers: routing (paths, branch, source-of-truth docs), cost columns + cost basis, the 11 cost buckets, quota/revenue, time/period machinery, alert + issue vocab (two-queue + 9 alert types + 8 suppression rules + lifecycle terms), data tiers (Tier 1 / 1b / processed + tricks), DuckDB query layer, old → new tab naming, frontend state vocab, order source split, things-to-verify, open questions.

Cross-references existing keepsake pin for the shipping data mart and prior S023 bank/skill drafts.

## Notes / open

- Bank note is a **draft** — promotion to `bank/notes/` waits for alching. Per [[D-017]]-style brevity rule, it could probably be tightened on review; left rich for now since the domain is dense and dwarves' findings are the durable backup if I cut too aggressively.
- The shipping-mart-cutover branch hasn't merged. If/when it does, the "branch" routing line in the vocab note needs to be retired.
- `corridor_costs_weekly.parquet` referenced by `_build_alerts` fallback but not seen in main write path — flagged as an open question in the vocab.
- `/api/generic-trend` full-glob fallback when cost-range filters set without date pins is a known perf hot path.
- Two stale audit harnesses (`audit.py`, `backtest.py`) — would be a good follow-up Jebrim task.

### T4 — convergence documentation + parked quest

Principal asked for my read on the dashboard alongside the shipping-agent. I laid out interrelation (monitor vs investigator over the same mart), four risks, and four questions. Principal confirmed:

1. Dashboard ↔ mart alignment is incomplete (mart is source of truth; dashboard needs more cutover work).
2. Dashboard's structural-coverage-hole reporting is currently wrong; will be resolved.
3. Cost-basis alignment between dashboard and agent — deferred.
4. Long-term direction — not yet thought through. Concrete near-term: agent could emit dashboard URLs.

Asked to document this and park a quest for the convergence work itself. Two new artifacts:

- `bank/drafts/notes/projects/dashboard_and_shipping_agent_convergence.md` — interrelation, the four confirmed positions, convergence directions in order of leverage, four coupling opportunities ordered by reversibility, open questions.
- `inventory/dashboard-agent-convergence-resume.md` — parked quest resume file. Recommends URL-routing (cheapest) + thin doc-pointer in the agent as the opening pair when this quest is picked up.

Quest is parked, not opened — no session number yet. Inventory file is named topically; gets renamed at first close-session of the actual work.

### T5 — close-session

No pending external actions. All session output is on disk:
- `bank/drafts/notes/projects/shipping_costs_monitoring_nextjs_vocab.md`
- `bank/drafts/notes/projects/dashboard_and_shipping_agent_convergence.md`
- `inventory/dashboard-agent-convergence-resume.md` (parked future quest)
- `inventory/S026-shipping-costs-nextjs-resume.md` (written this turn)
- Three dwarf findings in `quest-log/in-progress/` (S026_d1, _d2, _d3)
- This file (S026 narrative log)

Quest decision: **continue** (in-progress). Drafts ship-shape but await alching alongside S023's parked drafts. Same pattern as S023.

Harvest: empty. The two bank drafts and the parked-quest inventory file are this session's substantive durable output — there's nothing additional that earned its way. A skill draft for the "3-dwarf decomposition for codebase reads" pattern is tempting (used in S002 and now S026) but the two instances split differently — S002 across three external systems, S026 across three app layers. Wait for a clearer reproduction.
