# Dashboard gold cutover — resume

**Status:** in-progress. Quest opened 2026-05-22 — `quest-log/in-progress/2026-05-22_dashboard-gold-cutover.md`. Three dwarves spawned in parallel (D1 SQL+pipeline, D2 UI, D3 audit+backtest).
**Player:** Jebrim.
**Repo / branch:** `bi-analytics/`, branch `shipping-mart-cutover` (already in flight — 13+ commits ahead of main, the cutover work continues there).
**Companion work:** the shipping-agent cutover landed earlier in S028 (`bi-analytics-main` `7e74670`). This dashboard cutover brings the dashboard into alignment with the agent's gold-only contract.

## Where we are

Not started. This file is the entry point. The shipping-agent went standalone-on-gold in S028; the dashboard still reads from `enterprise_silver.*` with a defensive coalesce on top of the mart's `final_shipping_cost_eur` plus an ORWO inline CASE fallback. Agent and dashboard will return divergent numbers until the dashboard's cost-basis logic matches the agent's vocabulary.

Niklavs framed the work in three points + answered a list of clarifications during S028. The principal decisions below are locked; the apply is mechanical from here.

## Scope — in, out, deferred

### In scope (the apply tranche)

**A. Schema flips + dedup removal + ORWO CASE removal — `sql/query_mart.sql`**

- Replace `enterprise_silver.fact_shipments` → `shipping_mart.fact_shipments`.
- Replace `enterprise_silver.fact_shipment_cost_summary` → `shipping_mart.fact_shipment_cost_summary`.
- **Drop the `dim_shipping_providers` JOIN entirely.** `shipping_provider_group` (high-level carrier name) and `shippingprovider_extkey` (service-level) live on `shipping_mart.fact_shipments` directly. Existing pipeline aliases the extkey as `shippingprovider`; preserve that alias by reading from `fs.shippingprovider_extkey` instead of `dim.shippingprovider_extkey`. No data semantics change.
- **Drop the ORWO inline CASE** for `expected_shipping_cost` (`query_mart.sql:36-120`). Reduce the column to plain `fs.expected_shipping_cost_eur::float8 AS expected_shipping_cost`. Drop the `orwo_dhl_base` and `orwo_ups_base` CTEs (~30 lines).
- **Drop the Picturator-Wolfen dedup filter** at `query_mart.sql:159-162` (`AND NOT (fs.source_system = 'Picturator' AND fs.production_site = 'Wolfen')`). Niklavs: "this should be removed, it will be solved from data side." Trust the mart.
- **Drop the `order_source` CASE** at `query_mart.sql:128-131`. Replace with `fs.source_system AS order_source` directly. The CASE was a no-op except for lumping `Rewallution` into `Picturator` — that lumping is unwanted; let Rewallution surface as its own value.

**B. Schema flips — `sql/query_mart_items.sql`**

- Replace `enterprise_silver.fact_shipment_orderitems` → `shipping_mart.fact_shipment_orderitems`.
- Replace `enterprise_silver.fact_shipments` → `shipping_mart.fact_shipments`.
- **Keep `dw.dim_products` LEFT JOIN as-is.** Deferred per principal decision (see Deferred below). Dashboard user has broader grants — the `dw` reach is fine for now.

**C. Pipeline `cost_for_routing` simplification — `pipeline.py:552-564` (`transform()`)**

- Replace `cost_for_routing = COALESCE(shipping_cost_final if not null and >0, expected_shipping_cost)` with `cost_for_routing = shipping_cost_final` directly. No pipeline-side coalesce.
- Rationale: agent's vocab makes `final_shipping_cost_eur` the canonical one number. NULL `final` = uncosted; dashboard adopts the same stance. Removes the divergence source between agent and dashboard answers.
- Verify downstream code paths handle NULL `cost_for_routing` gracefully — should already, since `has_cost` / `has_expected` already gate on NULL. But spot-check anywhere `cost_for_routing` is dereferenced without a NULL guard.
- `expected_shipping_cost` column stays pulled (for the "Estimated only" toggle); just stops being a fallback source for routing.

**D. UI cost-basis label rename — agent-vocab alignment**

- Cost-basis toggle values + display labels:
  - `real_expected` → `final` (URL/internal); display "Final cost (invoiced + estimated)"
  - `real` → `invoiced` (URL/internal); display "Invoiced only"
  - `expected` → `estimated` (URL/internal); display "Estimated only"
- "real" badge on alerts UI → "invoiced".
- URL back-compat shim: `?bs=real_expected` / `?bs=real` / `?bs=expected` map to the new internal values for any existing bookmarked URLs.
- Search for usages: grep `real_expected` and `\"real\"` (quoted, as a string literal — too noisy unquoted) across `src/` to find all touch points.

**E. Naming-asymmetry note — dashboard `CLAUDE.md`**

- Add one-liner noting: column name is `real_shipping_cost_eur` but the gold `cost_source` flag value for invoiced rows is `'invoice'` (not `'real'`). Pipeline doesn't filter on `cost_source` today, but if future work does, the value rename matters. (Verified S028: no `cost_source` references in current dashboard codebase.)

**F. `issues.parquet` baseline reset**

- Delete `data/issues.parquet` (and `data/alerts.parquet` if it carries frozen-baseline state too) before the first post-cutover pipeline run.
- Reasoning: the ORWO/Picturator dedup removal + ORWO CASE removal both shift the `cost_for_routing` numbers for ORWO-Wolfen and ORWO-non-DHL/UPS corridors. Frozen baselines in `issues.parquet` were computed under the old logic. Reset gives clean baselines in the new world; loses active-issue continuity for one resolution cycle (acceptable per principal).
- Document the reset event in the pipeline run notes / commit message so anyone tracking specific active issues knows they re-fired as "new."

**G. `audit.py` + `backtest.py` rewrite**

- Both reference legacy `layer{1,2,3,4}_*.parquet` and single-file `processed.parquet` — fail against the current cutover-era output set (`processed/<YYYY-MM>.parquet` partitioned dir, `daily.parquet`, `daily_product.parquet`, etc.).
- Rewrite scope: enumerate which audit checks are still meaningful (some target removed concepts like `layer3_*` rollups); re-target the surviving checks at the new output set. Same for `backtest.py` — point at `processed/` dir, update threshold constants if needed.
- Could become its own quest if it ramps up — split if it gets >2 hours.

**H. Test sweep**

- Run `pytest tests/` after Phases A–E land.
- Triage failures. `tests/test_pipeline.py` (1302 lines) covers severity / issue / suppression logic — most should be schema-agnostic. `tests/test_creep.py` (150 lines) is detector-level — also schema-agnostic. Failures most likely come from:
  - Test fixtures that hardcode silver schema or pre-cutover cost values.
  - `cost_for_routing` semantic change (no pipeline-side fallback) — tests that build synthetic data with NULL `shipping_cost_final` and non-NULL `expected_shipping_cost` will see different `cost_for_routing` values now.
- Fix or update fixtures as needed.

### Out of scope (deferred or rejected — do NOT pull in)

- **Coverage-hole reporting in the Completeness tab.** Principal: "not part of the scope." Dashboard's coverage tab will be addressed separately. Agent's `reference/coverage-audit.md` remains the canonical structural-vs-invoice-lag distinction.
- **`ALERT_REAL_COST_THRESHOLD = 65%` re-validation.** Principal: "out of scope." Threshold stays at 65% post-cutover; revisit if alert volume looks off in practice.
- **% invoiced indicator everywhere a cost number is shown** (Gap 6). Principal: "defer." Buckets view's existing indicator stays; other surfaces don't get it in this pass. The agent's how_to §0 rule 11 still mandates % invoiced disclosure for agent answers — the dashboard / agent split on this is intentional for now.
- **Adopting agent's plain-English source-system labels in dashboard UI** (Q3b). Principal: "skip." Dashboard surfaces `source_system` values raw (`Picturator`, `ORWO`, `PCS`, `Rewallution`, `PicaAPI`). No translation table in UI.
- **Long-term agent ↔ dashboard convergence** (URL emission, shared definitions surface, dashboard ad-hoc layer). See `inventory/dashboard-agent-convergence-resume.md` — separate parked quest; not in this scope.

### Deferred (waiting on something)

- **Items query / `dw.dim_products` removal** (Q1). Principal: "lets defer until we add the shop order group." Waiting on `shop_order_group` migration into `shipping_mart.fact_shipment_orderitems`. Until then, `query_mart_items.sql` keeps the `dw.dim_products` JOIN. When the migration lands, drop the JOIN and use the gold column directly.
- **ORWO expected-cost migration into the mart.** The mart populates `expected_shipping_cost_eur` for Picturator/PicaAPI but not ORWO. Post-cutover, ORWO rows have NULL `expected_shipping_cost`; if mart's `final_shipping_cost_eur` covers via `avg` they're costed, otherwise uncosted. When ORWO procedure migrates to the mart, the dashboard already handles it (just pulls `expected_shipping_cost_eur` directly).
- **CSV export rework** (2026-05-22, parked during dashboard gold cutover). `OutliersTable.tsx` CSV download headers (`"Cost","Expected"`) were left intact during Phase D to avoid breaking downstream CSV consumers — vocab inconsistent with the gold rename ("Estimated" would match). Principal: "we will rework the export in general, we can make it better now, park it." When the broader export rework opens, align the vocab.
- **`?bs=` URL emission** (2026-05-22, parked during dashboard gold cutover). D2's `coerceCostBasisParam` shim is purely defensive — no tab actually emits cost-basis into URL today (state lives in tab-local React/sessionStorage). When the broader shareable-links story opens (likely alongside the agent ↔ dashboard convergence quest), wire one or more tabs to round-trip cost-basis through `?bs=`. Principal: "park it."
- **`backtest.py` signal-density tuning** (D3 flag, 2026-05-22). Constants `MIN_ABS_CHANGE_EUR=0.50` and `MIN_SHIPMENTS=100` kept as-is through the cutover. Cost-basis distribution may have shifted post-cutover (ORWO rows now NULL where the inline CASE used to fill). Principal: "keep as is." Re-evaluate from observation if signal density looks off; not blocking.

## Next concrete step

Open the quest file (`players/jebrim/quest-log/in-progress/<YYYY-MM-DD>_dashboard-gold-cutover.md`) and start with Phase A — `sql/query_mart.sql` rewrite. Smoke test after Phase A (run the pipeline, confirm row counts sane). Phases B–E in sequence (B simplifies pipeline, C touches UI, D adds doc note, E resets baselines). Phase F (issues reset) goes immediately before the first post-cutover pipeline run. Phases G + H are independent; can interleave or do after.

## Files / paths to read first

1. This file.
2. `players/jebrim/bank/drafts/notes/projects/shipping_costs_monitoring_nextjs_vocab.md` — dashboard vocab (cost columns, alert types, period machinery, tabs).
3. `players/jebrim/quest-log/in-progress/S026_d1_sql_pipeline.md` — deep reference on SQL + pipeline.
4. `players/jebrim/quest-log/in-progress/S026_d2_api_and_data_layer.md` — API + data layer reference (read when touching UI / data wiring).
5. `players/jebrim/quest-log/in-progress/S026_d3_frontend.md` — frontend reference (read when touching Phase D label renames).
6. `bi-analytics/NFE/dashboards/shipping_costs_monitoring_nextjs/CLAUDE.md` — dashboard's own entry doc.
7. `bi-analytics/NFE/dashboards/shipping_costs_monitoring_nextjs/sql/query_mart.sql` — primary Phase A target.
8. `bi-analytics/NFE/dashboards/shipping_costs_monitoring_nextjs/sql/query_mart_items.sql` — Phase B target (light edits only).
9. `bi-analytics/NFE/dashboards/shipping_costs_monitoring_nextjs/pipeline.py:552-564` — `cost_for_routing` simplification.
10. **For agent-side reference (cross-check):** `bi-analytics-main/NFE/projects/3_shipping_data_mart/shipping-agent/reference/mart-contract.md` § Cost columns — the vocabulary the dashboard is aligning to.

## Smoke tests (post-apply)

Order: A → B → smoke 1 → C → D → smoke 2 → E → smoke 3 → F (issues reset) → next pipeline run → smoke 4 → G + H interleaved.

- **Smoke 1 (after A + B):** Run the pipeline (`python pipeline.py --refresh-full` or `--refresh` for a faster check). Confirm:
  - Pipeline completes without errors.
  - `raw.parquet` row count is in the expected range (note: should be **higher** than pre-cutover by the count of previously-deduped Picturator-Wolfen rows). Compare against the prior run's row count from `_pipeline_run.log` or `meta.json`.
  - `daily.parquet` rebuilt; `meta.json` carries fresh `date_bounds`.
  - Sanity query against `raw.parquet`: April 2026 TCG row count should approximate the agent's `276,490` figure (TCG = `Picturator + PicaAPI + PCS`; cross-check with `python -c "import polars as pl; df = pl.read_parquet('data/raw.parquet'); print(df.filter((pl.col('order_date') >= '2026-04-01') & (pl.col('order_date') < '2026-05-01') & (pl.col('order_source').is_in(['Picturator','PicaAPI','PCS']))).height)"`).
  - Sanity check `cost_for_routing` for ORWO rows: previously the inline CASE filled them; now they're either populated via mart's `final_shipping_cost_eur` (via `avg` fallback) or NULL. Coverage drop expected on ORWO corridors.

- **Smoke 2 (after C + D):** Start the dev server (`npm run dev`). Confirm:
  - Cost-basis toggle on Overview shows new labels ("Invoiced only" / "Final cost (invoiced + estimated)" / "Estimated only").
  - Switching the toggle still renders correctly; URL param updates.
  - Old URL with `?bs=real_expected` still loads (back-compat shim works).
  - Alert badge that previously showed "real" now shows "invoiced".

- **Smoke 3 (after E):** Visual check of dashboard CLAUDE.md naming-asymmetry note.

- **Smoke 4 (after F + first post-cutover pipeline run):** Confirm `data/issues.parquet` rebuilt fresh. Alert count probably spikes (many active issues re-detect as new). Acceptable noise per principal — track for the resolution cycle.

- **Cost-basis parity check (agent ↔ dashboard):** With the dashboard fully rebuilt on gold, the April 2026 TCG invoiced-only avg should match the agent's `€6.95 / 209,874 invoiced parcels` figure within rounding. From dashboard's API: query Overview with date range April 1–30 2026, source filter `Picturator+PicaAPI+PCS`, cost basis "Invoiced only" — read off the average. This is the load-bearing convergence smoke test.

## Constraints (in-force)

- **Branch `shipping-mart-cutover` is the working surface.** Don't open a new branch; the work continues on the existing one. Commit cadence: per-phase or per-coherent-change, push when natural.
- **Dashboard user has broader grants** than `ship_mart_ro` — both `shipping_mart` and `dw` access. That's why `query_mart_items.sql` can still hit `dw.dim_products`. Don't try to lock dashboard down to `ship_mart_ro` (different from the agent, intentionally).
- **The mart's `final_shipping_cost_eur` is `COALESCE(real, expected, avg)`.** Post-cutover, dashboard's `cost_for_routing` IS this — no additional coalesce. NULL `final_shipping_cost_eur` = uncosted shipment from the dashboard's perspective (8% of mart-wide rows, per gold verification).
- **Naming asymmetry:** column is `real_shipping_cost_eur` but `cost_source` flag value is `'invoice'`. Pipeline doesn't filter on `cost_source` today; if it ever does, use `'invoice'`.
- **Defensive SQL for `cost_source = 'invoice_estimate'` remnant:** 0.5% of rows mart-wide currently carry this value (transient remnant being renamed to `'invoice'` upstream). If any future query filters on `cost_source`, use `cost_source IN ('invoice', 'invoice_estimate')` until the rename lands.

## Open items (won't block start, surface during work)

- **DAG verification.** Airflow refresh DAG runs at 08:00 Berlin and pulls from Redshift. Per principal, user grants are fine (broader than `ship_mart_ro`). Verify the first scheduled run post-cutover lands without error. If it fails, root-cause and surface.
- **The cost-basis parity check (Smoke 4) is the success criterion** for this entire cutover. If the dashboard's invoiced-only April-TCG avg doesn't match the agent's €6.95 within rounding, something didn't align. Diagnose before declaring the cutover done.

## Related

- `inventory/dashboard-agent-convergence-resume.md` — the parked convergence quest. This cutover is a prerequisite step toward that work but not the same thing. Convergence covers URL emission, shared definitions surface, long-term direction — all out of scope here.
- `bank/drafts/notes/projects/shipping_costs_monitoring_nextjs_vocab.md` — dashboard vocab.
- `bank/drafts/notes/projects/dashboard_and_shipping_agent_convergence.md` — convergence analysis.
- `bank/drafts/notes/projects/shipping_mart_cost_vocabulary_2026-05-22.md` — agent's cost-vocab (the contract this cutover aligns dashboard to).
- S028 quest log on S024 — the agent-side cutover that this dashboard cutover mirrors.
