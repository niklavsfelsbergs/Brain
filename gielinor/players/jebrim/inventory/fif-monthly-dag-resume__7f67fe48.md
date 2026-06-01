---
quest: S116_shipping-agent-fif-monthly-skill
sid8: 7f67fe48
ts: 2026-05-29 17:00
---

# Resume — FIF UPS-ORWO report DAG (S116)

**Status:** in-progress (parked). Code complete, deployed (image + branch), live-validated. Awaiting principal: PR merge + first DAG run.

## Where we are
Built a **daily bi-etl DAG** `fif_ups_orwo_monthly` that delivers the FIF (UPS ORWO) report to SharePoint in two forms under `Share/InvoiceDataShipping/UPS_FiF_reports/`:
- `invoice_level/` — one xlsx per invoice as they arrive (`{inv}_{invdate}_{procdate}.xlsx`), folder-as-ledger, process-once.
- `month_summary/` — whole-month report; month M "closed" once an M+1 invoice exists; regenerates if a late M invoice arrives (driven by invoice_level's months_touched). VAT = option A (per-invoice isolation).

Transform ported verbatim from the validated NFE standalone pipeline. Fixed a real bronze DQ bug (invoicedate mixed ISO + US M/D/YYYY → normalize `::date`).

**Deployed + validated 2026-05-28:** ECR image `fif_ups_orwo:latest` pushed (digest ebfe767). Brain-side bi-etl commits on branch `feat/fif-ups-orwo-monthly`: `39a1d9d42` (v1 monthly) + `de3e74f87` (daily redesign), pushed. Live smoke (tcg_nfe → local, no SharePoint): invoice_level 75 files, month_summary built Jan–Apr (May held, no June); Mar=20 invoices (date-fix payoff), Apr exact €104,312.29. Only the SharePoint PUT is unexercised (needs in-cluster `sharepoint_credentials` Variable).

## Next concrete step
Two principal actions, then verify:
1. **Open + merge the PR** — https://github.com/picanova/bi-etl/pull/new/feat/fif-ups-orwo-monthly (gh CLI absent here, so it wasn't auto-created). Branch = both commits; net = the daily two-folder design.
2. **Run the DAG** `fif_ups_orwo_monthly` (first run backfills 75 invoice files + Jan–Apr summaries). Watch the `month_summary → upload_sharepoint` path land files under `Share/InvoiceDataShipping/UPS_FiF_reports/`.
3. If the **SharePoint PUT** errors (folder perms / Variable shape), that's the one likely fix point — adjust `utils/sharepoint_upload.py` or the DAG env, rebuild + re-push image.

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
