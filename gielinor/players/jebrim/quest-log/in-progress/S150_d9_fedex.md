# [[S150_e59202cf_carrier-overview-report-design|S150]] d9 — FedEx section, Carrier Overview Report

Dwarf d9 for Jebrim. Building `2_analysis/carrier_overview/sections/fedex.md`.
Carrier slug `fedex`, label FedEx, badge firm (engine fedex-2.0.0).

## Steps
- [x] Read PLAN.md §3+§4, fedex constants + engine doc, REVIEW_CONCLUSIONS + ASSUMPTIONS
- [x] Run cost_slices (lane_position/profile_position/cheapest_share/baseline/envelope/pop)
- [x] Write fedex.md (7 §4 elements) — done, all 7 elements
- [x] Return summary

## DONE. Section written: 2_analysis/carrier_overview/sections/fedex.md

## Findings
**Cost position (full-year vol-wtd €/parcel, rank among contenders):**
- FedEx is a contender on ALL 9 lanes (highest coverage on every lane — prices ~2.87M, broadest eligibility) but NEVER within the 10% band of the lane cheapest. Rank: DE 6/6, FR 5/6, Benelux 6/7, AT 8/9, IT 6/7, Iberia 6/7, CH 6/8, Nordics 6/7, ROW 7/7.
- ROW: FedEx €51.52 (q1 €54.42), 80.8% cov — LAST. DHL Paket WINS ROW (€28.09, cheapest, 95.5% cov). So FedEx is NOT the ROW cheapest; it's the premium ROW option. Its real edge = breadth (prices nearly everything; broadest single-engine coverage), not price.
- EU economy off-pace confirmed: DE €10.69 vs Hermes €4.16 (winner); IT €13.80 vs Maersk €6.21; CH €23.54 vs Austrian Post €8.66.
- cheapest_share: FedEx is count-cheapest on FR 163,663 parcels (the light-compact tail where IE/RE base undercuts), Nordics 22,884, IT 20,769, ROW 15,955 — so it wins specific compact sub-segments even where vol-wtd avg loses.

**Native cliffs (computed from population.parquet, exact constants):**
- vol÷5000 bites HARD: chargeable>actual on 96.23% of book; median chargeable/actual = 2.21×. FedEx bills the box.
- AHS-Dim trigger fires 7.41% (driven by L+girth≥266 = 7.4%; 2nd-side≥76 = 5.69%; longest≥121 = 1.48%; vol≥169901 = 0.7%).
- Oversize (243/330/283168/50kg) = 0.60%; AHS-weight (gross>25) = 0.06%; parcel reject (>274 / L+girth>419) = 0.22%.
- Clean (no AHS-Dim/oversize/ahs-wt) = 92.58%. Freight (>68kg chargeable) = 5,425 parcels.

**Levers (REVIEW_CONCLUSIONS Round-2):**
- Customs lane scope: CH-only (€0 on DAP, bundled). NO/GB/LI/IS held — extending a guessed per-parcel fee to high-vol GB swings headline; principal call.
- Fuel basis: Q1-flat (Regional 20.5% RE/REF, Intl 34.5% IE/IEF) vs monthly/forward (parked annualisation). Fuel = 5.99M/yr (~17% of 34.47M).
- ODA: Tier A/B/C wired by shipping_zipcode; remote = 1.19M/yr.
- FedEx FY2025 = €34.47M @ 99.6% cov; add_fedex = -€1.63M (net cost, prices as premium).

**Incumbent baseline (overlap):** ROW UPS €23.88 / APG €11.54; CH UPS €9.66; DE UPS €5.64, DB Schenker €39.70 (freight).
**Confidence:** firm (fedex-2.0.0). Residuals: Jan/Feb Intl fuel reconstructed→pulled; GB ODA outward-code matcher (near-zero); customs NO/GB scope held; year-1 only.
