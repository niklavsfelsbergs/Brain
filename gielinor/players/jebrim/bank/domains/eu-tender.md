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
  - bank/notes/projects/2026-06-11-eu-tender-red-team-audit.md
  - bank/notes/projects/2026-06-11-eu-tender-annualization-method.md
  - bank/notes/projects/2026-06-11-ups-cascade-new-canon.md
  - bank/notes/projects/2026-06-11-eu-tender-baseline-bridge-basis.md
  - bank/notes/projects/2026-06-11-ups-routing-keep-vs-offer-and-ww-eco-tail.md
  - bank/notes/projects/2026-06-11-ups-engine-vs-current-cost-corrected.md
  - bank/notes/projects/2026-06-11-eu-tender-no-hermes-6th-slot-landscape.md
  - bank/notes/projects/2026-06-11-gls-old-vs-new-offer-why-worse.md
  - bank/notes/projects/2026-06-11-eu-tender-negotiation-cost-positions.md
  - bank/notes/projects/2026-06-11-dhl-sperrgut-template-knife-edge.md
  - bank/notes/projects/2026-06-11-eu-tender-result-investigation-round1.md
  - bank/notes/projects/2026-06-11-savings-yardstick-rate-vintage-bridge.md
specialist: shipping-agent (spawn for the 2026-Q1 actuals baseline pulls)
freshness: 2026-06-11
synthesized: 2026-06-11 (post-UPS-cascade re-stamp)
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

## Current state (2026-06-11, post-UPS-cascade — maersk-3.2.0 / hermes-2.2.0 / ups-2.0.1)
**CANONICAL PRESENTED REPORT = `2_analysis/final_report_no_hermes_v2/`** (`report_no_hermes_v2.html` + `deck_no_hermes_v2.html`), presented to management 2026-06-12 as a standalone "Carrier Recommendation". Headline = **five-carrier base portfolio €976,024/yr firm** (`final_stats.json` → `structure.base_ann`; no Hermes, DBS pinned to freight). When asked "the final saving" → **976k firm** is the answer. The gated Hermes+DBS-reroute module (€932,683/yr, `structure.module_ann`) is stripped from this presented version — it lives in the with-module reports only. **`2_analysis/final_report/` and the old base €420k / oversize-module €577k split are SUPERSEDED — do not quote them** ([[S221_eec4ee99_eu-tender-report-review-qa|S221]] standalone reframe; the €976,024 base already nets Direct Link exit −€47,305 + Q4 peak differential −€41,194 → [[S222_3309c3da_no-hermes-v2-headline-reconciliation|S222]]).

UPS tender engine built + cascaded into the portfolio (incumbent-with-engine, per-(dest×packagetype)-cell pick) → [[2026-06-11-ups-cascade-new-canon]]. **NEW CANON (q09 do-nothing basis): paid €2,955,020 → do-nothing €3,055,317 → plan €2,660,120 = Q1 €395,197 (12.93%) / annual €1,908,707/yr (12.66%, band €1.88–1.93M); firm €990,225 + DBS-contingent €918,482; rate moves €483,133.** Supersedes both prior canons (€974,692/yr q09-no-UPS, €997,720/yr vs-today). Savings basis = keep_ref − rcost vs **do-nothing @2026 rates** (not raw Q1 actuals) → [[2026-06-11-eu-tender-baseline-bridge-basis]] / [[2026-06-11-savings-yardstick-rate-vintage-bridge]]. The firm/contingent split is the decision line (pre-UPS it was base €420,218 + oversize module €577,502, [[S194_907d4e63_eu-tender-holdup-pass-and-project-rating|S194]]); DBS-contingent still rides the gated Hermes+DBS-reroute module (3 gate conditions: DBS dims check, module numbers hold, Hermes' appetite for ~30k/yr oversize-heavy volume). Maersk girth ceiling + Hermes gate unchanged → [[2026-06-10-maersk-hermes-oversize-corrections-and-savings-split]] / [[2026-06-10-db-schenker-reroute-package-dims-and-savings]]. Annualization = Q1 base × per-country 2025 profile (~×4.8; peak the only seasonal term) → [[2026-06-11-eu-tender-annualization-method]]; red-team standing items → [[2026-06-11-eu-tender-red-team-audit]].

**UPS decision + portfolio moves:** contract being replaced → "keep today" is off the table; **sign the offer, negotiate CH/GB operative-tier base before signature** (that's the residual cost gap), dispute Nordics oversize; offer ~break-even vs GRI'd today, WW-ECO/AU tail stays on current by rule → [[2026-06-11-ups-routing-keep-vs-offer-and-ww-eco-tail]] / [[2026-06-11-ups-engine-vs-current-cost-corrected]]. renew_ups −€50.9k wholesale vs +€103k/Q1 selective (report-framing call). No-Hermes 6th-slot: DBS reroute **survives without Hermes** (€696k UPS+DHL) → [[2026-06-11-eu-tender-no-hermes-6th-slot-landscape]]. GLS now uncompetitive vs its own 2025 terms (flat 2-25kg card abolished) → [[2026-06-11-gls-old-vs-new-offer-why-worse]]. Per-carrier negotiation levers + cost positions → [[2026-06-11-eu-tender-negotiation-cost-positions]]; DHL Sperrgut = template knife-edge artifact, not a lever → [[2026-06-11-dhl-sperrgut-template-knife-edge]]. Reports current through the [[S208_9399f067_ups-cascade|S208]] cascade + [[S210_a17168ec_decision-report-regen|S210]] decision_report regen; **management deck still stale** (pre-UPS). UPS round-2 asks open (CH/GB tier, OML 400-vs-419, LPS, Express).

## Project scale (as of 2026-06-12)
~**115 Claude sessions actually worked this tender** (73 heavy build/report/audit; 66 left a tender quest file; 68 did hands-on file work) — out of **441 total sessions** on the repo and **~215 main-brain close rituals**. The quest-file count under-counts real effort ~2× (lighter working/consult + `/clear`-without-close sessions leave no durable trace; "mentions" over-count too — the digest force-loads on any carrier/tender cue). Counted by *work-signal depth*, not keyword mentions → forensic method + full reconciliation in [[S215_12aa2f0f_rateproof-study-guide|S215]].

## Live work
Spawn the **shipping-agent** for actuals/mart pulls. Per-carrier rate detail, fuel/surcharge specifics → the engines in the repo + [[carrier-contracts]]. Sibling [[shipping-mart]] is the data layer underneath.
