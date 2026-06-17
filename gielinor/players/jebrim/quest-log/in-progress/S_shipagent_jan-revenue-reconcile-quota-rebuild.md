# Shipping-agent pull — Jan-2026 revenue reconcile (€11.4M vs €7.2M) + 2026 quota rebuild

Spawned by Jebrim. Scope resolved in brief: vertical = TCG (Picturator+PicaAPI), origin = ALL production sites EXCEPT {Wolfen, PCS CMH, PCS MI, PCS PX}.
Tier: mostly gold contract; dw.sales_fact side is OFF-CONTRACT (CLAUDE.local.md full-access, tcg_nfe user). Read-only throughout.

## Status log
- Loaded how_to.md (full) + mart-contract + CLAUDE.local.md. Confirmed quota = SUM(final_cost)/SUM(net_revenue_eur), order-month, mart net_revenue_eur.
- TASK 1: SCM repro Jan-2026 = €7,152,452 (NOT IN exclusion, NULLs dropped) / €7,192,983 (NULL sites kept). Lands ~€7.2M. Confirmed.
- Suspect dw figure reproduced to the cent: €11,445,413.54 (dw.sales_fact.revenue_net_price_eur, archivedtime, data_source only).
- TASK 2 gap decomposition (stacks exactly, €0 residual):
  - site exclusion (a): -€3,707,124  (mart all-sites OM €10,859,576 -> site-excl €7,152,452)
  - date-lens archivedtime->order-month (c): -€542,716  (dw archivedtime €11,445,414 -> dw created_date €10,902,698)
  - source-swap dw->mart (b): -€43,122 (negligible — same revenue def)
  - population test/invalid/cancelled/non-shipped (d): ~€0. testorder=€0, invalidorder=€0. dw `shipped_at` is SPARSELY POPULATED (only 68,875 of 336,308 OM rows), NOT a ship/cancel signal — row counts dw 336,308 vs mart 343,155 match. The "€10.4M never-shipped" red herring dissolved on the count reconcile.
- TASK 3 quota rebuilt on SCM-correct revenue (order-month). Hybrid cost: invoiced freight (excl tax+customs) by shipment_date else expected_shipping_cost_eur by order-month (mart has no archivedtime — surfaced).
  - Jan 20.89% | Feb 18.50% | Mar 15.51% | Apr 17.74%(partial) | May 18.47%(partial) | Jun 19.44%(partial)
  - Revenue lens used = order-month. Jan under ship-lens = 18.84% -> lens choice moves Jan ~2.05pp.
  - Fallback share: Jan 1.98% Feb 1.94% Mar 2.20% Apr 9.06% May 25.63% Jun 70.81%. Apr+ partial (invoice frontier ~2026-06-15).

## Checks
- Gap components sum to €4,292,962 = €11,445,414 - €7,152,452 exactly.
- dw vs mart at matched scope+lens within €43K / 7K rows — confirms same population, same revenue def.
- Cost numerator 98%+ invoiced Jan-Mar; fallback climbs as expected at frontier.

Deliverable: chat-only (per brief). No files outside brain.
