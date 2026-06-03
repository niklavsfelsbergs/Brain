---
quest: S148_eu-tender (FedEx Round-2 rebuild continuation)
sid8: e59202cf
ts: 2026-06-03 13:00
open_dep: FedEx fedex-2.0.0 BUILT + matrix re-run, UNCOMMITTED — principal-gated commit + 2 decisions to surface
---

# Resume — EU Tender FedEx Round-2 rebuild → fedex-2.0.0 (S148 cont., session e59202cf)

**Status:** in-progress · 2026-06-03 · **FedEx rebuild DONE end-to-end, UNCOMMITTED.** Adopted 104c786b's clean-CLOSING resume.
**Parent quest:** `quest-log/in-progress/S148_104c786b_eu-tender-dhl-paket-round2.md` (FedEx continuation appended).

## Where we are
`fedex-1.0.0 → fedex-2.0.0` built on the Round-2 reply. All blockers closed; full-year matrix + decision_scorer + bias + cross_carrier + report regenerated; doc cascade landed. **Everything UNCOMMITTED, principal-gated.**

## Engine deltas (fedex-2.0.0)
- **Vol-weight div 5000 all services** — `billable = max(gross, lwh/5000)`; freight bills on chargeable; parcel/freight boundary on chargeable (light-bulky → freight, closes a `no_rate_found` overflow).
- **Two-index fuel, base+surcharges/VAS scope** — Regional 20.5% (RE/REF) / Intl 34.5% (IE/IEF), Q1 averages, FLAT (sibling-consistent; monthly/forward-fuel parked in annualisation).
- **FX 4.30 → 4.234** (billed PLN → ECB Q1 avg), re-migrated.
- **Remote-area (ODA)** — `RemoteArea` VAS, Tier A/B/C by zipcode (D1's `oda_tiers.parquet`, 67.5k rows). GB + city-only = near-zero gap.
- **Customs CH = €0** (DAP bundled, pulled by P1) — `Customs` surcharge kept at 0 (one-line DDP flip). Scoped CH.
- 29/29 fixtures pass.

## Numbers
FedEx FY2025 **€34.47M** at 99.6% coverage (base €19.77M + fuel €5.99M [~17%] + remote €1.19M + customs €0). decision_scorer `add_fedex` −€1.63M; do_nothing €0.00 PASS. v1 0%-fuel under-pricing (€4.89M Q1 headline) closed.

## Two decisions to surface to principal (at close)
1. **Customs lane scope** — priced CH only (€0 on DAP anyway). NO/GB/LI/IS held (a guessed fee on high-volume GB would swing the headline). Confirm CH-only or extend.
2. **Fuel basis** — Q1-average flat used (sibling-consistent). Monthly schedule + full-year forward-fuel parked in annualisation. Confirm flat-Q1 is the intended basis for the full-year run.

## Still open (non-blocking)
- Jan/Feb Intl fuel RECONSTRUCTED (validated vs pulled March + June anchor) — upgrade to PULLED via Wayback if wanted.
- GB ODA outward-code matcher deferred (remote-island volume tiny).
- Minor doc-sync: PLAN.md §B.26 line 184 still reads "fedex-1.0.0 Live ... HEAVILY provisional" — flip to 2.0.0 next pass (DECISIONS/REVIEW_CONCLUSIONS/OPEN_QUESTIONS/engine-docs already synced).

## Commit plan (when principal says go) — pathspec-only (S131 #1 hazard; shared dirty tree)
- **bi-analytics-main** (separate repo, on main @ 750e00d, UNCOMMITTED):
  `git commit -- "NFE/projects/2_EU_tender_2026/2_analysis/carriers/fedex" "NFE/projects/2_EU_tender_2026/2_analysis/data/cost_matrix" "NFE/projects/2_EU_tender_2026/2_analysis/data/scenarios.parquet" "NFE/projects/2_EU_tender_2026/2_analysis/cross_carrier_view.html" "NFE/projects/2_EU_tender_2026/2_analysis/decision_report/decision_report.html" "NFE/projects/2_EU_tender_2026/2_analysis/decision_report/report.py" "NFE/projects/2_EU_tender_2026/2_analysis/docs" "NFE/projects/2_EU_tender_2026/carrier_responses_to_open_questions/fedex/REVIEW_CONCLUSIONS.md"`
  (data parquets may be gitignored — verify; the engine code + HTML + docs are the tracked surface. New untracked: customs.py, remote_area.py, build_oda_tiers.py, oda_tiers.parquet.)
- **brain** (this repo): `git commit -- gielinor/players/jebrim/quest-log/in-progress/S148_104c786b_*.md gielinor/players/jebrim/quest-log/in-progress/S148_d1_*.md gielinor/players/jebrim/quest-log/in-progress/S148_p1_*.md gielinor/players/jebrim/research/2026-06-03-fedex-q1-2026-fuel-history.md gielinor/players/jebrim/inventory/eu-tender-fedex-round2-resume__e59202cf.md gielinor/comms/active.md .claude/intent/jebrim-e59202cf.txt`

## Files to read first (next session)
- `carrier_responses_to_open_questions/fedex/REVIEW_CONCLUSIONS.md` (Round-2 block).
- `2_analysis/carriers/fedex/` engine + `docs/technical/engines/fedex.md`.
- This resume + `research/2026-06-03-fedex-q1-2026-fuel-history.md` (P1).
