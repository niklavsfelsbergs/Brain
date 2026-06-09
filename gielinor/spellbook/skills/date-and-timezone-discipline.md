# Date & timezone discipline — skill

Hard-won date-handling rules — the bugs that have actually bitten. Cross-language (JS + Python), so they belong with the agent, not one repo. War wounds, not API docs.

> Migrated from `bi-analytics-main/NFE/.claude/reference/date-handling.md` (2026-06-09, [[D-034_guthix_executes_on_explicit_authorization|D-034]]). The NFE doc keeps the pipeline-specific `--simulate-date` bit and points here.

## When this fires

Any date computation for display, comparison, filtering, or API params — especially in JavaScript, especially when a one-day-off error would be silent.

## The CET timezone trap (the big one)

`new Date("2025-11-24T00:00:00")` **without `Z`** parses as *local* midnight. In CET (UTC+1) that's `2025-11-23T23:00:00Z`, and `.toISOString().slice(0,10)` then gives `"2025-11-23"` — **one day off**.

- **Always use the `Z` suffix** when you intend UTC math: `new Date("2025-11-24T00:00:00Z")`.
- **Always use UTC methods** in arithmetic: `setUTCDate`/`getUTCDate`/`setUTCMonth`/`getUTCDay`, never the local-time variants.
- **Rule of thumb:** a `T00:00:00"` without `Z` in date-arithmetic code is a bug.

## Prefer string comparison for ISO dates

`YYYY-MM-DD` strings compare correctly lexicographically (`"2025-09-29" <= "2025-10-05"` is `true`). For date *filtering* in DuckDB and client-side, compare the strings directly — don't parse to `Date` objects. Fewer objects, no timezone surface.

## Partial periods are always dropped

The analytical convention, not just a code detail: **never let a partial current week/month skew a trend.** Cap chart data and queries at the last *full* period.

- Last full week (Sunday-ending): step back to the prior Sunday unless today *is* Sunday.
- Week alignment (Python): Monday of the week is `max_date - timedelta(days=max_date.weekday())`; if today isn't the week's last day, use the *previous* full week.
- Baseline windows (e.g. 5 weeks before an event) compute off the capped current value, not raw today.

## What stays in the repo

The pipeline `--simulate-date` parquet-reload filter (must also filter persisted `processed/*.parquet`, not just the in-memory frame) — that's pipeline-framework mechanics, not portable discipline.
