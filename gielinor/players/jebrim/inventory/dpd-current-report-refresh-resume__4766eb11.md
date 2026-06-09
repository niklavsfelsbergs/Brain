---
quest: S180_dpd-current-report-refresh
sid8: 4766eb11
ts: 2026-06-09 19:05
open_dep: awaiting principal commit-go + scope confirmation on the bi-analytics commit (the 2 scope questions)
---

## Status: deliverable complete; the bi-analytics commit is the only open item (principal-gated)

UPS +5% GRI wired + routing reran (13.4%→12.8%, €377k); all three EU-tender reports refreshed to kept-DPD-on-current + post-GRI; decision_report re-scored (renew_dpd_pl +€68k); 5 sibling cards reconciled; DPD PL (current) added to carrier_overview as the #1 grid winner. Engine gate −0.4%, 11/11 fixtures. **Everything is done except the commit.**

## Next concrete step (a question for Niklavs)

Give the **go** to commit the bi-analytics deliverable as one unit, and confirm the two scope questions:

1. **Include the 3 untracked decision-track files** (`_decision_sets_2026q1.py`, `decision_scorer_2026q1.py`, `report_2026q1.py`)? They're integral (the `dpd_pl→dpd_pl_current` wiring + scorer + the report I edited) but were authored ~Jun 5 and never committed — confirm they're this deliverable's, not another live session's.
2. **Confirm the excluded files** stay out (UPS `engine.py`, `carriers/dhl_paket/*`, `NFE/.claude/reference/*`, `NFE/CLAUDE.md`, `_data/hands/*`, `docs/ASSUMPTIONS.md`, untracked dirs) — parallel-session work, not mine.

Commit is **pathspec-scoped** (shared tree dirty; S144 sweep hazard + a live `a0b39f49` §Z sibling deleting jebrim drafts). Proposed message: `S180: DPD-PL current-contract engine forward + UPS +5% GRI + EU-tender reports refresh`. Brain close artifacts already committed separately this session.

## Files to read first

- `bi-analytics-main/NFE/projects/2_EU_tender_2026/2_analysis/routing_2026q1/build_final.py` — the GRI wiring (`UPS_GRI_PCT`, `today_eur_fwd`).
- `.../carrier_overview_v2/sections/dpd_pl_current.md` + `lib/competitive_map.py` (`CURRENT` set) + `build_report.py` (registration) — the new entry.
- `.../decision_report/report_2026q1.py` — the reframed DPD blurb.
- `quest-log/in-progress/S180_4766eb11_dpd-current-report-refresh.md` — full session narrative + Cascade.
- [[S178_09c2d809_dpd-pl-current-engine]] (completed/) — the engine build this continues.

## Follow-ups (non-blocking, for later)

- routing_report France caveat: the Maersk-FR-extension ~€60k estimate predates the DPD-current engine → re-estimate against DPD's new FR capture.
- Annualisation (full-year cost_matrix already carries `dpd_pl_current` after this session's rebuild — picks up automatically when annualisation runs).
