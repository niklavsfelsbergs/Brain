---
quest: S163_ups-phase1-offer-triage
sid8: 0109840c
ts: 2026-06-08 16:00
open_dep: awaiting UPS Round-1 replies (Q1 fuel base, Q4 LPS threshold, Q6 peak schedule are the headline-blockers)
---

# UPS carrier assessment — resume

**Status:** in-progress. Phase 1 done; Phase 2 (calculator) is the next work.

**Where we are.** UPS offer triaged end-to-end. Carrier reference + cost tree + an 11-question verification-first Round 1 (dispatched to UPS 2026-06-08) all built. Two research anchors grounded the surcharge picture against the published tariff AND our real invoices — which revealed the hidden peak/demand layer and fuel ~20% (not the card's 35%). Phase-2 v1 assumptions locked.

**Next concrete step.** Build the Phase 2 calculator (PLAYBOOK Phase 2) for UPS:
1. **Assumption-independent scaffold first** (do this regardless of UPS replies): `1_offers/picanova/UPS/calculation/` per the playbook layout; SQL population pull (Picanova outbound, scope TBD at 2.1); extract the rate sheets + the `DE_ZONES` matrix to parquet; engine skeleton with billable-weight (÷5000, round up 0.5kg) + zone resolution (origin-PLZ→dest→zone) + base-rate lookup.
2. **Parameterize, don't bake:** fuel (flat 35% v1), peak/demand layer, LPS threshold — wire as parameters with the locked v1 assumed values. **Hold the headline cost number until Q1/Q4/Q6 replies land** (keepsake risk #1 — provisional-fuel collapse precedent).
3. Locked v1 assumptions: service = cheapest eligible; OML = €0; LPS = on (threshold pending Q4); line-haul = €0 placeholder; customs duties excluded; `ups` stream only.

**Files to read first (ordered):**
- `bi-analytics-main/NFE/projects/2_EU_tender_2026/1_offers/picanova/UPS/CLAUDE.md` (the reference + assumptions A1–A12)
- `.../UPS/questions_for_carrier.md` (the 11 + the locked our-side decisions; check for landed replies)
- `.../UPS/offer_summary/cost_calculation_tree.md`
- `players/jebrim/research/2026-06-08-ups-current-invoice-charge-profile.md` (real-invoice ground truth — the reconciliation)
- `players/jebrim/research/2026-06-08-ups-germany-2026-published-surcharges.md` (published book)
- `bi-analytics-main/.../1_offers/PLAYBOOK.md` Phase 2 + the Austrian Post `calculation/` worked example
