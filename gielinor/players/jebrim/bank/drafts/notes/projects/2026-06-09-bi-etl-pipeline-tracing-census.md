# bi-etl pipeline repo census — 2026-06-09 (tracing map)

> Structured inventory of `Documents/GitHub/bi-etl/` as of 2026-06-09, built by a Jebrim-dwarf read-only recon (sid 91513c92). The **corpus anchor** for the [[bi-etl]] domain — whose job is *trace a warehouse/mart table or column back to the DAG that populates it and the source it comes from*. Live anchor: `bi-etl/CLAUDE.md` (the real repo map; root `README.md` describes only one FB-marketing image).

## What the repo is
Apache Airflow ETL monorepo (~70 domain folders under `dags/`, Python DAGs on K8s pods; per-DAG containers from `dags/**/docker/` Dockerfiles, legacy in `docker_images/`) ingesting 25+ source systems → **Amazon Redshift**.

**Warehouse layers (two generations side-by-side):**
- **Modernized (prefer):** `enterprise_bronze.*` (raw) → `enterprise_silver.*` (clean/conform) → gold (`sl_gold.*`, `ol_gold.*`, `shipping_mart.*`/`shp_gold.*`).
- **Legacy (do-not-extend, data still flows):** `poc_landing → poc_staging → poc_dw`; `sl_bronze/silver`, `ol_bronze/silver`, `bi_stage_dev[_dbo].*`, `dw.*`. `dags/ETL_full_NDW/` decommissioned.
- Bronze-consolidation migration in progress — status authority: `dags/enterprise_bronze/enterprise_bronze_migration.md`.

## DAGs (by theme)
- **Modernized spine:** `enterprise_bronze/` (per-source children: picturator, picaapi, pcs, mws, mixpix, lillestoff, rewallution, orwo_revenue/shipping/pts_cs/cogs, currency_rates, marketing/material/labour_costs, ga4_sessions/purchases, payment_providers, hubspot_tickets, sendmoments, cdc_bridge, channel_reassignment; master `bronze_orchestrator_shop_level.py` 05/09/13/16 UTC) → `enterprise_silver/` (revenues, order_costs/data/addresses, shipping_costs, shipping_pipeline, avg/orderitem_shipping_costs, tracking_orders/orderitems, orwo_cs, `Shipping_Data_Mart/` bronze-dim prep; master `silver_orchestrator_shop_level.py`) → `Shop_Level/gold/` (`sl_gold.*`) + `order_level/gold/` (`ol_gold.*`, no orchestrator — externally triggered).
- **Shipping mart (primary tracing target):** `shipping_mart/` (children `fact_shipments/`, `fact_shipment_orderitems/`, `fact_shipment_invoice_lines/`, `fact_shipment_cost_summary/`, `fact_truck_charges/`, `dim_transit_time/`; `shipping_mart_orchestrator.py` 5 phases, conn `amazon_redshift_airflow_testing`). `shipping_invoice_cost/` = carrier-invoice ingestion (Outlook ×6, SFTP ×3, SharePoint ×3 → `asa_representation` → `FactShipmentCosts_DW_main_job`; entry `shipping_inoices_main.py` [sic]). Plus `expected_shipping_costs/`, `shipping_lookup/`, `shipment_logs/`, `order_trackingnumbers_new/`.
- **Standalone-by-design:** ORWO family (`orwo_dag`, `orwo_navision[_generic]_dag` → Oracle/Navision → `poc_landing.orwo_*`/`sl_bronze.orwo_*`); reporting (`Livedash`, `HR_Reports`, `lucanet`, `AI_Automations/` incl. `fif_ups_orwo`, `advent_calendars`, `alerting`); legacy per-source ingest (freshdesk/caller/chat, bing_ads, ga4, tiktok_costs, emarsys, trusted_shops, mws, wms, payment_providers, rewallution, sendmoments, pi_pcs); legacy dim/fact builders (`dim_products/shops/users`, `orders/orderitems/refunds`); infra (`common/`, `custom_utils/`, `SFTP_TRANSFER/`, `universal_sftp_to_s3/`, `email_to_s3/`, `sharepoint_sync_s3/`, `s3_operations_dag/`).
- **Scratch — do not use:** `Rst.py`, `test.py` (hardcoded SFTP creds — flag), `test1.py`. Archived: `archive_old/`.
- **Naming:** DAG files `{source}_{operation}_{layer}.py`; folder = table/entity; modernized ids `bronze_*`/`silver_*`; header `Layer:` ∈ Bronze/Silver/Gold/Orchestration.

## The two tracing artifacts
1. **DAG header docstring** (spec `.claude/rules/dag-header.md`) — every DAG `.py` opens with `Reads from:` + `Writes to:` table lists, `Layer (schema)`, `Grain`, `ClickUp task`, a `What this does` paragraph. Authoritative because code-colocated. Example `dags/shipping_mart/fact_shipments/shipping_mart_fact_shipments_dag.py`: `Reads from: enterprise_silver.map_shipment_key, … enterprise_bronze.pict_orders …` / `Writes to: shipping_mart.fact_shipments`.
2. **Data-definition markdown** — human-readable column-level lineage. ⚠ **Four near-duplicate folders, typos load-bearing, content differs:** `data definitions/data_definitions.md` (model overview + layer map), `data_definition_claude/` (`data_definitions.md` + **`source_systems.md`** = source→DAG→landing-table inventory + `sl_bronze/silver_tables.md` + `poc_dw_*` refs), `data_definations_claude/` [sic] (**gold + mart defs**: `gold_layer_data_definitions.md`, `shipping_data_mart_definitions.md`, order/item/customer-level tables, `time_windows_and_rfm.md`), `data definitions/` (space, single md). Richest per-column shape: `data_definations_claude/shipping_data_mart_definitions.md` — every column a **`Source`** cell (e.g. `shp_gold.fact_shipments.trackingnumber` → `PICT: pict_trackingnumbers; PICAAPI: picaapi_shipment_trackings; PCS: pcs_sentparcels`; derived cols name the formula; cost cols point at `fact_shipment_cost_summary.total_eur`). Deepest (shipping mart only): `dags/shipping_mart/data_lineage_review.md` — column-by-column source→transform→target with SQL + DQ caveats.

## Supporting dirs
- `custom_utils/s3_utils.py` (clean/move S3, `copy_to_redshift`); DAG-shared utils in `dags/common/utils/connection_utils.py`.
- `scripts/` — maintenance (`generate_gold_layer_definitions.py`, `rename_shipping_schema.py`, `add_shipping_to_xlsx.py`).
- `docs/` (sparse `superpowers/`), `plans/` (e.g. NGE-5699 lucanet allocated-costs), `reports/` (generated `shop_gold_review_*.html`), `alerting_agent/` (standalone Claude DQ-alerting app, separate from `dags/alerting/`).
- `NFE/1_shipping_data_mart/` — the mart **design/investigation** home (CLAUDE.md, data_model.html, model/, investigation/) — mirrors NFE project 1_.
- Root `outlook_to_s3.py` (win32com Outlook→S3, the carrier-invoice Outlook pattern), `data_pipeline_tasks.py` (generic task outline, not live).

## The trace-back workflow (the heart of the domain)
Given e.g. `shipping_mart.fact_shipments.final_shipping_cost_eur` or `enterprise_bronze.ups_orwo`:
1. **Layer from schema prefix** → owning folder (`enterprise_bronze.*`→`dags/enterprise_bronze/`; `enterprise_silver.*`→`dags/enterprise_silver/`; `shipping_mart.*`/`shp_gold.*`→`dags/shipping_mart/`; `sl_gold`/`ol_gold`→`Shop_Level`/`order_level`; legacy `poc_*`/`bi_stage_dev*`/`dw.*`→matching standalone folder).
2. **Find owning DAG** — `Grep "Writes to" + table name across dags/**/*.py`. Folder name usually = table.
3. **Read its `Reads from:`** — one hop back; recurse (each upstream is a `Writes to:` elsewhere).
4. **Column source** — open the layer's data-definition md, read the column's `Source` cell. Shipping mart → `dags/shipping_mart/data_lineage_review.md` for the SQL chain.
5. **External source** — `data_definition_claude/source_systems.md` (system → integration → DAG → landing table; e.g. ORWO → Navision/PTS federated → `orwo_navision_generic_dag` → `poc_landing.orwo_*`).

## Flags
- `shipping_mart.*` == `shp_gold.*` (renamed; `scripts/rename_shipping_schema.py`).
- `enterprise_bronze.ups_orwo` had no exact-name DAG this pass — UPS/ORWO path runs through `AI_Automations/shipping_nfe/fif_ups_orwo_monthly/` + `shipping_invoice_cost/`; grep `Writes to.*ups`.
- Migration in progress — many standalone DAGs still write legacy schemas mid-consolidation.

## Provenance
Read-only dwarf recon, no bi-etl files touched. Anchor for the [[bi-etl]] digest. Next deepen if needed: a column-level shipping_mart lineage walk (the `data_lineage_review.md` is the entry).
