# S240 — SCM Breakdown tab: faster load on filter-state change

**Player:** Jebrim
**Session:** a7f855d6
**Repo (work, external):** `bi-analytics-main/NFE/dashboards/shipping_costs_monitoring_nextjs/` → committed `c10818a`, **pushed to origin/main**.
**Brain:** this quest-log entry + harvest drafts only.

## Ask
Make the Breakdown tab load faster on filter-state change without materially raising serving memory.

## What happened
- Diagnosed the filter-change load path: sidebar-dim changes rebuild the `bd_<hash>` cache table (parquet scan, unavoidable); cost-basis/date are cheap; **bucket changes refetch the whole table for byte-identical data** (cost is basis-driven, not bucket-driven — route `buckets` param feeds `bucketSumExpr` which is never called). Client also wiped childData and re-waterfalled `total` + `level=0` + N per-node child fetches on every refresh.
- Proposed #1 drop dead buckets param, #2 batch the refresh, #3 server result-cache for level queries.
- **Key catch:** my first diagnosis read the **stale `bi-analytics` sibling checkout**. The live build tree `bi-analytics-main` was substantially ahead ([[S147_dcb495a7_scm-perf-audit|S147]] Tranche-3): #3 already done (immutable fingerprint `bd_<hash>` tables, LRU-cap 8, results cacheable) and the sparkline half of #2 already batched. Re-grounded on the live tree before editing. Still-open subset = #1 + the row-data half of #2.

## Shipped (2 files, memory-neutral)
- `src/app/api/breakdown/route.ts` — added a `specs` batch branch mirroring breakdown-sparklines: `?specs=<JSON[{level,expand,...}]>` returns `{total, level0, children}` in one call/connection over the shared `bd_<hash>` table.
- `src/components/BreakdownTab.tsx` — (#1) `filterQS(f, includeBuckets=true)`; table `structuralQS` calls it `false` so bucket toggles don't refetch the table (sparklines keep buckets — they ARE bucket-driven; cost-basis auto-flip still refetches on its own). (#2) effect-1 refresh fires one `specs` request, marks `fetchedRef` synchronously so the incremental-expand effect skips batched keys. Filter change with N nodes open: **2+N requests → 1**, waterfall gone.

## Decisions
- Did NOT cache multiple `bd_<hash>` tables / raise DuckDB `memory_limit` — would undo the [[S146_f20d7744_scm-serving-memory-review|S146]]/[[S147_dcb495a7_scm-perf-audit|S147]] pod-safe memory bounding (principal's explicit constraint).
- Option B→A on the client: collapsed total+L0+children into the single `specs` call (full 1-request refresh), since children pins are known synchronously up front.

## Verification
- `tsc --noEmit` clean; `next build` passes (`/api/breakdown` compiles, lint+types ok); test suite parity (3 pre-existing date-dependent failures in `types.test.ts`, identical on clean main — not mine).
- **Live-confirmed by principal: "loads a lot faster."**
- Commit scoped with per-file pathspecs ([[D-024_scope-git-commits-with-pathspecs-parallel-sessions|D-024]]) — working tree was full of unrelated in-flight EU-tender work; nothing swept.

## Pending external actions
None pending. Committed + pushed; CI rebuilds ECR `:latest` → serving picks up the new image on next DAG run (serving-only change, no pipeline/data regen).

## Next concrete step
None — quest closed.
