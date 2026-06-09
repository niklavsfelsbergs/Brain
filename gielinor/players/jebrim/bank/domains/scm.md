---
domain: scm
title: Shipping Costs Monitoring — the shipping_costs_monitoring_nextjs dashboard
patterns:
  - scm
  - shipping costs monitoring
  - shipping_costs_monitoring
  - cost dashboard
  - alert engine
corpus:
  - bank/notes/projects/shipping_costs_monitoring_nextjs_vocab.md
  - bank/notes/projects/scm_alerts_entity_split.md
  - bank/notes/projects/scm_nextjs_duckdb_oom_modes.md
  - bank/notes/projects/2026-06-02-scm-serving-node-oom-mode.md
  - bank/notes/projects/shipping_costs_dashboard_csv_export_architecture.md
  - bank/notes/projects/dashboard_and_shipping_agent_convergence.md
specialist: shipping-agent (spawn for live mart queries)
freshness: 2026-06-02
synthesized: 2026-06-09
---

# SCM — Shipping Costs Monitoring dashboard

The productized, always-on cost **monitor** over the gold `shipping_mart` — *known unknowns*, patterns watched continuously (the shipping-agent is the ad-hoc *investigator*; same mart, different loop). App: `bi-analytics/NFE/dashboards/shipping_costs_monitoring_nextjs/`, branch `shipping-mart-cutover`. Self-contained — own CLAUDE.md / README / docs/. **Two runtimes:** the batch **pipeline** (Airflow DAG, ~08:00 Berlin → refreshes parquets → S3 → pod restart) and the **serving** Next.js app (EKS). The cutover replaced 5 Redshift queries with 2 pulls against the mart.

## Cost basis (load-bearing)
- **`cost_for_routing`** = the default cost everywhere downstream = `COALESCE(shipping_cost_final, expected)`; `shipping_cost_final` = mart `final_shipping_cost_eur` = `COALESCE(real, expected, avg)`.
- **11 cost buckets** sum to `total_eur == real_shipping_cost_eur` to the cent (invariant). Reducers `bkt_discounts` / `bkt_credit_note` are **negative**; tax + customs **excluded** (pass-through).
- ORWO `expected` is a SQL-level `CASE` fallback (DHL/UPS country avgs + seasonal peak), not mart-sourced — stand-in until ORWO migrates. UI basis: `real_expected` (default) or `real`.

## Alert engine
- `alerts.parquet` (per-week × corridor × type) → gap-and-island → **`issues.parquet`, the UI's primary surface** (`/api/alerts` returns issues, not alerts).
- **Two queues:** `early_warning` (every corridor, can fire on expected-only) + `confirmed` (real-cost coverage ≥ 65%). Types: `rate_spike`, `carrier_shift` / `routing_shift` / `product_shift`, `new`/`vanished_corridor`, `creep`, `deviation_blowout`, `volume_anomaly`.
- **Frozen-baseline override** keeps a long-running shift from dissolving into its own baseline (issues *settle* after N flat weeks).
- **Entity split ([[S098_4041e159_scm-alerts-orwo-tcg-split-plan|S098]]):** segmented ORWO (`order_source=='ORWO'`) vs TCG (everything else) by running the engine as a black box **once per entity** (suffixed artifacts) — never re-keyed; All/ORWO/TCG toggle on the Alerts tab.

## Data tiers + the OOM family
- Tiers: `daily` (~300K) / `daily_product` (~2M, built via DuckDB UNNEST — Polars segfaults on the wide schema) / `processed/<YYYY-MM>` (~4.8M). `processedPruned(from,to)` avoids full-glob scans.
- **Three distinct OOM modes — read the traceback to tell them apart:** (1) **pipeline RAM OOM** (memory_limit too high); (2) **pipeline temp-spill OOM** (low cap forces spill onto the near-full DATA disk); (3) **serving 502** — the in-process serving DuckDB had **no `memory_limit`**, so it sized to the host node (not the pod) outside the V8 heap → cgroup SIGKILL (exit 137).
- **Lesson:** an embedded analytics engine in a memory-limited container is a *second, uncapped memory pool* beside the language heap — capping `--max-old-space-size` is necessary but not sufficient; set the engine's `memory_limit` to the pod budget. The serving k8s manifest (mem limit, volume) is **not** in the app repo.

## CSV export & deploy
- Unified export via shared `src/lib/csv.ts` (`rowsToCsv` / `downloadCsvBlob`): snake_case columns, **gold-contract vocab** (`final`/`invoiced`/`estimated`), `<from>_<to>` filenames; `cost_source` only on `/api/export` (per-row provenance).
- **Deploy:** push to `main` → CI rebuilds ECR `:latest` → DAG runs the new image. `pipeline.py` value-changes only take effect on the **next refresh**. Schema-add ordering: regenerate data **before/with** the serving deploy or filtered views 500 ([[S098_4041e159_scm-alerts-orwo-tcg-split-plan|S098]]). Deploy topology + safe dirty-main pattern: [[bi_analytics_deploy_topology]].

## Corpus (Tier 1 — read for detail)
- [[shipping_costs_monitoring_nextjs_vocab]] — **the anchor glossary**: cost cols, 11 buckets, full alert/issue vocab + suppression rules, period machinery, data tiers, DuckDB query layer, tabs, frontend state.
- [[scm_alerts_entity_split]] — the ORWO/TCG per-entity engine split + the reusable segment-a-stable-pipeline pattern.
- [[scm_nextjs_duckdb_oom_modes]] — the two *pipeline* OOM modes (RAM vs temp-spill).
- [[2026-06-02-scm-serving-node-oom-mode]] — the third (serving 502) + the embedded-engine lesson.
- [[shipping_costs_dashboard_csv_export_architecture]] — CSV export architecture + locked conventions.
- [[dashboard_and_shipping_agent_convergence]] — monitor-vs-investigator, cost-basis reconciliation, convergence directions.

## Live work
Spawn the **shipping-agent** (`specialist`) for any live mart pull — this digest is *about* the dashboard, not a substitute for querying the mart.
