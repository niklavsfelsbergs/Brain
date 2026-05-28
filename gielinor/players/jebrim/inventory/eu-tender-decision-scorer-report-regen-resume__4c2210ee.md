# RESUME — EU Tender 2026 (next session) — from S118 (f41737e5)

**Status:** in-progress (EU tender ongoing; S118's own deliverables shipped — regen + full doc reconciliation).
**Repo:** out-of-tree `bi-analytics-main/NFE/projects/2_EU_tender_2026/`. Tender HEAD after this session: docs + cross_carrier refreshed; engines unchanged since S117 (`96bc47f`).

## Where we are
6 deterministic-ready engines rebuilt+committed (maersk-3.0.0 / hermes-2.0.0 / dhl_express-2.0.0 / austrian_post-2.0.0 / dpd_pl-2.0.0 / gls-2.0.0); cost_matrix re-run (S117); decision_scorer + report regenerated (S118); all 8 docs + cross_carrier_view.html reconciled to current state. Baseline do-nothing = €2.91M Q1.

## Decision-so-far (trustworthy engines = scorer realistic floor)
- **Renew Maersk + add Hermes ≈ €250k/Q1, full coverage** (leader). Keep-all-incumbents + add Hermes ≈ €224k. renew_maersk_drop_dpd_pl_plus_gls_dhl_express ≈ €196k. **GLS the strong alternate.**
- **Hermes = MVP entrant** (alone covers 96.5% @ €443k cherry-pick).
- **Maersk renewal alone strands ~25k parcels** (engine rejects its own incumbent oversize/country tail) → must pair Maersk with a broad-coverage carrier (Hermes/GLS).
- Provisional sets leaning on FedEx/Güll/DHL Paket as NEW_OFFER score higher (€330–379k) **but rest on under-priced held engines** (FedEx prices residential/fuel/vol-weight at 0) → optimistic ceilings, will shrink once priced. This is why we wait, not decide.

## Done this session (4c2210ee, 2026-05-28) — UNCOMMITTED, awaiting principal go
1. **`decision_report.html` HARDENED** ✓ (report.py prose). Trustworthy/provisional split (HELD_ENGINES + _is_trustworthy; KPI leads with trustworthy full-cov leader renew_maersk_plus_hermes €247.7k vs provisional ceiling renew_maersk_plus_fedex €379k; per-row TW/PROV badge, 17/73 of 90); decision-so-far in summary; 2 material caveats callout (dpd_pl CH €484k, gls EFTA €278.9k); full Section-04 carrier rewrite (principal chose full); refreshed frontier/fuel/what-changes prose. Regenerated + verified (numbers ground-truthed; NOT pixel-eyeballed). Opened in browser.
2. **Full-year basis CHOSEN = Option 1** (replay 2025 actuals on 2026 cards). Feasibility GREEN: repoint population.sql silver→gold (silver cost_summary gone; all 22 fact cols + 14 buckets on gold 1:1), 2025 in-scope = 2.93M ships, ~26M-row matrix (chunk by month). Recorded in DECISIONS.md / NEXT.md item 3 (5-step build plan) / FULL_YEAR_SCOPING_NOTE.md.

## Next concrete step (agent-drivable — pick up here)
1. **COMMIT** the report-hardening + doc updates (principal go): tender = report.py + decision_report.html + docs/{DECISIONS,NEXT}.md + FULL_YEAR_SCOPING_NOTE.md (commit -- <pathspec>, untracked debris stays out); brain = jebrim quest-log + inventory + comms + intent.
2. **Full-year build (Option 1)** — the 5-step plan in NEXT.md item 3: (a) repoint+widen population.sql to gold 2025, (b) chunk cost_matrix.py by month, (c) wire seasonal peak/demand surcharges, (d) re-price do-nothing baseline on 2026 rates, (e) fuel band → re-run scorer+report. Meaty next phase.
3. **Other meantime workstreams** (carrier-independent): service-quality sidecar (S034 cond #2); fuel sensitivity sweep across the 6 rebuilt engines.
4. **Refresh the management deck** (`docs/EU_Tender_2026_Management_Summary.*`) — STALE pre-ranking snapshot. Flip to current-situation overview. `.pptx` needs PowerPoint closed; `.md`+`.html` regenerate freely.

## Status checks (principal / Picanova ops — phrased as questions)
- The 4 internal items (fold into engine assumptions when answered): DHL Express incoterm — DTP? DHL Express pickup days/week? AP parcels-per-pallet density? AP import-VAT-8% treatment?
- Any UPS offer / FedEx round-2 / DHL Paket round-2 / Güll reply landed?

## Carrier-blocked (awaiting; assumed + documented per locked strategy)
UPS (no offer); FedEx r2 (June ZOOM 2/9 Jun); DHL Paket r2 (Bulky €2.31M); Güll r1 reply (engine still guell-1.0.0). **Strategy:** assume + document, escalate only when decision-vital; the 3 material deferrals (dpd_pl CCD €484k, gls EFTA €278.9k, AP density ±€20–82k) carry explicit "revisit if shortlisted" triggers in ASSUMPTIONS.md.

## Files to read first
- `carrier_responses_to_open_questions/CROSS_CARRIER_OVERVIEW.md` (readiness)
- `2_analysis/docs/NEXT.md` (current handoff)
- `2_analysis/data/scenarios.parquet` (90 sets) + `decision_report.html` + `cross_carrier_view.html` (refreshed)
- `2_analysis/docs/DECISIONS.md` (2026-05-28 entries) + `REPORT_NOTES.md`

## Session commits
tender: ede440f (report regen) · 002486c (8 docs) · 465ba56 (revisit triggers) · cross_carrier_view.html (refreshed, committed at close). brain: cb6e91c / b6cfcbf / 8048abb (+ close commit).
