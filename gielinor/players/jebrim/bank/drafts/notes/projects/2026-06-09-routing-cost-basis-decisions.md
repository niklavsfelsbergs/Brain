# EU-tender routing — forward cost-basis per carrier (2026-06-09)

**Status:** decisions stable (made [[S175_6c5170d1_routing-cost-basis-review|S175]], sid 6c5170d1). Routing NUMBERS pending rebuild — **do not quote a saving from this note.**
**Anchor:** quest `S175_6c5170d1`; engine validations off `2_analysis/data/cost_matrix_2026q1/` (March DHL, Q1 DPD); plan `2_analysis/carriers/PLAN_dpd_pl_current_engine.md`.

The routing should price each carrier on its FORWARD basis vs a **2026-Q1 invoiced-actuals baseline**:

- **Principle:** current contract = invoiced actuals (mart); new offer = the per-carrier engine. `5_shipping_savings/engines/` re-rates are one-shot / un-reviewed / incomplete (under-price 20–35% vs invoices) — not used.
- **DHL Paket → new engine.** Validated +3.1% vs March-2026 actuals (Preisliste live 2026-03-01); base <1%; Warenpost cheap on light. €20 Sperrgut on 953 WICKEL parcels (d_mid > 60) = €19k/Q the current contract bills at €0 — accepted.
- **DPD PL → keep current contract, decline new offer** (worse on 100% of material volume). Price on invoiced actuals → build a current-contract engine (covers ~30 lanes, ships 7).
- **UPS → actuals ×1.05** (GRI proxy; no trustworthy engine).
- **Maersk → FR actuals + EU engine. DB Schenker → actuals. Hermes → new engine.**

**DPD flow detail (why the new offer is worse):** the current contract has two export services — `Direct, special offer` (6 western countries: AT/DE/FR/BE/LU/NL, cheap) and `export MIX HOME service` (all 30). The new offer (`27.04.2026v2.xlsx`) is a single `Picanova` sheet that kept the cheap `direct transport` flow only for DE/BE/NL and **demoted AT/FR/LU to `Mix transport`**. The new Mix rates ≈ the current MIX HOME rates — so it's **not a hike on the comparable tier, it's a flow downgrade** + a €0.20/pc flat-services stack. FR is the extreme: +60%, pure flow-swap.

Links: [[eu_tender_2026]]. Sibling lesson: [[reconcile-contract-tier-against-actuals]].
