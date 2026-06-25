---
quest: S368_orwo-per-lane-band-grain-sizing
sid8: 364d42cd
ts: 2026-06-25 18:30
open_dep: principal to lock method choices (absolute floor value, tie-break rule, DE-only vs +FR) before building the canonical band engine (step 2)
---

# ORWO finer-grain routing (destination × weight-band) — plan + resume

## The decision this came from
Niklavs flagged that **one carrier per whole country hides weight crossovers** (his example: Maersk wins GB ≤3kg, GLS wins 3kg+). Current ORWO routing (`per_lane_optimum.py`) assigns ONE carrier per country (`group_by country_iso2`). We sized whether going finer (destination × weight-band, EU-tender style) banks materially more.

## The finding (validated, H1 invoice-date basis, 606,217 parcels)
- **Finer grain banks €36,206 H1 total — and DE is €34,619 of it (96%).** The move is **DHL <10kg → Maersk ≥10kg on DE** — a clean, single, monotone threshold. Whole-country misses it because DE is ~90% light parcels where DHL wins the blend; Maersk wins decisively on the heavy tail (10kg band: €22,433 vs €12,708).
- FR is a €1,503 footnote (Maersk <1kg → UPS ≥1kg). AT €64, LU €18, **all other 21 lanes €0** (one carrier already optimal across all weights). GB — the original example — has **no** crossover; Maersk wins every GB band.
- **Indicative annual ≈ €84k/yr** for DE (×2.43 portfolio proxy) — **NOT firm**; DE-domestic heavy parcels may scale below the cross-border-driven portfolio factor. The dated per-band reweight (step 4) produces the real number.
- Whole-country baseline (unchanged): **€140,886 H1 / −€343k/yr** (`per_lane_optimum.py` → `annual_orwo.py`).

## The validated method (this is what the redo runs on)
**Band on the UNION of the carriers' rate-card weight breakpoints, then per-band argmin → merge same-winner runs → coherence pass → cost.**
- Mathematical guarantee: between two adjacent breakpoints every carrier is on a fixed rate step, so each carrier's per-parcel cost is constant → the cheapest carrier cannot change inside an interval. **A crossover can only occur AT a breakpoint**, so the union grid catches every crossover — nothing hides between edges.
- Breakpoints are in the engines' rate tables: GLS domestic [1,2,3,5,8,10,15,20,25,31.5,40], GLS euro [1,2,5,10,15,20,25,30,40], **Maersk incl. sub-kg [0.25,0.5,0.75,1,1.25,…,2,3,…,10,15,20,25,30]**, UPS, DHL. Per-country (eligible carriers + breaks vary).
- **Contracts set the grid EDGES (completeness), not the thresholds.** Crossover values stay computed from the engine's repriced full cost (coalesce to incumbent `current_full` where a carrier is ineligible).
- **Completeness proven this session:** the union-grid scan returned €36,206 H1 ≈ the coarse 1kg grid's €36,197, and the raw unconstrained ceiling (€36,568) sits barely above the bookable plan → no hidden sub-kg or multi-crossovers. We have caught it all.

## ⚠ Artifact caution — do NOT trust / commit `per_lane_band_optimum.py` as-is
The on-disk-but-uncommitted `repricing_base/carrier_engines/per_lane_band_optimum.py` (+ `band_sizing/` outputs) has **two defects** that made its smoothed rung-3 read −€999 (i.e. it HID the DE prize):
1. **The borrowed EU-tender `max(25, 5% of lane)` floor.** On DE (548k parcels) 5% = 27,401 — a bar no DE weight band clears, so it absorbed the real €34.6k handoff as "noise." The %-of-lane floor breaks on a lane that's 90% of the book.
2. **A tie-break collapse.** At 31kg DHL=Maersk exactly (€8,296); `min()` broke the tie to incumbent, manufacturing a DHL→Maersk→DHL "return" that tripped the full-lane collapse fallback, discarding the prize.
**The trustworthy logic is the union-grid scan run inline this session** (recorded in the quest-log turn log), NOT the file's smoothing. The redo should build the validated logic fresh; treat the existing file as scratch.

## THE PLAN — redo the methodology + calculations at destination × weight-band grain
1. **✅ Completeness proof** — DONE this session (union-breakpoint grid; DE clean single threshold; nothing hidden).
2. **Canonical band-optimum engine** — build the union-grid (per-country) argmin + run-merge into the engine. Absolute parcel floor (value TBD), tie-break toward the heavier-weight neighbour, no packagetype axis (ORWO is dim-poor). Self-check rung-1 against €2,311,013. *Replaces the artifact file.*
3. **Band-grain routing report** — EU-tender ops style (`routing_report_ops_no_hermes.py` shell): destination × weight-band, "all weights" for the ~23 single-carrier lanes, DE split @10kg + FR @1kg shown explicitly.
4. **Per-band annual reweight** — extend `annual_2026/annual_orwo.py` to band grain → the real DE-heavy yearly number (resolves the €84k caveat). **⚠ COORDINATE: live sibling `jebrim-614ffdf6` (S286) is on `annual_orwo.py` — check comms before editing; don't clobber.**
5. **Update the presentation** — `methodology_walkthrough.html` (built S367) + headline = whole-country −€343k/yr + the DE-heavy band move (~€84k/yr indicative, pending step 4).

## Next concrete step (blocked on principal)
Before building step 2, lock three method choices:
- **Absolute floor value** — minimum parcels to introduce a mid-lane switch (25? higher for DE-domestic operational sanity?).
- **Tie-break rule** — toward the heavier-weight neighbour, or toward the switch-in carrier?
- **Scope** — DE-only (the €34.6k), or include FR's €1.5k footnote too?

## Files to read first (ordered)
- this resume + `quest-log/in-progress/S368_364d42cd_orwo-per-lane-band-grain-sizing.md`
- `bank/domains/eu-tender.md` (the EU-tender method digest); whole-country baseline note `bank/drafts/notes/projects/2026-06-19-orwo-tender-wolfen-spine-and-reprice-engine.md`
- `…/7_ORWO_tender_2026/repricing_base/carrier_engines/per_lane_optimum.py` (current whole-country) + `per_lane_band_optimum.py` (this session's scan — **with the artifact caveats above**)
- `…/carrier_engines/{gls,maersk}/rate_tables/*.parquet` (the breakpoints) + the two `switch_vs_baseline_*.parquet` (the per-parcel repriced cost)
- `…/2_EU_tender_2026/2_analysis/routing_investigation/ops_coherence/{triage_routing_rules,cost_check_smoothing}.py` (the EU coherence method) + `routing/no_hermes/routing_report_ops_no_hermes.py` (report shell)
- `…/7_ORWO_tender_2026/repricing_base/annual_2026/annual_orwo.py` (annualization to extend — **sibling-active**)

## Anchors
Parent ORWO umbrella [[S275_abfcf511_orwo-tender-contracts-coverage-weight-grain]]. Annualization S286 (sibling). Whole-country optimum = `per_lane_optimum.py`. All figures read READ-ONLY from the engine switch parquets, 2026-06-25.
