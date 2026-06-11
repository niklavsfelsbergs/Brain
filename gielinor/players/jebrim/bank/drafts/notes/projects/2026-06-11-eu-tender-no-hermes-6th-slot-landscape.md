# EU tender — the no-Hermes 6th-slot landscape

> Source: [[S200_104770bd_eu-tender-no-hermes-portfolio-check|S200]] (`104770bd`, 2026-06-11) analysis of `2_analysis/data/scenarios_2026q1.parquet` (82 decision sets, 2026-06-10 17:10 scorer build) + per-carrier decomposition. Basis = **Q1 cherry-pick selection ceiling**, ≤6-family cap — NOT the routing-annual basis of the report headline. Cross-link: [[eu-tender]], [[S194_907d4e63_eu-tender-holdup-pass-and-project-rating|S194]] final-report structure.

## The question it answers

If Hermes fails its gates (DBS dims / ops / appetite), one portfolio slot opens. Which rejected bidder fills it best, and does any 6-carrier no-Hermes set beat the base 5?

## The landscape (Q1 cherry-pick, vs base-5 `all_renewals_plus_maersk_eu_new` €258,263 / 8.74%)

| 6th slot | Q1 saving | Δ vs base-5 | Verdict |
|---|---|---|---|
| dhl_express | €378,266 (12.80%) | +€120k | **Mirage** — ~€84k is DBS-origin freight parcels (DBS slice 5,062→2,690 parcels, dhl_express takes them at ~€37 avg). Same conditional oversize slice as the Hermes module → gated on the same dims check; engine last biased 196% of invoice (420-parcel slice, 2026-05-22 table). |
| fedex | €313,573 (10.61%) | +€55k | Partly same mirage (takes ~1,200 DBS parcels); 1.73 full-eligibility bias; no winning-slice bias measured. |
| guell | €307,465 (10.40%) | +€49k | **Defensible** — 14.6k parcel-shaped wins (avg €5.84), DBS slice untouched (5,062→4,929). Engine 0.75 of invoice on winning slice ("fresh-bid undercut, saving real"). Residual risk commercial: do the offered rates hold. |
| austrian_post | €280,693 (9.50%) | +€22k | Marginal; narrow AT eligibility. |
| gls | €259,412 (8.78%) | +€1k | Adds nothing (and 1.28 winning-slice bias). |

Reference: with-Hermes 6-set `all_renewals_plus_maersk_eu_new_hermes` = €347,476 (11.76%).

## The reading

- **The base-5 pick survives a Hermes exit intact.** No 6th slot changes who the core carriers are; the only honest add is Güell for a thin slice.
- **DBS dims gate both paths.** The DBS-origin oversize value reroutes credibly to *no one* until the dims question (template-vs-measurement on zV parcels) resolves — Hermes or DHL Express alike. Any "6th carrier recovers the module" claim is the same conditional wearing a different logo.
- **Missing piece for the report:** a cell-level routing run + annualization for base+Güell (same machinery as the build_final_stats counterfactual) — the cherry-pick +€49k will take the usual routing haircut (~20% historical decision→routing gap) before annualizing.

## Caveats / vintage

- Bias table (`decision_report/bias_table.md`) is the 2026-05-22 refresh — pre-3.2.0/2.2.0, 2025 population. Already on the [[S194_907d4e63_eu-tender-holdup-pass-and-project-rating|S194]] hold-up cleanup list.
- Scenario parquet predates the [[S198_cbc40f78_fr-incumbent-rebase|S198]] FR-incumbent rebase (which touched routing/annual attribution, not the scorer) — directionally fine, but a scorer re-run would shift incumbent baselines slightly.
- Post-rebase base = **€393,477/yr** (annual_stats structure), not the €420,218 in final_stats' stale structure block (drift found at [[S200_104770bd_eu-tender-no-hermes-portfolio-check|S200]] close — see quest log).
