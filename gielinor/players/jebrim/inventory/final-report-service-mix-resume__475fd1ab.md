---
quest: S201_final-report-service-mix
sid8: 475fd1ab
ts: 2026-06-11 14:35
open_dep: bi-analytics final_report/ regenerated + service-mix section uncommitted — awaiting principal eyeball + commit go (bundles S198's cascade artifacts; separate repo, never push)
---

# Resume — final report service-mix section

**Status:** in-progress (built + verified; blocked on principal review/commit in bi-analytics).

**Where we are:** §02 of the final report now carries the service-mix-per-carrier table (carrier × service, annualized parcels/yr + share-of-carrier, 17 rows). Computed in `build_final_stats.py` (`service_mix` block, asserts tie per-carrier sums to portfolio and total to annual parcels — both 0.0000), rendered in `final_report.py` (SVC/SVC_NULL label maps; NULL-service rows labeled "carrier-level rates"), verified in `verify_report.py`. Full chain PASS. The rebuild also absorbed S198's FR-rebase cascade: headline now base €393,477 + module €581,215 = €974,692 (was €997,720 at commit 98cdd49; matches S198's documented −€23,028).

**Next concrete step:** Niklavs eyeballs `final_report.html` in browser — the new §02 table AND §03 (headline moved since he last saw it). On his go: bi-analytics commit, pathspec `2_analysis/final_report/` bundled with S198's cascade artifacts (its resume names the full pathspec). Decide whether `annual_2026/annual_report.py` gets the same service-mix section (sibling consumer, not built unasked).

**Files / paths to read first:**
- bi-analytics `2_analysis/final_report/{build_final_stats.py, final_report.py, verify_report.py}` (the three edits)
- `quest-log/in-progress/S201_475fd1ab_final-report-service-mix.md` (turn log incl. the drift catch)
- `inventory/fr-incumbent-rebase-resume__cbc40f78.md` (the cascade this rebuild absorbed + its commit pathspec)
