# S222 — EU tender no-Hermes v2: headline-vs-flow-split reconciliation Q&A

**Session:** `3309c3da` · 2026-06-12 · Jebrim · continuation of [[S221_eec4ee99_eu-tender-report-review-qa|S221]] (`eec4ee99`) no-Hermes v2 review thread.

## What was asked

Niklavs, reviewing `final_report_no_hermes_v2`, flagged that the "How the saving is earned" split table (reprice €412,052 + reroute €652,472 = €1,064,523) does **not** match the €976,024 headline saving. Then asked what the Q4 peak differential is and why it's separate.

## What was done

1. **Traced the gap.** Reconciled split-table sum → headline from `stats_no_hermes.json`: `flow_total €1,064,523 − Direct Link residual €47,305 − Q4 peak differential €41,194 = €976,024`. Gap €88,500 is **by design** (`report_no_hermes_v2.py:178-190`, `flow_total + resid_sv + peak_diff == headline`).
2. **Explained the two netting items.** Direct Link exit (dropped carrier's volume re-homes at a net cost, excluded from the kept-carrier split) + Q4 peak differential (per-flow figures are peak-free Q1 repricing scaled to volume; peak is a portfolio-level annual overlay — `today_peak €241,274` vs `routed_peak €282,468`, plan concentrates volume onto Oct–Dec-surcharge carriers).
3. **Added a one-line on-page bridge** under the §03 split table in `report_no_hermes_v2.py`; regenerated `report_no_hermes_v2.html` (25KB). Verified the line renders with live values.
4. **Decision (principal):** not worth folding the netting into the split total — the one-line reconciliation is enough. Logged the full finding to a bank draft so it isn't re-litigated.

## Decisions

- **Keep the split table peak-free + over kept carriers only; reconcile to the headline with a one-line bridge, not by folding the netting into the per-flow total.** Peak doesn't decompose cleanly onto from→to rows; the dropped-carrier cost doesn't belong in a kept-carrier split.

## Pending external actions

None pending. (bi-analytics edit is uncommitted but that's a principal-gated commit, not a dangling action — see resume.)

## Harvest

- 1 bank draft: `bank/drafts/notes/projects/2026-06-12-eu-tender-no-hermes-v2-headline-vs-flow-split-reconciliation.md`.
