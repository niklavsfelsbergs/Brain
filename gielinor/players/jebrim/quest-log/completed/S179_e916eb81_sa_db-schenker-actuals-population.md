# Shipping-agent trace — DB Schenker actuals population pull

**Role:** shipping-agent (emulation) | **Player:** Jebrim | **Tier:** gold-contract
**Spawned for:** DB Schenker 2025-vs-2026 rate-card re-pricing (project 5_shipping_savings).

## Ask
Pull full DB Schenker freight shipment population from gold `shipping_mart`, one row per
shipment over the most recent full 12 months, to parquet + report coverage/seasonality/cost-source.

## Scope used
- Carrier: `shipping_provider_group = 'DB SCHENKER'` (gold contract, no joins).
- Period: 2025-06-01 .. 2026-05-31 (most recent FULL 12 calendar months; June 2026 partial, excluded).
- Date axis: `shop_order_created_date` (fully populated; order-placement basis).
- All verticals + all production sites combined (re-pricing wants the whole DB Schenker book; stated as assumption).

## Turn log
- Confirmed provider-group vs service-code: `DB SCHENKER` covers TWO service codes, not one
  — `DBSCHENKERPLEUHOME` (79,474 lifetime) + `DBSCHENKERPLEUB2B` (103 lifetime). Brief expected
  only HOME. Preferred provider_group filter per brief → both included (B2B is 0.1%).
- Picked full-12-month window; Dec 2025 spike (7,166) = holiday seasonality, not DQ.
- Cost basis = `real_shipping_cost_eur` (invoiced-only, `cost_source='invoice'`). NULL on `expected` rows.
- Invoice-lag at tail: Apr-2026 41% invoiced, May-2026 0% invoiced → invoiced total UNDERSTATES annual.
  Rule-36 check: cost present + stable for 10 of 12 months → invoice lag, NOT a reload.
- Pulled per-row in 4 quarter-slices via MCP (each overflowed to saved JSON); assembled with polars.

## Headline result
- 33,718 shipments. Invoiced actual = EUR 1,554,912.95 (real cost; 28,399 rows / 84.2% invoiced).
- Final cost (invoiced + estimated, full coverage) = EUR 1,849,902.33 — the fuller annual figure.
- Reconciliation note for the re-rate: the EUR 1.55M actual covers the INVOICED 28,399 rows only;
  Apr+May 2026 are mostly/entirely un-invoiced (lag). Re-rate against the matching basis.

## Deliverable (outside brain)
- `Documents/GitHub/bi-analytics-main/NFE/projects/5_shipping_savings/analysis/db_schenker_2025_vs_2026/actuals_population.parquet`
- SQL: same folder `/sql/20260609-01_db_schenker_actuals_population.sql`

## Checks
- Row count + invoiced total reconcile exactly between per-row parquet and GROUP BY aggregate.
- 33,718 distinct shipment_ids (no dupes). Null counts match (vol/wt = 1 each; destcc = 0).

## Open / needs principal
- B2B service code (`DBSCHENKERPLEUB2B`, 103 lifetime / a handful in window) folded into the population
  via provider_group filter — flag if the re-pricing is HOME-only.
- Brief's "only one service code" assumption was slightly off — worth noting upstream.
