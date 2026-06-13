# S238 — EU tender architecture: validated inventory + refactor plan

**sid8:** 318993fc · **player:** Jebrim · **date:** 2026-06-13
**Thread:** continuation of the [[S236_a7ea5300_eu-tender-cleanup-and-nfe-commit-rule|S236]] (a7ea5300) EU-tender cleanup — executes the discovery plan [[S236_a7ea5300_eu-tender-cleanup-and-nfe-commit-rule|S236]] wrote.

## What this session did

Executed `docs/ARCHITECTURE_DISCOVERY_PLAN.md` (discovery only, no file moves) for
`bi-analytics-main/NFE/projects/2_EU_tender_2026/`, then drafted the refactor plan it gates.
Two deliverables, both committed to the work repo (not pushed):

1. **`docs/ARCHITECTURE_INVENTORY.md`** — commit `505b213`. Code-traced the `2_analysis/` import
   graph + mined the record (Jebrim quest-log, `bank/domains/eu-tender.md`, git log).
2. **`docs/REFACTOR_PLAN.md`** — commit `be05824`. 6-phase sequenced archival.

## Key findings (verified against code, not relayed from the scout)

- **`pipeline.py` is NOT the orchestrator** — it only builds the stale 2025 full-year
  `population.parquet`. There is no end-to-end orchestrator; the canonical DAG is run by hand.
- **Fork verdict (the headline):** the `_2026q1` modules are **canonical/live**; the unsuffixed
  "full-year" modules (`cost_matrix.py`'s `load_cost_matrix`, `decision_scorer.py`, `_decision_sets.py`,
  `decision_report/report.py` v1) are the **superseded [[S120_3760e65b_eu-tender-full-year-build|S120]] original** (2025-replay basis). The naming
  inverts the truth. The €976,024 headline flows entirely through `cost_matrix_2026q1 → routing_2026q1
  → annual_2026 → final_stats.json`. `cost_matrix.py` survives as a shared lib (`classify`/`run_engines`).
- **One live defect:** `_refresh_bias_table.py` re-ran 2026-06-12 on the stale full-year matrix
  (matches [[S236_a7ea5300_eu-tender-cleanup-and-nfe-commit-rule|S236]]'s flagged `bias_table.md` self-contradiction). The plan's P3 ports it to the Q1 basis.
- `REPORTS_STATUS.md` status calls **confirmed** by the usage trace — no corrections.

## Decisions (residuals resolved with Niklavs via multiple-choice)

- **3_UK/** → stays nested. Niklavs: late-arriving UK offer, calculated separately, same project.
- **Engines** → clean in place, not extracted to a shared package.
- **Full-year cluster** → archive + re-point the bias diagnostic to the Q1 matrix.
- **capability.py** → archive (dead since [[S034_2026-05-22_eu-tender-logic-review|S034]], imported by nothing).

## Refactor plan shape (for execution)

6 phases, leaf-first so no import dangles at any commit: P1 dead code → P2 full-year cluster →
P3 bias-diagnostic port to Q1 (the one code change) → P4 engines engine-only + final regen gate
(`base_ann == 976023.94`). P5 de-suffix + P6 regen orchestrator are optional/deferred. Two ordering
constraints baked in (verified): the 6 engine `report.py` import `scenarios.py`, and
`_refresh_bias_table.py` imports `invoice_adjustments.py` — so both libs are archived last.

## Pending external actions

None pending. Both deliverables committed to bi-analytics-main (`505b213`, `be05824`); not pushed.

## Cascade.
None — work confined to the bi-analytics work repo + this quest/inventory/bank-draft. No meta/ritual/hook changes.

## Main-brain changes.
Quest-log entry (this file) + inventory resume + one bank draft (`bank/drafts/notes/projects/2026-06-13-eu-tender-pipeline-architecture-fork.md`).

## Executed — graduated S239 (dc163efd, 2026-06-13)
The plan's open dep (execution) is done: all 6 phases + README executed and committed to
bi-analytics-main (`1ce97a2`, `0bae297`, `c16a5db`, `32d631c`, `8cc1fc0`, `04c54f7`, `8081e1c`;
not pushed). See [[S239_dc163efd_eu-tender-architecture-refactor-execution|S239]]. Graduated to
completed/ at S239 close; shared resume archived.
