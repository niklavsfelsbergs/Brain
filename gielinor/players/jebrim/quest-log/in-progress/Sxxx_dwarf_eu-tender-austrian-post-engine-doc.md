# Dwarf trace — Austrian Post engine doc + audit (EU Tender 2026, document-as-audit)

**Role:** dwarf for Jebrim. **Task:** write `2_analysis/docs/technical/engines/austrian_post.md` per the technical README template; audit AP constants vs REVIEW_CONCLUSIONS/FUEL_SUMMARY/ASSUMPTIONS as a byproduct.

## Read
- `carriers/austrian_post/` — calculate.py, constants.py, CLAUDE.md, all 6 surcharges, tests/ (test_engine.py + fixtures.py, 19 fixtures), __init__ (ALL/BASE).
- `carriers/_base/` — supplement.py (add_sorted_dims, add_chargeable_weight), pipeline.py (apply_surcharges + eligible-gate, lookup_rate_asof forward-asof, stamp_version), surcharge.py (Surcharge ABC).
- `carrier_responses_to_open_questions/Austrian Post/REVIEW_CONCLUSIONS.md` (12 Qs), `FUEL_SUMMARY.md` (AP AT/CH/trucking rows).
- `docs/ASSUMPTIONS.md` AP block (lines 409–442) + cross-carrier AT fuel-scope row (52–53).

## Engine snapshot
- Version `austrian_post-2.0.0` (S114 rebuild). Services: `paket_at_hd` (AT), `paket_ch_hd` (CH+LI). HD only, gross weight only, max 30 kg.
- Phase order: supplement → attach rates (forward-asof on weight_kg) → eligibility → `_apply_ch_fx` → apply_surcharges(BASE) → `_apply_fuel` → finalize → stamp.
- Surcharges: MAUT_AT 0.29 (AT), SPERRGUT_AT 7.80 (AT, d_max>100 & L+girth<=360), DIESEL_CH 0.05 (CH), CUSTOMS_CH 1.00 (CH, regardless ZAZ), LINE_HAUL ~0.83 (all eligible, flagged), PEAK 0 (placeholder). All BASE phase, none DEPENDENT.
- Fuel: AT base×4% (D5 Q1 point est); CH=0 (diesel is fixed-EUR surcharge).

## Audit findings (detail; consolidated in final report)
1. **FX uplift band: source prose vs engine reconcile but cite different top.** REVIEW_CONCLUSIONS Q3 + ASSUMPTIONS say "+1.1% to +3.7%" citing ECB Jan 1.0784 / Feb 1.0940 / **Mar 1.0996**. Engine applies **prior-month lag** (Jan→Dec 1.0716 = ×1.0109, Feb→Jan 1.0784 = ×1.0174, Mar→Feb 1.0940 = ×1.0321). So the engine's actual Q1 band is **+1.1% to +3.2%**; Mar 1.0996 is never billed (Mar orders use Feb's avg). Not a code bug — the source prose conflates "ECB month-average series" with "what gets billed under the 1-month lag." Doc/source drift worth a footnote. CH_FX_MULT_BY_MONTH itself is correct per the stated lag mechanism.
2. **LINE_HAUL fires on CH rows too but is NOT FX-rescaled** — correct by design (German-origin trucking, EUR-fixed) and matches the docstring; flagging only because it's easy to misread as a CH-tariff component.
3. **Pallet density 150 = largest flagged assumption.** Sensitivity ~€20–82k Q1; revisit trigger = "before signing IF AP makes final shortlist" (ASSUMPTIONS line 422). Documented, not a bug.
4. **Import VAT 8% not refunded** — flagged in constants + REVIEW_CONCLUSIONS, NOT modelled, and carries **no explicit revisit trigger** in code (only "confirm cost treatment"). Surfacing as the softest of the flagged items.
5. **Maut early-Q1 0.27→0.29** — 0.29 flat applied; ~0.02€/parcel early-Q1 overstate, flagged, transition date unconfirmed. Known.
6. **AT diesel 4% + DSV trucking diesel 4%** — both Q1 point estimates; AP's own D-card not public, DSV exact Q1 % PDF-gated. 12% = Iran sensitivity, not Q1. Known/flagged.
7. **No peak (structural edge)** — PEAK pinned 0, confirmed by carrier (Q5 "No"). Invisible in Q1 but a genuine advantage in the Q4-heavy full-year view; engine has no peak machinery at all. Correct + noteworthy.
8. Constants↔REVIEW_CONCLUSIONS otherwise reconcile exactly (Maut 0.29, Sperrgut 7.80/>100cm, diesel 0.05, customs 1.00/regardless-ZAZ, gross-only, 21–29kg round-up, off-limit=0).

## Wrote
- `2_analysis/docs/technical/engines/austrian_post.md` (one file; created engines/ subdir — first engine doc in the set).

## Boundary
Read-only on engine code; did not run code, did not commit, touched no other carrier.
