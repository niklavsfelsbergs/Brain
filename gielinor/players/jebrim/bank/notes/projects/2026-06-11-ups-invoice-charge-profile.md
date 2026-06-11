# UPS current-invoice charge profile (ground truth, 12-mo)

As of: 2026-06-08

- Window 2025-06-08 to 2026-06-07, `invoice_source = 'ups'` on `fact_shipment_invoice_lines`: EUR 5.03M net freight, 726,748 shipments, ~2.72M lines. Tax/customs excluded; stream is ~96% TCG, the right tender population.
- Structure: base ~72% (3.64M) / fuel ~13% (669K) / oversize ~9% NET (981K applied minus 528K reversed - UPS claws back ~54% via refund-in-place) / residential ~4% (201K) / tail ~1.4%.
- Effective fuel runs ~18.4% net / ~20.5% gross of base (monthly range 10.9-26.4%), NOT a flat 35% (the card's "35" is a Percent-Off discount on the floating index — [[2026-06-09-ups-old-vs-new-rate-card-diff]]; implied index ~30%, effective ≈ index × 0.65). Caveat: denominator may be wider than UPS's fuel base; question-round item is to confirm the fuel base + index with UPS.
- ~EUR 235K/yr (~4.7% of freight) is billed by charge types NOT in the cost model:
  - Peak/demand ~191K, the biggest gap - hides in 3 places: demand stacked on oversize (~134K), Surge Fee Residential (~49K), Surge/Demand Commercial (8K). Ask UPS for the demand schedule (rates + weeks).
  - Fee tail ~34K: Address/Shipping Correction ~17.6K, Presentation Fee 6.8K, Paper Commercial Invoice 5.5K (avoidable with e-docs), misc.
  - Unclassified 24.5K across 157,179 lines UPS sends with NO description - ask UPS to itemize.
  - Remote Area 2.6K.
- Seasonal Base Rate Surcharge (0.20) not found as a distinct invoice line - confirm with UPS whether it applies on our lanes.
- Always monitor oversize NET, not gross (in-place reversals); verify `length_plus_girth_cm` before treating any Over Maximum charge as legitimate (S124 found sub-threshold parcels charged - dispute basis).
- `ups_orwo` (Wolfen bulk-bill) is a separate stream, excluded from the tender headline; carries VAT as line items, effective fuel ~14%.

Source research: [[2026-06-08-ups-current-invoice-charge-profile]] - full sources and detail there.
