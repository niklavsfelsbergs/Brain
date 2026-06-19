# Dwarf trace: ORWO Austrian Post contract review
**Date:** 2026-06-19
**Dwarf:** Jebrim-dwarf (spawned for ORWO tender recon)
**Deliverable:** `NFE/projects/7_ORWO_tender_2026/contracts_review/austrian_post.md`

## Run log

- Rate Card PDF (150 KB, 3 pages, Excel-derived) -- extracted via pdftotext; clean machine text, fully readable.
- T&C PDF (1.5 MB, 9 pages, scanned/image) -- pdftotext yielded ~13 lines; OCR'd via pymupdf + tesseract (English tessdata, deu not installed). All 9 pages recovered. Document is a 2024-dated offer letter with 2025 tariffs structurally; 2026 rate card overrides pricing.
- No Factsheet found in file set (referenced 3x in rate card -- fuel, volumetric, rural surcharge). Flagged as open question.
- Tender project folder exists: `contracts_review/` already had `guell.md`; `austrian_post.md` written.

## Findings summary

- **Entity/validity:** Austrian Post International Deutschland GmbH (Bonn) <-> ORWO Net GmbH (Bitterfeld-Wolfen). Rate card: 01.01.2026--31.12.2026.
- **Service list:** Paket AT B2C (outbound), Kleinpaket, Kleinpaket Plus, Paket AT Retoure (return). AT domestic only. Pallet trunk haul billed separately (EUR 125 Wolfen->Salzburg, EUR 134 Wolfen->Troisdorf).
- **Dims dependence verdict:** Base rates are weight-only (two bands: <=2 kg and <=30 kg). Sperrgut klein/gross (4.00/7.80 EUR) and Volumengewicht require L/W/H -- NOT keyable with 77% NULL dims. Kleinpaket eligibility (max 235x162x5 mm) also dims-dependent.
- **Keyability bottom line:** Base rate + road pricing (0.27 EUR flat) + fuel surcharge (diesel-index) are fully keyable from weight + product code + date. Oversize and volumetric surcharges are a blind spot. Factsheet needed before full reprice is possible.
- **Open questions:** Factsheet (volumetric divisor, rural rate), product code mapping in manifest, T&C 2026 contract letter, Warenversand International 2026 status, zone-mix validation vs AT ZIP data.
