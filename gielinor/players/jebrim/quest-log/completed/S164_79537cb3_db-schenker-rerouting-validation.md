# S164 · 79537cb3 — EU Tender 2026: DB Schenker re-routing contract validation

> Sub-quest of the S150 EU-tender final-setups work. Niklavs wanted to verify, down to the carrier contracts, that the ~7.6k parcels the final routing moves OFF DB Schenker onto the two NEW offers (Hermes + Maersk EU) can genuinely be carried there. Deliverable lives in the bi-analytics repo: `2_analysis/routing_2026q1/validation/db_schenker/`. Resume state in `inventory/db-schenker-rerouting-validation-resume__79537cb3.md`.

## What this session did

Opened as a discussion ("talk about the EU tender again… the routing report"). Niklavs scoped it across three turns: not the whole routing — specifically **what we move away from DB Schenker** (small volume but expensive, so the move is welcome), and **where in the contracts that move is verifiable**. Then named the deliverable: a self-contained `validation/DB_schenker_rerouting.html` (he later moved it to `validation/db_schenker/`, anticipating sibling validations), Hermes + Maersk only, traced to the contract.

**Grounding (no mart-from-memory).** Read the routing pipeline (`build_final.py`, `derive_envelope.py`, `routing_stats.json`), the eligibility architecture (`capability.py` pure-rules + per-carrier `carriers/<c>/calculate.py` engines), the `_decision_sets_2026q1.py` incumbent mapping (DB Schenker = `shipping_provider_group == "DB SCHENKER"`), and the actual contract docs (Hermes offer T&C slide + Country Details; Maersk rate card xlsx Surcharges sheet + `REVIEW_CONCLUSIONS.md`).

**Pipeline built** (`validation/db_schenker/`): `build_population.py` → `validate.py` → `report.py`.
- Population: DB Schenker carried **8,951** parcels in 2026-Q1; routing moves **7,593** to the new offers (**4,746 Hermes + 2,847 Maersk**) — reconciles exactly with `routing_stats.json` migration table.
- Validation: **100% (7,593) eligible** under the assigned carrier (cost-matrix ground truth). Headroom + breach severity computed per parcel.

## Findings

- **Hermes (4,746) — contract-clean.** Offer T&C slide (page 8 of the PDF) states DE max = 31.5 kg / 450 l / 2 m; engine caps length at **170 cm** (Country Details p2, Q4 reply) — *stricter* than the offer's 200 cm. All parcels ≤29 kg / ≤170 cm. 3,681 (78%) ride the 120–170 cm bulky band with surcharge. Intl dims are a documented DE proxy (Q4 open) — only 293 parcels.
- **Maersk (2,847) — mechanism confirmed, 1,291 need carrier sign-off.** Eligibility from the rate card "Oversized Surcharge" table (Surcharges sheet rows 47–78). Q6 (REVIEW_CONCLUSIONS) confirmed the *cumulative* "one breach = oversize" reading; Q8 confirmed IT/CH hard rejects. **But the rate card states no UPPER ceiling for surcharge countries**, and the engine applies none — so **1,291 parcels breach their country's standard dim threshold by >1.5× (up to 2.0×)**, overwhelmingly DE GEL "tube" parcels at nominal **200 cm / 560 cm L+girth** (DE standard girth 360, surcharge €21). Modeled eligible only because DE carries a surcharge value.
- **Dims are nominal per packagetype**, not measured (GEL = 200/560; zugeschnittene Verpackung = 130; CUSTOM_OVERSIZED ≤200). So the breach rests on nominal envelopes — a production-floor measurement of real GEL parcels is the pivot that de-risks (or confirms) the Maersk question.
- **Economics added** (2nd request): per-packagetype avg selected-carrier cost vs DB Schenker invoice. Savings are real and large — GEL→Maersk €26.89 vs €73.09 (€46/parcel); CUSTOM_OVERSIZED→Hermes €10.43 vs €40.07 (€30/parcel). The biggest per-parcel win (GEL) is the same cluster under the oversize-ceiling cloud.

## Decisions / outputs (principal)
- Scope locked to Hermes + Maersk, traced to the actual contract documents (not just the engine transcription).
- Report expanded twice on principal request: (1) per-packagetype fit (max dims/weight) + cost comparison; (2) an "Open questions" Section D with the three question sets — **for Maersk** (DE oversize ceiling, general per-country max, flat-vs-banded, 30 kg confirm), **for Hermes** (intl dims, 170 cm ceiling + bulky band/surcharges), **for the production floor** (real GEL/CUSTOM_OVERSIZED dims + shape, PALLET-XXL stays freight).
- Path resolution made depth-robust (name-walk to `cost_matrix_2026q1.py`) after Niklavs nested the folder under `validation/db_schenker/` for future sibling validations.

## Pending external actions
No pending external actions. Deliverable built + committed to bi-analytics. The three question sets are for Niklavs to put to Maersk / Hermes / the floor — his action, not a queued send.

## Follow-up (same session, post first close)
Niklavs reopened to ask the mirror question — what STAYS on DB Schenker and why. Added the stay-side analysis to the pipeline + a **Section E** to the report. The final DB Schenker book = 1,076 parcels, three reasons: **165 must-freight** (no carrier anywhere — GEL tubes up to 66 kg/200 cm, heavy CUSTOM_OVERSIZED up to ~100 kg, PALLET-XXL), **240 not-in-6** (eligible only on a carrier outside the chosen 6 — incl. all 143 CH, since Hermes excludes CH and Güll/Austrian Post aren't in the 6), **671 price** (a final-6 carrier could take it but DB Schenker's invoice is cheaper, 90.9% of the time). The price bucket is 97% **FR (510) + PL (142)** — the FR slice is a direct readout of the open FR-extend decision. Only the must-freight cluster is a hard constraint; the other two are levers. Second bi-analytics commit for the Section E change.

Cascade: none (no gielinor meta/ritual/hook changes this session).
Main-brain changes: none beyond this quest-log + inventory resume + one bank draft (harvest).
