---
quest: S265_scm-resizable-columns
sid8: 5cbb1d00
ts: 2026-06-18 17:45
open_dep: SHIPPED — committed a22ca52 + pushed to picanova/bi-analytics main (deploy) 2026-06-18; Country default widened to 200; only Breakdown (deferred) remains
---

# SCM resizable columns — implementation resume (session 5cbb1d00)

**Where we are:** Built drag-to-resize on 6 of 7 SCM data tables in `bi-analytics-main` (live deploy tree, branch `main`, HEAD c1a6daf). Edit-only — NOT committed, NOT pushed. `tsc --noEmit` clean. Not yet live-tested.

**Files touched (all in `NFE/dashboards/shipping_costs_monitoring_nextjs/src/`):**
- `lib/useResizableColumns.ts` — NEW shared hook (localStorage `scm-colw-<tableId>`, MIN_COL_W=40, double-click reset, sort-not-triggered via stopPropagation on mousedown+click).
- `app/globals.css` — `.col-resize-handle` + `.data-table.resizable-cols td` clip rule.
- `components/RateChangesTable.tsx` (rate-changes), `ShiftsTable.tsx` (routing-shifts), `CarrierShiftsTable.tsx` (carrier-shifts), `ProductShiftsTable.tsx` (product-shifts) — mechanical wire of the shared colgroup pattern.
- `components/OutliersTable.tsx` (outliers), `DeviationsTable.tsx` (deviations) — added tableLayout:fixed + colgroup + width defaults + `resizable-cols` class; Outliers thead refactored to mapped OUTLIER_COLUMNS.

**Next concrete step:**
1. Niklavs live-tests the 6 tables: drag a header edge → width changes; refresh → persists; double-click handle → that column resets; dragging never triggers a column sort.
2. On his go: `git commit` (pathspec the 7 files) + push to picanova/bi-analytics main = DEPLOY. Edit-only until then.
3. Breakdown (7th): DEFERRED — percent-width colgroup + dynamic preset columns + sticky col + tree rows; pixel-resize hook doesn't fit. Decide later: percent-aware variant or leave.

**Known wart to mention if it surfaces:** Outliers renders one sub-table per provider, all sharing tableId "outliers"; resizing one won't live-update other simultaneously-expanded provider sub-tables until re-render (localStorage syncs on mouseup, re-read on mount). Cosmetic; one provider open at a time is the norm.

**Files to read first (if resuming cold):** this file; `quest-log/in-progress/S265_17290ea4_scm-resizable-columns.md` (full impl log); `src/lib/useResizableColumns.ts`.
