# EU Tender 2026 annualization method and assumptions ledger

As of: 2026-06-10

- The method (durable even as numbers refresh): base = the 2026-Q1 book (current carrier mix; a 2025-population replay is invalid - GLS/Colis-Prive gone, DPD-PL/Maersk new at scale). Scale volume per-country: FY_2026 = Q1_2026_actual x (FY_2025_country / Q1_2025_country). 2025 monthly profile: Q1 20.7% / Q2 21.2% / Q3 17.9% / Q4 40.2% -> roughly x4.8 Q1-to-FY.
- The locking simplification: all engine fuel is flat/month-invariant (Hermes 7%, Maersk-EU 6.6% / ROW 24.75%, DHL 1.25%/5%, DPD 5%/11%), so the only seasonal cost component is PEAK. Annual cost = peak-free unit cost x annual volume + peak rate x peak-window volume. No 12-month fuel curve.
- Peak by carrier class: engines from contract rates (DHL EUR 0.19 Nov-Dec + 0.50 PiP Nov24-Dec7; Hermes/Maersk EUR 0.25 Oct-Dec; DPD none, principal-confirmed); invoiced carriers (UPS/DBS/Direct Link) get a Q4 premium DERIVED from their 2025 invoice actuals; Maersk-FR has no 2025 base so 0.25 assumed.
- Discipline: one consistent 2026 cost basis on BOTH sides (do-nothing and portfolio); routing fixed, re-priced, no peak re-routing; saving = FY_baseline - FY_portfolio. Peak fires on both sides so it largely cancels in the saving.
- Band logic: fuel is a RATE sensitivity (vary the flat rates, e.g. +/-2pp) - the annual saving is presented as a band, never a point. Q4 product-mix NOT adjusted (locked) - qualitative caveat only, hits both sides.
- Deliverable: a 4th report (annual_2026/) parallel to the Q1 routing report, plus a Q1-to-annual bridge waterfall (Q1 anchor x volume scale +/- peak +/- fuel band) and a per-carrier peak-exposure exhibit.
- Key flagged assumptions (F/P status): Hermes flat 7% fuel is above the offer's Q1 ladder (conservative); Maersk-EU 6.6% is above the carrier's stated 4-6% band; Maersk-ROW 24.75% is a placeholder; UPS GRI held at 5% vs own research 5.9%; DPD ~9% discount is fitted, not in the offer; volume assumes 2026 Q2-Q4 track 2025's shape at 2026-Q1's level.
- Open carrier chases: Maersk EU fuel schedule + 6.6%-vs-band reconciliation, Maersk real peak schedule, UPS GRI confirm, DPD discount confirm, DHL thin-flat Sperrgut waiver (upside-only, pending Stefan).
- Numbers in the source file (EUR 275,484 / 9.32% Q1, ~2.56M FY parcels) are that date's vintage - the live headline lives in the bank/domains/ eu-tender digest; the method above is what to reuse.

Source research: [[2026-06-10-eu-tender-annualization-method-and-assumptions]] - full sources and detail there.
