# Shipping mart — V1-freeze reconciliation (agent docs synced to live mart)

**As of:** 2026-05-25 (S068). Mart V1 declared complete/frozen. Reconciled the shipping-agent's `reference/*.md` (all stamped 2026-05-22 gold-cutover) against live `shipping_mart.*` via redshift MCP (9 probes) and synced the docs. Committed + pushed to picanova/main (`393fdcf`). Narrative: `quest-log/in-progress/S068_363fdec7_*`.

## What V1 landed — caveats that were WRONG, now fixed in the agent docs

- **ORWO revenue: 0% → 100%** populated (the most-repeated ORWO caveat; was "intended-populated not yet landed").
- **ORWO `destination_country`: 100% blank → 0%** (fully populated; ORWO country slicing now works).
- **`cost_source`: 4 values, sums 100%** — `invoice 67.82 / expected 26.57 / null 5.18 / avg 0.44`. The transient `invoice_estimate` 5th value seen *during* the May reload is **gone**. Reload pulled uncosted 8.04%→5.18%. Mart-wide invoiced ≈ **88%** (was ~85%).
- **`fact_shipment_invoice_lines`: 18 cols** (new `source_table`), not 17.
- **`is_returned`: now ~67% populated** (2 distinct values) — semantics **UNCONFIRMED**, kept do-not-use pending a principal ruling.

## Held constant by principal ruling (2026-05-25)

- **Data floor stays 2024** — live MIN dates hit 2023 for Picturator/PicaAPI/PCS, but those are invoice-lag absorption, not the intended floor.
- PicaAPI doc "starts 2025-08" corrected to **2024**.

## Confirmed still accurate (no change)

`fact_shipments` 65 cols; bucket invariant `SUM(11 buckets)==total_eur` **0 violations / 12.18M rows**; PCS revenue 100% NULL; invoice_lines `shipment_id` 0.85% NULL; POST_DVF + ORWO POST structural cost holes. Resolves prior open items H2 (invoice_estimate — transient) + H3 (65-vs-63 — doc miscount, mart is 65).

## Stale siblings to retire at next alching

- [[shipping_mart_cost_vocabulary_2026-05-22]] — old cost_source dist (65.15/24.37/8.04/1.99).
- [[shipping_mart_coverage_audit_2026-05-21]] — old ~85% / ORWO rev 0%.

Both carry pre-reload numbers superseded by this note. Promote this note + archive those at the next Jebrim alching, once the `is_returned` ruling lands.
