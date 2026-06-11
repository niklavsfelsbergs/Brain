# Shipping-agent pull — UPS OML/LPS surcharge predictor investigation

**Role:** shipping-agent (emulation) · **Player in scope:** Jebrim · **Date:** 2026-06-11 · **Tier:** gold + upstream (maintainer overlay; silver `ups_invoices`, bronze `csv_ups_zip_invoicedata`)

## Ask
What predicts UPS OML-family + LPS surcharges? Full UPS invoiced population, PCS PL hotspot. Outcomes: (a) predictor in our declared data → partly legitimate; (b) predictor only in UPS's own billed dims → our measurement gap; (c) no predictor anywhere → UPS mischarge. Contractual: LPS L+G>325, OML L+G>419. Book secondaries (side>274, wt>70) unconfirmed-contract. Net basis (refund-in-place reversals).

## Scope resolved
- Charge handle (silver): `chargedescriptioncode IN ('LPS','OVR','OML')` + demand-stacked `SLP` ("Nachfragezuschlag-Großes Paket" = Demand LPS) + `SOV` ("Nachfragezuschlag-Über Max." = Demand Over Max). German originals; gold's "Demand Surcharge - Over Maximum" = SOV via the bucket-mapping table. PSC/PSR/SAH (residential/AHS demand) excluded by design.
- Window: silver all-time 2023-01-10 → 2026-05-29 for totals; bronze UPS-dims slice limited to invoices 2026-03-11 → 2026-06-03 (~3-mo zip retention). Gold joins on trackingnumber (UPS rows).
- Population: 11,128 charged trackings; 99.3% match gold 1:1; PCS PL carries >99% of net. Total standing net all-time €1.440M (PCS PL €1.456M net of applied; other sites carry −€15k reversal-only credits).

## Live numbers (all-time, PCS PL matched, standing net = applied − reversed)
- LPS 11,036 shipments net €792.0k; SLP 4,487 net €242.0k; OVR 898 net €155.9k; SOV 1,193 net €206.6k; OML 303 net €59.1k.
- Declared-dims triggers on charged set: L+G>325 → LPS-family 43% of shipments (net: LPS €340.5k + SLP €84.9k above 325). L+G>419 → 3 shipments (€278). Side>274 → ZERO. Weight>70 → ZERO. Dim-weight@5000>70 → 7 shipments. Book secondaries explain nothing in OUR data.
- Incidence per L+G band (full PCS PL UPS invoiced, 1.61M): <250 0.09%; 250–300 0.43%; 300–325 2.35%; 325–419 46.4%; >419 3/7. Sigmoid around threshold; above-trigger only ~46% charged (not ~100%).
- UPS own dims (bronze, 2026-03→06): 627/1,161 recent charged trackings carry `packagedimensions` (UPS-measured) + `detailkeyeddim` (keyed). PASSTHROUGH TEST: keyed = our declared (881/888 within 1–3cm) → measured is independent. UPS tape: 100% of dims-carrying charged >325; over-max family (OVR/SOV/OML) 256/258 >419. Their billing is internally consistent with THEIR measurement.
- Disagreement structure: 53% measured-longest within 10% of keyed (excess from width/height inflation: keyed thin-side avg 7cm → measured 11cm+); 32% measured length 1.5–2.7× keyed (avg 98→263cm) — physically implausible for single flat canvases. Dims coverage concentrates exactly on the sub-threshold-declared charged subset (our_hit_325 = 0 there) → UPS prints dims when its audit changed the billing.
- Grain: single-package 11,398/11,399 charged lead-shipments → grain mismatch ruled out.
- Cohorts (net all-time): zugeschnittene Verpackung (avg L+G 329, all >325) €394k @ 46% incidence — legitimate band; STANZVERPACKUNG 120x90 (all 300–325) €290k @ 2.5% — tolerance zone; STANZVERPACKUNG 120x80 (max 296) €162k @ 0.6% — dispute; WICKELVERPACKUNG 80x60 AE (max 270) €109k @ 0.16% — dispute incl. over-max; CUSTOM_OVERSIZED €95k @ 1.9%, avg L+G 296, only 70/31,580 >325 — label ≠ physical, NOT the predictor.
- Within >325 band: charged vs uncharged identical on every declared attribute (L+G 332.3 vs 332.9, wt 7.0 vs 7.1) — no second declared predictor; selection is UPS-side.
- Time: reversal coverage collapsed since Q4-2025 (OVR mid-2025 ~100% reversed → now ~30–37%); un-reversed accrual now ~€160k+/quarter. SLP seasonal (peak Q4–Q1) as expected for demand windows.

## Verdict (per family, standing net)
- LPS-family (LPS+SLP, €1,034k): ~41% (€425k) legitimate by our own dims (>325); ~38% (€390k) tolerance-zone 300–325 (UPS measures over by small width/height inflation — contested, physical audit decides); ~21% (€219k) sub-300 dispute.
- Over-max family (OVR+SOV+OML, €422k): 0% justified by our dims (zero >419 ever); UPS's tape says >419 but at +150–250cm over keyed on single-package flat parcels — physically implausible → dispute. UPS itself was reversing ~100% mid-2025 and has stopped keeping up.
- Outcome mix: (a) €425k legitimate; (b)-zone €390k measurement-disagreement; (c) €641k UPS-mischarge dispute.

## Checks done
- Reconciled vs prior S124 all-time standing net (~€1.44M) ✓; family totals cross-checked across two groupings (€3.6k fan-out from 15 multi-matched trackings explained).
- Passthrough test on keyed dims passed (keyed = ours → measured independent).
- Falsifying cut: charged-vs-uncharged within >325 band — no declared-data separator.
- Grain check (multi-package) ruled out.
- Bronze coverage concentration explained (dims printed where audit changed billing).

## DQ caveats
- Off gold contract: all family-level applied/reversed/net (silver), UPS dims (bronze). Bronze ~3-mo retention only — UPS-dims findings extrapolated structurally, not totalled.
- destination_country empty on PCS PL slice — geography untestable.
- PCS CGN/Köln carry reversal-only credits (−€15k) for charges applied on other trackings.
- Demand-family WorldEase variants included; never-reversed (WorldEase reversal channel absent).

## Deliverable
- Final report in return message (numbers-first). Probe SQL: `shipping-agent/scratchpad/ups_oml_lps_predictor_probes.sql`. No chart requested.

## Open / needs principal
- known-dq UPS LPS/OML entry should gain the UPS-independent-measurement finding (maintainer edit, principal-gated).
- Physical audit of the 300–325 tolerance zone (€390k) is the decisive next action — sample re-measure of STANZVERPACKUNG 120x90 packed parcels vs UPS dimensioner.
- Reversal-rate collapse since Q4-2025 → standing receivable now accruing ~€160k+/qtr un-reversed; dispute-filing cadence question for whoever files UPS claims.
