# Shipping-agent pull: characterize BI invoice-number field for QB↔BI US recon

**Spawned by:** Jebrim (US-entity QuickBooks↔BI invoice-number reconciliation, topic 48 / LucaNet-vs-BI arc — sibling: S250_44773956_us-lucanet-vs-bi-reconciliation.md)
**Date:** 2026-06-17
**Tier:** gold-contract (raw carrier invoice_number IS exposed on the gold mart — silver/bronze not needed despite authorization)
**Scope:** production_site IN ('PCS MI','PCS PX','PCS CMH'), destination_country_code IN ('US','CA'), invoice_date 2026-01-01..2026-05-31

## Status
- Located invoice_number: gold `shipping_mart.fact_shipment_invoice_lines.invoice_number` (varchar, nullable in DDL but 100% populated in scope). No silver/bronze reach needed — stayed on contract.
- Carrier vocab (uppercase, on fact_shipments.shipping_provider_group): ONTRAC, FEDEX, USPS, ASENDIA USA, UPS. No LaserShip, no DHL in US scope.
- Grain: lines fact is per-charge-line, many rows per invoice_number. Joined to fact_shipments on shipment_id for scope cols.
- Dedup check: 12 invoice numbers span >1 carrier_group — all are dominant-carrier invoices with a handful of mis-tagged shipment rows (invoice_source consistent within each number). invoice_source is the clean grouping key, not shipping_provider_group.
- Per-source distinct invoice-number counts (invoice-date lens): ontrac 23, fedex 31, usps 137, asendia_usa 20, ups 18. invoice_number 100% populated, zero null/blank everywhere.
- Format flags vs QB: OnTrac + Asendia match QB shape; FedEx in BI is 9-digit pure numeric (925426987) vs QB hyphenated (9-125-58074) — likely hyphens stripped; USPS DOES carry invoice numbers in BI (date-stamped YYYYMMDDNNNN) despite QB having none (Check-paid). Both flagged to Jebrim.

## Result
Characterization returned to principal in chat. No matching performed (per brief). Deliverable chat-only.
