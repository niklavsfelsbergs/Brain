---
quest: S219_eu-tender-final-report-content-pass
sid8: e0eb59c8
ts: 2026-06-12 00:45
open_dep: both v2 reports BUILT + UNCOMMITTED (bi-analytics separate repo, never push); Niklavs to review the two rendered HTMLs + commit go + decide v2-supersedes-v1 / mirror to annual
---

# Resume — EU-tender final-report content pass + v2 build

## Where we are
Autonomous editorial pass DONE on the three live final reports (main / no-Hermes / annual). Deliverable:
`2_analysis/final_report/REVIEW_2026-06-11_content-pass.md`. Then per Niklavs' go, **built TWO v2 reports**, both
uncommitted (separate repo), v1 reports left intact:
- `2_analysis/final_report_v2/` (`final_report_v2.py` → `final_report_v2.html`, 33 KB) — main report, all 11 changes.
- `2_analysis/final_report_no_hermes_v2/` (`report_no_hermes_v2.py` → `report_no_hermes_v2.html`, 24 KB) — no-Hermes
  report, same treatment. Go-live plan = base €976,024; Aug-1 banks €487,876 (50% of run-rate). v1 untouched.

### What the v2 contains (vs v1)
- NEW §04 "What 2026 actually banks — go-live timing": stub-year table by go-live month + mint headline callout
  (Aug-1 = €972,978 full / €487,876 base) + transition-sequence info callout + switching-cost/ramp caveats.
- §03 trimmed: cut `totals_table` (subset of bridge3), dropped `structure_table` (merged into tier_bar),
  replaced the full flow `matrix_table` with a pointer to the routing report. 8 exhibits → 5 + go-live.
- §02 module warn rewritten to post-UPS truth (module = 98.5% the DBS reroute; Hermes = a destination, not a
  standalone case; the binding gate is the dimensions check) + de-duplicated (told once in full; §06 module risk
  cut to a back-ref; summary Part 2 tightened). Sections renumbered 04→08.
- §06 risks: added quantified volume sensitivity (−10% vol → ≈€1.72M), one-time switching-cost caveat, and an
  "Open upside" info callout (UPS CH/GB tier + DHL Sperrgut waiver).
- Renderer reads existing `final_stats.json` unchanged + `annual_2026/annual_stats.json` for the seasonal shape
  (stub_year() helper). No pipeline rebuild; no hand-typed numbers. Verified: renders, 0 stray placeholders,
  go-live table ties to the standalone calc.

## Go-live by start month (full plan / base, % of run-rate)
Aug-1 €972,978 / €487,876 (51%) · Sep-1 €854,988 (45%) · Oct-1 €740,521 (39%) · Nov-1 €619,179 (32%) · Dec-1
€396,214 (21%). Aug–Dec = 52.0% of annual volume; value concentrated in not missing November.

## Stale-source note / live sibling
S217 (4e69b79c, now CLOSED-uncommitted) edited the original `final_report/final_report.py` (added a savings-
decomposition matrix + discontinued-carrier residual handling) between my first read and the v2 copy. The v2 was
copied from that newer post-S217 v1, so it's current. No clobber (v2 is a new file). If v1/stats get rebuilt again,
re-run `final_report_v2.py` to stay in sync.

---
# (original review-pass record below)

## Where we are (review pass)
Autonomous editorial pass DONE on the three live final reports (main / no-Hermes / annual). Deliverable written to
the repo working tree (uncommitted): `2_analysis/final_report/REVIEW_2026-06-11_content-pass.md`. Reports NOT edited.

Verified current canonical numbers (post-UPS, main & annual reconcile): base €976,024 (6.5%) / module €932,683 /
full plan €1,908,707 (12.7%) on €15.08M do-nothing spend. The S194 resume's €420k/€577k base/module is STALE.

## The go-live answer (the new idea Niklavs floated)
Go-live 2026-08-01 → stub-year 2026 ≈ **€973k full plan / €488k base** = ~51% of run-rate from a 5-month stub,
because Aug–Dec = **52.0% of annual volume** (peak-weighted; Nov+Dec = 33.5%). Naïve 5/12 understates ~€178k.
By later go-live: Oct-1 ≈ €0.76M, Nov-1 ≈ €0.64M. Method: `annual_stats.json → global_shape.monthly_share` +
`bridge` (peak-free saving × vol-share + full −€41k peak diff, which is wholly in Oct–Dec).

## Next concrete step (all await Niklavs — he was offline)
1. He reads the REVIEW doc; decides which of the ranked changes to apply (TL;DR + §7 net recommendation).
2. If yes to the go-live cut: build it into `annual_report` §02 (shade Aug–Dec on the monthly curve) + a
   `final_report` §03 callout — that's a renderer/stats change, separate go.
3. Quick wins flagged: cut `totals_table` (subset of bridge3), merge tier_bar+structure_table, recheck the
   "Hermes+reroute=one decision" prose against the now-97%-reroute module numbers (coherence note §6).
4. Commit of the REVIEW doc (and any report edits) is his call — separate bi-analytics repo, pathspec-scoped,
   never push.

## Files to read first
- `2_analysis/final_report/REVIEW_2026-06-11_content-pass.md` (the deliverable — everything is in it)
- quest-log `S216_e0eb59c8_eu-tender-final-report-content-pass.md`
- digest `bank/domains/eu-tender.md`; prior resume `eu-tender-final-report-resume__907d4e63.md` (pre-UPS, partly stale)

## Watch-outs
- bi-analytics is a SEPARATE repo, principal-gated commits, never push. REVIEW doc is untracked.
- I did not visually open the rendered HTML — review is from the renderers + stats (data layer). Prose
  recommendations are from reading the .py source, which is the source of truth for layout + copy.
