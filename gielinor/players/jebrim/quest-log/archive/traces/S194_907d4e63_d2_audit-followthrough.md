# [[S194_907d4e63_eu-tender-holdup-pass-and-project-rating|S194]] D2 — Red-team audit follow-through check (dwarf)

Brief: verify which of the 2026-06-09 red-team "must fix before management" items (a)–(g) landed between 39c4595 and a96e449.
Repo: bi-analytics-main/NFE/projects/2_EU_tender_2026 (read-only).

## Turn log

- T1: git log 39c4595..a96e449 — 4 commits: fceacc6 (Maersk+Hermes oversize corrections), 6833671 (flow corrections into routing/decision/carrier-overview + DB Schenker split), 052d3c4 (hermes-2.2.0 flat-7% fuel + 3 reports rebuilt), a96e449 (Maersk girth L+2W+2H 3.2.0 re-run).
- T2: (c) decision_scorer.py:189 still `pl.coalesce(["assigned_cost_eur", "real_total_eur"])` — no min(bid, real) floor. decision_scorer_2026q1.py:154 same shape (`coalesce(assigned_cost_eur, today_eur)`). Neither file in 39c4595..a96e449 diff → unchanged since audit. Band: mandatory_saving + migration_saving both computed (lines 197-199) — was already so at audit time.
- T3: (d) bias_table.md header "Last refreshed: 2026-05-22" — stale; lines 23-26 still claim FedEx "absent from _decision_sets.CARRIERS entirely". But _decision_sets.py:23,53 wires fedex NEW_OFFER|OFF. bias_table.md last touched by e2b898c (a move, pre-audit). → (d) OPEN.
- T4: (e) annual_report.py:152 "UPS forward | Q1 actuals × 1.05 GRI | evergreen tariff-floating; GRI vs own note 5.9%" — GRI still 5%, discrepancy disclosed in standing-items callout (line 409). Need to find the constant.
- T5: (e) q1_base.py:27 `UPS_GRI_PCT = 0.05` — still 5%; annual_report.py:152+409 disclose "GRI vs own note 5.9%" as a standing item. PARTIAL (disclosed, not fixed).
- T6: (b) build_annual.py:196-206 — two-tier split: contingent = DB-Schenker-origin reroute saving (€525k), firm = rest (€472k). annual_stats.json: lowconf_dest (Maersk+Hermes destination) = €782k = 80% of peak-free saving → ~€256k of never-validated Maersk/Hermes face-value saving sits INSIDE firm tier (origin-gate, not destination-gate). Disclosed in callout (annual_report.py:391 "80% of total saving lands on Maersk+Hermes regardless of origin"). Mechanism = gating/split, no haircut/band (fuel ±2pp band only).
- T7: (a) routing_report.py:60-82,323-325 — Q1-framed headline, §00 confidence split, Hermes/Maersk never-shipped-face-value-no-trust-gate caveat, UPS GRI bullet, "annualisation is a separate re-weight, not a ×4". decision_report.html — same Q1 framing + "engines at face value" + Hermes "modelled, never shipped". BUT both still say annualisation "parked"; neither points to annual_2026/ report. exec_brief.html — Hermes "modelled, never invoice-measured / validate a real invoice before banking" present; Maersk card has "two Maersks" + "ROW demand/peak assumptions (held)"; NO UPS-GRI caveat, no annualization note (it's a full-year-2025 segment brief).
- T8: (f) hermes constants.py:8 ENGINE_VERSION "hermes-2.2.0"; changelog 2.1.0 (Q4 reply 2026-06-10): 450L volume gate RETRACTED, replaced by dims/girth gate. calculate.py:195-209 — standard (d_max<=120): reject if d_mid>60 | d_min>60 | girth>300; bulky (120<d_max<=170): reject if girth>360. Cross-section breaches now GATED at eligibility (rejected → route elsewhere), not surcharged. LANDED (commit fceacc6, rebuilt via 052d3c4/a96e449).
- T9: (g) maersk constants.py:118-128 ROW_DEMAND_EUR_PER_KG = 0.0 — still a documented flagged deferral ([[S120_3760e65b_eu-tender-full-year-build|S120]]), unchanged post-audit. maersk-3.2.0 changed girth def only. Disclosed in exec brief ("ROW demand/peak assumptions (held)"). OPEN.
- T10: (a) management_briefing/eu_tender_2026_briefing.html — UNTRACKED in git, still says "€377,000 saved in Q1 ... And it's a conservative floor — the real number is likely higher" while current routing_stats.json saving = €201,916. The management-facing artifact retains exactly the framing the audit flagged + a stale number. Neither routing_report nor decision_report points to annual_2026/ (both still say annualisation "parked").

## Verdicts
(a) PARTIAL — routing/decision reports reframed as Q1 + caveats; management briefing still "conservative floor" + stale €377k; no pointer to annual_2026.
(b) PARTIAL — gating mechanism (firm vs DB-Schenker-contingent) in place + clearly separated; but gate is origin-based: ~€256k Maersk/Hermes face-value saving inside "firm"; no haircut/band.
(c) OPEN — coalesce unchanged, no floor (decision_scorer.py:189; _2026q1.py:154); band (mandatory+migration) predates audit.
(d) OPEN — bias_table.md last refreshed 2026-05-22; still claims FedEx unwired vs _decision_sets.py:53.
(e) PARTIAL — UPS_GRI_PCT=0.05 (q1_base.py:27); 5.9% discrepancy disclosed as standing item, not fixed.
(f) LANDED — hermes-2.1.0 girth/cross-section eligibility gate (calculate.py:195-209).
(g) OPEN — ROW_DEMAND_EUR_PER_KG=0.0 (maersk constants.py:128), unchanged.

Bottom line: 1 of 7 fully closed (f); 3 partial (a,b,e); 3 open (c,d,g).
