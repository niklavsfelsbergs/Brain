# S203 — q09: report baseline bridge + switch threshold

> sid8: `021047a4` · 2026-06-11 · Jebrim · handoff target of 87f50e88's 13:55 comms UPDATE
> ("report baseline-bridge rework → prompt delivered in chat for a NEW session; q09_*
> namespace reserved"). SNNN: [[S202_276897ca_eu-tender-negotiation-levers|S202]] publicly claimed by 276897ca → took S203.

## The ask (Niklavs' handoff prompt, verbatim intent)

The report uses one baseline (Q1 invoiced actuals) for two jobs — measuring the plan and
justifying the routing. Fix: a three-number bridge — (1) Q1 paid €2.96M, (2) do-nothing at
2026 rates, (3) the plan — with (2)−(3) as THE saving and the only per-flow figure; rate
moves live once in the (1)→(2) step. Plus the Q01b minimum-saving switch threshold.
Explicitly NOT wanted: two saving columns per flow. The handoff also bundled the [[S200_104770bd_eu-tender-no-hermes-portfolio-check|S200]]
final_stats ordering-drift fix.

## Turn log

- T1: respawned (address `Hey Jebrim`), grounded in keepsake + eu-tender digest + the
  5733cb1d/475fd1ab resumes; comms tail revealed this is the q09 handoff session → flipped
  from assessment-mode to build-mode. Posted OPEN claiming final_report/ + routing chain +
  q09_* (87f50e88 LIVE, owns README + q01-q08 — steering clear).
- T1 (cont.): read build_final.py / q1_base.py / build_annual.py / build_final_stats.py /
  verify_report.py + all three renderers. Key finding: keep machinery (March-anchored
  `keep_cost`, `today_eur_fwd` GRI) existed for the OPTIMIZER but never fed REPORTING;
  annual_stats' "do_nothing" block was annualized actuals mislabeled.
- Build: per-parcel `keep_ref` through the whole chain; savings basis = keep_ref − rcost
  everywhere (tiers, structure, flows, by-dest); `do_nothing_total`/`rate_moves` in stats;
  bridge3 block; three renderers re-anchored. T=0 parity run matched committed chain to
  the cent before enabling the threshold.
- Threshold: q09 grid showed same-family flips dominate naive parking → cross-family-only
  semantics; pinned SWITCH_MIN_PCT=0.02 (parks 81 cells / 17.6k Q1 parcels, true cost
  €11.4k/yr incl. peak side-effect). Verify caught the hard-typed "~62% UPS migrates"
  prose going stale (→54%) → made computed (fix-the-class: also routing_report's UPS
  card + GRI bullet).
- [[S200_104770bd_eu-tender-no-hermes-portfolio-check|S200]] fix: verify_report now cross-asserts final_stats vs LIVE annual_stats (fails on
  stale); build_final_stats' structure assert made unconditional.
- Chain rebuilt end-to-end: verify PASS. Findings: `q09_baseline_bridge_findings.md`.

## Results (new canon, uncommitted in bi-analytics)

Q1: paid €2,955,020 → do-nothing €3,058,974 (+€103,954 rate moves) → plan €2,761,964 =
**€297,009 (9.7%)**. Annual: €15,096,445 → €13,631,996 = **€1,464,449/yr (9.70%)**, band
€1,437k–€1,491k, rate moves +€501,176/yr. Structure: base €862,401 + module €602,049.
ups→ups books €0; q08 cell +€9k/yr true; residual→DPD −€13.3k honest consolidation cost.

- T2 (Q&A): "firm 400k→800k?" — reconciled: +€469k is the base-side rate-move
  reclassification (974,692 + 501,176 − 11,419 = 1,464,449 ties exactly).
- T3 (Q&A): "DHL+UPS GRIs = 500k/yr?" — split per carrier → q09b_rate_moves_by_carrier.py
  + findings §Q09b: UPS €228k + DHL €205k = €433k verified; Maersk €36k is anchor drift,
  NOT a verified rate event (flagged); DBS/DPD ~€35k drift.
- T4 (Q&A): "where did the 68k come from?" — q09c_drift_decomposition.py + findings
  §Q09c. One mechanism (March keep anchor, std cells): Maersk €36k = 100% FR forward
  repricing of the completed switch (q04c by design); DBS €21k ≈ month-mix noise in two
  DE zV cells (flag as ±); DPD €14k small genuine drift in pure cells. DHL cross-checks
  as a uniform per-cell rate step, as a real event should.

- T5 (Q&A): "no letter, so where from?" — q09d_dbs_zv_march_jump.py: the DBS €21k is
  NOT mix-noise (corrected §Q09c): DBS like-for-like flat; the March cell mean was
  contaminated by 21+37 UPS parcels carrying S199-family oversize fees (mean €46-68,
  median ~€6) in the shared DE zV cells → cell-grain keep mean repriced DBS parcels
  ~€10/parcel. Fix option surfaced (per-incumbent keep_ref grain), not built unasked.

- T6 (Q&A): "was March itself pricier than Q1 for Maersk-FR/DBS/DPD?" —
  q09e_maersk_fr_like_for_like.py: Maersk-FR own March mean €4.85 vs €4.64–4.67 (~+4%,
  but heavier mix 0.76 vs 0.71 kg → partly mix, no rate event; composition from the
  departed Jan DPD €4.36 cohort stacks on top — §Q09c corrected AGAIN, my "100%
  completed-switch" framing was incomplete). DBS: no (flat, contamination only).
  DPD: yes, ~+0.9% in pure cells. Full conclusion delivered in chat per principal ask.

- T7 (BUILD, principal go via AskUserQuestion): per-incumbent keep grain (q09d fix).
  Discovery first: the contaminated DE zV cells SWITCHED to Hermes (3× margin) → the
  €21k sat in the module saving, not just the rate-moves line. Built keep_ref at
  (cell × incumbent) + kept-cell plan cost = dom's own mean; optimizer bid untouched
  (zero routing churn). New canon: saving €292,636 Q1 / €1,442,782 ann (9.57%), rate
  moves €100,297 Q1 / €483,133 ann; module reroute 517,123; base 874,433. q09b re-run:
  DBS 21.2k→2.5k, Maersk 36k→17.6k, UPS absorbs its own disputed fees (+21.5k→249k).
  Chain verify PASS. Records updated (findings table + §Q09b/c/d).

- T8: principal Q&A on the grain fix's symmetry (base +12k / module −34k both-ways blend
  bias) — reconciled in chat; session closed on his cue.

No pending external actions.

## Open / pending principal

1. Eyeball the three rebuilt HTMLs (headline basis changed everywhere).
2. Threshold value call: 2% (recommended) vs 1% vs 3% (grid in findings).
3. bi-analytics commit go — my pathspec: `2_analysis/routing_2026q1/{build_final.py,
   routing_report.py,routing_stats.json,routing_rules.csv,routing_assignment.parquet,
   routing_report.html,cell_candidates.parquet}`, `2_analysis/annual_2026/{q1_base.py,
   q1_base.parquet,build_annual.py,annual_stats.json,annual_report.py,annual_report.html}`,
   `2_analysis/final_report/*`, `2_analysis/result_investigation/q09_*`. NOTE: bundles the
   already-uncommitted S198-cascade + S201-service-mix artifacts in final_report/.
4. README q09 row — 87f50e88 owns README; suggested row posted in comms.
5. Stale-basis consumers: management deck, eu-tender digest headline (re-stamp at alch),
   carrier_overview prose where it cites routing savings.
