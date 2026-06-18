# S264 — SCM Cost Drivers shift tabs: "--" for EUR Impact + Base Cost

**Player:** Jebrim · **sid8:** 17290ea4 · **Date:** 2026-06-18 · **Status:** complete (shipped + committed + pushed)

## Ask

Niklavs: "something wrong with the cost drivers tab in SCM. All the shift tabs show -- for EUR impact and base cost, something is broken, check it out."

## Outcome

Root-caused and fixed a baseline-pruning bug in the SCM shift query. One-file change to the external `bi-analytics` repo, committed `e452939`, pushed to `picanova/bi-analytics` main (= deploy) on explicit principal go.

## The bug

`shipping_costs_monitoring_nextjs/src/lib/shifts.ts` → `grainConfig()` selected the data source as:

```ts
const fromExpr = hasProcessedOnly
  ? processedAsDaily(params.from, params.to)   // current window only
  : `'${... PARQUET.daily ...}'`;
```

The shift query is a **current-vs-baseline comparison** — its `tagged` CTE reads rows from *both* windows. But when any **Production Site / Shop / Order Source** filter is active (`hasProcessedOnly`), it switches off the full-history `daily.parquet` onto the `processed/` tier via `processedAsDaily(params.from, params.to)`, passing **only the current window**. `processedPruned` then enumerates months current→current and loads just that one month file. The baseline month is never read → baseline role empty → `baseline_avg_cost` null → **Base Cost / Premium / % Premium / EUR Impact all render `--`**, while current-period `gainer_cost` (Avg Cost) survives. With no baseline, every provider's baseline share reads 0, so all share deltas go positive and there are no "losers" → `from_cost` finds no counterparts → falls back to the null baseline → Base Cost `--` too.

Trigger condition: any site/shop/order-source filter active on a shift tab. The default no-filter view reads `daily.parquet` (all months) and was never affected — which is why it didn't show in casual use, and why the Top Drivers/Savers list (date-only params, no dim filter) stayed populated.

## How it was found

- Faithful DuckDB repro of the shift SQL over local **and** live `daily.parquet` (live pulled today via fresh AWS creds) for the default May/April window → top rows populated. Code, local data, live data, deployed code (origin/main == HEAD for all shift files), default window all checked out. Could **not** reproduce from default state.
- The crack was the principal's **screenshot**: URL carried `order_srcs=PCS,PicaAPI,Picturator` and every Share delta was uniformly positive (many "+100.0pp") — the fingerprint of an absent baseline. That pointed straight at the processed-tier path.
- Proven against live `processed/2026-04.parquet` + `2026-05.parquet`: May-only prune → baseline corridors **0**; Apr+May span → baseline corridors **1702** (1193 with populated `baseline_avg_cost`).

## The fix

Prune the processed tier across the union of both windows:

```ts
const spanBounds = [params.from, params.to, params.baselineFrom, params.baselineTo].filter(Boolean).sort();
const spanFrom = spanBounds[0];
const spanTo = spanBounds[spanBounds.length - 1];
const fromExpr = hasProcessedOnly ? processedAsDaily(spanFrom, spanTo) : `'${... daily ...}'`;
```

Safe: the `tagged` CTE already re-filters by the two date windows, so any in-between months read are discarded. Also restores the `baseline_weeks` / `baseline_period_count` / `baseline_weekly_vol` CTEs (same `fromExpr`), which were silently empty too. `tsc --noEmit` clean.

## Decisions

- **Edit-only first, then push on explicit go.** Repo auto-deploys on push to `picanova/bi-analytics`, so I stopped at the edit, showed the diff, and only committed/pushed when the principal said so.
- Pushed commit carried 8 commits (this fix + 7 prior NFE analysis commits already ahead of origin) — flagged to principal before push.

## No pending external actions

Commit `e452939` pushed (`d3c7039..e452939 main -> main`), origin/main confirmed at the fix. Deploy proceeds via CI on next pod restart / DAG run.

## Cross-links

- `bank/domains/scm.md` — the SCM dashboard digest (two runtimes, cost basis, tiers).
- Related data-tier note harvested this session: `bank/drafts/notes/projects/2026-06-18-scm-shift-processed-tier-baseline-prune.md`.
