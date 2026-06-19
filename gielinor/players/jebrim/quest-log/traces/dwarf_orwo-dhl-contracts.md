# Trace: ORWO DHL contracts review dwarf
**Run:** 2026-06-19
**Deliverable:** `NFE/projects/7_ORWO_tender_2026/contracts_review/dhl.md`

## Run log

- Globbed current + old ORWO DHL folders — confirmed file inventory
- PDF text extraction: most source docs are scanned images; VTR/AN1/AN2/AN3 are digital text — extracted cleanly via pymupdf
- Rate card PDFs (image-only) rendered as images and read visually — content cross-validated against digital AN1/AN2
- SEPA sendmoments extracted — confirmed entity as sendmoments Studio GmbH, Munich
- AN3 (88 pp billing arrangements) searched for all "sendmoments" references — found 3 billing numbers

## Findings summary (5–7 lines)

**Account IDs:** Customer 5311934365 (EKP-Nr), contractual number 40440743. Contract effective 28.10.2025, updated 30.12.2025. DHL Express separate account DE102981753 (signed 13-08-2025).

**Product list:** DHL PAKET domestic (EUR 3.35–10.55 weight-break), DHL Kleinpaket (EUR 2.79 flat ≤1 kg), DHL PAKET International Premium + Economy/CDP (zone 1–6, base + per-kg), Warenpost International Premium + Economy (zone 1–6, base + per-100g), DHL Retoure / Retoure Online, DHL Express International + Economy Select (via DE102981753), DHL Freight (admin only — no rates).

**POST/Warenpost verdict: CONFIRMED.** Warenpost International (settlement code 66, billing numbers 5311934365 66xx) is the Deutsche Post cross-border mail product — invoiced by Deutsche Post AG under the same DHL account. This IS the rate basis for the "POST" carrier (~EUR 82k/mo, 99% estimated). Rate formula: base price + (100g increments × 100g rate), keyed by destination country (zone 1–6 lookup) and service level (Economy vs Premium). Weight is the only data field needed for pricing; dims are NOT needed for pricing (only for eligibility check against 1 kg / 35.3×25×10 cm envelope).

**Dims dependence:** Warenpost eligibility needs dims (max 10 cm height, max 35.3×25 cm footprint, max 1 kg). For Paket base pricing, dims are only needed for bulky goods surcharge. 77% dims NULL means we can price but cannot confirm eligibility for most shipments. Weight is also 77% NULL in the mart — this is the core gap for Warenpost repricing.

**Keyability:** DHL PAKET and Kleinpaket domestic — high (weight available, simple lookup). DHL PAKET International — good (weight + country). Warenpost International — partial (23% where weight known; 77% requires estimation or manifest data). DHL Express — good from weight + country + product type.

**sendmoments flag:** sendmoments Studio GmbH (Munich, customer 6388746126) ships under the ORWO account 5311934365 as a "different mailer." Three dedicated billing numbers exist: 5311943655333 (PAKET INT. SENDMOMENTS), 5311934365**6623** (WPI SENDMOMENTS), and 5311934365**6239** (KLEINPAKET SENDMOMENTS). Their own SEPA mandate exists (DE75370400440210932000) but current AN3 shows ORWO's bank as the payer for at least some sendmoments billing numbers — possible consolidation. Scope question: are sendmoments costs included in the ORWO tender or separated?
