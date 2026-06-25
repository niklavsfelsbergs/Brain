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

## Red-team audit (S282 / sid 9d9e0b14, 2026-06-19) -- the 3 options STAND
Independent re-derivation off the live mart (5 shipping-agent pulls + 1 penguin fuel re-quote). Every committed
figure reconciles within live-mart rounding drift. Verdict: **safe to stand behind the 3 options.** Confirmed:
- Basis clean: existing GBP 288,058 = **RAW INVOICED ACTUAL** mainland ex-truck parcel (re-derived 288,061),
  NOT a reprice. `_eur`/1.1515, truck baked in (row-verified), `_local` mixed-currency corruption proven (1.9x).
- Mainland 93,480 / offshore 4,792 exact; tier mix + base + OOG (15x2,050 + 50x389) reconcile to 349,948.
- Fuel 18% still current (penguin web re-quote), trend DOWN from 19% -> not widening.
- Lever arithmetic: all 3 land within +-GBP 80 of 0.0% vs the Q1-as-billed baseline.

## Open actions from the red-team (carry forward)
1. **PHYSICAL CHECK (principal's instruction).** The Medium cap-miss rests on **declared** dims. The 1,679-parcel
   pool is the `60x40 Box-in-the-Box` (canvas 60x40), declared **66.1 x 42.1 x 8.5cm** -- width 42.1 busts Yodel's
   41cm Medium mid-cap by 1cm. **Measure/verify the real box + wrap-up in real life** before acting: if the true
   width is <=41 there is no miss; the cap-nudge/re-spec question is moot. Declared dims drive the whole tier classification.
   Example PCS orders to pull: D41354111 / D41346792 / D41374937 (all 66.1x42.1x8.5, currently ship DPD UK).
2. **COMMS exposure (UNRESOLVED).** Confirm what was actually put to Maersk on the **70cm** ask. 70cm ALONE closes
   only ~65% of the gap (~GBP 29.7k of 45.3k) -> ~+3.4% vs today; it was NEVER modeled as a standalone close.
   Parity needs the PAIR (70cm Medium + Large 120->170cm killing the GBP 15 band) or a rate trim. If 70cm was
   communicated as reaching parity, ~GBP 15.6k/Q to walk back or backfill.
3. **GO-FORWARD TRUCK reframe.** Three-way credits the move with the full GBP 3,700->3,350 truck cut, but
   3,700->3,620 already happened (May 2026); go-forward stay = 3,620. Honest go-forward gap is ~GBP 3.8k bigger
   (~49.1k / +10.7%), so each option lands ~+0.8% not 0%. To true up: base -16.4% / Large -26% / OOG -98%.
   Also: "47.5 trucks" is an allocation artifact (60 physical Q1 loads); per-truck rate currency (EUR vs GBP 3,700)
   is ambiguous in the mart -- confirm before any deck quotes a per-truck figure (gap itself is robust to it).
4. **Optional top-up.** 1cm Medium mid-cap nudge (41->43, any >=42.1) captures the 1,743 -> +GBP 2.5k/Q.
   Don't re-spec the flagship 60x40 canvas box for ~GBP 10k/yr; only fold the nudge into the ask if structural is the route.
