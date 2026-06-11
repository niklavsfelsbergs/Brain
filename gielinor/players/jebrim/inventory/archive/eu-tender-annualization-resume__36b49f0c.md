---
quest: S191_eu-tender-annualization-report
sid8: 36b49f0c
ts: 2026-06-10 16:20
open_dep: bi-analytics annual_2026/ uncommitted — awaiting principal commit go (separate repo, never push)
---

# Resume — EU-tender annualization report (the 4th report)

## Status
**BUILT — awaiting principal commit go.** Full-year 2026 annualization is built + verified in bi-analytics
`2_analysis/annual_2026/`, parallel to `routing_2026q1/`. All figures reconcile + tie end-to-end. **bi-analytics
is a SEPARATE repo, UNCOMMITTED, principal-gated, never push.** Niklavs said "good for now" — has NOT yet said
commit bi-analytics.

## Headline (two-tier — principal-directed)
- **FIRM €535,365 / 3.7%** (bankable: DHL/DPD engines + UPS actuals) — the headline floor.
- **+ €806,361 DB Schenker reroute — CONTINGENT** on the open package-setup investigation + Maersk-EU/Hermes
  engine validation.
- = up to **€1,341,726 / 9.19%**, band **€1.31M–€1.37M**, on €14.59M do-nothing / 2.57M parcels.

## Next concrete step
Does Niklavs want bi-analytics `2_analysis/annual_2026/` committed? If yes: `git commit -- <pathspec>` scoped to
annual_2026/ ONLY (shared tree, S131/S144 sweep hazard), never push. If later promoting the annual number into
the management deck / docs/, run that cascade then (deferred — and the deck itself is deferred until the Maersk
girth definition is confirmed per S189).

## Files to read first
- bi-analytics `2_analysis/annual_2026/{build_annual.py, annual_stats.json, annual_report.html}` — the deliverable.
- bi-analytics `2_analysis/annual_2026/{q1_base.py, aggregates_2025.py}` — the upstream base + 2025 aggregates.
- `research/2026-06-10-eu-tender-annualization-method-and-assumptions.md` — the locked plan (Part A + Part B ledger).
- `inventory/eu-tender-annualization-resume__9a064d86.md` — the S190 parent resume (more build detail).

## Watch-outs
- bi-analytics SEPARATE repo — pathspec-scoped commits only, principal-gated, never push.
- Visual layout of annual_report.html NOT eyeballed by me (no GUI) — data layers fully verified (reconciliation,
  ties, parcel conservation, clean SVG coords). Niklavs has been reviewing it live across the refinement rounds.
- A0 (Maersk MAERSKUK scope) still unconfirmed — flagged in report caveats; doesn't distort the directional result.
- Q4 product-mix NOT modelled (locked) — qualitative caveat only.
