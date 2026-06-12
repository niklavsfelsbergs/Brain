# EU tender no-Hermes v2 — why the flow split ≠ the headline (and why we left it)

> Source: [[S222_3309c3da_eu-tender-no-hermes-v2-headline-reconciliation|S222]] (`3309c3da`, 2026-06-12), Q&A over `final_report_no_hermes_v2/report_no_hermes_v2.py`. Cross-link: [[eu-tender]]. Sibling: [[S217_*_eu-tender-final-report-savings-decomposition]] (the with-Hermes version of the same split).

## The finding

The "How the saving is earned" split table sums **above** the headline:

| | € / yr |
|---|---|
| Reprice (kept carriers, better rates) | 412,052 |
| Reroute (volume moved to a cheaper carrier) | 652,472 |
| **Split-table sum (`flow_total`)** | **1,064,523** |
| − Drop Direct Link ("residual") volume | −47,305 |
| − Q4 peak differential | −41,194 |
| **= Headline (`base_ann`)** | **976,024** |

Gap = €88,500, and it is **by design** — `flow_total + resid_sv + peak_diff == headline` (code comment `report_no_hermes_v2.py:178-190`).

## Why the two netting items exist

- **Direct Link exit (−€47,305).** The split is over the **five carriers we keep**; it excludes `residual` (Direct Link, the carrier we're dropping). But Direct Link's flows have *negative* saving — its volume re-homes onto UPS/DPD/Maersk at a net cost (residual→UPS −€34k, →DPD −€14k…). The headline carries that cost; the split drops it, so the split reads €47k too high.
- **Q4 peak differential (−€41,194).** The per-flow figures are **peak-free by construction**: each flow's saving is `keep_ref − rcost` from the **Q1 cost matrix**, scaled to annual volume — and Q1 (Jan–Mar) is low season, zero peak on both sides. The annual model then adds the peak as a separate portfolio-level overlay: `today_peak` €241,274 (do-nothing Q4 bill) vs `routed_peak` €282,468 (plan Q4 bill) → −€41,194. The plan's peak is *higher* because do-nothing leaves big volume on zero-peak carriers (Direct Link €0, DB Schenker €0, DPD-PL none) while the plan concentrates volume onto carriers that carry Oct–Dec surcharges (DHL €0.19/parcel + Nov24–Dec7 peak-in-peak, Maersk €0.25 peer-anchored, UPS €0.27). Source schedule: `annual_2026/annual_report.py:144-151`.

## Why peak is *separate* from the flow split (not folded in)

1. The flow rows live in **peak-free Q1 space** — there is no peak in them to attribute.
2. Peak is computed **once at the whole-book level** (per-carrier peak premium × annual peak-window parcels, both sides). It does not decompose cleanly onto individual from→to rows, so the annual waterfall carries it as its own reconciling step: Q1 anchor → ×volume scale → ± peak differential → annual point.

## Decision (2026-06-12, principal)

**Not worth folding the €88.5k netting into the split-table total.** Doing so would push a portfolio-level peak overlay + the dropped-carrier cost down onto per-flow rows where neither belongs cleanly. Instead: added a **one-line reconciliation** under the split table in `report_no_hermes_v2.py` ("Reconciles to the €976,024 headline: €1,064,523 gross, less €47,305 to exit Direct Link… and €41,194 for the Q4 peak differential…"). The split stays an honest peak-free Q1 decomposition; the headline stays the annual number; the bridge is now visible on the page. Logged for the future so the question doesn't get re-litigated.
