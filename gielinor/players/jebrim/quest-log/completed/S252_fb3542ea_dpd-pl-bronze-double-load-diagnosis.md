# S252 — DPD-PL invoice sum differs across enterprise_bronze / bi_stage_dev_dbo / shipping_mart

**Actor:** Jebrim (principal-self, read-only DB diagnostic via Redshift MCP `tcg_nfe`).
**Ask:** "DPD PL invoices show a different sum in each source — where's the issue? enterprise_bronze returns a lot (duplicates?), bi_stage_dev_dbo maybe missing invoices, and how does shipping_mart differ from bronze if that's the source?"

## Headline result

Two distinct things were conflated:

1. **The three "sources" are not the same population.** Scoped to struct1 (firststructure):
   - `enterprise_bronze.dpd_poland_firststructure_invoice` = the **current landing batch only** (May-2026, `invoice_date` all `2026-05-31`).
   - `bi_stage_dev_dbo.dpd_poland_firststructure_invoice` = the **legacy ndw pipeline, frozen** at the Nov-2025 batch (`2025-11-30`), 47,995 rows, €229,306.97 — a dead pipeline, not "missing invoices."
   - `enterprise_silver.dpd_poland_struct1_invoices` = full cleaned history 2022-10→2026-05, 455,203 trackings, €2,186,825.89 `netcost` — **this feeds the mart**, not bronze `_invoice`.
   - Lineage is bronze `_raw_historical` → silver → `shipping_mart`. Bronze `_invoice` is just the landing batch, so comparing it to the mart diverges by construction.

2. **The one real defect — bronze double-load.** `enterprise_bronze.dpd_poland_firststructure_invoice` holds the **same May-2026 invoice twice**: a `2026-06-08` load (26,376 rows, consignment grain) and a `2026-06-15` reload (105,022 rows, charge-line grain). Both = the same 26,376 consignments, both `SUM(total_price)` = **€124,549.75**. Table wasn't truncated between loads → `SUM(total_price)` = **€249,099.50 = exactly 2×**. Same DQ *class* as [[S177_eac2ab42_dpd-poland-clc-de-reconciliation|S177]] (which was the silver `struct1_charge_lines` double-load); this time it's the bronze current-batch table.

## Proof delivered (verified live)

- **Q1 (money):** `GROUP BY dw_timestamp::date` → two load days, identical €124,549.75 each.
- **Q2 (smoking gun):** every consignment's distinct-load-day count = **2** for **100%** (26,376/26,376) of consignments. No "loaded once" cohort.

Both queries handed to the principal; principal forwarded the finding to the ETL team.

## Scope / caveats

- **struct1 (firststructure) only.** DPD-PL also has struct2 (secondstructure) + rewallution_1/2 streams — NOT profiled; offered the same double-load sweep across them as the next step (principal closed before running it).
- Gold mart DPD-PL slice not pulled (mapping struct1→mart needs the provider extkey, e.g. `DPDPOLANDCLC` per [[S177_eac2ab42_dpd-poland-clc-de-reconciliation|S177]]); stopped once the bronze root cause was clear.
- `enterprise_bronze.dpd_poland_firststructure_invoice_raw_historical` (1.25M rows, 2023-08→2026-05, €1,932,445.89) also shows reload duplication (distinct_id 369,191 ≪ rows) — expected for an accumulation table; clean figure needs dedup.

## Pending external actions

None pending. Diagnosis + queries delivered in chat; principal sent to ETL team. No commits to external repos, no sends by me.

## Anchors

- Prior art: [[S177_eac2ab42_dpd-poland-clc-de-reconciliation]] (silver struct1_charge_lines double-load).
- Lineage: [[bi-etl]] domain digest; bronze→silver→shipping_mart.
- DQ candidate: bronze current-batch tables are not truncate-before-load → harvest note `bank/drafts/notes/projects/2026-06-17-dpd-pl-bronze-current-batch-double-load.md`.
