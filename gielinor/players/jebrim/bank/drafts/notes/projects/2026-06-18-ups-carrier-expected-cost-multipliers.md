# Carrier `expected_shipping_cost_eur` accuracy + applied correction multipliers

**Drafted:** 2026-06-18 (S262). From the June Picturator quota-crater investigation → generalized to a per-carrier estimate-accuracy scan. Scope: TCG order sources (`source_system IN ('PCS','PicaAPI','Picturator')`), gold `shipping_mart`, order-month lens.

## The decision (principal, 2026-06-18)
Applying these multipliers to the carrier `expected_shipping_cost_eur` estimate: **UPS ×1.20, DB Schenker ×1.10, DPD UK ×1.10, USPS ×1.08.** All other carriers left at ×1.0.

## Why — the estimate is understated, carrier-specific not global
Same-parcel test (invoiced parcels, 2026 YTD, `cost_source='invoice'`, expected vs real on identical shipments — zero selection confound):

| Carrier | exp/pcl | real/pcl | gap% | under-fill € (2026 YTD) | raw mult |
|---|--:|--:|--:|--:|--:|
| **UPS** | 6.87 | 8.44 | 18.6% | **429,542** | ×1.23 |
| DB Schenker | 50.73 | 55.66 | 8.9% | 61,259 | ×1.10 |
| DPD UK | 6.22 | 6.95 | 10.4% | 44,218 | ×1.12 |
| USPS | 5.98 | 6.44 | 7.1% | 42,228 | ×1.08 |
| DPD Poland | 4.35 | 4.66 | 6.7% | 34,336 | ×1.07 |
| Asendia USA | 18.11 | 20.06 | 9.7% | 33,936 | ×1.11 |
| OnTrac | 9.03 | 9.27 | 2.6% | 30,797 | ×1.03 |
| Direct Link | 6.54 | 7.24 | 9.7% | 6,063 | ×1.11 |
| Yodel | 6.05 | 6.07 | 0.2% | 200 | ×1.00 |
| **DHL** | 3.31 | 3.31 | −0.1% | −2,395 | ×1.00 |
| FedEx | 19.99 | 19.81 | −0.9% | −4,730 | ×0.99 |
| Maersk | 4.87 | 4.74 | −2.8% | −11,633 | ×0.97 |

- **UPS is the dominant defect — 63% of all under-fill.** Everything else is a rounding error beside it.
- **DHL is accurate AND the biggest carrier (523k parcels) — it anchors the blended quota.** That's why the all-carrier quota barely moved on UPS-only correction; June's residual gap needed the mid-tier carriers too.
- **Maersk / FedEx OVER-estimate** (×0.97 / ×0.99) — a uniform global bump would make them worse. Correction must be per-carrier.

## UPS multiplier basis (the refined ×1.20)
- UPS estimate is **flat ~€6.8/parcel year-round**, missing the variable layers (fuel index 11–26% m/m, peak/demand, linehaul). It does NOT track the seasonal cost rise → understates worst in high-cost months (Apr–May 2026, ~25%).
- Raw real-vs-expected = ×1.23. Refined to **×1.20** by taking the target as *real with over-max fully refunded + LPS at 30% refund* (target ≈ €8.0/parcel ÷ expected €6.8). Over-max charges land on sub-threshold parcels (≤328cm vs 400cm UPS limit) → dispute/refund basis is sound.
- **Flat-multiplier caveat:** ×1.20 over-corrects calm low-surcharge months (mid-2025) and under-shoots over-max months (Apr–May 2026, where real carries the over-max the ×1.20 excludes). Validated sim lands adjusted-expected within ±1.3pp of real, centered near zero. The *real* fix is refreshing the estimator's fuel/base, not a flat scalar — multiplier is the interim.

## Where the gap originally surfaced
June 2026 Picturator quota looked artificially low (~16% vs ~19% matured). Two causes: (1) **partial-month maturity** — June ~20% invoiced, cost numerator under-fills vs order-month revenue; (2) **estimate under-pricing** — the un-invoiced majority rode the low estimate. Both self-correct as invoices land except the estimate defect, which these multipliers address. Applying UPS ×1.2 alone lifts June's blended all-carrier quota only +0.68pp (17.94→18.62) — the mid-tier carriers are needed to close the rest.

## DQ note (corrects an in-session claim)
- Gold `fact_shipment_invoice_lines` **DOES** carry UPS main-source (`invoice_source='ups'`) oversize charge detail — an earlier in-session assertion that it only held `dhl`/`ups_orwo` and forced a silver detour was wrong (verified live: May 2026 UPS oversize €77,124 present in gold, reconciles to the bucket).
- `fact_shipment_cost_summary.oversize_overweight_eur` = LPS + OML + demand-LPS + demand-OML + additional-handling, **net of in-place reversals**. Split LPS vs OML via `fact_shipment_invoice_lines.charge_description_english ILIKE '%large package%'` vs `'%over max%'`.

## Artifacts
- Charts + SQL: `shipping-agent/workbench/analysis/20260618-ups-quota-refund-adjusted/` (multiplier sim: `outputs/...quota-invoiced-vs-adjusted-expected-sim.html`).
- Quest-log: `quest-log/in-progress/S_shipagent_picturator-ups-overmax-refund-rerate.md` + siblings (`...june-quota-maturity`, `...june-estimate-gap-decompose`).

Cross-link: [[reference_shipping_mart_revenue_and_quota]] (quota basis), [[scm]] digest (cost-basis: `final = COALESCE(real, expected, avg)`), [[shipping-mart]] digest, [[carrier-contracts]] (UPS fuel/peak surcharge structure feeds the estimator gap).
