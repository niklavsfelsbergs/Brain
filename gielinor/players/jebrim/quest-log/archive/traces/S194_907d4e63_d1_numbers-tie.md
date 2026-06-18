# [[S194_907d4e63_eu-tender-holdup-pass-and-project-rating|S194]] D1 — EU Tender 2026 numbers-tie verification (dwarf)

Player: Jebrim. Repo: bi-analytics-main @ a96e4493 (read-only). Task: verify 7 claims tie across artifacts.

## Turn log

- T1: Confirmed HEAD = a96e4493b394937093952f8bba382097a0f70b1d. Located stats JSONs: routing_2026q1/routing_stats.json, annual_2026/annual_stats.json, switch_list_2026q1/switch_stats.json.
- T2: routing_stats.json — saving 201,915.88 (6.833%) → Check 2 PASS. db_schenker origin saving 107,683.63 (53.33% of total); db_schenker_to: hermes 4,463 / maersk 27 / dhl_paket 218 / dpd_pl 104 / ups 1 / self 4,138 → Check 4 numbers present; note 4,490 = Hermes+Maersk only, total moved off DBS = 4,813.
- T3: annual_stats.json — total_point 997,719.68 (6.84%), band 969,286.77–1,026,152.59, contingent_db_schenker 525,360.05 (52.66% of point, not 54% — check report wording). anchor_q1.saving = 201,915.88445547363 — identical to routing_stats.saving (delta €0) → q1_base reconciles.
- T4: Version stamps. Engine source: carriers/maersk/constants.py:8 = maersk-3.2.0, carriers/hermes/constants.py:8 = hermes-2.2.0. All three cost_matrix_2026q1 parquets (01/02/03) stamp maersk-3.2.0 + hermes-2.2.0 on every row (193,533/carrier in 01). Data layer CURRENT.
- T5: Stale prose stamps found. carrier_overview_v2/carrier_overview.html: auto-synced ledger lines say hermes-2.2.0 (l.231) and maersk-3.2.0 (l.302), but hand-written prose says hermes-2.0.0 (cost-structure intro + confidence footer "Hermes at hermes-2.0.0", l.224/545) and maersk-3.0.0 ("TWO Maersks" warning l.234 + cost-structure intro l.279). decision_report/decision_report.html: "Engine carrier-confirmed (maersk-3.0.0)" l.234 and "(hermes-2.0.0)" l.239 — stale labels, though its numbers are current. carrier_overview v1 + carriers/maersk/migration_plan.html (maersk-2.0.1) are explicitly SUPERSEDED (v1 PLAN.md banner, 2026-06-05) — historical, OK.
- T6: Decision report (HEAD a96e449): leading ≤6 candidate EUR 306,402 (10.4%) = selection ceiling; executed saving EUR 201,916 (6.8%); gap explained in "Headline: why this differs from the routing report" callout — floor 2,634,893 / committed 2,753,104 / op gap 118,211, all matching routing_stats.json exactly. Regenerated on current artifacts.
- T7: Routing report headline €201,916 / 6.8%, DBS reroute €107,684 / 53% low-confidence, Hermes 4,463 / stays 4,138 — current. Annual report: €997,720 point, band €0.97M–€1.03M, "DB Schenker reroute — low confidence €525,360, 54% of total" + gated callout. Note: 54% is vs the pre-peak-differential split (525,360/976,976=53.8%); tierbar widths show 52.7% vs 997,720 — minor internal wobble, both present in report.
- T8: Parcel conservation: population_2026q1.parquet = routing_assignment.parquet = annual q1_base.parquet = 531,194 rows = routing_stats n_parcels. PASS.
- T9: Stale-number sweep (whole project dir): €377,471/€377k/12.77% quoted as CURRENT in 2_analysis/management_briefing/eu_tender_2026_briefing.html (sourced to "routing_stats.json" which now says 201,916) — STALE artifact; it is UNTRACKED in git (?? status), as is annual_2026/ (the annual report is working-tree only, not in HEAD). No artifact anywhere quotes 276,951 or 275,484.
- T10: Exec brief (carrier_overview_v2/exec_brief.html) is full-year-2025 segment view (2,875,235 shipments), quotes no Q1 saving — no conflict. switch_stats total_save 367,518 is the unconstrained per-parcel switch-list lens, distinct number, not quoted as the routing headline anywhere I found.

## Verdicts (summary)
1. Engine versions: PASS on data (constants + all cost matrices 3.2.0/2.2.0), FAIL on prose — stale hermes-2.0.0/maersk-3.0.0 labels in carrier_overview_v2 (4 spots) and decision_report (2 spots).
2. Q1 routing €201,916/6.8%: PASS (routing_stats.json saving=201,915.88, pct=6.833).
3. Annual €997,720/6.84%, band 969,287–1,026,153, DBS slice 525,360 low-confidence: PASS; q1 anchor identical to routing saving (€0 delta). "54%" appears verbatim in report (note: 52.7% vs final point).
4. DBS reroute €107,684 (53.3%), Hermes 4,463 + Maersk 27 = 4,490: PASS — caveat: total moved off DBS is 4,813 (incl. DHL 218, DPD 104, UPS 1); 4,490 counts the Maersk/Hermes destinations only.
5. Decision report + carrier overview regenerated: PASS on numbers (both at HEAD a96e449, decision headline 306,402 ceiling vs 201,916 executed, gap explained); prose version stamps stale (see 1).
6. Parcel conservation 531,194 everywhere: PASS.
7. Cross-report consistency: PASS with one stale artifact — management_briefing (untracked) still presents €377,471/12.77% as current. Nothing quotes 276,951/275,484.

Status: dwarf task complete; reported to principal [[S194_907d4e63_eu-tender-holdup-pass-and-project-rating|S194]].
