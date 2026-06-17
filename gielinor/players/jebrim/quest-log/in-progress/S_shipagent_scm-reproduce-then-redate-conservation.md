# shipping-agent: reproduce SCM cost-quota, then re-anchor date lenses + conservation test

**Asked:** Reproduce SCM cost-quota on its native lens (validate vs given Jan KPIs + 6-mo FINAL walk), then re-anchor date attribution only (invoiced cost -> ship date; expected tail + revenue -> order archived date), prove full-2026 cost & revenue conserve. Plus reconciled-vs-invoice-line cost-basis sensitivity.

**Scope:** TCG (source_system IN Picturator, PicaAPI); production sites = ALL EXCEPT {Wolfen, PCS CMH, PCS MI, PCS PX}. All EUR. Full-access profile (CLAUDE.local.md present) -> dw.sales_fact in-scope, flagged off gold contract.

## Status (turn-by-turn)
- Loaded how_to.md + mart-contract + CLAUDE.local.md (full-access maintainer profile, user tcg_nfe).
- No SCM contract doc in shipping-agent reference; used brief's ground-truth targets + MEMORY note (quota = final_cost / net_revenue_eur, order-month lens).
- STEP 1 VALIDATED. Native lens = order-created month (shop_order_created_date), final_shipping_cost_eur / net_revenue_eur. Jan: 235,379 ship (tgt 235,212), rev EUR7.19M, cost EUR1.41M, %inv 97.9, FINAL quota 19.55. 6-mo FINAL walk 19.55/19.14/18.26/18.86/19.25/16.38 vs tgt 19.7/19.2/18.3/19.0/19.3/16.5 -- all within ~0.15pt. HIT.
- dw.sales_fact: ordernumber unique 1:1, archivedtime fully populated; join coverage 99.97% of shipments / 99.998% revenue. Clean.
- Reconciled invoiced cost EUR5.78M vs ex-tax invoice-line sum EUR5.21M = reconciled +9.9% (NOT -6%); recon also exceeds all-lines-incl-tax by EUR276k -> reconciliation adds RTS/bulk-allocation beyond raw lines.
- STEP 2 re-anchored FINAL walk (reconciled): 22.14/20.13/17.99/18.56/20.20/17.77.
- STEP 3 conservation: full-2026 rev SCM 35.48M vs re-anchored 36.58M (+3.1%); cost 6.70M vs 7.20M (+7.5%). Delta = one-sided Jan boundary inflow (2025-created orders archiving in 2026 = EUR1.10M rev, EUR0 outflow since year open). Interior Feb-May window ties: rev +0.31%, cost +1.8% -> conservation confirmed.
- STEP 4 line-basis annual cost EUR6.60M vs reconciled EUR7.20M = -8.3%; walk drops ~1.5-2pt/month.

**Deliverable:** chat-only (per brief).
**Open:** SCM cost-basis gap measured at +9.9% reconciled-over-line, vs the ~6% the brief assumed -- flag to principal.
