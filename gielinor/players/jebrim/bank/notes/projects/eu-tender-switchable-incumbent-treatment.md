# EU tender — switchable-incumbent treatment

**Source:** `bi-analytics-main/NFE/projects/2_EU_tender_2026/2_analysis/docs/technical/03-scorer.md` + `_decision_sets.py`. Anchor [[S122_330dea7d_eu-tender-switchable-incumbent-open-qs|S122]]. Parent note [[eu_tender_2026]].

## The concept

A **switchable incumbent** = a carrier we ship with today *and* that submitted a 2026 offer with a working rate engine. As of 2026-05-29: **DHL Paket, Maersk, DPD PL**. (UPS = incumbent, offer pending. New entrants — DHL Express, GLS, Güll, Austrian Post, Hermes, FedEx — have no incumbent book.)

Each switchable takes one of three mutually-exclusive states per decision set: `INCUMBENT | NEW_OFFER | OFF` (signing the new contract replaces the old book, so a carrier never bids both ways in one scenario).

## The one rule (uniform across all three)

The INCUMBENT bid is the **2026 engine price wherever the engine can price the parcel, and the 2025 invoice only as a fallback where it can't.** Same mechanic for DHL Paket, Maersk, DPD PL — not a different story per carrier. No-engine incumbents (UPS, DB Schenker) keep the flat 2025 invoice.

Consequence: the do-nothing **baseline is itself a 2026 engine computation**, not the 2025 invoice. baseline_2026 €14.85M vs invoice_today €14.27M = **+€581k (2026 cards dearer for the same volume)**.

## What it surfaced (2026-05-29 / full-year)

- **DHL Paket** — pure rate increase, new card live since 03.01. Not a decision lever; fixed cost in every scenario (engine over-prices the book ~+2.9% → kept as incumbent anchor, never a renewal win).
- **DPD PL** — new offer over-prices its own current parcels: `renew_dpd_pl` standalone **−€417k full-year**. Signal: if DPD PL stays, keep it at the current invoice — *unless* the current contract expires (then it collapses to `{NEW_OFFER, OFF}`: sign the dearer card or drop).
- **Maersk** — new card covers a **narrower country set** than what we run today. EU card = 25 countries; ROW = ~150 via FedEx Economy. **GB, FR, SE, FI, IE are on neither** → `country_not_served`. Of the Phase-1 "already-Maersk" lanes (FR/GB/SE/DK/FI), only **DK** is actually on the 2026 card. On-card lanes (~88%, DE the bulk) re-price to the new offer; the off-card tail falls back to 2025 invoice in the baseline and **strands on renewal** (must pair Maersk with a broad-coverage carrier — Hermes/GLS).
