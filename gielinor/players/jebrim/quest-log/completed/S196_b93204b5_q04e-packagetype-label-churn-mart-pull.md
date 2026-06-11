# S196 (b93204b5) — q04e label-churn mart pull (shipping-agent sub-agent)

**Asked:** EU-tender side-investigation — packagetype label history from gold shipping_mart on SHIP-date grain. PCS PL site. 4 deliverables: monthly counts per label 2024-01..latest; daily counts in two cutover windows; dim tuples per label by month 2025-11..latest + ORWO_80x60 birth; contradictions vs order-date story.
**Scope:** vertical/origin pre-resolved by brief — PCS PL production site, labels in WICKEL/ORWO/STANZ 120x9/120x8/Plattenverpackung families. Volume/dims only, no cost.
**Tier:** gold contract (shipping_mart.fact_shipments only).

## Turn log
- Probing production_site values + label inventory.
- Site = 'PCS PL' (bare 'PL' has 10 rows in these families — excluded). Ship-date grain = received_by_carrier_date; NULL share ~1-2% from Nov 2025 (reliable for cutovers), 7-22% in 2024 (monthly undercount), Jun 2026 partial (data to ~Jun 10).
- Monthly matrix + both daily cutover windows pulled. Carrier-side cutovers: WICKEL AE→ORWO_80x60 = Mon 2026-02-23 (order-date Feb 18 + weekend); STANZ 120x90→120x80 ramp = 2026-02-02..04 (order-date Jan 28 + weekend).
- Dims: AE 86.5x63x4.3 stable to death; ORWO 91x62x4.5 stable; S120x90 120.5x90.5x5 stable incl. post-cutover; S120x80 120x80x5 EXCEPT Dec-Jan dormancy where 122.5x81.5x5.5 dominated (466/534 in Jan), gone by Mar.
- Contradictions found: ORWO_80x60 born 2025-07-24 (not Jan 2026); STANZ story is a REVERSION (120x80 was dominant for years, 120x90 took over only Dec'25-Jan'26); plain WICKEL 80x60 label resurrected 2026-05-12 on a new 90.3x60.5x9 box; siblings missed by brief: PIZZA 120x90 [x2], WICKELVERPACKUNG_90x60, STANZ 120x80 (2stk. strapped).
- HEADLINE: carrier-side switch dates 2026-02-23 (WICKEL→ORWO) and 2026-02-02..04 (STANZ 90→80); both labels' surviving dims stable at cutover. Reported to principal; deliverable chat-only.
- Addendum (separate agent run): +3 labels to monthly table — GEL, zugeschnittene/Zugeschnittene Verpackung, 2024-01→2026-06, PCS PL site, order-date grain. All three persist through 2026-06. GEL did NOT stop: weekly check shows ~70-80/wk steady through late March → May 2026 (no 60/wk→0 collapse on this scope). Both casing variants persist post-Q1. Contradiction with the Q1 order-date extract flagged to principal.
