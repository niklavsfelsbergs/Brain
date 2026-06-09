---
quest: S164_db-schenker-rerouting-validation
sid8: 79537cb3
ts: 2026-06-08 13:40
open_dep: awaiting Niklavs' carrier/floor answers (Maersk DE oversize ceiling; real GEL dims) — analysis side is shipped + committed
---

# Resume — DB Schenker re-routing contract validation

## Where we are
Deliverable shipped + committed to bi-analytics: `2_analysis/routing_2026q1/validation/db_schenker/DB_schenker_rerouting.html` (self-contained, contract-cited) + pipeline `build_population.py → validate.py → report.py`. Verified: all 7,593 parcels moved off DB Schenker → Hermes (4,746) + Maersk (2,847) are eligible under the assigned carrier. Hermes is contract-clean; Maersk's 1,291 extreme-oversize parcels (esp. DE GEL tubes 200 cm/560 girth) rest on an unstated per-country oversize ceiling. Report's Section D carries the three question sets (Maersk / Hermes / production floor). **Section E** (added this session) covers the mirror — what STAYS on DB Schenker: 1,076 = 165 must-freight + 240 not-in-6 (incl. all CH) + 671 price (97% FR+PL; FR slice = the FR-extend readout).

## Possible next (offered, not started)
Size the FR-extend flip: the 510 FR price-retained parcels, DB Schenker cost vs Maersk FR @ €4.72.

## Next concrete step (mostly Niklavs-gated)
1. **Niklavs** puts the three question sets to Maersk, Hermes, and the production floor (Section D of the report). The floor measurement of real GEL dimensions is the pivot — it either dissolves the Maersk oversize concern or makes Maersk's explicit acceptance mandatory.
2. When answers return: if real GEL dims are well under nominal 200 cm, the breach shrinks → update `validate.py` breach calc with measured dims and re-render. If Maersk confirms/denies a DE ceiling, encode it in the maersk engine eligibility (`oversize_no_surcharge` currently has no upper bound) and re-run the routing — a denied ceiling would shrink the €399,750 routing saving on the DB Schenker slice.
3. **Sibling validations**: the `validation/` folder is set up for more (Niklavs nested `db_schenker/` deliberately). Same pattern reusable — paths are depth-robust.

## Files / paths to read first (bi-analytics repo, NOT brain)
1. `bi-analytics-main/NFE/projects/2_EU_tender_2026/2_analysis/routing_2026q1/validation/db_schenker/DB_schenker_rerouting.html` — the deliverable.
2. `.../validation/db_schenker/{build_population,validate,report}.py` — the pipeline.
3. `.../carriers/maersk/calculate.py` `_decide_eligibility` + `rate_tables/eu_oversize.parquet` — the Maersk dim-gate (the no-upper-ceiling spot).
4. `.../carriers/hermes/calculate.py` + `constants.py` — Hermes 170 cm / 450 L gate.
5. `carrier_responses_to_open_questions/Maersk/REVIEW_CONCLUSIONS.md` — Q6/Q8 oversize confirmations.
6. This session's quest-log: `quest-log/in-progress/S164_79537cb3_db-schenker-rerouting-validation.md`.

## Commits
- bi-analytics (this close): `validation/db_schenker/` committed pathspec-scoped on the current branch, NOT pushed. (Derived parquets gitignored — commit code, regen data.)
- brain (this close): S164 quest-log + this resume + 1 bank draft + comms CLOSING, scoped to 79537cb3 pathspecs only.

## No pending external actions.
