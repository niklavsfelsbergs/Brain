# [[S185_e9821cdf_eu-tender-report-signoff|S185]] — Sign-off reconciliation: EU-tender decision report (Jebrim dwarf)

**Task:** Read-only sign-off of `decision_report/decision_report.html` before commit. Trace ground truth, extract every quantitative/factual claim, mark MATCH/DRIFT, verify cross-report consistency + caveats. Do NOT edit the report.

**Repo (NOT brain):** `bi-analytics-main/NFE/projects/2_EU_tender_2026/2_analysis`

## Ground truth established
- Report `decision_report.html` (mtime 19:44) is **freshly regenerated** — newer than `data/scenarios_2026q1.parquet` (18:24), which is newer than the cost matrix (17:13). So all *generated* numbers track the current parquet.
- `report_2026q1.py` consumes `data/scenarios_2026q1.parquet` + `data/cost_matrix_2026q1/` + `routing_2026q1/routing_stats.json`.
- Parquet baseline = €2,955,020.01 (Σ today_eur). 82 decision sets. Verified by reading parquet + recomputing live cost-matrix facts via `load_cost_matrix_2026q1()`.

## Generated numbers — all MATCH parquet/live
| Claim | Report | Ground truth | |
|---|---|---|---|
| renew_dpd_pl mandatory | +€68,245 | +€68,245.02 | MATCH |
| renew_dpd_pl vs tender-offer score | "vs −€2k" (historical) | was −€2k pre-reframe | MATCH (correct historical ref) |
| keep-not-retire DPD framing | NEW_OFFER=current contract, tender DECLINED | scorer state = dpd_pl_current | MATCH |
| all_renewals_drop_dpd_pl | −€339,778 (sharply neg) | −339,778.28 | MATCH |
| Lead (KPI/summary/block03/callout) | all_renewals_plus_maersk_eu_new_hermes €430,055 / 14.6% | parquet firm n≤6 uncov≤100 best = 430,055.17 / 14.55% | MATCH |
| Held ceiling (n≤6) | same set €430,055 | cap6 top = same | MATCH |
| Single biggest lever | add_maersk_eu_new €305,824 / 10.3% | 305,824.04 / 10.35% | MATCH |
| Baseline | €2.96M | 2,955,020.01 | MATCH |
| N_SHIPS | 531,194 | 531,194 | MATCH |
| FR_BOOK / FR_MEAN | 27,447 / €4.72 | 27,447 / 4.72 | MATCH |
| MAERSK_ENG_FR (FR priced by EU engine) | 0 | 0 | MATCH |
| FR_KEPT in lead | 13,269 of 27,447 | lead pc maersk_current_fr n=13,269 | MATCH |
| Hermes coverage / avg | 96.5% / €6.22 | 96.5 / 6.22 | MATCH |
| UPS OML | 70 parcels / €75,978 removed | 70 / 75,977.9 | MATCH |
| renew_dhl_paket near-neutral | +€12,941 | 12,940.53 | MATCH |

## DRIFT FOUND — 1 (internal consistency, stale narrative label)
**Hermes carrier-card** (hardcoded string in `CARRIER_NARRATIVE`, report_2026q1.py L362–369) still calls
`keepfr_maersk_eu_plus_hermes` = €389,937 **"the leading ≤6 candidate."**
- The €389,937 number itself is CORRECT (that set's true score = 389,937.42).
- But the **label is now FALSE**: the dynamic `lead` (KPI strip, summary bullet, block-03 header, routing callout — all 3 other "leading ≤6 candidate" mentions) correctly names `all_renewals_plus_maersk_eu_new_hermes` = €430,055 / 14.6%.
- So the report internally contradicts itself: 3 places say lead=€430k (all_renewals variant), 1 place (Hermes card) says lead=€390k (keepfr variant). The lead flipped to the all_renewals set; the static Hermes prose didn't follow.
- `389,937` appears 2× in HTML, both in the Hermes card. Drift is from a hardcoded narrative string that predates the current parquet's lead-set ordering — NOT a data error.

## Cross-report consistency — PASS (exact)
Routing callout vs `routing_2026q1/routing_stats.json`:
- Executed saving €377,471 (12.8%) = 377,471.11 / 12.77% ✓
- Floor €2,475,020 = 2,475,020.40 ✓
- Routed €2,577,549 = 2,577,548.90 ✓
- Op gap €102,529 = 102,528.50 ✓
- All MATCH. Headline routing number agrees with the brief's €377,471 / 12.77%.

DPD reframe consistency across report: PASS. No leftover "retire DPD-PL" decision prose. All 3 "retire"/2 "retirement" hits are legitimate cap-logic / keep-DPD framing ("must retire a carrier", "retirement needs paired cover", "far from a retirement candidate"). "−€2k" appears once, correctly as the historical/pre-reframe reference.

## Caveat check
- **FR-floor caveat (DPD-current engine over-prices France vs Chronopost actuals → saving is a conservative floor): ABSENT.** Zero hits for chronopost / france / fr-floor / conservative-floor / over-price anywhere in the HTML. The single "floor" hit is the routing per-parcel theoretical floor (€2,475,020), unrelated. This caveat is NOT stated in the decision report.
- **UPS +5% GRI in forward routing: ABSENT from decision report.** Only real "GRI" mention is the routing callout's "uses a GRI-free baseline" (describing the routing report's baseline, not a +5% UPS GRI). Decision report scores UPS as INCUMBENT at invoice (no GRI) — GRI is a routing-layer concept, arguably out of scope here, but the "+5% GRI in forward routing" the brief flagged is not surfaced. Note: routing callout's "GRI-free baseline" line may itself now be stale if the routing report adopted a +5% UPS GRI — worth a principal check against routing_stats provenance (no GRI key in routing_stats.json).
- **Stale scenario number predating UPS-GRI + DPD-current refresh: none in generated values** (parquet is current; report regenerated off it). The only stale artifact is the Hermes-card "leading ≤6 candidate" label above.

## Bottom line
Numbers are sound — every generated figure ties to the current parquet/routing_stats, renew_dpd_pl +€68k and keep-not-retire are consistent with the scorer. **Two things to fix before commit:** (1) the Hermes carrier-card hardcoded string still calls keepfr_maersk_eu_plus_hermes "the leading ≤6 candidate" — now contradicted by 3 other places naming the €430k all_renewals set; (2) the **FR-floor caveat is ABSENT** and the brief expected it PRESENT. Both are principal calls (narrative edits, not data).
