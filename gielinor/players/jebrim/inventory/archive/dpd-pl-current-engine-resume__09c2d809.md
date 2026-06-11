---
quest: S178_dpd-pl-current-engine
sid8: 09c2d809
ts: 2026-06-09 17:50
open_dep: incorporation-scope discussion (Niklavs) + bi-analytics commit gate + UPS-GRI/FR-rate follow-ups
---

## Status: deliverable shipped; open thread = where to incorporate the engine

The `dpd_pl_current-1.0.0` engine is built, validated (−0.4% vs DPD invoiced
actuals), wired into `routing_2026q1/build_final.py`, and the routing reran
(+€17.3k/Q). Done as specced. But Niklavs flagged a follow-up: *"we need to talk
about where we incorporate this engine"* — the routing is one consumer; there may
be others (full-year annualisation, decision report, carrier-overview, the
`5_shipping_savings` track). That conversation is the live thread.

## Next concrete step (for Niklavs)

Pick up the **"where do we incorporate this engine"** discussion. Candidate
consumers beyond `routing_2026q1/build_final.py` (already wired):
- the full-year annualisation step (S175's parked tail) — does current-DPD bid there too?
- `decision_report/` / `carrier_overview_v2/` — does the kept-DPD cost-basis need to flow through?
- `5_shipping_savings/engines/` — the one-shot re-rates DPD note says are NOT used; does this replace them for DPD?
- whether `cost_matrix.py` (the 2025/full-year track, not just 2026q1) should also register `dpd_pl_current`.

## Open decisions awaiting Niklavs

1. **Commit the bi-analytics engine?** All engine + wiring changes are UNCOMMITTED
   in the separate `bi-analytics-main` repo (principal-gated; the incorporation
   discussion may revise wiring, so held). Brain close artifacts committed separately.
2. **UPS GRI** — `build_final.py` prices UPS at today_eur actuals, NO ×1.05. S175's
   plan intended UPS×1.05; it isn't wired. Apply it? (Doesn't change the IT/ES verdict.)
3. **FR rates** — engine over-prices FR (€5.86 vs DPD's own actuals €4.37, Chronopost).
   FR-incumbent is kept at actuals; FR-off-UPS wins booked at €5.86 → +€17.3k is a floor.
   Correct FR to Chronopost actuals for a higher (truer) saving?
4. **Discount figure** — used the contractual 9% Niklavs cited (8% centres exactly;
   9% lands −0.4%, conservative). Pin the exact contractual % if it differs.

## Files to read first

- `bi-analytics-main/NFE/projects/2_EU_tender_2026/2_analysis/carriers/dpd_pl_current/CLAUDE.md` — full technical record.
- `.../carriers/PLAN_dpd_pl_current_engine.md` — status header (BUILT+VALIDATED+WIRED) + the refuted IT/ES thesis.
- `.../carriers/dpd_pl_current/validate.py` — the validation gate (rerun anytime).
- `quest-log/in-progress/S178_09c2d809_dpd-pl-current-engine.md` — session narrative.
- S175 resume: `inventory/routing-cost-basis-review-resume__6c5170d1.md` — the parent plan + annualise tail.

## Key facts to carry

- Sheet-vs-invoiced gap = **~9% negotiated discount** (Niklavs-confirmed), NOT a dim
  divisor. Faithful ÷5000 contract divisor + 9% discount on base. (Interim ÷8000 fudge superseded.)
- Energy fee (€0.176) documented but NOT invoiced → excluded.
- IT/ES-off-UPS thesis REFUTED: DPD pricier than UPS there (€8.58/€9.39 vs €7.38/€7.59); Maersk/GLS win those lanes.
- Tender `dpd_pl` engine stays materialised as the declined-offer counterfactual; excluded from the routing bid pool.
