---
quest: S150_carrier-overview-v2
sid8: e04c495d
ts: 2026-06-05 13:30
open_dep: next phase queued (final carrier setups / portfolio scoring) + 1 small report reword; v2 deliverable shipped + committed
---

# Resume — Carrier Overview v2 — SHIPPED; next phase = final carrier setups

## Where we are
v2 carrier-overview is **built, vs-today-extended, internally consistent, and committed** to bi-analytics `main` (`510fc67`, 5 commits f70226c→510fc67; NOT pushed). Deliverable: `bi-analytics-main/NFE/projects/2_EU_tender_2026/2_analysis/carrier_overview_v2/{carrier_overview.html, exec_brief.html}`. The "vs Today" baseline = 2026-Q1 real invoices (UPS+Maersk, PCS PL, OML netted / LPS kept). Headline: tender beats today on 33/46 segments (~89% book); fails on ~11% — keep Maersk on FR + CH/ROW bulky.

## Next concrete step — EXECUTE THE PLAN
**Read `bi-analytics .../2_analysis/decision_report/PLAN_final_setups_2026q1.md` in full first — it is the authoritative spec for this phase** (written end of this session; context was full → handover). Summary: score the candidate final carrier setups (portfolios, cap 6) on a **2026-Q1 actual-invoice "today" basis** in the **decision report**, then summarize the chosen setups in the carrier overview. Setups scored LAST.

Phases: **A** build the 2026-Q1 cost matrix (full population pull via shipping-agent → engines + real invoices, OML-netted; the Maersk-FR fix falls out — 27.6k @ €4.72) → **B** re-point `decision_scorer.py` at it (drop the S120 engine-reprice-baseline hack; incumbent bid = real 2026 invoice) → **C** reconcile vs the overview → **D** define + score the candidate setups (with principal) → **E** summarize in the overview.

**Decisions locked:** all invoiced "today" costs = 2026-Q1 actuals; setups live in the decision report, summarized in the overview. **Open decisions to resolve (in the PLAN, don't skip):** (1) **the two-Maersks problem** — current-Maersk-FR vs new-Maersk-EU must be modelled as two carriers or the FR finding breaks; (2) new-carrier bid bias (engines under-price, new carriers uncorrectable); (3) Q1-vs-annualized volume basis. Also queued: the new-carrier-caveat reword across the overview.

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
