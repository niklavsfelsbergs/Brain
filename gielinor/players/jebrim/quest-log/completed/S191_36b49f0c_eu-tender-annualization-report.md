# S191 — EU Tender 2026 annualization report (the 4th report)

**Player:** Jebrim · **sid8:** 36b49f0c · **Opened:** 2026-06-10 · continuation of [[S190_9a064d86_eu-tender-red-team-audit-and-report-rebuild|S190]]'s open dep (annualization build).

## Ask
Build the full-year-2026 annualization report (the 4th EU-tender report) per the locked plan
(`research/2026-06-10-eu-tender-annualization-method-and-assumptions.md` + the [[S190_9a064d86_eu-tender-red-team-audit-and-report-rebuild|S190]] resume). Build it
in bi-analytics `2_analysis/annual_2026/`, parallel to `routing_2026q1/`, matching that report's quality.

## What was built
Four scripts + outputs in bi-analytics `2_analysis/annual_2026/` (SEPARATE repo, principal-gated, UNCOMMITTED):
1. `q1_base.py` → `q1_base.parquet` — replicates `routing_2026q1/build_final.py` routing EXACTLY, emits the
   per-parcel frame (dest, cur_inc, rcarrier, today_eur, rcost). **Reconciles to the cent** vs the committed
   routing_stats.json: today €2,955,020 / routed €2,679,536 / saving €275,484 / 9.32% / 531,194 parcels.
2. `aggregates_2025.py` → `aggregates_2025.json` — from the 12-month 2025 cost matrix: per-country seasonal
   ratios (FY/Q1, 3.16 FI .. 6.69 CH), peak-window fractions (Oct-Dec / Nov-Dec / PiP Nov24-Dec7), global
   monthly shape (Q1 20.7% · Q4 40.1% · Dec 21.5% — matches plan anchors), invoiced-carrier Q4 peak premium.
3. `build_annual.py` → `annual_stats.json` — cost both sides = peak-free base × annual vol + peak × peak-window
   vol; fixed routing (no re-route); fuel-rate band; the Q1→annual bridge; the two-tier firm/contingent split.
4. `annual_report.py` → `annual_report.html` (39 KB) — reuses the routing report's dark shell. SVG bridge
   waterfall (centerpiece), monthly volume/cost curve, peak-exposure exhibit, two-tier saving, by-destination
   (firm/contingent columns), methodology, full Part-B assumptions ledger.

## Headline
- **Firm annual saving €535,365 / 3.7%** (bankable: DHL/DPD validated engines + UPS actuals) — the headline floor.
- **+ €806,361 DB Schenker reroute — CONTINGENT** on the open package-setup investigation + Maersk-EU/Hermes
  engine validation.
- = up to **€1,341,726 / 9.19%** point, band **€1.31M–€1.37M**, on **€14.59M** do-nothing / **2.57M** parcels.
- Bridge: Q1 €275,484 → +€1,046,455 per-country volume scale → peak-free €1,321,939 → +€19,787 peak
  differential → €1,341,726 → ±€30,111 fuel band.

## Decisions made in-flight
- **Reconstruct-and-reconcile** the Q1 base rather than re-solve or modify build_final — replicated its routing,
  asserted reconciliation to the committed €275,484 before building on top. Trustworthy anchor.
- **Invoiced peak premium from real_total_eur, not real_peak_eur** — the latter is undecomposed for invoiced
  carriers (UPS €6.6k FY, DBS/residual €0). Used the plan's stated method: Q4-vs-non-Q4 real_total_eur uplift.
  UPS robust **median €0.27/parcel** (mean €1.05 is Q4-mix-contaminated). DBS €0 (Q4 uplift negative — freight).
  Direct-Link €0 (2025 "residual" = gone-carrier soup, GLS/Colis-Privé — not a clean 2026 signal).
- **Peak per-carrier on both sides** (carrier's own schedule) → largely cancels in the saving; net +€19,787
  from shedding UPS Q4 volume onto no-peak DPD-PL.
- **Seasonal proxy = order date** (ship date unavailable). Noted in-report.

## Principal-directed refinement rounds (presentation)
1. De-weight DB Schenker → **two-tier headline**: firm floor leads, DB Schenker reroute gated. (chose via
   AskUserQuestion; firm €535k / contingent €806k / total €1.34M.)
2. Standalone report → **explain what the DB Schenker reroute is** (freight ~€53 → parcel ~€7–14) in §04.
3. Also explain it in the **headline KPI card** + the **summary bullet** (all from the same computed figures).
4. **By-destination table** → split into firm + DB Schenker + total columns (reveals DE 81% contingent, CH/FR
   mostly firm).
5. **Color** → DB Schenker contingent yellow read as "important"; switched to muted gray (#8b939e) to downplay.

## Pending external actions
None pending. (bi-analytics is uncommitted by principal gate — not a pending *action*, a held decision.)

## Cascade.
None — the annualization is a new standalone report; it does not edit the docs/ canonical or per-carrier
status tables. If the annual number is later promoted into the management deck / docs, that cascade runs then.

## Main-brain changes.
None — this is repo deliverable work; no gielinor meta/ritual/hook changes.

## Turn log
- Read the spec + [[S190_9a064d86_eu-tender-red-team-audit-and-report-rebuild|S190]] resume + routing report shell; profiled the 2025 + Q1 matrices.
- Built q1_base (reconciled), aggregates_2025, build_annual, annual_report. All ties asserted in-code.
- 5 principal-directed presentation refinements (above). Each re-rendered + re-verified ties.
- Niklavs: "good for now, wrap up."
