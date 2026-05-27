# FedEx EU-tender — public interim values: fuel, FX, remote-area + address-correction

**Date:** 2026-05-27
**Player:** Jebrim | **Context:** EU Tender 2026, FedEx carrier. v1 cost engine has fuel=0, FX=4.30 PLN/EUR placeholder, no remote-area surcharge. Pulling public interim values ahead of a carrier meeting.
**Shipper:** Picanova ex Stettin (PL). Services in scope: **RE** = FedEx Regional Economy (intra-Europe ground/road, dominant service); **IE** = FedEx International Economy (international air).
**Confidence:** Targets 2 and 3 high (authoritative sources). Target 1 low — FedEx publishes the percentages only on access-gated pages; the per-month table is unresolved and becomes a carrier ask.

---

## Target 1 — FedEx Poland fuel surcharge, 2026 Q1 (by service)

### Structure (authoritative — this is the load-bearing finding for the engine)

FedEx Poland runs **three independent fuel-surcharge indices**, confirmed verbatim in the on-disk VASS schedule *(source: `bi-analytics-main/NFE/projects/2_EU_tender_2026/carrier_responses_to_open_questions/Maersk/new-offer-rates-vassuis-en-pl.pdf`, p.6, "Fuel Surcharge", applicable in Poland from 5 Jan 2026)*:

- **International Fuel Surcharge** — "Dynamic Fuel Surcharge according to the variation in the price of **kerosene-type jet fuel** for **all international services except** FedEx Regional Economy and FedEx Regional Economy Freight." → **This is the index that applies to IE (FedEx International Economy).**
- **Regional Fuel Surcharge** — "For **FedEx Regional Economy and FedEx Regional Economy Freight** services… Dynamic Fuel Surcharge which is based on the **automotive gas oil prices from the EU country/territory zone**." → **This is the index that applies to RE (and REF).**
- **Domestic Fuel Surcharge** — separate, for FedEx First/Priority Express/Priority/Priority Express Freight/Priority Freight (automotive gas oil, EU zone). Not in scope for RE/IE.

So **RE and IE are on different fuel indices**: RE on the EU automotive-gas-oil (diesel) regional index, IE on the kerosene jet-fuel international index. The v1 engine's single fuel=0 placeholder cannot be replaced by one number — it needs (at minimum) two: a Regional % for RE and an International % for IE.

### Publication cadence (observed)

- **Regional / Express Regional index: weekly.** "Changes to the FedEx Express Regional fuel surcharge will be applied effective each **Monday**, with information on the fuel surcharge for each week available approximately the **Friday before**." *(source: search-surfaced text from FedEx en-* surcharges pages, 2026-05-27 — full pages access-gated; see Gap)*. Tied to EU Automotive Gas Oil prices published by the European Commission, DG Transport & Energy.
- **International index: periodic step changes** with named effective dates — "the International FedEx Fuel Surcharge will be updated" effective **6 April 2026** and again **11 May 2026** (updated table available ~3 days before each effective date). *(source: FedEx CDN PDF title + search text, `https://www.fedex.com/content/dam/fedex/eu-europe/downloads/FedEx-International-Fuel-Surcharge-6-April.pdf`, 2026-05-27)*.

### Percentages retrieved

- **International index, ~late May 2026:** A third-party logistics analysis reports international air-export/import fuel surcharges from "both integrators" (UPS + FedEx) "reached as high as **49.75%**" in May 2026 *(source: `https://flexlogistics.eu/ups-and-fedex-fuel-surcharge-hikes-how-multi-country-eu-sellers-should-respond/`, accessed 2026-05-27)*. **Caveat: this is a non-FedEx aggregate covering UPS and FedEx jointly, not a FedEx-published per-service figure — treat as an order-of-magnitude indicator for IE, not a citable contract value.**
- **Regional index, any 2026 month:** not retrievable from public sources (see Gap).
- **Jan / Feb / Mar 2026, either index:** not retrievable from public sources (see Gap).

### Why the percentages could not be pulled

Every FedEx-published surcharge surface was access-gated on 2026-05-27:
- `https://www.fedex.com/en-pl/shipping/surcharges.html` → "you don't have permission to view this webpage" (incident-numbered error).
- `https://www.fedex.com/en-pl/shipping/rates/fedex-rates.html` → same error.
- `https://www.fedex.com/en-gb/shipping/fuel-surcharge.html` → same error.
- `https://www.fedex.com/content/dam/fedex/eu-europe/downloads/FedEx-International-Fuel-Surcharge-6-April.pdf` (the live table) → same error via fetch.
- web.archive.org → not fetchable from this environment.

The structure, index definitions, and cadence above are firm; the actual % values per month are the gap.

---

## Target 2 — ECB EUR/PLN reference rate, 2026 Q1 monthly averages

Replaces the 4.30 PLN/EUR placeholder.

| Period | EUR/PLN (PLN per 1 EUR) | Source |
|---|---|---|
| **Jan 2026 avg** | **4.2114** | exchange-rates.org monthly avg, ECB-reference-based |
| **Feb 2026 avg** | **4.2186** | exchange-rates.org monthly avg |
| **Mar 2026 avg** | **4.2725** | exchange-rates.org monthly avg |
| **Q1 2026 avg** | **≈ 4.234** *(inferred: mean of the three monthly averages = (4.2114+4.2186+4.2725)/3 = 4.2342)* | computed |
| 2026 YTD avg (to late May) | 4.2398 | exchange-rates.org |

*(source for the three monthly averages and YTD: `https://www.exchange-rates.org/exchange-rate-history/eur-pln-2026`, accessed 2026-05-27, double-fetched and consistent.)*

**Cross-check against ECB daily reference rates** *(source: `https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/eurofxref-graph-pln.en.html`, accessed 2026-05-27)* — daily values are consistent with the monthly averages above:
- Feb daily sample: 4.2105–4.2243 (Feb 2: 4.2173; Feb 16: 4.2105; Feb 23: 4.2173).
- Mar daily sample: 4.2440–4.2890 (Mar 2: 4.2440; Mar 31: 4.2890).
- Recent May daily: May 4: 4.2570; May 6: 4.2330; May 26: 4.2315.
- 2026 daily extremes: low 4.1989 (Jan 28), high 4.2976 (Mar 9) *(source: search of exchange-rates.org.uk 2026 history, 2026-05-27)*.

**Verdict on the 4.30 placeholder:** **4.30 is HIGH** versus actual. Q1 2026 actual averaged ~4.23 PLN/EUR; the placeholder over-states PLN per EUR by ~1.5% (4.30 vs ~4.234). Even the 2026 single-day peak (4.2976, Mar 9) did not reach 4.30. Net effect: a cost engine converting PLN-denominated FedEx charges into EUR at 4.30 **understates** the EUR cost (divides by too large a number); at 4.234 the EUR figure is ~1.5% higher. Recommend the Q1 average ~4.234 (or the live monthly rate) as the interim replacement.

*Note on authority:* exchange-rates.org tracks the ECB reference series; the per-month numbers were corroborated against the ECB's own daily graph page. The ECB Data Portal series `EXR.M.PLN.EUR.SP00.A` ("Spot Polish zloty Euro Average", Monthly, last updated 30 Apr 2026) is the canonical source but did not return its numeric values through the fetch tool — flagged so the figures can be confirmed straight off `data.ecb.europa.eu` before they go into the engine.

---

## Target 3 — FedEx Poland remote-area + address-correction surcharges

**Source (authoritative, on disk):** `bi-analytics-main/NFE/projects/2_EU_tender_2026/carrier_responses_to_open_questions/Maersk/new-offer-rates-vassuis-en-pl.pdf` — FedEx Poland "Value Added Services and Surcharges (VASS)", PLEN-SLR-VASS, **applicable in Poland from 5 January 2026**, all fees **exclusive of VAT** (footnote 3), PLN. (Filed in the Maersk response folder but it is the FedEx PL schedule.)

### (a) Remote-area / out-of-delivery-area surcharge — "Extended Area Service" (p.5)

Definition: "Shipments picked up from or delivered to remote and less accessible locations are assessed an **Out-of-Pick-up-Area (OPA)** or **Out-of-Delivery-Area (ODA)** surcharge." The schedule says: **"Please refer to the list of postal codes or areas where this surcharge applies."** → **a published postcode list exists** (it is hyperlinked from the live schedule; the list itself was not pulled here).

**Trigger basis: tiered by postcode/area, charge basis differs per tier** (INTERNATIONAL):

| Tier | Charge | Basis |
|---|---|---|
| Tier A | PLN 15 / shipment | per-shipment flat |
| Tier B | PLN 2.60 / kg | per-kg, **minimum PLN 105** |
| Tier C | PLN 3.35 / kg | per-kg, **minimum PLN 135** |

So it is **per-postcode-list driven**, and within that, Tier A is a flat per-shipment fee while Tiers B and C are per-kg with a minimum charge. (No DOMESTIC EAS row is shown — international tiers are what's published.) Effective 5 Jan 2026.

### (b) Address-correction surcharge — "Address Correction" (p.5)

Trigger: "If a recipient's address on an Air Bill, Air Waybill, Waybill or shipping label is **incomplete or incorrect**, we may attempt to find the correct address and complete delivery and we will assess a surcharge." (Also applies to a broker's incomplete/incorrect address under International Broker Select.)

| Scope | Amount | Basis |
|---|---|---|
| **INTERNATIONAL** | **PLN 43.70 / shipment** | per-shipment flat |
| DOMESTIC | PLN 12 / shipment | per-shipment flat |

Effective 5 Jan 2026. Exclusive of VAT.

### Adjacent surcharges captured in passing (same schedule, may matter to the engine)

These were not asked for but are in the same VASS doc and are the kind of thing the v1 engine likely also zeroes — flagged for the meeting, not picked here:
- **Additional Handling Surcharge (INTERNATIONAL):** Dimension PLN 150/pkg; Packaging PLN 120/pkg; Weight (>25 kg) PLN 180/pkg (highest single applies; 18 kg min billable weight on AHS-Dimension).
- **Oversize Charge (INTERNATIONAL):** PLN 220/package.
- **Demand Surcharge:** variable, references `fedex.com/demand-surcharges` (separate EU demand-surcharge PDF exists: `https://www.fedex.com/content/dam/fedex/international/rates/fedex-demand-surcharge-en-eu.pdf`).
- **Third Party Billing:** 2.5% of total shipment charges. **Toll (DOMESTIC):** 6.5%.

---

## STILL A GAP — carrier ask

Items that could **not** be resolved from public sources as of 2026-05-27. These are the questions to put to FedEx:

1. **Fuel % — Jan, Feb, Mar 2026, Regional index (RE).** Not publicly retrievable. The Regional index is weekly (Monday-effective, EU automotive gas oil) but FedEx does not publish a historical Q1 table on an accessible page. **Ask FedEx for the weekly or monthly Regional fuel % for Jan–Mar 2026.**
2. **Fuel % — Jan, Feb, Mar 2026, International index (IE).** Not publicly retrievable. Only a non-FedEx aggregate (~49.75%, UPS+FedEx combined, May 2026) surfaced; no clean per-month FedEx-published figure. **Ask FedEx for the International fuel % effective each step-change date Jan–Mar 2026** (and confirm the ~late-May current value).
3. **Current (late-May 2026) fuel % for RE and IE, FedEx-published.** The live FedEx surcharge/fuel pages and the live International-fuel PDF were all access-gated. **Ask FedEx to confirm the current % for both indices** (or re-attempt the live `en-pl/shipping/surcharges.html` from an unblocked network).
4. **Which index applies to RE vs IE *for THIS contract.*** Public docs say RE→Regional (diesel) index and IE→International (jet-fuel) index. Confirm the contract doesn't carve out a negotiated/blended fuel basis. **Carrier confirmation needed — do not assume the public default carries into the tender.**
5. **Fuel scope: base-only vs base+surcharges.** Whether the fuel % applies to the base transportation charge only, or also to surcharges (and which ones). **Explicitly carrier-only — not guessed here.**
6. **The Extended Area Service postcode list.** Confirmed to exist and is referenced from the live schedule, but the actual list of OPA/ODA postcodes (and which Picanova destination lanes fall in Tier A/B/C) was not pulled. **Obtain the current postcode/area list** to estimate remote-area exposure on Picanova's actual destination mix.
7. **ECB monthly figures — canonical confirmation.** The Q1 monthly averages (Jan 4.2114, Feb 4.2186, Mar 4.2725; Q1 ≈ 4.234) are corroborated across two sources but came from exchange-rates.org + the ECB daily graph, not the ECB monthly series numerics directly. **Before they enter the engine, confirm off `data.ecb.europa.eu` series `EXR.M.PLN.EUR.SP00.A`.** (This is a verification step, not a carrier ask.)
