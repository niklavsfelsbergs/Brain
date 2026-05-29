# S103 — EU Tender 2026 engine rebuilds (continued)

**Session:** d4f287de · 2026-05-27 · Jebrim (principal)
**Continues:** [[S102_6217a8d5_eu-tender-fedex-reply-review|S102]] (6217a8d5, closed clean @15:30). Adopting resume `inventory/eu-tender-engine-rebuilds-resume__6217a8d5.md`.
**Repo:** out-of-tree `Documents/GitHub/bi-analytics-main/NFE/projects/2_EU_tender_2026/2_analysis/carriers/`

## Goal
Rebuild the deterministic-ready engines on confirmed Round-1 values, then re-run the Q1 cost matrix to surface the ranking shift off the old proxies. Order: hermes-2.0.0 → dhl_express-2.0.0 → austrian_post-2.0.0 → `cost_matrix.py`. FedEx + DHL Paket HELD (round-2 pending). maersk-3.0.0 is the committed reference.

## Turn log

### Turn 1 — respawn + scope
Respawned Jebrim. Loaded keepsake + comms tail; no live siblings (no session active in last 15min). Posted OPEN to comms. Read resume note + Hermes spec (`carrier_responses_to_open_questions/Hermes/REVIEW_CONCLUSIONS.md`) + research (`research/2026-05-27-hermes-destatis-diesel-index.md`) + maersk-3.0.0 pattern + the `_base` framework. Confirmed: dormant `diesel_schedule.parquet` holds the retired 2015-base offer ladder (NOT to be used). polars 1.33 (`replace_strict` available). Pulled rate bands for bulky fixtures (DE/AT/NL/FR/PL/ES/IT).

**Decisions taken (within-spec):**
- Fuel mechanism = per-month resolved point estimate `FUEL_PCT_BY_MONTH {Jan:0, Feb:0, Mar:0.07}`, base-only, citing the research index resolution (122.5/122.7/158.5 on the 2021-base reply ladder). March 0.07 is the point estimate; research band is 6.5–7.0% (±0.5% on the exact ladder band edge) — documented as sensitivity. Not encoding a full 2021-base parquet ladder (the research only knows it to a linear approximation; fabricating parquet precision would be a trap). `diesel_schedule.parquet` left dormant (engine never loads it) + flagged superseded in the doc.
- Fixtures: NON_PEAK March→Feb 15 (keeps existing base/maut/peak/reject fixtures at 0% fuel, unchanged) + new March-fuel and bulky fixtures added.

Building hermes-2.0.0 (constants → bulky → fuel → fixtures → doc → verify → commit).

### Turn 2 — hermes-2.0.0 SHIPPED ✅
Built + verified + committed `hermes-2.0.0` (tender `990d61c`, 5 files +365/-92, pathspec-scoped, local-only — 77 unrelated WIP files in the tree untouched).
- **Constants:** ENGINE_VERSION 2.0.0; MAX_LENGTH 200→170; `FUEL_PCT_BY_MONTH {Jan:0, Feb:0, Mar:0.07}` + default 0; `BULKY_COST_BY_COUNTRY` (DE 8.85 + named intl + 57.75 default) + trigger consts (120/170/360).
- **Bulky** (`surcharges/bulky.py`): `conditions()` = d_max>120 & ≤170 & length_plus_girth_cm≤360 & base not null; `cost()` = `replace_strict` per-country expr.
- **Fuel** (`calculate.py` `_apply_fuel`): per-month `replace_strict` on `shop_order_created_date.dt.month()`; base-only; null on ineligible.
- **Fixtures:** NON_PEAK March→Feb (existing fuel=0 fixtures unchanged); +Jan/Mar fuel + 4 bulky-value + 5 boundary fixtures. **31/31 pass.**
- **Smoke** (528,721 rows): 96.5% eligible (was 96.7%; 1,953 new over_max_length from the 170 cap), total €3.16M, maut €102,011 (=510,055×0.20 ✓), **peak €0** (Q1, no Oct-Dec), **bulky €445,430 / 18,873 parcels** (per-country values all correct), **fuel 0/0/7% by order month = €52,091**.
- **Doc:** `hermes/CLAUDE.md` refreshed (output table, surcharges, fuel ladder + diesel_schedule superseded note, eligibility limits, open items Q1-Q6 resolved, 31 fixtures, version history).

**Pre-existing (not mine):** `tests/test_f3_billable_lookup.py` has 1 intentional FAIL — a guard that the rate lookup stays on `weight_kg`. Q1 confirmed gross-only, so correct; the guard only fires if vol-weight is ever activated without flipping `_attach_rate_tables`. Untouched by me (git diff empty).

Next: **dhl_express-2.0.0** (§B.23), then **austrian_post-2.0.0** (§B.7), then `cost_matrix.py` re-run + ranking shift. FedEx + DHL Paket HELD.

### Turn 3 — dhl_express scoping + checkpoint decision
Read the dhl_express engine (constants/calculate) + REVIEW_CONCLUSIONS + confirmed scope. It's a **7-subsystem rebuild** (monthly CW fuel, fuel-on-listed-surcharges two-phase, 108k-row remote-area xlsx parse + postcode-range matching [engine doesn't read shipping_zipcode today], non-conveyable weight + OSP exclusivity, demand zone-matrix Jan1–Feb16, population-allocated pickup line-haul, + oversize/customs confirms) — materially bigger than Hermes.

**Principal rulings this turn:**
1. **dhl_express residual drivers → MODEL BOTH** (demand + pickup) as clearly-flagged ASSUMPTION constants, not hold-at-0. (Folded into the resume note's build plan.)
2. **Session scope → checkpoint here, build dhl_express fresh next session.** Right discipline for a precision-sensitive multi-subsystem engine; avoids carrying a half-built engine across a context boundary.

**Clean checkpoint state:** hermes-2.0.0 shipped + committed (tender `990d61c`). Full dhl_express-2.0.0 build plan (7 ordered steps, model-both folded in) is durable in `inventory/eu-tender-engine-rebuilds-resume__d4f287de.md`. Brain-side S103 records (this quest-log, inventory resume, comms, intent) UNCOMMITTED — held for principal go (consistent with the held S099/[[B-008_2026-05-26_eighth-bankstanding|B-008]] brain records). Live sibling: guthix-97dba361 ([[B-009_2026-05-27_ninth-bankstanding|B-009]] bankstanding, globals-only) — no collision; jebrim-34ab5b53 (mgmt deck, different bi-analytics subtree).

Session paused at clean checkpoint. Resume = wire dhl_express-2.0.0 per the resume-note plan.
