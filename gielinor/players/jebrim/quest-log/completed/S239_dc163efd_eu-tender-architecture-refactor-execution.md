# S239 — EU tender architecture refactor: execution (P1–P6) + README

**sid8:** dc163efd · **player:** Jebrim · **date:** 2026-06-13
**Thread:** execution continuation of [[S238_318993fc_eu-tender-architecture-inventory-and-refactor-plan|S238]] (318993fc) — runs the 6-phase `docs/REFACTOR_PLAN.md` that [[S238_318993fc_eu-tender-architecture-inventory-and-refactor-plan|S238]] wrote and gated on `docs/ARCHITECTURE_INVENTORY.md`.

## What this session did

Executed the **entire** refactor plan against `bi-analytics-main/NFE/projects/2_EU_tender_2026/2_analysis/`
— all six phases + a capstone README — each its own commit to the work repo (not pushed). Every move
was `git mv` into `_archive/full_year_v1/` (zero deletes), with the acceptance grep + a live-module
smoke test after each phase, and the regen gate (`base_ann == 976023.94`) as the real proof.

| Phase | Commit | What |
|---|---|---|
| P1 | `1ce97a2` | archive dead `capability.py` + `final_report/_superseded/` |
| P2 | `0bae297` | archive the superseded full-year cluster (33 renames) |
| P3 | `c16a5db` | re-point the bias diagnostic to the Q1 matrix; archive `invoice_adjustments.py` |
| P4 | `32d631c` | engine dirs → engine-only; archive `scenarios.py`; final regen gate |
| P6 | `8cc1fc0` | add `regen_all.py` DAG orchestrator |
| P5 | `04c54f7` | de-suffix the `*_2026q1` naming trap (62 files) |
| — | `8081e1c` | `2_analysis/README.md` (Phase-2 architecture orientation) |

## Decisions (principal, via multiple-choice)

- **P3 bias winning-pool** → mirror `_decision_sets_2026q1.NEW_ENTRANTS` (fedex in; dhl_paket/dpd_pl_current/ups → full-elig only).
- **P4 carrier reports** → archive the 6 `report.py` (retired basis), not port to Q1 (a separate build).
- **P5 de-suffix scope** → modules + folders, **keep** the period-meaningful data names (`data/cost_matrix_2026q1/`, `population_2026q1`, `scenarios_2026q1`, `actuals_2026q1`).

## Key findings / judgment calls

- **P3 — the plan's literal "drop the adjustment" was insufficient.** The Q1 cost-matrix
  `real_total_eur` is **raw** (OML netting lives in the *scorer*, not the matrix), so I computed
  `today_eur = real_total_eur − OML(>400)`, LPS full, exactly as `decision_scorer_2026q1` does.
  Proof it now shares the live basis: Σ today_eur = €2,955,020.01, matching the live `do_nothing`
  baseline to the cent. Resolved the [[S236_a7ea5300_eu-tender-cleanup-and-nfe-commit-rule|S236]] `bias_table.md` self-contradiction. Pools derived from the
  decision-set module (drift-proof), not hardcoded.
- **Regen gate passed twice** — after P4 and again after P5's rename — at `base_ann == 976023.94`;
  `final_stats.json` restored byte-identical each time (ran the terminal stage, not a from-population
  regen, to avoid perturbing the presented intermediates — invariant 1).
- **P5 — `routing_2026q1/ → routing/` hit a Windows dir-handle lock** (one of ~14 live python
  processes, likely a parallel session). Worked around it by `git mv`-ing the tracked files
  individually + plain-`mv` the gitignored data, rather than killing sibling processes.

## Pending external actions

None pending. All seven commits in bi-analytics-main (`1ce97a2`, `0bae297`, `c16a5db`, `32d631c`,
`8cc1fc0`, `04c54f7`, `8081e1c`); **not pushed** (push is a separate principal action).

## Cascade.
None — work confined to the bi-analytics work repo + this quest/inventory/comms/harvest. No meta/ritual/hook changes.

## Main-brain changes.
This quest-log entry + resume archived (`inventory/archive/`) + comms OPEN/CLOSING + harvest drafts (see close).

## Post-close continuation (same session, after the S239 wrap)

Principal re-opened with follow-ups; all committed to bi-analytics-main and **pushed** to origin/main:

1. **Refreshed the project-root README** (`385fd9e`) to post-refactor state (carrier_engines, the
   11-engine model, €976,024 result, pointers to the new `2_analysis/README.md`). Then **pushed the
   full EU-tender arc** (10 commits, `24de3fa..385fd9e`).
2. **`carriers/ → carrier_engines/`** (`d337700`) — renamed the engine package (180 files); updated
   `from carriers.X` → `carrier_engines.X` across 38 .py + 57 .md. Caught + reverted a blanket-replace
   over-reach that hit the same-named sibling folder `docs/carriers/` (a different folder).
3. **Report folders consolidated under `reports/`** (`8e30d0f`) — `final_report/`,
   `final_report_no_hermes_v2/`, `final_report_no_hermes_with_gull/`, `decision_report/`,
   `management_briefing/`. Depth change broke the builders' `ROOT = parents[1]` anchors → bumped all
   10 to `parents[2]`; fixed `regen_all.py` + doc paths. Then **pushed** (`385fd9e..8e30d0f`).

Regen gate held at `base_ann == 976023.94` through every rename; presented lineage byte-identical.
Harvest: 1 examine draft (blanket folder-rename hits same-named sibling folders). Origin now 0/0.
