# S230 · EU Tender — no-Hermes + Güll report (six-carrier variant)

**Player:** Jebrim · **sid8:** b94d4675 · **Started:** 2026-06-12

Continuation of [[S225_9f716f1f_guell-2.0.0-build]] / [[S228_50e52247_guell-no-hermes-portfolio-marginal]]. Built the standalone six-carrier (no-Hermes + Güll) management report that [[S228_50e52247_guell-no-hermes-portfolio-marginal|S228]] queued.

## What was asked

Build `final_report_no_hermes_with_gull/` in `bi-analytics-main/NFE/projects/2_EU_tender_2026/2_analysis/`, templated on `final_report_no_hermes_v2/` — the 5-carrier no-Hermes portfolio plus Güll (guell-2.0.0) as a standalone "Carrier Recommendation" beside the existing 5-carrier one. Stats builder + report; deck optional. bi-analytics edits stay UNCOMMITTED (principal's commit-go).

## What shipped

New folder `final_report_no_hermes_with_gull/` (4 files, all on disk, bi-analytics untracked):

- `build_stats_no_hermes_with_gull.py` — templated from `final_report_no_hermes/build_stats_no_hermes.py`. Deltas: `FINAL` set +`guell`; `FAMILY_TO_ENGINE` +`{"guell":"guell"}`; offer-mask +`guell`; the published-5-carrier `base_ann` equality assert **re-anchored** (dropped the hard assert; `d_x` now reported as Güll's marginal; internal `do_nothing−plan==base_q1` assert kept and passes).
- `stats_no_hermes_with_gull.json` — the data.
- `report_no_hermes_with_gull.py` / `.html` — six-carrier "Carrier Recommendation", v2 framing, renders clean (36 KB).

## Numbers (this report's conservative basis: UPS-on-engine, DBS-pinned)

- **Headline €1,139,121/yr (7.55%)** on €15.08M spend.
- **Güll net marginal +€163,097/yr** over the 5-carrier €976,024 floor — came out **~equal** to the +€163,897 decision-set PAPER ([[S228_50e52247_guell-no-hermes-portfolio-marginal|S228]]), **not smaller as the resume predicted**. Different pipeline, same number by coincidence; the DBS-pin neutralizes the decision-set "DBS sliver" artifact by construction.
- Güll routes **87,236 parcels/yr** (CH 44,270 / AT 42,966 — note this **inverts** the decision-set's AT 79k / CH 32k; q1-routing population + UPS-on-engine shift the competitive field). Gross offer saving €205,479; net marginal €163,097 (the gap is volume taken from Maersk/UPS/DPD).
- Tiers reconcile: confirmed €648,892 + offer-based €490,228 (Maersk-EU €284,750 + Güll €205,479) = headline. Bridge reconcile Δ€0.0000; flow legend reconciles exactly (€1,227,620 − €47,305 Direct-Link − €41,194 peak = €1,139,121).

## Verification

- guell routability proven before building: in `_ENGINES`, `ENGINE_TO_CARRIER_ID`, family `guell`; 34,931 eligible Q1 rows; one clean service per shipment (`at_parcel`/`ch_postpac`/`ch_bulky`), no join fan-out.
- Stats + report both ran clean; no unrendered f-string tokens in HTML; 150/pallet flag present; headline reconciles.

## Judgment calls (flagged to principal, not corrected)

1. **Framing** — kept six-carrier total as headline (per "headline reconciles") but gated Güll hard: dedicated Güll panel (PAPER +€163k vs **defensible floor €60–120k**), the 150-parcels/pallet density callout (~±€40k per 50 parcels, pending logistics-manager number, "revising = re-run engine prices not just text"), strongest new-carrier caveat in §06. Offered the alternative (Güll fully outside the headline) as a small edit.
2. **Deck skipped** — principal said "only if wanted"; the three deliverable criteria met without it. Offered to template it.

## Pending external actions

None pending on the agent side. **Principal owns:** the bi-analytics commit (separate repo, their go) — deliberately left uncommitted per the brief.

## Decisions

- Re-anchored the `base_ann` cross-check rather than asserting the published 5-carrier figure (adding Güll moves the total; the delta IS the marginal).
- Güll → offer-based tier (it's a new written offer like Maersk-EU; all eligible rows carry a non-null service → captured cleanly).

## Next

Principal flagged the **next conversation = linehaul (density / parcels-per-pallet) estimation again** — the 150/pallet gate that firms Güll's marginal. See the resume file for the carry-forward.
