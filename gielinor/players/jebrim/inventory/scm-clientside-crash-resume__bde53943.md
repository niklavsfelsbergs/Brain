---
quest: S255_scm-clientside-crash-diagnosis
sid8: bde53943
ts: 2026-06-17 00:00
open_dep: root-cause throw unconfirmed; awaiting next-crash [SCM] console error + Actions deploy-green confirmation
---

# SCM client-side crash — resume

**Status:** mitigation shipped + pushed; root cause not yet pinned.

**Where we are:** The full-page "Application error: a client-side exception" white-screen was caused by the SCM dashboard having NO React error boundary — any rare data-state throw in a tab unmounted the whole tree. Shipped error boundaries (per-tab `ErrorBoundary` + route `error.tsx` + `global-error.tsx`) that contain the throw to one panel and log the real `[SCM]` error. Committed `d3c7039`, pushed to picanova/bi-analytics `main` (auto-redeploys via GitHub Actions).

**Next concrete step:**
1. Confirm the GitHub Actions run for `d3c7039` went green (else the fix never reached the live site). Actions tab on picanova/bi-analytics.
2. The underlying throw still fires (contained now). On the next panel-error, grab the `[SCM] render error ...` line from the browser console + note which page/filter/month triggered it — that pins the exact throwing line + data condition. Then fix the root cause and the quest closes.

**Files to read first:**
- `quest-log/in-progress/S255_bde53943_scm-clientside-crash-diagnosis.md` — full diagnosis + ranked suspect sites (BreakdownTab:592, OutliersTable:234, KPIRow fmtRange are the low-rank soft ones).
- App: `bi-analytics-main/NFE/dashboards/shipping_costs_monitoring_nextjs/src/` — new boundary files in `src/components/ErrorBoundary.tsx`, `src/app/error.tsx`, `src/app/global-error.tsx`.
- Memory: `reference_scm_deploy_github_actions` (push = deploy).
