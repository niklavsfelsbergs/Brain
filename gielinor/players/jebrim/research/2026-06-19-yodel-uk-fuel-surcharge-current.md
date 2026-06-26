# Yodel UK monthly fuel surcharge — current published rate (June 2026)

**Research date:** 2026-06-19
**For:** Jebrim — UK shipping cost validation (committed cost analysis assumed 18%)
**Question:** Is the published Yodel UK fuel surcharge still 18% (June 2026), and what is the recent trend?
**Confidence:** High on current rate (primary source confirms); medium on the multi-month trend shape (historic page is JS-driven; May figure confirmed via two independent searches, earlier months not directly read).

## Headline

- **Current published rate: 18%, effective June 2026.** Confirms the analysis assumption — **no material difference; 18% holds.**
- Basis: "Based on the May 2026 Road Fuel Price of **£1,841.10 per 1,000 litres**." Band table for contracts with effective date **from 14 April 2014**.
- Source: [yodel.co.uk/fuel-surcharges](https://www.yodel.co.uk/fuel-surcharges), fetched 2026-06-19.

## Trend

| Effective month | Surcharge % (14-Apr-2014 band) | Diesel basis (UK Gov Weekly Road Fuel Price) | Source |
|---|---|---|---|
| May 2026 | 19% | April 2026 RFP £1,898.10 / 1,000 L | WebSearch ×2, 2026-06-19 |
| June 2026 | **18%** | May 2026 RFP £1,841.10 / 1,000 L | yodel.co.uk/fuel-surcharges (primary), 2026-06-19 |

**Direction: down.** Diesel fell ~£57 per 1,000 L month-on-month (£1,898.10 → £1,841.10), and the surcharge stepped down one point (19% → 18%). The downtrend is favorable for the cost gap — every point *above* 18% widens it, and the current move is *below* the prior month, not above.

Earlier-2026 months were not directly read (see Gaps).

## Mechanism / basis (as published)

- Surcharge is **diesel-linked**, tied to the **UK Government Weekly Road Fuel Prices**, applied on a band table.
- Band range on the current page: diesel **£0 to £2,011+ per 1,000 L** → surcharge **1.00% to 20.50%**.
- The headline rate quoted (18% / 19%) is the **"contracts with effective date from 14 April 2014"** band — the same band the committed analysis appears to track. Note there is at least one **other band** ("contracts with effective date from 1st August 2012") which showed **11.0%** for June 2026 on the historic page — a different contract vintage, NOT a contradiction of the 18% figure. **Confirm which contract vintage our committed analysis maps to** (the 18% assumption implies the 14-Apr-2014 band, which the primary page's headline matches).
- Lag structure: the *month's* surcharge is set off the *prior month's* road fuel price (June 2026 uses May 2026 RFP). One-month lag.

## Gaps & open questions

- **Historic page is JS-driven.** [yodel.co.uk/fuel-surcharges/historic-fuel-surcharges](https://www.yodel.co.uk/fuel-surcharges/historic-fuel-surcharges) returned only single band values on fetch (June 2026 = 11.0% on the 1-Aug-2012 band), not a chronological listing. A full month-by-month 2026 trend was not directly readable — only May (19%) and June (18%) are pinned.
- **Pre-May 2026 months not sourced** — cannot state whether the 19%→18% step is a fresh reversal or the continuation of a longer decline without reading the rendered historic table directly.
- **Band/contract-vintage mapping** — verify the committed analysis uses the 14-Apr-2014 band (18%) and not the 1-Aug-2012 band (11.0%). One-point error vs the whole 7-point gap between vintages have very different blast radii.

## Sources

- [Yodel — Fuel Surcharges (primary)](https://www.yodel.co.uk/fuel-surcharges) — current rate 18%, June 2026, May RFP £1,841.10/1,000 L. Fetched 2026-06-19.
- [Yodel — Historic Fuel Surcharges](https://www.yodel.co.uk/fuel-surcharges/historic-fuel-surcharges) — JS-driven; partial read. Fetched 2026-06-19.
- WebSearch (2026-06-19, two independent queries) — May 2026 = 19%, basis April 2026 RFP £1,898.10/1,000 L, 14-Apr-2014 band.
