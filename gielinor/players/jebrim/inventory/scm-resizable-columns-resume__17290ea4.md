---
quest: S265_scm-resizable-columns
sid8: 17290ea4
ts: 2026-06-18 00:00
open_dep: not started — plan handed over for the next session to implement
---

# SCM resizable table columns — hand-off plan

**Status:** in-progress (planned, not built). Next session implements.

**Where we are:** Niklavs asked for **drag-to-resize column widths** on the SCM dashboard tables, after the Country column kept overlapping the next column across the Cost Drivers tabs (truncation fix shipped for 3 of the 4 Cost-Drivers tables in `c1a6daf`, but RateChangesTable was missed and still overlaps). Decided **scope = ALL data tables**, not just Cost Drivers. Nothing built yet — this is the plan.

**Repo:** `bi-analytics` (external) — `NFE/dashboards/shipping_costs_monitoring_nextjs/`. Deploys on push to `picanova/bi-analytics` main. Edit-only until Niklavs gives the commit/push go (per his standing rule).

## Scope — 7 tables using `className="data-table"`

| Table | Column-def shape | Difficulty |
|---|---|---|
| `RateChangesTable.tsx` | `COLUMNS[]` + `<colgroup>` (same pattern as shifts) | easy |
| `ShiftsTable.tsx` (routing) | `COLUMNS[]` + `<colgroup>` | easy |
| `CarrierShiftsTable.tsx` | `COLUMNS[]` + `<colgroup>` | easy |
| `ProductShiftsTable.tsx` | `COLUMNS[]` + `<colgroup>` | easy |
| `OutliersTable.tsx` | check its column structure first | medium |
| `DeviationsTable.tsx` | check its column structure first | medium |
| `BreakdownTab.tsx` | tree/hierarchy table, expandable rows — most complex; columns may be dynamic | **hard — do last, may defer** |

The 4 Cost-Drivers tables share an identical `const COLUMNS = [{key,label,width,center?}]` + `<colgroup>{COLUMNS.map(c => <col style={{width:c.width}}/>)}` + `<thead>` mapping. Build the shared hook against that shape, wire those 4 first, then adapt Outliers/Deviations, then Breakdown.

## Design

**1. Shared hook — `src/lib/useResizableColumns.ts` (new).**
- Signature: `useResizableColumns(tableId: string, defaults: {key: string; width: number}[])`.
- State: `widths: Record<string, number>`, init = defaults merged over `localStorage["scm-colw-" + tableId]` (guard `typeof window`).
- Returns `{ widths, getHandleProps(key), resetColumn(key), resetAll() }`.
- `getHandleProps(key)` returns `onMouseDown` that: records `startX`, `startWidth`; attaches `document` `mousemove`/`mouseup`; on move sets `widths[key] = Math.max(MIN_COL_W, startWidth + (e.clientX - startX))`; on up persists to localStorage + detaches; sets `document.body.style.cursor='col-resize'` + `userSelect='none'` during drag, restores on up.
- `MIN_COL_W = 40`. No max.
- Persist the full `widths` map under `scm-colw-<tableId>` on mouseup.

**2. Resize handle in each `<th>`.**
- `<th style={{position:'relative', ...}}>` (th must be `position: relative`).
- Append `<span className="col-resize-handle" {...getHandleProps(col.key)} onDoubleClick={(e)=>{e.stopPropagation(); resetColumn(col.key);}} onClick={(e)=>e.stopPropagation()} />`.
- The handle's `onMouseDown` must `e.stopPropagation()` so it does NOT trigger the th's sort `onClick`. (Sort-vs-drag conflict is the main correctness trap — verify a drag never fires a sort.)

**3. CSS — add to `globals.css`.**
```
.col-resize-handle { position:absolute; top:0; right:0; width:6px; height:100%; cursor:col-resize; user-select:none; }
.col-resize-handle:hover { background: rgba(147,197,253,0.4); }
```

**4. Colgroup from state.** Replace `<col style={{width: col.width}}/>` with `<col style={{width: widths[col.key]}}/>`.

**5. Each table keeps `tableLayout: 'fixed'`** (shift tables already have it). Verify Outliers/Deviations/Breakdown — if any is `auto`, set fixed + ensure a `<colgroup>` exists, else col widths won't bind. Cells should keep `truncate`/`overflow-hidden` so content clips when a column is narrowed (shift-table cells already do post-`c1a6daf`).

**6. tableId per table:** `"rate-changes"`, `"routing-shifts"`, `"carrier-shifts"`, `"product-shifts"`, `"outliers"`, `"deviations"`, `"breakdown"`. Independent widths per table (do NOT share across the 4 Cost-Drivers tables — predictable + simpler).

**7. Reset affordance (optional, nice-to-have):** a small "Reset widths" text button near each table's export button calling `resetAll()`. Double-click on a handle already resets one column.

## Build order (phased)
1. Hook + CSS.
2. Wire `RateChangesTable` (also fixes its outstanding Country overlap) → verify drag, persist, double-click reset, sort-not-triggered.
3. Wire the 3 shift tables (mechanical copy of step 2).
4. `OutliersTable` + `DeviationsTable` (inspect column defs first).
5. `BreakdownTab` last — assess complexity; if the tree-table makes it disproportionate, defer with a logged note (don't silently drop it).
6. `tsc --noEmit` clean; manual drag test on each tab.
7. Show Niklavs the diff; commit + push on his go (push = deploy).

## Files to read first
- `src/components/RateChangesTable.tsx` — start here (and it still has the Country overlap).
- `src/components/ShiftsTable.tsx` / `CarrierShiftsTable.tsx` / `ProductShiftsTable.tsx` — the shared COLUMNS+colgroup pattern; see the `c1a6daf` Country-cell flex/truncate treatment to mirror.
- `src/components/OutliersTable.tsx`, `DeviationsTable.tsx`, `BreakdownTab.tsx` — inspect column structure before wiring.
- `src/lib/useChartZoom.ts` — existing hook style to match (mouse-drag + document listeners precedent).
- `src/app/globals.css` — where the handle CSS lands.

## Watch-outs
- **Sort vs drag:** the handle mousedown/click must stopPropagation or every resize fires a column sort. Test explicitly.
- **SSR:** guard all `localStorage`/`window` access.
- **Breakdown tree:** dynamic/!indented columns — hardest; may warrant its own follow-up.
- This is additive to the `c1a6daf` truncation fix (truncation = default state; resize lets you widen). Don't remove the truncate/min-w-0 cell treatment.
