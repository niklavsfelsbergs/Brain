# S246 — US LucaNet-vs-BI: final vs invoiced cost, 3-way (corrected scope)

**Asked:** Per carrier × month (Jan–May 2026) + totals + YTD, show FINAL cost, INVOICED cost,
and INVOICED % (euro-weighted + count-weighted). Corrected NA scope. Order-month lens, EUR.

**Scope used (canonical, as given):**
- production_site IN ('PCS MI','PCS PX','PCS CMH')
- destination_country_code IN ('US','CA')
- shop_order_created_date in [2026-01-01, 2026-06-01)
- Lens: order-month (shop_order_created_date). Currency: EUR (mart native).
- Tier: gold-contract (shipping_mart.fact_shipments only). No CLAUDE.local — gold-only perimeter.

**Invoiced-cost column resolved:** real_shipping_cost_eur ≡ final_shipping_cost_eur WHERE cost_source='invoice'.
Probe proved exact equivalence: real populated iff cost_source='invoice' (real_where_not_invoice=0,
cnt_real_notnull = cnt_invoice = 264,153, zero invoice rows with NULL real). Used real_shipping_cost_eur.

**Headline / ties (all confirmed):**
- Final YTD = €2,709,610.57 — ties to anchor exactly.
- Invoiced YTD = €2,652,868.62 → euro-weighted invoiced % = 97.90%; count-weighted = 98.73%.
- Per-carrier final YTD: OnTrac €1,208,596.47 ✓ / USPS €594,813.51 ✓ / FedEx €547,997.62 ✓ / Asendia €358,079.38 ✓.
  (UPS €123.60 / OTHER + null carrier €0 uncosted — 9 + 9 stray shipments.)

**May flag:** confirmed soft — May euro-weighted invoiced % = 95.09% (only sub-96 month).
Driver is FedEx (May 83.65% €-wt, vs ~98% other months) and Asendia (94.86%); OnTrac/USPS still ~98–99.7%.
Expected invoice-lag on the trailing month, not a coverage defect.

**Deliverable:** chat-only (tidy long table + matrices + exact SQL returned to principal). No chart (as asked).

**Status:** complete — ties verified, equivalence proven, May flagged. Returned to principal.
