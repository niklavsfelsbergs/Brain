---
domain: eu-tender
title: EU Tender 2026 — the quantitative carrier-tender review
patterns:
  - eu tender
  - eu_tender
  - carrier tender
  - tender 2026
  - decision report
  - routing report
  - carrier overview
  - portfolio scoring
corpus:
  - bank/notes/projects/eu_tender_2026.md
  - bank/notes/projects/eu_tender_2026_S034_update.md
  - bank/notes/projects/eu-tender-switchable-incumbent-treatment.md
  - bank/notes/projects/2026-05-31-shipping-savings-rerating-trust-gate.md
  - bank/notes/projects/2026-06-09-routing-cost-basis-decisions.md
  - bank/notes/projects/2026-06-08-eu-tender-db-schenker-reroute-validation.md
  - bank/notes/projects/2026-06-09-hermes-slice-carrier-delta.md
  - bank/notes/projects/2026-06-09-decision-vs-routing-savings-reconciliation.md
  - bank/notes/projects/2026-06-09-dpd-pl-current-engine-export-only-gap.md
  - bank/notes/projects/2026-06-09-tender-2.96M-vs-scm-3.3M-scope-reconciliation.md
  - bank/notes/projects/2026-06-10-maersk-hermes-oversize-corrections-and-savings-split.md
  - bank/notes/projects/2026-06-10-db-schenker-reroute-package-dims-and-savings.md
specialist: shipping-agent (spawn for the 2026-Q1 actuals baseline pulls)
freshness: 2026-06-10
synthesized: 2026-06-10
---

# EU Tender 2026 — quantitative carrier-tender review

Pick **4–6 parcel + 1 freight** carrier partners for TCG-Picanova, optimising **cost only** (qualitative goes in prose, not weights). Repo: `bi-analytics-main/NFE/projects/2_EU_tender_2026/`. **Decision basis = full-year cost**: 2026-Q1 is the per-shipment unit-cost reference, annualized via per-country seasonal ratios + peak-window volumes (Q1 never exercises peak/demand surcharges). Locks (2026-05-12): hard cap 6, cost-only, lane diagnostic informs + portfolio scenarios decide. Scope = PCS-PL print site, invoiced-only, 18 countries (€2,955,020 Q1 — a backfilling snapshot, quote with as-of date); not comparable to all-sites SCM views → [[2026-06-09-tender-2.96M-vs-scm-3.3M-scope-reconciliation]]. Maersk-UK (A0) is a separate deal, out of tender scope.

## Architecture (Phase 2, `2_analysis/`)
Capability matrix (pure `(carrier,service,country,weight,dim,packagetype)→eligible?+reject_reason`) → **per-carrier rate engines** (`carriers/<slug>/`, polars `Surcharge` ABC, two-phase BASE→DEPENDENT, version-stamped) → **cost matrix** (one row per shipment×carrier×service) → lane diagnostic + portfolio scorer. 9+ engines incl. `dpd_pl_current` (**export-only — PL-domestic unmodeled**, the "carrier-only" slice → [[2026-06-09-dpd-pl-current-engine-export-only-gap]]). `docs/` is live state; **DECISIONS must match engine state, not target state** → [[eu_tender_2026_S034_update]].

## Scoring — the switchable incumbent
A carrier we ship today *and* that bid with a working engine takes `INCUMBENT | NEW_OFFER | OFF` per scenario; **INCUMBENT bid = the 2026 engine where it can price**, invoice fallback otherwise → [[eu-tender-switchable-incumbent-treatment]]. **Decision report = selection ceiling (per-parcel cherry-pick); routing report = executed plan (one-carrier-per-(dest×packagetype)-cell)** — their headlines legitimately differ (~€102.5k operational gap) → [[2026-06-09-decision-vs-routing-savings-reconciliation]].

## Re-rating discipline (load-bearing, hard-won)
- **Trust gate before any savings claim**; quarantine grain = service-lane, not engine → [[2026-05-31-shipping-savings-rerating-trust-gate]].
- **Reconcile contract tier against invoiced actuals before comparing; decompose a cost gap to driver before naming a cause.**
- **Headline the bankable floor; gate + visually downplay the contingent slice** (firm leads, low-confidence gated).

## Current state (2026-06-10, maersk-3.2.0 / hermes-2.2.0)
Carrier replies resolved the oversize gaps: Maersk hard ceiling **longest ≤175 (DE 200) AND L+2W+2H ≤ 300** (girth ruling = the downside reading; most EU oversize surcharges now unreachable → Maersk lane essentially standard-only) + Hermes dimensional gate + flat-7% fuel → [[2026-06-10-maersk-hermes-oversize-corrections-and-savings-split]]. **Q1 saving €201,916 (6.8%)** (was €377k pre-corrections); **annual €997,720/yr (7%)**, band €969k–€1,026k (`annual_2026/`). The girth change re-homed the *whole book*, not just DBS (13,170 of 20,171 affected parcels were on non-DBS carriers). **DB Schenker reroute = €107,684 (53%), LOW confidence**: 4,490 moved (Hermes 4,463 / Maersk 27); 85% of switch saving sits on zV parcels whose dims are a **template, not a measurement** (open bi-etl lineage trace) → [[2026-06-10-db-schenker-reroute-package-dims-and-savings]]. All 4 reports (carrier overview, decision, routing Q1, annual) current on 3.2.0/2.2.0; management deck deferred (stale at €377k). Open carrier items: Maersk EU fuel band/schedule, UPS GRI 5/5.9, DHL thin-flat waiver.

## Live work
Spawn the **shipping-agent** for actuals/mart pulls. Per-carrier rate detail, fuel/surcharge specifics → the engines in the repo + [[carrier-contracts]]. Sibling [[shipping-mart]] is the data layer underneath.
