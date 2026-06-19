# ORWO tender — Wolfen spine, baseline reprice engine, new UPS offer ([[S280_e5be6eb5_orwo-tender-reprice-engine|S280]])

Durable state of the ORWO carrier tender after [[S280_e5be6eb5_orwo-tender-reprice-engine|S280]] (`e5be6eb5`). Repo:
`bi-analytics-main/NFE/projects/7_ORWO_tender_2026/`. Cross-link parent [[eu-tender]] (Picanova sibling —
method transfers, engine shape transfers), [[carrier-contracts]], [[shipping-mart]].

## The entity (corrected)

**ORWO = `production_site='Wolfen'`, NOT `source_system='ORWO'`.** ORWO Photolab is a **white-label
logistics operator** at the Wolfen plant, shipping for ~20 photo brands (Hofer/Rossmann/Aldi/Monoeuvre/
Sendmoments/Bestecanvas/MeinFoto/Lidl/MyPoster/…) under **two UPS accounts** (0R6D51 reseller + 0R6D66
ORWO-proper, both with ORWO 2026 rate cards). In the mart, Wolfen output is split across `source_system`
`ORWO` (34k) + `Picturator` (93k) = **~126k UPS trks**, **cross-border-first**: AT 41k > DE 33k > UK 21k >
FR 12k > CH 5k > US 3k. PCS-PL (432k) is the separate Picanova tender. DHL keys the same (`Wolfen`).

## The pipeline (UPS, baseline complete + gated)

- **Cost basis = silver invoices only** (`enterprise_silver.ups_orwo_invoices`); the silver row carries
  trackingnumber + receivercountry + UPS `zone` + billedweight + per-line cost = a complete spine for the
  invoiced book (62k freight trks; 93.5% match mart-Wolfen). Mart `real_shipping_cost_eur` dropped
  (bundles/consolidates/RTS-redistributes).
- **Per-tracking base** `repricing_base/sql/02_ups_tracking_base_silver.sql` — charge lines bucketed
  (freight / fuel / residential / surcharge_other / tax-duty-excluded).
- **Cards extracted machine-readable + trust-gated** `repricing_base/rate_cards.md` — Standard export
  (country-keyed) + Economy DDP (GB/US). The Phase-1 "50–85% gap" was a PDF zone mis-map (AT off Denmark's
  column), dead; cards reproduce invoiced freight to the cent. 0R6D51 xlsm = signature wrapper, no data.
- **Reprice engine** `repricing_base/engine/` (EU-tender-style: `build_rate_tables.py` → parquet →
  `calculate.py` polars as-of weight-band join + fuel(0.175) + residential → `run_gate.py`). **Full-grain
  trust gate: modeled own-cost = invoiced freight at 0.971 portfolio, every material lane 0.98–1.00.**
  This is the validated BASELINE (switchable-incumbent own-cost), *not* an offer.

## New UPS offer (Tender 2026)

`offers/UPS/` — `Netto-Tarife ORWO Photolab - Tender 2026.xlsm` repriced on the same 58.8k parcels
(`build_offer_tables.py` + `compare_offer.py`). **Saving €16,973 H1 / ~€34k/yr (4.4%), almost entirely
Switzerland** (CH −€11.2k/−29%, light-parcel cut 11.44→8.04) + mid-weight DE (−€5.7k/−11%). **AT (biggest
lane) + FR/NL/IT/ES + GB/US UNCHANGED.** Negotiation lever = AT (held flat; a 5% AT cut beats the whole CH
concession). GB/US stay Economy DDP (offer's GB Standard is worse).

## Next

Negotiate AT ask → competitor offers (DHL/AT-Post/Güll/GLS/Maersk) in the same machinery → annualization
via seasonal ratios → DHL Phase 2 (same Wolfen spine + engine shape). Parent quest
[[S275_abfcf511_orwo-tender-contracts-coverage-weight-grain]]; this session
[[S280_e5be6eb5_orwo-tender-reprice-engine]].
