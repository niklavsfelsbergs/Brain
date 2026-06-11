# Go-live (stub-year) realization — a mid-year start captures volume-share, not calendar-share

**Source:** [[S219_e0eb59c8_eu-tender-final-report-content-pass|S219]] (e0eb59c8), 2026-06-12 — the EU-tender go-live cut Niklavs asked for + his "how is Aug–Dec only ~half?" probe.

## The concept
For a savings program with an annualized run-rate, "what does *this* year bank if we go live mid-year?" is **not** the
calendar fraction of the year remaining. It is the **cumulative volume share** of the months from go-live to year-end,
because saving accrues per shipment, and shipment volume is seasonal.

For the PCS-PL shipping book (2025 seasonal shape, per-country, from `annual_stats.global_shape.monthly_share`):
- Aug–Dec = **52.0%** of annual volume (vs a naïve 5/12 = 41.7%).
- But the window decomposes: **Aug+Sep+Oct = 18.5%** (the year's *lowest* months — late-summer lull) + **Nov+Dec = 33.5%** (the real peak). October is ~average, not peak.
- So a 2026-08-01 go-live banks ~51% of the run-rate (full plan ≈ €0.97M of €1.91M; base ≈ €0.49M of €0.98M), and the
  stub-year value is **decided by being live before November** — slipping Aug→Oct costs only ~€0.23M, but slipping
  past Nov-1 forfeits the peak (Oct-1 ≈ €0.76M, Nov-1 ≈ €0.64M, Dec-1 ≈ €0.40M).

## The method (defensible, reusable)
stub_saving(go_live_month m0) = vol_share(≥m0) × plan_peakfree + peak_diff × (peak-window volume in [m0..12] / total peak-window volume)
- `plan_peakfree = plan_ann − peak_diff` (peak is the only across-year-varying cost component once fuel is flat).
- The annual peak differential (−€41,194 here, a small drag) lands **entirely inside Oct–Dec**, so a window that
  includes the peak carries it; a Nov/Dec-only start carries the pro-rated slice.
- Caveats to always state: linear within-month accrual (a phased pilot ramp pushes realization *later* → treat the
  full-switch date as a ceiling); **gross of one-time switching cost**; gated slices keep their gates.

## Why it matters
The reports headlined only the steady-state run-rate; the first CFO question is "so what lands in 2026?" — and the
intuitive 5/12 answer understates a peak-heavy book by ~€0.18M. The realization curve also reframes the deadline: the
program's in-year value is a **November cliff**, not a smooth ramp.

Implemented in `final_report_v2/` §04 + `final_report_no_hermes_v2/` §04 (stub_year helpers; read the seasonal shape
from `annual_stats.json`). Links: [[eu-tender]] · [[2026-06-11-eu-tender-annualization-method]].
