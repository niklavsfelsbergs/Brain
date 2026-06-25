# S369 -- UK Maersk: revenue-loss-for-100% reframe (locked)

**sid8:** 997395cd | **player:** Jebrim | **date:** 2026-06-25
**Continues:** [[S277_47bed7aa_uk-yodel-negotiation-levers]] (the 3 rate asks + structural option).
**Deliverable home:** EXTERNAL `bi-analytics-main/NFE/.../3_UK/2_analysis/yodel_negotiation_levers.md`
(new LOCKED section + re-sized options).

## Ask
Maersk declined the 4 concession options (3 rate asks + the structural Medium/Large tier-threshold
extension) and flipped the question: **how much revenue must THEY lose annually for us to give them
100% of UK volume.** "We already calculated this -- get the number." Confirm understanding, then deliver.

## What happened (turn arc)

1. Anchored to [[S277_47bed7aa_uk-yodel-negotiation-levers|S277]]; pulled the authoritative figures from the committed engine result
   (`yodel_cost_engine_result.md`, S282-validated three-way) + `uk_truck_linehaul_cost.md`.
2. **Truck-isolation caveat (principal):** Maersk doesn't care about truck -- we pay it -- so the
   concession must be a pure parcel number. Worked the ex-truck framing.
3. **My error, principal caught it:** I first quoted ~GBP 297K/yr (ex-truck parcel gap, 349,948 -
   288,058 = 61,891/Q). That DOUBLE-removed the truck: it stripped truck from Maersk's side AND denied
   us the truck saving on our own 0%-neutrality calc. Wrong -- the truck saving is real, ours, and
   legitimately reduces what Maersk must concede.
4. **Corrected:** Maersk's loss for us to hit 0% total = the parcel cut that, *with* the truck saving,
   lands our total flat = the GBP 45,251/Q figure -- NOT 61,891. All 3 options already carve exactly
   this; they differ only in WHERE (base/Large/OOG), not how much.
5. **Go-forward truck correction (principal):** today's truck is GBP 3,620 (3,700->3,620 already
   happened May 2026), not 3,700. Move takes 3,620->3,350 = 270/truck (not 350). Smaller truck saving
   -> Maersk concession rises 45,251 -> **49,054/Q** (~47.5 mainland trucks x 80/truck = +3,803/Q).
6. **LOCKED at GBP 235K/year** (49,054/Q x4.8). Built the final view: Maersk revenue (parcel + truck
   component) and our total-cost (do-nothing vs after-cut) tables, both tying to 0% / GBP 2.21M/yr.
7. Re-sized the 3 options to 49,054/Q (exact linear scaling -- rate cuts don't reclassify tiers):
   base -16.4% (1.66/2.00/3.09); Large -26.2% (->2.73); OOG -97.7% (near-maxed, weakest route).

## Decisions
- **LOCKED: Maersk revenue loss = GBP 49,054/Q = ~GBP 235K/yr** for 100% UK mainland at 0% cost increase.
- **Go-forward baseline (truck @3,620), not the 3,700 Q1-as-billed** -- this is the honest basis.
- Truck saving (consolidation-driven, ours) stays OUT of Maersk's concession; their loss is pure parcel.
- 3 options re-sized to the 49,054/Q target; structural option = the 4th (deprioritized, on the shelf).

## Data-discipline catches this session
- **Isolating a cost component from a counterparty's concession != removing its benefit from our own
  neutrality calc.** Truck stays out of Maersk's ask AND its saving still counts toward our 0%. Removing
  it from both sides inflated the ask by ~80K/yr. (Examine draft written.)
- Annualize via the EU-tender x4.8 seasonal profile, NOT a naive x4 (would understate the figures).

## Pending external actions
None pending. (Analysis + doc update only; no sends, no commits beyond the close commit.)

## Cascade
- NFE: `3_UK/2_analysis/yodel_negotiation_levers.md` -- new LOCKED section + re-sized options
  (committed in the NFE repo, standing auth, pathspec-scoped, never push).

## Main-brain changes
- This quest-log entry + `inventory/uk-yodel-negotiation-levers-resume__997395cd.md`.
- Examine draft: `2026-06-25-isolate-component-from-concession-not-from-our-neutrality.md`.
- Comms: jebrim-997395cd OPEN + CLOSING (posted late, at the require-open gate).
