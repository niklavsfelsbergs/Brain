# S150 D11 — EU Tender 2026: 2026-Q1 full-book population pull (shipping-agent)

**Role:** shipping-agent sub-agent (mart specialist), spawned by Jebrim for the tender decision report Phase A.1.
**Tier:** gold-contract (`shipping_mart.*` only — local full-access profile present but not needed; pure gold pull).
**Scope:** PCS PL origin, 2026-Q1 (half-open `>= 2026-01-01 AND < 2026-04-01`), 18-country whitelist, ALL carriers (no provider filter — full incumbent book). Vertical/origin pre-resolved by the brief.

## What was asked
Near-exact redate of the 2025 full-year `population.sql` → 2026-Q1 full book. Only change = date window. Execute to parquet, verify cost-basis invariant + tax/customs question, reconcile (per-carrier extkey+group, MAERSKFR confirmation, cost_source dist, DQ).

## Turn-by-turn
- Read `how_to.md` (full) + `population.sql` spec + `CLAUDE.local.md` (full-access present; pull is gold-only so stayed on contract).
- Wrote `sql/population_2026q1.sql` — identical to spec except date window + header comment. 18-country whitelist, NULL gates, 23 fact + 14 bucket cols, casts, LEFT JOIN all preserved. No provider filter.
- Live-mart aggregate: 531,194 rows, Σ €3,030,997.91, mean €5.71. Invariant `cs.total_eur == fs.real_shipping_cost_eur`: 0 breaks, max abs diff €0.000000, 0 NULL real-cost rows.
- Tax/customs: buckets stored NULL-when-empty (first COALESCE-less check returned 0 — fixed). With COALESCE: all 531,194 rows reconcile total_eur = 11 freight buckets EXCLUDING tax & customs, residual €0.0000. WITH tax+customs only 264,194 match (the zero-tax rows). => total_eur is clean carrier-shipping basis; tax (€153,889 / 267,769 rows) + customs (€964 / 80 rows) are side buckets. Consistent with rule 13.
- Extracted to `data/population_2026q1.parquet` via keyset paging on shipment_id (6 pages, 100k each). Parquet reconciles to mart exactly: 531,194 rows, Σ €3,030,997.9091, 37 cols.
- MAERSKFR: 27,447 @ €4.72 — matches expected ≈27,600 @ €4.72. CONFIRMED.
- cost_source: 100% invoice (NULL-gate makes pull invoiced-by-construction).
- DQ: no negative totals; DB Schenker mean €51.29 is real freight grain (max €1,680), not error; oversize concentration sane.
- Protected artifacts untouched: `population.parquet` (2025) + `actuals_2026q1.parquet` (3-carrier).

## Headline result
531,194 parcels, Σ real shipping cost €3,030,997.91 (invoiced basis, 100% invoiced), mean €5.71/parcel. MAERSKFR confirmed at 27,447 @ €4.72. total_eur excludes tax & customs (clean freight basis).

## Deliverables (outside brain)
- `bi-analytics-main/NFE/projects/2_EU_tender_2026/2_analysis/sql/population_2026q1.sql`
- `bi-analytics-main/NFE/projects/2_EU_tender_2026/2_analysis/data/population_2026q1.parquet`
- `bi-analytics-main/.../sql/_extract_population_2026q1.py` (throwaway extractor harness)

## Open / needs principal
- None blocking. Note: pull is invoiced-only by construction (the `cs.total_eur IS NOT NULL` gate) — so it excludes the small late-invoice tail that engines could still price but has no parity truth, same as the 2025 artifact. Flag if downstream needs the uninvoiced rows.
