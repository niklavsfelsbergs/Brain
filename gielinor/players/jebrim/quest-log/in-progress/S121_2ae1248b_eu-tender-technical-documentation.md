# S121 — EU Tender 2026: technical documentation (document-as-audit)

**Session:** jebrim-2ae1248b · 2026-05-28 · new quest, same session re-opened after S120 close.
**Goal:** Full technical documentation of the analysis system incl. every calculation engine's logic, as a "document-as-audit" pass (principal-chosen scope: stable-first; parallel dwarves).

## Resume foreground
See `inventory/eu-tender-technical-documentation-resume__2ae1248b.md` (written at close).

## Turn log

**T1 — setup + dwarf fan-out.**
- Posted S121 OPEN. Grounded on `carriers/_base/` (Surcharge ABC, apply_surcharges w/ eligibility gate + exclusivity groups, lookup_rate_asof, two fuel modes, in_period) + `_decision_sets.py` + gls/calculate.py (exemplar). Confirmed dwarf-write-boundary hook exits 0 for out-of-tree paths → dwarves can write tender docs.
- Stood up `2_analysis/docs/technical/`: README (index + status legend + per-engine template) — `01-architecture.md`, `02-engine-framework.md`, `03-scorer.md`, `04-report.md` authored by me from session context.
- Spawned **6 background dwarves** (maersk/hermes/dhl_express/austrian_post/dpd_pl/gls), each documenting+auditing its engine into `docs/technical/engines/<carrier>.md` + returning findings. Authored the 3 HELD-engine lite docs (fedex/dhl_paket/guell) myself while they ran.

**T2 — dwarves returned; synthesis.**
- All 6 returned clean docs. Verified all 14 files at correct paths (one dwarf's "docs/docs" was a narrative typo; file landed right). **All engine priced constants reconcile to their confirmed sources — no mis-priced constant.**
- Wrote `05-audit-findings.md` consolidating: **5 material code findings** + **11 doc-drift items** + lower-priority notes. The headliners are Q1-era assumptions the full-year shift silently invalidated:
  - **A1 (dhl_express):** `PICKUP_ELIGIBLE_PARCELS=184273` hardcoded Q1 count → pickup line-haul mis-allocated on full-year (~957k eligible).
  - **A2 (dhl_express):** demand window `in_period((1,1),(2,16))` year-agnostic + misses the Oct1–Dec31 2025 demand leg.
  - A3/A4 (maersk ROW fuel scope base-only vs base+surcharges; ROW AHS stacked vs highest-only) — small ROW tail.
  - A5 (gls Season month gate no date-column guard) — latent crash.
  - Doc-drift B1–B11: stale CLAUDE.md files (maersk/gls/dpd_pl), Hermes ASSUMPTIONS fuel row + "11 assumptions" framing, FUEL_SUMMARY "no reply" lines, dpd_pl CH-customs €484k-Q1-vs-€2.32M/yr basis, AP FX band +3.7%→+3.2%, maersk fixtures/parity.
- Cross-engine note: PEAK (maersk EU + hermes Q4) was dead code on Q1; S120 full-year is the first to fire it — validation to-do, not a fix.

**Status:** technical reference COMPLETE (15 files). All UNCOMMITTED — held for principal go + a corrections-scope decision (code fixes A1–A5 move numbers → re-run; doc-drift B1–B11 is a no-number cleanup). Dwarf traces in `quest-log/in-progress/S121_*_dwarf.md`.

## Cascade
EU-tender working repo (out-of-tree bi-analytics-main): new `2_analysis/docs/technical/` tree (15 files). No engine code changed (audit findings documented, not yet applied).

## Main-brain changes
jebrim quest-log S121 (this file) + 6 dwarf traces + inventory resume + comms OPEN + intent. Commit pending principal go.

**T3 — corrections (principal: "fix everything + re-run") + commit/push/close.**
- Applied all 5 code fixes, each verified against its engine fixtures: A1 DHL Express pickup denom re-baked Q1→full-year (€0.538→€0.414/parcel; 26/26), A2 demand window wrap to Oct–Feb, A3 Maersk ROW fuel→base+AHS, A4 Maersk ROW AHS exclusivity per Q11 highest-only (adjudicated against REVIEW_CONCLUSIONS — the dwarf was right, the Phase-1 "stacks" comment wrong; 17/17, updated the stack fixture), A5 GLS Season guard (12/12). Doc-drift B1–B10 fixed; B11 deferred (documented in 05-audit-findings.md resolution table).
- **Re-ran the pipeline:** cost_matrix rebuilt (fixed engines) → scorer → report. do_nothing=€0.00 PASS; baseline €14.85M unchanged; headline renew_maersk_plus_hermes €634,959 (≈unchanged, €106 maersk-ROW nudge); drop-DPD route €732k→€726k (DHL Express A1 cheaper-pickup net of A2 added Oct–Dec demand); ranking + decision intact.
- **Verify-before-commit caught my own drift:** the architecture doc claimed scenarios.parquet "committed" — it's gitignored (build intermediate). Fixed before commit.
- Committed tender 36ee4fa (32 files, pathspec-scoped) → rebased --autostash onto origin/main (clean, 43 unrelated WIP untouched) → pushed (07e65be..36ee4fa). Brain committing this close.

**S121 CLOSED.** Technical reference (15 files) + 5 code fixes + doc-drift on origin/main. Residuals tracked in 05-audit-findings.md.

## Cascade
EU-tender working repo (out-of-tree bi-analytics-main): docs/technical/ (15 new files) + 5 engine code fixes (dhl_express/maersk/gls) + doc-drift (ASSUMPTIONS/FUEL_SUMMARY/CLAUDE.md/report.py) + regenerated decision_report.html → committed 36ee4fa, rebased + pushed origin/main. scenarios.parquet + data/cost_matrix/ gitignored.

## Main-brain changes (close)
jebrim quest-log S121 + 6 dwarf traces + inventory resume `__2ae1248b` + comms OPEN/CLOSING + intent → committed + pushed origin/main this close.
