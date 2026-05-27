# Shipping mart — gold lineage + agent access tiering

**As-of:** 2026-05-27. **Source:** [[S101_612683db_shipping-agent-access-split|S101]].
Domain knowledge from mapping what feeds the gold `shipping_mart` and designing the shipping-agent dual-access setup. Repos: `bi-etl` (DAGs), `picanova/shipping-agent` (the talk-to-your-data agent).

## Gold mart lineage — what feeds `shipping_mart.*`

Gold builds in **`bi-etl/dags/shipping_mart/`** (top-level DAG — moved off the old `enterprise_silver/shipping_data_mart/` path). Four facts: `fact_shipments`, `fact_shipment_cost_summary`, `fact_shipment_orderitems`, `fact_shipment_invoice_lines` (per-carrier provider SQL under `.../sql/providers/`); `fact_truck_charges` out of agent scope.

Source schemas (from FROM/JOIN across the build SQL), all in Redshift db `bi_stage_dev`:
- **`enterprise_silver`** (dominant input) — cleaned per-carrier invoices/charge-lines (`*_invoices`, `dpd_poland_struct1_charge_lines`, `db_schenker_lines`, …), `shipping_charge_bucket_mapping` (**the source of the 11 gold cost buckets**), `dim_shipping_providers`, `map_shipment_key`, `revenues`, `avg_shipping_costs`, `pcs_*` order rollups.
- **`enterprise_bronze`** — source-system orders/shipments: `picaapi_*` (MerchOne), `pict_*` (Picturator), `orwo_*` (Wolfen), `pcs_*` (internal print), `rew_*` (Rewallution); a few still-raw carrier invoices (`fedex_invoicedata_historical`, `dpd_poland_secondstructure_invoice`, `ontrac*`, `landmark*`); static ref (`currency_rates`, `countries_static_iso_map`, `dim_truck_costs`).
- **`dw.dim_products`**, **`sl_gold.dim_date`** — dimensions.
- `poc_dw` is **NOT** read by gold (older parallel cost fact). The raw carrier-CSV ingestion (`bi-etl/dags/shipping_invoice_cost/`) lands into bronze/silver/`poc_landing`/`poc_staging` — upstream of silver, not a direct gold input. (First pass mistakenly read those write-targets as gold's sources.)

## Access tiering — one agent, two tiers

- **Colleagues** — shared `picanova/shipping-agent`, `.env` user `ship_mart_ro` (read-only, gold-only). `how_to.md` rule 10 perimeter holds.
- **Niklavs (maintainer / full-access)** — same repo + a **gitignored `CLAUDE.local.md`** overlay widening scope to silver/bronze/dw/sl_gold, `.env` user `tcg_nfe` (the NFE pipeline user). **Verified 2026-05-27 (redshift MCP): `tcg_nfe` has USAGE+SELECT on `enterprise_silver`/`enterprise_bronze`/`dw`/`sl_gold`/`shipping_mart`** — no new role/grants; `.env` is a user swap (same cluster/db).
- **Design principle:** hard boundary = the DB role (`ship_mart_ro` denies non-gold *at the database*, non-bypassable); the rule-10 perimeter is the UX layer, made **conditional** on the local overlay (no overlay → gold-only default, unchanged for colleagues). Upstream silver/bronze is **off the gold contract** — no bucket collapse, no DQ cleaning, raw vocab — flag it when querying there.

One repo to train/version; per-user access lives in two gitignored files (`.env` + `CLAUDE.local.md`).
