# Dwarf trace — SIGN-OFF reconciliation: EU-tender routing report

**Player:** Jebrim (dwarf) · **Date:** 2026-06-09 · **Mode:** read-only sign-off (no report edits)
**Target:** `routing_2026q1/routing_report.html` (+ `.py` + `carrier_envelopes.py`)
**Ground truth:** `routing_stats.json`, `routing_assignment.parquet` (531,194 rows; cols: shipment_id, destination_country_code, packagetype, weight_kg, volume_cm3, chg_kg, d_max/mid/min, family, service), `routing_rules.csv` (1,968 rules; carrier/service/parcels/cost).

## Method
Extracted every quantitative/factual claim from rendered HTML prose + KPI strip + cards + tables + the `.py`/`envelopes.json` generators. Recomputed each against stats/parquet/rules via polars (PYTHONIOENCODING=utf-8). Note: parquet has NO per-parcel cost and NO from-carrier column — migration "from" totals recomputed from `routing_stats.json["migration"]`; €/parcel from rules.csv.

## Claims checked — all MATCH except as noted

### Headline / KPI
- saving €377,471 / 12.8% (12.77% rounded) — MATCH (stats saving 377471.107, saving_pct 12.774)
- today_total €2,955,020 — MATCH · routed €2,577,549 — MATCH · floor €2,475,020 — MATCH · op_gap €102,529 — MATCH
- 531,194 parcels — MATCH · 1,968 rules / 1,886 std rules / 82 by-dims — MATCH (n_rules 1968, n_std_rules 1886, 1968−1886=82) · 165 must-freight / 0.03% — MATCH (0.0311%)

### Portfolio cards (actual routing) — all MATCH
- dhl_paket 282,638 / €961,039 / €3.40 · dpd_pl 88,985 / €438,734 / €4.93 · hermes 68,191 / €368,156 / €5.40 · maersk 60,523 / €395,758 / €6.54 · ups 29,781 / €311,970 / €10.48 · db_schenker 1,076 / €101,892 / €94.70 — all MATCH (rules parcels-per-carrier reproduce stats portfolio exactly).

### DPD-PL three-bucket service split (card chips) — MATCH
- Dpd Direct Home 80,583 / Dpd Mix Home 6,515 / carrier-only 1,887 — MATCH (rules.csv group_by service on dpd_pl: dpd_direct_home 80583, dpd_mix_home 6515, null 1887). Sums to 88,985.

### Maersk service split — MATCH
- EU Home Delivery 43,370 / carrier-only 16,085 / ROW Home Delivery 1,068 — MATCH. Sums to 60,523.

### FR caveat numbers — MATCH
- FR → DPD-PL 20,814 (largest on lane) — MATCH (parquet FR by family: dpd_pl 20814 > maersk 16085 > ups 12244 > db 695 > hermes 123 > dhl 29; FR total 49,990 — MATCH by_dest).
- Maersk-FR €4.72 kept, DPD FR engine ~€5.3–5.9, Chronopost actual €4.37 — narrative anchors, not recomputable from supplied ground truth (no FR cost in parquet); arithmetic self-consistent.

### by_dest savings table — MATCH (spot-recomputed all 17)
- IT €41,806 / 20.6% · NL €25,315 / 12.7% · FR €10,077 / 2.8% · AT €40,708 / 26.7% · ES €50,507 / 36.2% · SE −€6,403 / −8.3% (negative, flagged red in report) — all MATCH.

### Migration / narrative
- UPS sheds ~119k of 149k — MATCH (UPS from-total 149,041; stays 29,760; migrate-away 119,281).
- DB Schenker 8,951 → ~1,076; ~7,875 switch out — MATCH (8,951−1,076=7,875).
- DB breakdown 165 must-freight + ~591 freight-cheapest + ~320 consolidation = 1,076 — MATCH (165+591+320=1,076).
- France effect: FR 119 / CH 11 / SE 24 must-freight — MATCH (envelope_by_destination: FR 119, SE 24, CH 11).
- DPD "~27.6k cross-carrier volume engine can price but actuals never could" — MATCH (inflow into dpd_pl from non-dpd origins = 27,629).

### Not recomputable from supplied ground truth (NOT drift — flagged as unverifiable here)
- GRI figures: +5% GRI, €38.9k avoided of €56.5k full-book, +€17.3k engine / −€17.6k GRI absorbed. No GRI/baseline cost columns in stats/parquet/rules. Internally arithmetically plausible; would need build_final.py / invoice basis to verify.

## DRIFT / ISSUES FOUND

### DRIFT-1 (caveat wording) — "81 over-33kg" is wrong
- Report (DPD card) implies carrier-only 1,887 = PL-domestic + an over-33kg tail. Brief's caveat (b) states 1,887 = 1,806 unmodeled PL-domestic + 81 **over-33kg** held at actuals.
- TRUTH (parquet, dpd_pl & service is null): 1,887 total; by dest PL=1,806, NL=52, BE=11, LU=8, SE=8, AT=2. The 81 non-PL parcels are NOT over 33 kg — **0 parcels in the carrier-only set exceed 33 kg** (floor(weight_kg)>33 → 0; >33 → 0; ≥33 → 0). The 81 = the non-PL remainder (1,887−1,806), not a weight tail.
- So the "1,806 PL-domestic + 81 over-33kg" decomposition is **factually wrong on the 81** (the count 81 is right; its *characterisation as over-33kg* is wrong). AND see CAVEAT-2: the report doesn't actually state this decomposition at all.

### INCONSISTENCY-1 (presentation) — Section 03 totals ≠ portfolio totals
- "What each carrier takes" (smoothed overview, from envelopes.json) shows: DHL 278,347 · DPD-PL 92,212 · Hermes 81,901 · Maersk 55,981 · UPS 22,189 · DB 564 (sum 531,194).
- Portfolio cards (actual routing) show: DHL 282,638 · DPD 88,985 · Hermes 68,191 · Maersk 60,523 · UPS 29,781 · DB 1,076.
- Same carriers carry two different parcel totals in the same report (e.g. Hermes 68,191 vs 81,901; Maersk 60,523 vs 55,981; UPS 29,781 vs 22,189). By-design (overview groups by dominant-cell family + contiguity smoothing, a different basis than per-parcel routing), and each is locally labelled, but a reader gets two "Hermes parcel counts" with no reconciliation note. parcels_moved=4,020 does NOT explain the ~14k Hermes gap — different aggregation basis. Worth a one-line "(smoothed dominant-cell view; differs from routed totals)" disclaimer. Judgment call, not a data error.

## CAVEAT CHECKS
- (a) FR-floor caveat — **PRESENT.** Section 08 callout "France — DPD-PL now wins it, conservatively": "The engine prices FR at a conservative ~€5.3–5.9/parcel against DPD's own FR Chronopost actuals of €4.37 — it over-prices FR, so the FR portion of the saving is a floor (correcting it would only raise the saving)." Clear and correct.
- (b) carrier-only / PL-domestic caveat — **ABSENT.** No text "PL-domestic", "PL domestic", "unmodeled", "held at actuals", "over-33", "over 33", "33 kg", "domestic" anywhere in the report. The 1,887 appears only as a bare "carrier-only" service chip with no explanation of what those parcels are or why they're held at actuals. The caveat the brief expects is not in the report.

## BOTTOM LINE
Numerically the report is clean — every recomputable headline/portfolio/split/by-dest/migration figure MATCHES ground truth (incl. the DPD 80,583/6,515/1,887 and Maersk 43,370/16,085/1,068 splits). Two issues: (1) caveat (b) is ABSENT, and the "81 over-33kg" framing it would carry is factually wrong (those 81 are non-PL remainder, 0 are >33kg); (2) one by-design presentation inconsistency (Section 03 smoothed totals vs portfolio totals, unlabelled). FR-floor caveat (a) is present and correct.
