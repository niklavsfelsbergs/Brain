# DHL Sperrgut on Wickels — a template knife-edge, not a cost position

**As of:** 2026-06-11. **Status:** finding, verification open (box widths). **Anchor:** [[S202_276897ca_eu-tender-negotiation-levers|S202]].

## The concrete case

The `dhl_paket` engine charges €20.00 Sperrgut (bulky DE) on every WICKELVERPACKUNG_90x60 parcel because its **template** second-longest side is **60.5 cm** against DHL's 120×60×60 standard envelope (`carriers/dhl_paket/surcharges/bulky_de.py` — trigger is purely dimensional: d_max>120 | d_mid>60 | d_min>60; constant across all parcels → catalog dim, not a measurement). **Ground truth: DHL ships 2,687 of these DE-bound in Q1 and bills Sperrgut on 34 (1.3%, €680)** — the physical box passes DHL's dimensioners.

## Why it does NOT distort the tender headline (keeps)

Since the 2026-06-11 March-anchor (q04c/q09), incumbent keeps are booked at **invoice actuals**; engines price only challenger bids and switches. The 90x60s are DHL keeps at ~€3.73 — the €20 never enters. ([[S175_6c5170d1_routing-cost-basis-review|S175]] had previously accepted this discrepancy at 953 parcels/€19k-Q under the then DHL-engine keep basis; the March-anchor retired it silently.)

## Where it DOES bite

1. **314 Q1 switches to DHL** (206 ex-DBS, 108 ex-UPS) booked at engine face incl. the fee: €6.3k Q1 ≈ **€29k/yr saving understatement** if phantom.
2. **Suppressed challenger wins — the real money.** WICKELVERPACKUNG **80x60 AE**: 17.2k Q1 parcels (~82k/yr) on DPD/UPS at €4.44–5.36; DHL's bid is €23.38 *because its template width is 63 cm* (€3.38 without). If the physical box is ≤60: ~**€110–140k/yr** unlocked. NO DHL billing history exists for this packagetype — UPS's clean record doesn't transfer (UPS thresholds start far above 63). The 100x75 families (template 75) are genuinely over the gate — correctly routed away.

## Verification path (cheapest first)

1. Packaging spec sheet / tape measure: outer width of 80x60 AE (and confirm 90x60 at 60.5 vs 60).
2. If over: 1-day routing trial, DE×80x60-AE cell → DHL (~190 parcels/day; worst case ≈€3.5k vs counterfactual). Readout = DHL invoice oversize lines in the mart for the trial cohort (DHL feeds carry no dims but the charge bucket is visible — same way the 34/2,687 was measured).
3. If ≤60: fix population template dims (not just the engine), re-run cascade — and if the box is genuinely 61–63, a 3cm packaging change is an internal lever worth the same €110–140k/yr with no negotiation.

Same disease class as the zV/DBS template-dims thread ([[2026-06-10-db-schenker-reroute-package-dims-and-savings]]): derived charges off template dims sitting at a threshold. Other engines' dimensional gates not yet class-checked against template values — open sweep candidate.
