# UPS residential + peak-surge invoice mechanics ([[S206_01871b26_ups-2.0.0-engine-build|S206]] calibration findings)

**As of:** 2026-06-11. **Session:** [[S206_01871b26_ups-2.0.0-engine-build|S206]] (01871b26). **Player:** Jebrim. **Status:** draft (invoice-verified, principal-accepted into ups-2.0.1).

## Residential ("Privatzustellung", code RES)

- €0.40/shipment, billed as its own charge line on the regular freight invoices (327-series); English mart label "Residential Delivery"; reversals appear as −0.40 on 2003-series adjustment invoices (refund-in-place, same mechanic as oversize).
- **Incidence ≈ 46.3% of parcels** (Q1-2026 PCS PL switch book, counted on residential-bucket lines > 0), NOT all parcels — UPS classifies the rest as business/pickup-point addresses. Mart-wide 2026 (invoice-date, `ups` stream): 43.3%; `ups_orwo` only 16.2%. Niklavs' report showed ~38% (window/dedup gap, same animal).
- **Divisor trap (the retracted 64%):** dividing the residential bucket EUR by 0.40 overstates incidence — the avg per *charged* shipment is €0.551 in Q1 because the bucket also carries surge amounts. Count lines, don't derive counts from euros.

## Peak Residential Surge ("Surge Fee - Privatkunde", code PFR)

- **Residential-gated, not per-package:** in the 2025-26 peak window 195,107 shipments carried PFR vs 193,843 with RES — 96% overlap. The published "€0.20 Base Rate Surcharge per package" framing is wrong for our billing; UPS's reply ("Residential Surge Fee, ~€0.20 last year") was the right component but a round-down.
- **Weekly-escalating rate**, line amounts 0.04 / 0.07 / 0.11 / 0.15 / 0.19 / 0.22 / 0.25+ with €0.25 modal at peak; **volume-weighted ~€0.29 per residential parcel** (€56,949 total last peak).
- No forward schedule from UPS ("no visibility before next peak") → 2026-27 modeled on the 2025-26 observed pattern, documented assumption.

## Engine treatment (ups-2.0.1, principal-approved)

Expected-cost, same BY-BILL philosophy as the oversize layer: residential = 0.40 × 0.463 per parcel; peak surge = 0.29 × 0.463 in-window (rides `ups_peak_if_in_window_eur` for the annualization; Q1 replay carries €0 peak by the locked full-year-only decision). Gate effect: residential bucket prices 0.73× the Q1 actual — correct, the actual carries Jan-window surge the model prices in the peak layer (no double-count).

## Related

- [[2026-06-11-ups-invoice-charge-profile]] — the 12-mo charge structure this drills into.
- [[2026-06-11-ups-oml-lps-negotiated-thresholds]] — the oversize sibling (S199 dimensioner).
- Engine: `bi-analytics-main/NFE/projects/2_EU_tender_2026/1_offers/picanova/UPS/calculation/` (findings.md §5).
