# S185 — EU-tender report sign-off + DPD carrier-only investigation

**Player:** Jebrim · **sid8:** e9821cdf · **2026-06-09**

## What this session was

Started as a question about the routing report's DPD-PL "carrier-only 1,887" bucket; became a full pre-commit **sign-off pass** on all three EU-tender reports and a multi-file prose reconciliation.

## Turn log

1. **Q: how is "carrier-only" defined in "what each carrier takes"?** Grounded in the [[S166_f82b01df_routing-service-split-build|S166]] build record + `service_labels.py` (`service_label(None → "carrier-only")`). carrier-only = a routed parcel with null `service` (no named modeled product), costed at actuals. UPS/DBS/Maersk-FR fully carrier-only.

2. **Q: what are the DPD 1,887 carrier-only?** Pulled live: `routing_assignment.parquet` — DPD split 80,583 Direct Home / 6,515 Mix Home / 1,887 carrier-only. Profiled: 1,806 PL-domestic + 81 non-PL.

3. **Q: were these shipped with DPD even though they don't fit?** Verified `cur_inc` via `cost_matrix_2026q1` — **all 1,887 actually shipped DPD** (cur_inc=dpd_pl), kept on DPD at actuals. **Corrected my own earlier "they don't fit" framing** — carrier-only is a *model* gap, not a physical misfit.

4. **Q: why can't the engine price them?** Verified `reject_reason` from the matrix: **1,806 `country_not_served`** (all PL — the `dpd_pl_current` engine is export-only, no PL-domestic rate table) + **81 `over_max_weight`** (dimensional/billable weight 33.5–34.4 kg over the 33 kg cap; actual median 4 kg → light-but-bulky). Zero girth/length. Saved bank draft `bank/drafts/notes/projects/2026-06-09-dpd-pl-current-engine-export-only-gap.md`.

5. **"reports are good — what do you think?"** Gave a grounded second opinion (not a rubber stamp): analytically sound but uncommitted + FR-floor caveat + consistency loose ends. Niklavs chose a **sign-off pass**.

6. **Sign-off pass — 3 dwarves** (one per report, reconcile prose→parquet + caveat check). Traces: `signoff-{routing-report,carrier-overview,decision-report}__e9821cdf_dwarf.md`. Result: numbers tie to the euro everywhere, but **prose drift across all 3** (the [[S180_4766eb11_dpd-current-report-refresh|S180]] "derived prose drifts from data" class, recurring).

7. **"fix all of it."** Discovered carrier_overview drift was deeper than counts — inserting dpd_pl_current (16 wins) cannibalized specific segments from fedex/gls/dhl_paket/guell, so their per-segment *narratives* (not just counts) were stale. Re-authored against the parquet:
   - **carrier_overview** (sections/*.md + EXEC dict): fedex 1→**0** mean-wins + "cheapest on 9"→**7** + fixed a pre-existing FR-Bulky/Standard mislabel; gls 5→**2** wins (both ROW, no hollow) + "9 within-10%"→**4**; dhl_paket 10→**7** (FR/Benelux Std → dpd_pl_current); guell 10→**9**; maersk "the most"→**second-most (14)**.
   - **decision_report** (report_2026q1.py): Hermes card no longer calls the €389,937 keepfr set "the leading ≤6 candidate" (the €430,055 all-renewals set is the lead); added **FR-floor caveat**.
   - **routing_report** (routing_report.py): added the **carrier-only/PL-domestic caveat** to the DPD card.

8. **Rebuilt all 3 HTMLs (exit 0) + verified:** zero stale win-counts remain (surviving "wins the most" = dpd_pl_current's correct claim); corrected counts in both carrier_overview + exec_brief; headline €377,471 / 12.8% ties; both caveats render.

## Decisions

- carrier-only is a **modeling-layer label** (engine coverage), not a physical-routing fact — verified against `cur_inc`.
- Hands cards (`_data/hands/*_card.md`) are **stale but NOT rendered** (build_report reads `sections/*.md`) — flagged for a future regenerate/delete, not blocking.
- Re-derived win-counts using reproducible parquet definitions (winner col / `within` flag / cheapest_modal); off-pace via eligible−within.

## No pending external actions.

The bi-analytics report changes are **complete but UNCOMMITTED** (separate repo, principal-gated) — that's an open dependency, not a dangling pending action.
