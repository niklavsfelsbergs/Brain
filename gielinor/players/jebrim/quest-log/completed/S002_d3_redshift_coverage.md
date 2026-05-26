# [[S002_2026-05-20_shipping-data-mart-v1-gap-analysis|S002]] — D3 — Redshift coverage probe of `enterprise_silver` Shipping Data Mart V1

**Spawn:** 2026-05-21
**Role:** Jebrim-inherited dwarf
**Scope:** Read-only probe of the 8 V1 mart tables. No DDL, no writes. No ClickUp, no repo reads.
**Reference snapshot taken at:** 2026-05-21 (mart `dw_timestamp` clock most recent at 2026-05-20 14:51 UTC)

## 0. Table existence

7 of 8 expected tables exist in `enterprise_silver`:

- `map_shipment_key` — present
- `fact_shipments` — present
- `fact_shipment_orderitems` — present
- `fact_shipment_invoice_lines` — present
- `fact_shipment_cost_summary` — present
- `fact_truck_charges` — present
- `dim_shipping_providers` — present
- **`dim_carrier_sla`** — **ABSENT**. Not in `enterprise_silver`. Confirmed via `information_schema.tables` and a fallback name-search (no table with `sla` or `carrier` in its name exists in the schema). Not probed further.

Recency proxy: no `loaded_at` column anywhere; every active table carries `dw_timestamp` and `updated_at`. Those are used below. For `map_shipment_key`, both timestamp columns are 100% NULL on every row — domain date columns (`order_created_date`) used instead.

## 1. Row counts + recency, per table

| Table | Rows | MAX(`dw_timestamp`) | MAX(`updated_at`) | Domain max date |
|---|---:|---|---|---|
| `map_shipment_key` | 18,609,142 | NULL on all rows | NULL on all rows | `order_created_date` = 2026-05-20 |
| `fact_shipments` | 18,441,433 | 2026-05-20 14:37:36 | 2026-05-20 14:51:14 | `received_by_carrier_date` = 2026-05-20 |
| `fact_shipment_orderitems` | 121,922,488 | 2026-05-20 14:28:21 | 2026-05-20 14:28:21 | n/a |
| `fact_shipment_invoice_lines` | 55,457,841 | 2026-05-20 12:44:55 | 2026-05-20 12:44:55 | `shipment_date` = 2026-05-18 |
| `fact_shipment_cost_summary` | 12,038,152 | 2026-05-20 14:50:22 | 2026-05-20 14:50:22 | n/a |
| `fact_truck_charges` | 2,317 | 2026-05-20 14:42:20 | 2026-05-20 14:49:20 | `departure_date` = 2026-05-20 |
| `dim_shipping_providers` | 326 | **2026-05-15 09:58:08** | **2026-05-15 09:58:08** | (no domain date) |

**Recency anomalies:**

- `dim_shipping_providers` last refreshed **2026-05-15** — 5 days stale relative to facts that ran on 2026-05-20. Could be benign (slow-changing dim) or a freshness bug — flagging.
- `map_shipment_key.dw_timestamp` and `updated_at` are 100% NULL across **all 18.6M rows**. The columns exist but are never populated. DQ violation against the convention used elsewhere in the mart. Flagging.

## 2. Row count by `source_system`

`source_system` column exists on: `map_shipment_key`, `fact_shipments`, `fact_shipment_orderitems`, `dim_shipping_providers`. It is **absent** on `fact_shipment_invoice_lines` (uses `invoice_source` instead), `fact_shipment_cost_summary`, `fact_truck_charges`.

| Table | Picturator | PicaAPI | PCS | Rewallution | ORWO |
|---|---:|---:|---:|---:|---:|
| `map_shipment_key` | 13,038,884 | 3,011,069 | 59,009 | 6,191 | 2,493,989 |
| `fact_shipments` | 13,023,015 | 2,859,307 | 58,931 | 6,191 | 2,493,989 |
| `fact_shipment_orderitems` | 28,899,376 | 3,391,294 | 41,021 | 8,200 | 89,582,597 |
| `dim_shipping_providers` | 124 | 89 | 83 | **0** | 30 |

**`fact_shipment_invoice_lines.invoice_source`** distribution is per-carrier, not per source_system (sample top buckets): `dhl` 27.9M, `dhl_orwo` 9.6M, `ups` 5.7M, `fedex` 4.3M, `gls` 1.7M, `dpd_poland_struct1` 1.04M, `yodel` 990K, `dpd` 917K, `ontrac` 742K, `colis_prive` 732K. (Full distribution in raw output — 23 distinct values.)

**Cross-table coverage anomalies:**

- **Rewallution is absent from `dim_shipping_providers`.** All other source_systems have provider entries. Rewallution shipments cannot resolve to a provider via the dim — but provider FK on `fact_shipments.shipping_provider_id` still resolves (see §4) because the column is populated by source pipeline, not by lookup. Still: a Rewallution-grouped report would join to no dim rows.
- **Map vs fact gap for PicaAPI:** map has 3,011,069 PicaAPI rows; fact_shipments has 2,859,307. 151,762 PicaAPI map rows have no matching fact (see §4).
- **Map vs fact gap for Picturator:** map 13,038,884 vs fact 13,023,015 — 15,869 orphans (§4).
- **ORWO orderitems are 89.6M of 121.9M orderitems total** (73%). Skews the orderitems table heavily ORWO-side, while ORWO is only 13.5% of `fact_shipments`.

## 3. % NULL on V1-critical columns

### 3a. `fact_shipments` by source_system

| source_system | rows | `shipment_id` | `cost_source` | `final_shipping_cost_eur` | `destination_country` | `weight_kg` | `received_by_carrier_ts` | `delivered_by_carrier_ts` | `shipping_provider_id` |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Picturator | 13,023,015 | 0.00 | 5.56 | 5.56 | 0.00 | 14.68 | 33.38 | 35.86 | 0.18 |
| PicaAPI | 2,859,307 | 0.00 | 1.11 | 1.11 | 0.03 | 0.97 | 77.62 | 79.16 | 0.75 |
| ORWO | 2,493,989 | 0.00 | 28.80 | 28.80 | **100.00** | **47.06** | 0.00 | **100.00** | 0.00 |
| PCS | 58,931 | 0.00 | 0.87 | 0.87 | 0.00 | 0.04 | **100.00** | **100.00** | 0.00 |
| Rewallution | 6,191 | 0.00 | 20.80 | 20.80 | 0.00 | **100.00** | **100.00** | **100.00** | **100.00** |

(`revenue_eur` and `product_key` do not exist on `fact_shipments` — see 3b. `fact_shipments` has `net_revenue_eur` instead; not probed since brief specified `revenue_eur`.)

### 3b. `fact_shipment_orderitems` by source_system

| source_system | rows | `shipment_id` | `revenue_eur` | `product_key` | `quantity` | `sku` |
|---|---:|---:|---:|---:|---:|---:|
| Picturator | 28,899,376 | 0.00 | 0.14 | 0.08 | 0.00 | 0.08 |
| PicaAPI | 3,391,294 | 0.00 | 0.01 | 0.03 | 0.00 | 0.00 |
| ORWO | 89,582,597 | 0.00 | **100.00** | **100.00** | 0.00 | 0.00 |
| PCS | 41,021 | 0.00 | **100.00** | 1.94 | 0.00 | 1.74 |
| Rewallution | 8,200 | 0.00 | 0.00 | **100.00** | 0.00 | **100.00** |

### 3c. `fact_shipment_invoice_lines` (no source_system; whole-table)

| rows | `shipment_id` | `charge_amount_eur` | `charge_bucket` | `invoice_source` |
|---:|---:|---:|---:|---:|
| 55,457,841 | 0.82 | 0.00 | 0.00 | 0.00 |

0.82% NULL `shipment_id` = ~455K orphan invoice rows that cannot be tied to a shipment. Charge bucket and amount are fully populated.

### 3d. `fact_shipment_cost_summary` (no source_system; whole-table)

| rows | `shipment_id` | `total_eur` | `billed_weight` |
|---:|---:|---:|---:|
| 12,038,152 | 0.00 | 0.08 | 0.36 |

Clean. 100% shipment_id, ~0% NULL on totals.

### 3e. `fact_truck_charges` (no source_system; whole-table)

| rows | `truckload_id` | `cost_per_truck_eur` | `cost_per_parcel_eur` | `shipment_count_allocated` |
|---:|---:|---:|---:|---:|
| 2,317 | 0.00 | 0.00 | 8.29 | 0.00 |

8.29% NULL `cost_per_parcel_eur` — probably trucks with 0 allocations or pending allocation; not investigated further.

### 3f. Brief-asked columns that don't exist where expected

- `loaded_at` — does not exist on any table; `dw_timestamp`/`updated_at` used instead.
- `revenue_eur` on `fact_shipments` — does not exist; `net_revenue_eur` is present but wasn't probed (brief specified `revenue_eur` for orderitems, not shipments).
- `product_key` on `fact_shipments` — does not exist; lives on orderitems.

## 4. FK joinability

### 4a. `map_shipment_key.shipment_id` ↔ facts

| Direction | Orphan rows |
|---|---:|
| `fact_shipments` rows with no map row | **0** |
| `map_shipment_key` rows with no `fact_shipments` row | **167,709** |
| `fact_shipment_orderitems` rows with no map row | 0 |
| `fact_shipment_invoice_lines` rows with no map row (excl. NULL shipment_id) | 0 |
| `fact_shipment_cost_summary` rows with no map row | 0 |

Map is a complete superset of every fact's `shipment_id`. Map carries 167,709 shipment_ids that never made it into `fact_shipments`. Breakdown:

| source_system | orphan map rows | min order_created_date | max order_created_date |
|---|---:|---|---|
| PicaAPI | 151,762 | 2023-01-02 | 2026-05-19 |
| Picturator | 15,869 | 2023-01-01 | 2026-05-19 |
| PCS | 78 | 2025-07-29 | 2026-05-13 |

Spread across 3+ years and includes recent dates. Either pipeline filters (e.g., cancelled orders never shipped) or a silent drop. Worth a ticket-context lookup; from Redshift alone I can't tell whether intended.

### 4b. `dim_shipping_providers` ↔ `fact_shipments`

| Check | Orphan rows |
|---|---:|
| Via `shipping_provider_id` join | 0 |
| Via `(shippingprovider_extkey, source_system)` join | 0 |

Both keys resolve 100%. Provider FK is healthy from `fact_shipments` to dim.

However: 41 of 326 `dim_shipping_providers` rows have both `shippingprovider_group` and `service_type` NULL — 12.6% of the dim is unclassified. (Doesn't break joinability, but degrades any group/service rollup.)

### 4c. `dim_carrier_sla` joinability

**N/A — table absent.** Cannot probe.

## 5. SLA-breach feasibility

**`sla_breach_flag` and `days_vs_sla` are NOT computable from the current mart.**

Reasons:

1. `dim_carrier_sla` does not exist in `enterprise_silver`. Search by table name and by column name (anything `*sla*`) returns zero matches in the schema.
2. `dim_shipping_providers` carries `service_type` (Standard / Express / DPD POLAND / Bring [nShift] / Fast Track / etc.) but **no SLA day count, no SLA target column**. Service type alone isn't enough to compute days_vs_sla.
3. Even if a SLA dim existed: `delivered_by_carrier_ts` is **100% NULL for ORWO and PCS**, 35.9% NULL for Picturator, 79.2% NULL for PicaAPI. SLA breach requires a delivery timestamp — so for ORWO + PCS the calculation is structurally impossible until delivery timestamps land.

V1-blocking finding: SLA breach is a V1 KPI per the brief; no path to compute it from the mart as-of 2026-05-20.

## 6. Anomaly summary (top hits, ranked by V1 impact)

1. **`dim_carrier_sla` does not exist.** SLA-breach metric is blocked. (See §5.)
2. **ORWO `destination_country` is 100% NULL** on 2,493,989 rows. Country-level reporting for ORWO is impossible without a backfill. (§3a)
3. **ORWO `delivered_by_carrier_ts` is 100% NULL.** No delivery date for the entire source. Transit time and SLA both blocked for ORWO regardless of dim. (§3a)
4. **ORWO orderitems `revenue_eur` and `product_key` are 100% NULL.** Orderitems table has 89.6M ORWO rows that are revenue-empty. Cross-table revenue rollups for ORWO are broken. (§3b)
5. **Rewallution is structurally unusable in V1.** 100% NULL on weight, shipping_provider_id, both carrier timestamps on `fact_shipments`; 100% NULL on product_key and sku on orderitems; **absent entirely from `dim_shipping_providers`**. Only 6,191 shipments — consider scoping out of V1. (§3a, §3b, §2)
6. **PCS has 100% NULL on `received_by_carrier_ts` AND `delivered_by_carrier_ts`.** No carrier timestamps at all for 58,931 shipments — transit time and SLA blocked for PCS. (§3a)
7. **PCS orderitems `revenue_eur` is 100% NULL.** Same revenue gap as ORWO, smaller volume. (§3b)
8. **`map_shipment_key.dw_timestamp` and `updated_at` are 100% NULL** across 18.6M rows. Columns exist but never populated. DQ convention violation; affects any freshness check that relies on the map's own timestamps. (§1)
9. **`cost_source` distribution does not match expected `real`/`expected`/`avg`.** Actual values seen: `invoice` (dominant), `expected`, `avg`, `invoice_estimate`, NULL. **`invoice_estimate` is a bucket not in the V1 spec** and represents 82K rows. The brief's `real` value does not appear at all — probably renamed to `invoice` at silver curation. (§6 of probe)
10. **`fact_shipment_cost_summary` is wired and fresh, contradicting the README's "v2 not yet built" claim.** 12.0M rows, 100% shipment_id, MAX(updated_at) = 2026-05-20 14:50. Joins 100% from its own side to `fact_shipments`. **But coverage from the fact side is 65.3%** — 6.4M of 18.4M shipments have no cost_summary row. PCS has the worst per-source gap at 62.2% no-link. (§3d, §4 supplement)
11. **`dim_shipping_providers` is 5 days stale** relative to facts (2026-05-15 vs 2026-05-20). Could be benign (slow-changing) or a freshness bug; flag, don't conclude. (§1)
12. **167,709 map rows have no fact_shipments record**, spread 2023-01 to 2026-05-19. Could be cancelled/never-shipped or a silent drop. (§4a)
13. **41 of 326 `dim_shipping_providers` rows have NULL `shippingprovider_group` AND NULL `service_type`.** 12.6% of providers are unclassified — degrades any group-level rollup. (§4b)
14. **0.82% NULL `shipment_id` in `fact_shipment_invoice_lines`** = ~455K orphan invoice rows that cannot be tied to a shipment. Affects cost reconciliation. (§3c)
15. **Invoice sources with frozen `MAX(shipment_date)`** that may be stuck or retired (not investigated, flag only): `gls` 2025-08-21, `dpd` 2024-09-10, `colis_prive` 2025-11-10, `landmark_taxes` 2024-08-06, `landmark_parcels` 2024-10-20, `dpd_poland_rewallution` 2024-06-30, `dhl_america` 2025-12-14, `apg` 2025-12-19, `db_schenker` 2026-03-27. Several million rows total in retired/frozen state.
16. **`dpd_poland_struct1` invoice_source is stuck — MAX(shipment_date) = 2026-04-14**, over a month stale on 1.04M rows. Matches D1/D2 bug-report reference to `dpd_poland_invoices_firststructure`. `ups_orwo` mentioned in same report is NOT stuck (max 2026-05-18).
17. **Picturator carrier timestamps are 33–36% NULL.** This is the largest source by volume — a third of shipments have no received timestamp and a third have no delivery timestamp. Transit-time KPI accuracy on Picturator depends on the principal's view of whether that's expected backfill lag or a real gap.

## 7. Notes on what the probe did NOT do

- Did not probe `enterprise_bronze`, `poc_landing`, `poc_staging`, `dw` legacy. Scope was `enterprise_silver` mart only.
- Did not test computability of `transit_time_days` (already a column on `fact_shipments`; presence does not imply correctness).
- Did not deep-dive the frozen invoice sources (§6 item 15). Listed for the synthesis pass.
- Did not check `net_revenue_eur` on `fact_shipments` (brief asked for `revenue_eur`, which lives only on orderitems).
- Did not probe row count by destination_country, by carrier, or by date — pure schema/coverage probe per brief.

## 8. Verdict (one line)

V1 ships in 2 days with **SLA-breach unbuildable**, **ORWO destination_country + deliveries empty**, **Rewallution structurally unusable**, and a **`fact_shipment_cost_summary` that the README says doesn't exist but does and is fresh** — the largest tickets-vs-reality gap surfaced here.
