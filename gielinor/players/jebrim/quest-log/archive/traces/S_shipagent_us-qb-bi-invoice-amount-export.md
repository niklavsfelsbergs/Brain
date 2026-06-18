# shipping-agent: US QB↔BI per-invoice AMOUNT export (topic 48)

**Spawned by:** Jebrim. **Tier:** gold-contract. **Date:** 2026-06-17.

## Ask
Export per-invoice AMOUNT totals from the BI gold mart so Jebrim can join locally to QuickBooks (USD) bill totals. Invoice-NUMBER match already done (sibling trace); this is the amount side. NO analysis, no QB match.

## Scope (identical to prior NUMBER extract)
- `fact_shipment_invoice_lines` ⋈ `fact_shipments` on shipment_id (inner)
- production_site IN ('PCS MI','PCS PX','PCS CMH') AND destination_country_code IN ('US','CA')
- invoice-date lens, window 2025-09-01 .. 2026-05-31, invoice_number NOT NULL
- RAW full invoiced charge — every charge line, all buckets. NO cost-basis filter (not real_shipping_cost, not cost_for_routing).
- Grain: one row per (invoice_source, invoice_number).

## Turn log
- Verified columns: scope cols (production_site, destination_country_code) on fact_shipments; invoice fields + charge_amount_local/_eur/currency_code on lines. ✓
- Probe: 1,508,022 scoped lines, 370 distinct invoices, 0 invoices mix currencies, 184 null charge_amount_local lines (all EUR sources), 0 null EUR.
- Inner join drops ~1% null-shipment_id lines globally — they carry no site/destination, cannot be scoped, correctly excluded.
- Per-invoice aggregate ran (370 rows); MCP token cap exceeded → result saved to disk, parquet built from it via polars.
- Reconciled parquet vs probes: lines 1,508,022 ✓, invoices 370 ✓, mixed-cur 0 ✓, per-source line counts ✓.

## Result (per invoice_source)
| source | inv | lines | sum_local | sum_eur | cur |
|---|---|---|---|---|---|
| ontrac | 40 | 935,082 | 2,723,787.57 | 2,330,664.54 | USD |
| fedex | 74 | 274,683 | 1,258,934.19 | 1,077,530.48 | USD |
| usps | 183 | 162,161 | 1,241,449.83 | 1,061,758.52 | USD |
| asendia_usa | 41 | 135,932 | 999,525.76 | 855,625.36 | USD |
| ups | 28 | 134 | (null local) | 378.69 | EUR |
| dhl_america | 3 | 27 | (null local) | 237.00 | EUR |
| dpd_poland_struct1 | 1 | 3 | 3.89 | 3.89 | EUR |

Grand: local 6,223,701.24 / eur 5,326,198.48 / 1,508,022 lines / 370 invoices.

## DQ caveats
- 4 USD volume carriers (ontrac, fedex, usps, asendia_usa) = QB-comparable USD; sum_charge_local is USD, 0 nulls.
- 3 stray EUR sources (ups 28, dhl_america 3, dpd_poland_struct1 1) match site+dest filter — likely cross-region/misrouted. sum_charge_local null for ups+dhl (32 inv... actually 31), only EUR populated. Flagged via currency_codes col.
- No invoice mixes currencies (n_currencies=1 for all 370).

## Deliverable
- `bi-analytics-main/NFE/shipping_topics/48_US_Lucanet_vs_BI/bi_carrier_invoice_amounts.parquet`
- SQL: same dir `sql/bi_carrier_invoice_amounts.sql`
