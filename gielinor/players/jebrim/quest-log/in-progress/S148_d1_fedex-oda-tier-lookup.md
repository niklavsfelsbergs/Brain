# [[S148_104c786b_eu-tender-dhl-paket-round2|S148]] D1 — FedEx ODA tier postcode lookup (Jebrim, EU Tender 2026)

Dwarf D1, parent session e59202cf. Build deterministic postcode→tier lookup from FedEx
Extended-Area (ODA/OPA) workbook + coverage report. Feeds FedEx remote-area surcharge in engine rebuild.

## Progress

- Verified source: `carrier_responses_to_open_questions/fedex/round_2/ODA_OPA_tiers_codes (1).xlsx`,
  single sheet "Postal Codes and Tiers ", 67,515 rows x 13 cols, effective Jan 12, 2026.
- Header band verified by reading rows: column-header row is **row 10**, data starts **row 11**.
  - A(0)=Country, B(1)=Country Code, C(2)=City, D(3)=Begin Postal Code, E(4)=End Postal Code
  - Row 9 merged band: F+G = "Out-of-Pickup Area Surcharge" (OPA), H+I = "Out-of-Delivery Area Surcharge" (ODA)
  - Row 10 sub-headers: F(5)=OPA Parcel, G(6)=OPA Freight, **H(7)=ODA Parcel, I(8)=ODA Freight**
  - Picanova SHIPS OUT → relevant surcharge is **ODA** (cols H/I). Keeping ODA Parcel + ODA Freight tiers.
  - Tier values: `Tier A`/`Tier B`/`Tier C`/`No`. Stripped "Tier " prefix; "No"/blank → null.

## Deliverables built

- **D2 build script:** `2_analysis/carriers/fedex/rate_tables/build_oda_tiers.py` — openpyxl(data_only) →
  polars, regenerates parquet from the xlsx. Docstring names source + effective date (Jan 12 2026) + the
  ODA-not-OPA decision. Runs clean: `wrote oda_tiers.parquet : 67505 rows`.
- **D1 lookup parquet:** `2_analysis/carriers/fedex/rate_tables/oda_tiers.parquet`, 67,505 rows.
  Cols: destination_country_code (ISO2), city, begin_postal (str,nullable), end_postal (str,nullable),
  oda_parcel_tier ("A"/"B"/"C"/null), oda_freight_tier ("A"/"B"/"C"/null). One row per source data row
  (67,515 sheet rows − 10 header-band rows = 67,505; rows with blank Country Code dropped).

## Coverage report

**(a) Total rows:** 67,505.

**(b) Range-based vs city-only:**
- Postal-RANGE based (begin AND end populated): **62,539** (92.6%). begin/end are always both populated or
  both null — 0 rows have only one side.
- CITY-only (no postal codes): **4,966** (7.4%). These are un-attributable from a zipcode (no postal key) —
  they live in 70 fully city-only countries (see (d)).

**(c) ODA tier distribution (67,505 rows):**
- ODA **Parcel**: A=12,362 · B=42,782 · C=4,019 · No/blank(null)=8,342
- ODA **Freight**: B=49,473 · C=4,019 · No/blank(null)=14,013  (no "A" tier exists for freight)

**(d) Picanova key destinations — all 100% postal-RANGE, zero city-only:**
| Country | rows | range | city-only | ODA-parcel tiers | postal shape |
|---|---|---|---|---|---|
| CH | 75 | 75 | 0 | all B | 4-digit numeric, uniform |
| NO | 1098 | 1098 | 0 | C=569, B=529 | 4-digit numeric |
| GB | 168 | 168 | 0 | all B | **alphanumeric** outward-prefix + `X` placeholder (`HS1X`, `IM2X`); begin==end per row |
| DE | 44 | 44 | 0 | C=31, B=13 | 5-digit numeric |
| FR | 397 | 397 | 0 | C=33, B=364 | 5-digit numeric (leading zeros present, e.g. `04100`) |
| NL | 7 | 7 | 0 | all B | 4-digit numeric |
| IT | 836 | 836 | 0 | B=813, C=23 | 5-digit (leading zeros, e.g. `00051`) |
| ES | 1752 | 1752 | 0 | B=1605, C=147 | 5-digit, **but 77 rows show stripped leading zero** (`5514`=`05514`) |
| SE | 1642 | 1642 | 0 | B=719, C=923 | 5-digit numeric |
| CZ/HU/AT/PL | 24/218/13/201 | all | 0 | all/mostly B | numeric |
- BE absent (no FedEx ODA entries → no remote-area surcharge applies to BE destinations).
- EU city-only exposure: **HR (Croatia, 89 rows)** and **RS (Serbia, 81)** are fully city-only.

**(e) Attribution mechanic — recommendation:**
- **Mechanic: exact postal-range containment**, matched on `(destination_country_code, zipcode)`. For a numeric
  zipcode: `begin_postal <= zip <= end_postal`. 35,645 ranges are point codes (begin==end); 26,370 are true spans.
- **Compare numerically, not lexically.** Cast to int: `int(begin) <= int(zip_norm) <= int(end)`. Reason: the
  source strips leading zeros on some rows (ES `5514` = `05514`; 9 countries show mixed widths from this), so a
  raw string compare misorders. Within any single row begin/end always share char-length (0 mismatches), so a
  zero-pad-to-row-width string compare is the equivalent safe alternative. Normalize the mart zipcode the same way
  (whitespace strip, take leading digits, int-cast) before comparing.
- **CH is cleanly range-attributable** — 75 ranges, uniform 4-digit numeric. NO/DE/FR/IT/SE/etc likewise.
- **GB is NOT numeric — special-case it.** Codes are UK outward-code prefixes with a trailing `X` wildcard
  (`HS1X` = postcode district HS1). The engine must match on the **outward-code district** of the GB shipping
  zipcode (alpha prefix + leading digit(s)), not numeric containment. begin==end for every GB row, so it's a
  prefix-membership set, not a span. CA (356 rows) is the only other alphanumeric country (not a Picanova focus).
- **City-only countries are un-attributable from zipcode** (4,966 rows, 70 countries — incl. EU HR + RS). For
  these, the engine cannot assign an ODA tier from (country, zipcode) alone; either skip the surcharge or
  fall back to a city-name match if the mart carries destination city. Flag HR/RS for Niklavs as the only
  EU/near-EU city-only gaps.

## Status: COMPLETE
All three deliverables built; parquet regenerates from script; coverage facts verified against the data.
