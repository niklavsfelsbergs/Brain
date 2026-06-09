# [[S150_e59202cf_carrier-overview-report-design|S150]] d3 — DHL Express section (Carrier Overview Report)

Dwarf d3 for Jebrim. Building `2_analysis/carrier_overview/sections/dhl_express.md`.
Carrier slug `dhl_express`; label "DHL Express"; badge **firm**; premium/express network.

## Progress
- [x] Read PLAN.md §3/§4 + decisions
- [x] Read constants.py + engine doc (dhl_express.md)
- [x] Read REVIEW_CONCLUSIONS.md + ASSUMPTIONS DHL Express block
- [x] Run cost_slices (lane_position, profile_position, cheapest_share_lane, + cross-carrier baselines)
- [x] Write section (7 §4 elements) → `sections/dhl_express.md`

## DONE
Section written. All 7 §4 elements covered. Badge firm. Numbers all from cost_slices lib (single source of truth), coverage near-complete (≥99.7%) on the 8 bid lanes so no per-number coverage caveat needed; DE rejection called out as structural.

### Cost-position findings (slices)
- **8 lanes priced, DE absent** (rejected country_not_served — the DHL Paket lane, 66.7% of book). Coverage on the 8 it does bid: all 99.7-99.9% (near-complete).
- **Never the vol-weighted cheapest, never within-10% band on ANY lane.** Ranks: CH 5/8, FR 6/6, ROW 6/8, Benelux 7/7, IT 7/7, Iberia 7/7, Nordics 7/7, AT 9/9 (last).
- BUT count-of-cheapest on a parcel slice per lane: FR 8,931; Benelux 4,571; CH 2,909; ROW 1,349; Nordics 1,141; AT 1. Premium network wins specific heavy/remote parcels even where it loses the average.
- €/parcel (full-yr vol-wtd) vs cheapest: AT 14.72 (Güll 4.33); Benelux 14.37 (DPD 5.36); FR 15.47 (GLS 8.11); IT 19.93 (Maersk 6.21); Iberia 21.51 (Maersk 5.60); CH 20.15 (AP 8.66); Nordics 23.74 (DPD 10.15); ROW 45.83 (DHL Paket 28.09).
- **ROW is the structural story:** DHL Express has 99.9% coverage on ROW where economy carriers thin out (DPD 7.3%, Hermes 25.9%, GLS 25.7% — all non-contenders). Only DHL Paket (95.5%, €28.09), Maersk (93.2%, €35.36), FedEx (80.8%, €51.52) and DHL Express (99.9%, €45.83) are contenders. DHL Express beats FedEx on ROW avg AND coverage; loses to DHL Paket + Maersk on price.
- Total engine spend across 8 lanes ≈ €16.17M (FR 4.60M, Benelux 2.82M, IT 2.26M, AT 2.06M, ROW 1.64M, Iberia 1.49M, Nordics 1.20M, CH 1.08M).
- **Incumbent baselines (UPS/DB Schenker):** CH UPS €9.66 (53,399 — vs DHLx 20.15); ROW UPS €23.88; DB Schenker = freight tier (CH €248, FR €95, DE €40) — not parcel-comparable. DHLx off-pace vs every parcel incumbent.
- Levers (REVIEW_CONCLUSIONS): pickup line-haul days/week confirm (denominator); Demand magnitude/zone-mapping confirm; DTP incoterm confirm. None are big €-flips — DHLx is structurally premium, not mis-priced. Cost moves UP on the levers resolving, not down. Volume-tier OUT of scope.

## Findings (streaming)
### Engine facts (from constants + doc)
- Two services: express_worldwide (TDI air, ~220 countries/11 zones), economy_select (DDI road, ~37 EU/6 zones). HD only, no PUDO.
- **DE rejects `country_not_served`** — Germany on neither zoning sheet → ~344k DE parcels (65% of book) reject. This is the DHL Paket lane. Structural.
- Vol-weight divisor 5000 (÷5000, bills the box) — both services. MAX_WEIGHT 70kg, MAX_LONGEST_SIDE 300cm.
- Full-year eligible: 956,968 parcels (33.3% of 2,875,235). ~957k matches brief.
- Fuel two-phase: TDI air ~30% / DDI road ~18%, per-ISO-week; uplifts base + listed surcharges (Q3). Road = ~86% of eligible vol.
- Surcharges: Oversize 10 intl/6 dom (d_max>100 OR d_mid>80); Non-conveyable 20/12 (actual 25-70kg); Demand per-kg (Oct1-Feb16 window); Remote Area 0.50/kg min 24 EUR; Overweight never fires (70kg cap); customs 0 (Q7), residential 0, emergency 0.
- Pickup line-haul: flat ~0.414/parcel adder (full-year basis), excluded from fuel base.
