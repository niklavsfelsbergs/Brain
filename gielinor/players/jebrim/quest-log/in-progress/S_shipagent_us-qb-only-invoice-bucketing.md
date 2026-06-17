# S (shipagent dwarf) — US QB-only invoices: why-absent bucketing (topic 48)

**Asked:** For the 78 QB-only carrier invoice keys (QuickBooks GL, not in BI gold mart under US-entity scope; 37 fedex / 41 asendia_usa, 2026 Jan–May), look each up in `shipping_mart.fact_shipment_invoice_lines ⋈ fact_shipments` with NO scope filter. Classify A (not in mart / genuine gap) vs B (intl dest) vs C (other site) vs D (in-scope, other exclusion). Tell Jebrim whether the ~$109k Asendia + ~$9k FedEx tail is "BI missing shipments" or "legitimately outside US/CA quota scope."

**Scope/tier:** gold-contract. Off-scope lookup (no site/dest/date filter) but stayed inside `shipping_mart`. Match on `REPLACE(UPPER(invoice_number),'-','') = k`.

**Status trace:**
- Loaded 78 keys from qb_only_invoices.csv. Note 5 asendia keys are `26M######` not `26B` (task said 26B only).
- MCP validator rejected multi-`LISTAGG(DISTINCT)`; rewrote with conditional COUNTs.
- Key correction: `found` flag must come from invoice-lines side, NOT post-shipments-join shipment_id (LEFT JOIN to fact_shipments nulls it when shipment row missing). Re-derived.
- Found a 3rd presence state: FedEx invoice lines present with `shipment_id = NULL` (unlinked cost rows, source_table=enterprise_bronze.fedex_invoicedata_historical) — line exists, no shipment to scope on.

**Result (all reconcile to 78 keys / full $ tail):**
- Asendia: 41/41 NOT in mart invoice lines at all → bucket A. $110,252.93. GENUINE GAP.
  - Mart DOES carry asendia_usa, same 26B###### format, 108 distinct invs = weekly CONSOLIDATED freight invoices (thousands of lines each, all shipment-linked). QB-only keys are the supplementary/surcharge invoices issued between the weekly freight ones — never ingested.
- FedEx: 6 not in mart ($4,204.78, bucket A) + 25 unlinked-no-shipment ($3,539.41, A2 — lines exist, shipment_id NULL) + 6 international-dest linked ($1,263.84, bucket B; dests AU/GB/FR/IE/NZ/PR from PCS CMH — correctly out of US/CA scope, incl. PR coded separately from US).
- Buckets C (other site) and D (in-scope, other exclusion): 0 keys.

**Headline:** The ~$109k Asendia tail = BI is MISSING those invoices (bucket A, not a scope artifact). FedEx ~$9k splits: ~$7.7k genuinely absent/unlinked (A+A2), ~$1.3k legitimately out-of-scope intl exports (B).

**Caveats:** A2 (unlinked FedEx lines) means the cost is in the mart invoice-lines fact but unattributable to a shipment — distinct from a pure gap; flagged for Jebrim. Asendia weekly-consolidation hypothesis is strongly evidenced by the invoice-number cadence but the exact ingestion filter wasn't traced into silver/bronze (off gold contract).
