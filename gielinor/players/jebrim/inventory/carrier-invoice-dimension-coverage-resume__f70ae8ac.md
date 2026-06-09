---
quest: S167_carrier-invoice-dimension-coverage
sid8: f70ae8ac
ts: 2026-06-09 13:13
open_dep: 2 feed-currency questions (DPD DE post-2024-09 feed? Ambro retired?) + optional report-doc render
---

# Resume — carrier invoice dimension-data coverage audit

## Status
in-progress (deliverable shipped: corrected coverage map saved to bank draft + returned in chat; 2 named verification follow-ups remain open).

## Where we are
Answered "which carriers provide dimension data on invoices + how complete" across the RAW upstream layer for all ~21 carriers. A first broad pass (silver name-scan) false-negatived ~14 carriers; UPS-skepticism from Niklavs triggered a deep re-check that overturned it, then a 4-agent fan-out re-checked every "none" carrier. Corrected map is in `bank/drafts/notes/projects/2026-06-09-carrier-invoice-dimension-coverage.md`.

## Corrected headline
~10 carriers carry real measured dims (Maersk/OnTrac/FedEx/Asendia/USPS/DB-Schenker/Direct-Link live; Yodel/UPS partial; DPD-DE/Ambro/Hermes stale), 5 carry oversize-surcharge billing signal only (DPD-UK/GLS/DPD-PL/APG/Colis-Privé), 3 give nothing (DHL DE/America/ORWO). Method lesson: profile the WIDE bronze source + charge-description VALUES, never name-scan narrow silver.

## Next concrete step (principal's call — none blocking)
1. (optional) Render the bank-draft map as a persisted report doc / HTML if Niklavs wants a shareable deliverable.
2. Close the 2 feed-currency questions: did DPD DE move to a post-2024-09 feed that keeps dims? Is Ambro retired or shipping under a renamed feed?
3. (optional) Reconcile carrier→table identity against the gold provider SQL (`bi-etl/dags/shipping_mart/fact_shipment_invoice_lines/sql/providers/`).
4. Promote the bank draft to `bank/notes/` at next alching.

## Files to read first
- `bank/drafts/notes/projects/2026-06-09-carrier-invoice-dimension-coverage.md` — the corrected map (the deliverable).
- `quest-log/in-progress/S167_f70ae8ac_carrier-invoice-dimension-coverage.md` — broad pass + UPS/Ambro/APG/Schenker corrections.
- `quest-log/in-progress/S167_f70ae8ac_dpd-dimension-coverage-reaudit.md` — DPD sub-trace.
