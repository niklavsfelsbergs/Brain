# S034 F4 — Refresh bias_table.md for 9-engine cost matrix

**Spawned:** 2026-05-22 by Jebrim (principal) for S034 EU tender remediation, fix F4.
**Dwarf scope:** refresh bias ratios + doc for the 9 engines now in `cost_matrix.parquet` (maersk, dhl_paket, dhl_express, gls, guell, austrian_post, hermes, dpd_pl, fedex).

## Output

- **Script:** `bi-analytics-main/NFE/projects/2_EU_tender_2026/2_analysis/_refresh_bias_table.py`
  Standalone, reads cost_matrix.parquet, applies `apply_invoice_adjustments()`, computes both full-eligibility and winning-slice ratios per engine, writes markdown table + `data/_bias_refresh.parquet`.
- **Doc:** `bi-analytics-main/NFE/projects/2_EU_tender_2026/2_analysis/docs/bias_table.md`
  Overwritten with 2026-05-22 refresh. Header timestamp updated to `Last refreshed: 2026-05-22 (S034 F4)`. Methodology preserved verbatim from 2026-05-15 version with the additions called out below.

## Methodology decisions

1. **Two slices per engine.**
   - **Full-eligibility slice** for all 9 engines: every shipment the engine deems eligible with non-null `cost_total_eur` and positive `real_total_eur`.
   - **Winning slice** for the 7 SCORER_ENGINES only (maersk, dhl_paket, dhl_express, gls, guell, austrian_post, hermes): argmin engine across that pool per shipment.
2. **DPD PL + FedEx limitation handled explicitly.** Per D7 audit finding, neither is in `_decision_sets.CARRIERS` as NEW_OFFER-capable:
   - DPD PL: `allowed_states={INCUMBENT, OFF}` only (being retired).
   - FedEx: absent from CARRIERS entirely (new entrant 2026-05-20).
   So neither competes for any of the 528,397 winning slots. The doc reports their **full-eligibility ratio only** and flags the limitation in a dedicated section + "Open work" list.
3. **Volume-weighted ratio.** `sum(engine cost) / sum(real)` on the slice. Same as the 2026-05-15 methodology.
4. **OML/LPS adjustment applied before ratio.** Same as before -- consistent with `decision_scorer.py` baseline.

## Refreshed top 9 bias ratios

### Winning-slice (7-engine REC portfolio)

| Carrier | Ratio | Reading |
|---|---:|---|
| Hermes | **0.588** | engine = 59% of invoice (flagged, Q1-Q10 pending) |
| Austrian Post | **0.701** | 70% of invoice (fresh-bid undercut) |
| Güll | **0.750** | 75% of invoice (fresh-bid undercut) |
| Maersk | **0.849** | 85% of invoice (stable) |
| DHL Paket | **1.020** | 102% -- near parity |
| GLS | **1.276** | 128% -- saving understated |
| DHL Express | **1.956** | 196% -- small denominator (420 parcels, residual after Hermes) |
| **Portfolio** | **0.889** | 89% collectively (Hermes-dominated) |

### Full-eligibility-slice (only frame available for DPD PL + FedEx)

| Carrier | Ratio | Reading |
|---|---:|---|
| **DPD PL** | **2.957** | engine = 296% of invoice -- not a credible NEW_OFFER bidder |
| **FedEx** | **1.732** | engine = 173% -- tail-bidder candidate, not headline |

## Top 3 surprises

1. **DPD PL at 2.957 full-eligibility.** New observation, loudest signal in the refresh. Strongly supports the existing retire-DPD-PL stance -- their new-offer rate card is ~3x invoice on the slice their engine prices.
2. **The 7-engine winning-slice picture is byte-for-byte identical to 2026-05-15.** Maersk 0.849, DHL Paket 1.020, DHL Express 1.956, GLS 1.276, Güll 0.750, AP 0.701, Hermes 0.588, Portfolio 0.889. DPD PL and FedEx take zero winning slots because they're not in the scorer's NEW_OFFER pool. The §B.13 decision-set headlines remain valid without re-running the scorer.
3. **Austrian Post full-eligibility ratio ~1.000.** AP's rate card is virtually identical to incumbent invoice across its narrow eligibility (32,802 shipments, ratio 1.003). Its 0.701 winning-slice ratio reflects AP only winning on lanes with structural cost advantage (CH/LI cross-border); on broader eligibility it's at parity. Narrows AP's portfolio value -- cherry-pick wins, not a general-purpose bidder.

## Hermes confirmation

Hermes winning-slice ratio **still 0.588** (unchanged from 2026-05-15). The 11 working assumptions awaiting Q1-Q10 carrier replies are unchanged. Refresh did NOT firm any of them up.

## DHL Paket bias direction

Unchanged from 2026-05-15. Full eligibility 1.915 (engine grossly over-prices full book vs. invoice -- DHL Paket is the deepest-discounted incumbent), winning slice 1.020 (the slice it wins is where its rate card is closest to its invoiced book).

## Open work surfaced (for Jebrim to decide whether to action)

1. Wire DPD PL into `_decision_sets.CARRIERS` as NEW_OFFER-capable, or formally confirm retire-only. Full-eligibility 2.957 suggests low-value to add (won't win lanes).
2. Wire FedEx into `_decision_sets.CARRIERS`. Full-eligibility 1.732 suggests tail-bidder.
3. Re-run after Q1-Q10 Hermes replies land.

## Files touched

- `bi-analytics-main/NFE/projects/2_EU_tender_2026/2_analysis/_refresh_bias_table.py` -- created
- `bi-analytics-main/NFE/projects/2_EU_tender_2026/2_analysis/_inspect_matrix.py` -- created (schema spike; can be archived/removed at Jebrim's discretion)
- `bi-analytics-main/NFE/projects/2_EU_tender_2026/2_analysis/data/_bias_refresh.parquet` -- created (machine-readable refresh output)
- `bi-analytics-main/NFE/projects/2_EU_tender_2026/2_analysis/docs/bias_table.md` -- overwritten

## Dwarf write-boundary observance

- No writes to `confirmed/`, no deletes, no sub-spawn.
- All quest-log writing in this file (Jebrim's `quest-log/in-progress/`).
- No draft writes; observations stay in this quest-log per dwarf discipline.
