# S099 p2 — FedEx public interim values (fuel / FX / remote-area)

Penguin run. Pulling three external data sets for the FedEx v1 cost-engine recalibration ahead of carrier meeting. Output: `research/2026-05-27-fedex-fuel-fx-remotearea.md`.

## Turn log

- Source map opened. Read brief: 3 targets (FedEx PL fuel %, ECB EUR/PLN Q1 2026, FedEx PL remote-area + address-correction).
- On-disk Maersk PDF (`new-offer-rates-vassuis-en-pl.pdf`) failed to render via Read (pdftoppm missing in env). Will retry / route around.
- Both live FedEx en-pl HTML pages (surcharges.html, fedex-rates.html) returned access-denied error pages (incident-numbered). Pivoting to FedEx CDN PDFs found via search.
- Search surfaced load-bearing CDN PDFs: FedEx-International-Fuel-Surcharge-6-April.pdf, fedex-demand-surcharge-en-eu.pdf, new-offer-rates-export-en-pl.pdf. ECB: Webstat monthly endpoint + CEIC (Feb 4.224, Mar 4.289 partial).
- Next: fetch ECB monthly averages (authoritative), FedEx fuel PDF, demand PDF, export rate sheet.
- On-disk VASS PDF rendered fully on retry (Read native PDF path). It IS the FedEx PL schedule (PLEN-SLR-VASS, eff. 5 Jan 2026) — answers Target 3 outright: Extended Area Service (Tier A PLN 15/shp, B PLN 2.60/kg min 105, C PLN 3.35/kg min 135, postcode-list-driven) + Address Correction (INTL PLN 43.70/shp, DOM PLN 12/shp). Also confirms 3-index fuel split: International=jet fuel (covers IE), Regional=EU automotive gas oil (covers RE/REF), Domestic separate.
- FX (Target 2): Jan 4.2114, Feb 4.2186, Mar 4.2725, Q1 avg ~4.234, 2026 YTD 4.2398 — exchange-rates.org, cross-checked vs ECB daily graph. 4.30 placeholder is HIGH (~1.5% over actual).
- Fuel % (Target 1): every FedEx-published surface (en-pl surcharges/rates HTML, en-gb fuel, eu-europe Intl-fuel PDF) access-gated 2026-05-27; Wayback unfetchable. Only non-FedEx aggregate ~49.75% (UPS+FedEx, May, intl air) surfaced. Cadence confirmed: Regional=weekly (Mon-effective), International=step changes (6 Apr, 11 May effective). Per-month RE/IE % = documented GAP → carrier ask.
- Research file written: research/2026-05-27-fedex-fuel-fx-remotearea.md. 7-item STILL-A-GAP section (5 carrier asks + 2 verification steps). Run complete.
