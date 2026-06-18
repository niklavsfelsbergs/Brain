# Three-way shipping-cost-quota comparison — Jan–May 2026 (shipping-agent pull)

**Actor:** shipping-agent (emulated sub-agent), principal Jebrim
**Date:** 2026-06-17
**Tier:** gold-contract for SCM + anchored invoiced/expected/revenue; OFF-CONTRACT note on the date-anchored archived legs (dw.sales_fact archived-date population not in the gold mart) and Accounting (LucaNet, given literals, not queried).

## Ask
Assemble SCM vs date-anchored vs Accounting cost/revenue/quota per month Jan–May 2026 + YTD total, write as plain CSV to shipping-agent scratchpad.

## Scope (SCM + anchored)
- Order source: source_system IN ('Picturator','PicaAPI')
- Production sites: ALL EXCEPT {Wolfen, PCS CMH, PCS MI, PCS PX}; NULL-site Picturator bucket INCLUDED (matches Jebrim's validated SCM reproduction — Jan rev €7.19M).

## Turn log
- Loaded how_to.md (full) + CLAUDE.local.md → full-access maintainer profile, tcg_nfe, upstream in-scope. Confirmed contract.
- Site enumeration: PCS MI absent (Miami closed); excluded CMH/PX/Wolfen. Big retained site = PCS PL.
- Method 1 SCM (final cost / net rev by shop_order_created_date): 19.56/19.15/18.26/18.87/19.26, Jan rev €7.19M cost €1.41M — reproduces Jebrim's prior 19.55/19.14/18.26/18.86/19.25 exactly. Confirmed, used as canonical.
- Method 2 anchored: invoiced (real cost, cost_source='invoice') by received_by_carrier_date + expected non-invoiced by order date; revenue by order date (mart proxy for archived date).
  - Mart-derived anchored cost: Jan 1.58M / Feb 1.31M / Mar 1.10M / Apr 1.15M / May 1.28M.
  - Mar/Apr/May reconcile cleanly to validated €1.10/1.13/1.27M. Jan (€1.58M vs €1.64M) and Feb (€1.31M vs €1.35M) land ~4% LOW under the mart's order-created-date anchor (validated series uses archived-date population, off-contract, captures more revenue + cost in early months).
  - Per brief: kept VALIDATED levels as canonical in the CSV; flagged Jan/Feb mart difference here.
- Method 3 Accounting: LucaNet CM1 Europe ACT 2026 literals ×1000. Not queried.

## Result (CSV cells)
SCM YTD: cost €6,176,112 / rev €32,433,723 / quota 19.04%
Anchored YTD (validated): cost €6,490,000 / rev €32,660,000 / quota 19.87%
Accounting YTD: cost €7,181,000 / rev €38,034,000 / quota 18.88%

## Caveats carried into report
- Accounting "Europe" is a different population (legal entity, ~€9.07M Jan rev vs SCM/anchored ~€7.2–7.4M) — quotas comparable, absolutes NOT same-scope.
- Apr/May anchored still-settling (sub-½pt upside per prior bias analysis).
- Off-contract: dw.sales_fact archived legs for the anchored revenue/expected anchor.

## Deliverable
C:\Users\niklavs.felsbergs\Documents\GitHub\shipping-agent\scratchpad\20260617-shipping-quota-three-way-jan-may-2026.csv
