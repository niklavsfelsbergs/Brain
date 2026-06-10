---
quest: S190_eu-tender-red-team-audit-and-report-rebuild
sid8: 9a064d86
ts: 2026-06-10 22:30
open_dep: annual report (the 4th report) not yet built — full spec in the annualization note
---

# Resume — EU-tender annualization (the 4th report)

## Status
**in-progress.** Audit shipped + committed; all 3 Q1 reports rebuilt on Hermes flat-7% + committed (bi-analytics `052d3c4`, headline €275,484/9.32%); the annualization method/plan is **locked and saved**. Remaining: build the 4th report.

## Where we are
Both engine rebuilds (oversize + Hermes flat-7%) are done and committed. The annualization plan is fully spec'd. Nothing blocks the build.

## Next concrete step
**Build the annualization report** — a 4th report, `2_analysis/annual_2026/`, parallel to `routing_2026q1/`, per the plan note's Part A + build checklist. Recipe: per-country full-year volume (2026-Q1 × 2025 seasonal ratio) → cost = peak-free base × annual volume + peak × peak-window volume (engines from constants; invoiced UPS/DBS/Direct-Link from a 2025-matrix-derived Q4 peak premium; Maersk-FR €0.25 assumed) → fixed routing re-priced, no re-route → both sides → saving as a fuel-rate band → the Q1→annual bridge waterfall → render reusing the routing report shell. Q4 product-mix NOT adjusted (caveat only).

## Files to read first
- `players/jebrim/research/2026-06-10-eu-tender-annualization-method-and-assumptions.md` — **the complete build spec** (Part A method + Part B assumptions ledger + build checklist).
- `players/jebrim/research/2026-06-09-eu-tender-2026-red-team-audit.md` — the audit (tier-(a) A0–A5 context).
- bi-analytics `2_analysis/routing_2026q1/{build_final.py, routing_report.py, routing_stats.json}` — the shell + structure to mirror.
- bi-analytics `2_analysis/data/{cost_matrix_2026q1/, cost_matrix/}` — Q1 + 2025 matrices (both hermes-2.2.0/7%, current).

## Watch-outs
- bi-analytics is a SEPARATE repo — pathspec-scoped commits only, principal-gated, never push.
- The annualization note itself was updated this session and committed in this close — it's current.
- A0 (Maersk MAERSKUK scope) is still unconfirmed — flag it doesn't silently distort the annual Maersk lever.
