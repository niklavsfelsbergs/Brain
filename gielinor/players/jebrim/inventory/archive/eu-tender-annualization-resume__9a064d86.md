---
quest: S190_eu-tender-red-team-audit-and-report-rebuild (annualization continuation, sid8 36b49f0c)
sid8: 9a064d86
ts: 2026-06-10 ~15:55
open_dep: annual report BUILT — awaiting principal review + commit decision (bi-analytics uncommitted)
---

# Resume — EU-tender annualization (the 4th report)

## Status
**BUILT — awaiting review.** The 4th report (full-year 2026 annualization) is built in
bi-analytics `2_analysis/annual_2026/`, parallel to `routing_2026q1/`, per the locked plan.
All numbers reconcile + tie end-to-end. **bi-analytics is UNCOMMITTED** (separate repo,
principal-gated, never push).

## Headline (TWO-TIER — principal-directed reframe to de-weight DB Schenker)
- **FIRM annual saving €535,365 / 3.7%** — bankable now (DHL/DPD validated engines + UPS actuals;
  routing that does NOT touch the DB Schenker question). **This is the headline floor.**
- **+ DB Schenker reroute €806,361 — CONTINGENT** on (1) the open DB Schenker package-setup
  investigation (can those freight parcels leave freight, or are they must-freight?) and (2) the
  unvalidated Maersk-EU/Hermes engines. **Gated upside, not banked.**
- = up to **€1,341,726 / 9.19%** point, band **€1.31M–€1.37M** (8.99%–9.40%), on **€14.59M**
  do-nothing spend / **2,573,333** full-year parcels.
- Bridge (Q1→annual): Q1 €275,484 → **+€1,046,455** per-country volume scale → peak-free €1,321,939 →
  **+€19,787** peak differential → **€1,341,726** point → **±€30,111** fuel band (Hermes/Maersk-EU ±2pp).
- KPI strip + summary + §04 (now "two-tier saving — firm floor vs DB Schenker contingent", with a
  firm/contingent stacked bar) all lead with the firm floor. saving_split: DBS reroute 61% of saving,
  84.9% lands on Maersk+Hermes.

## What was built (annual_2026/)
1. `q1_base.py` → `q1_base.parquet` — replicates build_final.py routing EXACTLY, emits per-parcel
   (dest, cur_inc, rcarrier, today_eur, rcost). **Reconciles to the cent**: today €2,955,020 / routed
   €2,679,536 / saving €275,484 / 9.32% / 531,194 parcels.
2. `aggregates_2025.py` → `aggregates_2025.json` — from the 12-month 2025 matrix: per-country
   seasonal ratios (FY/Q1, divergent 3.16 FI .. 6.69 CH), peak-window fractions (Oct-Dec / Nov-Dec /
   PiP Nov24-Dec7), global monthly shape (Q1 20.7% · Q4 40.1% · Dec 21.5% — matches plan anchors),
   invoiced peak premium (UPS Q4 real_total_eur uplift €0.27/parcel robust median; DBS/Direct-Link €0).
3. `build_annual.py` → `annual_stats.json` — cost both sides = peak-free base × annual vol + peak ×
   peak-window vol; fixed routing; saving band; the Q1→annual bridge. All ties asserted in-code.
4. `annual_report.py` → `annual_report.html` (34 KB) — reuses the routing report's dark shell.
   Centerpiece = SVG bridge waterfall. + monthly volume/cost curve (Q4 spike), peak-exposure exhibit,
   annual saving_split, do-nothing-vs-tender, by-destination, methodology, full Part-B assumptions ledger.

## Key modelling decisions made this session (defensible, documented in-report)
- `real_peak_eur` is NOT decomposed for invoiced carriers (UPS €6.6k FY, DBS/residual €0) → used the
  plan's stated method: Q4 vs non-Q4 **real_total_eur** uplift. UPS robust **median €0.27** (mean €1.05
  is Q4-mix-contaminated). DBS Q4 uplift negative → €0 (freight, no parcel peak). Direct-Link €0 (2025
  "residual" is gone-carrier soup — GLS/Colis-Privé — not a clean 2026 Direct-Link signal).
- Peak applied per-carrier on BOTH sides (carrier's own schedule) → largely cancels in the saving; net
  +€19,787 from shedding UPS Q4 volume onto no-peak DPD-PL.
- Fuel band = portfolio-side only (Hermes/Maersk-EU are new-offer/engine; FR + baseline are actuals).
- Seasonal proxy = order date (shop_order_created_date); ship date unavailable. Noted in-report.

## Next concrete step
Niklavs reviews `annual_2026/annual_report.html` (open in browser — visual layout unverified by me,
no GUI eyeball). On his go: commit bi-analytics `2_analysis/annual_2026/` (pathspec-scoped, never push).
Then optionally cascade docs/ + the management deck (deferred until Maersk girth confirmed per S189).

## Watch-outs
- bi-analytics SEPARATE repo — pathspec-scoped commits only, principal-gated, never push.
- A0 (Maersk MAERSKUK scope) still unconfirmed — flagged in the report caveats; doesn't distort the
  directional result but the Maersk EU lever rests on scope being FR+EU not UK.
- Q4 product-mix NOT modelled (locked) — qualitative caveat only; hits both sides, ~cancels in saving.
