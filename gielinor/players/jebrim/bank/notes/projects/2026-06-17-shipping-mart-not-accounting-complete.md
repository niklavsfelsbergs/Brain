# Shipping mart `fact_shipment_invoice_lines` is allocation-shaped, NOT accounting-complete

**Drafted:** 2026-06-17 (S251/d8d2c1be) · from a UPS May 2026 accounting-close reconciliation.

## Claim

`shipping_mart.fact_shipment_invoice_lines` filters and *alters* carrier cost on the way from silver, so it does **not** equal what the carrier actually invoiced. For an accounting close / whole-invoice total, reconcile off `enterprise_silver.<carrier>_invoices`, **not** the mart. The mart is the tracked, non-RTS, mappable subset built for per-shipment allocation.

## The layer chain (UPS, verified)

- **Whole invoice** = `enterprise_silver.ups_invoices` — every charge line, all charge types (returns, tax, gov/customs, brokerage, adjustments), all accounts. `SUM(netamounteur)` on `transactiondate` for May = **€434,551 / 156,795 lines** (direct stream only — the Wolfen bulk-bill is a separate table, `ups_orwo_invoices`).
- **Silver build** (`bi-etl/dags/shipping_invoice_cost/SFTP/UPS/sql/insert_to_silver.sql`) drops vs bronze: a hardcoded **22-invoice blacklist** + a **×0.072789 rescale on 17 Swiss invoices** (both legacy, all pre-2025/2026 — no current-period impact) + incremental dedup. No charge-type filtering.
- **Gold build** (`bi-etl/dags/shipping_mart/fact_shipment_invoice_lines/sql/providers/ups.sql`) — five cost-affecting filters:
  1. `trackingnumber IS NULL/''` → **dropped, unrecoverable** (€4,800 / May).
  2. `netamounteur IS NULL` → dropped.
  3. `invoicedate < 2024-01-01` → dropped (V1 scope).
  4. `chargecategorydetailcode = 'RTS'` → return lines removed from the load…
  5. …then **redistributed** onto the original parcel (`UPS_add_returns` legacy mirror, matched on `shipmentreferencenumber1`), **capped at 90 days** — late returns lost. The redistribution is baked into `charge_amount_eur` (`+ rr.per_line_addition`), NOT a separate line/bucket.

## UPS May reconciliation (direct stream)

```
  434,551   whole direct invoice (silver)
−  12,060   RTS lines removed
−   4,800   no-tracking lines dropped
+   7,600   returns redistributed back into surviving lines (of the 12,060; ~4,460 lost to 90-day cap / unmatched)
= 425,291   mart (fact_shipment_invoice_lines, all buckets)
  net structural loss vs whole invoice = 9,260 (~2.1%) = 4,800 no-tracking + 4,460 returns-not-recovered
```

## Cost basis nuances

- **Tax/customs are IN the mart** as `tax` + `customs_duties` buckets — not dropped at build. "Freight only" excludes them at *query* time (`charge_bucket NOT IN ('tax','customs_duties')`). All-in = include them. Whole-co both-stream May UPS: €517,736 all-in / €503,910 freight.
- **`fact_shipment_cost_summary`** (the 11-bucket pivot / `final_shipping_cost_eur`, "the one number") **excludes tax/customs by design** (pass-through). Anything using that surface is structurally freight-only.
- **Entity vs provenance:** `source_system` = entity (TCG = `Picturator`+`PicaAPI`); `invoice_source` = billing stream (`ups` direct vs `ups_orwo` bulk-bill). The Wolfen bulk-bill stream (€79,858) is ~63% TCG parcels — entity ≠ stream. [[reference_shipping_mart_revenue_and_quota]] sibling.

## Cross-carrier caveat

Filtering is **per-carrier** — 23 provider SQL files in `fact_shipment_invoice_lines/sql/providers/`, each bespoke (DPD Poland has struct1/struct2/rewallution; ORWO streams do bulk-mail cost-splitting). The UPS filter set above does not necessarily generalize; trace each before assuming.

## So what

- Accounting close keyed on "what the carrier billed" → use silver, with a defined baseline (bronze vs silver: silver already alters via the blacklist + CH rescale).
- The principal filed an ETL ticket to make invoice_lines carry ALL cost (move filters/transforms to the invoice_lines→cost_summary hop). Acceptance test: per-carrier `invoice_lines` total == raw, delta = 0.
