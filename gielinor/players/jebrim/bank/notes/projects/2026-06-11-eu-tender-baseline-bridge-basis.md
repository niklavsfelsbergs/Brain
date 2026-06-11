# EU tender — the q09 baseline bridge: savings basis since 2026-06-11

**As of:** 2026-06-11 ([[S203_021047a4_q09-baseline-bridge|S203]], sid8 021047a4; uncommitted in bi-analytics pending principal go).

Every routing/annual/final-report saving is now measured **against doing nothing at 2026
rates**, not against Q1 invoiced actuals. Three numbers, one meaning each:

1. **Paid** — Q1 invoiced actuals: €2,955,020 (finance-reconcilable; annualized €14.60M).
2. **Do-nothing** — same volume, same current carriers, 2026 forward rates: €3,055,317 Q1 /
   €15.08M ann. Per-parcel `keep_ref` = the parcel's **own incumbent's** March-anchored
   mean within its cell (q09d grain fix — a cell-wide blend let the S199 UPS dimensioner
   fees reprice DB Schenker cell-mates and inflate the module saving ~€21k/yr) or
   `today_eur_fwd` (variable). Kept cells' plan cost = the dominant incumbent's own mean;
   the OPTIMIZER's keep bid stays cell-grain (decisions locked). (2)−(1) = the carriers'
   rate moves (+€100,297 Q1 / +€483,133 ann: UPS €249k — incl. ~€21k of its own disputed
   fees — DHL €205k March step, Maersk €17.6k own-mix, DPD €13k, DBS €2.5k).
3. **Plan** — €2,762,682 Q1 / €13.64M ann.

**THE saving = (2)−(3): €292,636 Q1 / €1,442,782 ann (9.57%)**, band €1,416k–€1,470k.
Old basis (vs actuals) retained in stats as `saving_vs_today` only — never per flow. Flow
signs match the optimizer by construction: stays book €0 (the old ups→ups −€108.7k was the
GRI), dhl→dhl +€39k Q1 = staying on DHL *at tender terms*, residual→DPD −€13.3k = the real
cost of dropping Direct Link. Headlines citing **€974,692/yr are the old basis** (also
pre-threshold) — the digest/deck need re-stamping.

**Switch threshold (Q01b resolved):** `SWITCH_MIN_PCT = 0.02` in `build_final.py` +
`q1_base.py` (must stay lockstep), **cross-family only** (same-family engine wins are not
switches), ties to the incumbent. Parks 81 cells / 17.6k Q1 parcels; true cost €11.4k/yr
(incl. the peak side: parked UPS volume keeps its Q4 peak). 3% would also park the q08
DE-Poster40 cell (genuine 2.5% margin on the new basis). Grid:
`result_investigation/q09_switch_threshold_grid.py`; record:
`q09_baseline_bridge_findings.md`.

**Guard:** `verify_report.py` cross-asserts `final_stats.json` against the LIVE
`annual_stats.json` (the [[S200_104770bd_eu-tender-no-hermes-portfolio-check|S200]] ordering-drift can't pass verify anymore); migration prose
percentages are computed, not hand-typed.

Structure on the new basis: base €874,433 + oversize module €568,349 (reroute €517,123 +
Hermes other lanes €51,225). Related: [[2026-06-09-routing-cost-basis-decisions]],
[[2026-06-11-eu-tender-annualization-method]], [[2026-06-09-decision-vs-routing-savings-reconciliation]].
