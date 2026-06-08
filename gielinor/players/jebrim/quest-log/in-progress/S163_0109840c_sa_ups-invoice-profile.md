# S163 — shipping-agent: UPS current-invoice charge profile (2026-06-08)

Spawned by Jebrim for the EU-tender UPS contract assessment. Profile our current UPS invoices over gold `shipping_mart`: full charge-bucket vocabulary, effective fuel %, surcharge presence, and the reconciliation verdict (what's billed that our UPS cost model does NOT explain).

- Loaded mart contract by construction: how_to.md §0 + reference/{mart-contract,tables,known-dq}.md. Gold-only perimeter, 4 facts, no joins outside `shipping_mart`. Key UPS facts noted: refund-in-place reversals (negatives keep bucket), LPS/OML oversize banding, Manual Bill 838-prefix = customs/duty not freight, exclude tax/customs from freight.
- UPS keyed as `shipping_provider_group = 'UPS'` (uppercase). All-time: 2,384,136 shipments.
- Window: invoice_date 2025-06-08 .. 2026-06-07 (12mo, max invoice_date = 2026-06-07). UPS invoice_sources in window: `ups` (2.72M lines), `ups_orwo` (415K lines, Wolfen bulk-bill — separate vertical).
- Full join fact_shipments x invoice_lines aborts (query timeout on large scan) — profiling off invoice_source on the lines table directly, validating against spine separately.
- `ups` bucket profile (net EUR, window): base_rate €3.64M / fuel €669K / oversize €452K net (BUT -€528K reversed -> gross applied much higher) / residential €201K / customs €53K(excl) / other €34K / unclassified €24.5K / peak_demand €7.96K / remote_area €2.6K / tax €811(excl).
- Description-level pulled. Notables for reconciliation: oversize bucket carries Demand-Surcharge-* (peak stacked on oversize); `other` carries Presentation Fee, Paper Commercial Invoice Surcharge, UPS Access Point Hold, Saturday Delivery, Monopoly Fee, Shipping Correction Fee, Address Correction; residential carries Surge Fee-Residential (peak); peak_demand = Surge/Demand Commercial. unclassified desc = literal 'Unclassified'.
- unclassified bucket = 157,179/157,183 lines have NULL charge_description; €24,480. Genuine unknown — UPS sends lines with no description text.
- FUEL: effective fuel as % of base_rate = ~18.4% net / ~20.5% gross over window; by month ranges 10.9%-26.4%, mostly 17-21%. NOT ~35%. Material finding: contract's flat 35% >> what we're actually billed (different/narrower denominator on UPS side, or negotiated effective ~20%). Flag as empirical check.
- Spine validation: invoice_source='ups' lines -> 100% shipping_provider_group='UPS' (May sample). 'ups' stream is ~96% TCG (Picturator+PicaAPI), ~2.4% ORWO, trace PCS. Distinct UPS shipments with lines in window: 726,748. Separate ups_orwo = Wolfen bulk-bill, reported separately.
- ups_orwo profile: base €328K / tax €47K(excl, DHL-style VAT lines) / fuel €46.5K / other €18.6K / residential €6.8K / customs €5.3K / peak €414 / unclassified €239 / oversize €95 / remote €34.
- Freight total (ups, tax/customs excluded) = €5,032,182 / 12mo. Oversize gross €980,543 applied, -€528,384 reversed, €452,159 net (~54% clawed back, refund-in-place). Manual Bill 838-prefix = 10,213 lines (customs/duty/VAT, correctly excluded). Distinct invoices 756.

## Reconciliation verdict
- Explained by cost model (~95.3%, ~€4.80M): base (incl Economy DDP), fuel, flat residential, oversize (LPS/OML/AddlHandling).
- NOT explained (~€235K / ~4.7%): (1) PEAK/DEMAND ~€191K — biggest gap, stacks inside oversize (€134K Demand-Surcharge-*), residential (€49K Surge-Residential), + standalone Commercial €8K; (2) `other` fee tail €34K — Address/Shipping Correction, Presentation Fee, Paper Commercial Invoice Surcharge, Access Point Hold, Saturday Delivery, Monopoly; (3) unclassified €24.5K (no description — genuine unknown); (4) Remote Area €2.6K; (5) seasonal Base-Rate-Surcharge €0.20 not found as distinct line.
- FUEL: effective ~18-21% of base (window ~18.4% net / 20.5% gross), NOT the contract's flat 35%. Moves monthly (index, not flat). Flag: ask UPS for the fuel base/index — measured well below quoted 35%.

## Deliverable + boundary note
- Write boundary BLOCKED the brief's research/ path (shipping-agent brain-internal write surface = quest-log + inventory only). Per discipline, substantive deliverable lands OUTSIDE the brain. Full profile written to: C:\Users\niklavs.felsbergs\Documents\GitHub\shipping-agent\workbench\analysis\20260608-ups-invoice-charge-profile\ups-current-invoice-charge-profile.md
- Open for principal: if the profile must live at the brief's research/ path, the principal (not the shipping-agent) places it there — it's a player-namespace write gated to alching/principal, not a sub-agent write.
