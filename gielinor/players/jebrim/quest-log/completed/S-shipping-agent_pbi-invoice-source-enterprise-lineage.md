# Shipping-agent pull: PBI "Shipping Invoice Details" — old source → enterprise-layer mapping

**Spawned by:** Jebrim (NFE work). Read-only lineage/mapping.
**Tier:** UPSTREAM / off the gold contract (CLAUDE.local.md full-access via tcg_nfe; enterprise_bronze + enterprise_silver in scope). Curated gold guarantees do NOT apply — raw vocab, no bucket collapse, no DQ guarantees.

## Sources used
- shipping-agent/how_to.md (rules), CLAUDE.local.md (full-access schema scope)
- DAG provider SQL: bi-etl/dags/shipping_mart/fact_shipment_invoice_lines/sql/providers/{dhl,ups,ups_orwo,dpd_poland_struct1,dpd_uk,fedex,yodel,dhl_orwo,ontrac}.sql
- LIVE Redshift MCP: information_schema across enterprise_bronze / enterprise_silver / poc_landing / bi_stage_dev_dbo / bi_asa_dev_dbo / dw / sl_gold

## Turn log
- Read rulebook + local overlay → confirmed upstream tier authorized.
- Read 9 DAG provider SQLs → got the mart's authoritative enterprise input table names per carrier.
- Live-listed enterprise_bronze/silver invoice tables → every carrier has a home in BOTH layers; UPS Claims has NO enterprise table.
- Column-count + set-diff old-landing vs bronze-mirror: DHL/UPS-temp1/DPD-PL-raw/DPD-UK/DHL-ORWO/OnTrac/FedEx all COLUMN-PERFECT verbatim mirrors (0 cols missing). Yodel bronze missing 2 cols (dw_sourcecode, net_amount_eur).
- Silver vs old DHL columns: heavy rename (invoicenr→invoiceid, identcode→trackingnumber, pudate→pu_date, wgt→weightkg, chargeamount/total→netcosts). Silver = column drift; bronze = no drift.
- Row counts: all new tables populated. ups_orwo bronze=silver=246,010.
- pcsu_* has NO enterprise equivalent named pcsu_*; the enterprise family is pcs_* (rename pcsu_→pcs_).

## Headline
Two viable repoints per carrier: (a) enterprise_bronze verbatim mirror = ZERO M rework (same column names), (b) enterprise_silver cleaned = renamed cols, needs remapping. Recommend bronze mirror for a like-for-like repoint. UPS Claims stays (no enterprise home, and it's a claims table not freight invoice). Supporting joins: pcsu_→pcs_ is a real move; dw.* and ecb stay.

## Deliverable
Returned in final message to Jebrim (mapping table + column-drift + supporting-joins verdict). No file outside brain written.
