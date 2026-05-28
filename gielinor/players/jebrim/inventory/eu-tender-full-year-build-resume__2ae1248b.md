# RESUME — EU Tender 2026 full-year build (Option 1) — S120 cont. (2ae1248b)

**Status:** Step 5 DONE. Full-year build (Option 1) computationally + presentation complete. All code/docs UNCOMMITTED (held for principal go).
**Repo:** out-of-tree `bi-analytics-main/NFE/projects/2_EU_tender_2026/2_analysis`. Tender HEAD = `6991d37` (S120 steps 1-4).
**Predecessor resume:** `inventory/eu-tender-full-year-build-resume__3760e65b.md` (steps 1-4, had the STEP 5 HANDOFF SPEC).

## Where we are
Steps 1–4 were done+committed (tender 6991d37). **Step 5 (fuel band + report regen) now DONE this session.** report.py + the doc cascade are edited and verified; decision_report.html regenerated and ground-truthed. Held for commit.

## Step 5 — what was done
1. **Fixed report.py matrix read** — `pl.read_parquet(DATA/"cost_matrix.parquet")` → `load_cost_matrix()` (lazy, column-pruned), mirroring decision_scorer. Moved the cm-load + bias infra above the narrative so a live-facts block can feed the prose.
2. **Q1 → full-year prose conversion** — every hardcoded Q1 figure replaced with a LIVE-computed value off scenarios/matrix (no re-drift): bias ratios, per-set savings, Hermes coverage, customs caveats, OML/LPS stats, the dhl_paket book ratio. Relabelled all "Q1" framing → full-year.
3. **New framing surfaced** — baseline_2026 (€14.85M re-priced do-nothing) vs invoice_today (€14.27M, +€581k/+4.1%), switchable-only re-pricing explained; dhl_paket over-prices its book (+2.9%, NOT +5.5% as the handoff said — corrected live); maersk EU peak €250k/yr flagged assumption + ROW-demand deferral added to caveats.
4. **Fuel band** — DEFERRED the numerical low/mid/high sweep (principal call); report ships on the mid/current point with the band framed qualitatively (low/mid/high table from FUEL_SUMMARY in the fuel callout).
5. **Doc cascade** — NEXT.md (full-year build EXECUTED, next steps reordered: fuel sweep #1), DECISIONS.md (S120 full-year-build-executed entry), ASSUMPTIONS.md (maersk peak + ROW-demand entries w/ revisit triggers), REPORT_NOTES.md (full-year figures + executed note), stray PEAK_PCT refs fixed in carriers/maersk/report.py + migration_plan.html.

## Two PRINCIPAL DECISIONS made this session
- **Headline leader:** KEEP `renew_maersk_plus_hermes` (€635k/yr, 3 uncov) as the pinned minimum-disruption headline. Full-year reorders the trustworthy ≤6 ranking — `renew_maersk_drop_dpd_pl_plus_gls_dhl_express` €732k (retires DPD-PL) and `renew_maersk_plus_gls` €642k both score higher — surfaced as alternatives in prose, not headline. Also: the Q1 `n_uncovered==0` "full coverage" filter matched nothing on full-year (every set strands 3-20 parcels) → relaxed to ≤100 tolerance, headline pinned to Hermes.
- **Fuel:** DEFER the numerical sweep; ship qualitative band now.

## Verified full-year headline (ground-truthed, in the HTML)
- baseline_2026 €14,851,018 vs invoice_today €14,269,584 (+€581,434 / +4.07%); do_nothing €0 PASS.
- Pinned leader renew_maersk_plus_hermes €635,065/yr (3 uncov). Higher trustworthy: drop-DPD route €732,017 (5 uncov), +GLS €641,713 (20 uncov).
- renew_maersk ALONE now NEGATIVE −€199,313 (strands 138,536 parcels). Provisional ceiling all_renewals_plus_fedex €1.68M.
- Customs caveats full-year: GLS EFTA €1.32M/yr, DPD-PL CH customs €2.32M/yr. Maersk EU peak €250,410/yr (post-OML-adj).
- Hermes coverage 96.8%, avg €5.87. dhl_paket over-book ratio 1.029 (+2.9%).

## NOT converted (scope call — flagged to principal)
- **cross_carrier_view.{py,html}** left as the **Q1 unit-cost reference** companion (its entire framing is "Q1 2026"; reads the current legacy Q1 matrix; html @16:47 already current). Converting it to full-year is a separate build that changes its purpose — flagged, not done.
- Scratch `_groundtruth_s120.py` left in the analysis dir (untracked `_`-debris, excluded by commit discipline; brain delete-hook blocks rm — remove manually if wanted).

## COMMIT SCOPE (HELD — principal "always ask before committing")
Tender (out-of-tree, `git commit -- <pathspec>`, local-only no push; ~80+ unrelated WIP — NEVER bare `git add`):
- `2_analysis/report.py` (Step 5)
- `2_analysis/docs/{NEXT.md, DECISIONS.md, ASSUMPTIONS.md, REPORT_NOTES.md}`
- `2_analysis/decision_report.html` (regenerated)
- `2_analysis/carriers/maersk/{report.py, migration_plan.html}` (PEAK_PCT refs)
- Data parquets gitignored — not committed. `_groundtruth_s120.py` excluded (untracked debris).
Brain: jebrim quest-log S120 + this inventory + comms + intent.

## Next concrete step
1. **Commit** the above (principal go). 
2. Then per NEXT.md: fuel low/mid/high sweep (deferred), remaining seasonal layers (DHL Paket peak/peak-in-peak, Hermes Q4, DHL Express/Maersk-ROW demand), carrier round-2s (FedEx/DHL-Paket/Güll/UPS) to flip held sets from provisional.

## Carrier-blocked (full-year build does NOT depend on these)
UPS (no offer); FedEx r2 (June ZOOM 2/9 Jun); DHL Paket r2 (Bulky €2.31M); Güll r1. HELD on old engines → provisional in matrix, flagged downstream.
