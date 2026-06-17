---
quest: S250_ups-routing-investigation
sid8: bd2469b9
ts: 2026-06-17 (session close)
open_dep: margin backbone not built — needs instrumenting build_final.py for routing-faithful per-cell carrier margins
---

# Resume — UPS routing investigation (per-country)

**Status:** in-progress (multi-session; CH pilot landed, structure + decisions locked).

**Where we are.** Reframed the "UPS negotiation / what moves off UPS" work into a **per-country routing investigation** that validates the no-Hermes plan's cell grid and produces an ops-ready routing table. All deliverables live in the **separate `bi-analytics-main` repo** (uncommitted):
`NFE/projects/2_EU_tender_2026/2_analysis/routing_investigation/` → `CH.md` (pilot, complete-ish, status open) + legacy `ups_investigation/ups_migrating_cohorts.md` (holds the AU draft).

**Next concrete step.** Two open threads, principal's pick:
1. **Build the margin backbone (D7).** Per-cell carrier ranking + margin-to-runner-up, **routing-faithful** — by *instrumenting `build_final.py` to export its own candidate costs* (keep = invoice×1.05 GRI, others = engine bid, ≥99% coverage, 2% switch threshold, DBS pin), NOT a reimplementation (a naive cheapest-engine margin misleads ~50% on UPS cells — engine over-prices UPS). This unlocks the "where else could each cell go + swing list" class of questions.
2. **Continue countries.** CH is still **open** (more questions landing); else next-largest is **DE** (66,622 parcels, UPS-vs-DPD). Carry the AU draft from `ups_investigation/ups_migrating_cohorts.md` into `AU.md` when AU; then retire that legacy file.

**Locked decisions (this session):**
- Primary axis = **country**, one at a time; **all carriers** per country (not UPS-only); validate-and-refine `routing_rules.csv`, don't rebuild.
- Per-country file (`routing_investigation/<CC>.md`); structure = §1 migration flow (today→plan, all carriers) · §2 fat cells (≥50, packagetype×weight grid + carrier max-envelope table) · §3 thin tail (carrier-level only) · §4 mechanics · §5 questions log · §6 pending. A country "closes" when its Open-questions list is empty.
- Fat/thin floor = **50 parcels** (start; ~98% of volume in ~466 fat cells; recalibrate to coverage-based ~90% later). Thin tail stays **visible**, not rule-hidden.
- Cost bases: today = `final_shipping_cost_eur` (gross, OML netted in routing); **UPS keep = invoice×1.05, NOT engine price**; plan = engine `cost_total_eur`; saving = keep_ref − routed.

**Key findings (verified, in CH.md):** UPS keep-cost basis (engine over-prices UPS ~50%); Warenpost envelope = ≤1kg & 35.3×25×10 (eligibility, 0 cost-crossover); carrier max-envelope caps (UPS 70kg/274/419, DHL 31.5/200/300, DPD 33/175/300, Maersk-ROW 30/121/266, DBS freight catch-all); **L+girth is the binding constraint in CH** (oversize → UPS/DBS). AU: UPS can't bid (offer EU-only), WW-Economy stays on price; the digest's "AU stays on UPS" is wrong (49% moves).

**Files to read first (next session):**
- `bi-analytics-main/NFE/projects/2_EU_tender_2026/2_analysis/routing_investigation/CH.md` (the pilot + locked structure).
- `…/2_analysis/routing/build_final.py` (cell logic: CELL=dest×packagetype×1kg, keep vs engine, SWITCH_MIN_PCT=0.02, DBS pin) — the instrument target for the backbone.
- `…/2_analysis/routing/no_hermes/routing_rules.csv` (the cell grid) + `data/cost_matrix_2026q1/` (the correct matrix; NOT the stale flat `cost_matrix.parquet`).
- legacy `routing_investigation/ups_investigation/ups_migrating_cohorts.md` (AU draft to carry).

**Open for principal:** the bi-analytics `routing_investigation/` work is **uncommitted** (separate repo, NFE standing-commit authorization applies) — checkpoint-commit it, or keep iterating uncommitted?
