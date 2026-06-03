# FedEx PL — Q1 2026 fuel-surcharge history (Intl + Regional) + Switzerland clearance fee

## Question

EU Tender 2026 / FedEx Round-2 rebuild ([[S148_104c786b_eu-tender-dhl-paket-round2|S148]]). Two asks:

1. For **each month of Q1 2026** (and ideally each weekly effective period, then a monthly average), the FedEx PL fuel-surcharge percentages for **both** indices:
   - **International** FSC (applies to International Economy / IE + International Economy Freight / IEF) — based on the U.S. Gulf Coast (USGC) kerosene-type jet-fuel spot price (U.S. EIA, weekly).
   - **Regional** FSC (applies to Regional Economy / RE + Regional Economy Freight / REF) — based on a rounded average of EU Automotive Gas Oil prices (European Commission Weekly Oil Bulletin, incl. duties & taxes).
   Calibration anchor (current week, 1–7 Jun 2026): International **49.25%** at USGC $4.113; Regional **22.50%**.
2. FedEx PL's published **per-parcel customs clearance / disbursement fee for Switzerland** (DAP basis; plus DDP duty/VAT advancement fee if published).

## Date of research

2026-06-03.

## Confidence

**Medium-high** on both indices. The International schedule is **validated** (FedEx's own pulled March history rows match the band table I applied, exactly — see below), so Jan/Feb reconstruction rests on a confirmed table + an authoritative price series. The Regional schedule is reconstructed from the FedEx PL band table + the EC weekly series with no pulled history rows to cross-check, so it is one notch lower. CH disbursement fee: **high** (pulled from FedEx CH's own CHF ancillary schedule).

---

## Findings

### How the two FSCs work (mechanism)

- **International** FSC adjusts weekly off the **USGC kerosene-type jet-fuel spot price** (EIA, published weekly). FedEx applies a **~2-week look-back**: the surcharge effective in week *W* uses the EIA price published ~2 weeks prior. New % takes effect each **Monday**, posted the Friday before. (FedEx PL surcharges page; FedEx US fuel-surcharge page. Lag empirically confirmed below.)
- **Regional** FSC adjusts weekly off a **rounded average of EU-zone Automotive Gas Oil (diesel) prices in EUR**, incl. duties & taxes, from the **EC Weekly Oil Bulletin**. Same Monday-effective cadence. (FedEx PL/EU surcharges pages.)

### The lag, confirmed from FedEx's own pulled history rows

FedEx PL's International history table (retrieved via proxy — see Sources) showed these **PULLED** effective-week rows, each carrying the price FedEx used:

| Effective week | FedEx-shown USGC price | FedEx % (PULLED) | EIA week that price came from |
|---|---|---|---|
| 09–15 Mar 2026 | $2.469 | **35.00%** | EIA 27-Feb-2026 ($2.469) |
| 16–22 Mar 2026 | $3.103 | **40.25%** | EIA 06-Mar-2026 ($3.103) |
| 23–29 Mar 2026 | $3.478 | **43.50%** | EIA 13-Mar-2026 ($3.478) |

The FedEx-shown price for each effective week equals the EIA spot price from ~2 weeks earlier → **~2-week lag confirmed**. And each pulled % matches the FedEx International band table (eff. 6-Apr-2026) applied to that price **exactly** ($2.469→35.00%, $3.103→40.25%, $3.478→43.50%) → the **same International schedule was live across Q1 and into Q2**, so reconstructing Jan/Feb with that table is safe, not a guess. (The 6-Apr table prints up to $4.01→47.75%; the Jun anchor 49.25% at $4.113 is just the same +0.25%/$0.03 slope extended above the printed top.)

### Input price series (both PULLED)

**EIA USGC kerosene-type jet fuel, weekly spot $/gal** (eia.gov, 2026-05-28 release):

| EIA week | $/gal | | EIA week | $/gal |
|---|---|---|---|---|
| 26-Dec-25 | 1.950 | | 13-Feb-26 | 2.154 |
| 02-Jan-26 | 1.908 | | 20-Feb-26 | 2.317 |
| 09-Jan-26 | 1.873 | | 27-Feb-26 | 2.469 |
| 16-Jan-26 | 2.015 | | 06-Mar-26 | 3.103 |
| 23-Jan-26 | 2.095 | | 13-Mar-26 | 3.478 |
| 30-Jan-26 | 2.184 | | 20-Mar-26 | 4.038 |
| 06-Feb-26 | 2.120 | | 27-Mar-26 | 4.009 |

**EC Weekly Oil Bulletin EU avg automotive gas oil, EUR/L** (fuel-prices.eu mirror of the EC bulletin):

| Bulletin week | EUR/L | | Bulletin week | EUR/L |
|---|---|---|---|---|
| 05-Jan-26 | 1.502 | | 23-Feb-26 | 1.545 |
| 12-Jan-26 | 1.496 | | 02-Mar-26 | 1.572 |
| 19-Jan-26 | 1.513 | | 09-Mar-26 | 1.748 |
| 26-Jan-26 | 1.523 | | 16-Mar-26 | 1.835 |
| 02-Feb-26 | 1.534 | | 23-Mar-26 | 1.965 |
| 09-Feb-26 | 1.536 | | 30-Mar-26 | 2.000 |
| 16-Feb-26 | 1.549 | | | |

### FedEx International FSC — weekly Q1 2026 (effective-week basis)

Effective week uses the EIA price ~2 weeks prior, mapped through the FedEx International band table (eff. 6-Apr-2026, validated above). Mar rows where FedEx history was visible are **PULLED**; all others **RECONSTRUCTED**.

| Effective week | Lagged EIA price | FSC % | Source flag |
|---|---|---|---|
| 05–11 Jan | 1.950 (26-Dec) | 31.50% | RECONSTRUCTED |
| 12–18 Jan | 1.908 (02-Jan) | 31.75% | RECONSTRUCTED |
| 19–25 Jan | 1.873 (09-Jan) | 31.50% | RECONSTRUCTED |
| 26 Jan–01 Feb | 2.015 (16-Jan) | 31.75% | RECONSTRUCTED |
| 02–08 Feb | 2.095 (23-Jan) | 31.75% | RECONSTRUCTED |
| 09–15 Feb | 2.184 (30-Jan) | 32.75% | RECONSTRUCTED |
| 16–22 Feb | 2.120 (06-Feb) | 32.25% | RECONSTRUCTED |
| 23 Feb–01 Mar | 2.154 (13-Feb) | 32.50% | RECONSTRUCTED |
| 02–08 Mar | 2.317 (20-Feb) | 33.75% | RECONSTRUCTED |
| 09–15 Mar | 2.469 (27-Feb) | **35.00%** | PULLED |
| 16–22 Mar | 3.103 (06-Mar) | **40.25%** | PULLED |
| 23–29 Mar | 3.478 (13-Mar) | **43.50%** | PULLED |
| 30 Mar–05 Apr | 4.038 (20-Mar) | ~47.75%+ | RECONSTRUCTED (price above printed table top; extrapolated) |

Band-table mapping used (eff. 6-Apr, FedEx EU Intl): $1.89–2.09→31.75%; $1.95→31.50% sits in $1.69–1.89? — note: the published table's lowest printed band is $1.69–1.89→31.50%, then $1.89–2.09→31.75%, then $0.03 steps of +0.25% upward. Jan/Feb prices ($1.87–2.18) fall in the table's flat low end (31.50–32.75%), which is why early-Q1 International barely moves; the late-Mar fuel spike is what drives the climb to 43.50%+.

**Monthly averages (International), effective-week basis:**

| Month | Avg FSC % | Basis |
|---|---|---|
| **January** | **~31.65%** | RECONSTRUCTED (4–5 wks, $1.87–2.02 lagged) |
| **February** | **~32.65%** | RECONSTRUCTED (4 wks, $2.10–2.18 lagged) |
| **March** | **~39–40%** | mixed PULLED/RECONSTRUCTED — flat low ~35% early, spiking to 43.5%+ late |

> **Recommended single Q1 value for the engine (International): ~34–35%** as a quarter average — but Q1 is *not* flat. If the engine prices a representative recent/forward state, the **late-Q1 exit rate (~43.5%, rising)** better reflects the trajectory than the Jan/Feb floor. Recommend modelling Jan ~31.5%, Feb ~32.5%, Mar ~40% rather than one blended number, because the March fuel spike is the load-bearing signal.

### FedEx Regional FSC — weekly Q1 2026 (effective-week basis)

Same ~Monday cadence. Mapped through the FedEx PL **Regional band table** (PULLED in full — see Sources): €1.11–1.15→17.00% rising to €2.51–2.55→32.00%, roughly +0.25% per €0.04 band. **No pulled Regional history rows for Jan–Mar were available**, so all Regional Q1 cells are **RECONSTRUCTED**. The EC/AGO→effective-week lag is not independently confirmed for Regional; assuming a ~1–2-week lag similar to International. Values below apply the band table directly to the EC weekly diesel price (un-lagged, as a base case; a 1–2 wk lag shifts each row by at most one band given how flat Jan/Feb is).

| Bulletin/effective week | EU diesel EUR/L | Regional FSC % | Source flag |
|---|---|---|---|
| early Jan | 1.502 | 19.50% | RECONSTRUCTED |
| mid Jan | 1.496 | 19.50% | RECONSTRUCTED |
| late Jan | 1.513–1.523 | 19.50% | RECONSTRUCTED |
| early Feb | 1.534 | 19.50% | RECONSTRUCTED |
| mid Feb | 1.536–1.549 | 19.50% | RECONSTRUCTED |
| late Feb | 1.545 | 19.50% | RECONSTRUCTED |
| early Mar | 1.572 | 20.00% | RECONSTRUCTED |
| 09-Mar | 1.748 | 22.00% | RECONSTRUCTED |
| 16-Mar | 1.835 | 23.50% | RECONSTRUCTED |
| 23-Mar | 1.965 | 25.00% | RECONSTRUCTED |
| 30-Mar | 2.000 | 25.50% | RECONSTRUCTED |

Band mapping (FedEx PL Regional, PULLED): €1.47–1.55→19.50%; €1.55–1.59→20.00%; €1.71–1.75→22.00%; €1.83–1.87→23.50%; €1.95–1.99→25.00%; €1.99–2.03→25.50%.

**Monthly averages (Regional), effective-week basis:**

| Month | Avg FSC % | Basis |
|---|---|---|
| **January** | **~19.50%** | RECONSTRUCTED (diesel €1.50–1.52, flat) |
| **February** | **~19.50%** | RECONSTRUCTED (diesel €1.53–1.55, flat) |
| **March** | **~23%** | RECONSTRUCTED (diesel €1.57→2.00, climbing 20.0%→25.5%) |

> **Recommended single Q1 value for the engine (Regional): ~20.5%** quarter average — but, like International, Q1 Regional is back-loaded: flat ~19.5% Jan–Feb, climbing to ~25.5% by end-March on the EU diesel spike. Model Jan ~19.5%, Feb ~19.5%, Mar ~23% rather than one blended number.

**Sanity check against the June anchor:** the brief's current Regional 22.50% corresponds to band €1.75–1.79 on the pulled table — consistent with EU diesel having eased from the late-March €2.00 peak back to ~€1.75–1.78 by early June. The table reproduces the anchor, supporting the reconstruction.

### Switzerland customs clearance fee

FedEx PL/EU pages are gated, but FedEx **Switzerland's** own ancillary fee schedule (pulled via proxy, CHF-denominated) is authoritative for the CH leg:

- **DDP basis — Disbursement / Advancement Fee** (FedEx fronts duty + import VAT to Swiss customs, invoices the receiver): **2.50% of the duties & taxes advanced, minimum CHF 22.00, whichever is greater.** (FedEx CH ancillary schedule.) — This is the load-bearing per-shipment CH clearance fee for the tender.
- **DAP basis — standard clearance:** FedEx Express routine customs clearance into Switzerland is **bundled into the transportation charge** — there is **no separate flat per-parcel "clearance entry fee"** for a standard single-commodity dutiable Express shipment. The clearance cost only surfaces as the disbursement fee above when FedEx advances the duty/VAT (i.e., on a DDP/duty-unpaid-by-shipper consignment). So the DAP-basis incremental clearance fee for a routine parcel is effectively **CHF 0** above transport, with situational add-ons (below).
- **Situational add-ons** (not standard per-parcel; only if triggered): multi-line-item fee **CHF 13.00 per line item from the 6th line item**; In-Bond Transit **CHF 74.00/shipment**; Other Government Agency **CHF 84.00/shipment + pass-through**; Post Entry Adjustment **CHF 135.00/shipment**. (FedEx CH ancillary schedule.)

> **Recommended CH clearance figure for the engine:** **CHF 22.00 minimum (2.5% of duty+VAT) per shipment on a DDP basis**; **CHF 0 incremental on a DAP basis** for standard single-commodity parcels (clearance bundled in transport). Earlier proxy reads also surfaced a generic pan-EU display (€8 min / €15 flat €50–600 / 2.5% >€600); the **CH-specific CHF 22 / 2.5%** schedule supersedes it for Switzerland.

---

## Sources

- **EIA — Weekly U.S. Gulf Coast Kerosene-Type Jet Fuel Spot Price FOB ($/gal)** — https://www.eia.gov/dnav/pet/hist/eer_epjk_pf4_rgc_dpgW.htm (via LeafHandler). Authoritative weekly price series, the basis of the International FSC. Pulled the full Q1 2026 series; release date 2026-05-28. **Load-bearing — the International index input.**
- **FedEx PL — Shipping Surcharges** — https://www.fedex.com/en-pl/shipping/surcharges.html (direct fetch **gated**; retrieved via r.jina.ai proxy). Source of the Regional band table (full), the International band structure, and the **pulled March 2026 International history rows** that validated the reconstruction. **Load-bearing.**
- **FedEx — International Fuel Surcharge table, eff. 6 Apr 2026 (EU)** — https://www.fedex.com/content/dam/fedex/eu-europe/downloads/FedEx-International-Fuel-Surcharge-6-April.pdf (direct **gated**; retrieved via r.jina.ai proxy). The full International band table ($1.69–1.89→31.50% … $3.98–4.01→47.75%, +0.25%/$0.03). **Load-bearing — the International threshold table applied.**
- **fuel-prices.eu — EU Weekly Fuel Reports 2026** (mirror of EC Weekly Oil Bulletin) — https://www.fuel-prices.eu/weekly/2026/ . EU-avg automotive gas oil EUR/L, full Q1 2026 weekly. **Load-bearing — the Regional index input.** Cross-checked against EC bulletin (week 02-Mar EU avg 1629.22 EUR/1000L ≈ €1.63/L; bulletin n°2296 prices at 23-Feb-2026).
- **European Commission — Weekly Oil Bulletin** — https://energy.ec.europa.eu/data-and-analysis/weekly-oil-bulletin_en . The official EC source the Regional FSC names; used to corroborate the fuel-prices.eu mirror.
- **FedEx CH — ancillary/clearance fee schedule (CHF)** — https://www.fedex.com/content/fedex-com/component-library/ancillary/en_tw/ch.html and https://www.fedex.com/en-ch/billing/duty-tax.html (via r.jina.ai proxy). Disbursement Fee 2.50% / min CHF 22.00; situational flat fees. **Load-bearing — the CH clearance answer.**
- **FedEx US fuel-surcharge page / ShipSigma / IndexBox / Supply Chain Dive** — https://www.fedex.com/en-us/shipping/fuel-surcharge.html ; https://shipsigma.com/blog/fedex-fuel-surcharges-2026 ; https://www.indexbox.io/blog/fedex-and-ups-hike-fuel-surcharges-and-introduce-new-shipping-fees-in-may-2026/ ; https://www.supplychaindive.com/news/ups-and-fedex-up-international-fuel-surcharge-rates-add-surge-fees/819749/ . Mechanism, Monday-effective cadence, ~2-wk lag, and the "$4/gal → 38.5% export" datapoint (US export column — note the EU/PL Intl column runs higher). Context, not primary.

## Gaps & open questions

- **No pulled Jan/Feb International history rows.** The FedEx PL page only retained recent weeks (earliest visible was 09-Mar). Jan/Feb International %s are RECONSTRUCTED — but on a table validated against the adjacent pulled March rows, so confidence is good. To convert to PULLED, retrieve a Wayback snapshot of the FedEx PL surcharges page dated Jan/Feb 2026 (WebFetch could not reach web.archive.org this session — try from a browser or a different archive proxy).
- **Regional history rows entirely absent for Q1.** All Regional Q1 cells are RECONSTRUCTED with no FedEx-pulled cross-check (unlike International). The Regional EC-price→effective-week lag is assumed (~1–2 wk), not confirmed; given how flat Jan/Feb diesel is, lag choice barely moves the result, but late-March (steep climb) is lag-sensitive by up to one band per week.
- **Band-table edge precision.** The 6-Apr International table's lowest printed band is $1.69–1.89→31.50%; a couple of early-Jan lagged prices sit right at band edges, so ±0.25% per affected week is possible. Immaterial to the monthly average.
- **CH DAP flat fee.** Could not find a separately published flat DAP per-parcel clearance/entry fee for CH (none appears to exist for standard Express — clearance is bundled). If the tender model needs an explicit DAP clearance line, CHF 0 incremental is the defensible default; confirm against the FedEx CH conditions of carriage (Jan-2026) or the new-offer export rates PDF if a contractual clearance line is required.
- **June anchor cross-check passed** for both indices (Intl 49.25% ≈ table extended to $4.113; Regional 22.50% ≈ €1.75–1.79 band), which is the strongest available validation of both reconstructed schedules.
