---
quest: S283_60de5609_orwo-tender-assumptions-and-carrier-questions (continues S275/S281 ORWO arc; this increment worked under session ca27d9be)
sid8: 60de5609
ts: 2026-06-22 16:10
open_dep: surcharge re-run DONE -> GLS/Maersk verdict REVERSED (primary switch dead on full-cost; real saving ~-EUR265k/yr lane-specific). COMPARISON.md rewritten. Dispatch send-ready, awaiting Niklavs to SEND + carrier replies. Provisional surcharges still unconfirmed.
---

# ORWO Tender 2026 - resume

## >>> WHERE WE STAND (2026-06-22, 16:10) - read this first

**The surcharge re-run is DONE and it REVERSED the verdict.** Folding each carrier's own
surcharge stack into GLS/Maersk AND leveling the incumbent's ACTUAL invoiced surcharges into
"current" (full-cost both sides) kills the -EUR509k/yr GLS saving. On full-cost:

- **All-GLS single switch: +EUR792k/yr WORSE.** All-Maersk: +EUR777k/yr WORSE.
- **DE-domestic core (548k parcels) is the driver:** GLS lands ~+43% (27% stack + ~EUR0.53/parcel
  flat tolls) vs DHL's ACTUAL invoiced ~5.4%. GLS loses DE-domestic **even at 0% energy**
  (+EUR92k H1 / +EUR185k/yr) - so GLS A1 (energy) sizes the loss but CANNOT flip the domestic core.
- **Real saving = lane-specific, ~-EUR265k/yr** (per-lane whole-lane full-cost optimum): keep DHL
  on DE domestic, move **GB -> Maersk (-EUR177k/yr)**, **AT -> GLS (-EUR56k/yr)**, **CH -> GLS
  (-EUR18k/yr)**, small EU tails. NOT a primary switch.
- The -EUR741k/yr freight-only per-lane optimum and -EUR509k/yr primary are both DEAD (freight-base).

**Load-bearing caveat:** GLS/Maersk surcharges are MODELED at Picanova-default (provisional) rates;
DHL/UPS are ACTUAL invoiced (trust-gated). The reversal is conditional on the provisional % - the
dispatch confirms them. But the 0%-energy check shows it'd take negotiating the WHOLE GLS stack
(klima+diesel+toll+private) down, not just fuel, to bring GLS-primary back.

## DONE THIS SESSION (sid ca27d9be)
1. **GLS engine** (`carrier_engines/gls/{constants,calculate}.py`): added the surcharge stack -
   Energy 20.5% + Klima 2.5% + Season(blended 0.417%) on base, Toll Intl 5.70% x-border / 0.38
   national flat domestic, Dieselfloater 4.1% after toll, DE delivery-private 0.15. Emits
   `gls_full_eur` / `gls_surcharge_eur`.
2. **Maersk engine** (`maersk/{constants,calculate}.py`): EU fuel 6.6% on base + country tolls
   (AT 0.29/DE 0.19/DK 0.05) + Overpack 0.40/parcel. Emits `maersk_full_eur`.
3. **Both `switch_compare.py`**: load_book carries incumbent surcharge (UPS fuel+resi; DHL surcharge
   ex Sperrgut), builds `current_full`; prints freight-only AND full-cost. Re-ran both.
4. **New `carrier_engines/per_lane_optimum.py`**: whole-lane cheapest-carrier synthesis -> -EUR265k/yr.
5. **COMPARISON.md REWRITTEN** to the corrected full-cost verdict (pending banner -> CORRECTED note;
   restructured headline + lane table; primary-switch-dead reading).

## NEXT CONCRETE STEP
1. **Niklavs to SEND the dispatch** - `carrier_questions/{GLS,Maersk}.md` (send-ready, unchanged this
   session; outward action, no channel wired here). The whole GLS stack now decides viability, not
   just A1/A2. Flip rows to RESOLVED as replies land; swap real % into the engine constants + re-run.
2. **Get each incumbent's real ORWO GRI%** (UPS/DHL) - the only incumbent-offer value is GRI-avoided,
   currently on a placeholder 5%.
3. Then: US/ROW-zone modeling, seasonal annualization (replace H1x2 + blended Season/BlackWeek with
   real monthly), confirm Maersk DE last-mile (B1) + GB clearance (B3) - GB-Maersk -EUR177k/yr leans
   on clearance folded into the Evri/Yodel door rate (assumption B3, Low-Med).

## FILES (corrected state)
- `repricing_base/carrier_engines/COMPARISON.md` - the corrected verdict doc (full-cost).
- `repricing_base/carrier_engines/{gls,maersk}/{constants,calculate,switch_compare}.py` - engines w/ stack.
- `repricing_base/carrier_engines/per_lane_optimum.py` - the -EUR265k/yr synthesis.
- `carrier_questions/{GLS,Maersk}.md` + `_provisional_assumptions.md` - dispatch + the locked provisionals.

## KEY NUMBERS (full-cost, H1; x2 ~ annual)
- Current full-cost all lanes: EUR 2.452M H1.
- GLS non-GB +EUR428k H1 (+EUR857k/yr); GB IC18 -EUR65k/yr. Maersk non-GB +EUR485k H1 (+EUR969k/yr); GB -EUR192k/yr.
- DE-domestic: GLS +EUR441k H1 (+22.5%); at 0% energy still +EUR92k H1.
- Per-lane optimum saving: -EUR132k H1 / -EUR265k/yr (GB Maersk + AT/CH GLS + tails).

## DECISIONS LOG (carried)
- Full-cost BOTH sides is the headline basis (Niklavs confirmed 2026-06-22) - freight-only and
  GLS-side-only both mislead (opposite directions).
- Ignore non-conveyable / DHL Sperrgut going forward (EUR307k excluded from current).
- Provisional assumptions adopted for the interim calc (see `_provisional_assumptions.md`).

## STILL OPEN (carried)
- The uninvoiced-carrier coverage gap (~600k Wolfen shipments / ~22% via 0%-invoice carriers:
  Deutsche Post, Bring, Cirro, PostNL...) - sibling resume `orwo-tender-resume__cb17c25e.md`;
  Niklavs to decide cost basis.
- Create the `orwo-tender` bank digest at next Jebrim alching (mart-weight-grain -> shipping-mart,
  rate cards -> carrier-contracts; add the full-cost-both-sides reversal as a method note).

## ANCHORS
NFE `projects/7_ORWO_tender_2026/`. Quest [[S283_60de5609_orwo-tender-assumptions-and-carrier-questions]];
prior [[S281_926f247a_orwo-carrier-engines-refactor-gls-maersk]]; umbrella
[[S275_abfcf511_orwo-tender-contracts-coverage-weight-grain]]. MEMORY: competitor-reprice-carries-own-surcharges.
