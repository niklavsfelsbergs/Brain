# Resume — EU Tender engine rebuilds (S103)

**Status:** in-progress · session d4f287de · 2026-05-27
**Quest:** `quest-log/in-progress/S103_d4f287de_eu-tender-engine-rebuilds.md`
**Continues:** S102 (6217a8d5). **Repo:** out-of-tree `bi-analytics-main/NFE/projects/2_EU_tender_2026/2_analysis/carriers/`

## Where we are
- **maersk-3.0.0** — DONE + COMMITTED (tender `3b86d6a`, S102). Reference pattern.
- **hermes-2.0.0** — DONE + VERIFIED + COMMITTED (tender `990d61c`, S103). 31/31 fixtures + full-pop smoke clean (528,721 rows, 96.5% elig, €3.16M; bulky +€445k, fuel 0/0/7%). Bulky per-country + per-month base-2021 fuel + MAX_LENGTH 170 all wired.
- **FedEx** — `fedex-2.0.0` HELD (round-2 pending). **DHL Paket** — HELD (round-2, Bulky ~€2.31M).
- **DHL Express, Austrian Post** — NOT started (next).

## Next concrete step — wire `dhl_express-2.0.0` (PLAN §B.23) — BIG build (7 subsystems)
Engine: `carriers/dhl_express/` (`dhl_express-1.1.0` now). Spec: `carrier_responses_to_open_questions/DHL_express/REVIEW_CONCLUSIONS.md` + research `research/2026-05-27-austrian-post-public-indices-and-dhl-express-demand.md`. **Principal ruling (S103): MODEL BOTH residual drivers (demand + pickup) as clearly-flagged ASSUMPTION constants** (not hold-at-0). Build order:

1. **Fuel monthly (Q1/Q2)** — replace scalar `FUEL_PCT_AIR=0.45`/`FUEL_PCT_ROAD=0.12` with a per-ISO-week (CW) schedule keyed on `shop_order_created_date`. Values from REVIEW_CONCLUSIONS: TDI(air) CW2026 1-5=30.00 / 5-9=28.75 / 9-14=30.50; DDI(road) CW2026 1-5=18.50 / 5-9=17.00 / 9-14=18.25 (+ CW2025 40-52 for completeness). **Note:** `_select_service` compares fuel-aware totals using the scalar pcts → must switch to the per-row month/week pct.
2. **Fuel-on-listed-surcharges (Q3, two-phase)** — fuel uplifts base + listed transport surcharges (oversize, overweight, non-conveyable, remote-area, demand, residential, etc.) but NOT customs/clearance/toll/DG. cost_fuel = pct × (base + Σ fuel-eligible surcharges).
3. **Remote Area (Q4)** — ⚠️ heaviest piece. Parse `DHL_Express_Remote_Area_Surcharge_locations_2026.xlsx` (108,755 rows: Country/City/Postcode-range, eff 2026-01-04) into a parquet; build country+postcode-RANGE matching against `shipping_zipcode` (engine does NOT currently read shipping_zipcode — add it to the input contract). Fires 0.50 EUR/kg min 24. `surcharges/remote_area.py` exists as a stub.
4. **Non-Conveyable weight (Q5)** — actual weight 25-70 kg → 12€ dom / 20€ intl; **exclusivity group with Oversize (OSP)**. Shape branch un-wireable (no mart shape signal) → document/accept. `surcharges/nonconveyable.py` stub exists.
5. **Demand Surcharge (Q9) — MODEL per principal** — Jan 1–Feb 16 window (`shop_order_created_date`). Penguin per-kg values: dom TDI €0.10/kg, intl DD €0.15/kg, intl-TD zone matrix €0.10–1.90/kg (Europe→Americas €0.50/kg). Wire per-service per-kg × billable_weight, in-window only. **Flag the zone-mapping + "held in Jan–Feb" as ASSUMPTION** (penguin residual). Map Picanova PL→ lanes to zones (state the mapping).
6. **Pickup line-haul (Q11) — MODEL per principal** — population-allocated flat per-parcel adder: (van 387.50 + truck 905.00 + road-fuel) × **5 days/wk** (ASSUMPTION) × weeks ÷ total eligible DHL-Express parcels ≈ +€0.5–0.9/parcel. Compute once over the population, apply flat to eligible rows. Flag days/week.
7. Keep **oversize** €10 (Q6 correct), **customs** 0 (Q7 correct; + DTP note — confirm Picanova incoterm not DTP), **emergency** 0 (Q10 suspended), **residential** 0 (WA8). Bump ENGINE_VERSION `dhl_express-2.0.0`; fixtures for every new driver + boundaries; `python -m carriers.dhl_express.tests.test_engine`; full-pop smoke; commit pathspec-scoped local-only.

**Net effect (per review):** DHL Express cost moves UP on rebuild (road fuel +6pp on 86% bulk, pickup now allocated, demand for the Jan1–Feb16 slice, remote+non-conveyable now fire) → less favourable ranking than the under-priced current engine.

Then `austrian_post-2.0.0` (§B.7.c/d: gross-only, no-peak, Sperrgut>100cm, Stettin→CH Hohenems rate, CH customs 1.00 regardless ZAZ, CH FX, DSV trucking).
Finally: `python cost_matrix.py` → compare new Q1 per-carrier totals + portfolio ranking vs the old-proxy run; surface the shift; then `decision_scorer.py` + report regen.

## Build pattern (proven on hermes-2.0.0)
1. Read the carrier's `REVIEW_CONCLUSIONS.md` "Engine to-do" + research file + the engine's current constants/calculate/surcharges/fixtures.
2. constants → surcharges → calculate (fuel/eligibility) → fixtures (re-date NON_PEAK off any non-zero-fuel month; add new-feature + boundary fixtures) → CLAUDE.md doc + version history.
3. Verify: `python -m carriers.<carrier>.tests.test_engine` (UTF-8: `PYTHONUTF8=1`) + full-pop smoke over `data/population.parquet` (no error + sane aggregate + new components populated).
4. Commit pathspec-scoped (`git commit -- <explicit files>` — tree has heavy unrelated WIP; never `git add .`), local-only, "EU tender: <carrier>-X.Y.Z rebuild (S103)" + Co-Authored-By trailer.

## Files to read first
- `carriers/dhl_express/` (constants + surcharges + calculate + tests)
- `carriers/maersk/` (committed 3.0.0 pattern — esp. two-index fuel by region, oversize modules) + `carriers/hermes/` (committed 2.0.0 — per-month fuel + per-country surcharge `replace_strict`)
- `carrier_responses_to_open_questions/<carrier>/REVIEW_CONCLUSIONS.md`
- `docs/PLAN.md` §B.23 / §B.7

## Notes / residuals
- Hermes residuals (non-blocking): pin Feb/Mar exact Destatis index off the carrier's promised Feb figure (settles the 122.7 knife-edge + Mar ±0.5%); Island Delivery 8.00€ auto-vs-opt-in (Q8).
- `carriers/maersk/CLAUDE.md` version-history still describes pre-3.0.0 state (10% fuel, toll placeholders) — refresh on a docs pass.
- `tests/test_f3_billable_lookup.py` 1 intentional FAIL is a standing gross-only guard, not a regression.
- Brain-side S103 records (quest-log/inventory/comms/intent) uncommitted — awaiting principal go (S099 brain records also still uncommitted per S099 close).
