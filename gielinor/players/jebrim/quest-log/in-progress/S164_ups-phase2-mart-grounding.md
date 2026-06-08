# S164 — UPS EU-tender Phase-2: mart grounding for the cost-replay engine

**Player:** Jebrim · **Role:** shipping-agent (emulated) · **Opened:** 2026-06-08 · **Status:** returned to principal

Grounding pull for the UPS Phase-2 cost-replay engine. Replay Picanova OUTBOUND UPS shipments (Q1 2026, `ups` regular stream, ORWO out) through the 2026 UPS rate card; calc-vs-actual. Window: `shop_order_created_date` in [2026-01-01, 2026-04-01).

**Tier:** UPSTREAM / off the gold contract. The AP/Maersk siblings pull from `enterprise_silver.fact_shipments` (not `shipping_mart`). Maintainer overlay (`CLAUDE.local.md`, user `tcg_nfe`) grants the upstream scope.

## Headline findings

- **Population predicate (contract-correct):** `UPPER(shipping_provider_group)='UPS' AND production_site='PCS PL'`, Q1 window. This is the AP/Maersk pattern and it gives a **perfectly clean ORWO exclusion** — verified: zero PCS PL rows carry a `ups_orwo` invoice line. ORWO/Wolfen is a *separate* production_site, so excluding `Wolfen` excludes the photo-lab bulk-bill entirely. No order_source/extkey ORWO signal needed.
- **Leakage:** production_site='PCS PL' drops only **1,039** Wolfen shipments that were UPS-regular-billed (~0.67% of the regular stream) — acceptable; those are photo-lab parcels, correctly out. Invoice-source filtering would pull them in, which is wrong for an outbound-TCG replay.
- **No origin PLZ exists.** No sender/warehouse/origin postal column on fact_shipments; order_addresses carries only destination + billing. PCS PL origin is a fixed warehouse constant — supply it to the rate card as a constant, not a column.
- **No residential flag exists** at any accessible grain. The +€0.40 residential surcharge can't be sourced from the mart; must be inferred or sourced from the UPS invoice lines (residential_eur bucket) for the actual side.
- **cost_summary lives in `shipping_mart`, NOT `enterprise_silver`.** enterprise_silver only has `fact_shipment_cost_summary_old`. Brief assumed enterprise_silver — corrected to shipping_mart (fresher: dw_timestamp 2026-06-08 vs 05-24). All 14 bucket columns confirmed.
- **Population shape:** 155,010 rows, **100% priceable** (dim+weight all populated). 98.49% invoiced (replay has actuals). Weight max 64.7kg, **zero >70kg**. DE 44% / IT 17% / FR 12% / ES 10% / CH 7% lead.

## Checks
- ORWO leakage: PCS PL × ups_orwo line = 0 (clean). Wolfen regular-ups = 1,039 (deduped to shipment grain).
- Reversals: only 2 negative-total rows; zero credit-note rows.
- Weight band CDF for p50/p95 (MEDIAN()/PERCENTILE_CONT rejected by MCP validator — band CDF used instead).

## Deliverable
- Structured text + ready `sql/pull_shipments.sql` returned to principal (he writes the files). No brain-external files written by me.
