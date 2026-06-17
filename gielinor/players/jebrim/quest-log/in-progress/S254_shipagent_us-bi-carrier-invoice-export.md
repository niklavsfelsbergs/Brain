# Shipping-agent trace — US BI carrier-invoice-number export (topic 48)

**Spawned by:** Jebrim, as scoped mart-pull engine.
**Parent quest:** S250_44773956_us-lucanet-vs-bi-reconciliation (topic 48, QB↔BI invoice-by-invoice recon).
**Asked:** clean DISTINCT per-carrier BI invoice-number extract → parquet, for local join against the QB side. No analysis, no QB match.

## Scope used
- Sites: PCS MI / PCS PX / PCS CMH; destination US + CA (matches the US LucaNet-entity filter).
- Lens: invoice-date. Window 2025-09-01 → 2026-05-31 (deliberately wider than Jan–May so late-2025-dated QB bills still appear; avoids false "missing" from timing skew).
- Per-carrier key: invoice_source (NOT shipping_provider_group — per brief, that splits ~12 invoice numbers on tag noise).
- Grain: DISTINCT (invoice_source, invoice_number). Excluded NULL invoice numbers.
- Tier: gold-contract. Both invoice_source + invoice_number live on the invoice-lines fact; join to shipments only for the site/destination scope filter on shipment_id.

## Result
- Rows written: 370.
- Per-source distinct invoice numbers: usps 183, fedex 74, asendia_usa 41, ontrac 40, ups 28, dhl_america 3, dpd_poland_struct1 1.

## Checks
- Per-source counts from the parquet match an independent summary query exactly (sum 370).
- line_count total 1,508,022 = 1,543,063 in-scope lines − 35,041 null-invoice-number lines (exact reconciliation).
- Grain-distinct assertion held; date span inside window; parquet round-trip read OK (370×5).

## DQ caveats (flagged to principal)
- ~2.3% of in-scope charge-lines (35,041 / 1,543,063) carry a NULL invoice number — excluded (unmatchable to a QB bill). No empty strings, no null sources/dates otherwise.
- dpd_poland_struct1 (1 invoice) and dhl_america (3) look like minor/edge sources for a US/CA scope — left in per the "clean extract of whatever's in scope" brief; principal may want to ignore on the QB join.
- Schema-doc nit: the spawn brief said invoice_source lives on fact_shipments; it actually lives only on the invoice-lines fact. No impact (key + invoice_number on same table); flagging for the maintainer.

## Deliverable
C:\Users\niklavs.felsbergs\Documents\GitHub\bi-analytics-main\NFE\shipping_topics\48_US_Lucanet_vs_BI\bi_carrier_invoices_2026.parquet
