---
quest: S212_eu-tender-no-hermes-report
sid8: 177f00f1
ts: 2026-06-11 23:55
open_dep: principal decisions — (1) mirror AU relabel + service-mix format into main report? (2) commit bi-analytics report files? (3) UPS AU special-offer check
---

# eu-tender no-Hermes report — built; awaiting principal calls

## Where we are

Built `2_analysis/final_report_no_hermes/` in bi-analytics: `build_stats_no_hermes.py` + `report_no_hermes.py` → `stats_no_hermes.json` + `report_no_hermes.html`. Headline €976,024/yr (conservative basis, DBS pinned to freight), reconciles to `annual_stats.structure.base_ann` (Δ €0.00). Main report `final_report/final_report.py` also got a service-mix table reformat (carrier total + % share). All **uncommitted in bi-analytics** (separate repo; principal hasn't green-lit the commit).

## Next concrete step

Three open principal decisions (all asked, none answered before wrap):
1. **Mirror to main report?** The AU service-row relabel ("Australia — current UPS contract (not in 2026 offer)") and the service-mix carrier-total format both currently live only in the no-Hermes report / partial in main. The main `final_report.py` still has the stale "All UPS volume — carrier-level rates" label. Mirror both, or keep divergent?
2. **Commit the bi-analytics changes?** Pathspec-scoped: `final_report_no_hermes/` (4 files) + the `final_report/final_report.py` service-mix edit. Principal must green-light (always-ask; separate repo from the brain close commit).
3. **UPS AU special offer** — Niklavs is checking whether UPS has an AU/WWE special offer that would re-price the Australia tail under the new contract (would change the AU row from kept-current to engine-priced, and resolve the +€211k forced-reassignment exposure). Connects to live sibling S211.

## Files / paths to read first

1. this file
2. `bi-analytics-main/NFE/projects/2_EU_tender_2026/2_analysis/final_report_no_hermes/build_stats_no_hermes.py` (the headline basis + pinning + the reroute-caveat math)
3. `report_no_hermes.py` (the rendered story; SVC_NULL["ups"] = the AU label)
4. quest-log `S212_177f00f1_eu-tender-no-hermes-report.md` (full turn log + findings)
5. sibling `inventory/.../S211` UPS-savings session for the WWE thread
