# EU Tender 2026 — DB Schenker re-routing: contract validation findings

> ⚠ **SUPERSEDED on numbers (2026-06-10).** Every per-slice figure below is pre-girth-confirmation (maersk-3.1.0, pure-girth): the L+2W+2H ruling (maersk-3.2.0) collapsed the Maersk lane — current state is 4,490 moved (Hermes 4,463 / Maersk 27), reroute saving €107,684. Current numbers + dim-provenance: [[2026-06-10-db-schenker-reroute-package-dims-and-savings]]. The two-layer eligibility method and validation workflow below remain valid.

> Draft (harvest, [[S164_79537cb3_db-schenker-rerouting-validation|S164]] 2026-06-08). Source: `bi-analytics .../2_analysis/routing_2026q1/validation/db_schenker/`. Cross-ref [[eu_tender_2026]] + S150 final-setups. Promote at next Jebrim alch if still load-bearing.

**Context.** The final routing moves 7,899 of DB Schenker's 8,951 Q1 parcels off (it's low-volume but expensive freight); 7,593 go to the two NEW offers — Hermes (4,746) + Maersk EU (2,847). Validated whether the contracts can actually carry them.

**Durable findings:**

1. **Eligibility is two-layer.** `capability.py` (pure rules: country + max-weight + excluded-packagetype only — Hermes/DPD/UPS/FedEx are NOT in it) AND the per-carrier engine `carriers/<c>/calculate.py` (dimension specs, rate lookup, oversize). **Dimensions live in the engine, never in the pure-rules layer.** To verify "can carrier X take this," trace: `eligible` flag → engine → `rate_tables/` → the contract doc in `1_offers/` + `carrier_responses_to_open_questions/`.

2. **Hermes is contract-clean** for the reroute: offer T&C slide = DE 31.5 kg / 450 l / 2 m; engine caps length at 170 cm (Country Details p2, Q4) — stricter than the offer. Intl dims = DE proxy (Q4 open, low stakes).

3. **Maersk EU's reroute hinges on an unverified oversize ceiling.** Rate card "Oversized Surcharge" table gives a per-country standard threshold + flat surcharge but **no upper limit**; the engine accepts any oversize (≤30 kg) where a surcharge exists (Q6 confirmed cumulative one-breach=oversize; Q8 confirmed IT/CH reject). 1,291 parcels breach the standard threshold >1.5× (up to 2.0×) — mostly **DE GEL tubes at nominal 200 cm / 560 cm L+girth** (DE standard girth 360, €21). Needs explicit carrier confirmation of the DE upper bound before banking that slice of the saving.

4. **Eligibility is judged on NOMINAL packagetype dims, not measured.** GEL = 200/560, zugeschnittene Verpackung = 130, CUSTOM_OVERSIZED ≤200. A production-floor measurement of real GEL parcels is the pivot — if real < nominal, the Maersk concern shrinks.

5. **The savings are real and large where clean.** GEL→Maersk €26.89 vs €73.09 Schenker (€46/parcel); CUSTOM_OVERSIZED→Hermes €10.43 vs €40.07 (€30/parcel). The biggest per-parcel win (GEL) is the same cluster under the oversize-ceiling cloud — so the carrier conversation and the savings prioritise the same rows.

**Reusable method (candidate skill for alching):** reroute-eligibility validation = reconstruct moved population from incumbent→new carrier → confirm eligibility vs cost-matrix ground truth → grade headroom/breach severity per axis → trace each limit to the source contract doc → separate "mechanism confirmed" from "assumption unverified."
