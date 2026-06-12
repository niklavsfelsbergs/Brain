---
quest: S221_eu-tender-report-review-qa
sid8: eec4ee99
ts: 2026-06-12 02:45
open_dep: bi-analytics report_no_hermes_v2.py + deck_no_hermes_v2.py (+ regenerated HTML) uncommitted — awaiting principal eyeball + commit go (separate repo, never push)
---

# Resume — EU tender no-Hermes v2: report review + deck + standalone reframe

**Status:** in-progress (all edits built + verified; blocked on principal review/commit in bi-analytics).

**Where we are:** Worked the no-Hermes v2 report through a review session — answered what "carrier-level rates" means (DPD-PL export-only contract, PL-domestic not priced), relabeled that DPD row "Poland — not in contract", restored the §03 carrier-to-carrier flow matrix, reframed the whole report as a standalone management "Carrier Recommendation" (stripped the Hermes module framing + the DB-Schenker oversize-reroute upside; numbers unchanged at €976,024 base), built a clean slide deck `deck_no_hermes_v2.py` (report-scale type, 14 slides), lightened the low-contrast palette (MUT 0.42→0.62, DIM 0.26→0.44) in both, and removed the "Open upside" callout. All in `2_analysis/final_report_no_hermes_v2/`.

**Next concrete step:** Niklavs eyeballs `report_no_hermes_v2.html` + `deck_no_hermes_v2.html` in browser. On his go: bi-analytics commit (pathspec `2_analysis/final_report_no_hermes_v2/`); never push. Then two open decisions: (1) **propagate** the standalone reframe + contrast fix + DPD label to the sibling reports (`final_report.py` main, `report_no_hermes.py` v1, their decks) or keep v2 as the canonical management set? (2) the **DPD-PL domestic rate-card gap** — extract/get the PL-domestic rate so that lane prices properly, or leave the 1% carrier-level tail?

**Files / paths to read first:**
- bi-analytics `2_analysis/final_report_no_hermes_v2/{report_no_hermes_v2.py, deck_no_hermes_v2.py}` (the two built artifacts)
- `quest-log/in-progress/S221_eec4ee99_eu-tender-report-review-qa.md` (the Q&A + action log)
- `carriers/dpd_pl_current/constants.py` (the 29-country export served-set — why PL-domestic is "not in contract")
- bank/domains/eu-tender.md (domain digest)
