---
domain: bi-etl
title: bi-etl pipeline repo — trace warehouse/mart data back to source
patterns:
  - bi-etl
  - bi etl
  - data pipeline
  - trace back
  - lineage
  - which dag
  - what populates
  - where does this data come from
  - enterprise_bronze
  - enterprise_silver
  - airflow dag
corpus:
  - bank/notes/projects/2026-06-09-bi-etl-pipeline-tracing-census.md
specialist: null
freshness: 2026-06-09
synthesized: 2026-06-09
---

# bi-etl — tracing data pipelines back to source

`Documents/GitHub/bi-etl/` is the **Apache Airflow ETL monorepo** (~70 domain folders under `dags/`, Python DAGs on K8s pods) that ingests 25+ source systems and loads **Amazon Redshift**. This domain's job: given a warehouse/mart **table or column**, find **which DAG populates it and from which source**. Full map: [[2026-06-09-bi-etl-pipeline-tracing-census]]. **The repo map is `CLAUDE.md`, not `README.md`** (root README describes only one FB-marketing image).

## Warehouse layers (two generations live side-by-side)
- **Modernized (prefer):** `enterprise_bronze.*` (raw ingest) → `enterprise_silver.*` (clean/conform) → gold marts (`sl_gold.*`, `ol_gold.*`, `shipping_mart.*` *aka* `shp_gold.*`).
- **Legacy (do-not-extend, data still flows):** `poc_landing → poc_staging → poc_dw`; older `sl_bronze/silver`, `ol_bronze/silver`, `bi_stage_dev[_dbo].*`, `dw.*`. `dags/ETL_full_NDW/` is decommissioned.
- Migration consolidating bronze into `enterprise_bronze` is **in progress** — authority on what's moved: `dags/enterprise_bronze/enterprise_bronze_migration.md`.

| Hop | Folder owning it | Schema written |
|---|---|---|
| source → bronze | `dags/enterprise_bronze/<source>/` | `enterprise_bronze.*` |
| bronze → silver | `dags/enterprise_silver/<entity>/` | `enterprise_silver.*` |
| silver → shop/order gold | `dags/Shop_Level/gold/`, `dags/order_level/gold/` | `sl_gold.*`, `ol_gold.*` |
| silver+bronze → shipping mart | `dags/shipping_mart/` (orchestrator, 5 phases) | `shipping_mart.*`/`shp_gold.*` |
| carrier invoice (Outlook/SFTP/SharePoint) → fact | `dags/shipping_invoice_cost/` | → `fact_shipment_invoice_lines` |

## The two tracing artifacts (use both)
1. **DAG header docstring** (`.claude/rules/dag-header.md`) — every DAG `.py` starts with explicit **`Reads from:` / `Writes to:`** table lists + `Layer`, `Grain`, ClickUp task. Code-colocated → the authoritative "which DAG writes table X from what." Folder name usually = the table.
2. **Data-definition markdown** — column-level lineage with a per-column **`Source`** cell. ⚠ **Typo folder names are load-bearing, content differs:** `data_definations_claude/` [sic] = gold/mart defs (`shipping_data_mart_definitions.md` — richest per-column source map); `data_definition_claude/` = source/silver/bronze (`source_systems.md` = source→DAG→landing-table inventory). For shipping_mart, the deepest is `dags/shipping_mart/data_lineage_review.md` (full SQL chain).

## How to trace a pipeline back (the workflow)
1. **Layer from schema prefix** → the owning folder (`enterprise_bronze.*`→`dags/enterprise_bronze/`, `shipping_mart.*`→`dags/shipping_mart/`, etc.).
2. **Find the owning DAG** — grep DAG headers for `Writes to:` + the table name (`Grep "Writes to" across dags/**/*.py`).
3. **Read its `Reads from:`** — the one-hop-back upstreams; recurse (each is a `Writes to:` elsewhere).
4. **Column-level source** — open the layer's data-definition md, read the column's `Source` cell (formula or upstream physical column).
5. **Original external source** — `data_definition_claude/source_systems.md` maps source system → integration method → DAG → landing table.

## Gotchas
- `shipping_mart.*` == `shp_gold.*` (renamed; `scripts/rename_shipping_schema.py`).
- Carrier invoices land via `shipping_invoice_cost/` + `email_to_s3/`; the UPS/ORWO path runs through `dags/AI_Automations/shipping_nfe/fif_ups_orwo_monthly/` — grep `Writes to.*ups`, don't assume a dedicated bronze DAG.
- `dags/test.py` has hardcoded SFTP creds — flag, don't touch. Scratch: `Rst.py`, `test1.py`.
- The shipping mart **design/investigation** home is `bi-etl/NFE/1_shipping_data_mart/` (mirrors NFE project 1_). The mart *contract* for analysis stays the external `picanova/shipping-agent` reference → [[shipping-mart]].
