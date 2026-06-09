# S172 — DHL truck (linehaul) cost: Warenpost + Kleinpaket → engine + cascade

**Player:** Jebrim. **Session sid8:** df374cef. **Project:** EU tender 2026 / dhl_paket engine.
**Born:** 2026-06-09. Continues the Warenpost thread from [[S165_f4a07849_cost-structure-card-warenpost-routing-plan|S165]] (f4a07849) + [[S166_f82b01df_routing-service-split-build|S166]] routing (f82b01df).

## Ask
Add a truck (linehaul/injection) cost for DHL Warenpost + Kleinpaket. Step 1: size it from
`shipping_mart.fact_truck_charges`. Then wire into the EU-tender engine and re-run downstream.

## What happened

### 1. Sizing (two shipping-agent pulls)
- **2026 YTD pull** (sub-trace `S169_truck-cost-warenpost-sizing.md`): the brief's `truck_provider LIKE 'DHL%W%'` returned **zero rows** — `truck_provider` holds **lane** names, not carrier services, and there is no "Warenpost" lane. Resolved by ground-truth join `fact_shipments.allocated_truckload_id = fact_truck_charges.truckload_id` (NOT the bare `truckload_id`): Warenpost rides the lane labelled **"DHL Kleinpaket"** (99%+ `DHL54WARENPOST` — a misnomer). 2026 YTD = €0.78/parcel.
- **Niklavs corrected the window:** the truck tariff is a flat €284/load, so per-parcel cost is purely truck-fill; 2026 YTD misses Q4 peak fill and overstates. Re-sized on **FY2025** (sub-trace appended to `S150_d2_dhl_paket.md`): €224,928 / 487,354 parcels = **€0.46/parcel** volume-weighted (Dec floor €0.29 at 976 parcels/load; Feb ceiling €1.04). Recommended single FY-weighted €0.46; season-split rejected (fragility on a flat tariff).

### 2. Decisions (Niklavs)
- Use **€0.46/parcel for both Kleinpaket AND Warenpost** (real Kleinpaket has no dedicated lane; Warenpost figure used as common linehaul).
- **Include it in the cheapest-eligible selection, not just the total** — because DE Paket / Paket Intl linehaul is **bundled in their rate-card prices** while Kleinpaket/Warenpost linehaul is not; adding €0.46 to the latter puts all six services on the same all-in basis.

### 3. Engine wiring → `dhl_paket-2.2.0`
- `constants.py`: `TRUCK_COST_PER_PARCEL_EUR = 0.46` (documented); version bump.
- `surcharges/truck_cost.py` (NEW): `TruckCost` Surcharge — fires on KP + both Warenpost only (inverse of `TollCO2`); registered in `surcharges/__init__.py`.
- `calculate.py`: +€0.46 into `_select_cheapest` for kp / wpstd / wpprem compares; `cost_truck` output column; comments + docstring.
- `tests/`: `cost_truck` asserted on every fixture; KP×2 / RO / CH carry it; **NL flips Warenpost→Paket Intl Premium** (5.30 vs 5.15 all-in) — the behavioural proof. **22/22 pass.**
- Docs: engine `CLAUDE.md` (surcharge table, output col, selection note, version history incl. backfilled 2.1.0) + `docs/ASSUMPTIONS.md` (new [[S169_truck-cost-warenpost-sizing|S169]] subsection).

### 4. Cascade (full downstream re-run)
- Re-ran **both tender matrices** off existing population (no Redshift pull): `cost_matrix_2026q1.py` (4.78M rows) + `cost_matrix.py` (full-year 25.9M rows). Only my `dhl_paket` engine is dirty in `carriers/` (no UPS in the roster; [[S171_c4e56024_ups-fuel-basis-and-gri-sensitivity|S171]] UPS refit lives in `1_offers/`, doesn't feed the matrix) — verified.
- Rebuilt **carrier_overview_v2**: competitive_map → build_summary → build_hand_cards → _cost_structure_probe (**9/9 clean**) → build_report. `carrier_overview.html` + `exec_brief.html` regenerated.
- Rebuilt **routing_2026q1**: build_final → routing_report. **Q1 saving €411,344 (13.9%) → €377,753 (12.8%)**, −€33,591 (truck cost raises routed total; today/incumbent unchanged).
- **Matrix verification:** `cost_truck` = exactly €0.46 on `dhl_kleinpaket_de` / `warenpost_intl_std` / `warenpost_intl_premium`, €0.00 on Paket DE/Intl, version 2.2.0 throughout.

## Cascade.
EU-tender doc/status cascade: engine `CLAUDE.md` + `ASSUMPTIONS.md` updated in-pass (Step-8 discipline). Cost-structure-card prose (carrier_overview_v2/sections/dhl_paket.md) NOT re-touched — the rendered ledger auto-picks `cost_truck`; prose narrative unaffected by a flat per-parcel add. The **S150 decision_report is now stale** vs the refreshed `cost_matrix_2026q1` — left for a coordinated S150 pass (not rebuilt).

## Main-brain changes.
None. All knowledge writes are Jebrim-scoped drafts (harvest below). No global/meta/lorebook edits.

## Decisions locked
€0.46/parcel; both KP + Warenpost; in-selection (all-in basis); FY2025 weighted basis; single figure (no season split); decision_report deferred to S150; bi-analytics commit deferred to principal go.

## Sub-traces
- `S169_truck-cost-warenpost-sizing.md` — the 2026-YTD sizing pull (superseded by FY2025).
- `S150_d2_dhl_paket.md` — carries the FY2025 sizing append (S150's file, dirty; not mine to commit).
