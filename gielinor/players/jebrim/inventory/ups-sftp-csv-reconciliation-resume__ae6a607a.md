---
quest: S142_ups-sftp-csv-reconciliation
sid8: ae6a607a
ts: 2026-06-01 00:00
open_dep: Niklavs to send the drafted UPS message; optional verify of 2003636503 + PDF totals
---

# Resume — UPS SFTP invoice reconciliation

**Status:** in-progress (core reconciliation shipped; follow-ups are principal-owned).

**Where we are:** Reconciled the full UPS portal "My invoices" list (100 rows) against our SFTP
CSV feed. 83/100 present; 17 missing. The only material gap = 11 credit notes (account 698W75,
25 May 2026, `2003636503`–`2003636513`, ≈€110.5k) that arrived as PDF only and never entered the
CSV/bronze feed. Other 6 misses are €0,00 Inland/Export on accounts not in our feed. A short message
to UPS is drafted (not sent).

**Next concrete step:** Waiting on Niklavs to send the UPS message. If asked to follow up: (1) confirm
`2003636503` ↔ `A0000698W75-20260525-1.pdf`; (2) pull `Gesamtkreditbetrag` from all 11 PDFs for an
exact missing-credit total to cite to UPS. Note AWS creds were temporary STS and are likely expired —
re-request before touching S3 again. Cached data at `/tmp/ups_inv/` may also be gone after reboot.

**Files / paths to read first:**
- `gielinor/players/jebrim/quest-log/in-progress/S142_ae6a607a_ups-sftp-csv-reconciliation.md`
- `bi-etl/dags/shipping_invoice_cost/SFTP/UPS/ups_sftp.py` (prod DAG; reads `ups_sftp_config`)
- `bi-etl/dags/shipping_invoice_cost/SFTP/UPS/sql/copy_to_bronze_temp2.sql` (CSV column mapping)
- S3: `s3://etl-poc-dev/shipping_providers/ups_sftp/archive/` (PDFs + CSVs)
