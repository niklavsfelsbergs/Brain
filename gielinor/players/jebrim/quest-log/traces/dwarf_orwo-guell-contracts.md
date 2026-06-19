# Trace: ORWO Güll Contract Review

Date: 2026-06-19
Dwarf: Jebrim-dwarf
Task: Read Güll CH parcel contract (2025) and produce structured review note for ORWO tender.

## Run log

- Read PDF (11 pages) via pdfplumber — all pages extracted cleanly, no OCR gaps.
- Pages 1-6: contract body (parties, scope, liability, duration).
- Page 7 (Anlage 1): product conditions for PostPac Priority/Economy + letter formats.
- Page 8-9 (Anlage 2): handling services detail incl. customs clearance spec and returns.
- Pages 10-11 (Anlage 3): price tables — parcel rates, letter rates, handling fees, add-ons.
- Wrote guell.md to contracts_review/ with 7 sections per brief.

## Key findings (4-5 line summary)

Parties: ORWO Photolab GmbH (Bitterfeld-Wolfen) buys handling + CH dispatch from Güll GmbH (Lindau). Contract in force from 01.08.2025, indefinite, prices fixed to 31.12.2025.

Rate basis: Pure weight-break per-parcel (up to 2 kg / 10 kg / 30 kg) in CHF, two service levels (PostPac Priority E+1 / Economy E+2). NO density pricing, NO pallet-based rates — the Picanova EU tender density/pallet concern does NOT apply here. Güll is a handling intermediary; Post CH AG is the actual carrier.

Dims dependence: Negligible for standard parcels. Sperrgut (oversized/bulky, rate 29-39 CHF vs 7-23 CHF normal) is the only dimension-gated tier but trigger definition is absent from contract. At 1,000 parcels/year, financial exposure is small. 77% NULL dims problem does NOT block repricing normal parcels.

Keyability: HIGH for base parcel rates (weight-break lookup + service flag). Blocking gaps: (a) Sperrgut flag or dim coverage needed to classify outliers; (b) CHF/EUR split requires FX at invoice date; (c) customs declaration frequency needed to key 40 EUR/declaration fee; (d) declared value per shipment needed for 8.1% Swiss VAT component.

Open question to resolve first: does ORWO's photobook product mix ever produce Sperrgut-sized parcels? If not, the dim-coverage gap is irrelevant.
