---
quest: S283_60de5609_orwo-tender-assumptions-and-carrier-questions (continues S275/S281 ORWO arc)
sid8: 60de5609
ts: 2026-06-22 14:30
open_dep: GLS -EUR509k headline OMITS GLS energy/diesel (~25%) - NOT meeting-ready until re-run with the provisional surcharge stack; carrier-question dispatch awaiting send + carrier replies
---

# ORWO Tender 2026 - resume (rolls __926f247a; predecessor archived)

## >>> WHERE WE STAND (2026-06-22) - read this first

**The ORWO carrier tender modeling is built (4 carriers: UPS, DHL, GLS, Maersk) but the GLS headline is NOT meeting-ready.** The prior session's "GLS primary ~-EUR509k/yr, verdict SAFE" claim was OVERTURNED this session: the GLS engine omits GLS's own ~25% fuel/energy stack.

**The one-paragraph state.** GLS is still the most promising carrier, but the -EUR509k/yr figure is a **freight-base** comparison that leaves out GLS's Energy (20.5%) + Dieselfloater (4.1%) + ClimateProtect (2.5%) surcharges - which the EU-tender GLS engine modeled and the ORWO engine does not. Folding them in shrinks the saving substantially and could flip the -EUR238k DE-domestic driver (GLS ~25% surcharge stack vs DHL domestic ~7.5%). So before any stakeholder sees a number, the GLS (and Maersk) engines need their surcharge layers added and a re-run.

## NEXT CONCRETE STEP
1. **Lock the provisional surcharge assumptions** (`NFE/.../carrier_questions/_provisional_assumptions.md`) into `carrier_engines/gls/` (Energy 20.5% + Diesel 4.1% + Klima 2.5% on base, Toll Intl 5.70% on full net x-border, DE delivery-private 0.15, Season) and add the Maersk surcharge layer (EU fuel 6.6%, country tolls, Overpack 0.40). Re-run `switch_compare.py` both -> the **corrected working number**. This is the deliverable for the stakeholder meeting: "here's the saving once each carrier's own fuel is in, pending carrier confirmation."
2. **Send the carrier-question dispatch** - `NFE/.../carrier_questions/{GLS,Maersk}.md`. The two that decide the GLS verdict: **GLS A1 (current ORWO energy %) + A2 (dieselfloater %)**. Swap real values in when they reply (flip the question-file rows to RESOLVED).
3. Then: US/ROW-zone modeling, seasonal annualization (replace H1x2), confirm Maersk DE last-mile (B1) + GB clearance, present the corrected GLS recommendation.

## FILES TO READ FIRST
- `NFE/projects/7_ORWO_tender_2026/carrier_questions/_provisional_assumptions.md` - the compute-now values + the load-bearing flag.
- `NFE/projects/7_ORWO_tender_2026/carrier_questions/{GLS,Maersk}.md` - the dispatch (confirm-same-as-Picanova + ORWO-specific).
- `NFE/.../repricing_base/carrier_engines/COMPARISON.md` - the verdict doc, now carrying a PENDING-CORRECTION caveat.
- `NFE/.../repricing_base/carrier_engines/gls/{constants.py,switch_compare.py}` - where the surcharge stack must be added.
- Per-carrier assumption detail: `players/jebrim/quest-log/traces/dwarf_orwo-{ups,dhl,gls,maersk}-*.md` (5 traces).

## KEY FINDINGS THIS SESSION
- **Dims/oversize is a non-issue.** ORWO packaging catalog tops out at 120cm/135L - trips NO GLS oversize surcharge (1 type id-27 hits an 80cm mid-dim reject). The "reprice the bulky tail at volumetric weight" deferred item is **DROPPED as immaterial** (supersedes the prior MONDAY HANDOVER's "TOP deferred" item).
- **DHL Sperrgut (EUR307k) = TOO THIN / non-conveyable, not oversize** (Niklavs). The GLS analog is Non-conveyable EUR0.80/parcel (on the ORWO card), ~18x cheaper than DHL's ~EUR14. **DECISION (Niklavs): IGNORE non-conveyable** going forward (one-off DHL situation) - logged as assumption.
- **Per-carrier assumption state:** UPS saving EUR34-50k/yr is GRI-avoided on a placeholder 5% GRI; DHL offer reprices FLAT -> saving = EUR0 without the real GRI%; GLS overstated (energy omitted); Maersk has NO invoiced baseline (everything modeled, ungated).
- **GLS oversize thresholds (120/150/300) provenance:** GLS GTC SS4.2 + Picanova Q12/Q14 answers, NOT the ORWO contract - a flagged assumption (Section A8/A2 of the GLS dispatch confirms it for ORWO).

## DECISIONS LOG (this session)
- Ignore non-conveyable / DHL Sperrgut going forward.
- Carrier-question approach = EU-tender playbook; confirm-same-as-Picanova where already answered.
- Provisional assumptions adopted for the interim calc (see `_provisional_assumptions.md`).

## STILL OPEN (carried)
- The uninvoiced-carrier coverage gap (~600k Wolfen shipments / ~22% via 0%-invoice carriers: Deutsche Post, Bring, Cirro, PostNL...) - see sibling resume `orwo-tender-resume__cb17c25e.md`; Niklavs to decide cost basis. Fold into this resume's OPEN list at a clean session.
- Create the `orwo-tender` bank digest at next Jebrim alching (route mart-weight-grain -> shipping-mart, rate cards -> carrier-contracts).

## ANCHORS
NFE `projects/7_ORWO_tender_2026/` (carrier_engines/ + carrier_questions/ + offers/). Quest [[S283_60de5609_orwo-tender-assumptions-and-carrier-questions]]; prior [[S281_926f247a_orwo-carrier-engines-refactor-gls-maersk]]; umbrella [[S275_abfcf511_orwo-tender-contracts-coverage-weight-grain]].
