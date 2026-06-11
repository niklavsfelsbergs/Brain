# S201 — EU tender final report: service-mix-per-carrier section

- **sid8:** 475fd1ab
- **Date:** 2026-06-11
- **Actor:** Jebrim (principal)
- **Status:** in-progress

## Turn log

**T1 — ask.** Niklavs: final report is missing the split of services used per carrier; suggests "a small overview of service volume per carrier", asks how to incorporate.

**T2 — grounding + recommendation.** Read keepsake, `eu-tender-final-report-resume__907d4e63`, the final_report/ pipeline, and the routing data. `routing_assignment.parquet` already carries (family, service) per shipment — 17 carrier-service rows, clean. Recommended: compact carrier × service table (annualized parcels/yr + share-of-carrier), computed in `build_final_stats.py`, tie-outs in `verify_report.py`. NULL-service rows labeled honestly as carrier-level rate models ([[S185_e9821cdf_eu-tender-report-signoff|S185]] lesson: model grain ≠ operation). Placement offered as multiple-choice; **Niklavs picked §02 under the carrier cards** (the recommended option).

**T3 — build.** Three files edited in bi-analytics `2_analysis/final_report/`:
- `build_final_stats.py` — `service_mix` block (group pp by rcarrier × service, annualized via the same per-country ratios); asserts per-carrier sums tie to `portfolio` parcels and total ties to annual parcels (both 0.0000); deltas added to `checks`.
- `final_report.py` — `SVC`/`SVC_NULL` label maps + service-mix table rendered in §02 between the cards and the "Not selected" callout, with a legend explaining carrier-level rows (UPS, Maersk-FR, DBS freight).
- `verify_report.py` — recomputes the mix tie-outs from the JSON + checks the table rendered (heading + largest row). Full chain re-run: **PASS**.

**T4 — drift catch (the real finding of the session).** The rebuilt headline differs from commit 98cdd49: base €420,218→€393,477, module €577,502→€581,215, total €997,720→**€974,692**. Cause verified, not an error: sibling [[S198_cbc40f78_fr-incumbent-rebase|S198]] (cbc40f78, FR incumbent rebase) re-ran the full cascade at 12:45 — its documented result is exactly −€23,028 to €974,692, verified, awaiting commit go. My rebuild absorbed that approved state; the final report and annual report now agree on the new base (cross-assert passed). Surfaced to Niklavs: the report he last saw said €997,720.

## Open

- Niklavs to eyeball the new §02 table in `final_report.html` (data layer verified; visuals not eyeballed by me).
- Sibling consumer: `annual_2026/annual_report.py` does NOT have the service-mix section — flag, not built unasked (fix-the-class watch-out noted, his call).
- Commit go pending in bi-analytics (pathspec `final_report/`), bundled with [[S198_cbc40f78_fr-incumbent-rebase|S198]]'s cascade artifacts per its resume. Never push.

## Close (T5, wrap cue)

No pending external actions — the bi-analytics commit is principal-gated, not a dangling agent action.
Cascade: none owed by this session — the report addition generates from live artifacts; the stale eu-tender digest headline (€997,720 → €974,692) was already flagged by [[S198_cbc40f78_fr-incumbent-rebase|S198]]'s resume for the next alch.
Main-brain changes: this quest-log, `inventory/final-report-service-mix-resume__475fd1ab.md`, one examine draft (rebuild-vs-committed-baseline), comms OPEN/UPDATE/CLOSING, intent sidecars.
