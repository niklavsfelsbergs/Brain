---
quest: S206_01871b26_ups-2.0.0-engine-build
sid8: 01871b26
ts: 2026-06-11 21:15
open_dep: cascade paused by principal (go pending); bi-analytics UPS stack uncommitted (commit ask pending)
---

# ups-2.0.x — engine done; CASCADE SEQUENCE for the next session

**Status:** in-progress (engine phase DONE + gated; cascade phase queued).

## Where we are

ups-2.0.1 built, trust-gated, documented — all in `bi-analytics-main/NFE/projects/2_EU_tender_2026/1_offers/picanova/UPS/` (UNCOMMITTED, stacked on S205's uncommitted docs). Switch book −1.3% vs FIF actuals; EU core −6..−14%; portfolio fit −0.5% ex-truck on the EU core. CH/GB operative-tier question PARKED by principal (overprice accepted — those lanes just won't be picked for UPS; revisit pre-signature). Residential calibrated 0.40×46.3%; peak surge 0.29×46.3% residential-gated (invoice-verified). Harvest drafts: ups-residential-and-peak-surge-mechanics (bank), counts-by-counting (examine).

## THE CASCADE SEQUENCE (principal-noted 2026-06-11 — execute in order)

1. **Commit the UPS stack first** (principal go, pathspec `1_offers/picanova/UPS/* + carrier_responses_to_open_questions/UPS/*`) — clean rollback point before the cascade; bundles S205 docs + S206 engine.
2. **Read the cascade pattern:** `2_analysis/carriers/_base/` (Surcharge ABC, two-phase BASE→DEPENDENT, version-stamping) + one reference engine (`carriers/maersk/` or `carriers/hermes/` — most recently corrected) + the capability-matrix spec + `docs/DECISIONS.md` conventions.
3. **Build `2_analysis/carriers/ups/`** porting the ups-2.0.1 model: Standard destination-keyed + Express zone-keyed cards; NO dim weight on Standard (Express ÷5000 assumption); fuel 0.20; resi 0.40×0.463; fee tail 0.05; oversize incidence layer (reuse the calibration parquets from `1_offers/.../calculation/data/`). ⚠ The incidence cohorts are calibrated on UPS-carried traffic — pricing parcels currently on OTHER carriers extrapolates the cohort rates to them; flag it (packagetype mix differs by carrier).
4. **Capability matrix UPS row:** Standard-served zone set + Express family reach; hard limits per Q9 (>70 kg / >274 cm / L+G >400-or-419 — the 400-vs-419 round-2 item; use 419 per the S199 negotiated ruling until contradicted); the WW-ECO-unserved overseas tail = ineligible on the 2026 offer (it isn't quoted) — mirrors the 1_offers stays rule.
5. **Switchable-incumbent wiring:** UPS flips from invoice-fallback-only to INCUMBENT-with-engine (bid = the 2026 engine where it can price, invoice fallback otherwise — the standing incumbent treatment). Keep costs stay invoice actuals at the (cell × incumbent) grain (S203 q09d fix) — do not let the new engine leak into keep_ref.
6. **Line-haul basis decision (PRINCIPAL SIGN-OFF before reports):** UPS actuals carry ~€0.75/parcel allocated injection trucking (€110k/Q1 ≈ €440k/yr) that the offer excludes. Pick ONE convention — add ~€0.75/parcel to the UPS engine cost, or strip truck from UPS keep costs — apply it symmetrically, record in `docs/DECISIONS.md`. This shifts UPS vs every other carrier; do not regen reports before it's decided.
7. **Regen the chain with verify:** cost matrix → decision report → routing Q1 → `annual_2026/` (peak layer consumes `ups_peak_if_in_window_eur` + per-country seasonal ratios + peak-window volumes) → `final_report/` (three-number bridge, savings = keep_ref − rcost, SWITCH_MIN_PCT=2% cross-family) → `verify_report` PASS. Current canon to beat/supersede: paid 2,955,020 → do-nothing 3,055,317 → plan 2,762,682 = €292,636 Q1 / €1,442,782 ann (9.57%, S203).
8. **CROSS_CARRIER_OVERVIEW UPS row + carrier_overview prose:** UPS entering with a real engine invalidates EVERY carrier's relative claims (counts, superlatives, within-N) — re-derive the whole field, not just the UPS row.
9. **Coordination:** post comms UPDATE BEFORE regenerating shared report artifacts — they currently bundle 021047a4/475fd1ab/cbc40f78 uncommitted states; check `gielinor/comms/active.md` + sidecar for live siblings first. Management deck remains stale (separate item).
10. **Close the loop:** flip UPS/CLAUDE.md phase status + findings §9; round-2 batch (LPS amount, OML 400-vs-419, Multi/zone, Express dim+fuel) goes whenever Niklavs talks to UPS; CH/GB stays parked.

## Files / paths to read first

1. this file
2. `1_offers/picanova/UPS/findings.md` + `calculation/engine.py` (the v2.0.1 model)
3. `2_analysis/carriers/_base/` + `carriers/maersk/` (the porting pattern)
4. `players/jebrim/bank/domains/eu-tender.md` (scoring + bridge conventions)

## Also open (not cascade)

- additional-service-charge-de-gb-en.pdf — browser fetch (UPS CDN blocks scripts) → `carrier_responses_to_open_questions/UPS/`.
- Jebrim alch is due (11+ examine drafts, 2 bank drafts incl. this session's).
