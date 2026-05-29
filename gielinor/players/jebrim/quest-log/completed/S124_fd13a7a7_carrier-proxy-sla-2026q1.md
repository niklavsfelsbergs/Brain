# Shipping-agent: carrier proxy SLA / transit-time baseline — 2026 Q1

**Actor:** shipping-agent (emulated), inherited player Jebrim
**Date:** 2026-05-29
**Tier:** gold-contract (`shipping_mart.fact_shipments` only)

## Asked
Build an Excel proxy carrier-SLA baseline — no contractual carrier transit SLAs exist, so
derive an empirical p90 decimal-business-day transit baseline from our own delivered 2026-Q1
shipments. Per-shipment pull, decimal calcs in Python (numpy/polars), aggregate to
carrier × service × country (+ carrier × country rollup), floor 200, Definitions sheet.

## Scope used
- Cohort: `received_by_carrier_date` ∈ [2026-01-01, 2026-04-01); delivery date present;
  business-transit window valid; `is_returned = false`. 734,614 shipments.
- No vertical (`source_system`) filter — all production lines combined. Brief gave the cohort
  filter explicitly with no vertical scope; carrier-SLA work is lane/origin-shaped not
  vertical-shaped. FLAGGED to principal as the one open scope choice (re-run TCG-only if wanted).
- Gold contract only — local full-access profile present but not needed.

## Turn log
- Read shipping-agent how_to.md in full + CLAUDE.local.md (full-access profile present, unused).
- MCP structure check: all 9 pull columns present on fact_shipments. Cohort = 734,614 (matches ~734k).
- MCP DQ probes: 0 null event ts in cohort, 0 same-day negatives, 10,468 null production ts, 11 carriers.
- Wrote SQL (per-shipment, no SQL aggregation) + polars/numpy build script importing harness/db.py.
- Decimal-BD formula: numpy.busday_count(handover_date, delivery_date) + intra-day
  (delivery_tod − handover_tod)/24h, clamp ≥ 0. Documented in Definitions sheet.
- QA caught a NaN-vs-null bug: invalid production span as NaN blanked the average but kept
  the median (polars .mean() NaN-propagates, .median() skips). Fixed → invalid = NULL.
- Built xlsx via xlsxwriter (installed, no pip needed).

## Headline result
- Overall transit p90 = 4.12 business days (median 2.08, max 61.0 long economy/sea tail).
- overview sheet: 49 segments (732,555 ships kept). by_carrier_country: 38 segments (733,226).
- Service × country matters: UPS04STD p90 = 3.16 BD→DE, 4.34→FR, 5.03→IT, 5.96→ES.

## Checks
- Percentile monotonicity: 0 rows violate p85 ≤ p90 ≤ p95 on either sheet.
- Reconciliation: by_carrier_country total (733,226) ≥ overview total (732,555) — rollup
  recovers thin-cell coverage the finer grain dropped to the 200-floor. Correct direction.
- Negatives before clamp: 2,481 (0.34%), worst −0.98 BD, mean −0.20 BD — intra-day scan
  jitter, correctly floored to 0. No large/structural negatives.
- SLA header bold + amber, freeze panes at A2 — verified via openpyxl.

## Caveats surfaced
- Denominator = DELIVERED only → transit-distribution baseline, NOT a true OTD%-with-misses.
- Recent-Q1 shipments still settling (fast bias on late weeks).
- Per-shipment timestamp DQ — cohort aggregates trustworthy, individual shipments not.

## Deliverable
`Documents/GitHub/shipping-agent/workbench/analysis/20260529-carrier-proxy-sla-2026q1/outputs/carrier_proxy_sla_overview_2026Q1.xlsx`
(workbench item with sql/, notebooks/, data/ snapshot, CLAUDE.md repro doc).

## Open / needs principal
- Vertical scope left open by design (all-lines). Confirm or ask for a TCG-only re-run.
- True OTD% needs the full received-cohort denominator + a chosen target threshold (no set SLA) — deferred.
