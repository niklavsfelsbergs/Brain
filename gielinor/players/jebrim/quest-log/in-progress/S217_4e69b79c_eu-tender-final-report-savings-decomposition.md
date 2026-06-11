# S217 — EU tender final report: savings decomposition (what the savings consist of)

**Session:** 4e69b79c · **Date:** 2026-06-11 · **Player:** Jebrim
**Family:** EU-tender final-report siblings — [[S194_907d4e63_eu-tender-holdup-pass-and-project-rating|S194]] (907d4e63 holdup pass), [[S216_e0eb59c8_eu-tender-final-report-content-pass|S216]] (e0eb59c8 content pass). This session = the savings-decomposition build pass on the live `final_report/` + `final_report_no_hermes/`.

## The ask
Niklavs: "I know what we're missing in the final report — what the savings actually consist of." Add it, iteratively shaped over several turns into a from→to carrier matrix with cost columns.

## What I did (the arc)
1. **From→to carrier matrix** in §03 ("What it saves"), both reports. The flow data already existed in `final_stats.json` (`flows`, computed in `build_final_stats.py`); the report only rendered the off-diagonal "moves" (filtered `from != to`), hiding the diagonal. Added the full matrix grouped by source carrier: diagonal = **reprice** (kept carrier, new rate), off-diagonal = **reroute** (volume moved).
2. **Reprice/reroute split** — reprice €404,483 (21%, 75% of parcels) / reroute €1,545,418 (79%, 25% of parcels). The contrast (most parcels stay → a fifth of savings; the quarter that move → four-fifths) is the headline of the cut.
3. **Total-cost before/after anchor** (do-nothing €15,078,402 → plan €13,169,695 = save €1,908,707 / 12.7%) at the top of the composition, to size the saving against total spend. Canonical figures (`bridge3.annual`), unchanged headline.
4. **Cost-now / cost-after columns** per flow (his real ask, clarified via screenshot). Build change: added `cost_before_ann` (`keep_ref`) + `cost_after_ann` (`rcost`) to the `flows` aggregation in both build scripts.
5. **Removed §04 "What changes in operations"** — fully redundant with the §03 matrix (which *is* the operable one-carrier-per-cell plan). Folded the operability note + module-gating pointer into the §03 matrix legend; renumbered sections (full 01–07, no-hermes 01–06). Section-count check caught a hidden §08 "Going deeper" that had to be pulled to 07.
6. **Removed Direct Link** (`residual`) — a dropped carrier Niklavs doesn't want to see. Filtered in the **report display only** (not the build — headline still nets it); generic reconciliation legend ("a carrier being discontinued", unnamed); stripped the §02 "Not selected" mention. 0 "Direct Link" in rendered HTML. Decomposition now sizes to the 5 contracted carriers €1,997,207, reconciling to headline via −€47k residual −€41k peak.

## Decisions
- Matrix lives in **§03** (savings composition), not §04 — the cost columns make it a savings view, not an ops view.
- Cost columns are **peak-free** (Q4 peak added separately both sides) → footnoted; they total €14.57M → €12.57M (5 carriers, ex-Direct Link), under the with-peak anchor.
- Direct Link excluded from **display** only; the build/headline keep it (the small negative is a dropped-carrier baseline, real but not worth showing).
- All reconciliations tie to **0.00** (flow + cost, per-row and totals). `verify_report.py` gained flow + cost-column checks (pass).

## Known open / watch-outs
- **`verify_report.py` VERDICT = FAIL on a PRE-EXISTING check** (`service-mix table rendered`), NOT this work: an earlier uncommitted edit (the e0eb59c8/service-mix refactor) changed the service table to shares, breaking the verifier's raw-count grep (`879,596`). Proven pre-existing via stash-to-HEAD (PASS at HEAD). Offered a one-line fix (point the check at the carrier total); awaiting Niklavs' go.
- **bi-analytics is a separate repo, commit-gated, never pushed.** All edits uncommitted in the working tree — awaiting Niklavs to eyeball both HTMLs (visual not eyeballed by me; data + structure verified) and give the commit go.
- Matrix is now **7 columns** — confirm it reads at presentation width.

## Files changed (bi-analytics-main, UNCOMMITTED — separate repo)
- `NFE/projects/2_EU_tender_2026/2_analysis/final_report/{build_final_stats.py, final_report.py, verify_report.py}`
- `NFE/projects/2_EU_tender_2026/2_analysis/final_report_no_hermes/{build_stats_no_hermes.py, report_no_hermes.py}`

## Cascade
None — no `gielinor/` meta/ritual/hook/digest changes this session.

## Main-brain changes
None beyond this quest-log entry + its resume + one examine draft (harvest).
