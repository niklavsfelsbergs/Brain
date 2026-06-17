---
quest: S250_us-lucanet-vs-bi-reconciliation
sid8: 44773956
ts: 2026-06-17 (invoice-recon session)
open_dep: none
---
Status: in-progress

Where we are: Added a **QB↔BI invoice-number reconciliation** to topic 48 (new file `Transaction list by Vendor.xlsm` = QB Desktop GL export, all vendors 2025–2026, US/PCS entity). Two-way invoice-number match complete; `findings.md` updated with a new section + corrections. Key outcomes:
- **Integration-DB "$706/unbooked → LucaNet=accruals" finding is WRONG** — principal confirmed the integration DB was missing data. QB Desktop export shows 2026 carrier Bills ARE booked (Asendia 26B*, FedEx, OnTrac=LaserShip). findings.md TL;DR #5 + QB-section banner corrected.
- **OnTrac = vendor "LaserShip, Inc"** in QB (acct 4731 03 Lasership/OnTrac; LaserShip→OnTrac 2022 merger).
- **Direction BI→QB: every BI carrier invoice is in QB (zero BI-only).** Direction QB→BI: OnTrac 22/22 perfect; FedEx complete bar $9k of one-offs; Asendia 41 QB-only / $110k.
- **Asendia $110k decomposed (backs principal's "maybe not really Asendia US shipping" hunch):** only 20 invoices / **$6.6k** booked purely to `4730 Asendia` (shipping); **21 invoices / $103.7k are `-SPLIT-`** (multi-account, likely duties/VAT/customs — non-freight). At most ~$6.6k is confirmed shipping freight BI lacks. Transaction-list export collapses splits → can't classify the $103.7k from this file.
- **USPS unmatchable** — QB Check-paid, no invoice numbers (BI has 137). Totals-only. Principal confirmed USPS has no invoices.
- **Caveat surfaced:** QB gross vendor totals ≠ freight (mix Bills+Checks+SPLIT non-freight). QB Asendia gross 2026 ≈ $1.18M vs LucaNet/BI freight ~$445k — that spread is split/payment-type noise, not coverage.
- **Amount comparison DONE for matched invoices** (`bi_carrier_invoice_amounts.parquet`): OnTrac +0.1% (22/22 within 1%), FedEx +1.4%, Asendia +3.5%. QB ≥ BI on every invoice — QB bundles surcharge/duty lines BI freight rows exclude. Numbers + amounts both reconcile.

Next concrete step (principal soft-approved chasing Asendia):
1. **Asendia `-SPLIT-` composition** — get bill split detail (expanded QB export "Transaction Detail by Account", or QB bill-line table once integration DB backfilled) to classify the $103.7k as freight vs duties/VAT.
2. Amount-level QB↔BI per-invoice recon (clean freight basis: Bills only, strip SPLIT non-freight).
3. Re-validate BI↔QB 2025 cost bridge via the Desktop export (not the integration DB).
Plus still-open from prior session: February revenue ~10% LucaNet residual (test recognition timing in ol_gold); confirm LucaNet accrual basis with accounting.

Files / artifacts (topic 48, NFE repo — not committed by brain close):
- `shipping_topics/48_US_Lucanet_vs_BI/findings.md` (canonical — updated 2026-06-17)
- `Transaction list by Vendor.xlsm` (new QB Desktop GL export)
- `qb_carrier_transactions.parquet`, `bi_carrier_invoices_2026.parquet`, `qb_only_invoices.csv`
- QB connection: `NFE/.env` (`QB_*`)

Pending drafts: none. Harvest candidates at alching: OnTrac=LaserShip in QB; QB-integration-DB-was-incomplete correction; QB gross-vendor-≠-freight.
