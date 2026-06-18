# S259 — Shipping-cost quota: archived/shipment-date anchored, three-way vs SCM + Accounting

**Player:** Jebrim · **sid8:** 5463f8a7 · **2026-06-17**

Arc: from a date-boundary shipment count to a full three-way (SCM / date-anchored / Accounting) monthly cost-quota for 2026, built by spawning the shipping-agent repeatedly, then debugged directly when a number looked wrong.

## What happened (turn arc)

1. **Archived-end-April / shipped-early-May count.** Via `dw.sales_fact.shipped_at` (log) = **0** — `shipped_at` is coupled to `archivedtime`. Via the mart's carrier invoice-line `shipment_date` = **17,571 distinct orders** (65,287 lines). Join: `dw.sales_fact.ordernumber = fact_shipment_invoice_lines.shop_ordernumber`.
2. **Monthly cross-month spillover, 2026.** Jan→Feb 18,216 … Apr→May 17,571; May→Jun partial, Jun+ no data (loading frontier ~2026-06-15).
3. **Monthly 2026 shipping-cost quota.** Hybrid cost (invoiced by shipment date where present, else expected by archived date) / revenue by archived date. Scope: order source Picturator+PicaAPI; sites excl. US PCS (CMH/MI/PX).
4. **SCM revenue reconcile.** Initial €11.4M Jan revenue vs SCM €7.2M → gap decomposed: **−€3.7M production-site-filter leak** (revenue from `dw.sales_fact` had no site filter — that column is mart-only), −€0.5M archived-vs-order-month lens, source-swap negligible. SCM revenue = mart `net_revenue_eur` by order-placed month.
5. **Reproduce SCM then re-date + conservation test.** Reproduced SCM walk (19.7/19.2/18.3/19.0/19.3) to <0.15pt. Re-dating conserves on an interior closed window (Feb–May revenue +0.31%, cost +1.8%); full-2026 differs only by the open-year boundary inflow.
6. **Three-way deliverable.** SCM / date-anchored / Accounting (LucaNet CM1 Europe ACT 2026, given). CSV + formatted Excel in shipping-agent scratchpad.
7. **v2 = include Wolfen** (sites excl. US only). Wolfen runs ~16.4% cost/rev (SCM lens) — cheaper than core ~19%; the earlier "+1.4–2.2pt" uptick was the US sites, not Wolfen.
8. **Anchored-revenue regression caught.** v2 anchored revenue == SCM revenue (broken) — agent had inverted the join (dw has no production_site). Fix: drive from `fact_shipments` (has site), look up `archivedtime` from sales_fact (many-to-one, no fan-out).
9. **The received_by_carrier_date bug (principal caught).** Anchored quota read suspiciously low (17.47%). Root cause: I dated invoiced cost by `fact_shipments.received_by_carrier_date` (NULL on 113k Wolfen rows → cost dropped, revenue kept) instead of the spec's invoice-line `shipment_date`. I had rationalized the low number with a "Wolfen displacement" story instead of tracing it. Corrected → **anchored YTD 19.54%**, in band with SCM 18.72% / Accounting 18.88%.

## Final v2 (incl. Wolfen) YTD quota
SCM **18.72%** · date-anchored **19.54%** · Accounting **18.88%**. Anchored uses reconciled cost (SCM-comparable); literal invoice-line basis ~8% lower (~17.9%).

## Mart facts pinned this session
- `fact_shipments`: `cost_source` ∈ {invoice, expected, avg, NULL}; `real_shipping_cost_eur` populated only when `cost_source='invoice'`. `shop_order_created_date` = order-placed (SCM lens). `received_by_carrier_date` is sparsely populated — NOT the ship-date to use.
- Invoice-line ship date = `fact_shipment_invoice_lines.shipment_date` (the spec's "shipment date from invoice lines").
- `net_revenue_eur` is shipment-split; sum across shipment rows reproduces SCM (one-per-order undershoots).
- Reconciled cost runs ~8–10% above raw invoice-line freight sum (RTS redistribution / 90-day cap).
- SCM native lens = final cost / net revenue, both by order-placed month.

## Decisions
- Revenue lens for the anchored series = archived month (matches user spec + lands ≈ Accounting, which recognizes at fulfillment).
- Cost basis = reconciled (for SCM/Accounting comparability), invoice-line basis noted as alternative.

## Pending external actions
None pending. Deliverables (CSV + 2 xlsx) written to `Documents/GitHub/shipping-agent/scratchpad/`.

## Next concrete step
See `inventory/shipping-quota-three-way-resume__5463f8a7.md`.
