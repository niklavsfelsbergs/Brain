# EU tender `2_analysis/` — the pipeline fork (canonical vs superseded)

**Source:** [[S238_318993fc_eu-tender-architecture-inventory-and-refactor-plan|S238]] (sid 318993fc) architecture-discovery pass; verified by import trace + data mtimes +
git recency. Anchor docs in-repo: `NFE/projects/2_EU_tender_2026/docs/{ARCHITECTURE_INVENTORY,REFACTOR_PLAN}.md`.

**The non-obvious fact (the naming inverts the truth).** `2_analysis/` carries two parallel pipelines.
The **`_2026q1`-suffixed** modules (`cost_matrix_2026q1.py`, `decision_scorer_2026q1.py`,
`_decision_sets_2026q1.py`, `decision_report/report_2026q1.py`, `routing_2026q1/`, `annual_2026/`) are
the **canonical, live** path. The **unsuffixed** modules — which *read* as "the main ones"
(`cost_matrix.py::load_cost_matrix`, `decision_scorer.py`, `_decision_sets.py`,
`decision_report/report.py`) — are the **superseded [[S120_3760e65b_eu-tender-full-year-build|S120]] original**, running the 2025 full-year replay
basis. A future reader will assume the unsuffixed names are current; they are not.

**Why:** [[S120_3760e65b_eu-tender-full-year-build|S120]] (2026-05-28) built the original full-year decision on a *2025 12-month replay*. S150
onward (2026-06-05) rebuilt it on the *2026-Q1 actuals + per-country seasonal annualization* basis and
the 2025-replay was abandoned. So "full-year decision basis" is now computed by the `_2026q1` modules
feeding `annual_2026/`, NOT by the unsuffixed "full-year" modules.

**The proof:** the presented €976,024/yr headline (`final_report/final_stats.json` `structure.base_ann`)
is built by `final_report/build_final_stats.py` reading `annual_2026/q1_base.parquet` +
`routing_2026q1/routing_assignment.parquet` — entirely the Q1+annualization path; it never touches
`data/cost_matrix.parquet`. Data freshness confirms: `data/cost_matrix/` (2025 12-month) frozen at
2026-05-28; `cost_matrix_2026q1/` current.

**Two exceptions to "unsuffixed = dead":**
- `cost_matrix.py` is **live** — `cost_matrix_2026q1.py` imports `classify`/`run_engines`/`WEIGHT_BAND_LABELS`
  from it. It's the shared engine-run library; only its `load_cost_matrix` (full-year loader) is retired.
- `_refresh_bias_table.py` still runs on the stale full-year matrix (the `bias_table.md` self-contradiction)
  — slated to be re-pointed to the Q1 matrix in the refactor.

**`pipeline.py` is mis-named** — it only runs `population.sql → population.parquet` (the stale full-year
population). There is no end-to-end orchestrator; the canonical DAG is run stage-by-stage by hand.

Links: [[eu-tender]] domain digest; supersedes nothing there but adds the architecture-layer map the
digest didn't carry.
