# S099 d1 — FedEx Poland curl fetch (dwarf run-log)

**Role:** dwarf (curl operative), inheriting Jebrim.
**Brief:** Use `curl` to fetch the FedEx Poland public pages the penguin's WebFetch couldn't reach (FedEx domain bot-gated). Extract the International fuel-surcharge %, PLN handling/area amounts, and peak/demand schedule — each with source URL, effective date, and the method that worked. Resolve the Maersk "49.50% published → 24.75% net" discrepancy.

---

## VERDICT (the 49.50% question)

**49.50% is NOT FedEx Poland's published *International* Fuel Surcharge, and it is not their Regional or Domestic FSC either.** Every FedEx PL fuel rate I could fetch (Regional, Domestic, Jan–Mar 2026) sits in the **18.5%–19.5%** range; the published *International* FSC (the USGC jet-fuel index, the one that actually governs a FedEx Economy *international* lane) reads ~**37–43%** per the penguin's trade-press sourcing. **Nothing FedEx PL publishes reaches 49.50%.** So:

- A flat "49.50% published, 50% discount → 24.75% net" is a **Maersk-internal commercial construction**, not a transcription of FedEx Poland's public schedule. The claim "surcharges follow FedEx Poland's public %" does **not** reconcile with 49.50% on the fuel line.
- 24.75% net is *coincidentally* near the published International export FSC at lower jet-fuel bands, but the arithmetic path (49.50% × 50%) is not the published-schedule path.
- **Action for Niklavs/Jebrim:** put back to Maersk — (a) name the exact FedEx service on the ROW lane (International Economy = USGC jet-fuel index, ~37–43%; vs **Regional Economy = EU-diesel index, ~18.5–19% — fetched below**), and (b) cite the specific FedEx PL table/row the 49.50% comes from. If it's Regional Economy, the governing public FSC is ~19%, not 49.5%.

This is **fetched-confirmed** for Regional/Domestic (wayback snapshots below) and **inferred** for International (its table is JS/API-rendered and WAF-blocked everywhere — see Unreachable).

---

## The bot-gate — what blocks what

`fedex.com` is behind a **WAF (Web Application Firewall)**, not a User-Agent filter. Every direct curl — HTML, DAM PDF, and guessed API endpoints alike — returns an **884-885 byte "FedEx | System Down / you don't have permission" failover stub** regardless of browser headers, locale, redirects, or compression. Confirmed against:
- `https://www.fedex.com/pl-pl/shipping/surcharges.html` — 200, 884 B stub
- `https://www.fedex.com/en-pl/shipping/surcharges.html` — 200, 884 B stub
- `https://www.fedex.com/content/dam/fedex/eu-europe/downloads/FedEx-International-Fuel-Surcharge-6-April.pdf` — 200, 885 B stub
- `https://www.fedex.com/content/dam/fedex/international/rates/fedex-demand-surcharge-en-eu.pdf` — 884 B stub
- `https://www.fedex.com/content/dam/fedex/international/rates/fedex-rates-vassuis-pl-pl.pdf` — 883 B stub
- `https://www.fedex.com/content/dam/fedex/international/rates/new-offer-rates-vassuis-en-pl.pdf` — 885 B stub
- 3 guessed dynamic-FSC API endpoints (`/api/…`, `/bin/fedex/…`, `…jcr:content.fuelsurcharge.json`) — all 885 B stubs.

**What worked: web.archive.org (Wayback).** The Wayback CDX API listed `200`-status snapshots of the surcharge pages; fetching the raw (`id_`) snapshot with browser headers returned real ~42 KB pages. (Wayback's `availability` API rate-limited at first with 429 — spacing requests 3 s apart fixed it.)

**Second structural blocker:** even inside the recovered Wayback HTML, the **fuel-surcharge rate tables are `apiType: Dynamic`** — rendered client-side from a WAF-gated AEM endpoint (`<script type="application/json" data-config="js-fuelsurcharge-config">{ "apiType":"Dynamic","serviceName":"express_weekly","region":"eu","importExportPercentageOption":"1" }`). The **International** and **IXF/ATA** tables therefore carry **no rate values in the static HTML at all** (headers `Effective date | USGC value | Surcharge` + a "Show all weeks" toggle, empty body). The **Regional** and **Domestic** tables, by contrast, embed their current dated rates statically — so those are fetched-confirmed.

---

## 1. Fuel surcharge

### Mechanism (fetched-confirmed, Wayback en-pl 2026-03-13 + pl-pl snapshots)
Source: `https://www.fedex.com/en-pl/shipping/surcharges.html` via `https://web.archive.org/web/20260313022952id_/...` (and pl-pl 20260116174627 / 20260218005055).

Four distinct fuel surcharges on the FedEx PL page, three relevant:
- **International FSC** — applies to **FedEx Express International export & import** transportation charges. Index: **USGC spot price for a gallon of kerosene-type jet fuel (EIA), weekly, 2-week lag.** **Explicitly does NOT apply to FedEx Regional Economy / Regional Economy Freight.** *(verbatim: "The international fuel surcharge does not apply to FedEx Regional Economy and FedEx Regional Economy Freight.")*
- **Regional FSC** — applies to **FedEx Regional Economy and Regional Economy Freight**. Index: **rounded average of EU Automotive Gas Oil (diesel) prices in EUR (European Commission DG MOVE), weekly, incl. duties/taxes.**
- **Domestic FSC (PL)** — applies to **FedEx Priority Overnight only**. Index: **PKN Orlen wholesale diesel**, PLN-based, monthly base.
- IXF/ATA FSC — International Express Freight / Airport-to-Airport, monthly USGC jet-fuel. (Not relevant to a parcel Economy lane.)

The fuel surcharge is applied to the net transport rate **plus** these transport-related surcharges (so fuel compounds on top of ODA/OPA, AHS, demand, etc.): Broker Select, Extended Area (ODA/OPA), Saturday Delivery, Additional Handling (Dimension/Packaging/Weight/Freight), Oversize, Non-Stackable, Delivery Signature, and Demand Surcharge.

### Published percentages — Q1 2026 (FETCHED, dated)

| Index | Rate | Effective window | Source snapshot |
|---|---|---|---|
| **Regional FSC** (FedEx Regional Economy — EU diesel) | **18.50%** | 12–18 Jan 2026 | pl-pl 2026-01-16 |
| **Regional FSC** | **18.50%** | 19–25 Jan 2026 | pl-pl 2026-01-16 |
| **Regional FSC** | **18.50%** | 2–8 Feb 2026 | pl-pl 2026-02-18 |
| **Regional FSC** | **19.00%** | 9–15 Feb 2026 | pl-pl 2026-02-18 |
| **Regional FSC** | **18.50%** | 2–8 Mar 2026 | en-pl 2026-03-13 |
| **Regional FSC** | **19.00%** | 9–15 Mar 2026 | en-pl 2026-03-13 |
| **Domestic PL FSC** (Priority Overnight — Orlen diesel) | **19.50%** | 1–31 Jan 2026 | pl-pl 2026-01-16 |
| **Domestic PL FSC** | **19.00%** | 1–28 Feb 2026 | pl-pl 2026-02-18 |
| **Domestic PL FSC** | **19.50%** | 1–31 Mar 2026 | en-pl 2026-03-13 |

- **International FSC % for Jan/Feb/Mar 2026: NOT FETCHED** — the table is dynamic/JS + WAF-gated, and has no static snapshot value on FedEx PL, the EU PDF, or TNT PL (TNT's table is JS-rendered too). The penguin's trade-press range stands as the best estimate: **~37–38.5% export / ~41–43% import** around $4/gal jet fuel in early-mid 2026 (Q1 ≈ 36.5% export at $4/gal, pre the +2pt structural step on 11 May 2026). **Inferred, not fetched.**

### Cadence change (fetched, TNT PL — `https://www.tnt.com/express/pl_pl/site/shipping-services/fuel-surcharges-europe.html`, 200, direct curl OK)
International FSC moves **monthly → weekly from 11 May 2026** (table published the preceding Friday); prior step-ups noted 7 Oct 2024, 9 Jun 2025, 6 Apr 2026. TNT is FedEx-group and uses the identical USGC jet-fuel index — corroborates the mechanism but **its rate table is also JS-rendered (no static values).**

### Plausibility of 49.50%
Not plausible as any FedEx PL *published* figure. Regional/Domestic are ~18.5–19.5% (fetched). International is ~37–43% (penguin-sourced). 49.50% exceeds even the import International band. See VERDICT.

---

## 2. PLN amounts — Additional Handling, ODA/OPA, oversize/overweight

**NOT FETCHED — unreachable.** The PLN values live in the FedEx PL **VASS** PDF (`fedex-rates-vassuis-pl-pl.pdf` / `new-offer-rates-vassuis-en-pl.pdf`) and the rates page (`fedex.com/pl/ratesinformation`):
- Both VASS PDFs return the 883–885 B WAF stub on direct curl.
- **No Wayback snapshots exist** for either VASS PDF (CDX returned empty for `*vassuis*` and `*/international/rates/*` PLN docs).
- The surcharges page itself carries **zero PLN tokens** and no amount tables — it only links out to the (blocked) rates pages.

What IS confirmed (fetched, from the surcharges page) is the **list of surcharge types** FedEx PL levies, which fuel compounds on: ODA/OPA (Extended Area), Additional Handling Surcharge — Dimension / Packaging / Weight / Freight, Oversize Charge, Non-Stackable Surcharge. The trigger thresholds (70 kg / 150 cm longest / 70 cm other edge / <180 cm sum-of-two; AHS-Weight >25 kg; vol weight ÷5000) were already captured by the penguin from Polish aggregators (apaczka/polkurier) and are unchanged — **definitions confirmed, PLN amounts gapped.**

---

## 3. Peak / Demand surcharge schedule

**NOT FETCHED — unreachable.** The intra-Europe Economy demand schedule lives in `fedex-demand-surcharge-en-eu.pdf`:
- Direct curl → 884 B WAF stub.
- **No Wayback snapshot** (CDX empty).
- The fuel-surcharge page mentions "Demand Surcharge (formerly Peak Surcharge)" only as a *fuel-base component*, not with its own values.

Best available remains the penguin's search-summary figures (unverified by me): intra-Europe Economy demand **€0.10 → €0.15/kg, 20 Oct–21 Dec 2025**, stepping to **€0.15 → €0.10/kg, 22 Dec 2025–15 Feb 2026** (Priority +€0.20/kg over Economy). FedEx PL also runs a PLN "dopłata okresowa" (weight-based, ~0.50–8.80 PLN/kg, min 4.40 PLN/shipment per a 2024 aggregator) — **indicative shape only, not fetched.**

---

## What worked per figure (method ledger)

| Figure | Method | Result |
|---|---|---|
| Regional FSC % Jan–Mar 2026 (dated) | Wayback `id_` snapshot of pl-pl + en-pl surcharges page | **Fetched** |
| Domestic PL FSC % Jan–Mar 2026 (dated) | same | **Fetched** |
| Fuel mechanism / index / cadence / which-service-which-index | Wayback snapshot (FedEx) + direct curl (TNT PL) | **Fetched** |
| International FSC % (the load-bearing one) | direct curl (WAF stub), Wayback (table is dynamic/empty), TNT (dynamic/empty), API guesses (WAF stub) | **Unreachable** — JS/API + WAF; inferred ~37–43% from penguin's trade press |
| PLN handling/ODA/OPA/oversize amounts | direct curl (WAF stub), Wayback CDX (no snapshot) | **Unreachable** — VASS PDF not archived |
| Peak/demand schedule + per-kg | direct curl (WAF stub), Wayback CDX (no snapshot) | **Unreachable** — demand PDF not archived |

## Still unreachable (and why)
1. **International FSC weekly %** — table is `apiType: Dynamic`, rendered from a WAF-gated AEM endpoint; no static value anywhere (FedEx PL, EU PDF, TNT all JS-render it). A human in a real browser on the FedEx PL surcharges page can read it off the rendered "International Fuel Surcharge" table in seconds. *This is the one figure that would definitively settle 49.50% vs published.*
2. **VASS PDF (PLN amounts)** — WAF-blocked on direct fetch, not in Wayback. Needs a human browser session, or a fresh-from-Maersk copy of the exact `new-offer-rates-vassuis-en-pl.pdf` they referenced.
3. **EU demand-surcharge PDF** — WAF-blocked, not in Wayback. Same remedy.

## Status: fetch complete within reachable surface. Regional + Domestic FSC fetched-confirmed with effective dates; International FSC structurally unreachable (resolved via inference + the verdict). PLN amounts and demand schedule remain behind the WAF with no Wayback fallback. Temp dumps in system temp (`/tmp/fedex-d1`), not written into the brain.
