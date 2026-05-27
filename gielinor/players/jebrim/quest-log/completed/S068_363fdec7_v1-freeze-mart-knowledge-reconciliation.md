# S068 — V1-freeze: shipping-agent knowledge vs live mart reconciliation

**Session:** 363fdec7 · **Player:** Jebrim · **Opened:** 2026-05-25

Principal: shipping data mart V1 is complete and will hold for a bit. Review what the shipping-agent's docs claim about the mart — all the DQ caveats — against the live `shipping_mart.*` gold schema, and report whether the agent's knowledge matches reality.

## Method

Read the agent's documented mart knowledge (out-of-tree `Documents/GitHub/shipping-agent/reference/{mart-contract,tables,sources,coverage-audit,known-dq}.md`, all stamped **Last verified 2026-05-22** = gold-cutover day). Diffed each verifiable claim against the live mart via redshift MCP (9 probes). Read-only; no agent edits.

## Findings — three buckets

### A. STALE — V1 landed the wiring, the caveat is now WRONG

| # | Doc claim (where) | Live reality | Severity |
|---|---|---|---|
| A1 | **ORWO revenue 100% NULL / "intended-populated not yet landed"** (sources.md maturity, mart-contract §4, coverage-audit) | ORWO `net_revenue_eur` **100.0% populated** (2025+ window) | HIGH — the most-repeated ORWO caveat is now false |
| A2 | **ORWO `destination_country` 100% blank / "no country slice possible"** (sources.md, mart-contract §4, coverage-audit country section, known-dq) | **0 of 2,071,489 ORWO rows blank** → fully populated; country slicing now works | HIGH |
| A3 | **Data floor 2024-01-01 all sources except ORWO** (mart-contract §1) | MIN `shop_order_created_date` = **2023-01-01** for Picturator, PicaAPI, PCS. ~8M Pict + ~1.67M PicaAPI rows live pre-2025 | MED — floor wrong by a full year; full-fact ≈18.07M vs 8.3M in the 2025+ window the docs reason about |
| A4 | **PicaAPI "data starts 2025-08"** (sources.md) | PicaAPI MIN 2023-01-01; 1.67M of 2.87M rows pre-2025 | MED — contradicts A3's own floor too |
| A5 | **`is_returned` undefined / "do not use, no agreed semantics"** (mart-contract §4, tables.md) | **2 distinct values, 67.4% populated** (5.88M of 18.07M NULL). Column now carries data | MED — needs a ruling: is returns now defined? (relevant — agent currently refuses return-rate questions) |

### B. STALE — numbers drifted (reload backfill / V1 churn); re-stamp

| # | Doc claim | Live | Note |
|---|---|---|---|
| B1 | `cost_source` dist 65.15 / 24.37 / 8.04 / 1.99 (**sums 99.55%**) | **invoice 67.82 / expected 26.57 / null 5.18 / avg 0.44** (sums 100%) | The 0.45% gap = the transient `invoice_estimate` 5th value (bank H2). **Not present now** — 4 values, 100%. Enumeration correct; distribution stale (reload pulled uncosted 8%→5.2%) |
| B2 | Coverage by source: Pict 86.7 / ORWO 68.7 / PicaAPI 93.9 (cost%) | Pict **92.0** / ORWO **74.6** / PicaAPI **95.0** | Mart-wide invoiced ≈ **88%**, up from documented ~85% |
| B3 | ORWO `weight_kg` ~47% NULL | **57.7%** NULL | Direction holds, number moved |
| B4 | 4 holes: ORWO POST 568K@0.4 / POST_DVF 170K@0 / MAERSK 98K@68.9 / ASENDIA 5.8K@0 | ORWO POST **392K@0.7** / POST_DVF **184K@0.0** / MAERSK **102K@75.9** / ASENDIA **94 rows@0.0** | Structural holes (POST, POST_DVF) hold; MAERSK improving; **ASENDIA effectively resolved** (5.8K→94) |
| B5 | ORWO ~2.5M shipments (2025+) | **2.06M** (full-fact 2.07M) | ORWO volume dropped ~450K through the reload (POST shrank 568K→392K) — observation, possible dedup tightening |

### C. SCHEMA DRIFT

| # | Doc claim | Live | Note |
|---|---|---|---|
| C1 | `fact_shipment_invoice_lines` **17 cols** + enumerated list (tables.md) | **18 cols** — new `source_table` (varchar, ord 18) not documented | Minor |
| C2 | "**four facts** / 128 cols across 4 tables (65+14+17+32)" (mart-contract §1, tables.md) | 5th table **`fact_truck_charges` (12 cols)** exists in `shipping_mart`; invoice_lines is 18 → 129 across 4 modeled tables | truck table deliberately out of agent scope (keepsake), but docs don't note it exists |

### D. CONFIRMED — still accurate (no change)

- `fact_shipments` = **65 cols** ✓ (resolves bank H3 "65-vs-63" — 65 is real; the "63 enumerated" was a doc prose miscount, not a mart gap).
- Cost-bucket invariant `SUM(11 buckets) == total_eur`: **0 violations / 12,181,501 rows** ✓.
- `cost_source` is exactly 4 values, **no `invoice_estimate`** ✓ (resolves bank H2 — it was transient during the reload).
- PCS `net_revenue_eur` **100% NULL** by design ✓.
- `fact_shipment_invoice_lines.shipment_id` ~0.82% → **0.85% NULL** ✓ (56.1M lines).
- POST_DVF / ORWO POST structural cost holes ✓ (still ~0%).

## Probes (redshift MCP, 2026-05-25, full-fact unless noted)

1. cost_source dist (full fact). 2. col counts / table (information_schema). 3. coverage by source (≥2025-01-01, = coverage-audit Probe 1). 4. data floor MIN/MAX/count per source. 5. invoice_lines column list. 6. bucket invariant + cost_summary rowcount. 7. NULL-by-design combined scan (is_returned, ORWO dest_country, ORWO weight, PCS rev). 8. 4 concentrated holes. 9. invoice_lines shipment_id null.

## Corrections applied (2026-05-25, CORRECT mode — principal approved)

Principal rulings: **A3 data floor STAYS 2024** (no change — the 2023 min dates are invoice-lag absorption, not the intended floor); **A4 PicaAPI "starts 2025-08" → 2024**; all other corrections proceed.

Edited out-of-tree `shipping-agent/reference/*.md` (5 files, +45/-39):
- **mart-contract.md** — cost_source dist re-stamp (67.82/26.57/5.18/0.44, +invoice_estimate-was-transient note); ORWO §4 revenue+dest_country landed, weight 47→58%; is_returned factual-only (populated but semantics unconfirmed, keep do-not-use); fact_truck_charges 5th-table note; stamps→05-25.
- **sources.md** — maturity table ORWO revenue+country landed, weight→58%; PicaAPI→2024; ORWO count 2.5M→2.1M; stamps.
- **coverage-audit.md** — by-source matrix re-stamped (Pict 92 / ORWO 74.6+rev100 / PicaAPI 95); mart-wide 85→88%; 4 holes (POST 392K@0.7, POST_DVF ~184K, MAERSK 75.9%, ASENDIA→94 resolved); ORWO country populated; by-month table flagged as 2026-05-22 read (not re-run).
- **known-dq.md** — is_returned note + POST_DVF count (surgical; carrier-ts content NOT restamped — not re-verified this pass).
- **tables.md** — invoice_lines 17→18 (+`source_table`); header 128→129; is_returned; ORWO weight→58%; ORWO count→2.1M.

**how_to.md NOT touched** (dirty `M` at 8de877b — sibling's/pre-existing; excluded from any commit). Live sibling jebrim-006248ef (demo-readiness read) pinged in comms; no collision (it's read-only + how_to.md; I'm reference/ only).

## State

Edits done, **commit/push to picanova HELD for principal go** (demo 2026-05-26 — these fix the A1/A2 stale-caveat demo risk the sibling flagged). Still open: **A5 is_returned semantics ruling** (made a conservative do-not-use-but-now-populated edit that doesn't depend on the ruling). Bank note (durable as-of-2026-05-25 reconciliation) held pending close.
