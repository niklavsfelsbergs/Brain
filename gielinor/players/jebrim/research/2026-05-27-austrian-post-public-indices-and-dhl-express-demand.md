# Austrian Post public indices + DHL Express demand surcharge — public-data lookup

**Question.** For the EU Tender 2026 (Picanova carrier tender), source four independent public-data inputs the carriers cited: (A) Austrian Post diesel fuel surcharge series + monthly %, (B) EUR/CHF monthly averages and the €1.06-baseline uplift, (C) DSV diesel-floating index, (D) DHL Express Demand Surcharge amounts for the 2025/26 window.
**Date of research.** 2026-05-27.
**Replay window.** Q1 2026 (Jan / Feb / Mar).
**Author.** Penguin (research operative), player Jebrim.
**Overall confidence.** Medium-high. Sections B and D are anchored on authoritative/primary sources (ECB data-api; DHL.de). Sections A and C are anchored on the *driver* series and *method* (BMWET diesel series; DSV method + current value) but the carrier-specific exact percentage tables for each Q1 month are not fully public — see gap notes.

---

## A) Austrian Post — AT diesel fuel surcharge (Treibstoffzuschlag / Dieselzuschlag)

**Confidence: medium.** The *driver* series (BMWET weekly diesel price) is authoritative and complete. Austrian Post's *own* D-tier mapping page was not located on post.at; a published Austrian analogue tier table (TKA) running on the same mechanism is reported as the nearest public proxy.

### A.1 — The driver: BMWET weekly Austrian diesel price series

The carrier-cited source is live. The Austrian Ministry (BMWET) publishes a weekly nationwide diesel price ("Treibstoffpreise 2026"), weighted average including all taxes/VAT, updated **Thursdays**.
Source: <https://www.bmwet.gv.at/Themen/Energie/kosten.html>

Weekly AT diesel price (gross, €/L) — full series pulled 2026-05-27 (source: BMWET kosten.html):

| Week (Thu) | €/L | | Week (Thu) | €/L |
|---|---|---|---|---|
| 05.01.2026 | 1.495 | | 02.03.2026 | 1.564 |
| 12.01.2026 | 1.477 | | 09.03.2026 | 1.898 |
| 19.01.2026 | 1.487 | | 16.03.2026 | 1.954 |
| 26.01.2026 | 1.509 | | 23.03.2026 | 2.109 |
| 02.02.2026 | 1.520 | | 30.03.2026 | 2.204 |
| 09.02.2026 | 1.529 | | 06.04.2026 | 2.228 |
| 16.02.2026 | 1.518 | | 13.04.2026 | 2.075 |
| 23.02.2026 | 1.546 | | 20.04.2026 | 1.948 |
| | | | 27.04.2026 | 1.910 |
| | | | 04.05.2026 | 1.999 |
| | | | 11.05.2026 | 1.913 |
| | | | 18.05.2026 | 1.914 |

Approx. **monthly max** gross diesel (the figure that typically drives the *next* month's surcharge — see A.2):
- Jan 2026: ~**1.509** €/L (26.01)
- Feb 2026: ~**1.546** €/L (23.02)
- Mar 2026: ~**2.204** €/L (30.03) — sharp spike from ~1.56 to ~2.20 across March
- Apr 2026: ~**2.228** €/L (06.04), easing to ~1.91 by month-end

The March spike to ~2.10–2.23 €/L is consistent with the carrier's narrative of a *currently elevated* surcharge ("currently 12% due to the war in Iran"). *(inferred from the BMWET series + the carrier statement — the price jump is real and dated, the attribution to the Iran conflict is the carrier's, not independently verified here.)*

### A.2 — The surcharge mechanism (Austrian TKZ family)

Austrian fuel surcharges of this kind (TKZ — Treibstoffkostenzuschlag) are computed from an **index based on the gross diesel prices published by the Ministry** (BMWET, formerly BMNT), **adjusted monthly**, with the **maximum gross diesel price of the previous month** as the basis for the following month.
Source (mechanism, TKA): <https://www.tka.co.at/de/treibstoffzuschlag> — *"Der Treibstoffzuschlag (kurz TKZ) wird anhand eines Indexes, basierend auf den Brutto Dieselpreisen vom BMNT … monatlich angepasst."*
Corroborated for the courier sector by GLS Austria, which "bases its diesel surcharge calculation on an index derived from the fuel price monitor published by Austria's Federal Ministry … setting the index and diesel surcharge for each month based on the last published index value from the previous month."
Source: <https://gls-group.com/AT/de/pakete-versenden/versandinfos/dieselzuschlag>

### A.3 — Published D-tier table (TKA analogue — nearest public proxy)

The TKA page publishes a full tier table mapping **gross diesel €/L → surcharge %** (141 price points, monthly basis, same BMWET driver):
Source: <https://www.tka.co.at/de/treibstoffzuschlag>
- €0.85/L → **0.0%**
- €0.88–€1.22/L → **1.0%–14.8%** (incremental)
- €1.23–€1.50/L → **15.0%–18.4%**
- €1.51–€2.25/L → **18.45%–22.15%** (0.05% increments at the top)

Reading the Q1 monthly-max diesel figures against this *analogue* table *(inferred — TKA's table, not Austrian Post's own, used as a proxy)*:
- Jan-max ~1.509 → ~**18.4%** band; Feb-max ~1.546 → ~**18.5%**; Mar-max ~2.204 → near the **~22%** ceiling.

> **Caveat on the proxy.** TKA's table tops out at ~22.15% at €2.25/L. The carrier described Austrian Post's table as running **~0%–32%** with "typically 4%, currently 12%." Those numbers do **not** match the TKA tier table's slope or ceiling — Austrian Post evidently runs a *different* D-tier mapping (lower baseline, higher ceiling). So the TKA table establishes the *mechanism and the driver series* but is **not** a substitute for Austrian Post's own tier card. The carrier's "typically 4% / currently 12%" cannot be reconstructed from public data without Austrian Post's specific D-table.

### A.4 — Gaps (Section A)
- **Austrian Post's own published Treibstoffzuschlag page was not located.** `post.at/g/c/treibstoffzuschlag` returns 404; no post.at surcharge tier card surfaced via search. The carrier-specific D-tier mapping (0%–32%) is therefore **not confirmed from a public source** — request the tier card directly from Austrian Post.
- The "12% currently / 4% typical" values are the carrier's; they're plausible against an elevated March diesel print but cannot be tied to a public Austrian Post table.
- BMWET series is weekly; the monthly-max selection rule is inferred from the TKA/GLS mechanism, not from an Austrian Post document.

---

## B) EUR/CHF monthly averages + €1.06-baseline uplift

**Confidence: high.** Anchored on the ECB monthly reference series via the ECB data-api. The convention puzzle in the carrier's quote ("€1.06 baseline, currently €1.09") is resolved below.

### B.1 — The convention (this is the load-bearing finding)

The ECB publishes the franc series as **CHF per 1 EUR** (series `M.CHF.EUR.SP00.A`), which in this period sits at **~0.91–0.93** (the franc is *stronger* than the euro).
Source (daily, convention confirmed "CHF per 1 EUR" ≈ 0.91–0.92): <https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/eurofxref-graph-chf.en.html>

The carrier's "EUR/CHF = 1.06 / 1.09" figures are the **reciprocal** convention — **EUR per 1 CHF** (= 1 ÷ ECB reference rate) — which sits at **~1.07–1.10**. The carrier bills the Switzerland lane on this reciprocal, against a €1.06 reference baseline.

### B.2 — Monthly values (ECB monthly reference, both conventions)

Source: ECB Data Portal, series `EXR.M.CHF.EUR.SP00.A` via the ECB statistical API
<https://data-api.ecb.europa.eu/service/data/EXR/M.CHF.EUR.SP00.A> (description page: <https://data.ecb.europa.eu/data/datasets/EXR/EXR.M.CHF.EUR.SP00.A>)

| Month | ECB ref (CHF per 1 EUR) | Reciprocal (EUR per 1 CHF) = carrier "EUR/CHF" | Uplift vs 1.06 baseline (on reciprocal) |
|---|---|---|---|
| Oct 2025 | ~0.9290 | **1.0765** | +1.6% |
| Nov 2025 | ~0.9290 | **1.0764** | +1.5% |
| Dec 2025 | ~0.9332 | **1.0716** | +1.1% |
| Jan 2026 | ~0.9273 | **1.0784** | +1.7% |
| Feb 2026 | ~0.9141 | **1.0940** | +3.2% |
| Mar 2026 | ~0.9094 | **1.0996** | +3.7% |
| Apr 2026 | ~0.9213 | **1.0854** | +2.4% |

Notes:
- The reciprocal column (1.0716–1.0996) **matches the carrier's framing exactly** — baseline €1.06, "currently €1.09" ≈ the Feb/Mar 2026 prints. This confirms the carrier bills on `1 ÷ ECB-reference`.
- The ECB "CHF per 1 EUR" column is given to 4 dp where the data-api returned it; figures shown ~4dp, rounded for display. The reciprocals are as returned by the data-api fetch (4 dp).
- **Billing rule (carrier-stated):** Switzerland lane is billed at the **previous month's average** EUR/CHF. So a January invoice uses the **December** average (1.0716, +1.1%); a March invoice uses the **February** average (1.0940, +3.2%). Apply the table with a one-month lag.
- Uplift % computed as (reciprocal − 1.06) / 1.06.

### B.3 — Cross-check (secondary, X-Rates)
X-Rates monthly averages for 2026 (CHF per 1 EUR): Jan **0.9276**, Feb **0.9141**, Mar **0.9099**, Apr **0.9218**.
Source: <https://www.x-rates.com/average/?from=EUR&to=CHF&amount=1&year=2026>
These are consistent with the ECB CHF/EUR column above (and the daily extremes: high 0.9390 on 09.12.2025, low 0.9004 on 09.03.2026, per <https://www.mtfxgroup.com/tools/historical-currency-exchange-rates/eur-to-chf-rate/>).

### B.4 — Gaps (Section B)
- ECB CHF/EUR monthly values to full precision were taken from the data-api reciprocals (the API returned reciprocals labelled EUR/CHF); the CHF/EUR column is derived (1 ÷ reciprocal) and shown to ~4 dp. For an audit-grade figure, pull the raw `OBS_VALUE` from the ECB Data Portal CSV export directly.
- 2025 monthly averages (Oct/Nov/Dec) for the X-Rates cross-check were not separately retrievable (X-Rates fetch served only 2026); the Oct–Dec 2025 figures above rely on the ECB data-api series alone.

---

## C) DSV diesel-floating index (per-pallet trucking surcharge driver)

**Confidence: medium.** Method, basis, and the *current* value are authoritative (DSV's own page). The exact Q1-2026 monthly percentages are not published historically — see gap.

### C.1 — Source and current value
Carrier-cited source: <https://www.dsv.com/de-de/unsere-loesungen/transportarten/landtransport/zuschlaege/diesel-floating>
Current values (week 22, 25–31.05.2026), per the DSV page:
- **Stückgut (piece goods): 13.5%**
- **Direkt (LTL/FTL): 23.0%**
- Reference diesel price: **€197.2 / 100L** (Germany)

(Earlier in the quarter-adjacent window, week 18 = 27.04–03.05.2026 read **13.20%** for Dieselflex at €213.3/100L. Source: <https://www.dsv.com/de-de/unsere-loesungen/transportarten/landtransport/zuschlaege> / Dieselflex page.)

### C.2 — How it is computed
Source: <https://www.dsv.com/de-de/unsere-loesungen/transportarten/landtransport/zuschlaege/diesel-floating> (basis page: <https://docs.dsv.com/countries/germany/road/dieselpreise-basis-wochentlich-DSV-floater/>)
- **Basis index:** EU Commission **Weekly Oil Bulletin** (Germany diesel), referenced against the **Q4 2005 average** diesel price.
- **Update frequency:** **weekly, every Thursday** — but DSV **transitioned from monthly to weekly adjustments on 2026-03-16**. So **Jan/Feb/early-Mar 2026 surcharges were set monthly**; from mid-March they update weekly.
- **Sensitivity:** Stückgut **±0.5 pp per ±4%** diesel-price move; LTL/FTL **±1.0 pp per ±4%** move. (An older statement of the model cites +1.2 pp per €0.05 move on a €1.60/L gross-diesel reference — <https://www.dsv.com/de-de/unsere-loesungen/transportarten/landtransport/zuschlaege/dieselflex>; the "±0.5 pp / ±4%" figure is the current per-DSV-page statement for Stückgut.)

### C.3 — Gaps (Section C)
- **Exact Q1-2026 monthly percentages (Jan/Feb/Mar) are not published.** The DSV page retains the **current week** plus the method/derivation table only; historical monthly values are behind a PDF (<https://docs.dsv.com/countries/germany/road/dieselpreise-basis-wochentlich-DSV-floater/> — PDF-gated, not extractable via web fetch). Request the historical Dieselflex schedule from DSV, or reconstruct from the EU Weekly Oil Bulletin Germany series using the ±0.5 pp/±4% rule off the Q4-2005 reference.
- Note the **monthly→weekly switch on 2026-03-16**: a Q1 replay must treat Jan/Feb/early-Mar as flat-monthly and only late-March as weekly-varying.
- The brief frames this as Austrian Post's *per-pallet trucking* surcharge driver; the DSV page is the German Landtransport Dieselflex index. Confirm with Austrian Post that they peg the AT per-pallet surcharge to this exact German DSV index (vs an AT-specific DSV table).

---

## D) DHL Express — Demand Surcharge (Bedarfszuschlag / Demand Surcharge)

**Confidence: high (on the amounts and dates), medium (on full zone-matrix enumeration).** Anchored on DHL.de's own surcharges page.

### D.1 — Effective period
**Active 01.10.2025 – 16.02.2026** — confirmed. This **overlaps the Q1 2026 replay for 01.01.2026 – 16.02.2026** (i.e. all of January and the first 16 days of February are inside the surcharge window; 17.02.2026 onward is clear).
Source (primary): <https://www.dhl.de/en/geschaeftskunden/express/produkte-und-services/zuschlaege.html>
Source (secondary, period corroboration): <https://www.dhl.com/content/dam/dhl/local/us/dhl-ecommerce/documents/pdf/peak-surcharge-2025-2026.pdf>

### D.2 — Surcharge amounts (€ per kg, billing weight)
From the DHL.de Express surcharges page (<https://www.dhl.de/en/geschaeftskunden/express/produkte-und-services/zuschlaege.html>):

- **Domestic Time Definite services:** flat **€0.10 / kg** demand surcharge.
- **International Day Definite services** (e.g. Economy Select): flat **€0.15 / kg** demand surcharge.
- **International Time Definite services** (e.g. Worldwide): a **zone-pair matrix**, €/kg on billing weight, **based on origin and destination**, ranging **€0.10 – €1.90 / kg**. Example points the page enumerates:
  - China / Hong Kong → Americas: **€1.70/kg** *(note: secondary search snippet cited €1.90/kg as the matrix top; the primary fetch enumerated €1.70/kg for CN/HK→Americas — treat €1.70–1.90 as the top band, exact cell to be confirmed)*
  - Europe → Americas: **€0.50/kg**
  - Rest of World routes: **€0.80/kg** (flat)

All amounts: "applicable in € per kg (billing weight), based on the shipment's origin and destination." The page also states: *"Charge amounts and application dates may vary throughout the demand period determined by DHL."*

### D.3 — Relevance to the replay
For Picanova's outbound Express lanes during 01.01–16.02.2026:
- Domestic AT/DE Time Definite parcels: **+€0.10/kg**.
- Economy Select (Day Definite) cross-border: **+€0.15/kg**.
- Worldwide (Time Definite) cross-border: the **zone-pair €/kg** from the matrix — for **Europe→Americas €0.50/kg**; intra-Europe and other lanes per the matrix cell (lower end ~€0.10/kg; confirm the exact origin/destination cells against Picanova's actual lanes).

### D.4 — Gaps (Section D)
- **The DHL.de page retains the current/active demand-surcharge period only** — it explicitly notes amounts/dates "may vary throughout the demand period" and shows the active matrix, not a dated historical archive. Because the 01.10.2025–16.02.2026 window was still the *most recent* period at research time, the matrix captured is the one that applied during the replay, but DHL does **not** publish a locked historical snapshot — if DHL refreshes the page for a 2026/27 period the values seen here will be overwritten and not retrievable from the public page.
- The **full Worldwide zone-pair matrix** was only partially enumerated by the fetch (example cells, plus a €0.10–€1.90/kg range). For an exact lane-by-lane replay, request the complete demand-surcharge matrix PDF from DHL, or capture the live matrix page before the next period rollover. The €1.70 vs €1.90/kg top-cell discrepancy (primary fetch vs secondary snippet) is unresolved.
- A secondary blog source (shippgl.com) that indexed this period 404'd on fetch; the DHL.de primary source is the basis for all figures above.

---

## Source map (one line each)

- **BMWET diesel cost page** — <https://www.bmwet.gv.at/Themen/Energie/kosten.html> — authoritative AT weekly diesel price series; the driver for Section A. **Load-bearing, fetched.**
- **TKA Treibstoffzuschlag** — <https://www.tka.co.at/de/treibstoffzuschlag> — published Austrian D-tier table + mechanism; proxy for A. **Load-bearing, fetched.**
- **GLS Austria Dieselzuschlag** — <https://gls-group.com/AT/de/pakete-versenden/versandinfos/dieselzuschlag> — corroborates the prior-month-index monthly mechanism. **Supporting, search.**
- **ECB data-api EXR.M.CHF.EUR** — <https://data-api.ecb.europa.eu/service/data/EXR/M.CHF.EUR.SP00.A> — authoritative monthly EUR/CHF; Section B. **Load-bearing, fetched.**
- **ECB CHF reference graph** — <https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/eurofxref-graph-chf.en.html> — convention confirmation (CHF per 1 EUR). **Load-bearing, fetched.**
- **X-Rates EUR→CHF 2026** — <https://www.x-rates.com/average/?from=EUR&to=CHF&amount=1&year=2026> — secondary monthly-average cross-check for B. **Supporting, fetched.**
- **MTFX EUR/CHF history** — <https://www.mtfxgroup.com/tools/historical-currency-exchange-rates/eur-to-chf-rate/> — daily extremes cross-check. **Supporting, search.**
- **DSV diesel-floating** — <https://www.dsv.com/de-de/unsere-loesungen/transportarten/landtransport/zuschlaege/diesel-floating> — current value + method; Section C. **Load-bearing, fetched.**
- **DSV Dieselflex / basis docs** — <https://www.dsv.com/de-de/unsere-loesungen/transportarten/landtransport/zuschlaege/dieselflex>, <https://docs.dsv.com/countries/germany/road/dieselpreise-basis-wochentlich-DSV-floater/> — model derivation; C. **Supporting (PDF-gated).**
- **DHL.de Express surcharges** — <https://www.dhl.de/en/geschaeftskunden/express/produkte-und-services/zuschlaege.html> — demand-surcharge amounts + dates; Section D. **Load-bearing, fetched.**
- **DHL peak-surcharge 2025-2026 PDF** — <https://www.dhl.com/content/dam/dhl/local/us/dhl-ecommerce/documents/pdf/peak-surcharge-2025-2026.pdf> — period corroboration. **Supporting, search.**

## Consolidated gaps & open questions
1. **Austrian Post's own D-tier card (0%–32%) is not public** — the carrier's "4% typical / 12% current" can't be reconstructed from public data. Request the tier card directly. (A)
2. **DSV Q1-2026 monthly percentages are PDF-gated** — only the current week + method are on the public page. Reconstruct from EU Weekly Oil Bulletin or request the historical schedule. Mind the monthly→weekly switch on 2026-03-16. (C)
3. **DHL publishes no locked historical demand-surcharge snapshot** — the live matrix captured here applied during the replay window, but will be overwritten at the next period; full Worldwide zone matrix only partially enumerated, and a €1.70-vs-€1.90/kg top-cell discrepancy is open. (D)
4. **Convention confirmed for B** — carrier "€1.06/€1.09" = EUR-per-CHF reciprocal of the ECB CHF/EUR reference; billed on the previous month's average. No open question, but flag it so the tender model uses the reciprocal series with a one-month lag.
