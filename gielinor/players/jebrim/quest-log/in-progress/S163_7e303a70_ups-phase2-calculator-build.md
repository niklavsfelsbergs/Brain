# S163 — UPS EU-tender Phase 2 v1 calculator BUILD

**Session:** 7e303a70 (continuation of S163; design/Phase-1 born under 0109840c).
**Date:** 2026-06-08.
**Player:** Jebrim.
**Ask:** Build the temporary UPS Phase-2 calculator — a runnable v1 engine producing per-shipment
UPS calculated cost on locked assumed values; refine once UPS answers Round 1; do NOT chase a
final headline.

## What was asked → what I did

Built the calculator per PLAYBOOK Phase 2, scaffolding
`bi-analytics-main/NFE/projects/2_EU_tender_2026/1_offers/picanova/UPS/calculation/`.

**Read first (grounding):** the resume, UPS CLAUDE.md + cost_calculation_tree, both research
anchors (real-invoice profile + published surcharges), PLAYBOOK Phase 2, and the Austrian Post
+ Maersk worked examples (Maersk's zone-matrix `join_asof(by=zone)` was the structural template).

**2.1 window:** confirmed **2026-Q1 (Jan–Mar)** with the principal (recommended; matches the
decision-report actuals basis + Maersk window). Flagged the peak-coverage tradeoff (Q1 barely
overlaps the peak window) — accepted for a v1 where the headline is held.

**Mart grounding (spawned shipping-agent, not from memory):**
- Population predicate = `production_site='PCS PL'` + `UPPER(shipping_provider_group)='UPS'`. This
  is the **clean ORWO exclusion** — verified ZERO PCS-PL shipments carry a `ups_orwo` line (ORWO
  ships from `production_site='Wolfen'`). Matches the AP/Maersk pattern.
- 155,010 Q1 rows; **100% dim+weight populated; 0% over 70kg (max 64.7kg); 98.5% invoiced.**
- **No origin-PLZ column** (PCS PL is one fixed DE origin → supply as a constant; confirms the
  collapse-by-ISO2 zone design). **No residential flag on the shipment row** (the brief assumed
  one; it only exists post-hoc as `residential_eur` on the cost summary).
- **Cost-summary correction:** `enterprise_silver.fact_shipment_cost_summary` does NOT exist
  (only `_old`, stale); the live one is `shipping_mart.fact_shipment_cost_summary`. SQL points there.
- Dest mix: DE 44% · IT 17% · FR 12% · ES 10% · CH 7% = ~90%; overseas tail (AU/US/NZ/CA ~5%) on
  Worldwide Economy (a product not in our 4 cards).

**Rate extraction (`extract_rates.py`):** discovered the two-shape rate card —
- **Standard Single is DESTINATION-keyed** (each column = a negotiated country GROUP; CZ & BE are
  both "Zone 3" but priced 4.99 vs 4.36 → rate is per destination, not per zone). Exploded to ISO2.
- **Express / Express Saver / Expedited are ZONE-keyed** (zone row → rate; destination→zone via
  DE_ZONES). This is why the zone matrix is load-bearing.
- Outputs: `rates_standard.parquet` (31 ISO2 × 34 bands), `rates_zone.parquet` (1,656 rows),
  `de_zones.parquet` (382 rows, 205 ISO2, export/Versand zones + origin PLZ band + X remote flag).

**Engine (`engine.py`):** billable weight = greater(actual, L×W×H÷5000) round-up next 0.5 kg →
forward as-of band lookup; zone/destination resolution; cheapest-eligible across the 4 services;
**every uncertain input a tagged parameter** (FUEL_PCT, PEAK, LPS on/threshold/amount,
RESIDENTIAL_MODE, OML=0, LINE_HAUL=0, customs excluded). Prices 155,010/155,010 (100%). Writes
`output/replay.parquet` (per-shipment cost + chosen service + bucket breakdown + real_* buckets).

**Verification (PLAYBOOK 2.9):** DE@1kg→base 2.82 (exact card match); DE@10kg→4.90; ES@2kg→5.21;
FR billable 7.5→band 8→7.50; fuel = exactly 35% of base; **bucket-sum invariant 0 violations**.

## Key finding — LPS placeholder is 12× the actuals

Book LPS default (L+girth>300cm, €101.80, on) fires on **16,257 parcels (10.5%) = €1.65M**, vs
**actual oversize €142K on 707 parcels (0.5%)**. It inverts the cost structure (LPS > base) and
makes the calc total (€3.34M) 2.7× the actual Q1 freight (€1.26M). Added a standing
validation-vs-actuals block that flags this every run. → **LPS is Q4-decision-vital.** **Decided
(principal): v1 LPS default = OFF** (one-flag togglable; re-rate when Q4 lands). LPS-off calc
total = €1.68M (vs €3.34M LPS-on; actual Q1 freight €1.26M).

## Headline discipline

The engine refuses a quotable number — every run prints "PROVISIONAL & UNDERSTATED" (line-haul €0
→ understated; fuel 35% vs real ~20%; peak/LPS provisional). Per keepsake risk #1.

## Open / next

- Principal decision: v1 LPS default (off recommended). Residential mode (defaulted 'all').
- On UPS Round-1: set fuel (Q1), LPS (Q4), peak (Q6) → re-rate. Then Phase 3 (comparison/findings)
  + add the line-haul layer (A10) before any headline.
- NOT committed — awaiting principal's LPS decision + commit go.

Resume: `inventory/ups-carrier-assessment-resume__0109840c.md`. Mart-grounding sibling trace:
`S164_ups-phase2-mart-grounding.md`.
