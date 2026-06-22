# S282 · SCM — fix KPIRow crash on cost-less provider filter (FKBRING)

**Session** `8792cd8e` · new topic (fresh SCM bug report). Jebrim. No prior resume; shipped same session.

## What this session did

Niklavs reported an SCM crash: selecting a provider filter that returns "no rows or no costs" (e.g.
**FKBRING**) throws *"Cannot read properties of null (reading 'toFixed')"*.

Traced end to end in `bi-analytics-main/NFE/dashboards/shipping_costs_monitoring_nextjs`:

- **Root cause.** `src/app/api/overview/route.ts:204` computes `avg_cost` as
  `ROUND(SUM(sum_routing)::DOUBLE / NULLIF(SUM(n_routing), 0), 4)`. A provider with **shipments but zero
  routing-cost rows** (`n_routing = 0`) makes the denominator `NULL` → `avg_cost` returns `null`. The row is
  still returned because `n_shipments > 0` (route.ts:158), so `kpis` is a valid object carrying
  `avg_cost: null`.
- **Crash site.** `src/components/KPIRow.tsx:274` rendered `kpis.avg_cost.toFixed(2)` unguarded — the lone
  unguarded numeric KPI. Every other field routes through `fmtPct`/`fmtCompact`/etc. (all null-guard to "-"),
  and its own Revenue sibling (line 322) already guarded with `!= null`. So FKBRING was the only path that
  hit raw `null.toFixed`. It's the "no costs" case, not "no rows" (a true zero-shipment provider yields
  `kpis = null` and the page renders empty).

Fix (two files, both in `bi-analytics-main`):

1. `src/lib/types.ts:995` — `OverviewKPIs.avg_cost: number` → `number | null` (honest typing).
2. `src/components/KPIRow.tsx:274` — guard the Avg display to show `--` when null and suppress the now-
   meaningless % / YoY deltas for that card, mirroring the existing Revenue pattern.

`npx tsc --noEmit` clean; no other `kpis.avg_cost` consumers. FKBRING (and any shipments-but-no-costs
provider) now renders `--` instead of crashing.

## Decisions

- Render-guard + honest `number | null` typing, **not** a `COALESCE(...,0)` at the API — showing `0.00`
  avg would be a false "costs are zero"; `--` ("no cost data") matches the codebase's revenue convention.

## Pending external actions

None pending. Committed `24b416c` in `bi-analytics-main` (explicit pathspecs, two SCM files only — no
sibling sweep despite a busy working tree) and **pushed** (`2f9fe8c..24b416c`, main) at Niklavs' explicit
request. Brain committed at close.

## Cascade

- Push to `picanova/bi-analytics` main auto-deploys SCM via GitHub Actions — this fix is live on the next
  build.

## Main-brain changes

None beyond this quest-log entry. No drafts harvested (no reusable concept crystallized, no correction/
revert/misjudgment this session — the user supplied the error, the trace was clean first pass).
