---
quest: S247_scm-ontrac-fix-labels-breakdown-503
sid8: 52414165
ts: 2026-06-16 11:50
open_dep: post-airflow-run verification of OnTrac oversize series (deploy done) + optional bi-etl DAG docstring cleanup
---

**Status:** in-progress (all fixes shipped; one verification + one optional follow-up open).

**Where we are:** Four SCM dashboard fixes investigated, built, verified, committed, and pushed to `picanova/bi-analytics` main this session — OnTrac oversize root cause (stale cached partitions → full-refresh + S3 cache delete), Overview label thinning, Breakdown cost-filter 503 (debounce + cache-key decouple), monthly label budget. CI rebuilds the image; serving changes land on next pod pickup. The DAG full-refresh + label/breakdown serving changes are deployed.

**Next concrete step:** After the principal runs the next full-refresh Airflow run, confirm OnTrac "Oversize/overweight" in SCM reads ~€1–8/shipment back to mid-2025 (false Feb onset gone). If the pre-Feb months are *still* €0 after a successful full run, the cache wasn't the only freeze point — re-investigate. Separately, ask the principal whether to do the optional bi-etl DAG docstring/comment cleanup (the live DAG still describes the old incremental behavior) — a separate bi-etl commit.

**Files / paths to read first:**
- `players/jebrim/quest-log/in-progress/S247_52414165_scm-ontrac-fix-labels-breakdown-503.md` — full session narrative + commit hashes.
- `players/jebrim/quest-log/completed/S247_shipagent_ontrac-oversize-feb-onset-scm.md` — the OnTrac investigation verdict.
- `bi-analytics-main/NFE/dashboards/shipping_costs_monitoring_nextjs/docker/refresh.sh` + `pipeline.py` (`pull_raw`) — the refresh model.
- bi-etl `dags/AI_Automations/nextjs_dashboard_dags/shipping-costs-monitoring-dag/shipping_costs_monitoring_dag.py` — the LIVE DAG (60min timeout).
- `players/jebrim/bank/drafts/notes/projects/2026-06-16-scm-full-refresh-stale-partition-mechanism.md` — the durable mechanism note.
