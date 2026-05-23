# S002 resume — Shipping Data Mart V1 gap analysis

**Status:** in-progress. All external actions completed; no pending.
**Quest file:** `players/jebrim/quest-log/in-progress/S002_2026-05-20_shipping-data-mart-v1-gap-analysis.md`

## Where we are

V1 gap analysis carried across S002 → S008 → S011. Active threads:

1. **ORWO `sentat` → `order_produced_ts`** — posted to NGE-6129, pending Satya.
2. **NGE-6127 reopen** (ORWO classification + git-coverage gap) — posted; awaiting principal decision on ad-hoc UPDATE vs CASE WHEN + seed-file question.
3. **ORWO product SKU lineage — CLOSED in S011.** `poc_landing.orwo_navcluster_data` is the landed dim; remaining gap is the orderitem-grain fact (`admin.orderline` not in warehouse).
4. **ORWO `destination_country` — wiring problem, not missing-data.** Field exists in PTS bronze at 99.6% fill; current wiring fills only 6.4% of fact_shipments ORWO due to rolling-window source. Two paths forward; option (b) cheaper to check first.
5. **Grzegorz NGE-7094 (2026-05-20 EOD):** DB Schenker reconciled to +0.6% MATCH (two stacked bronze bugs fixed); UPS €50k apparent gap = customs+tax exclusion (keep as-is); UPS per-invoice grain confirmed; Alisa's 7 UPS invoices 1/7 recovered (rest lost to 2026-04-07 SFTP migration); UPS bronze `accountnr` 100% NULL backfilled.

Plus: `fact_shipment_invoice_lines.invoice_number` USPS 79.66% + direct_link 97.66% — both upstream-unrecoverable; footnote in V1 gap matrix Area 9.

**Synthesis HTML stale on 4 points:** received_by_carrier_ts semantic flip (S008), Area 9 dim_shipping_providers repo gap (S008), destination_country reclassification (S011), Area 9 sub-rows for USPS + direct_link unattributable invoice rows (S011). Patch in one pass.

## Next concrete step (priority order)

1. **ORWO `destination_country` cheap-check.** Probe `enterprise_bronze.orwo_shipping_data_mart` for a country column. Read the bronze DAG + ddl + silver ORWO branch. If column exists → 1-line silver fix to Grzegorz. If absent → Plan B is one-time Oracle backfill of `orwo_pts_parcelfinish`.
2. **NGE-6129 dim_products extension path** for ORWO. Now lineage is clean: graduate `poc_landing.orwo_navcluster_data` → silver, OR extend `dim_products` directly. Short note → comment on NGE-6129 if approved.
3. **ORWO classification decision** (pending principal): ad-hoc UPDATE vs CASE WHEN + seed-file question.
4. **ETL check-in reconciliation** (was scheduled 2026-05-22 AM). Update entry with agreed task list; principal pushes to ClickUp.
5. **V1 gap matrix HTML patch** — single pass, four known stale spots listed above.

If V1 ships clean and all threads close: move quest to `completed/` (sibling dwarf files come with).

## Files / paths to read first

1. The S002 quest-log file — full thread history + dwarf details.
2. `bank/notes/projects/shipping_data_mart_v1_gap_analysis.html` — canonical synthesis (sticky-nav; 4 stale spots noted above).
3. **For destination_country thread (priority 1):**
   - `bi-etl/dags/enterprise_bronze/orwo_shipping/bronze_orwo_shipping_data_mart.py`
   - `bi-etl/dags/enterprise_bronze/orwo_shipping/sql/table_creation_ddl.sql`
   - `bi-etl/dags/enterprise_silver/Shipping_Data_Mart/fact_shipments/sql/insert_to_silver.sql` (ORWO branch)
4. **For ORWO product lineage (priority 2 — context already gathered):**
   - `poc_landing.orwo_navcluster_data` on Redshift.
   - `bi-etl/dags/orwo_dag/02_production_metrics/sql/extract/navcluster_data.sql`.
   - `bi-analytics-main/NFE/shipping_topics/29_ORWO_sperrgut_tcg_and_orwo_shops/pipeline.py`.
5. **For ORWO classification thread:** `bi-etl/dags/enterprise_silver/Shipping_Data_Mart/dim_shipping_providers/sql/upsert_to_silver.sql` + `README.md`.
6. Dwarf siblings (detail if a finding needs re-checking): `S002_d1_clickup_subtree.md`, `S002_d2_bi_etl_state.md`, `S002_d3_redshift_coverage.md`.
7. Sibling quest `S001_2026-05-20_repo-orientation.md` — picks #3/#4/#5 unresumed.

## Constraints (in-force)

- ORWO is required for V1 (not optional).
- NGE-6120 is the V1 epic; no sibling epics.
- NFE planning docs are stale — do not treat as authority for project status.
- bi-etl `main` is the source of truth on implementation. `git pull origin main` before reading.
- Output grouping: by area with estimated owner per task, not by owner.
- Prefer in-repo `.html` "open pointers" over ClickUp attachments when both exist.
