---
quest: S277_uk-yodel-negotiation-levers
sid8: 47bed7aa
ts: 2026-06-19 00:00
open_dep: none (analysis + docs shipped; ask sheet for Maersk not yet drafted -- optional next step)
---

# Resume -- UK Yodel (Maersk) negotiation levers (S277)

## Status
in-progress (analysis delivered + docs written; the Maersk-facing ask sheet is an optional next step).

## Where we are
Locked: **Q1 mainland baseline.** All-Yodel = +9.8% / +GBP 45,251/Q. Three rate asks, Maersk picks one,
each -> ~0%: (1) base -15.1% across; (2) Large-tier base -24.1% (GBP 3.69->2.80); (3) OOG -90%.
Offshore checked + parked (neutral vs today; the DPD/UPS offshore blowout is an ops fix, not a tender input).
Mar-May rebase rejected -- mainland cost is flat; the March "rise" was offshore-only.

## Next concrete step
Optional: draft the **three-option rate ask sheet for Maersk** (clean copy to send) at the whole-book or
mainland numbers. Otherwise the analysis is complete. If chasing offshore later: size the
offshore->Maersk move (~1,400 Apr-May offshore DPD/UPS parcels at EUR 21-26 -> Maersk EUR 8).

## Files / paths to read first
- `bi-analytics-main/NFE/projects/2_EU_tender_2026/3_UK/2_analysis/yodel_negotiation_levers.md` (THE deliverable)
- `3_UK/2_analysis/yodel_cost_engine_result.md` (the three-way + engine headline)
- `3_UK/2_analysis/yodel_engine/` (constants + calculate)
- quest-log `S277_47bed7aa_uk-yodel-negotiation-levers.md` (turn arc + the lever-sizing maths)

## Reproduce notes
- Live mart via Redshift MCP, gold shipping_mart, restricted 30s -> keep queries lean (bucketed, prefilter
  offshore postcodes with `LEFT(zip,2) IN (...)`; cast district to BIGINT -- a malformed zip overflows INT).
- Cost basis: `real_shipping_cost_eur` /1.1515 (NOT `_local`, mixed currency). Truck baked into `_eur`.
