# S262 — UPS/carrier expected-cost estimate accuracy + correction multipliers

**Session:** ac4b4649 · **Player:** Jebrim · **Date:** 2026-06-18 · **Status:** complete

## Ask
Started from a SCM screenshot: "why is Picturator shipping cost quota so low in June?" Evolved across the session into a full UPS estimate-accuracy investigation and a per-carrier `expected_shipping_cost_eur` correction-multiplier decision.

## What happened (turn arc)
1. **June Picturator quota crater** — diagnosed as a partial-month maturity artifact (June ~20% invoiced; order-month books revenue early, cost lags) + UPS estimate under-pricing. Confirmed via shipping-agent sub-pull.
2. **Estimate-gap decomposition** — found UPS the dominant driver; the un-invoiced majority rides a low estimate.
3. **May→June quota bridge** — reconciled the −2.53pp drop to maturity (−1.75pp, self-corrects) + cheaper carrier mix (−0.78pp, real). Implied mature June ~17.8%.
4. **Over-max refund re-rate** — stripping all OML+peak-OML leaves a ~22% residual; the estimate is light beyond surcharges.
5. **Expected-vs-real chart series** — built the SCM-style UPS quota line + refund-adjusted + expected lines; proved the estimate is flat ~€6.8/parcel year-round, missing fuel/peak/seasonal.
6. **Multiplier derivation** — UPS target (over-max out + LPS 30%) ÷ expected ≈ **×1.20**.
7. **Per-carrier scan** — same-parcel expected-vs-real across all carriers; UPS ×1.23 dominates (63% of under-fill), DHL accurate (and biggest), Maersk over-estimates.
8. **Simulation + full-quota** — applied UPS×1.2/DBS×1.1/DPD-UK×1.1/USPS×1.08; validated adjusted-expected lands within ±1.3pp of real.

## Decision (principal)
Applying multipliers to `expected_shipping_cost_eur`: **UPS ×1.20, DB Schenker ×1.10, DPD UK ×1.10, USPS ×1.08**, rest ×1.0. Full detail + per-carrier table in the bank draft.

## My errors (harvested)
- Called the UPS estimate "in line" (×1.016) off a **selected un-invoiced-remainder subset** (€8.03/parcel) — wrong; corrected to all-parcel ×1.20 on a same-parcel proof. Classic selected-subset-vs-blend mistake; principal caught the confusion. → examine draft.
- Nearly over-spawned the shipping-agent for the per-carrier scan, which was one GROUP BY — caught it per the S260 litmus now in CLAUDE.md and ran it myself. → reinforces the run-yourself discipline.

## DQ correction
Gold `fact_shipment_invoice_lines` DOES carry UPS main-source oversize detail (verified live, reconciles to the cost-summary bucket) — contradicts an earlier in-session claim that forced a silver detour. `fact_shipment_cost_summary.oversize_overweight_eur` = LPS+OML+demand variants, net of reversals.

## No pending external actions.
All data work read-only (Redshift MCP + shipping-agent sub-agents). Chart/SQL deliverables live in `shipping-agent/workbench/analysis/20260618-ups-quota-refund-adjusted/` (outside the brain).

## Artifacts
- Bank draft: `bank/drafts/notes/projects/2026-06-18-ups-carrier-expected-cost-multipliers.md` (the durable capture).
- Sub-agent traces (this session): `S_shipagent_picturator-june-quota-maturity.md`, `...june-estimate-gap-decompose.md`, `...ups-overmax-refund-rerate.md` (moved to completed/ with this entry).

## Open (non-blocking, not owned here)
Interim fix is the flat multipliers; durable repair = refresh UPS's `expected_shipping_cost_eur` estimator to track fuel/peak/seasonal (bi-etl ticket) — would let the scalar be dropped. Principal's call if the estimate feeds anything beyond the dashboard.
