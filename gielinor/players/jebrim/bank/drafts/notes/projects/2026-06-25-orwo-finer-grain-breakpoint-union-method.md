# ORWO finer-grain routing — the breakpoint-union sizing method + the DE finding

**Source:** [[S368_364d42cd_orwo-per-lane-band-grain-sizing|S368]] (sid8 364d42cd), 2026-06-25. READ-ONLY off the engine switch parquets + rate tables. Continues the ORWO tender arc ([[S275_abfcf511_orwo-tender-contracts-coverage-weight-grain|S275]] umbrella / S286 annualization).

## The question
Does routing ORWO at **destination × weight-band** (vs the current one-carrier-per-country `per_lane_optimum.py`) bank materially more? A single carrier per country hides weight crossovers — a carrier can lose a country's blended average yet win a weight slice.

## The finding (H1, 606,217 parcels)
- **Finer grain banks €36,206 H1; DE is €34,619 (96%)** via a clean **DHL <10kg → Maersk ≥10kg** threshold. Whole-country misses it because DE is ~90% light parcels (DHL wins the blend); Maersk wins the heavy tail decisively (10kg band: €22,433 vs €12,708 on 11,360 parcels).
- FR €1,503 (Maersk <1kg → UPS ≥1kg); AT €64; LU €18; **21/25 lanes show €0** (single carrier already optimal). GB has NO crossover (Maersk wins every band).
- Indicative annual ~€84k/yr for DE (×2.43 portfolio proxy) — not firm; needs the dated per-band reweight (DE-domestic may scale below the cross-border-driven portfolio factor).
- Whole-country baseline unchanged: €140,886 H1 / **−€343k/yr**. The DE band move is **additive** to it.

## The method (reusable — this is the exhaustive way to find crossovers)
**Band on the UNION of all candidate carriers' rate-card weight breakpoints → per-band argmin on repriced full cost → merge same-winner runs → coherence pass → cost all rungs.**
- **Completeness guarantee:** between two adjacent breakpoints every carrier sits on a fixed rate step, so each carrier's per-parcel cost is constant → the cheapest carrier cannot change inside an interval. **A crossover can only occur AT a breakpoint.** Banding on the union of breakpoints therefore catches every crossover; nothing hides between edges. (Integer `floor(kg)` bands are a lossy approximation — they collapse Maersk's sub-kg breaks.)
- **Breakpoints live in the engines:** GLS domestic [1,2,3,5,8,10,15,20,25,31.5,40], GLS euro [1,2,5,10,15,20,25,30,40], Maersk incl. sub-kg [0.25,0.5,0.75,1,…,2,3,…,10,15,20,25,30], UPS, DHL. Per-country (eligible carriers + breaks vary).
- **Contracts set grid EDGES (completeness), NOT thresholds.** Crossover values stay computed from repriced full cost (coalesce to incumbent `current_full` where a carrier is ineligible).
- **Verified complete:** union-grid scan = €36,206 H1 ≈ coarse 1kg €36,197; raw ceiling €36,568 just above bookable → no hidden sub-kg or multi-crossovers.

## Caveat on the scratch tool
`carrier_engines/per_lane_band_optimum.py` (uncommitted) carries 2 artifacts — the `5%-of-lane` floor (eats DE on the 90% lane) + a 31kg tie-break collapse. Its rung-3 is misleading; the validated logic is the inline union-grid scan. Rebuild fresh in the redo.

## Links
Whole-country optimum = `…/7_ORWO_tender_2026/repricing_base/carrier_engines/per_lane_optimum.py`. EU-tender coherence method = `2_EU_tender_2026/2_analysis/routing_investigation/ops_coherence/`. Redo plan + open method choices in [[orwo-band-grain-resume__364d42cd]]. Parent [[S275_abfcf511_orwo-tender-contracts-coverage-weight-grain]]. Candidate for the (still-uncreated) `orwo-tender` domain digest.
