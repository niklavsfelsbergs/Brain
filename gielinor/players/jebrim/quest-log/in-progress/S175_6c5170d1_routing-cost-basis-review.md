# S175 — EU-tender routing cost-basis review (DHL / DPD / UPS forward pricing)

**Player:** Jebrim · **Session:** 6c5170d1 · **2026-06-09** · **Status:** in-progress (analysis + decisions done; DPD-current engine build + routing refactor pending)

Started as a read-only confidence assessment of `routing_2026q1/routing_report.html`; became a review of the routing's cost basis and a per-carrier set of forward-pricing decisions.

## What was asked
Rate confidence that `routing_report.html` is the cost/carrier-count optimum. The review exposed that the routing prices incumbents on a *mix* of invoiced actuals (the "keep" path) + new-offer engines, and that the basis was wrong or ambiguous for several carriers. Niklavs drove a per-carrier cost-basis decision, with a deep dive on DPD PL.

## Decisions — forward pricing basis for the routing rebuild
- **Principle:** current/old contract cost = **invoiced actuals** (the mart); new offers = the **per-carrier engines**. The `5_shipping_savings/engines/` re-rates are one-shot, un-reviewed, incomplete (under-price 20–35% vs invoices) — **not used** for anything.
- **DHL Paket → price off the new engine.** Validated vs March-2026 actuals (the new Preisliste is live since **2026-03-01**, so March actuals are on new rates): engine **+3.1%** aggregate, base matches <1%, light book (<2 kg, 88%) within 1–5%. Only divergence: €20 Sperrgut on **953 WICKELVERPACKUNG** parcels (d_mid 60.5 > 60 → correctly triggered) that the current contract bills at €0 — **€19k/Q**. Accepted (impact stays); note the quirk in docs, don't "fix".
- **DPD PL → keep current contract, DECLINE new tender offer.** New offer worse on **100% of material volume** (NL +12, BE +14, AT +29, LU +16, FR +60%). Root cause: new offer ≈ standard Mix rates + a €0.20/pc flat-services stack, and **AT/FR/LU were moved off the cheap `Direct, special offer` service onto `Mix transport`**. FR +60% is a pure flow-swap (new Mix rate = current MIX HOME rate; the current Direct flow is what's cheap). Price DPD on **invoiced actuals** interim → **build a current-contract engine** (covers ~30 lanes but ships only 7 → actuals-only is blind to the rest; opportunity ≈ €53k/Q displacing UPS on IT/ES/FR; ceiling ~€123k vs-today but mostly overlaps other carriers).
- **UPS → actuals ×1.05** (GRI proxy; no trustworthy engine — the re-rate under-prices, no new offer received).
- **Maersk → FR actuals + EU engine** (unchanged; the new Maersk offer structurally doesn't price FR).
- **DB Schenker → actuals. Hermes → new engine** (no actuals exist).
- **Baseline = 2026-Q1 invoiced actuals** (current contracts).

## Deliverable
`2_analysis/carriers/PLAN_dpd_pl_current_engine.md` — current-DPD engine build spec + handover prompt. Written to **bi-analytics-main (SEPARATE repo, UNCOMMITTED, principal-gated)**.

## Turn log (condensed)
- Confidence rating on routing_report.html: ~70% blended — carrier *set* strong (~85%), cost *magnitude* soft (~55-60%) on face-value engines / Q1-only / DPD tier.
- Established the cost-basis mechanism in `build_final.py` (keep=actuals, eng=offer, cheapest wins).
- DHL engine validated against March actuals by component → Sperrgut-on-WICKEL isolated.
- DPD: corrected polarity (the `1. EU` folder file is the CURRENT contract); new offer = `27.04.2026v2.xlsx` single Picanova sheet; decomposed +18.8% to base + flat-services (not CH customs, not service mismatch); per-lane + FR base side-by-side; flow-swap confirmed.
- Decided keep-current + build a current-DPD engine; wrote the plan; produced a handover prompt.

## Pending external actions
No pending external actions. (Analysis session; one plan file written to bi-analytics-main, uncommitted, principal-gated.)

## Cascade.
On the eventual rebuild: `routing_report.html` + `carrier_overview` annotations + the EU-tender `docs/` per-carrier status tables must reflect the forward-basis change (DHL→engine, UPS→×1.05, DPD→current engine). Not done this session — deferred to the build/refactor.

## Main-brain changes.
None.
