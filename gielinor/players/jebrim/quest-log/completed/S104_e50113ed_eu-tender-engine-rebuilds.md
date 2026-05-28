# S104 — EU Tender 2026 engine rebuilds (continued)

**Session:** e50113ed · 2026-05-27 · Jebrim (principal)
**Continues:** S103 (d4f287de, ended clean @16:43 same terminal — hermes-2.0.0 shipped). Adopting resume `inventory/eu-tender-engine-rebuilds-resume__d4f287de.md`.
**Repo:** out-of-tree `Documents/GitHub/bi-analytics-main/NFE/projects/2_EU_tender_2026/2_analysis/carriers/`

## Goal
Wire `dhl_express-2.0.0` (the next deterministic-ready rebuild — 7 subsystems), then `austrian_post-2.0.0`, then re-run `cost_matrix.py` to surface the ranking shift off the old proxies, then `decision_scorer.py` + report regen. maersk-3.0.0 + hermes-2.0.0 are the committed reference patterns. FedEx + DHL Paket HELD (round-2 pending).

## Turn log

### Turn 1 — respawn + scope + session setup
Respawned Jebrim (cue "Hey jebrim, lets continiue eu tender"). Loaded global keepsake/examine/niksis8 + Jebrim keepsake/examine/niksis8_character + last-alched (B-009 Phase 0, light/clean). Sibling detection: my predecessor d4f287de (S103) ENDED clean at a checkpoint in this same terminal (SessionEnd 16:43) — adopting its resume, not a crash. 6217a8d5 (S102) + 34ab5b53 (mgmt deck) idle/stale; guthix-97dba361 (B-009) globals-only, already alched Jebrim → no collision. Posted OPEN to comms. dhl_express engine confirmed at `dhl_express-1.1.0`, path verified.

Build plan (7 ordered steps, principal model-both ruling folded in) carried in `inventory/eu-tender-engine-rebuilds-resume__e50113ed.md`. Starting the build: read the dhl_express engine (constants/calculate/surcharges/tests) + REVIEW_CONCLUSIONS + research file before wiring.

### Turn 2 — dhl_express-2.0.0 WIRED + smoke clean (6/7 subsystems)
Grounded fully (engine + _base framework + REVIEW_CONCLUSIONS + research + population schema). Confirmed `shop_order_created_date` + `shipping_zipcode` both in the population input contract. Then wired all 7 subsystems:
- **constants.py** — ENGINE_VERSION 2.0.0; per-CW fuel dicts (TDI air ~30%, DDI road ~18%, weeks 1-14 + 2025 tail, half-open band rule); demand per-kg + window (Jan1–Feb16) + region sets; non-conveyable dom/intl 12/20; oversize dom/intl 6/10; pickup constants (van 387.50 + truck 905.00, ×1.18 road fuel, ×5 d/wk ×13 wk ÷ 184,273 elig = €0.538/parcel baked).
- **calculate.py** — fuel-aware service selection on per-row CW pct; `_apply_fuel` = per-row pct × (base + fuel-eligible surcharges, Q3 two-phase); `_apply_pickup` flat adder (road fuel baked in → excluded from fuel subtotal); remote-area `_remote_area_hit` via expanded-postcode semi-join; `_demand_region`/`_is_domestic` derived.
- **surcharges** — `peak.py`→`demand.py` (git mv); Demand per-kg×billable by service/region, in-window; RemoteArea fires on `_remote_area_hit`; NonConveyable activated (25-70kg actual, OSP exclusivity, dom/intl cost); Oversize dom/intl cost. `__init__` ALL list updated (Peak→Demand).
- **rate_tables/build_remote_area.py** — parses the 108,755-row xlsx → `remote_area_ranges.parquet` (85,661 ranges) + `remote_area_postcodes.parquet` (317,414 expanded points); strip-non-digits→int normalization (handles PL/PT/SE/numeric formats; IE city-only un-matchable → accepted).

**Full-pop smoke (528,721 rows): CLEAN.** €3,425,125 total; components reconcile exactly (base 2.03M + fuel 608.5k + oversize 282.6k + nonconveyable 200 + remote 326.7k + demand 77.8k + pickup 99.1k). 184,273 eligible (34.9%); service split economy_select 96,959 / express_worldwide 87,314 (fuel-aware selection shifted the split vs the old scalar-fuel run, as expected). Demand fires only Jan1–Feb16 ✓; pickup const €0.538 on every eligible row ✓.

**FINDINGS for principal:**
1. **Remote-area is a real, material driver — €326.7k/Q1, NOT the €5-15k Phase-1 guess.** 13,605 hits (7.4%), ~all at the €24 min. Geographically legit (metros clean-checked; hits = IT Sardinia/Sicily 15%, ES Balearics/Canaries 17%, AU 35%, SE/FI/PT ~25%, NL Wadden islands, CH/FR/AT alpine). The 108k-row list materially re-prices DHL Express upward — feeds the "DHL Express moves up on rebuild" thesis hard.
2. **DE (344,142 parcels, 65% of pop) = `country_not_served`** by the DHL Express zone tables (pre-existing 1.1.0 behaviour, unchanged — DE is DHL Paket's lane). Flagging; out of scope for this fuel/surcharge rebuild but worth a principal confirm that DHL Express genuinely doesn't bid DE from PL.

Remaining: fixtures + test harness (add shop_order_created_date + shipping_zipcode; Peak→Demand + pickup fields), CLAUDE.md doc + version history, commit pathspec-scoped local-only.

### Turn 3 — fixtures + harness + doc DONE; dhl_express-2.0.0 verified (awaiting commit go)
- **Fixtures rewritten** (`tests/fixtures.py`): 26 fixtures with `shop_order_created_date` + optional `shipping_zipcode`; `expected_cost_peak`→`expected_cost_demand` + `expected_cost_pickup_alloc_eur`. Bases re-derived independently from the rate tables (not engine output); selection/fuel/demand/remote/pickup hand-computed per the documented formula. Coverage: fuel-aware WW/ES flips, per-CW fuel bands, demand by service/region + Feb16/17 window boundary, oversize intl+dom+dim boundaries with fuel-on-surcharge, non-conveyable 25/24.9/70 + OSP exclusivity, remote-area Sardinia-hit vs Milan-miss with fuel-on-surcharge, 3 rejects.
- **Test harness** (`tests/test_engine.py`): passes date + optional zip; checks cost_demand + cost_pickup_alloc_eur. **26/26 PASS.**
- **Doc** (`dhl_express/CLAUDE.md`): refreshed — service split ~53/47, output columns, phase order, surcharge table, fuel scope, remote-area normalization, validation + the remote-area finding, residuals, version history (2.0.0 entry).
- **Final verify:** 26/26 fixtures + full-pop smoke clean (€3,425,125, invariant residual €0.00).

**Commit scope (pathspec, local-only, NOT yet committed — awaiting principal go per ask-before-commit):** `carriers/dhl_express/` — CLAUDE.md, calculate.py, constants.py, surcharges/{__init__,nonconveyable,oversize,remote_area}.py, surcharges/peak.py→demand.py (rename), tests/{fixtures,test_engine}.py, rate_tables/build_remote_area.py. (rate_tables/*.parquet are gitignored — regenerated from build scripts, consistent with the existing ww/es/zone parquets.)

Next after commit: `austrian_post-2.0.0` (§B.7), then `cost_matrix.py` re-run + ranking shift vs old-proxy. FedEx + DHL Paket HELD.
