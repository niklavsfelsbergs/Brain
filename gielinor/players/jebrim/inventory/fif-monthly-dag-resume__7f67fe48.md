---
quest: S116_shipping-agent-fif-monthly-skill
sid8: 7f67fe48
ts: 2026-06-01 11:00
---

# Resume — FIF UPS-ORWO report DAG (S116)

**Status:** SHIPPED. PR merged, DAG ran, **SharePoint PUT verified live 2026-06-01** — downloaded `UPS_FiF_report_2026-04.xlsx` from SharePoint diffs byte-equivalent (content-wise) to the standalone April reference: 149 pivot groups, net €104,312.29 / VAT €13,889.34 / gross €118,201.63, 0 group-level mismatches. SharePoint auto-created the `UPS_FiF_reports/{invoice_level,month_summary}/` subfolders on first PUT. Quest left in-progress for tail monitoring; ready to graduate to completed/ next session.

## Where we are
Built a **daily bi-etl DAG** `fif_ups_orwo_monthly` that delivers the FIF (UPS ORWO) report to SharePoint in two forms under `Share/InvoiceDataShipping/UPS_FiF_reports/`:
- `invoice_level/` — one xlsx per invoice as they arrive (`{inv}_{invdate}_{procdate}.xlsx`), folder-as-ledger, process-once.
- `month_summary/` — whole-month report; month M "closed" once an M+1 invoice exists; regenerates if a late M invoice arrives (driven by invoice_level's months_touched). VAT = option A (per-invoice isolation).

Transform ported verbatim from the validated NFE standalone pipeline. Fixed a real bronze DQ bug (invoicedate mixed ISO + US M/D/YYYY → normalize `::date`).

**Deployed + verified end-to-end:** ECR image `fif_ups_orwo:latest` (digest ebfe767). bi-etl branch `feat/fif-ups-orwo-monthly` commits `39a1d9d42` + `de3e74f87` + `9f7c241fd` (relocation to `AI_Automations/shipping_nfe/`), pushed. Live smoke 2026-05-28 (tcg_nfe → local): invoice_level 75 files, month_summary Jan–Apr, Mar=20 / Apr exact. **Live DAG run 2026-06-01: April month_summary downloaded from SharePoint matches standalone reference exactly (149 groups, totals to the cent, 0 mismatches).** SharePoint folder auto-creation confirmed working.

## Next concrete step
None required to ship — the DAG is live and verified. For next session:
1. **Graduate S116 → completed/** (no open dependency; PR merged, DAG running, SharePoint PUT verified).
2. **Triage the harvest drafts** via `/drafts` — examine `fixture-vs-live-data-claim` + bank `ups-orwo-fif-data-quirks`. (Note: B-010 already promoted the bank draft to confirmed mid-flight.)
3. (Optional, not urgent) Monitor a few daily runs to confirm steady-state behaviour: invoice_level idempotency holds, month_summary regenerates a closed month when a late invoice arrives.

## Files to read first
- `bi-etl/dags/AI_Automations/shipping_nfe/fif_ups_orwo_monthly/README.md`
- `.../fif_ups_orwo_monthly.py` (DAG) + `docker/src/tasks/build_fif.py` (modes + transform + gate)
- `.../docker/src/sql/{fif_pull,invoices_index,present_months}.sql`
- source of truth: `bi-analytics-main/NFE/shipping_topics/42_fif_orwo_ups_invoice_file/{CLAUDE.md,pipeline.py}`
- creds for live re-test: Redshift in `bi-analytics-main/NFE/.env` (tcg_nfe); AWS = principal provides (ECR/S3)

## Notes / open
- VAT option A accepted (per-invoice files under-count VAT ~€58/0.4% on 515 cross-invoice trackings; month_summary is exact). Reconsider B if accounting wants per-invoice files to sum to the month.
- Flag upstream: bronze `invoicedate` format inconsistency is a real ingestion DQ issue (handled defensively in the DAG via `::date`).
- No pending external actions — all commits/pushes/ECR completed this session.
