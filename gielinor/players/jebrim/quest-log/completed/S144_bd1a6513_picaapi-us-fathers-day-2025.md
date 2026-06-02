# Shipping-agent pull — Picaapi US Father's Day 2025 impact

**Role:** shipping-agent (emulation) · **Player in scope:** Jebrim · **Date:** 2026-06-02 · **Tier:** gold-contract

## Ask
Did US Father's Day 2025 (Sun 15 Jun) measurably impact US-destination shipment volume for "Picaapi"? Ship-date-aware (gift effect lands in the 1-2 weeks before 15 Jun). Confound-check vs Mother's Day, Memorial Day, seasonality, month boundaries. Chart + CSV out-of-brain + written verdict.

## Scope resolved
- **"Picaapi" → `source_system = 'PicaAPI'`** (the MerchOne B2B platform line). No `shop` named picaapi exists; all "pica" shops are picanova.com storefronts. PicaAPI is the only mart match for the name. Stated to principal as a production-line, not a brand/shop.
- **US → `destination_country_code = 'US'`** ('United States'), 0% null on the slice.
- **Ship-date anchor → `order_produced_date`** (dispatch proxy; `received_by_carrier_date` 53% NULL on this slice, unreliable per known-dq). Confirmed with principal-brief intent (ship date, not order date).

## Population
- US PicaAPI 2025 by order-created date: **76,108**; by ship/produced date within 2025: **75,152** (diff = produced dates spilling into early 2026 or pre-2025).
- DQ caveats: strong Mon-Sat ship cadence (Saturdays near-zero, no Sunday production) → weekly grain is the honest comparison unit. Late-Dec produced dates run into Mar 2026 (lag), immaterial to the June question.

## Numbers (ship-date weekly, ISO Mon-start)
- **Father's Day ship window (Mon 9 - Sat 14 Jun): 1,459 shipments.**
- Trailing 4 weeks (12 May - 8 Jun): 3,736 total → 934/wk avg → FD window **+56%**.
- Week before (2-7 Jun): 908 → **+61%**.
- Week after (16-21 Jun): 700 → **+108%**.
- Surrounding calm baseline (mid-Jun - Jul): ~600-900/wk.

## Confounds
- **Mother's Day (Sun 11 May):** ship week 5-11 May = 5,559 — a far bigger gift wave; +the 28 Apr week (3,142). Father's Day is real but ~1/4 the size.
- **Memorial Day (Mon 26 May):** ship week 26 May - 1 Jun = 631 — NO bump. Not a confound.
- **Month boundary:** FD spike is mid-June (9-14), isolated; not a 1st-of-month artifact.
- **Q4 peak:** Nov-Dec mega-wave (up to 11,881/wk) — separate, well after.

## Verdict
**YES — measurable, moderate-confidence.** The 9-14 Jun ship week is a clean, isolated +56% spike vs trailing baseline, concentrated in the days immediately before Father's Day, matching the gift-ship signature. Not month-boundary, not Memorial Day. Smaller and shorter than the Mother's Day wave. Single-year (no YoY); confidence is moderate not high.

## Deliverable (out-of-brain)
- Chart: `shipping-agent/workbench/analysis/picaapi-us-fathers-day-2025/outputs/20260602-074748--picaapi-us-weekly-fathers-day-2025.html`
- Data: `.../data/weekly_volume.csv`
- SQL: `.../sql/daily_weekly_volume.sql`

## Checks done
- Resolved Picaapi against both source_system + shop before trusting the name.
- Weekly grain chosen after spotting the Sat-zero / Sun-zero cadence (daily would mislead).
- Father's Day spike reconciled across 3 baselines (trailing-4wk, week-before, week-after) — all positive, consistent direction.
- Confounds individually checked (Mother's Day, Memorial Day, month boundary) rather than assumed.

## Open / needs principal
- Single-year only — no 2024 YoY comparison run (would lift confidence to high). 2024 PicaAPI US data exists (floor 2024-01-01) if a YoY check is wanted.
- "Picaapi"=MerchOne line resolution should be confirmed; if the principal meant the picanova.com US storefronts instead, re-scope.

## Follow-up (2026-06-02) — simplified chart rebuild
- Ask: rebuild the existing weekly-volume chart in a simpler form — single line, two labeled holiday verticals (Mother's Day 11 May, Father's Day 15 Jun), no bands / no extra series / no Q4 box. No new query — reused saved `weekly_volume.csv`.
- Built off the existing CSV (52 weekly rows, full 2025). Wrote a 2-col `weekly_volume_simple.csv`, drove the chart through the shipping-agent harness styling (`_report_style` + `render_html`) plus a thin driver adding the two `add_vline` markers — the harness CLI has no vertical-line flag and force-labels every point, both wrong for a minimal chart.
- Verified: exactly 1 trace, 52 pts, no fill (no band), 2 vertical shapes, 2 annotations ("Mother's Day"/"Father's Day"), y-title "US shipments per week". Data sanity-checks against the prior verdict — Mother's Day wave peaks 5,559 (5 May wk), Father's Day window 1,459 (9 Jun wk), Q4 peak 11,881 (15 Dec wk).
- Deliverable: `shipping-agent/workbench/analysis/picaapi-us-fathers-day-2025/outputs/20260602-075509--weekly-us-volume-simple.html`
- Driver kept at `.../picaapi-us-fathers-day-2025/build_simple_line.py` (reusable if labels/dates need tweaking).
- Flag: the chart harness can't express vertical reference lines or suppress per-point labels via its CLI — needed a thin driver around its style module. Worth a `--vline` / `--no-point-labels` flag in the harness if marked-date line charts recur (maintainer-gated edit, not mine to make).

## Close (S144, principal-self, sid bd1a6513)
- Quest born + graduated this session: shipped (verdict + 2 charts + CSV/SQL out-of-brain), no open dependency. Optional follow-ups (2024 YoY; confirm Picaapi=MerchOne-line vs picanova.com US storefronts) are new quests, not blockers.
- **Harvest:** read the full-year `weekly_volume.csv` directly and broke out all four gift holidays the principal named (Valentine's wasn't in the original analysis). Bank draft → `bank/drafts/notes/shipping/merchone-us-holiday-volume-peaks.md`. Single-week peaks: Christmas 11,881 >> Mother's 5,559 > Valentine's 3,983 > Father's 1,459 (vs ~550 calm baseline).
- Entry-OPEN leaked (went straight to work on "Hey Jebrim"); posted late at close on the hook trip. Self-obs not drafted — known recurring leak already covered in examine.
