---
quest: S226_eu-tender-routing-report-no-hermes
sid8: da65054b
ts: 2026-06-12 11:40
open_dep: none — shipped + committed (bi-analytics 9d171a2); only follow-up is rm 2 probe files
---

# no-Hermes routing report — built

## Where we are
Built a full no-Hermes routing report (the package×dest×weight-band "what's going
where" grid, scoped to the no-Hermes 5-carrier scenario). New artifacts in
bi-analytics `2_analysis/routing_2026q1/no_hermes/`:
`routing_report_no_hermes.{py,html}` + `routing_rules.csv` + `routing_stats.json`
+ `envelopes.json` + assignment/candidate parquets.

Approach (principal-approved, both via AskUserQuestion):
- DBS-oversize treatment = **pinned to freight** (conservative €976k basis), reroute shown as gated caveat.
- Build = **parametrize build_final.py** (not a fork).

`build_final.py` + `carrier_envelopes.py` parametrized (`carrier_set`/`pin_dbs`/`out_dir`,
and `data_dir`); defaults verified numerically identical (with-Hermes plan untouched).
`python build_final.py no_hermes` + `python carrier_envelopes.py no_hermes` +
`python no_hermes/routing_report_no_hermes.py` regenerate it.

Headline: Q1 saving €209,028 / annual €976,024/yr; 5 carriers; DBS retained 9,175 on
freight (saving 0); €696k/yr UPS/DHL reroute = gated upside, excluded.
Reconcile: do-nothing + parcel count (531,194) exact; Q1 saving within €3,280 (the
~226 non-DBS parcels in DBS-dominated cells following the cell onto freight — cell
commits to one carrier). Stated on-page §07.

## Next concrete step
Quest shipped + committed (bi-analytics `9d171a2`, pathspec-scoped, not pushed). Only
follow-ups, both optional/principal-side:
1. `rm 2_analysis/_probe_dbs.py _probe_dbs2.py` (brain delete-guard blocked me even there).
2. Open question Niklavs deferred (S225 sibling): does adding Güll to the no-Hermes
   5-carrier portfolio give meaningful savings? Would be a 6-carrier-minus-Hermes
   variant — same `build_final.py no_hermes` machinery, different carrier_set.

## Files to read first
1. this file
2. bi-analytics `.../routing_2026q1/no_hermes/routing_report_no_hermes.py`
3. `.../routing_2026q1/build_final.py` (the `build()` params + DBS pin)
4. sibling resume `eu-tender-no-hermes-report-resume__177f00f1.md` (the final-report no-Hermes work this builds on)
