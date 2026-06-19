# Dwarf trace — ORWO old carrier sweep

**Run:** 2026-06-19
**Output:** `NFE/projects/7_ORWO_tender_2026/contracts_review/_old_sweep.md`

## Steps
- Listed `0. OLD/EU/ORWO/` tree — found GLS/, UPS/ (sibling), DHL DE/ + DHL EXPRESS/ + DHL FREIGHT DE/ (siblings), FUJI RETURN EU.xlsx at root.
- Listed `0. OLD/nShift/` — full subscription doc set, ORWO addendum signed 2025-10-20.
- Read GLS Angebot 1-15STMUK PDF (16pp) via pdfplumber — full rate tables extracted.
- Read nShift Addendum PDF (11pp) — full text extracted.
- Read FUJI RETURN EU.xlsx via openpyxl — 1 sheet, 13 rows, rate table by country.
- GLS Offer ShopReturn .msg — skipped (.msg unreadable), existence noted.

## Carrier catalog
Non-UPS/DHL/AT-Post/Gull carriers found: **GLS Germany**, **Fuji Return** (unnamed carrier), **nShift** (integration platform, not a carrier).

## GLS rate verdict
Unsigned offer (2025-07-29), valid 2025-08-01 to 2025-12-31. Domestic DE: EUR 3.09-4.14 (1-10 kg), low dims risk (6 L/kg average rule, no volumetric on EU ground). EU coverage: 40+ countries. Competitive. Needs a refresh for 2026 tender — prices lapsed end-2025.

## Shortlist verdict
- GLS: **include** — activate negotiations, refresh rates. Already slated in nShift ORWO addendum (carrier list p. 8).
- nShift: **integration layer** — not a carrier shortlist item; already signed, ORWO start 2026-05-01.
- Fuji Return: **conditional** — flat per-parcel rate (no dims), broad EU coverage, but no carrier ID, no date, GB rate anomaly. Needs follow-up on carrier identity before shortlisting.
