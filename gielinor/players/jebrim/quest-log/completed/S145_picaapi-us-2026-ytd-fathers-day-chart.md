# S145 — PicaAPI US 2026 YTD weekly volume chart (shipping-agent mart pull)

**Actor:** shipping-agent (emulation, Jebrim namespace)
**Asked:** 2026 YTD re-run of the 2025 Father's Day chart — weekly US PicaAPI shipment volume by ship date, ISO Mon weeks, Jan 1 → max produced date, 3 holiday verticals (Valentine's / Mother's / Father's 2026). Same population + method as the 2025 pull.

## Scope / tier
- Gold contract only (`shipping_mart.fact_shipments`). No CLAUDE.local.md present — gold perimeter absolute. Pure gold pull, no upstream needed.
- Population: `source_system = 'PicaAPI'` (MerchOne line, not a shop), `destination_country_code = 'US'`. Axis = `order_produced_date` (ship proxy; received_by_carrier ~half-null on slice). Weekly ISO Monday.

## Status log
- Read how_to.md + 2025 driver + 2025 SQL/CSV — reused population verbatim.
- Max produced date = **2026-06-02** (= today). YTD total = 89,492.
- Weekly pull: 23 raw ISO weeks. Leading 2025-12-29 ISO week = 136 (only Jan 2-4 fragment, Dec excluded by YTD filter) → dropped from plotted line to match 2025's first-full-week start; noted in writeup.
- Tail: 2026-06-01 week = 949 (Mon 937 + Tue 12 only — partial, still producing). Prior week 2026-05-25 = 3,369 depressed by US Memorial Day (Mon May 25 = 23 shipments).
- Plotted: 22 weeks 2026-01-05 → 2026-06-01.
- Built chart via adapted driver (3 verticals, x-range extended past data so future Father's Day Jun 21 vertical shows the gap).
- Reconcile: 22 plotted (89,356) + 136 fragment = 89,492 = mart YTD total. Ties exactly. HTML carries all 3 markers + title.

## Headline
- Two spring peaks: Feb 2 week (8,726) ahead of Valentine's; late-Apr/early-May ramp (Apr 27 = 8,940, May 4 = 8,124) ahead of Mother's Day. Both holidays passed.
- No clear pre-Father's-Day build yet in early June — but data ends Jun 2, ~3 weeks before Father's Day, and the run-up week hasn't shipped. Inconclusive by design.

## Deliverables (outside brain)
- Chart: workbench/analysis/picaapi-us-2026-ytd/outputs/20260602-082140--weekly-us-volume-2026-ytd.html
- CSV: workbench/analysis/picaapi-us-2026-ytd/data/weekly_volume_simple.csv
- SQL: workbench/analysis/picaapi-us-2026-ytd/sql/weekly_volume.sql
- Driver: workbench/analysis/picaapi-us-2026-ytd/build_simple_line.py

## Follow-up — 2025-vs-2026 overlay (Mother's Day volume diff)
Principal asked for a YoY overlay to see the Mother's Day volume diff. No mart re-pull — reused the two existing validated weekly pulls (2025 full-year + 2026 YTD CSVs).
- **Method:** aligned by ISO week so the Mother's-Day week lines up across the calendar drift (2nd Sunday of May = 2025-05-11 / 2026-05-10, **both ISO week 19** — confirmed). Plotted on the 2026 Monday per week. Window = the spring stretch 2026 covers (ISO wk 2→22, through May 25). Dropped the partial final 2026 week (Jun 1, Mon-Tue only) so it doesn't read as a false cliff vs a full 2025 week.
- **Headline:** Mother's-Day-week (ISO wk 19) **8,124 in 2026 vs 5,559 in 2025 = +46%**. Pre-MD ramp peak even wider: wk Apr 27 8,940 vs 3,142 (+185%), wk Apr 13 6,457 vs 554 (+1066%). 2026 sits above 2025 in **every** plotted week — the whole US MerchOne line stepped up YoY, not just the holiday. (Note wk May 25 2026 = 3,369 depressed by US Memorial Day Mon.)
- **Deliverables:** chart `workbench/analysis/picaapi-us-mothers-day-yoy/outputs/20260602-141952--weekly-us-volume-mothers-day-yoy.html`; driver `build_overlay.py`; data `data/weekly_{2025,2026}.csv` (copies of the two source pulls).
