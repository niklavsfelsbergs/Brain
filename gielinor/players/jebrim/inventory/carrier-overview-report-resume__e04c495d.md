---
quest: S150_carrier-overview-v2
sid8: e04c495d
ts: 2026-06-05 13:30
open_dep: next phase queued (final carrier setups / portfolio scoring) + 1 small report reword; v2 deliverable shipped + committed
---

# Resume — Carrier Overview v2 — SHIPPED; next phase = final carrier setups

## Where we are
v2 carrier-overview is **built, vs-today-extended, internally consistent, and committed** to bi-analytics `main` (`510fc67`, 5 commits f70226c→510fc67; NOT pushed). Deliverable: `bi-analytics-main/NFE/projects/2_EU_tender_2026/2_analysis/carrier_overview_v2/{carrier_overview.html, exec_brief.html}`. The "vs Today" baseline = 2026-Q1 real invoices (UPS+Maersk, PCS PL, OML netted / LPS kept). Headline: tender beats today on 33/46 segments (~89% book); fails on ~11% — keep Maersk on FR + CH/ROW bulky.

## Next concrete step
The principal wants to move to **investigating actual potential final carrier setups** — i.e. combine the per-segment winners (best new offer + whether it beats today) into signable **4–6-carrier portfolios** (hard cap 6), respecting: keep current Maersk on FR; the three new carriers (Hermes/FedEx/DHL Express) carry irreducible model risk (never invoice-measurable pre-signing — confirmation #1); Güll HELD (awaiting reply); DB Schenker stays for freight. The companion **decision report** (`2_analysis/decision_report/` + `decision_scorer.py`) is the portfolio-scoring tool — this overview is its input. Start from the natural set the segment map implies (DHL Paket + Maersk + DPD + GLS + Hermes?) and test variants vs today.

## Small report fix queued (low priority)
Reword the **new-carrier caveat** across the report: it currently implies "validate before banking," but per confirmation #1 these carriers can never be invoice-measured pre-signature — so it's irreducible model risk, not a closable validation gap. Touch: methodology + the 3 new-carrier hands (hermes/fedex/dhl_express) + EXEC notes.

## Files / paths to read first
1. `bi-analytics-main/.../carrier_overview_v2/verification/ledger.md` — full audit trail (Phase 1 reconciliation + serving map + vs-today + LPS/OML).
2. `.../carrier_overview_v2/lib/{segments,competitive_map,build_summary,build_actuals}.py` — the pipeline.
3. `.../carrier_overview_v2/_data/competitive_summary.parquet` — per-segment winner + today + beats_today (the backbone).
4. `.../2_analysis/decision_report/` + `decision_scorer.py` — the portfolio scorer for the next phase.
5. This session's quest-log: `quest-log/in-progress/S150_e04c495d_carrier-overview-v2-build.md`.

## Recovery checkpoints
bi-analytics revert points: `510fc67` (final) · `b3904ee` (pre-OML-on-hands) · `beb32aa` (full vs-today) · `f70226c` (vs-today column) · `e475efb` (v2 no-baseline). brain: this close commit.

## No pending external actions.
