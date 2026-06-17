# S244 — US-origin freight in native USD (LucaNet USD-to-USD recon)

**Role:** shipping-agent sub-agent (mart pull). Principal: Jebrim.
**Tier:** gold-contract. `fact_shipment_invoice_lines` + `fact_shipments` only.

## Ask
Reproduce the prior US-origin freight-only invoice-line pull (shipment_date 2026-01-01..2026-05-31, production_site IN ('PCS CMH','PCS PX'), exclude charge_bucket tax/customs_duties, grouped by carrier) but in NATIVE LOCAL CURRENCY (USD) instead of EUR, for a no-FX USD-to-USD compare against the LucaNet USD ledger. Confirm the native column is original-invoiced USD, confirm currency purity, give EUR vs USD side-by-side + implied blended rate.

## Scope used
- Native column: `charge_amount_local` (paired with `currency_code`). Contract: `_local` = the figure "in the invoice currency"; `_eur` is the dated FX conversion of it. So local = original-invoiced.
- EUR control column: `charge_amount_eur`.

## Status (turn-by-turn)
- Loaded how_to.md + CLAUDE.local.md (maintainer profile present; stayed on gold — invoice-lines is a gold fact).
- Verified column semantics from mart-contract.md: `_local` is invoice-currency original; `_eur` is converted.
- Currency purity check: NOT 100% USD. 722,005 USD lines + 55 EUR lines (all UPS, EUR136.81). EUR lines have NULL native-USD.
- EUR reconciliation EXACT: all-lines EUR = EUR2,718,450.14 (matches prior pull). USD-lines EUR EUR2,718,313.33 + EUR-lines EUR136.81 = EUR2,718,450.14.
- Native USD total (USD lines) = $3,180,668.10.
- FX-consistency probe: per-line implied USD/EUR sits 1.15-1.20, drifts by month (Jan 1.173, Feb 1.181, Mar 1.155, Apr 1.171, May 1.168) -> dated conversion of a native USD amount, NOT a flat back-conversion. Confirms USD original.
- Blended rate = 3,180,668 / 2,718,313 = 1.170 USD/EUR (USD-line basis). Sane.

## Result
Per-carrier native USD: OnTrac $1,434,351.60; USPS $683,337.97; FedEx $627,167.10; Asendia USA $435,811.43; TOTAL $3,180,668.10. UPS = $0 native (EUR136.81 / 55 EUR lines only, reported separately).

## Deliverable
- Chart: shipping-agent/scratchpad/20260616-071917--us-origin-freight-by-carrier-native-usd-jan-may-2026.html
- SQL: shipping-agent/scratchpad/20260616-01_us-origin-native-usd-by-carrier.sql
- CSV: shipping-agent/scratchpad/20260616-us-origin-native-usd-by-carrier.csv

## Caveats / open
- 55 EUR lines (UPS, EUR136.81) carry no native-USD value; total is USD-line basis. The USD/EUR blended rate uses the matched USD-line subset (numerator and denominator both exclude the 55 EUR lines) so the rate is clean.
- Chart axis renders a EUR glyph (harness has only a EUR formatter); figures are USD. Flagged in report.
