---
quest: S238_eu-tender-architecture-inventory-and-refactor-plan
sid8: 318993fc
ts: 2026-06-13 00:00
open_dep: NONE — the entire REFACTOR_PLAN (P1–P6) is complete + committed to bi-analytics-main (not pushed). Quest done bar session-close graduation. Brain commit at session close.
---

# Resume — EU tender architecture cleanup (execution phase) — COMPLETE

**Status:** ALL phases (P1–P6) DONE + committed to bi-analytics-main (not pushed). The `2_analysis/`
tree is cleaned: full-year cluster archived under `_archive/full_year_v1/`, bias diagnostic on the Q1
basis, engine dirs engine-only, `regen_all.py` orchestrator, and the `*_2026q1` naming trap removed
(canonical modules/folders de-suffixed). Final regen gate passed (base_ann == 976023.94) after P4 AND
again after P5's rename. Presented `final_report_no_hermes_v2` lineage byte-identical throughout.

**P5 done — commit `04c54f7`** (62 files): extracted `engine_run.py` (shared engine core) from
`cost_matrix.py`; archived the dead full-year `cost_matrix.py`; renamed `cost_matrix_2026q1→cost_matrix`,
`decision_scorer_2026q1→decision_scorer`, `_decision_sets_2026q1→_decision_sets`,
`report_2026q1→report`, `load_cost_matrix_2026q1()→load_cost_matrix()`, folders
`routing_2026q1/→routing/` + `switch_list_2026q1/→switch_list/`; updated 39 .py + 9 live .md.
**Kept** period-meaningful DATA names (`data/cost_matrix_2026q1/`, `population_2026q1`,
`scenarios_2026q1`, `actuals_2026q1`, the sql extractor) per principal's scope choice. Historical
discovery/plan docs left as pre-refactor snapshots. Verified: ast-parse 0 errors, spine imports,
no stale renamed refs, regen gate PASS, final_stats.json restored.

**Commits:** P1 `1ce97a2` (dead code) · P2 `0bae297` (full-year cluster, 33 renames) · P3 `c16a5db`
(bias→Q1 + archive invoice_adjustments) · P4 `32d631c` (engine dirs engine-only + archive
scenarios.py, 14 renames) · P6 `8cc1fc0` (regen_all.py orchestrator, additive). Each move: git mv,
100% renames, acceptance grep + smoke after; full grep clean after P4; presented
`final_report_no_hermes_v2` lineage byte-identical throughout (final_stats.json restored after the
verification regen).

**P6 done — commit `8cc1fc0`:** `2_analysis/regen_all.py` chains cost_matrix_2026q1 → scorer →
routing/build_final → annual_2026/{aggregates_2025,q1_base,build_annual} → final_report/build_final_stats
(the core numeric spine ending at base_ann). Thin/additive — ordering + output checks around the
scripts' own asserts. Population (Redshift) opt-in `--with-population`; base_ann reported vs €976,023.94
not hard-asserted (engine-version change expected). Flags: `--dry-run`/`--from`/`--list`. Verified via
--dry-run only (NOT run end-to-end — would overwrite presented intermediates). HTML/no_hermes renders
left as a separate step (not chained).

**P4 done — commit `32d631c`:** archived the 6 carrier `report.py` + their `migration_plan.html` →
`_archive/full_year_v1/carrier_reports/<slug>/`; relocated `carriers/PLAN_dpd_pl_current_engine.md` →
`docs/carriers/`; archived orphaned `scenarios.py`. Principal chose archive (not port) for the 6
reports. Regen gate: re-ran `final_report/build_final_stats.py` (terminal stage, all asserts pass) →
base_ann 976023.9422629153 == 976023.94; restored final_stats.json byte-identical (invariant 1) —
ran the terminal stage, not a from-population regen, to avoid perturbing the presented intermediates.

**P3 done — commit `c16a5db`:** ported `_refresh_bias_table.py` to the Q1 basis + regenerated
`decision_report/bias_table.md` + archived orphaned `invoice_adjustments.py`. Key calls:
denominator = `today_eur` (= `real_total_eur − OML>400`, LPS full) NOT raw real_total_eur — the
plan's literal "drop the adjustment" was insufficient because the matrix real_total_eur is raw
(netting lives in the scorer); Σ today_eur = €2,955,020 matches the live `do_nothing` baseline to
the cent. Winning pool = `_decision_sets_2026q1.NEW_ENTRANTS` (derived, not hardcoded) — **principal
chose** "mirror NEW_ENTRANTS": fedex in, dhl_paket/dpd_pl_current/ups → full-elig only. Ratios
re-based not regressed (portfolio winning-slice 1.201).

**Where we are:** Discovery + plan committed (`505b213`, `be05824`). **P1 done — commit `1ce97a2`**
(archived dead `capability.py` + `final_report/_superseded/` → `_archive/full_year_v1/`). **P2 done —
commit `0bae297`** (33 renames: full-year cluster `decision_scorer.py`, `_decision_sets.py`,
`decision_report/{report,routing_explained,routing_rules_explained}` v1 + variant html,
`cross_carrier_view.{py,html}`, `pipeline.py` + `sql/population.sql`, `carrier_overview/` v1 whole
folder, `routing_2026q1/{build_routing,_v2,_final,derive_envelope,smooth_impact}.py` →
`_archive/full_year_v1/`). All `git mv`, 100% renames, history preserved. Not pushed.

**Verification after each phase:** acceptance grep + `ast.parse` smoke test on live entry modules
(incl. `build_final_stats.py`). Post-P2 grep is the *expected* state — only two carry-forwards remain:
`scenarios` (6 carrier `report.py` → archived in **P4**) and `invoice_adjustments`
(`_refresh_bias_table.py` → ported/dropped in **P3**). Presented `final_report_no_hermes_v2` lineage
untouched throughout.

**Leaf-ordering note (verified, corrects inventory prose):** `_refresh_bias_table.py` references
`_decision_sets` only in **comments/docstrings**, not imports — its real imports are
`invoice_adjustments` + `cost_matrix`. So `_decision_sets.py` was leaf-safe to archive in P2 (all real
importers co-archived). P3 step 3 ("repoint `_decision_sets` refs") is therefore mostly a
docstring/comment update + wherever it actually reads `NEW_ENTRANTS` — confirm at P3 start where the
NEW_OFFER pool list actually comes from (it's NOT a live `from _decision_sets import` in the script).

**Next concrete step — P3 (HOLD for principal go):** port `_refresh_bias_table.py` to the Q1 basis:
(1) `from cost_matrix import load_cost_matrix` → `from cost_matrix_2026q1 import load_cost_matrix_2026q1`
(read `data/cost_matrix_2026q1/`); (2) drop `apply_invoice_adjustments` (Q1 basis already nets OML/LPS
into `today_eur` — confirm the `real_total_eur` field is the Q1-adjusted one); (3) repoint
`_decision_sets` refs → `_decision_sets_2026q1`; (4) regenerate `decision_report/bias_table.md` +
eyeball-validate ratios move-but-stay-plausible (resolves the S236 bias_table self-contradiction).
THEN archive orphaned `invoice_adjustments.py`. Own commit. **P4** ends on the final regen gate
(`base_ann == 976023.94`). P5/P6 deferred.

**Files to read first (ordered):**
- `NFE/projects/2_EU_tender_2026/docs/REFACTOR_PLAN.md` — the phase sequence + invariants + acceptance check
- `NFE/projects/2_EU_tender_2026/docs/ARCHITECTURE_INVENTORY.md` — the validated file-by-file classification + fork verdict
- `NFE/projects/2_EU_tender_2026/2_analysis/REPORTS_STATUS.md` — the canonical-report source of truth
- `bank/domains/eu-tender.md` — the domain digest

**Execution discipline reminders:**
- `git mv` into `_archive/` (never delete); one phase = one commit; explicit pathspecs; never push.
- NEVER touch the presented `final_report_no_hermes_v2/` lineage; €976,024 must stay byte-identical.
- `cost_matrix.py` STAYS (live shared lib). Archive `scenarios.py` + `invoice_adjustments.py` LAST
  (after their consumers — the engine `report.py` and the bias diagnostic respectively).
- `git commit -m "..." -- <pathspec>` (flag order: `-m` before `--`, and `git add` new files first).
