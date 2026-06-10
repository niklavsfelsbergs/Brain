---
quest: S189_maersk-hermes-oversize-corrections
sid8: e3de8457
ts: 2026-06-10 14:45
open_dep: awaiting Maersk girth-definition reply — Niklavs to send the drafted clarification to Stefan; answer decides pure-girth (current) vs L+girth (Maersk oversize lane ~collapses)
---

# Resume — Maersk + Hermes oversize corrections + DB Schenker savings split

## Status
in-progress (engines + full cascade shipped + committed; one external dependency open).

## Where we are
Both engines corrected (`maersk-3.1.0` ceiling, `hermes-2.1.0` girth gate) and committed (bi-analytics fceacc6); Q1 + 2025 cost matrices regenerated; routing report (with the new DB-Schenker-vs-other savings split, 61% low-confidence), DB Schenker validation, decision report, and carrier overview all rebuilt + committed (6833671). Tender Q1 saving moved €377k → €276,951. Pure-girth is the working assumption for Maersk's "300 cm."

## Next concrete step (Niklavs-gated)
**When Stefan (Maersk) replies on the girth definition:** if he confirms pure girth = 2(W+H), nothing changes. If he means **L+2W+2H** (length+girth — the standard carrier format), re-run: corrected maersk engine value → `cost_matrix_2026q1.py` + `cost_matrix.py` → `build_final.py` → `routing_report.py` → `validate.py`/`report.py` → `decision_scorer_2026q1`+`report_2026q1` → carrier_overview chain. Maersk oversize fallout jumps 845→2,819 and the saving drops toward ~€200k. Then refresh the management deck (deferred this whole time).

## Also still open (pre-existing, not this session)
- Management deck (`management_briefing/`, untracked, S187/85b0fcc3) still shows €377k — refresh after girth is confirmed.

## Files / paths to read first (bi-analytics, NOT brain)
1. `2_analysis/carriers/maersk/constants.py` (the 175/300 ceiling + the girth-assumption comment) + `calculate.py` `_decide_eligibility`.
2. `2_analysis/carriers/hermes/constants.py` + `calculate.py` (girth gate).
3. `2_analysis/routing_2026q1/build_final.py` (the `saving_split` block) + `routing_report.py` §00.
4. `2_analysis/routing_2026q1/validation/db_schenker/carrier_ceiling_impact.py` (the surgical impact + sensitivity).
5. This session's quest-log: `quest-log/in-progress/S189_e3de8457_maersk-hermes-oversize-corrections.md`.

## The drafted Stefan question (Niklavs to send)
On the handling ceiling you confirmed (175 cm / 300 cm): your Oversized Surcharge table lists two separate measures, "L+W+H" and "L+2W+2H." When you say the 300 cm cap is "girth," which one is it — L+2W+2H, L+W+H, or girth on its own (2×(width+height))? And is the 175 cm just the single longest side? We want to screen our parcels against exactly the measure you use.
