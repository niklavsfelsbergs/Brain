# UPS Germany — 2026 Published Tariff & Surcharge Schedule

**Question.** For UPS **Germany (DE)**, shipping outbound to EU/Europe, what is the authoritative *published* (book-rate) surcharge schedule a negotiated contract sits on top of — with priority on seasonal Peak/Demand surcharges, plus the full standard accessorial set, the fuel-surcharge mechanism, and the dim-weight rule?

**Date of research.** 2026-06-08.

**Confidence.** **Medium-high** on the *mechanisms*, thresholds, dim-weight, declared-value, and the seasonal peak *structure*; **medium** on the exact current EUR peak per-package figures (best official anchor is the year-round Over-Max €440; the per-week seasonal figures are well-sourced but via a dated secondary); **low** on the *live* fuel-surcharge percentage (UPS publishes it only in a weekly JS table that could not be machine-fetched — flagged as a must-check-on-site item).

> **Provenance health-check (read this first).** UPS publishes the load-bearing numbers as large PDFs and a JS-rendered fuel table on `ups.com`/`assets.ups.com`. **Every direct fetch of those asset PDFs and the live fuel table timed out or returned compressed-binary** in this environment. Two EU Demand-Surcharge PDFs *did* download as binary and were read directly (cited as **[OFFICIAL-PDF]**). Where only a secondary carried the figure, it is tagged **[SECONDARY]** and should be re-confirmed against the live UPS page before it drives a contract number. Do **not** treat any US-dollar figure in this file as the German one — they are kept separate throughout.

---

## Headline

The published picture: UPS DE's standing accessorials are a flat per-parcel book (Additional Handling ~€23.65 nat / €26.70 intl, Large Package €101.80, Over-Maximum €499.10, Address Correction €6.50, Remote/DAS €25.00) layered with a **weekly fuel surcharge** (Standard/road indexed to EC diesel prices; Express/air indexed to US Gulf Coast jet fuel) and a **2026 GRI of 5.9%**. For a **Q4-heavy photo-gift shipper scored on full-year cost, the material layers are (1) the seasonal Peak/Demand surcharge** — a flat **€0.20/package Base Rate Surcharge on *every* package** plus per-package demand fees, running **2025-09-29 → 2026-01-17** (i.e. the entire Nov–Dec spike), and **(2) the fuel surcharge**, which is variable and not contract-fixable in reality (a fixed "35%" in an offer is a snapshot, not a guarantee). The Large-Package and Over-Maximum surcharges are large but only bite oversized parcels; for standard photo-gift cartons the **Base Rate Surcharge × Q4 volume** is the line that compounds. A contract waiving a *subset* of accessorials still leaves the seasonal Base Rate Surcharge and fuel at full published rate unless explicitly negotiated.

---

## Sources

**Official UPS (primary):**

- **[OFFICIAL-PDF]** UPS® Demand Surcharges, Europe (en_GB), dated **2025-01-31** — `https://www.ups.com/assets/resources/webcontent/en_GB/demand-surcharges-europe.pdf` — the year-round **Over-Maximum** demand surcharge table by country (Germany €440.00); confirms 19-country EU origin scope incl. Germany; business-only, ex-VAT (DE 19%). *Read directly via binary download.* **Load-bearing.**
- **[OFFICIAL-PAGE]** Fuel Surcharge | UPS Germany — `https://www.ups.com/de/en/support/shipping-support/shipping-costs-rates/fuel-surcharges` (and `/de/de/` German variant) — fuel **mechanism**: Standard updates Monday weekly on EC diesel index (2 weeks prior); air on US Gulf Coast jet fuel (EIA, 2 weeks prior); 14.50% threshold note. *Live % table is JS — not fetchable here.* **Load-bearing (mechanism).**
- **[OFFICIAL-PAGE]** Shipping Dimensions and Weight | UPS Germany — `https://developer.ups.com/de/en/support/shipping-support/shipping-dimensions-weight` — **dim-weight divisor 5000** (import/export, cm³÷5000), billable = greater(actual, dim), round up to next 0.5 kg. **Load-bearing.**
- **[OFFICIAL-PDF]** UPS 2026 Tariftabelle für Geschäftskunden in Deutschland (rate guide) — `https://assets.ups.com/adobe/assets/urn:aaid:aem:bf8cdba5-9d0b-45d3-ae10-4275fa34e2df/original/as/rate-guide-de-en.pdf` — the published 2026 DE rate book. **Could not be fetched (timeout).** Listed as the canonical anchor to pull on-site.
- **[OFFICIAL-PDF]** Additional Services & Charges, Germany (English) — `https://www.ups.com/assets/resources/webcontent/de_DE/additional-service-charge-de.pdf` — the per-accessorial EUR book (declared value, signature, Saturday, paper-invoice, SCC). **Could not be fetched (timeout).** Canonical anchor for items 6 & 8.
- **[OFFICIAL-PAGE]** Brokerage / Customs Brokerage Fee — `https://www.ups.com/de/en/supplychain/tools/surcharges/Brokerage-General-Rates.page` and customs-brokerage-billing-terms.pdf — disbursement & entry-prep fee structure.

**Third-party (secondary — re-confirm before use):**

- **[SECONDARY]** shipcloud.io — UPS DE max dimensions, surcharges & additional fees — `https://support.shipcloud.io/en/articles/5505390-...` — dated **2026-01-09, "effective Jan 1 2026."** Source for base accessorial EUR figures (AddlHandling, Large Pkg, Over-Max, Address Correction, Remote Area).
- **[SECONDARY]** shipcloud helpcenter — UPS Demand Surcharges Peak Season 2025 — `https://helpcenter.shipcloud.com/en/articles/4533049-...` — dated **2025-11-12.** Source for the **seasonal peak EUR per-package set** (Base Rate Surcharge €0.20, AddlHandling €7.35, Large Pkg €77.60, Over-Max €475.00).
- **[SECONDARY]** wein.plus — Overview of special UPS tariffs 2025/2026 — `https://www.wein.plus/en/uebersicht-sondertarife-ups-2025-2026` — DE book values: AddlHandling €22.20 nat / €25.05 intl, Residential €3.35, Oversize €468.60; **declared value: up to €510 incl., then 1.0% min €7.80**; fuel mechanism.
- **[SECONDARY]** loop.com — UPS rate increases 2025-2026 timeline — `https://www.loop.com/industry-insights/ups-rate-increases-2025-2026-...` — **2026 GRI = 5.9%** (announced 2025-12-22). *Fuel figures on this page are US-only.*
- **[SECONDARY, US-ONLY — do not use for DE]** refundretriever, lojistic, transimpact — US-dollar peak/demand tables. Cited only to mark what is *not* the German figure.

---

## 1. Seasonal Peak / Demand Surcharges  *(priority)*

**The window.** Peak/Demand season **2025-09-28/29 → 2026-01-17** (inclusive). Applies to parcels **originating from 19 EU countries incl. Germany**, to all destinations. [OFFICIAL-PDF demand-surcharges-europe; SECONDARY shipcloud]

**Two distinct surcharge layers — important:**

| Component | EUR / package (DE) | Trigger / scope | 2026 vs 2025 | Source |
|---|---|---|---|---|
| **Base Rate Surcharge** | **€0.20 per package** | **Every package**, all services, across the whole window | 2025-26 season figure | [SECONDARY] shipcloud helpcenter 2025-11-12 |
| **Additional Handling — Demand** (peak add-on) | **€7.35** (add-on, on top of standard AddlHandling) | Same triggers as standard AddlHandling (see §3), during the window | 2025-26 season | [SECONDARY] shipcloud helpcenter |
| **Large Package — Demand** (peak add-on) | **€77.60** (add-on, on top of standard Large Pkg) | L+girth >300 cm ≤400 cm, during the window | 2025-26 season | [SECONDARY] shipcloud helpcenter; cross-checks shipcloud.io "Large Pkg Peak €77.60" |
| **Over-Maximum — Demand (seasonal add-on)** | **€475.00** | Over-Max specs (see §4), during the window | 2025-26 season | [SECONDARY] shipcloud helpcenter; cross-checks shipcloud.io "Over-Max Peak €475.00" |
| **Over-Maximum — Demand (YEAR-ROUND, permanent)** | **€440.00 flat / parcel** | Over-Max specs — **in force since 2023-04-17, until further notice**, NOT time-boxed | Standing charge (2025 doc; current) | **[OFFICIAL-PDF]** demand-surcharges-europe.pdf |

**Note the two Over-Max figures.** The **€440** is the *permanent* year-round demand surcharge (official PDF). The **€475** is the *seasonal* peak Over-Max figure (secondary). They are the same conceptual charge at two vintages/scopes — the seasonal one supersedes during the window. Treat €440 as the firmly-sourced standing number.

**Exact week bands.** UPS's US scheme tiers peak by week (e.g. Sept 28–Nov 22 / Nov 23–Dec 27 / Dec 28–Jan 17). The **European** scheme, per the secondary, applies the figures **uniformly across the whole window** rather than escalating by week — but UPS reserves the right to adjust without notice. *The per-week European tiering, if any, is a gap — confirm against the live demand-surcharges-europe PDF.*

**Q4 relevance.** The **€0.20 Base Rate Surcharge on every package** is the line that scales with a photo-gift Q4 spike — it is not dimension-gated, so it hits the entire November–December carton volume. On, say, 200k Q4 parcels that is ~€40k of pure seasonal surcharge before fuel, independent of the negotiated rate card.

---

## 2. Large Package Surcharge

- **Rate:** **€101.80 per package** (standard, off-peak). [SECONDARY shipcloud.io, eff. 2026-01-01]
- **Trigger:** length **+ girth combined > 300 cm** but **≤ 400 cm** (max UPS size). `girth = (2×width)+(2×height)`. [OFFICIAL-PDF demand-surcharges-europe confirms the 300/400 definition.]
- **Minimum billable weight:** Large Packages are billed at a **minimum 40 kg**. [SECONDARY shipcloud.io; OFFICIAL-PDF]
- **Peak add-on:** +€77.60 during the season (see §1).
- **2026 vs 2025:** €101.80 is the 2026 standard figure per the 2026-effective secondary; wein.plus shows a lower *net* (member-discounted) figure — the €101.80 is the book/list value.

---

## 3. Additional Handling

- **Rate (standard, off-peak):** **€23.65 national / €26.70 international** per package. [SECONDARY shipcloud.io, eff. 2026-01-01]. *(wein.plus lists €22.20 nat / €25.05 intl as an earlier/net book value — the €23.65/€26.70 is the 2026 figure.)*
- **Triggers (any one):**
  - actual weight **> 25 kg** (lowered from 32 kg effective 2023-10-01 per wein.plus; **note shipcloud states ">32 kg"** — see caveat) ;
  - **longest side > 100 cm**, OR second-longest side **> 76 cm** ;
  - packaging is **metal or wood**, or a cylindrical container not fully enclosed in corrugated cardboard, or non-corrugated outer packaging.
- **Peak add-on:** +€7.35 during the season (see §1).
- **Caveat — the weight trigger:** wein.plus says the AddlHandling weight trigger dropped to **25 kg** in Oct 2023; shipcloud says **32 kg**. These may reflect different package classes (the Over-Max/AddlHandling boundary) or doc vintages. **The ≥25 kg trigger is the safer planning assumption; confirm against the live DE rate guide.**

---

## 4. Over Maximum Limits

- **Rate (standard, off-peak):** **€499.10 per package**. [SECONDARY shipcloud.io, eff. 2026-01-01]. *(Year-round demand-surcharge variant €440 official; seasonal €475 — see §1.)*
- **Trigger ("over maximum"):** actual weight **> 70 kg**, OR length **> 274 cm**, OR length + girth combined **> 400 cm**. Such packages are **not accepted for transport**; if found in the system they incur this charge (and, if >400 cm L+girth, *also* the Large Package Surcharge). **No money-back guarantee** on these. [OFFICIAL-PDF demand-surcharges-europe — verbatim spec.]

---

## 5. Delivery Area Surcharge (Extended / Remote Area)

- **Remote Area:** **€25.00 per package**. [SECONDARY shipcloud.io, eff. 2026-01-01]
- **Residential (list/book value):** **€3.35 per package** (member-discounted nets to ~€0.94). [SECONDARY wein.plus]
- **Extended Area / DAS tiering:** UPS DE publishes Extended/Remote area lists by postcode in the rate guide; **the full multi-tier DAS table is a gap** (rate guide PDF un-fetchable). Confirm on-site for the exact Extended vs Remote split. *These are noted as waived in the contract under assessment — this is the book value to price the waiver against.*

---

## 6. Declared Value / Insurance

- **Included cover:** up to **€510 per consignment** at no charge. [SECONDARY wein.plus / UPS DE]
- **Above €510:** **1.0% of the declared value, minimum €7.80** per shipment. [SECONDARY wein.plus / UPS DE]
- **2026 vs 2025:** structure is stable year-on-year; confirm the €7.80 minimum and the 1.0% rate against the live `additional-service-charge-de.pdf` for the 2026 figure.

---

## 7. Duties, Taxes, Brokerage / Disbursement

For cross-border (DE → non-EU; intra-EU shipments are duty/VAT-free at clearance), UPS bills:

- **Disbursement / advancement fee:** UPS fronts duties+import-VAT to customs and bills it back at **3.5% of the advanced amount, with a minimum** (UPS quotes ~**$14** / local-currency equivalent in the global glossary; the DE EUR minimum is in `additional-service-charge-de.pdf`). [OFFICIAL-PAGE brokerage glossary]
- **Entry preparation fee:** for preparing/submitting clearance documents — flat per-entry, EUR value in the DE additional-services PDF (un-fetchable; gap).
- **Per-tariff-line fee:** when a customs entry has **> 5 tariff lines**, a surcharge per additional line. [OFFICIAL-PAGE]
- **Transit/bond admin fee:** when UPS raises a transit procedure (in-bond) it charges a clearance-admin fee. [OFFICIAL-PAGE]
- **Duties & taxes themselves** are pass-through (the actual customs charge), separate from the brokerage/disbursement fees above.
- **EUR figures for the DE entry-prep, per-line, and disbursement minimum are a gap** — the structure is official; the exact EUR amounts need the `additional-service-charge-de.pdf` on-site. **Mostly N/A for intra-EU DE→EU lanes** (no customs entry), material only for DE→non-EU (UK, CH, NO).

---

## 8. Other Standard Accessorials

Brief — book values; exact 2026 EUR for several need `additional-service-charge-de.pdf` on-site (gap flagged):

| Accessorial | Rate (EUR) | Trigger | Source / status |
|---|---|---|---|
| **Address Correction** | **€6.50** / package | UPS corrects an incomplete/wrong address | [SECONDARY shipcloud.io 2026] |
| **Residential** (list) | **€3.35** / package | Delivery to a residential address | [SECONDARY wein.plus] |
| **Saturday delivery / pickup** | *gap* | Sat handling requested | Official additional-services PDF (un-fetchable) |
| **Signature Required / Adult Signature** | *gap* | Signature/adult-signature confirmation | Official additional-services PDF (un-fetchable) |
| **Carbon-neutral** | *gap* (historically small per-pkg) | Opt-in carbon offset | Official additional-services PDF; verify still offered |
| **Paper / non-EDI invoice fee** | *gap* | Non-electronic invoice / paper docs | Official additional-services PDF |
| **Shipping Charge Correction (SCC) audit fee** | *gap* (typically a % of the corrected amount, min fee) | UPS re-weighs/re-measures and corrects a mis-declared shipment | Official additional-services PDF / rate guide |

The five "gap" rows are real published accessorials whose **EUR values live only in the un-fetchable DE additional-services PDF** — listed here so the assessment knows they exist and where to pull them.

---

## 9. Fuel Surcharge Mechanism

- **How it's set:** a **weekly** percentage, **updated every Monday**. [OFFICIAL-PAGE UPS DE fuel]
  - **Standard / road services (UPS Standard, ground):** indexed to **diesel fuel prices set by the European Commission** (ECDG / EC oil bulletin), using the price from **two weeks prior** to the adjustment week. [OFFICIAL-PAGE]
  - **Express / air services (Express, Express Saver, Worldwide):** indexed to the **US Gulf Coast (USGC) kerosene-type jet fuel** price reported by the **US EIA**, **two weeks prior**. [OFFICIAL-PAGE / UPS fuel mechanism]
- **Threshold note:** UPS states the table updates whenever the surcharge rises above **14.50%** or thresholds change. [OFFICIAL-PAGE]
- **Current / 2026 published %:** **NOT captured** — the live percentages are published only in a JS-rendered weekly table on the UPS DE fuel page that **could not be machine-fetched**, and the available secondaries gave **US-only** fuel figures (which must not be substituted for DE). **This is the single most important on-site check.**
- **Implication for the contract's fixed "35%":** because the real surcharge is a moving weekly index (road ≠ air, and both float with fuel markets), **a contract that quotes a fixed flat fuel % is a snapshot, not a guarantee** — it will diverge from the published index over a full year. Whether 35% is favorable depends on the live published Standard vs Express percentages at assessment time. **Pull the live DE fuel table before scoring.**

---

## 10. Dimensional Weight Divisor

- **Divisor:** **5000** — dimensional weight (kg) = (L × W × H in cm) **÷ 5000**, for import/export shipments. [OFFICIAL-PAGE UPS DE dimensions]
- **Billable weight rule:** **the greater of actual weight vs dimensional weight**; round the result **up to the next 0.5 kg**. [OFFICIAL-PAGE]
- **2026 vs 2025:** stable; 5000 is the standing UPS EU/DE divisor. **High confidence — official source.**

---

## Gaps & caveats

1. **Live fuel surcharge % (Q9) — biggest gap.** Published only in a weekly JS table; un-fetchable here. Need the live DE fuel page for the current **Standard (road)** and **Express (air)** percentages before judging the contract's fixed fuel %.
2. **Exact 2026 EUR for several §8 accessorials** (Saturday, Signature/Adult Signature, Carbon-neutral, Paper-invoice, SCC audit) and the **§7 duties/brokerage EUR minimums** — all live in the DE `additional-service-charge-de.pdf` / 2026 rate guide PDF, **both of which timed out**. Structure is documented; exact EUR figures need an on-site pull.
3. **Seasonal peak figures are [SECONDARY].** The €0.20 / €7.35 / €77.60 / €475 set is from shipcloud (2025-11-12), not a directly-read UPS PDF. The **year-round Over-Max €440 is [OFFICIAL]**. Re-confirm the peak set against the live `demand-surcharges-europe.pdf` before it drives a number. Also: whether the European scheme **tiers by week** (like the US) or applies flat across the window is unconfirmed.
4. **AddlHandling weight trigger ambiguity (Q3):** ≥25 kg (wein.plus) vs >32 kg (shipcloud). Plan on **25 kg**; confirm.
5. **DAS/Extended-Area tiering (Q5):** only Remote €25 and Residential €3.35 captured; the full Extended-vs-Remote postcode tier table is in the un-fetched rate guide.
6. **All EUR figures are list/book values, business-customer, ex-VAT (DE VAT 19%).** Some secondaries quote member-*net* (discounted) figures — those are flagged inline; the assessment wants the **book** value (full published rate the un-negotiated accessorials apply at).
7. **2026 GRI = 5.9%** is confirmed (loop.com, from UPS's Dec-2025 announce) but the loop figure is framed around US services; the **DE rate guide is the canonical 2026 DE figure** — pull it to confirm the GRI flowed through to the German accessorial table at the same percentage.

---

## Cross-link — feeds the UPS carrier assessment (EU Tender, Picanova DE)

This file is the published-surcharge anchor for the UPS contract assessment:

- **Q7 (surcharge schedule):** §1–§8 here are the book rates the contract's un-negotiated accessorials apply at. The contract waives a *subset*; everything not waived (notably the **seasonal Base Rate Surcharge €0.20/pkg** and the standing Over-Max €440) bills at these full published rates.
- **Q4 (Q4 fuel):** §9 — fuel is a weekly floating index, not a fixed %; the contract's flat fuel figure is a snapshot to stress-test against the live published Standard/Express percentages.
- **Q1 (dim-weight):** §10 — divisor 5000, billable = greater(actual, dim), confirms the basis for billable-weight cost modelling.
- **Seasonal/Q4 exposure:** the **Base Rate Surcharge on every package across 2025-09-29 → 2026-01-17** is the layer that compounds against a photo-gift Q4 volume spike on full-year scoring.

*(Picking into `bank/drafts/notes/` happens at alching, not here — this research file is the source anchor.)*
