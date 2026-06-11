---
quest: S196_eu-tender-result-investigation
sid8: 87f50e88
ts: 2026-06-11 14:15
open_dep: q09 baseline-bridge session running in parallel (its landing changes the report basis); bi-analytics q05-q08 + README edits uncommitted there (commit ask pending); Q01b threshold decision open
---

# Resume — EU tender result investigation (final-report Q&A, after round 2)

## Status
in-progress (multi-session: review by question rounds; round 2 paused with q09 in flight)

## Where we are
- Rounds 1+2 done: **Q01–Q08 closed or answered** (conclusions/findings in bi-analytics
  `2_analysis/result_investigation/`, README = index). Round 2 added:
  Q07 no-Hermes structure CONFIRMED (only new thing = Maersk beyond FR; precisions: DHL CH/AU
  new-lane trust, residual consolidation, DBS book stays) + Maersk new volume per country
  (44,913 Q1 / ~190k yr, €224k/yr; IT 87.6% / ES 94.1% of country volume → concentration note);
  Q08 DHL→DPD = one DE Poster40 knife-edge cell, −€568 vs Q1 actuals but genuinely cheaper on
  DPD forward — DHL rate increase €3.13→€3.32 (+6.1%) late Feb verified in q08c.
- Q08 spawned the **structural finding**: savings yardstick (Q1 actuals) ≠ decision basis
  (March-anchored forward) → forward-correct moves report as losses; savings vs DHL understated;
  dhl→dhl stays book a phantom negative (ups→ups analog).
- **q09 baseline-bridge HANDED OFF to a parallel session** (prompt in chat, q09_* namespace
  reserved): three-number bridge (Q1 actuals → do-nothing @2026 rates → plan), per-flow savings
  on (2)−(3), S200 final_stats ordering-drift fix, thin-cell-fallback bias quantification
  (3,049 fallback cells, pro-incumbent ~4% on DHL), book-wide rate-increase scan all carriers.
- bi-analytics: 98cdd49 committed (through Q04d); q05–q08 + README rows UNCOMMITTED there.

## Next concrete step
When the principal resumes: (1) check q09 session landed + reconcile (new headline basis);
(2) ask commit-go for bi-analytics q05–q08 + README; (3) remaining review items: the three
stays (UPS→UPS −€108.7k — redo post-q09, the phantom-negative point), residual→DPD (−€58.5k
row), DBS→Hermes as own question, tier split, fuel band, do-nothing scenario (easier post-q09:
becomes a first-class report number); (4) Q01b minimum-saving threshold decision (q08
interaction noted: under the bridge that cell becomes a small genuine win).

## Files / paths to read first
- bi-analytics `2_analysis/result_investigation/README.md` (index Q01–Q08, q09 pending)
- `q08_dhl_paket_to_dpd_pl_findings.md` (§Q08b/c — the yardstick finding driving q09)
- `q09_baseline_bridge_findings.md` (if the parallel session landed it)
- `q07_maersk_new_volume_by_country_findings.md` (concentration-risk note awaiting conclusion)
- quest-log `S196_5733cb1d_eu-tender-result-investigation.md` (T1–T34 narrative)
