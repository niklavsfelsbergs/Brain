---
quest: S210_a17168ec_decision-report-regen
sid8: a17168ec
ts: 2026-06-11 (S210)
open_dep: none — decision_report landed (bi-analytics 5fb7289); one deferred flag below
---

# decision_report regen — DONE + COMMITTED (bi-analytics 5fb7289)

The lone straggler from the S208 UPS cascade. `2_analysis/decision_report/decision_report.html`
predated the cascade (Jun 10 17:10) while routing/annual/final/carrier_overview were rebuilt.
Inputs were already fresh (cost_matrix_2026q1 + scenarios_2026q1 scorer + `_decision_sets_2026q1`
with `ups` in RENEWABLES, all Jun 11 19:2x); only the HTML was never re-rendered.

## What landed (commit 5fb7289, pathspec decision_report/ only; NOT pushed)

- **Re-render** of `report_2026q1.py` picks up ups-as-renewable. Firm lead is now
  `all_renewals_plus_maersk_eu_new_hermes` = **€174,633 (5.91%)**, down from €306k —
  `renew_ups` is **−€50,908 wholesale** (offer prices above today's GRI-free invoice
  all-or-nothing), so including ups in all_renewals is honestly lower. **Six-to-sign
  unchanged: DHL Paket · Maersk · Hermes · DPD-PL · UPS · DB Schenker** (UPS badge = NEW OFFER).
- Routing canon flows into the headline callout: today 2,955,020 → do-nothing 3,055,317 →
  routed 2,660,120 = **€395,197 Q1 (12.93%)**. do_nothing sanity = 0.
- **Source edits** to `report_2026q1.py`: UPS narrative rewritten ("INCUMBENT-only, no offer"
  → sign the offer; contract being replaced so "keep today" off the table; wins per-cell not
  per-book; CH operative-tier base = negotiate, Nordics oversize/LPS = dispute, pre-signature
  levers). Pending-table UPS row updated likewise. Engine stamps maersk-3.0.0→**3.2.0**,
  hermes-2.0.0→**2.2.0** (ups-2.0.1 / dhl_paket-2.2.0 / dpd_pl_current-1.0.0 already current).
- **Verify PASS**: no brace/None leak ({text}/{x} are Plotly hovertemplate tokens, not leaks);
  canon present + matching scorer; engine versions match the matrix; UPS card = NEW OFFER +
  diagnostic table has a ups engine row.

## Deferred (principal call S210): bank digest re-stamp → next alching

`gielinor/players/jebrim/bank/domains/eu-tender.md` line 49 headline is **stale** (S194-era):
shows **Q1 €201,916 (6.8%) / annual €997,720/yr**, "all 4 reports current," base €420,218 +
oversize-module €577,502 split. **Re-stamp target (cascade canon):** Q1 **€395,197 (12.93%)** /
annual **€1,908,707 (12.66%)** band €1,882,470–€1,934,944; firm **€990,225** / DBS-contingent
**€918,482**; rate moves €483,133; **5 reports current**; engines now incl. **ups-2.0.1 +
dpd_pl_current-1.0.0**. It's a *reframe*, not a number swap (base+module split → firm+contingent).
Principal chose **defer to alching** (S210) rather than spot-edit. Ground the re-stamp in
`routing_2026q1/routing_stats.json` + the S208 `final_report/` frame.

## Pre-existing, NOT touched (flagged for a separate pass)

The decision_report's **"Held ceiling (leans on Güll)" KPI + the "raw top puts Güll in NEW_OFFER"
summary bullet** are mislabeled — the committed Jun-10 HTML *already* pointed them at a non-Güll
set (`all_renewals_plus_maersk_eu_new_dhl_express`, €306k), so it's a pre-existing label drift,
not caused by this regen. Out of scope for the UPS+canon task; worth a fix when the ceiling KPI
semantics get a pass (the hardcoded "leans on Güll" label no longer matches the top ≤6 set,
which is now firm `keepfr_maersk_eu_plus_hermes` €222,228).
