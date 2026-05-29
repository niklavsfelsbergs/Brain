# FedEx Poland public surcharges — Maersk ROW lane (FedEx Economy)

**Question.** Maersk's EU Tender 2026 offer includes a ROW (rest-of-world) lane operated as FedEx Economy via FedEx Poland. Maersk says: apply Maersk's contracted *base rates*, but the *surcharge definitions/percentages* follow FedEx Poland's public published schedule. Find the public FedEx Poland values for (1) fuel surcharge, (2) peak/demand seasonal surcharge, (3) non-standard parcel / Additional Handling definition + amounts, (4) Extended/Remote Area surcharge. Replay window: Q1 2026.

**Date of research.** 2026-05-27 (penguin p2, scoped to Jebrim).
**Confidence.** Medium. The mechanism, structure, dates, non-standard-parcel definition, and demand-surcharge windows are well-sourced. The **exact published fuel %** and **exact PLN amounts** could not be read off FedEx's own pages — see Gaps. Every FedEx HTML/PDF rate page returned an access-denied error page to the fetcher (geo/bot gate); figures below come from FedEx pages as surfaced by search-engine summaries, FedEx-group sister docs (TNT Poland), trade-press citing the FedEx tables, and Polish carrier-aggregators that republish FedEx PL's verbatim criteria.

---

## Source map

Load-bearing:
- **FedEx Poland surcharges (PL + EN)** — https://www.fedex.com/pl-pl/shipping/surcharges.html , https://www.fedex.com/en-pl/shipping/surcharges.html — the canonical Poland fuel-surcharge mechanism + index. *HTML blocked to fetcher; mechanism read via search summary.*
- **FedEx International Fuel Surcharge table (EU/Europe), eff. 6 April 2026** — https://www.fedex.com/content/dam/fedex/eu-europe/downloads/FedEx-International-Fuel-Surcharge-6-April.pdf — the actual European international FSC table. *Blocked to fetcher.*
- **Demand Surcharge for FedEx international services in Europe (PDF)** — https://www.fedex.com/content/dam/fedex/international/rates/fedex-demand-surcharge-en-eu.pdf — the intra-Europe Economy peak/demand schedule. *Blocked to fetcher; windows/values read via search summary.*
- **FedEx Poland VASS (value-added services & surcharges) PDF** — https://www.fedex.com/content/dam/fedex/international/rates/fedex-rates-vassuis-pl-pl.pdf — would carry exact PLN non-standard/area amounts. *Blocked; the file Maersk referenced ("new-offer-rates-vassuis-en-pl.pdf") is this VASS family.*
- **Supply Chain Dive** — https://www.supplychaindive.com/news/ups-and-fedex-up-international-fuel-surcharge-rates-add-surge-fees/819749/ — trade press citing the May-2026 FedEx international FSC structural change.
- **Global Trade Magazine** — https://www.globaltrademag.com/fedex-and-ups-hike-fuel-surcharges-and-introduce-new-shipping-fees-in-may-2026/ — corroborates the export %.
- **apaczka help centre** — https://www.apaczka.pl/centrum_pomocy/przesylki-standardowe-vs-niestandardowe-fedex/ — republishes FedEx PL non-standard-parcel definition verbatim.
- **polkurier knowledge base** — https://www.polkurier.pl/baza-wiedzy/artykul/maksymalne-wymiary-przesylek-i-uslugi-dodatkowe-w-fedex — FedEx PL dimension thresholds.
- **TNT Poland fuel surcharges (FedEx group)** — https://www.tnt.com/express/pl_pl/site/shipping-services/fuel-surcharges-europe.html — confirms weekly-from-11-May-2026 cadence + USGC/EIA index, 2-week lag.

Secondary / corroborating: kurjerzy.pl, przesylarka.pl (Polish carrier blogs), transimpact.com, FedEx en-us fuel/demand pages.

---

## 1. Fuel surcharge

### Mechanism (well-sourced)
- The fuel surcharge that governs **FedEx Express International** services (export & import) ex-Poland is the **FedEx International Fuel Surcharge**, expressed as a **% of transportation charges**. It is **distinct from** the FedEx domestic/ground FSC. (FedEx PL surcharges page, via search summary — https://www.fedex.com/pl-pl/shipping/surcharges.html and https://www.fedex.com/en-pl/shipping/surcharges.html)
- **Index:** rounded average of the **U.S. Gulf Coast (USGC) spot price for a gallon of kerosene-type jet fuel**, as published by the **U.S. Energy Information Administration (EIA)**, applied with a **two-week delay**. (FedEx PL surcharges page + TNT Poland — https://www.tnt.com/express/pl_pl/site/shipping-services/fuel-surcharges-europe.html)
- **Update cadence:** historically **monthly**; **changed to weekly from 11 May 2026** (effective Mondays, table published the preceding Friday). (TNT Poland, via fetch — https://www.tnt.com/express/pl_pl/site/shipping-services/fuel-surcharges-europe.html ; FedEx PL surcharges page confirms recent updates eff. 9 Jun 2025, 6 Apr 2026, 11 May 2026)
- **Regional Economy caveat:** the *International* fuel surcharge does **not** apply to **FedEx Regional Economy / Regional Economy Freight** — those use a separate **Dynamic Fuel Surcharge** based on EU diesel prices. The Maersk ROW lane is described as **FedEx Economy** (international), so the **International** FSC is the governing one — *but confirm the exact FedEx service name on the Maersk lane, because "Regional Economy" would change the index*. (FedEx en-pl surcharges page, via search summary — https://www.fedex.com/en-pl/shipping/surcharges.html)

### Published percentage (the load-bearing number — partially sourced)
The actual published FedEx **International** Fuel Surcharge table figures for the bands around current jet-fuel prices (early-mid 2026):

- **Effective 11 May 2026**, for jet fuel in the **$3.99–$4.03/gal** band: **Export 38.50%**, **Import 42.75%**. The published table spans roughly **Export 37.00%–38.50% / Import 41.25%–42.75%** across the bands near $4/gal. (Search summary of FedEx France/Italy/EU surcharge pages + FedEx US table eff. 5-11-26 — https://www.fedex.com/content/dam/fedex/us-united-states/services/fuel_surcharge_effective_5-11-26.pdf ; corroborated https://www.indexbox.io/blog/fedex-and-ups-hike-fuel-surcharges-and-introduce-new-shipping-fees-in-may-2026/)
- A **structural increase** took effect **11 May 2026**: **+2 percentage points** on international **export** FSC calculations and **+2.5 pts** on international **import**. Example given: at $4/gal jet fuel the export FSC rose from **36.5% → 38.5%**. (Supply Chain Dive — https://www.supplychaindive.com/news/ups-and-fedex-up-international-fuel-surcharge-rates-add-surge-fees/819749/ ; Global Trade Magazine — https://www.globaltrademag.com/fedex-and-ups-hike-fuel-surcharges-and-introduce-new-shipping-fees-in-may-2026/)
- **Q1 2026 (the replay window)** therefore sat **below** the post-11-May figures by the ~2-pt structural step: international **export FSC ≈ 36.5%** at $4/gal jet fuel before 11 May 2026, scaling up/down by the USGC band. *(inferred from the structural-change deltas above applied backward to Q1 2026; the exact week-by-week Q1 % was not directly sourced — see Gaps.)*
- For contrast, the **domestic** FedEx FSC (NOT applicable to this international lane) was far lower: **Domestic Air FSC 20% → 21.75% eff. 1 Dec 2025**. (Search summary, transimpact — https://transimpact.com/blog/fedex-increases-domestic-fuel-surcharges-effective-december-1-2025)

### Does the 49.50%-published / 24.75%-net figure check out?
**No — it does not match any FedEx-published *International* Fuel Surcharge table I could source.** The published FedEx International FSC for export sits in the **~36.5%–38.5%** range across Q1–mid-2026 (import ~41–43%), governed by the USGC jet-fuel band, not ~49.5%. Three possibilities to put back to Maersk:

1. **The 49.50% is Maersk's own list/contract surcharge basis, not FedEx Poland's public number.** If so, "we apply FedEx Poland's published surcharges" and "49.50% before a 50% discount" are in tension — the public FedEx number is materially lower (~37–43%), so a flat 50% discount off 49.5% (→24.75%) would *not* reproduce the public schedule.
2. **The figure may conflate a different band/year** — FedEx US peak-period or an older/higher jet-fuel band, or an import figure plus an add-on. Even the *import* published band (~41–43%) doesn't reach 49.5% in the sourced tables.
3. **Net 24.75% coincidentally lands near the published export FSC's lower-$3/gal bands** — i.e., 24.75% net is *in the ballpark of a genuinely-published low-fuel-price export %*, which may be why it "looked right." But the arithmetic path (49.5% × 50%) is not the published-schedule path.

**Recommendation for Jebrim/Niklavs:** ask Maersk to (a) name the exact FedEx service on the ROW lane (International Economy vs Regional Economy — different index), and (b) point to the *specific* FedEx Poland published table/row the 49.50% comes from. If they can't, the public FedEx International FSC (~37–43% gross, USGC-banded, no 50% discount) is the defensible public figure, and the "24.75% net" should be treated as a **Maersk-negotiated rate**, not a FedEx-Poland-published one. **Confidence: medium-high that 49.50% ≠ the published International FSC; the discrepancy is the headline finding.**

---

## 2. Peak / Demand / Seasonal surcharge

Two layers exist, and they are different things — keep them separate:

### A. FedEx US/standard "Demand Surcharge" window (Maersk's "Oct 27 – Jan 18")
- FedEx peak/demand surcharges for standard & expedited services run **27 October 2025 – 18 January 2026**, peaking **24 November – 28 December**. This matches Maersk's "usually Oct 27 – Jan 18, varies yearly." (Search summary, Supply Chain Dive 2025 peak article — https://www.supplychaindive.com/news/fedexs-2025-holiday-demand-surcharge-prices/752664/ ; FedEx demand-surcharges page — https://www.fedex.com/en-us/shipping/rate-changes/demand-surcharges.html)
- *This window is the US-published one. The intra-Europe Economy lane (relevant here) uses a different window — see B.*

### B. Demand Surcharge for FedEx **international services in Europe** (the relevant one for an ex-Poland Economy lane)
Per-kilo, applied in date bands (2025/26 season):
- **20 Oct 2025 – 21 Dec 2025**: intra-Europe (export & import) and Israel→Europe **Economy** Demand Surcharge **€0.10 → €0.15 per kg**; **Priority €0.30 → €0.35 per kg**. (Search summary of the EU demand-surcharge PDF — https://www.fedex.com/content/dam/fedex/international/rates/fedex-demand-surcharge-en-eu.pdf)
- **22 Dec 2025 – 15 Feb 2026**: steps back down — Economy **€0.15 → €0.10 per kg**; Priority **€0.35 → €0.30 per kg**. (same PDF, via search summary)
- Additional bands apply to Europe→US/Canada, LAC, MEISA, Australia/NZ lanes during the same window (values not individually captured). (same PDF)

So for the **ROW Economy lane**, the public European demand surcharge is a **per-kg** add (≈ **€0.10 baseline, €0.15 in the 20 Oct–21 Dec peak**), **not** a per-piece flat fee. *(Note: the en-EU PDF is denominated in EUR; a FedEx Poland PLN equivalent likely exists in the PL VASS doc — not sourced.)*

### C. FedEx Poland "opłata okresowa" (periodic/peak), weight-based PLN
A Polish carrier blog citing FedEx PL's periodic surcharge (2024 season) showed a **weight-based table 0.50–8.80 PLN/kg by route, minimum 4.40 PLN/shipment**, "opłata okresowa od 16 września 2024." (kurjerzy.pl, via fetch — https://www.kurjerzy.pl/blog/aktualnosci/przypomnienie-o-doplatach-w-szczycie-paczkowym-kluczowe-zmiany-w-ups-fedex-i-dhl2/) — *this is a 2024-season aggregator figure; treat as indicative of shape (PLN/kg, min charge), not as the current 2025/26 published value. The authoritative current PLN values live in the FedEx PL VASS PDF (blocked).* 

---

## 3. Non-standard parcel ("przesyłka niestandardowa" / Additional Handling)

### Definition / trigger spec (well-sourced — these are the criteria Maersk says to reuse)
A FedEx parcel is **non-standard** if it fails **any** standard criterion. Standard = all of:
- **Weight** up to **70 kg** actual weight (above 70 kg → non-standard). (apaczka, polkurier — https://www.apaczka.pl/centrum_pomocy/przesylki-standardowe-vs-niestandardowe-fedex/ , https://www.polkurier.pl/baza-wiedzy/artykul/maksymalne-wymiary-przesylek-i-uslugi-dodatkowe-w-fedex)
- **Longest edge** up to **150 cm**. (same)
- **No other edge exceeding 70 cm.** (same)
- **Sum of the two longest sides under 180 cm.** (same)

Plus, a parcel is non-standard (verbatim from FedEx PL criteria, via apaczka) if it:
- *"Ma przesunięty środek ciężkości lub może się łatwo przewrócić"* — shifted centre of gravity / tips easily.
- *"Nie jest prostopadłościanem lub ma nieregularny kształt"* — not a cuboid / irregular shape (tube, cylinder, oval).
- *"Najdłuższy bok nie jest podstawą paczki"* — longest side is not the base.
- *"Składa się z dwóch lub kilku odrębnych części połączonych"* — two or more separate parts joined together.
- *"Nie może być sortowana za pomocą sortera mechanicznego"* — cannot be machine-sorted.
(apaczka, verbatim — https://www.apaczka.pl/centrum_pomocy/przesylki-standardowe-vs-niestandardowe-fedex/)

Related FedEx PL rule: parcels **above 25 kg actual weight** carry an **Additional Handling Surcharge (AHS) – Weight** (introduced "od 14 lipca"). (przesylarka.pl — https://przesylarka.pl/czytelnia/zmiany-w-doplatach-i-warunkach-przewozu-paczek-fedex) — *so "Additional Handling" in FedEx PL is itself split into sub-triggers: AHS-Weight (>25 kg), plus the dimensional/shape non-standard triggers above.*

Volumetric weight formula: **L × W × H (cm) ÷ 5000**. (apaczka — same URL)

### Amounts
**Per the brief, the rates come from Maersk** (Maersk: "same definitions as FedEx Poland; ignore the rates in the link, use our rates"). The PLN amounts on the public FedEx PL VASS schedule were **not** sourced (PDF blocked) and are not needed — only the definition/trigger spec above is needed, which is captured. **Confidence on the definition: high.**

---

## 4. Extended / Remote Area surcharge (Out of Delivery / Pickup Area)

- FedEx PL applies **Out of Delivery Area (ODA)** and **Out of Pickup Area (OPA)** / Extended Area surcharges; these are listed in the FedEx PL VASS schedule and the surcharges page. The exact **PLN amounts were not sourced** (the VASS PDF and surcharges HTML were both blocked to the fetcher). (Referenced on FedEx PL surcharges page — https://www.fedex.com/pl-pl/shipping/surcharges.html ; polkurier lists "usługi dodatkowe" including area surcharges — https://www.polkurier.pl/baza-wiedzy/artykul/maksymalne-wymiary-przesylek-i-uslugi-dodatkowe-w-fedex)
- The EU international demand-surcharge PDF (item 2B) also contains **Out of Delivery Area** demand rows for the peak window. (https://www.fedex.com/content/dam/fedex/international/rates/fedex-demand-surcharge-en-eu.pdf)
- **Confidence: low on values.** Only the existence/structure is confirmed; figures need the VASS PDF.

---

## Gaps & open questions

1. **Exact published fuel % for Q1 2026, week by week.** Sourced the structure and the ~36.5–38.5% export / ~41–43% import range around $4/gal jet fuel, but not the precise Q1 2026 weekly rows. The FedEx **International** Fuel Surcharge PDF (eff. 6 Apr 2026) and the FedEx PL surcharges page are the authoritative sources — both blocked to the fetcher. **A human opening https://www.fedex.com/content/dam/fedex/eu-europe/downloads/FedEx-International-Fuel-Surcharge-6-April.pdf and the FedEx PL page directly will read the exact figure in seconds.**
2. **The 49.50% origin.** Strongest unresolved item. The published FedEx International FSC does not reach 49.5% in any sourced table. Need Maersk to cite the exact table/row, or confirm 49.5% is a Maersk-internal basis (in which case "follows FedEx Poland's public schedule" is inaccurate for fuel).
3. **Which FedEx service the ROW lane actually is.** International Economy (USGC jet-fuel index) vs Regional Economy (EU diesel Dynamic Fuel Surcharge) — different index, different %. Confirm with Maersk.
4. **Exact PLN amounts** for non-standard/Additional Handling, periodic/peak, and ODA/OPA — all live in the FedEx PL VASS PDF (`fedex-rates-vassuis-pl-pl.pdf`), which was blocked. Per the brief these rates come from Maersk anyway, so this is a low-priority gap except for ODA/OPA where Maersk's treatment is unstated.
5. **Currency basis.** EU demand surcharge is in EUR/kg; FedEx PL domestic schedules are PLN. Confirm which currency Maersk's ROW surcharge math uses.

---

## One-line synthesis
The governing fuel surcharge is FedEx's **International** Fuel Surcharge (USGC jet-fuel index, monthly→weekly from 11 May 2026), published at roughly **36.5–38.5% export / 41–43% import** around $4/gal in early-mid 2026 — so **the ~49.50%-published / 24.75%-net figure does NOT reconcile with FedEx Poland's public International FSC** and should be put back to Maersk; the non-standard-parcel definition and the intra-Europe peak/demand windows (≈€0.10→€0.15/kg, 20 Oct–21 Dec 2025) are confirmed, while exact PLN values for handling/area surcharges remain in a blocked FedEx PL VASS PDF.
