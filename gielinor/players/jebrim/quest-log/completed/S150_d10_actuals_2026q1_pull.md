# [[S150_e59202cf_carrier-overview-report-design|S150]] d10 — shipping-agent mart pull: 2026 Q1 actuals ("vs today" baseline)

Shipping-agent (emulated), Jebrim namespace. Pull for carrier-overview v2 "vs today" baseline.
Tier: **gold contract** (`shipping_mart.*` only — no upstream needed). Full-access profile present (`tcg_nfe`) but unused for tier.

## Brief
2026 Q1 actual invoiced cost/shipment, PCS PL origin, 18 tender countries, carriers UPS / Maersk / DB Schenker, with parcel dims + invoiced cost-component breakdown. Output parquet for the analysis.

## Scope used (verified against contract)
- Period: `shop_order_created_date` 2026-01-01..2026-03-31 (contract confirms this is the period field; no `sl_shipped_date` in gold).
- Origin: `production_site = 'PCS PL'`.
- Destinations: 18 tender countries.
- Carriers: `shipping_provider_group IN ('UPS','MAERSK','DB SCHENKER')` — cross-checked that group membership == extkey-prefix membership (0 mismatches), so group filter alone is exact.
- Cost basis: `real_shipping_cost_eur` (invoiced; EXCLUDES tax & customs by design — matches principal confirmation). Components from `fact_shipment_cost_summary` (invoiced-only).

## Run-log
- Loaded how_to §0 + mart-contract + tables + CLAUDE.local (full-access profile). Tier stays gold.
- Probed population: 189,917 shipments. Group split UPS 151,559 / Maersk 27,645 / DB Schenker 10,713.
- MAERSKFR now at REAL Q1 volume: 27,624 shipments (vs 2025's 107-parcel Nov/Dec tail), 99.4% invoiced, FR-only domestic, mean €4.72.
- Coverage: 97.8% invoiced by row, 94.0% euro-weighted (just under 95% threshold → flag both bases). DB Schenker is the soft one at 82.4% eur-wt.
- Dims/weight: 0% null (PCS PL is PCS-owned → fully dimmed). real_total null only on the 4,237 non-invoiced rows (expected).
- MCP payload can't carry 19K-row pages (connection closed) → bulk write via harness `connect()` (same live mart, read-only SELECT). MCP remained the authority for every reported number.
- Wrote parquet 189,917×29. Reconciled vs mart: rows match, invoiced 185,680 match, SUM(real_total)=€1,795,239.95 exact to cent, cost invariant maxdiff 0.0, 18 countries, window clamped.

## Headline results
- Mean real_total (invoiced-only): UPS €7.95 / Maersk €4.72 (all FR) / DB Schenker €51.29 (heavy, multi-country).
- UPS FR mean €8.37; Maersk FR €4.72 — Maersk structurally cheaper on the FR domestic lane.
- UPS components: base €5.12, fuel €0.96, truck €0.75, residential €0.55 means; oversize concentrated (701 of 149,277 parcels carry it, €141k total — 70 >€400 likely OML, 552 €50-400 likely LPS). Peak tiny (1,090 parcels, €1.8k). LPS/OML + peak ARE visible in components.

## Deliverable
- `bi-analytics-main/NFE/projects/2_EU_tender_2026/2_analysis/data/actuals_2026q1.parquet` (189,917 rows, 29 cols).
- SQL: `.../2_analysis/sql/20260605-01_actuals_2026q1.sql`. Extract script: `shipping-agent/scratchpad/extract_actuals_2026q1.py`.

## Caveats flagged to Jebrim
- DB Schenker 82.4% eur-wt invoiced — softest carrier; CH lane mean €222 (heavy/customs-laden, small n=199).
- 4,237 non-invoiced rows carry `expected_shipping_cost_eur` not `real_total_eur`; `final_shipping_cost_eur` included for that tail.
- Tiny extkeys (MAERSKSE n=13, MAERSKFN n=8, UPS bare n=416 all non-invoiced) — noise, not lanes.
