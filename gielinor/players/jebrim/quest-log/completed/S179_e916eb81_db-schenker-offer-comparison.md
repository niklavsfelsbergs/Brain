# S179 — DB Schenker 2026 offer vs 2025 prior offer: locate + re-price on actuals

**Player:** Jebrim · **Session:** e916eb81 · **Date:** 2026-06-09 · **Status:** complete

## Ask
Niklavs: we signed a new DB Schenker offer (~Jan 2026); find the *previous* offer and compare them.

## What happened
1. **Located both offers.** New = `docs/shipping_contracts/1. EU/1. PICANOVA/DB Schenker/DB Schenker Rate Card 2026.xlsx` (framework `WW-WWTWI-300005580866642`, accept-by 06.02.2026). Prior offer was NOT in the old `5_shipping_savings/contracts/` path; Niklavs pointed to a **new source-of-truth tree** `NFE/docs/shipping_contracts/` (`0. OLD/` for superseded). Prior = `0. OLD/EU/DB SCHENKER POLAND XXL PARCEL AND PALLER/cennik 2025/2025-02-27_Picanova GMBH_Oferta.xlsx` (framework `…300005296446370`). Recorded the source-of-truth change in the contract-overview bank note (a sibling session promoted it to `bank/notes/projects/` mid-session; my edit survived).
2. **Parameter diff.** Base-rate grid moved a **uniform +1.18%** (83,910 cells, stdev 0.00). Real changes: conversion factor 333→250 kg/m³ (favourable), MAUT 0.039→0.0645 (worse), two NEW 2026-only fees — **Sustainability €1 flat** + ETS (tiny).
3. **Re-priced on actuals.** Pulled 33,718 DB Schenker shipments (Jun'25–May'26) via a spawned shipping-agent → `actuals_population.parquet`. Built a 2025 rate table from the old `Cennik` sheet; re-priced the whole book under both cards with the **full additive calculator stack** (base + BAF + MAUT + CAF + MP + HOME fee + Sustainability + ETS), each card with its own conversion factor, floaters held constant.

## Result (decision-relevant)
- **Net: +€16,990/yr (+1.09%) — the 2026 card is marginally MORE expensive.** (First pass said −0.7% favourable — **wrong**, because it omitted the additive surcharge stack + new fees. See harvest.)
- Decomposition: conversion-factor cut saves ~€28k base, MAUT hike costs ~€21k, the **new €33k Sustainability fee** is the decisive swing → net unfavourable by ~€15–17k on a €1.85M lane. Roughly cost-neutral; not a red flag.
- **Validation:** full-stack model reconciles to actual invoiced with a **stable −15.8% gap in BOTH card-periods** (cheapest-zone fallback, symmetric → delta trustworthy; absolute ~16% low).

## Decisions in-flight
- Held BAF/CAF constant across both cards (external floaters, not card terms) to isolate the negotiated change.
- Used the country-MIN (cheapest-Strefa) zone fallback both ways — no PL postcode→zone map exists; symmetric so it cancels in the delta.

## Deliverables (work repo, bi-analytics-main — uncommitted there)
- `NFE/projects/5_shipping_savings/analysis/db_schenker_2025_vs_2026/` — FINDINGS.md, rates_2025.{csv,parquet}, actuals_population.parquet, repriced_full.parquet, SQL.

## No pending external actions.

## Optional follow-ups (NOT pending; offered, not taken)
- Harden to penny-exact via a PL postcode→Strefa map (delta won't move materially).
- Harvest a project bank note at next Jebrim alching.

## Child trace
- `S179_e916eb81_sa_db-schenker-actuals-population.md` (shipping-agent — the mart pull).
