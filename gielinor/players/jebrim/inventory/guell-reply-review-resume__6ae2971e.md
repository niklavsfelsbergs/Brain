---
quest: S223_guell-reply-review-doc-sync
sid8: 6ae2971e
ts: 2026-06-12 09:46
open_dep: guell-2.0.0 build + portfolio-fit read pending (next session)
---

# Resume — Güll reply review → engine rebuild → portfolio fit

**Status:** in-progress.

**Where we are:** Güll's Round-1 reply is reviewed and all 8 EU-tender docs are synced (uncommitted in bi-analytics-main). No carrier blocker remains — `guell-2.0.0` is unblocked. Next phase is the build, then the portfolio-fit read. Decided build-first (not triage-first): Güll already sits in the leading `renew_maersk_plus_guell` set on the old over-priced engine, so the rebuild can't be wasted and the honest fit answer needs the regenerated cost-matrix.

**Next concrete step:** build `guell-2.0.0` per PLAN §B.21, regenerate the matrix/scorer/report, then read whether cheaper Güll strengthens the leading set / unlocks an AT-CH retirement / replaces a carrier. Paste-ready handover prompt below.

**Files to read first (next session):**
- `bi-analytics-main/NFE/projects/2_EU_tender_2026/carrier_responses_to_open_questions/Gull/REVIEW_CONCLUSIONS.md` — the confirmed reply deltas.
- `2_analysis/docs/ASSUMPTIONS.md` (Güll table) + `PLAN.md` §B.21 — every constant + the build scope.
- `2_analysis/carriers/guell/` — the engine to rebuild (`guell-1.0.0` → `guell-2.0.0`).
- `2_analysis/data/cost_matrix.parquet` + `scenarios.parquet` + `decision_report.html` — current (stale) scoring; regenerate after the build.

**Also pending (non-blocking):** the 8 bi-analytics doc edits are UNCOMMITTED — Niklavs to give the commit go (separate work repo). Q11 Round-2 follow-up drafted at `1_offers/picanova/Güll/questions_round2.md`.

---

## Handover prompt (paste to open the next session)

Hey Jebrim, build `guell-2.0.0` per PLAN.md §B.21, then use the regenerated scoring to answer whether Güll now fits into or replaces something in the current EU-tender portfolio. The carrier inputs are all confirmed (Round-1 reply reviewed 2026-06-12) — this is the build, not a triage.

The confirmed deltas are already locked in the docs: `2_analysis/docs/ASSUMPTIONS.md` (Güll table — every constant with its 2026-06-12 value), PLAN.md §B.21 (constants + structural changes + module list), and `carrier_responses_to_open_questions/Gull/REVIEW_CONCLUSIONS.md` (the per-Q reasoning). Engine lives at `2_analysis/carriers/guell/`.

Build scope (all from §B.21): `FUEL_PCT_AT` → 0.15 fixed; `AT_MAUT_EUR` → 0.32 fixed; `_apply_fuel` base → base + B2C + bulky (not Maut); CH energy flat 0.04 → per-month schedule (supplied Jan-25→Jun-26, Q1 = .02/.02/.00); `CHF_TO_EUR` → per-month strongest-CHF (Commerzbank); wire inbound sprinter + outbound per-pallet line-haul at offer rates ÷ density; CH 40 EUR declaration (per-truck, near-zero consolidated); new AT oversize-tail recovery path (~4k items/yr @ 45 EUR via 2nd carrier — was a hard reject); `PEAK_PCT = 0`. Then: new fixtures for each wired surcharge, rebuild `data/cost_matrix.parquet`, re-run `decision_scorer.py`, refresh `bias_table.md`, regenerate `decision_report.html`.

Carry these as flagged working assumptions (non-blocking, same posture as Austrian Post): Q11 outbound per-pallet at the offer rates (24.50 AT / 40.00 CH) pending the Round-2 reply in `questions_round2.md`; parcels-per-pallet and parcels-per-sprinter density at 150 (Picanova-ops estimate); AT bulky shape branch left at the volume-only (>150 L) floor since the mart has no shape signal.

Then the payoff question, read off the regenerated report: does cheaper Güll (a) strengthen `renew_maersk_plus_guell`, (b) unlock retiring another AT/CH carrier (Austrian Post, or the CH legs of DPD PL / GLS), or (c) just hold? Güll serves AT/CH/LI per the current offer (not Güll's hard limit — it's a Lindau forwarder that could quote other lanes, but that's a fresh carrier ask), so it can only move those lanes. Report the before/after headline shift and what it displaces — with the brand-new-carrier caveat front and center (no parity validation; fixtures only; output carries higher uncertainty than Maersk/DHL Paket where Q1 actuals can validate).
