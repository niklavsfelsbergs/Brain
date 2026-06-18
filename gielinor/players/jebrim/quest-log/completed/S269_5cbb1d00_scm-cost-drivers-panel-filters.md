# S269 — SCM Cost Drivers panel: filter-reactivity + inline driver chart + type filter

**Player:** Jebrim · **sid8:** 5cbb1d00 · **Date:** 2026-06-18 · **Status:** completed (shipped + pushed to picanova/bi-analytics, deployed)

Continuation of the same session that did [[S265_17290ea4_scm-resizable-columns|S265]] (resize). Reopened after the first wrap on a string of Cost-Drivers-tab UX asks. All shipped to the live tree (`bi-analytics-main`, branch main) and pushed = deployed via GitHub Actions.

## Ask → deliverables (4 commits)

1. **Top Cost Drivers/Savers panel reacts to sidebar filters** (`4db2a24`). The panel fetched date-only params, ignoring the sidebar dimension filters — "full book." Changed `topQs` in `CostDriversTab.tsx` to feed the full filter set (`filterQS(filters)`); the backend `/api/cost-drivers-top` route already applied countries/providers/sites/orderSources, so no API change. Now re-scopes to order source / production site / country / carrier.

2. **Driver click shows an inline chart instead of setting filters** (`ec98015`). Clicking a driver called `handleDriverNavigate` (page.tsx:602) which overwrote the sidebar filters — and now that the panel reacts to those, every click collapsed the list. Repointed the top-panel click to toggle an inline chart below the lists (`selectedDriver` state), no filter mutation, no tab switch — click through freely. The tables' funnel "set filters to this corridor" buttons keep using `handleDriverNavigate` (unchanged). Chose this (inline-in-panel) over re-using the inner-table expand per a multiple-choice.

3. **Inline chart matches the driver's source tab** (`c14eb4a`). First cut rendered a single `CostTrend` (rate-changes style) for every driver type; Niklavs caught that shift drivers come from other tabs. Now: rate → `CostTrend`; carrier/routing/product → `CarrierShareChart` (the chart those tabs render on expand) — routing passes its packagetype, product its product, the driver's carrier highlighted.

4. **Driver-type filter on the panel** (`e4fe742`). Added a "Driver types" chip row (rate/carrier/routing/product, all on by default), distinct from the inner-tab toggle. Filtered **server-side** in the route (before the top-N slice) so selecting one type returns the true top-N within it, not just the rows that made the overall top-N. Deselect all → empty, no fetch.

Plus, earlier in the same session: Country-column default widened to 200 (part of the [[S265_17290ea4_scm-resizable-columns|S265]] resize ship, `a22ca52`).

## Files

- `src/components/CostDriversTab.tsx` — topQs→filterQS; selectedDriver inline chart (CostTrend vs CarrierShareChart by type); typeFilter chips + fetch wiring.
- `src/app/api/cost-drivers-top/route.ts` — `types` param, filter before top-N slice.

## Parallel-session notes

Across the pushes, two ORWO-session (e455d12d) rider commits rode along beneath mine on shared main and were published with Niklavs' explicit push-all approval each time: `7af8c14`/`67a8430` (with a22ca52) and `3ca551b` (with c14eb4a). All non-dashboard; deploys shipped only the SCM dashboard changes. `5c3ca76` (another session's product-shifts filter fix) was already on the remote, not pushed by me.

## No pending external actions

All 4 commits pushed (final tip e4fe742); deploys triggered + (a22ca52) verified green via Actions API. Nothing pending. Quest complete — no open dep. ([[S265_17290ea4_scm-resizable-columns|S265]] resize quest stays in-progress separately for the deferred BreakdownTab.)
