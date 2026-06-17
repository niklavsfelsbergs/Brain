# DPD-PL bronze "current-batch" tables can double-load — and the three DPD-PL sources aren't comparable

**Status:** draft (harvest from [[S252_fb3542ea_dpd-pl-bronze-double-load-diagnosis|S252]], 2026-06-17). Verified live against Redshift `tcg_nfe`.

## The reusable lineage fact (resolves the recurring "different sum per source" confusion)

For DPD-PL (and likely the other carrier streams in `enterprise_bronze`), there are **three non-comparable layers** that get mistaken for the same thing:

- **`enterprise_bronze.<carrier>_..._invoice`** = the **current landing batch only** (one invoice period; `invoice_date` is a single value). NOT a history table.
- **`enterprise_bronze.<carrier>_..._invoice_raw_historical`** = the **accumulation** (all periods; different/more columns incl. `invoice_no`, discount cols). Accumulation → carries reload duplication across periods by design.
- **`enterprise_silver.<carrier>_..._invoices`** = the **cleaned full history** — this is what the mart consumes.
- **`bi_stage_dev_dbo.*`** = the **legacy ndw pipeline** (frozen). For DPD-PL struct1 it stopped at the Nov-2025 batch. Treat as dead; do not reconcile against current data.

Lineage: bronze `_raw_historical` → `enterprise_silver` → `shipping_mart`. The mart does **not** read bronze `_invoice` (current batch), so comparing that table to the mart diverges by construction. See [[bi-etl]].

## The DQ defect (generalizes [[S177_eac2ab42_dpd-poland-clc-de-reconciliation|S177]] from silver to bronze)

The bronze current-batch table is **not truncate-before-load**. Observed: `enterprise_bronze.dpd_poland_firststructure_invoice` held the **same May-2026 invoice twice** — `2026-06-08` load (26,376 rows, consignment grain) + `2026-06-15` reload (105,022 rows, charge-line grain), same 26,376 consignments, each `SUM(total_price)` = €124,549.75 → table sums to €249,099.50 (exactly 2×). The two loads carried **different grain** as well as a duplicate, so row-count looks ~5× while money is 2×.

This is the **same DQ class as [[S177_eac2ab42_dpd-poland-clc-de-reconciliation|S177]]** (silver `dpd_poland_struct1_charge_lines` double-loaded a CSV), one layer upstream. The defect is a property of the **load** (appends / no truncate / no id+filename dedup), not the invoice — so it can recur on any carrier's bronze current-batch table.

## Detector queries (paste-ready)

```sql
-- money: same invoice total under >1 load day = doubled
SELECT dw_timestamp::date AS load_day, COUNT(*) AS rows,
       COUNT(DISTINCT consignment_no) AS consignments, ROUND(SUM(total_price),2) AS invoice_total
FROM enterprise_bronze.dpd_poland_firststructure_invoice
GROUP BY dw_timestamp::date ORDER BY load_day;

-- smoking gun: distinct load-days per consignment; all = N means N× loaded
SELECT loads_per_consignment, COUNT(*) AS num_consignments
FROM (SELECT consignment_no, COUNT(DISTINCT dw_timestamp::date) AS loads_per_consignment
      FROM enterprise_bronze.dpd_poland_firststructure_invoice GROUP BY consignment_no) t
GROUP BY loads_per_consignment ORDER BY loads_per_consignment;
```

## Open / follow-up

- Not yet swept: DPD-PL **struct2** + **rewallution_1/2** bronze tables for the same double-load.
- `known-dq.md` (picanova/shipping-agent) still has no entry for the bronze current-batch double-load class — candidate maintainer edit (principal-gated), alongside the [[S177_eac2ab42_dpd-poland-clc-de-reconciliation|S177]] silver gap.

Relates to [[shipping-mart]], [[carrier-contracts]], [[bi-etl]].
