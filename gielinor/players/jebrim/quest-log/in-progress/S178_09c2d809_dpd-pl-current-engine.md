# S178 — current-contract DPD PL engine (`dpd_pl_current`)

**Session:** 09c2d809 · 2026-06-09 · Jebrim
**Ask:** Build the current-contract DPD PL engine per `NFE/.../carriers/PLAN_dpd_pl_current_engine.md` — fork the tender `dpd_pl/` engine, transcribe the current offer's two export flows, add per-parcel cheapest-flow selection, **validate against DPD invoiced actuals before routing on it**, then wire into `routing_2026q1/build_final.py` as a forward competitor and rerun.

**Status: DONE.** Engine `dpd_pl_current-1.0.0` built, validation gate passed, wired, rerun. Full technical record lives in the repo (source of truth): `NFE/projects/2_EU_tender_2026/2_analysis/carriers/dpd_pl_current/CLAUDE.md` + the PLAN status header.

## What was built

- `carriers/dpd_pl_current/` — forked the tender engine. TWO export HOME flows (Direct special-offer 6-country + MIX HOME 29-country), per-parcel cheapest-eligible-flow selection stamped in `service`. Bands 1/3/10/20/31.5 (no 6 kg). `extract_rates.py` transcribes the offer xlsx base columns → `rates_direct.parquet` (6×5) + `rates_mix.parquet` (29×5).
- Surcharge mechanism: fuel fixed 5% of base; flat = security €0.06 (energy fee €0.176 documented but toggled OFF — absent from invoiced actuals); conditional zone (island postcodes, reused PDF table) + customs (immaterial on the all-EU served book).
- 11/11 hand-calc fixtures pass.

## The validation gate (the load-bearing step)

`validate.py` — engine vs DPD POLAND invoiced actuals (66,059 parcels). Two findings resolved the PLAN's flagged sheet-vs-invoiced base gap:

1. **Energy fee absent from invoices** — invoiced `real_other_eur` ≈ €0.06 (security only), not the sheet's €0.236 net add-on. Excluded.
2. **~9% negotiated discount off sheet rates** (Niklavs-confirmed, validated). Faithful /5000 contract divisor + a 9% discount on base. *Discriminating test:* parcels where dim weight doesn't bind (so band selection is divisor-independent) are still ~5% below sheet → only a multiplicative discount can produce that, not a divisor. (An interim /8000 effective-divisor fudge was masking this real discount; superseded once Niklavs flagged the discount.)

**Result: aggregate −0.4% (within ±5%).** Main lanes NL 0.987 / AT 1.018 / BE 0.998 / LU 1.008 — all within ±2%. Explained outliers: FR +8% (sheet DPD-FR rates superseded by Chronopost; FR incumbent-priced anyway) and SE −20% (heavy 0.9%-volume lane).

## Routing result + the refuted thesis

Wired: registered in `cost_matrix.py`, rebuilt the 2026-Q1 matrix (5.31M rows), pointed the dpd_pl family's forward bid at `dpd_pl_current` (declined tender `dpd_pl` kept as counterfactual but excluded from the bid pool), reran `build_final.py`.

- **Saving 12.8% → 13.4% (+€17.3k/Q).** DPD grows 65,759 → 83,454 parcels.
- **The PLAN's IT/ES-off-UPS hypothesis is REFUTED.** DPD-current is *more expensive* than UPS on IT (€8.58 vs €7.38) and ES (€9.39 vs €7.59) — and Maersk/GLS dominate those lanes regardless. The ×0.84 proxy over-stated it. DPD's real wins: FR-off-UPS (€5.86 < €8.37) and near-PL/Direct-6 incumbent displacement.
- FR forward bids are over-priced vs DPD's own FR actuals (€5.86 vs €4.37, Chronopost) → +€17.3k/Q is a conservative floor.

## Open / flagged

- **UPS has NO GRI in the routing** — UPS bids at today_eur actuals, no ×1.05. The PLAN assumed UPS×1.05; it isn't wired. Doesn't change the IT/ES verdict (DPD loses even vs UPS-today there). Flag for the principal if the GRI should be applied.
- FR engine rates could be corrected to Chronopost actuals → would lift saving further.
- bi-analytics engine + wiring UNCOMMITTED (separate repo, principal-gated; held pending the incorporation discussion, which may revise wiring). Touched: `carriers/dpd_pl_current/*` (new), `cost_matrix.py`, `_decision_sets_2026q1.py`, `routing_2026q1/build_final.py`, regenerated `data/cost_matrix_2026q1/*` + `routing_*`.

## Close (S178, 2026-06-09)

No pending external actions. Brain close artifacts (this quest-log, the resume file, the discount-vs-divisor examine draft, comms CLOSING) committed at close; the bi-analytics engine/wiring stays uncommitted (principal-gated, pending the "where do we incorporate" discussion). Quest stays **in-progress** — deliverable shipped, open thread = incorporation scope + the UPS-GRI / FR-rate / discount-figure decisions in the resume file. Niklavs overrode my ÷8000 fudge → 9% negotiated discount (harvested: `examine/drafts/2026-06-09-discount-vs-divisor-discriminator.md` + cross-conv memory).
