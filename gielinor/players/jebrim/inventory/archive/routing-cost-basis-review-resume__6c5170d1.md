---
quest: S175_routing-cost-basis-review
sid8: 6c5170d1
ts: 2026-06-09 15:45
open_dep: DPD-current engine build + routing refactor pending (next-session work)
---

# Resume — EU-tender routing cost-basis review (S175)

## Status
in-progress. Per-carrier forward-pricing decisions made; DHL + DPD analysis done; DPD-current engine plan written. Build + routing refactor pending.

## Where we are
Decided each carrier's forward pricing basis for a routing rebuild. DHL validated → price off engine. DPD → keep current contract, decline new offer, build a current-contract engine (plan written). UPS → actuals ×1.05. Maersk/DBS/Hermes unchanged. Baseline = 2026-Q1 invoiced actuals.

## Next concrete step (continue once the DPD-current engine is available)
1. **Build + validate the current-DPD-PL engine** per `2_analysis/carriers/PLAN_dpd_pl_current_engine.md`. Validation gate: engine vs invoiced actuals on the 7 served lanes within ~±5% by component; **resolve the sheet-rates-above-invoiced gap** before trusting it on the unserved lanes.
2. **Refactor** `routing_2026q1/build_final.py`: DHL→engine, UPS→actuals×1.05, DPD→current engine (compete all lanes), Maersk FR-actuals+EU-engine, DBS/Hermes unchanged; baseline = 2026-Q1 invoiced actuals.
3. **Rerun + diff** vs the current €411k saving (expect it to drop — DHL/UPS/DPD priced higher than old actuals-keep).
4. **Then annualise** (separate re-weight: peak / Q4 mix / forward fuel).

## Files to read first
- `2_analysis/carriers/PLAN_dpd_pl_current_engine.md` — the engine spec + handover
- `quest-log/in-progress/S175_6c5170d1_routing-cost-basis-review.md` — full record + decisions
- `routing_2026q1/build_final.py` — the routing builder to refactor
- `routing_2026q1/routing_report.py` — the report to rebuild

## Watch-outs
- bi-analytics-main is a SEPARATE repo (principal-gated commits); the plan file is uncommitted there.
- DHL Sperrgut on WICKEL (€19k/Q) accepted as-is — note in docs, don't "fix".
- DPD sheet rates run ABOVE invoiced actuals on served lanes (FR invoiced €4.07 vs sheet €4.61) — the engine validation must resolve this or it under-states DPD's reach.
- Niklavs may ask DPD to extend the Direct/special flow to AT/FR/LU in any new contract (the explicit ask).
