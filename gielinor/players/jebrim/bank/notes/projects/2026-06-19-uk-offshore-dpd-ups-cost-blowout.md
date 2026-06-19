# UK offshore cost = a DPD/UPS blowout, NOT a market rise; mainland is flat

**Status:** draft -- harvest at alching. From [[S277_47bed7aa_uk-yodel-negotiation-levers]]. Live mart, Q1 + monthly Nov2025-May2026, TCG GB, invoiced.

"UK cost went up in March" is true on the **whole book** (~EUR 5.85 Nov-Feb -> ~EUR 6.22 Mar-May) but the
driver is **offshore zips, not the market.** Decomposed:

- **Base is flat** all months (~EUR 3.44/pcl) -- no GRI / rate-regime change.
- March bump = a one-month **truck** spike (EUR 1.98->2.38, back to ~2.1 by Apr).
- Apr-May rise = **fuel** (EUR 0.07->0.31, volatile) + small oversize creep.
- Carrier mix shifted FAVORABLY (DPD 52%->31%, Maersk 28%->57%), yet DPD's own per-parcel jumped **+34%**
  (EUR 6.05->8.09) -- the mix shift masked a bigger DPD increase.

**Excluding offshore zips, mainland is flat:** EUR 5.64 (Jan-Feb) vs 5.61 (Mar-May); Apr-May actually BELOW
Jan-Feb. The entire "UK rose" signal is offshore, where per-parcel **~doubled Apr-May (EUR 9.7 -> 21)**.

Offshore by carrier (May): **DPD UK EUR 26.44/pcl, UPS EUR 28.78, MAERSK EUR 8.22.** Offshore rides the
expensive carriers; Maersk does offshore at ~1/3 the cost. **Offshore is ~neutral between today and the Yodel
offer** (existing ex-truck GBP 33,612 vs Yodel GBP 35,216) because the incumbent already pays a 2x offshore
base premium (EUR 7.02/pcl vs EUR 3.28 mainland) -- buried in base, billed ~EUR 0 as "remote".

**Consequences:** (1) Q1 is a fine mainland baseline for the Yodel comparison -- mainland is stable, the rebase
concern was an offshore artifact. (2) The real offshore win is moving offshore volume off DPD/UPS onto Maersk
(EUR 8/pcl) -- an ops fix, parked out of the tender. (3) Cost basis: use `real_shipping_cost_eur` (NOT `_local`
-- mixed GBP/EUR); truck is baked into `_eur` = `fact_shipment_cost_summary.truck_charges_eur`.
