# S219 — EU tender final-report content pass + v2 builds

**Session:** e0eb59c8 · **Date:** 2026-06-11 · **Player:** Jebrim
**Mode:** started autonomous (review pass, Niklavs offline) → then interactive (he returned, directed the v2 builds).

## The ask
Editorial/content pass on the EU-tender **final reports**: what's in them, what's redundant, what's
vital-but-missing, callout-box audit (add/remove), plus a new idea — model the savings if the setup goes live
**2026-08-01**. Niklavs asked me to state my understanding, then completed the rest unattended.

## What I did
- Scoped to the live final-report family: `final_report/` (main), `final_report_no_hermes/`, `annual_2026/`.
  Excluded stale `decision_report/`, `management_briefing/`, `carrier_overview*`.
- Read all three renderers + `final_stats.json` + `annual_stats.json` live.
- **Verified the numbers are current** (the [[S194_907d4e63_eu-tender-holdup-pass-and-project-rating|S194]] resume's pre-UPS base €420,218 / module €577,502 are stale —
  reports were regenerated post-UPS-cascade; main & annual now reconcile to the euro: base €976,024 /
  module €932,683 / total €1,908,707 / 12.7%).
- Computed the 2026-08-01 stub-year saving from the per-country seasonal shape.
- Wrote the review deliverable to the repo (working tree, **uncommitted**):
  `bi-analytics-main/NFE/projects/2_EU_tender_2026/2_analysis/final_report/REVIEW_2026-06-11_content-pass.md`

## Findings (headline)
- **Vital gap (the one that matters):** no report answers "what does 2026 actually bank?" — all are steady-state
  run-rate. Niklavs' go-live idea fixes it.
- **Go-live 2026-08-01 stub year ≈ €0.97M full plan / ≈ €0.49M base** — that's **51% of the €1.9M run-rate from a
  5-month stub**, because Aug–Dec = **52% of annual volume** (Q4 peak: Nov+Dec alone = 33.5%). Naïve 5/12 (€0.80M)
  understates by ~€0.18M. Recommended placement: annual report §02 monthly curve (shade Aug–Dec) + main report §03
  callout. Pairs with a transition-timeline gap (G2).
- **Redundancy:** main §03 has 8 money tables for one €1.9M; `totals_table` is a strict subset of `bridge3_table`
  (cut it); `tier_bar`+`structure_table` merge. No-Hermes report re-renders shared methodology — slim to a pointer.
- **Callouts:** all load-bearing; the "Hermes + reroute = one decision" story is told ~3× in full — tighten to
  once. One to add (timing). Annual report callouts/ledger: leave alone.
- **Coherence flag (not asked, surfaced):** module is now 97% the DBS reroute; Hermes' standalone other-lanes
  uplift collapsed to €14k post-UPS, and the no-Hermes report shows the reroute survives without Hermes. The real
  tie is the **dimensions check**, not Hermes↔reroute. The §02/§05 prose reads like it predates the UPS cascade —
  recheck.

## Then: built TWO v2 reports (Niklavs returned, said "implement all the changes as a v2", then "i wanted the no hermes version, make that as well")
- `final_report_v2/` (`final_report_v2.py` → `final_report_v2.html`, 33 KB) — main report, all 11 review changes.
- `final_report_no_hermes_v2/` (`report_no_hermes_v2.py` → `report_no_hermes_v2.html`, 24 KB) — no-Hermes, same treatment.
- Both carry: NEW §04 go-live/stub-year cut (by-start-month table + transition sequence + caveats), §03 trim (cut
  `totals_table`, matrix→pointer; main also merged tier_bar+structure), corrected/de-duped module prose (main),
  added volume-sensitivity + switching-cost + negotiation-upside risk lines. Renderers read the existing stats JSONs
  unchanged + `annual_stats.json` for the seasonal shape (stub_year helpers); no pipeline rebuild, no hand-typed
  numbers. Both verified: render clean, 0 stray placeholders, go-live tables tie to the standalone calc. v1 untouched.
- **Go-live numbers** (full plan / base, by start month): Aug-1 €972,978 / €487,876 (51%) · Sep €854,988 · Oct
  €740,521 · Nov €619,179 · Dec €396,214. No-Hermes plan = base €976,024 → Aug-1 banks €487,876 (50%).

## Numbers correction Niklavs probed
He challenged "how is Aug–Dec only ~half?" — defended + decomposed: it IS 52% of volume, but the back-half framing
misleads because Aug/Sep/Oct are the year's *lowest* months (~6% each); only Nov+Dec (33.5%) are the real peak. The
stub year is decided by being live before November. (My review's "Aug–Dec holds the entire Q4 peak" wording was loose
— corrected in chat to "the two peak months.")

## Open / awaiting Niklavs
- **Both v2 reports UNCOMMITTED** in bi-analytics (separate repo). Review the rendered HTMLs (visual not eyeballed),
  then commit go (pathspec the two `*_v2/` dirs) — never push. This is the open_dep.
- Decide whether v2 supersedes v1, or keep both; and whether to mirror the go-live cut onto `annual_2026/` too.
- The REVIEW doc + [[S217_4e69b79c_eu-tender-final-report-savings-decomposition|S217]]'s v1 matrix edits also sit uncommitted in that repo (today's EU-tender work needs a commit pass).

## Cascade.
None into the brain. All report/code changes are in the separate bi-analytics repo (uncommitted). Brain side is
quest-log + resume + comms + harvest drafts only.

## Main-brain changes.
None to `gielinor/` rules, rituals, or hooks. Player-namespace writes only (quest-log, inventory, drafts) + comms.

## Files
- Deliverables (bi-analytics, uncommitted): `2_analysis/final_report_v2/`, `2_analysis/final_report_no_hermes_v2/`,
  `2_analysis/final_report/REVIEW_2026-06-11_content-pass.md`
- Resume: `inventory/eu-tender-final-report-content-pass-resume__e0eb59c8.md`

## Pending external actions
None pending.
