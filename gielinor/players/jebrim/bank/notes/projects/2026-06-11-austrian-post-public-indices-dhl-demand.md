# Austrian Post fuel/FX indices + DHL Express demand surcharge - public-data mechanics

As of: 2026-05-27

- AT diesel surcharge (TKZ family): driver is the BMWET weekly gross diesel price (published Thursdays, bmwet.gv.at); surcharge adjusts monthly using the PREVIOUS month's max gross diesel price. Mechanism corroborated by TKA and GLS Austria.
- Austrian Post's own D-tier card (carrier-stated range ~0%-32%, "typically 4%, currently 12%") is NOT public; the TKA tier table (0% at 0.85 EUR/L up to ~22.15% at 2.25 EUR/L) is only a mechanism proxy, not a substitute. Tier card is a carrier ask.
- March 2026 AT diesel spiked from ~1.56 to ~2.20 EUR/L (monthly maxes: Jan 1.509, Feb 1.546, Mar 2.204, Apr 2.228) - consistent with the carrier's "currently elevated" narrative.
- EUR/CHF convention (the load-bearing FX finding): the carrier's "EUR/CHF 1.06 baseline / currently 1.09" is the RECIPROCAL of the ECB reference rate (EUR per 1 CHF = 1 / ECB CHF-per-EUR). ECB series EXR.M.CHF.EUR.SP00.A.
- CH lane billing rule: previous month's average reciprocal, uplift = (rate - 1.06) / 1.06. Q1 2026 reciprocals: Jan 1.0784 (+1.7%), Feb 1.0940 (+3.2%), Mar 1.0996 (+3.7%).
- DSV diesel-floating (per-pallet trucking driver): EU Commission Weekly Oil Bulletin Germany diesel vs Q4-2005 average; Stueckgut +/-0.5pp per +/-4% diesel move, LTL/FTL +/-1.0pp. Switched monthly -> weekly on 2026-03-16 (Q1 replay: Jan/Feb/early-Mar flat-monthly). Historical monthly values PDF-gated.
- DHL Express demand surcharge, active 01.10.2025-16.02.2026: Domestic Time Definite 0.10 EUR/kg flat; Intl Day Definite (Economy Select) 0.15 EUR/kg flat; Intl Time Definite a zone-pair matrix 0.10-1.90 EUR/kg (Europe->Americas 0.50 EUR/kg).
- Gotcha: DHL publishes only the CURRENT demand period - the matrix gets overwritten at each rollover, no public historical snapshot. Capture before rollover or request the PDF.

Source research: [[2026-05-27-austrian-post-public-indices-and-dhl-express-demand]] - full sources and detail there.
