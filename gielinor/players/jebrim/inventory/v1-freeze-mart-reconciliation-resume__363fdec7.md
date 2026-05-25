# Resume — S068 V1-freeze mart-knowledge reconciliation

**Quest:** `quest-log/in-progress/S068_363fdec7_v1-freeze-mart-knowledge-reconciliation.md`

## Where we are

DONE + SHIPPED. Corrections committed + pushed to picanova/main (`8de877b..393fdcf`, 5 `reference/*.md`, +40/-38). how_to.md excluded (sibling's WIP). Session wrapped 2026-05-25.

## Next concrete step

Open follow-up only: **A5 `is_returned` semantics ruling** — if returns got defined in V1, flip the conservative do-not-use edit to usable (reference/*.md + maybe how_to.md return-rate handling). Bank draft harvested: `bank/drafts/notes/projects/shipping-mart-v1-freeze-reconciliation-2026-05-25.md` (promote at alching; retires the 2026-05-21/22 stale siblings). Propose S068 →completed/ once A5 lands. Brain repo commit pending principal go (scoped to jebrim namespace + comms + intent + bank draft).

## Corrections applied (principal rulings folded in)

- [x] A1 — ORWO revenue 0%→100% (mart-contract §4, sources.md maturity, coverage-audit)
- [x] A2 — ORWO destination_country blank→fully populated (same 3 + known-dq cross-ref)
- [~] A3 — data floor: **NO CHANGE, stays 2024** (principal ruling; 2023 rows = invoice-lag absorption)
- [x] A4 — PicaAPI "starts 2025-08" → **2024** (sources.md; principal ruling — not 2023)
- [x] A5 — is_returned: factual-only edit (populated ~67%, 2 values, semantics unconfirmed, KEEP do-not-use). **Still needs principal ruling** on whether returns is now defined.
- [x] B1 — cost_source dist re-stamp 67.82/26.57/5.18/0.44 + invoice_estimate-transient note (mart-contract §3)
- [x] B2 — coverage matrix re-stamp + mart-wide ~88% (coverage-audit)
- [x] B3 — ORWO weight ~47%→~58% (mart-contract §4, sources.md, tables.md)
- [x] B4 — 4 holes re-stamp (coverage-audit + known-dq POST_DVF count)
- [x] C1 — invoice_lines 17→18 cols + `source_table` (tables.md)
- [x] C2 — fact_truck_charges 5th-table note (mart-contract §1, tables.md header)
- [x] Re-stamped edited files → 2026-05-25 (NOT known-dq carrier-ts content — not re-verified)
- [ ] Harvest durable bank note: as-of-2026-05-25 V1-freeze reconciliation (held for close)

## Confirmed accurate (no action)

fact_shipments 65 cols (H3 resolved); bucket invariant 0/12.18M (holds); cost_source 4 values no invoice_estimate (H2 resolved — was transient); PCS rev 100% null; invoice_lines shipment_id 0.85% null; POST_DVF/ORWO-POST structural holes.

## Coordination

OPEN + UPDATE + ping to @006248ef posted in gielinor/comms/active.md as jebrim-363fdec7. Sibling read-only on demo prep; how_to.md is its/dirty file — left untouched. Brain repo uncommitted (parallel-session norm) — no brain commit without principal go.
