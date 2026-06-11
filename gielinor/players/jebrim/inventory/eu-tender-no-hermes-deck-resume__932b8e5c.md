---
quest: S218_eu-tender-no-hermes-deck
sid8: 932b8e5c
ts: 2026-06-11 00:12
open_dep: bi-analytics commit-gated — awaiting Niklavs review of the rendered deck + commit go
---

# EU-tender no-Hermes management deck — built; awaiting principal review/commit

## Where we are

Built `final_report_no_hermes/deck_no_hermes.py` → `deck_no_hermes.html` (bi-analytics, separate
repo, **uncommitted**): 13-slide self-contained HTML management deck of the no-Hermes final report,
generated from `stats_no_hermes.json` (no hand-typed numbers). Headline €976,024/yr committed +
€696,082/yr gated optional upside — both tie vs the json. Opened in the browser; data + structure
verified, **visual not eyeballed by me**.

## Next concrete step

Principal-side: review the rendered deck and decide (1) commit the bi-analytics files? — pathspec-scoped
to `final_report_no_hermes/deck_no_hermes.{py,html}` (+ the `final_report/_superseded/` move if keeping
it tidy); always-ask, separate repo from the brain close commit; never push. (2) Want the with-Hermes
companion deck too? — the main-report version I built first sits in `final_report/_superseded/`; can be
restored + re-pointed, or rebuilt clean from `final_report/final_stats.json`.

## Files / paths to read first

1. this file
2. `bi-analytics-main/NFE/projects/2_EU_tender_2026/2_analysis/final_report_no_hermes/deck_no_hermes.py`
3. `final_report_no_hermes/report_no_hermes.py` + `stats_no_hermes.json` (the source story + numbers)
4. quest-log `S218_932b8e5c_eu-tender-no-hermes-deck.md`
5. sibling resume `inventory/eu-tender-no-hermes-report-resume__177f00f1.md` (the S212 report it presents)
