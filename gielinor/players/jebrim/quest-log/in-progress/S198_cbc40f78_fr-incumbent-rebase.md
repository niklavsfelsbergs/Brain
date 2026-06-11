# S198 — FR incumbent rebase in routing + cascade re-run

- **Session:** cbc40f78 · 2026-06-11 · Jebrim
- **Parent thread:** EU tender result investigation (S196_5733cb1d, q04 chain). Handoff via principal prompt; context committed at bi-analytics 98cdd49 (q04c + q04d findings).

## The ask

Principal-approved 2026-06-11. Three changes in `routing_2026q1/build_final.py` incumbent/keep derivation:

1. Relabel `cur_inc` for DPD-PL-origin FR parcels → `maersk` (completed switch — DPD-FR stopped after January, cohort absorbed by Maersk, q04c).
2. `keep_cost` from MARCH (latest-month) parcels' `today_eur_fwd` instead of full-Q1 average; fall back to full-Q1 where March volume thin (pick + document threshold, e.g. <10 parcels). Fixes UPS-inflated FR light bands; no-op for month-stable cells.
3. Baseline `today_total` stays full-Q1 actuals — only forward keep representation + origin labels change.

Do NOT touch rate engines or declined-DPD-offer handling. Re-run cascade (build_final → build_annual → build_final_stats → reports); cross-asserts + verify must PASS.

Deliverables: (a) FR cell-winner before/after diff (cells flipped, parcels + €/yr); (b) corrected flows table (DPD-FR origin → maersk); (c) headline delta vs committed €997,720/yr; (d) `result_investigation/q04f_fr_rebase_findings.md` + README row.

Watch-outs: q04e label churn = sibling b93204b5's lane (note interaction in q04f only, no normalizing); per-origin keep option OUT of scope; commit only on principal go, pathspec-scoped, never push.

No pending external actions. (All writes were local: bi-analytics working tree — uncommitted, principal-gated — and brain files committed at close.)

## Turn log

- T1 (respawn): loaded keepsake/domains/eu-tender digest + q04 comms trail. Siblings: 5733cb1d (result_investigation owner), b93204b5 (q04e). OPEN posted. Next: read q04c/q04d findings + build_final.py.
- T1 cont. (the build fix, all in one turn):
  - Implemented the 3 changes in `build_final.py` AND its exact replica `annual_2026/q1_base.py` (in lockstep — the reconcile assert is the drift lock). Threshold picked: `LATEST_MIN_N = 10` March parcels, else full-Q1 fallback (763 cells March-anchored / 3,049 fallback).
  - **Existence proof did NOT reproduce**: FR × Poster 40cm @0kg March blend €4.587 (cell genuinely still 12.6% UPS in March) vs DPD bid €4.517 → stays DPD. q04c's €4.09 was the Maersk-ONLY Q1 mean, not the approved March blend. Flagged in q04f + to Niklavs; spec implemented to the letter, no fudging.
  - Cross-assert caught a **latent nondeterministic tie-break** (NL GEL VERSANDTASCHE klein @8kg, 1-vs-1 dom tie → 2-parcel mismatch between the replicas). Fixed: stable secondary sort keys (carrier asc) on dom + both cost sorts, both files. Pre-existing bug, cost-identical fix.
  - Cascade re-run end-to-end: build_final → q1_base (RECONCILE OK exact) → build_annual (bridge ties) → build_final_stats (asserts <€1) → 3 report HTMLs → verify_report **PASS** (UPS-leaving 61.6% within the ~62% prose band).
  - Headline: Q1 €201,916 → €194,191 (−7,725); **annual €997,720 → €974,692 (−€23,028)**; base €420,218→€393,477, module €577,502→€581,215. Old keeps were understated (Jan-DPD/Jan-UPS contamination).
  - FR: 19/421 cells flipped (4,082 Q1 parcels), FR delta −€14,176/yr. Flows: DPD-FR origin 3,205→0 (maersk). **Non-FR side effect: DE × Poster 40cm @0kg, 21,858 parcels DHL→DPD on a €0.04/parcel knife edge** — flagged for the Q01b switch-threshold decision, not changed.
  - Deliverables: `result_investigation/q04f_fr_rebase.py` + `q04f_fr_rebase_findings.md` + README row (sibling 5733cb1d's uncommitted README edits + their new Q06 row left untouched). All bi-analytics work UNCOMMITTED — awaiting principal review + commit go (pathspec-scoped; never push).
