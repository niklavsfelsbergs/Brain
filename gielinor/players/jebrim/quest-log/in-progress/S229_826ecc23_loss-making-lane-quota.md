# S229 — Loss-making shipping-lane quota scan (NFE topic 47)

**Player:** Jebrim · **sid8:** 826ecc23
**Ask:** Find shipping lanes that should be closed — where shipping cost eats an outsized
share of (or exceeds) product revenue. Trigger: Niklavs spotted CH + DB Schenker at ~140%
cost quota. Grain: country+carrier primary, country+carrier+packagetype secondary. Build as
a new shipping topic in NFE.

**Deliverable home:** `bi-analytics-main/NFE/shipping_topics/47_loss_making_lane_quota/`
(findings.md + sql/ + build_data.py + make_excel.py + data/ + outputs/). External repo — the
analysis lives there, not in the brain. This quest-log entry is the narrative trace.

## Turn log

- Grounded in shipping-mart domain digest + topic-46 (NA quota) as the closest template.
  Quota = shipping cost ÷ net product revenue.
- **Correction 1 (Niklavs): "use the shipping mart, nothing to do with sales fact."** I'd
  started checking `dw.sales_fact` schema (it conveniently carries revenue+cost+country on
  one grain). Principal wanted mart-only. Pivoted to the shipping-agent. → examine draft.
- Spawned shipping-agent: revenue source in the gold mart = `net_revenue_eur` on
  `fact_shipments` (shipment grain, reconciles row-for-row to line-item revenue — no
  sales_fact needed). Built grain-1 + grain-2 scans. CH+DB Schenker confirmed 140.3%.
- Built topic 47: SQL (both grains), build_data.py, findings.md, materialized parquets
  live (reproduced the agent's numbers exactly).
- Drill-downs on principal cue: NL 112% is **one packagetype** (DB Schenker cut-to-size),
  lane overall healthy 55%. GB+DHL 67% lane is fine in bulk; flat letter/large-letter
  mailers (Großbrief/Maxibrief 175%) carry the loss.
- **Wolfen investigation (spawned 2nd shipping-agent → sub-trace
  [[S229_826ecc23_gb-dhl-wolfen-mailer-cost-decomp]]):** the GB+DHL flat mailers are
  Wolfen-origin (Picturator platform). Cost is NOT sperrgut — it's DHL international
  *parcel* base rate (~€21.50/ship, "DHL Parcel International GK Premium"); flats billed as
  premium parcels. Großbrief/B4 zero oversize; A3 calendar has a small justified bulky-goods
  surcharge.
- **Correction 2 / the big reframe (Niklavs): "how much has this cost us in 2026?" → €0.**
  The GB+DHL flat-mailer batch is **entirely Sep–Nov 2025** (1,790 ships, ~€45k cost,
  ~€18k net loss) — a dormant Q4 Christmas calendar/poster batch, zero 2026 activity. The
  whole scan was polluted by (a) seasonal 2025 batches reading as live bleeds and (b)
  estimated cost softening the quota. → Principal directed reframe: **2026 only + invoiced
  shipments only (cost_source='invoice')** as the canonical cut. → examine draft + memory.
- Rebuilt both grains on the reframed cut. New picture: CH+DB Schenker **worse** at 157%
  (invoiced-only); DB Schenker is **systemic** (whole continental cluster FR/IT/ES/NL/AT/DK/BE
  60–75%, FR biggest at €79k invoiced cost); biggest *new* live find = **US+FedEx "21" Tube"
  119% on 2,474 ships, 98% invoiced** (posters-in-tubes, year-round) — was invisible under
  the seasonal noise. GB+DHL correctly dropped out.
- Wrote the Wolfen episode into findings.md as a case study of *why* the reframe was needed.
- **Excel deliverable:** 3-sheet workbook (`outputs/loss_making_lanes_2026_invoiced.xlsx`)
  — dest×carrier, dest×carrier×packagetype, dest×packagetype; top 100 by quota desc, 2026
  invoiced. SQL in sql/ (honored the global "SQL in sql/ folder" rule). Iterated on cue:
  revenue>€5k floor (killed single-shipment noise), quota as 0–1 ratio pre-formatted as a
  percent. Sheet 3 surfaced that CH runs hot across *most* packagetypes → CH is a
  destination-level (cross-border) cost problem, not purely DB Schenker.

## Decisions

- Canonical cut for "bad quota segments" = **current-year + invoiced-cost only**. Trailing-12
  + all-cost-sources is artifact-prone (seasonal + modeled).
- Revenue stays mart-side (`net_revenue_eur`), never sales_fact — principal directive.
- Topic kept in-progress (not graduated): deliverable shipped, but named open follow-ups
  remain (principal decisions + optional deeper cuts).

## Pending external actions

None pending. NFE topic-47 files written to disk; **bi-analytics-main commit not yet made —
asked Niklavs at close** (separate repo, outside the brain's pre-authorized close commit).
