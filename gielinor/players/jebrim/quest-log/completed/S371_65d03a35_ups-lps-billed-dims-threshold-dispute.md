# S371 — UPS LPS billed-dims threshold dispute

**Player:** Jebrim · **sid8:** 65d03a35 · **Date:** 2026-06-26 · **Status:** completed (deliverable shipped)
**Continues:** the EU-tender UPS oversize arc — [[S370_0643e962_ups-retention-and-lps-treatment]] (resume `ups-retention-discount-resume__0643e962.md`) and the S199 "LPS fires off UPS's dimensioner" ruling.

## Ask

Principal's tip: UPS may apply LPS at a 300 cm L+G threshold when the contract is 325 cm — making every LPS on a parcel whose **UPS-billed** L+G is in [300, 325) disputable/refundable. Feeds the disputed-oversize pool the tender engine books at 0% recovery (~€100k/Q1). Confirm the contract threshold; compute the [300,325) count + €; size the refundable pool; flag the engine `BILLABLE_LPS_BANDS` implication. Use UPS's *billed* dims, not our declared geometry.

## What I did / found

1. **Contract threshold = 325 cm — confirmed.** `UPS Contract 04.24.pdf` Anlage B (Seite 36–37), "Angepasste Größen-Varianz / Paket-Toleranzwerte": Großpaket tolerance **25 cm**, applied *exclusively to invoice corrections (Rechnungskorrekturen)*. Mechanism = 300 cm tariff limit + 25 cm correction tolerance → operative 325 cm for dimensioner-driven LPS. (Over-max 400+19=419 = engine's `MAX_LENGTH_PLUS_GIRTH_CM`, confirms the +tolerance reading.)
2. **Source departure (justified).** Mart `fact_shipment_invoice_lines` has no dims; `fact_shipments.length_plus_girth_cm` is *declared*; `enterprise_silver.ups_invoices` (S199 source) has no dims. UPS billed dims survive **only** in `enterprise_bronze.csv_ups_zip_invoicedata` — `packagedimensions` = dimensioner/billed; `detailkeyeddim` = declared; `detailkeyedbilleddimension` empty. Surcharge € and dims sit on **separate rows** of the same trackingnumber (€101.80 charge row has empty dims; companion net=0 LPS row carries the reading).
3. **The verdict inverts the tip.** Window ≈ 2026 H1 (bronze feed: txn 2025-12-31→2026-06-12). 924 standing-LPS parcels (€94,369 net); 537 (58%) have measured dims. Of those: **[300,325) = 1 parcel / €102; <300 = 0; ≥325 = 536 / €54,768.** Charges floor hard at L+G 326. **UPS honours 325 where it dimensions.** Refundable pool on threshold grounds ≈ €0.
4. **Engine: no change.** Declared `c_300_325` band (351 parcels, €35.9k) — all measure ≥325 by UPS's tape → `BILLABLE_LPS_BANDS` is correct; moving c_300_325 to disputed would mis-reclassify ~€36k of legit charges. Also 180 parcels (€18.3k) declared <300 but UPS-measured ≥325 (S199 under-declaration), which if anything *over*-states the dispute pool — consistent with the 0% recovery assumption.
5. **42% no-dim caveat.** 387 standing-LPS parcels (€39,498) have no dimension in the feed; 382/387 are immature Q2 invoices — a feed-maturity artifact, not refundable. Separate "produce-the-dims" substantiation ask possible; re-run when Q2 matures.

## Decisions

- **Tip not supported; engine left unchanged.** Annotated (not altered) `BILLABLE_LPS_BANDS` in `2_analysis/carrier_engines/ups/constants.py` and `1_offers/.../extract_incidence.py` with the verification.
- Departed from mart-first to bronze deliberately — documented in the SQL header and findings; mart/silver provably cannot carry billed dims.
- Quest graduated to completed/ this session — deliverable shipped + committed, no open dependency (the Q2-mature re-run is optional, not a blocker).

## Pending external actions

None pending.

## Deliverables (NFE, committed 4298d67 — never pushed)

- `1_offers/picanova/UPS/lps_threshold_dispute_findings.md` (writeup)
- `1_offers/picanova/UPS/calculation/sql/pull_lps_billed_dims.sql` + `extract_lps_dispute.py` (reproducible)
- `1_offers/picanova/UPS/findings.md` §9.4, `constants.py`, `extract_incidence.py` (annotations)

## Optional follow-up (not a blocker)

- Re-run `extract_lps_dispute.py` once the bronze feed extends past 2026 H1 / Q2 invoices mature (closes the 42% no-dim gap).
- If a hard lever is wanted: substantiation ask to UPS for the no-dim LPS lines.

**Cascade.** NFE `bi-analytics-main` only — UPS offer findings + calc + engine annotations (commit 4298d67). No other repo touched.
**Main-brain changes.** One bank draft harvested: `bank/drafts/notes/carriers/ups-billed-dims-provenance.md` (UPS billed-dim source/shape). No identity-layer or confirmed writes.
