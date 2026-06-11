---
quest: carrier-overview-report (EU tender — manager-facing carrier report)
sid8: d691c033 (planned) → executed in continuation session e04c495d 2026-06-05
parent_sid8: e59202cf
ts: 2026-06-05
open_dep: v2 BUILT + verified end-to-end (Phases 0–7). Awaiting principal eyeball of the HTML + commit authorisation. NOT committed, NOT pushed.
---

# Resume — Carrier Overview v2 — BUILT & VERIFIED (Phases 0–7 complete)

## Where this is
- **v2 EXECUTED end-to-end** in `bi-analytics .../2_analysis/carrier_overview_v2/`. Phase 0 (8 decisions signed) → Phase 1 (9-dwarf contract extraction, all reconciled by me against `constants.py`) → Phase 2/3/4 (segment model + competitive map + reconciliation) → Phase 5 (9-dwarf hands) → Phase 6 (synthesis) → Phase 7 (render + verify).
- **Deliverables:** `carrier_overview_v2/carrier_overview.html` (113 KB) + `exec_brief.html` (16 KB).
- **v1 marked SUPERSEDED** in `carrier_overview/PLAN.md` (kept, archive-discipline).

## The build (all gated, every number traced)
- **Decisions:** `carrier_overview_v2/DECISIONS_PHASE0.md` (X=10%+gap, fold<2%, no cap/flag>7, single-source DROPPED, keep 9 lanes, friendly+predicate names, full-yr vol + Q1 cost, girth re-derive).
- **Verification spine:** `verification/ledger.md` (Phase-1 reconciliation + serving map + P2/3/4 + final attestation) + `verification/phase1/<carrier>.md` (9) + `verification/phase3_reconciliation.md` (every winner-flip → contract cause, no unexplained flips).
- **Code:** `lib/segments.py`, `lib/competitive_map.py`, `lib/build_summary.py`, `lib/build_hand_cards.py`, `build_report.py`. Data in `_data/*.parquet`. Hands in `sections/<carrier>.md`.

## Headline findings (decision-grade)
- Plan's thesis confirmed: **DE flips DHL Paket (Standard ≤2 kg) → Hermes/GLS (Bulky)** — the €20 Sperrgut cliff (`d_max>120 ∨ d_mid>60 ∨ d_min>60`, 20.4% of book) that v1's blended average hid. Every flip contract-explained.
- **IT/Iberia → Maersk** (gross-only flat card wins voluminous Bulky). **AT/CH → Güll but HELD** (no carrier reply — provisional; maersk/dhl_express firm fallbacks). **Benelux → DPD**; **FR/Nordics → DPD/FedEx/GLS**.
- **Mean-vs-per-parcel-cheapest divergence is intrinsic** (tested finer grids — worsens it). Both lenses reported; ÷divisor carriers (esp. FedEx) cheap on the typical compact parcel, costly on the voluminous tail.
- Corrections the empirical pass caught: dhl_paket serves ALL lanes (not DE-only); austrian_post wins ZERO segments.

## Next concrete step
1. **Principal opens `carrier_overview_v2/carrier_overview.html`** (+ `exec_brief.html`) — visual eyeball; the only layer not machine-verified (no GUI in-session).
2. **Commit** on authorisation (pathspec-scoped: `carrier_overview_v2/` + the v1 SUPERSEDED header). NOT pushed.
3. Optional follow-ups: get the Güll reply to firm AT/CH; close the Maersk-FR rate-card gap; EU-tender doc Step-8 cascade if any canonical status table is affected.

## Checkpoints
- bi-analytics: uncommitted working tree (v2 folder + v1 PLAN header). brain: this resume + comms OPEN + quest-log.
