# Trace — shipping-agent: what the `expected` model understates (non-ORWO)

**Spawned by:** Jebrim · **Date:** 2026-06-19 · **Tier:** gold-contract (`shipping_mart`, ship_mart_ro via MCP)

## Asked
Non-ORWO (TCG) population: invoiced/real cost runs above the `expected` estimate. What is the estimate understating, and does the gap survive the immature-month confounder (here direction is invoiced > expected)?

## Scope used
- Population: `source_system <> 'ORWO'` (= Picturator 1.34M + PicaAPI 348K + PCS 3.6K in 2026; Rewallution absent). ~92% is SCM-TCG; PCS sliver immaterial. Flagged: this is broader than SCM's strict TCG (Picturator+PicaAPI).
- Lens: ORDER-MONTH (`shop_order_created_date`). Clean signal measured on `cost_source='invoice'` rows where `expected_shipping_cost_eur IS NOT NULL` (~98% of invoiced rows; ~2% lack expected).
- Mature months: Jan–May ~91–95% invoiced. June immature (~33%) — excluded from the verdict.

## Turn log
- cost_source split by month done — June is the confounder (33% invoiced), Jan–May mature.
- Per-shipment real−expected residual: mature months hold +5% to +7.4% (Apr 1.074, May 1.073). Gap SURVIVES maturity. NOT a selection artifact.
- Carrier split (Apr): UPS dominates (€50.9K, +13%); DPD UK +43%; DB Schenker +18%; Asendia USA +22%. DHL/Maersk/OnTrac/USPS/FedEx ~flat.
- Decisive cut: oversize-charged parcels (2.9% of vol) carry 88% of the residual (Apr 1.737, May 1.984). Non-oversize ~flat (May 0.997). Reproduces on two mature months.
- Market: US ~flat (1.005, well-calibrated). EU +7%. "Other" = Australia lane (expected ≈ €0, flat per-country rate missing).
- Sum-invariance confirmed: 11 buckets == total_eur == real to the cent (€1,775,198.61).

## Headline
The `expected` model is calibrated on average but **dimension-blind**: a flat per-country scalar prices the 97% ordinary parcels correctly and systematically under-prices the ~3% oversize/large-package tail. The aggregate +5–7% understatement is ~entirely that tail. Top names: UPS oversize+fuel, DPD UK, the Australia lane (no rate).

## Caveats
- Gold-contract only. Residual measured on ~98% of invoiced rows that carry expected.
- "much higher" framing is the immature-month / full-population read; like-for-like understatement is moderate (+5–7%).
- Deliverable: chat-only (raw findings to Jebrim).
