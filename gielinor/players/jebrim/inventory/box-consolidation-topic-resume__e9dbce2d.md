---
quest: S204_na-may-quota-breakdown (spawned task — becomes its own quest on pickup)
sid8: e9dbce2d
ts: 2026-06-11 17:45
open_dep: handed off — next session builds the topic + HTML report
---

# Handoff — ORWO_80x60 box-consolidation shipping topic + HTML report

## The task (Niklavs, 2026-06-11)

Build a full NFE **shipping topic** for the L-002 finding, with the complete analysis
and a **final report in HTML** that clearly shows (a) the same product baskets now ship
in a more expensive package, and (b) charts of when it happened.

## What's already established (don't re-derive — verify against the artifacts)

- Finding: PCS PL eliminated the `ORWO_80x60` box (91×62×4.5cm) mid-May 2026; its whole
  mid-format family (DIGI-80X60, KLAS-75X50, QUAD-60X60, PAN1-80X40 articles) moved into
  `WICKELVERPACKUNG 100x75_AE` (100×75×5cm, girth 224→262cm).
- Evidence grain: basket signature = sorted articlenumber×qty per shipment. 55% of June
  100x75_AE volume = ex-old-box signatures. Identical basket, invoiced, box-vs-box:
  **+€1.26/parcel weighted (19 baskets, n≥30 each side; range +€0.42..+€2.08; 2-canvas
  baskets −€2.21)** ≈ €15–16k/mo ≈ €185k/yr pace at the old box's 12–13k ships/mo.
- Method + caveats: `NFE/projects/6_shipping_reporting_v2/investigations/l002_findings.md`
  + `l002_basket_trace.py` (LISTAGG basket pull → `../data/l002_baskets.parquet`, 59,461 ships).
  NOTE: the redshift MCP validator can't parse LISTAGG WITHIN GROUP — pull via NFE
  `shared.database` (the script does).
- Timing series for charts: monthly Apr 6,218/850 → May 2,288/5,120 → Jun 0/3,667
  (80X60-articles by box); daily/weekly grain needs a fresh pull (ship-day basis,
  COALESCE(received_by_carrier_date, order_produced_date, shop_order_created_date)).
- Caveats to carry into the report: June invoices immature (re-confirm delta);
  declared dims are template-derived; supersedes the earlier €0.97/€140k single-article estimate.

## What to build

1. `NFE/shipping_topics/47_orwo_80x60_box_consolidation/` (next free number — 46 taken;
   verify 47 free at creation). Standard topic shape: sql/ + pull/analysis scripts +
   data/ + CLAUDE.md. Reuse/adapt the l002 script rather than re-inventing.
2. Analysis additions beyond l002: daily/weekly migration series (the cutover chart),
   per-basket cost comparison table, cumulative extra-cost-since-May running total,
   carrier-mix check per basket (rule out routing as the delta's cause — or attribute it).
3. **HTML final report** (self-contained single file, charts embedded): the story in
   order — what happened (box elimination, when: the mid-May cutover chart), the proof
   (same baskets both boxes, cost side-by-side), the price (€/parcel, €/yr pace), the
   ask (PCS PL ops: priced decision? needs ≈€185k/yr packing benefit to break even).
   Plain-language, finance/ops audience. Clarify with Niklavs only if HTML tooling
   preference matters (plotly-offline vs static images — recommend plotly-offline).
4. Update ledger L-002 in `projects/6_shipping_reporting_v2/ledger.md` with the topic
   pointer once built.

## Files to read first

1. This file.
2. `projects/6_shipping_reporting_v2/investigations/l002_findings.md` (+ the script).
3. `projects/6_shipping_reporting_v2/ledger.md` (L-002 row) and `briefings/2026-06-11_wk23.md`.
4. Quest log `S204_e9dbce2d_na-may-quota-breakdown.md` (the L-002 turn lines, incl. method
   escalation dims→weight→article→basket).
