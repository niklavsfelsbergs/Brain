# SCM dashboard intermittent client-side crash — dwarf diagnosis

**Dwarf for Jebrim.** Task: diagnose why deployed SCM dashboard intermittently throws
"Application error: a client-side exception has occurred" (thrown JS exception during
React render/hydration, data-state-dependent).

Repo: `bi-analytics-main/NFE/dashboards/shipping_costs_monitoring_nextjs/src/`

## Findings

### (a) Error boundary: NONE exists
- Grep for `ErrorBoundary|componentDidCatch|getDerivedStateFromError` → 0 hits.
- No `src/app/error.tsx`, no `src/app/global-error.tsx`.
- `page.tsx` has an `error` state but it ONLY catches *fetch* failures (fetchMeta/fetchOverview),
  not render-time throws. Lazy tabs wrapped in `<Suspense>` — Suspense catches *suspense*, NOT
  thrown render errors.
- **Consequence:** any single thrown exception inside any tab's render unmounts the whole React
  tree and produces the exact generic Next.js message. This is the architecture-level root cause
  that turns one bad cell into a full-page crash.

### (b) Code is broadly defensive — most suspect patterns are guarded
- `lib/format.ts`: all formatters null-safe (`value == null → "-"`).
- All recharts `domain=` computations guard empty/infinite (`Math.max(...[])` sites all have
  `.length === 0` early returns; CarrierShareChart:709 returns `[0,10]` on `!isFinite`).
- All tooltip `payload[0].payload` accesses guarded by `!active || !payload?.length` returns.
- `data[0].x` auto-expand sites (CarrierShiftsTable:83, DeviationsTable:75, etc.) sit behind
  `data.length` checks.
- `parseShares`/`parseShareItems` (OverviewTab:171, CostTrend:95) are try/catch-wrapped.
- AlertsTab `.toFixed` on nullable IssueRow fields all behind `!= null` guards.

### Ranked crash-site shortlist
1. **No error boundary (architectural) — THE amplifier.** Without it every other risk below is
   fatal-to-page instead of fatal-to-widget. Fix first regardless.
2. `BreakdownTab.tsx:592-596` `bdDims[i]` indexed by composite-key segment count — if a URL `?bd=`
   or alert-nav produces a key with more segments than dims, `dim` is undefined (soft, no throw,
   but mis-routes filters). Low.
3. `OutliersTable.tsx:234` `new Date(row.order_date).toLocaleDateString(...)` — if order_date null,
   Invalid Date renders, no throw. Low.
4. KPIRow `fmtRange` on undefined `period_label` → NaN render, no throw. Low.

### Best-guess root cause
The defensive coding means there is likely no single always-throwing line. The intermittent crash
is the **missing error boundary** converting a *rare* data-state throw (a new carrier/dim, an empty
slice, a malformed share JSON that slips a non-array past try/catch into a downstream `.map`, or a
recharts internal on degenerate single-point data) into a whole-page white-screen. The fix that
addresses the *reported symptom* directly is adding `src/app/error.tsx` (+ optionally per-tab
boundaries) so a thrown tab isolates to that tab instead of nuking the page.

## Fix shipped (principal session, S255)

Implemented the dwarf's #1 recommendation + true per-tab isolation:

- **New** `src/components/ErrorBoundary.tsx` — reusable per-tab React class boundary; logs the real error + component stack with an `[SCM]` tag, renders a contained "this panel hit an error" card with a Try-again reset.
- **`src/app/page.tsx`** — wrapped all 11 lazy tab `<Suspense>` blocks in `<ErrorBoundary>` so a thrown tab isolates to that panel (rest of dashboard stays up).
- **New** `src/app/error.tsx` — route-level boundary for page-level throws (KPI row, sidebar, page logic): real message + recover button, replaces the generic white-screen.
- **New** `src/app/global-error.tsx` — root-layout safety net (inline styles, own html/body).

Verified: `npx tsc --noEmit` → exit 0. Committed `d3c7039` (explicit pathspecs, 4 files, 185 insertions; other dirty NFE work untouched) and **pushed** `eb6bdee..d3c7039 main` to picanova/bi-analytics. Push auto-redeploys via GitHub Actions (see memory `reference_scm_deploy_github_actions`).

**What this fixes vs doesn't:** kills the full-page white-screen and surfaces the real error; does NOT eliminate the underlying rare data-state throw — it contains + logs it. Root cause still needs the `[SCM]` console line from the next occurrence to pin.

## Status: mitigation shipped + pushed. Open follow-up: confirm the Actions deploy went green; on next panel error, capture the `[SCM]` console error + the page/filter/month to pin the root-cause throw.
