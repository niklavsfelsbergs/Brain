# S244 — US-origin shipping-cost QUOTA, mart revenue basis + lens reconciliation (LucaNet)

**Role:** shipping-agent sub-agent (mart pull). Principal: Jebrim.
**Tier:** gold-contract for the answer; revenue + cost both off the four gold facts. (CLAUDE.local.md maintainer profile present — `tcg_nfe` — but stayed on gold; no upstream needed.)

## Ask
Reconcile the US 2026 (Jan-May) shipping-cost quota (cost / revenue) per month vs LucaNet. Load the mart contract; state PRECISELY how `net_revenue_eur` is defined (grain/lens/scope/currency/refunds); compute monthly quota the SCM way; answer the lens-mismatch question (cost on ship-month, revenue on order-month).

## Scope used
- US origin = production_site IN ('PCS CMH','PCS PX'); calendar 2026-01-01..2026-05-31.
- Cost = freight only (final_shipping_cost_eur, tax/customs excluded by design; invoice-lines excluded explicitly).
- Revenue denominator = fact_shipments.net_revenue_eur.

## Revenue definition (load-bearing, from mart-contract + tables.md + S244 corrected bank note)
- Column: fact_shipments.net_revenue_eur. EUR (FX-converted). Shipment grain — per-order revenue split across parcels by qty share, reorders zeroed. Net of discounts.
- Picturator (B2C): PRODUCT + allocated SHIPPING - allocated DISCOUNT (includes customer-paid shipping -> NOT a pure-product denominator). PicaAPI (MerchOne): product-line-only. PCS: 0 by design (cost-only).
- SCM lens = ORDER-MONTH (shop_order_created_date) on BOTH sides. Reproduces SCM (S244 tie-out US May 26.5%). Ship/production month give different/higher numbers.
- SCOPE = shipped-subset: only revenue of orders that produced a US-origin parcel. US revenue with no US-origin shipment (digital/dropship/fulfilled elsewhere) is NOT in the mart denominator -> mart denom is a subset of full accounting Net Revenue. This explains mart quota running ~1.5-2pt above LucaNet.

## Results
SCM-faithful (order-month both sides): Jan 25.4 / Feb 24.5 / Mar 26.1 / Apr 28.3 / May 27.2 %. pct_invoiced 95-99%.
Lens-mismatch (cost ship-month / rev order-month): Jan 25.5 / Feb 27.7 / Mar 23.9 / Apr 26.6 / May 28.2 %.
Period total: ~26.3-26.4% (ties across lenses). LucaNet target: ~24-25%.

## Checks
- Ship-month invoice-line freight = EUR 2,718,450.137 / USD 3,180,668.11 -> ties EXACTLY to prior S244 cost pulls.
- Order-month cost (fact_shipments) = EUR 2,710,864 -> 0.3% below ship-month total (edge-of-window straddle). Annual ties; monthly wobbles up to 3pt -> the lens-mismatch effect confirmed.
- PCS zero-revenue rows distort quota immaterially (<0.2pt). Uncosted shipments ~0. May 95.1% invoiced = soft floor (late-May backfilling).

## Deliverables (outside brain)
- Chart: shipping-agent/scratchpad/20260616-073033--us-quota-mart-vs-lucanet-3series.html
- SQL: shipping-agent/scratchpad/20260616-02_us-quota-mart-revenue-lens-jan-may-2026.sql
- CSV: shipping-agent/scratchpad/20260616-us-quota-mart-vs-lucanet-long.csv

## Open / needs principal
- The mart denominator is a shipped-subset; reconciling fully to LucaNet needs the full US accounting Net Revenue (dw/ledger), which is off the gold contract. Mart cannot confirm how much US revenue has no US-origin shipment.
- LucaNet's monthly shape matches neither mart construction cleanly (Feb/Mar diverge) -> likely a definitional revenue gap (shipping-inclusive vs product-only; refund timing), not just lens.
