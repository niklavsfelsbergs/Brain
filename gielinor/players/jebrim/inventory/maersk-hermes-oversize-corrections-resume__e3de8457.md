---
quest: S189_maersk-hermes-oversize-corrections
sid8: e3de8457
ts: 2026-06-10 17:20
open_dep: none blocking — girth question RESOLVED (L+2W+2H, encoded 3.2.0). Remaining: management-deck refresh (optional, Niklavs-gated) + Hermes red fixtures (Niklavs' to fix)
---

# Resume — Maersk + Hermes oversize corrections + DB Schenker savings split

## Status
in-progress (all engine work + full cascade shipped + committed; girth question now closed; one optional deck refresh + a non-mine test-suite flag remain).

## Where we are
**Girth confirmed = L+2W+2H** by Maersk → `maersk-3.2.0` (ceiling `length_plus_girth_cm ≤ 300`). Full cascade re-run on 3.2.0 + committed `hermes-2.2.0` (flat-7% fuel). Final tender Q1 saving **€201,916 (6.8%)**; DB Schenker reroute **€107,684 (53%, low-confidence)**; 4,490 moved off DB Schenker, 4,191 stay freight. Routing report (+ split), DB Schenker validation, decision report, carrier overview all rebuilt + committed. bi-analytics commits this thread: `fceacc6`, `6833671`, `052d3c4` (Niklavs' Hermes), `a96e449` (girth 3.2.0).

## Next concrete step (Niklavs-gated, optional)
1. **Management deck** (`management_briefing/`, untracked) — refresh to the firm **€201,916** + the confidence split, when ready to present. No longer blocked on anything.
2. **Hermes test suite is red** — 21 fixtures assert pre-2.2.0 fuel (0% Jan/Feb); the `hermes-2.2.0` flat-7% engine is correct, the assertions are stale. Niklavs' change (`052d3c4`) — his to update/commit (offered; he committed 2.2.0 without the fixture pass).

## Files / paths to read first (bi-analytics, NOT brain)
1. `2_analysis/carriers/maersk/constants.py` (the 3.2.0 L+2W+2H girth block) + `calculate.py` `_decide_eligibility`.
2. `2_analysis/routing_2026q1/routing_report.html` §00 (the savings split, €107,684 / 53%).
3. `2_analysis/routing_2026q1/build_final.py` (`saving_split` block).
4. This session's quest-log: `quest-log/in-progress/S189_e3de8457_maersk-hermes-oversize-corrections.md` (see the continuation Update section).

## No pending external actions
The Maersk girth clarification — sent + answered (L+2W+2H). Nothing else awaiting an external party.
