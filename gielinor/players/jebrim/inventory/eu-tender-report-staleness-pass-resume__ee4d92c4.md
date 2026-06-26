# EU tender — report staleness pass (resume)

**Session:** ee4d92c4 · 2026-06-11 · Jebrim · autonomous (principal off)
**Ask:** "do a pass on which reports are now outdated and fix them. Don't touch the 2 final reports."

## What I found (full deliverable map)

Repo: `bi-analytics-main/NFE/projects/2_EU_tender_2026/2_analysis/`

- **PROTECTED — not touched** (per instruction): `final_report/` + `final_report_no_hermes/`. Both are the *freshest* artifacts (06-11 23:34, post-everything) — they're the authoritative current canon.
- **FRESH / current** (post-UPS cascade S208–S210, left alone): `decision_report` (06-11 20:57), `carrier_overview_v2` (20:36), `routing_2026q1/routing_report` (19:39), `annual_2026/annual_report` (19:39), `result_investigation/*` (all 06-11), `routing_2026q1/validation/db_schenker/`.
- **STALE & active → FIXED:** `management_briefing/eu_tender_2026_briefing.html` (was 06-09, pre-UPS). The only report that was *meant* to be current but wasn't.
- **Superseded historical artifacts — intentionally NOT touched** (reviving them would be wrong; flagged, not fixed): `carrier_overview/` **v1** (06-04, replaced by v2), `cross_carrier_view.html` (06-03), `switch_list_2026q1/switch_report.html` (06-06, **orphaned** — no cross-refs), `decision_report/routing_explained*.html` (05-29), `carriers/*/migration_plan.html` (05-13/28, Phase-1 method).

## What I fixed — the management briefing

Rebuilt it as a C-level simplification of the **untouched final_report** (read-only source for every figure + narrative). The old deck's whole story was dead: Hermes 68k→**5–26k parcels**, UPS 30k→**357k** (now "keep reduced", not "migrate away"), headline €377k Q1 → the current two-part annual frame.

New deck (12 slides, same reveal.js chrome/design preserved):
- **Headline = €1.91M/yr (12.7%)**, split into **base €976,024/yr (sign now) + gated oversize module €932,683/yr** (Hermes + DB Schenker reroute, after the dimensions check).
- Savings basis = **do-nothing @2026 rates (€15.08M)**, matching the rest of the suite. Q1 measured anchor €395,197 kept as support.
- Portfolio, decisions, risks, asks all re-derived from final_report §01–06. Every figure sourced in speaker notes.
- Verified: 0 stale numbers remain; tags balanced; slide-8 double-count (reprice vs UPS-source) fixed → clean reprice/reroute cut (€404k / €595k / €918k).

## ⚠️ One decision for you to confirm on return

I moved the deck from **Q1-only** (its old deliberate frame) to the **annual two-part** frame, to match the canonical final_report. If you specifically want the C-level deck to *lead* with the Q1 number for a particular audience, that's a one-call revert — say so and I'll reframe. Otherwise it's consistent with the suite.

## Not committed

Working-tree change only (`management_briefing/` is untracked). **Did not commit** — no authorization, and a C-level deck rebuilt on a reframe should get your eyes first. Review, then commit when ready.
