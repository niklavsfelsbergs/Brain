---
date: 2026-06-18
session: 5cbb1d00
quest: S265_scm-resizable-columns
domain: scm
---

# SCM dashboard — drag-to-resize table columns (`useResizableColumns`)

Shipped [[S265_17290ea4_scm-resizable-columns|S265]] (commit a22ca52, deployed). Reusable pattern for any SCM `.data-table`.

**Hook:** `src/lib/useResizableColumns.ts` — `useResizableColumns(tableId, defaults: {key,width}[])` → `{ widths, getHandleProps(key), resetColumn, resetAll }`. Widths persist per table in `localStorage["scm-colw-<tableId>"]` (merged over defaults, SSR-guarded). `MIN_COL_W = 40`. Drag = document mousemove/up listeners + body `cursor:col-resize`/`userSelect:none`; persists the full map on mouseup. Double-click a handle resets that column.

**Per-table wiring (3 edits):** colgroup `<col style={{width: widths[col.key]}}/>`; append `<span className="col-resize-handle" {...getHandleProps(col.key)} />` inside each `<th>`; table needs `tableLayout:'fixed'` + a `<colgroup>`.

**Sort-vs-drag trap:** the handle's `onMouseDown` *and* the trailing `onClick` both `stopPropagation()` so a resize never fires the column's sort `onClick`.

**Sticky-header gotcha:** `.data-table th` is `position:sticky` — that already makes it a containing block for the absolutely-positioned handle. Do NOT set the th to `position:relative` (would un-stick the header).

**Wired (6/7 tables):** RateChangesTable (rate-changes), ShiftsTable (routing-shifts), CarrierShiftsTable (carrier-shifts), ProductShiftsTable (product-shifts) — all shared `{key,label,width}`+colgroup. OutliersTable (outliers) + DeviationsTable (deviations) were `table-layout:auto` with no colgroup → added fixed+colgroup+width defaults + `.data-table.resizable-cols td {overflow:hidden;text-overflow:ellipsis}` so cells clip when narrowed.

**Deferred:** BreakdownTab — percentage-width colgroup + dynamic per-preset columns + sticky col + tree rows; the pixel hook doesn't fit, needs a percent-aware variant.

**Country default = 200px** on the four shift/rate tables: the Country cell carries two action icons (drill, set-filter) that squeeze the name; at the old 110/80 default it truncated to "Un…". Resize fine-tunes from there.

Source of truth: the dashboard code in `bi-analytics-main/NFE/dashboards/shipping_costs_monitoring_nextjs/`. See [[scm]] domain digest.
