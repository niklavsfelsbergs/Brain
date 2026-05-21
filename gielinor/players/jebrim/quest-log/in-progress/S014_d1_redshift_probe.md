# S014-D1 — Redshift probe (Shipping Data Mart, 2026-05-21)

## Summary

All 8 expected silver mart tables exist; `dim_carrier_sla` does **not** exist (so the live mart is 8 tables, not 9). All 5 source systems (Picturator, PicaAPI, PCS, Rewallution, **ORWO**) are landed in `fact_shipments` and `fact_shipment_orderitems` — ORWO is the largest item-count source (90M of 122.7M orderitem rows) but has near-100% NULLs on V1-critical shipment columns (destination_country, weight, timestamps, costs, currency, truckload, net_revenue). No shipping gold schema exists: `sl_gold` is present but is a shop-revenue mart (`fact_shop_daily`, `dim_shops`), not shipping. FK joinability is 100% from `map_shipment_key` to fact_shipments / orderitems / cost_summary; invoice_lines is 99.18% (0.82% unmapped or NULL `shipment_id`).

## Schema discovery

Schemas matching `%gold%`, `%shipping%`, `sg_%`:

- `ol_gold` — order-line gold (fact_order, order_marketings, order_shipping_costs, revenue_order_daily, lucanet_costs). Not the shipping mart's gold layer.
- `sl_gold` — present, but contents are **shop-level revenue / marketing**: `dim_currencies` (0 rows), `dim_date` (6,940), `dim_shops` (39,678), `fact_shop_daily` (332,600). Columns confirm it: `gross_revenue_eur`, `marketing_costs_eur`, `ga4_visits`, `adwords_costs_eur`, etc. **Not a shipping gold layer.**
- `shipping_costs` — schema exists; contains `actual_shipping_costs_fedex|ontrac|usps` + `expected_shipping_costs_*`. This is the legacy carrier-rate-card / expected-cost lookup space, not a gold mart.
- No `sg_*` schemas.

**Conclusion:** There is no shipping gold schema in Redshift today. If a finishing-touch gold layer is supposed to land for V1, it has not landed yet.

Other shipping-relevant objects in `enterprise_silver` outside the 8 probe targets: `avg_shipping_costs`, `order_shipping_costs`, `orderitem_shipping_costs`, `pcs_production_pot_truckload`, `pcs_shippingproviders`, `pcs_truckloads`, `picaapi_shipments`, `picaapi_shipping_providers`, `pict_shippingproviders`, `shipping_charge_bucket_mapping`, `shipping_cost_ratios`, `shipping_costs`, `shipping_pipeline_tracking`, `shipping_tracking_enriched`, `tmp_factshipmentcosts_no_truck`. Several are staging/source-mirror; `tmp_factshipmentcosts_no_truck` is presumably a transient build artifact.

## Per-table probe

### enterprise_silver.map_shipment_key

- Exists: **yes**
- Rows: **18,631,411**
- Columns: `shipment_id` bigint NOT NULL, `trackingnumber` varchar NOT NULL, `shop_ordernumber` varchar NOT NULL, `source_system` varchar NOT NULL, `source_order_id` bigint, `updated_at` timestamp, `dw_timestamp` timestamp, `order_created_date` date, `shippingprovider_extkey` varchar.
- source_system breakdown: Picturator 13,046,581 · PicaAPI 3,013,189 · ORWO 2,506,429 · PCS 59,021 · Rewallution 6,191. All 5 expected values present; no unexpected values.
- Recency: `MAX(updated_at)` and `MAX(dw_timestamp)` are **NULL across the entire table** (defaults exist but are not applied — rows inserted with explicit NULL). `MAX(order_created_date) = 2026-05-21`.
- NULL%: shipment_id 0% (NOT NULL).
- Surprises: `updated_at` / `dw_timestamp` entirely NULL despite having `now()` defaults. ETL writes these as NULL.

### enterprise_silver.fact_shipments

- Exists: **yes**
- Rows: **18,463,257** (~168k fewer than MSK — some MSK keys without a fact_shipments row; likely PCS / partial sources)
- Columns: 64 columns. PK `shipment_id` (unique index). Includes destination geography, package dimensions, lifecycle timestamps (`shop_order_created_ts`, `received_by_carrier_ts`, `delivered_by_carrier_ts`, `truckload_assigned_ts`, `truckload_closed_ts`), cost-roll-up columns (`real_shipping_cost_eur`, `expected_shipping_cost_eur`, `avg_shipping_cost_eur`, `final_shipping_cost_eur`), `net_revenue_eur`, `cost_source`, `currency_code`, `truckload_id`, etc.
- source_system breakdown: Picturator 13,030,699 · PicaAPI 2,860,995 · ORWO 2,506,429 · PCS 58,943 · Rewallution 6,191.
- Recency: `MAX(updated_at) = 2026-05-21 07:35:24`. `MAX(shop_order_created_date) = 2026-05-21`. Fresh.
- NULL% by source_system (V1-critical):

  | source_system | n | dest_country | weight_kg | recvd_ts | delivered_ts | final_cost | real_cost | cost_source | currency_code | truckload_id | net_revenue |
  |---|---|---|---|---|---|---|---|---|---|---|---|
  | ORWO | 2,506,429 | 100.00 | 47.06 | 100.00 | 100.00 | 100.00 | 100.00 | 100.00 | 100.00 | 100.00 | 100.00 |
  | PCS | 58,943 | 0.00 | 0.04 | 100.00 | 100.00 | 100.00 | 100.00 | 100.00 | 100.00 | 69.43 | 100.00 |
  | PicaAPI | 2,860,995 | 0.03 | 0.97 | 77.62 | 79.17 | 100.00 | 100.00 | 100.00 | 100.00 | 38.48 | 1.13 |
  | Picturator | 13,030,699 | 0.00 | 14.68 | 33.39 | 35.87 | 100.00 | 100.00 | 100.00 | 100.00 | 51.74 | 0.40 |
  | Rewallution | 6,191 | 0.00 | 100.00 | 100.00 | 100.00 | 100.00 | 100.00 | 100.00 | 100.00 | 100.00 | 0.00 |

- Surprises:
  - **`final_shipping_cost_eur`, `real_shipping_cost_eur`, `cost_source`, `currency_code` are 100% NULL across every source_system.** The cost-rollup columns on `fact_shipments` appear to be entirely unpopulated; actual cost data lives in `fact_shipment_cost_summary` / `fact_shipment_invoice_lines`. Either these columns are deprecated-but-still-defined or the cost merge step has not been wired.
  - ORWO is fully landed key-wise (every shop_order has a shipment row) but every shipment column except `weight_kg` (53% populated) is NULL. ORWO source has shipment **identities** but not shipment **attributes**.
  - PicaAPI is missing carrier received/delivered timestamps for ~78% of rows; Picturator missing ~34%. PCS and ORWO are 100% NULL on these (probably never had them in source).
  - `net_revenue_eur` is well-populated on the two big sources (Picturator 99.6%, PicaAPI 98.9%) and Rewallution (100%), but 100% NULL on ORWO and PCS.

### enterprise_silver.fact_shipment_orderitems

- Exists: **yes**
- Rows: **122,689,685**
- Columns: `shipment_id` bigint NOT NULL, `source_system`, `source_order_id`, `source_order_item_id`, `sku`, `articlenumber`, `quantity`, `revenue_eur`, `product_key` bigint, `option_key` bigint, `format_key` bigint, `updated_at`, `dw_timestamp`, `is_reorder` boolean. No index/PK shown.
- source_system breakdown: ORWO **89,987,048** · Picturator 29,257,239 · PicaAPI 3,396,166 · PCS 41,032 · Rewallution 8,200. **ORWO dominates this table** (73% of all orderitem rows).
- Recency: `MAX(updated_at) = 2026-05-21 07:03:32`.
- NULL%:

  | source_system | n | revenue_eur | product_key | shipment_id |
  |---|---|---|---|---|
  | ORWO | 89,987,048 | 100.00 | 100.00 | 0.00 |
  | PCS | 41,032 | 100.00 | 1.96 | 0.00 |
  | PicaAPI | 3,396,166 | 0.01 | 0.03 | 0.00 |
  | Picturator | 29,257,239 | 0.13 | 0.08 | 0.00 |
  | Rewallution | 8,200 | 0.00 | 100.00 | 0.00 |

- Surprises:
  - **ORWO orderitems have 100% NULL `revenue_eur` AND 100% NULL `product_key`.** ORWO contributes 90M rows but none have a product lineage tie or revenue figure. Picturator/PicaAPI orderitems are essentially fully populated.
  - PCS orderitems have 100% NULL `revenue_eur` as well, only 1.96% NULL `product_key`. PCS is a cost-data-only source historically — orderitem-shape revenue not flowing.
  - Rewallution and PCS have 100% NULL `product_key` and 100% NULL `product_key` respectively for the parts they're missing — fine for the small footprint, but means downstream product-attribute joins exclude them.

### enterprise_silver.fact_shipment_invoice_lines

- Exists: **yes**
- Rows: **55,458,803**
- Columns: `shipment_id` bigint NULLABLE, `trackingnumber`, `shop_ordernumber`, `invoice_source`, `shippingprovider_extkey`, `invoice_number`, `invoice_date`, `shipment_date`, `currency_code`, `charge_description`, `charge_bucket`, `charge_amount_local`, `charge_amount_eur`, `billed_weight`, `updated_at`, `dw_timestamp`, `charge_description_english`. **No `source_system` column.**
- source_system breakdown: N/A (no column).
- Recency: `MAX(updated_at) = 2026-05-21 08:53:22`.
- NULL%: shipment_id **0.82%** NULL · currency_code 0.00% NULL.
- Surprises:
  - This table is keyed on invoice charges, not on source system. The `invoice_source` and `shippingprovider_extkey` are the dimensional anchors.
  - 0.82% of invoice lines have NULL `shipment_id` — these are charges that couldn't be matched to a tracking number; will not join to MSK or fact_shipments (see FK section).

### enterprise_silver.fact_shipment_cost_summary

- Exists: **yes**
- Rows: **12,039,076** · Distinct shipment_id: 12,039,076 (one row per shipment).
- Columns: `shipment_id` bigint NOT NULL, `billed_weight`, `total_eur`/`total_local`, `base_rate_eur`/`local`, `truck_charges_eur`/`local`, `fuel_surcharge_eur`/`local`, `remote_area_charges_eur`/`local`, `peak_demand_charges_eur`/`local`, `oversize_overweight_eur`/`local`, `residential_eur`/`local`, `discounts_eur`/`local`, `credit_note_eur`/`local`, `other_eur`/`local`, `unclassified_eur`/`local`, `tax_eur`/`local`, `customs_duties_eur`/`local`, `updated_at`, `dw_timestamp`. **No `source_system`, no `currency_code`.**
- Recency: `MAX(updated_at) = 2026-05-21 07:27:01`.
- NULL%: shipment_id 0% (NOT NULL).
- Surprises:
  - 12.0M cost summaries vs 18.5M fact_shipments → ~6.4M shipments have no cost summary row (i.e., no invoice data). Probably ORWO and the older / no-invoice cohort.
  - No `currency_code` column on this table (cost-summary is pre-converted; EUR + local pair carried per bucket).

### enterprise_silver.fact_truck_charges

- Exists: **yes**
- Rows: **2,317** (truckload-grain, not shipment-grain)
- Columns: `truckload_id` varchar NOT NULL, `departure_date`, `departure_ts`, `production_site`, `truck_provider`, `cost_per_truck_eur`, `cost_per_parcel_eur`, `shipment_count_allocated`, `data_source`, `updated_at`, `dw_timestamp`, `cost_per_parcel_eur_smoothed`. No `source_system`, no `shipment_id`.
- Recency: `MAX(updated_at) = 2026-05-21 07:26:06`.
- NULL%: truckload_id 0% (NOT NULL).
- Surprises: Tiny table (2.3k rows); aggregates by truckload. `cost_per_parcel_eur_smoothed` suggests a moving-average / outlier-treatment column was added.

### enterprise_silver.dim_shipping_providers

- Exists: **yes**
- Rows: **326**
- Columns: `shipping_provider_id`, `shippingprovider_extkey`, `shippingprovider_group`, `service_type`, `truck_provider`, `has_truck_cost`, `updated_at`, `dw_timestamp`, `source_system`.
- source_system breakdown: Picturator 124 · PicaAPI 89 · PCS 83 · ORWO 30. **Rewallution absent here** (expected — Rewallution doesn't carry distinct providers).
- Recency: `MAX(updated_at) = 2026-05-21 10:46:57` (most recent of all probed tables). `MAX(dw_timestamp) = 2026-05-15`.
- Surprises: ORWO providers are present (30 rows), consistent with ORWO being a landed source.

### enterprise_silver.dim_carrier_sla

- Exists: **no**. Not present in `enterprise_silver`. No matching object anywhere in `information_schema.tables` under any schema either (would have shown in the `%shipping%` / `%carrier%` filter). Either renamed, deferred, or never built.

### enterprise_bronze.dim_truck_costs

- Exists: **yes**
- Rows: **7** (very small reference table — truck-cost rate card, SCD2-shaped with `valid_from`/`valid_to`).
- Columns: `truck_provider`, `destination_city`, `productionsiteids`, `truck_database_identifier`, `country_code`, `shippingprovider_key`, `cost_per_truck_eur`, `valid_from`, `valid_to`, `type`, `comment`, `updated_at`, `dw_timestamp`.
- Recency: `MAX(updated_at) = 2026-05-04 10:03:57` (oldest of probed tables — reference data, slow-changing).
- No `source_system` column; not applicable.

## FK joinability

`map_shipment_key.shipment_id` (18,631,411 distinct) ↔ each fact's `shipment_id`:

| fact | n_rows | % matched to MSK |
|---|---|---|
| fact_shipments | 18,463,257 | **100.00%** |
| fact_shipment_orderitems | 122,689,685 | **100.00%** |
| fact_shipment_cost_summary | 12,039,076 | **100.00%** |
| fact_shipment_invoice_lines | 55,458,803 | **99.18%** |

Notes:
- MSK has 168,154 keys *without* a fact_shipments row (18,631,411 − 18,463,257). Direction matters: MSK is a superset of the keys present in fact_shipments. Need a deeper probe to know which source_systems contribute the gap; likely PCS / Rewallution with partial shipment rollups.
- ~455k invoice_lines rows (0.82%) lack a shipment_id-to-MSK match. Cohort = charges with NULL `shipment_id` plus any unmatched-key remainder.

## Surprises / gaps

1. **ORWO is landed.** The "ORWO not landed" pre-V1 picture is wrong as of 2026-05-21. ORWO has 2.5M shipments and 90M orderitems — and is the largest single source by orderitem count.
2. **But ORWO is identity-only.** Every ORWO shipment column except `weight_kg` is 100% NULL. `revenue_eur`, `product_key`, `destination_country`, all timestamps, all cost columns, currency, truckload, net_revenue. ORWO contributes keys without contributing attributes — the lineage merge / enrichment for ORWO hasn't shipped.
3. **`fact_shipments` cost columns are 100% NULL across all source_systems.** `real_shipping_cost_eur`, `final_shipping_cost_eur`, `cost_source`, `currency_code` — all empty for all 18.5M rows. Either the cost roll-up onto fact_shipments was never wired, the columns are deprecated in favor of `fact_shipment_cost_summary`, or there's a broken merge step. Worth confirming: if these are meant to be the canonical cost columns, V1 has a hole; if they're vestigial, they should be dropped.
4. **8 mart tables, not 9.** `dim_carrier_sla` does not exist. Either renamed, deferred to V2, or never planned.
5. **No shipping gold schema.** `sl_gold` is shop-level revenue mart, not shipping. There is no `sg_*` or `shipping_gold` schema. If V1 closeout includes a gold layer, it's not in Redshift yet.
6. **`map_shipment_key.updated_at` / `dw_timestamp` are 100% NULL** despite having `now()` defaults. ETL writes explicit NULLs to these columns. Recency must be inferred from `order_created_date` for MSK.
7. **PicaAPI carrier timestamps are 78% NULL.** Even on a source where coverage is expected to be decent, `received_by_carrier_ts` and `delivered_by_carrier_ts` are missing for the majority. Picturator is better (~34% NULL) but still significant.
8. **MSK has 168k more keys than fact_shipments.** Not a huge gap (0.9%), but worth flagging: a MSK row should imply a fact_shipments row in a clean star.
9. **`fact_shipment_invoice_lines` has no `source_system` column.** Cost-side facts are keyed by `invoice_source` instead. This is consistent with carrier-invoice provenance, but a docs reader will need to know not to expect source_system there.
10. **PCS orderitems (41k) have 100% NULL `revenue_eur`.** Same shape as ORWO at smaller scale. PCS contributes cost data; orderitem-shape revenue is not its job.
