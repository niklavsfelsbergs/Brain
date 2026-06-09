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
specialist: shipping-agent (spawn for the 2026-Q1 actuals baseline pulls)
freshness: 2026-06-09
synthesized: 2026-06-09
---

# EU Tender 2026 — quantitative carrier-tender review

Pick **4–6 parcel + 1 freight** carrier partners for TCG-Picanova, optimising **cost only** (qualitative goes in prose, not weights). Repo: `bi-analytics-main/NFE/projects/2_EU_tender_2026/`. **Decision basis = full-year cost**: 2026-Q1 is the per-shipment unit-cost reference, re-weighted by an annual volume profile (Q1 never exercises peak/demand surcharges, the Q4 volume + product-mix spike, forward fuel — a Q1-cheap carrier can be Q4-expensive). Locks (2026-05-12): hard cap 6, cost-only, lane diagnostic informs + portfolio scenarios decide.

## Architecture (Phase 2, `2_analysis/`)
Capability matrix (pure `(carrier,service,country,weight,dim,packagetype)→eligible?+reject_reason`) → **per-carrier rate engines** (`carriers/<slug>/`, polars `Surcharge` ABC, two-phase BASE→DEPENDENT, version-stamped) → **cost matrix** (one row per shipment×carrier×service) → lane diagnostic + portfolio scorer. 9 engines: maersk, dhl_paket (incl Warenpost, →2.2.0), dhl_express, gls, guell, austrian_post, hermes, dpd_pl, fedex. UPS is a separate `1_offers/picanova/UPS/calculation/` track. `docs/` is live state (DECISIONS/ASSUMPTIONS/OPEN_QUESTIONS/NEXT…); **DECISIONS must match engine state, not target state** (the [[S034_2026-05-22_eu-tender-logic-review|S034]] drift lesson) → [[eu_tender_2026_S034_update]].

## Scoring — the switchable incumbent
A carrier we ship today *and* that bid with a working engine (DHL Paket, Maersk, DPD PL; UPS pending) takes one of `INCUMBENT | NEW_OFFER | OFF` per scenario. **INCUMBENT bid = the 2026 engine where it can price, 2025 invoice only as fallback** — so the do-nothing baseline is itself a 2026 computation (+€581k vs invoice-today). No-engine incumbents (UPS, DB Schenker) keep the flat invoice. → [[eu-tender-switchable-incumbent-treatment]].

## Re-rating discipline (load-bearing, hard-won)
- **Trust gate before any savings claim:** an engine must reproduce what that carrier *actually charged* on its own shipments before it may price a competitor. Only ~4/12 were unbiased; bias does **not** wash out in aggregate — quarantine a biased engine as a *destination*, never blanket-scale it to its actual. → [[2026-05-31-shipping-savings-rerating-trust-gate]].
- **Quarantine grain = service-lane, not engine** (MAERSKFR validated 1.00× but UK/SE dragged the engine aggregate to 0.50 → buried a real €249k FR lane).
- **Reconcile the contract tier against invoiced actuals before comparing** — the DPD new offer reads as a *flow downgrade* (AT/FR/LU demoted to Mix), not a rate hike; wrong tier flips the sign. **Decompose a cost gap to driver before naming a cause.**

## Current state (2026-06, routing rebuild in flight)
Baseline = **2026-Q1 invoiced actuals** (531,194 parcels, €3.03M, 100% invoiced). Forward basis per carrier → [[2026-06-09-routing-cost-basis-decisions]]: current = mart actuals, new offer = engine. Emergent portfolio ≈ **6**: DHL Paket, Maersk (FR actuals + EU engine), Hermes, DPD-PL (keep current, decline new), UPS (actuals ×1.05), **DB Schenker** (freight, ~165 must-freight via the per-destination size envelope → [[2026-06-08-eu-tender-db-schenker-reroute-validation]]). Q1 saving ≈ **€378–411k (~13–14%)**; tender beats today on ~89% of book, loses on ~11% (keep current Maersk on FR + CH/ROW bulky). Deliverables: `carrier_overview_v2/` (per-carrier cost-structure cards), `routing_2026q1/` (routing report + service split), `decision_report/`.

## Live work
Spawn the **shipping-agent** for actuals/mart pulls. Per-carrier rate detail, fuel/surcharge specifics → the engines in the repo + [[carrier-contracts]] (rate cards, invoice DQ). Sibling [[shipping-mart]] is the data layer underneath.
