---
quest: S182_routing-report-size-tiers
sid8: e3648d0d
ts: 2026-06-09 19:32
open_dep: bi-analytics-main routing_2026q1 changes complete but UNCOMMITTED — principal-gated
---

**Status:** in-progress (deliverable shipped, external-repo commit pending principal go)

**Where we are:** The 4-tier size class (small / standard / large / oversize) is built, validated against Q1 actuals, and rendering correctly in the routing report cards. All code + regenerated artifacts are in place in `bi-analytics-main`, uncommitted.

**Next concrete step:** Ask Niklavs whether to commit the `bi-analytics-main` `routing_2026q1/` changes (6 files: build_final.py, carrier_envelopes.py, routing_report.py + regenerated routing_assignment.parquet / envelopes.json / routing_report.html / routing_stats.json). If yes, pathspec-commit those specific files in the bi-analytics-main repo. Note other uncommitted files in that tree are from prior/parallel work — do NOT sweep them.

**Optional follow-up (not started):** propagate the 4-tier size vocabulary to `decision_report/` and `carrier_overview_v2/` if Niklavs wants the wording consistent across all EU-tender deliverables (sibling-consumer sweep — they may carry their own standard/oversize language).

**Files / paths to read first:**
- `bi-analytics-main/.../routing_2026q1/carrier_envelopes.py` — the `sz` classifier (the hybrid rule + `SZ_ORDER`).
- `bi-analytics-main/.../routing_2026q1/routing_report.py` — the card render + CSS (`.szr/.szn/.cls-*`).
- `bi-analytics-main/.../routing_2026q1/build_final.py` — `packagetype` → `routing_assignment.parquet`.
- this quest-log: `quest-log/in-progress/S182_e3648d0d_routing-report-size-tiers.md`.
- domain digest: `bank/domains/eu-tender.md`.
