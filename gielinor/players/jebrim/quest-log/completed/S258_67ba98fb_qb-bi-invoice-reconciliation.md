# S258 (sid8 67ba98fb) — QB↔BI carrier invoice reconciliation (topic 48)

Player: Jebrim. Continues **S250 us-lucanet-vs-bi** (topic `bi-analytics-main/NFE/shipping_topics/48_US_Lucanet_vs_BI`). Canonical record: that folder's **`findings.md`** (updated this session); this entry is the gielinor-side narrative.

## What this session did

Niklavs uploaded a new file to topic 48 — **`Transaction list by Vendor.xlsm`**, a full QuickBooks Desktop GL export (all vendors, 2025–2026, US/PCS entity). Reconciled US-entity carrier invoices **QuickBooks ↔ BI** invoice-by-invoice (numbers, then amounts), the thing the integration-DB path couldn't do.

## Arc

- **Located the carrier invoice numbers** in the `Num` column on Bill lines. Isolated shipping carriers; built `qb_carrier_transactions.parquet` (1,762 lines).
- **OnTrac was not absent** — it's the QB vendor **"LaserShip, Inc"** (acct `4731 03 Lasership/OnTrac`; LaserShip→OnTrac 2022 merger), the biggest US carrier.
- **Two-way number match** (FedEx hyphen-normalized, keyed on `invoice_source`, BI window widened to 2025-09→2026-05 for timing skew):
  - **Every BI carrier invoice is present in QuickBooks — zero BI-only, all carriers.** BI invents nothing.
  - QB→BI: OnTrac 22/22 perfect; FedEx complete bar $9k of one-offs; **Asendia 41 QB-only / $110k**; USPS unmatchable (Check-paid, no invoice number).
- **Asendia $110k decomposed** (principal's "maybe not really Asendia US shipping" hunch): only **$6.6k** (20 invoices) booked purely to `4730 Asendia` (shipping); **$103.7k** (21 invoices) is `-SPLIT-` multi-account (duties/VAT/customs — non-freight a shipping mart correctly excludes). The transaction-list export collapses split lines, so the $103.7k can't be classified further from this file.
- **Amount match for matched invoices** (`bi_carrier_invoice_amounts.parquet`, QB bill USD vs BI `SUM(charge_amount_local)`): OnTrac **+0.1%** (22/22 within 1%), FedEx **+1.4%**, Asendia **+3.5%**. **QB ≥ BI on every single invoice** — QB bundles surcharge/duty lines BI's freight rows exclude. Not noise; BI not over-counting.

## Corrections this session (harvest)

- **S250's "QB 2026 unbooked → LucaNet = accruals" finding was WRONG** — principal confirmed the *integration DB* was missing data. The QB Desktop export shows 2026 carrier Bills ARE booked. Corrected `findings.md` TL;DR #5 + added a superseded-banner to the QuickBooks section.
- **Caught my own over-claim:** presented QB gross carrier vendor totals (e.g. Asendia ~$1.18M) as "booked cost" — they overstate freight (mix Bills + standalone Checks + `-SPLIT-` non-freight; vs LucaNet/BI Asendia freight ~$445k). Flagged it rather than letting it stand. → `examine/drafts/2026-06-17-gl-vendor-total-is-not-freight.md`.
- Refined a subagent's "$109k genuine Asendia gap" claim by decomposing the split — only ~$6.6k is confirmed shipping. (Positive instance of verify-subagent-findings, not a miss.)

## Decisions / flags surfaced

- **Puerto Rico** shipments are dropped by `destination IN ('US','CA')` (coded `PR`, not `US`) — flagged to principal to confirm whether the US entity should include PR.
- USPS reconciles by total only (no invoice key) — principal confirmed USPS has no invoices.

## Pending external actions

None pending.

## Deliverables (external NFE repo — not committed by this brain close)

- `shipping_topics/48_US_Lucanet_vs_BI/findings.md` (canonical — updated: reconciliation section + amount comparison + corrections)
- `Transaction list by Vendor.xlsm` (new QB Desktop GL export, principal-supplied)
- `qb_carrier_transactions.parquet`, `bi_carrier_invoices_2026.parquet`, `bi_carrier_invoice_amounts.parquet`, `qb_only_invoices.csv`

## Follow-ups (tracked on parent S250 topic — `inventory/us-lucanet-vs-bi-resume__44773956.md` + findings.md open-items)

- Asendia `-SPLIT-` composition — needs an expanded QB export ("Transaction Detail by Account") or the backfilled integration DB to classify the $103.7k as freight vs duties/VAT.
- Tighten the FedEx/Asendia amount bias (which charge lines QB carries above BI freight).
- Re-validate the BI↔QB 2025 cost bridge via the Desktop export (not the integration DB).

## Sub-agent traces (this session)

`S_shipagent_us-qb-bi-invoice-number-characterization.md`, `S254_shipagent_us-bi-carrier-invoice-export.md`, `S_shipagent_us-qb-only-invoice-bucketing.md` (+ the per-invoice amount export agent, which wrote its parquet then died on an API socket error — file verified complete).
