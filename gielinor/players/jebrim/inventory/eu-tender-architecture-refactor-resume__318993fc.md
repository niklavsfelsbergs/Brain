---
quest: S238_eu-tender-architecture-inventory-and-refactor-plan
sid8: 318993fc
ts: 2026-06-13 00:00
open_dep: awaiting principal's go on which refactor phase(s) to execute
---

# Resume — EU tender architecture cleanup (execution phase)

**Status:** in-progress. Discovery + plan shipped; refactor execution not started.

**Where we are:** `ARCHITECTURE_INVENTORY.md` (validated) and `REFACTOR_PLAN.md` (6-phase) are written
and committed to bi-analytics-main (`505b213`, `be05824`, not pushed). Nothing has been moved yet —
the plan is the proposal.

**Next concrete step:** Which refactor phase do we run? Recommended start is **P1 + P2** (pure file
moves to `_archive/`, lowest risk — dead code + the superseded full-year cluster), each as its own
commit, with the acceptance grep after each. **P3** (port `_refresh_bias_table.py` to the Q1 matrix)
is the only code change and can be its own focused session. **P4** ends with the regen gate
(`base_ann == 976023.94`). P5 (de-suffix) / P6 (orchestrator) are optional, recommend deferring.
Blocked on principal: which phase(s) to authorize.

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
