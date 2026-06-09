# S142 — UPS SFTP invoice reconciliation: portal vs CSV feed

**Player:** Jebrim · **sid8:** ae6a607a · **Opened:** 2026-06-01

## Ask

Niklavs asked where the UPS SFTP server is defined in `bi-etl`, then to check whether
specific UPS invoices/credit notes are present in what we've received, and finally to
reconcile his full UPS portal "My invoices" list (100 rows) against our SFTP CSV feed and
draft a message to UPS about the gap.

## What happened

- **SFTP location.** The UPS SFTP host is **not** in git — it lives in the Airflow Variable
  `ups_sftp_config` (JSON: host/port/user/creds). DAGs at `bi-etl/dags/shipping_invoice_cost/SFTP/UPS/`
  (`ups_sftp.py` prod, `ups_sftp_listing_temp.py` diagnostic) read it and land files in S3
  `etl-poc-dev/shipping_providers/ups_sftp/{raw,transformed,archive}`. `raw` is empty (processed
  files move to `archive`); `archive` had 187 files (73 CSV + 114 PDF).
- **Reached the data via S3, not SFTP** — Niklavs supplied temporary AWS creds for account
  123038732324 (bi-account). Synced the archive CSVs + PDFs to `/tmp/ups_inv/` and searched.
- **Single-invoice lookups.** `2003636507` → PDF-only (`A0000698W75-20260525-5.pdf`), a
  `Rechnungskorrektur` (credit note), absent from every CSV. `2003611837` → present in **both**
  CSV (`A0000698W75-20260417.csv`, as `ADJ` rows, invoice field `002003611837`) and PDF. So credit
  notes *can* flow through CSV; the 25-May batch specifically did not.
- **Full reconciliation (100 portal rows).** Matched on invoice number with leading zeros
  normalized (portal pads to 15 digits, CSV field 6 to 12). **83/100 present, 17 missing**, in two buckets:
  - **11 credit notes, 25-May, account 698W75 (`2003636503`–`2003636513`)** — PDF-only, never in CSV.
    ≈ **€110,513** in credits → UPS cost in `sl_bronze.shipping_costs` overstated by ~€110.5k for the period.
    The same-date Import invoice (`838635985`) *did* arrive as CSV; only the credit batch dropped.
  - **6 zero-value Inland/Export, accounts `V39131` + `86W36A`** — those accounts aren't in our
    SFTP feed at all; every missing row is €0,00 → immaterial. (Account `80668E` also isn't a feed
    prefix yet its 3 invoices *are* present, bundled in another account's CSV.)
- **Deliverable.** Drafted a short message to UPS asking why the 11 credit notes (698W75, 25 May 2026,
  `2003636503`–`2003636513`) came as PDF only with no CSV billing data, and to re-send the CSV.

## Decisions

- Match key = invoice number with leading zeros stripped (robust across the portal's 15-digit and
  the CSV's 12-digit zero-padding, and across `I` invoices vs `2003…` credit notes).
- Field 6 of the raw archive CSV is `invoicenumber`; field 5 is `invoicedate` (per the bronze COPY
  column mapping in `bi-etl/.../SFTP/UPS/sql/copy_to_bronze_temp2.sql`). Latest invoicedate in feed: 2026-05-29.

## Pending external actions

None pending. (AWS creds were temporary STS — now likely expired; profile `bi` in `~/.aws/credentials`.
Downloaded data cached at `/tmp/ups_inv/`, outside the brain.)

## Open follow-ups (principal-owned)

- Niklavs to send the UPS message (drafted, not sent by me).
- Optional: confirm `2003636503` ↔ `A0000698W75-20260525-1.pdf` (the one PDF not yet mapped), and
  pull the exact `Gesamtkreditbetrag` from all 11 PDFs for a non-portal-derived missing-credit total.
- Domain insight worth a bank note once the picture settles: *UPS credit notes sometimes arrive
  PDF-only and never enter the CSV/bronze feed, silently overstating UPS cost.*
