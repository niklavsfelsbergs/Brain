# S370 (sid8 0643e962) — UPS retention levers + truck-cost check + LPS treatment

EU tender, Jebrim. Returned to the UPS slice. Three threads this session, all read-only analysis off the EU-tender `2_analysis/` parquets + the live mart (Redshift MCP) + raw UPS invoices (silver). One NFE deliverable written.

## Thread 1 — UPS retention levers (Maersk-UK/Yodel-style)
Reframed the EU-tender question to its inverse: what discount keeps UPS's current volume vs the tender plan. Built the analysis off `cost_matrix_2026q1` + `routing_assignment` + `population_2026q1` (model-vs-model, no engine re-run — the matrix has a clean component split).
- Locked basis (principal): compete vs **tender plan**; discounts off **UPS offer** (ups-2.0.1); levers = base + negotiable surcharges; fuel/LPS/OML excluded; full current book; 2% incumbent cushion.
- Finding: gap to keep whole book = **€140,186/Q1 (+13.9%)**, but only **7% is UPS base** — 41% line-haul (OUR trucking), 38% fuel level (excluded), 13% ancillaries. CH = half the gap (~47% out, needs −50% base → lost to DHL on rate).
- **Deliverable shipped:** `bi-analytics-main/NFE/projects/2_EU_tender_2026/2_analysis/ups_retention_levers.md` (Yodel-structured; option menu + decomposition + line-haul/uneconomic-cuts reframes). Uncommitted in NFE.

## Thread 2 — UPS truck cost (Andrea tip → investigated → REVERTED)
Principal relayed Andrea: truck cost miscalculated, "1 UPS truck/day." Checked gold `fact_truck_charges`: UPS lane shows 119 truckload rows / 64 days (~1.86/day), flat €1,025/load, incl phantom loads (a 17-parcel "truckload" billed €1,025). Independently suggested the gold table over-counts. Andrea's corrected basis = €374/weekday → would drop truck €122k→€24k/Q1, line-haul €0.75→€0.15.
- **Then: Andrea corrected himself — the €374/day was about ORWO, not UPS EU tender.** UPS truck cost **stays as is** (€0.75/parcel, real_truck_eur untouched). No files changed. The retention deliverable (built on €0.75) stands unaffected.
- Parked (independent of Andrea): the gold `fact_truck_charges` UPS lane still shows odd shape (phantom small truckloads) — a possible gold-table grain quirk worth a separate look. Principal's call; no action.

## Thread 3 — UPS LPS engine treatment (deep dive, principal-led)
Explained exactly how the tender treats UPS LPS/oversize, then validated against actuals.
- **Engine adds LPS as an expected value:** per parcel, band it by OUR declared L+G (`length_plus_girth_cm`), look up historical incidence `p_lps` (from real UPS invoices, `extract_incidence.py`), `cost_lps = p_lps × (€101.80 + 40kg-minbill bump)` for billable bands; sub-300 LPS + over-max → `cost_oversize_disputed`. Both in the total. NOT triggered by our geometry (that'd be ~€0); NOT zero.
- **Billable cutoff = 300 cm** (`BILLABLE_LPS_BANDS = c_300_325/d_325_419/e_419plus`). The header explicitly calls 300–325 a "tolerance zone" filed as billable. **Principal's tip: real contractual LPS threshold may be 325, not 300** → the c_300_325 band would be mis-bucketed (should be disputable, not justified).
- **Gross vs net:** engine prices LPS at GROSS €101.80 × count-incidence (refunded shipments still counted; `extract_incidence` `has_lps` flags any charge line). Refunds ignored for LPS (only the over-max line uses observed net). Incumbent (keep) cost IS net of realized refunds. Asymmetry: incumbent LPS net, engine LPS gross.
- **Per-month Q1 LPS, same UPS book** (engine modeled vs incumbent actual): engine €81,296 / incumbent gross €94,291 / refund −€20,841 (22%, rising Jan 11%→Mar 43%) / **net-paid €73,451**. Engine sits between gross and net (~+11% vs net). The refund mechanism is alive and growing — contradicts the engine's "reversals collapsed Q4-2025" assumption. Opportunity = push the refund rate higher via the 325-threshold dispute, not a model fix.

## Decisions
- Retention basis locked (plan / offer / 2% cushion / full book); deliverable shipped.
- UPS truck cost UNCHANGED (Andrea's €374 was ORWO).
- LPS 300-vs-325 dispute = the live refund lever → handed to a next Jebrim session (prompt + numbers in the resume).

## Post-close continuation (same session, after first wrap)
Principal reopened to scope the next-session base-rate work.
- **Outflow finding (the headline):** from `final_stats.json` `flows` (do-nothing basis), **61% of the €976k plan saving = €595,363/yr comes from moving ~376k parcels/yr (80k Q1) OFF UPS** — Maersk €298,072 (30.5%) · DHL €176,972 (18.1%) · DPD €83,315 (8.5%) · Hermes €38,984 · DBS −€1,978. Plus UPS kept-on-UPS offer saving €158,936 (16%) → UPS-related ≈ 77% of the whole plan. De-UPS-ing IS the tender.
- **Per-country "how far off" preview** (Q1/matrix, shed parcels, avg UPS vs avg plan): CH 48% off (15.62 vs 8.08) · ES 30% · IT 15% · DE 9% · AT 30% · PT 49%. DE+IT cheap to keep, CH the outlier.
- **Next-session scope locked:** UPS base-rate retention, **RETAIN ONLY**; lever = base rates only (fuel/LPS/OML/line-haul out). First output = the per-country table (do-nothing basis, annualized, w/ avg UPS vs avg plan + gap), **then stop and discuss** — not a solo report. Full brief in the resume.
- **LPS 300-vs-325 dispute thread DROPPED** (principal). LPS engine-treatment knowledge stays as reference (bank draft + above); no dispute follow-up.

## Pending external actions
None pending. (NFE deliverable written but uncommitted in its repo — flagged to principal.)
