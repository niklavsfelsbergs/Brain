# GLS old contract vs 2026 tender offer — why GLS stopped being cheap

As of: 2026-06-11 (S201). Source: `bi-analytics-main/NFE/projects/2_EU_tender_2026/1_offers/picanova/GLS/comparison/`
(scripts + findings.md + parquets). Old cards: `NFE/docs/shipping_contracts/0. OLD/EU/GLS/{2025,2026}/`
(contract line 276a45fi26); tender offer 276a159AiC (engine gls-2.0.0).

**Headline (same Q1-2026 tender parcels, 501,728):** 2025 terms €2.67M → tender €3.07M = **+14.9%**.
The tender bid is **+8.7% above GLS's own 2026 continuation conditions** — worse than staying would
have been. Bridge: +5.7% GLS annual uplift / +€97k base-card re-shape / +€148k heavier stack.

**Driver 1 — flat mid-weight card abolished.** Old card: one price 2–25 kg on core lanes (AT 4.11,
BE 3.95, DE 4.14 @15–25 kg). Tender: steep per-kg gradient (DE 25 kg +190%, AT 15 kg +119%); only
the 2 kg band got cheaper; EBP 1 kg entry band +18–32%. Bites because 95% of eligible EBP parcels
are dim-weighted (÷6000) — the canvas slice re-weights into exactly the re-priced bands.

**Driver 2 — heavier stack.** NEW 4.1% Dieselfloater (old contract had a single Energy index, no
separate floater); Klima 1%→2.5%; EFTA clearance 19.50→25.00; partially offset by energy discount
−2%→−4%. Net ≈ +4.8pp on every EBP base euro.

**Invoice ground truth (shipping-agent):** GLS volume ended 2025-07 (wind-down Aug); old book was
NL+AT 83% / DE 3%, ~1.4 kg light export at ~€4.5/parcel landed. Old-stack model validated: non-DE
stack÷base 28.8% actual vs 29.2% modelled; DE toll €0.380 exact. GLS's energy/klima/toll lands in
the mart's "Unclassified" bucket (charge-bucket-mapping gap if GLS analysis recurs).

**Rule:** when a formerly-cheap carrier looks uncompetitive in a new tender, diff the *card shape*
(band structure), not just levels — a flat-band card vs a graduated card flips ranking for a
dim-weighted mix without any single "price increase" line; and check the new bid against the
incumbent line's own continuation conditions (here the tender bid was above it).
