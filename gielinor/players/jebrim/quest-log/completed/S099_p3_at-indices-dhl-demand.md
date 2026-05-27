# S099_p3 — Austrian Post public indices + DHL Express demand surcharge (penguin run-log)

**Role:** penguin (research operative), player Jebrim
**Brief:** Four independent public-data lookups for EU Tender 2026 (Picanova carrier tender):
A) Austrian Post AT diesel fuel surcharge (Treibstoffzuschlag) — series + monthly % Jan/Feb/Mar 2026 + current
B) EUR/CHF monthly avg Oct 2025–Apr 2026 (ECB), uplift vs €1.06 baseline
C) DSV diesel-floating index — current + Q1 2026 values, computation method
D) DHL Express Demand Surcharge (Bedarfszuschlag) — per-weight/zone amounts for 2025/26 window (active 01.10.2025–16.02.2026, overlaps Jan 1–Feb 16 2026)
**Replay window:** Q1 2026 (Jan/Feb/Mar)
**Deliverable:** `research/2026-05-27-austrian-post-public-indices-and-dhl-express-demand.md`

## Turn log

- T1: Read research.md + spawning-penguins.md + meta. Brief understood: 4 clusters, web-only, cite every figure inline. Opening broad scout across all four.
- T2: Source map built — 4 clusters, ~8 load-bearing sources. A: BMWET kosten.html confirmed as live weekly diesel series (got full Jan-May 2026 table, 1.477→2.228 €/L; late-Mar/early-Apr spike supports carrier's "12% / war in Iran"). D: DHL.de surcharges page confirmed Oct 1 2025–Feb 16 2026, €0.10/kg domestic, €0.15/kg intl day-definite, time-definite intl matrix €0.10–€1.90/kg by zone. C: DSV diesel-floating = EU Weekly Oil Bulletin basis (Q4 2005 ref), switched monthly→weekly 2026-03-16, current piece-goods 13.5% wk22. B: ECB CHF page is daily only (~0.91–0.92 CHF/EUR); monthly avgs need data portal.
- T3: Fetching ECB data portal monthly avgs, post.at Treibstoffzuschlag page, DSV historical-monthly page.
- T4: post.at fuel-surcharge URL 404; DSV historical page PDF-gated. Found TKA (tka.co.at) as a published Austrian D-tier table — same mechanism (BMWET/BMNT gross diesel, prior-month max, monthly), 141 price points, 0% at €0.85 → ~22.15% at €2.25. Austrian Post's specific table differs in ceiling (carrier said ~32%) but same family. Logged as nearest public analogue.
- T5: ECB monthly EUR/CHF resolved via data-api.ecb.europa.eu (M.CHF.EUR.SP00.A). RAW series = CHF per 1 EUR ≈ 0.91–0.93. RECIPROCAL (EUR per CHF) = 1.0716–1.0996 — this matches carrier's "€1.06 baseline / currently €1.09" EXACTLY. Convention nailed: carrier bills on the reciprocal (1/ECB-ref). Documented both conventions. X-Rates 2026 monthly (CHF/EUR) cross-check: Jan 0.9276, Feb 0.9141, Mar 0.9099, Apr 0.9218 — consistent with ECB reciprocals.
- T6: Writing deliverable. All 4 sections have public values + source URLs + dates + confidence/gap notes. Gaps: post.at's own surcharge page not located (used BMWET driver series + TKA analogue); DSV exact Q1 monthly %s not public (page shows current week + method only); DHL time-definite full zone matrix only partially enumerated and page retains current period only (historical 2025/26 values confirmed via secondary PGL source + DHL.de active matrix).
- T7: Deliverable written to research/2026-05-27-austrian-post-public-indices-and-dhl-express-demand.md. Run complete. Overall confidence medium-high: B+D anchored on authoritative/primary (ECB data-api, DHL.de); A+C anchored on driver series + method (BMWET, DSV) but carrier-specific exact %s not fully public. Returning report to principal.

## Final state: COMPLETE
