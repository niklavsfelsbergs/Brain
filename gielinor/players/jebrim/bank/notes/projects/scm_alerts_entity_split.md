# SCM alerts — ORWO/TCG entity split ([[S098_4041e159_scm-alerts-orwo-tcg-split-plan|S098]])

**As of:** 2026-05-26 ([[S098_4041e159_scm-alerts-orwo-tcg-split-plan|S098]]). Shipped: bi-analytics `54cde63` → merged to main `3535229`. App: `NFE/dashboards/shipping_costs_monitoring_nextjs/`.

The SCM alert engine is **segmented per business entity**: `ORWO` = `order_source == 'ORWO'`, `TCG` = everything else (PicaAPI + PCS + Picturator). Each entity gets its own alerts/issues with its own baselines, coverage, and suppression.

## How it's built (Option B — per-entity loop)

The detection engine (just stabilized in [[S055_9837afe8_shipping-costs-dashboard-cutover-review|S055]]+[[S076_949a59cf_scm-alert-engine-audit|S076]]) is treated as a **black box run once per entity**, rather than re-keying its ~20 internal corridor group-bys:

- `pipeline.py`: `_entity_expr()` derives `entity` on `df_weekly` (`order_source` added to `FRAMEWORK_COLS`). New `_entity_period_alerts(dfw, entity, cfgs, prior_issues)` helper runs the per-period loop on the entity-filtered frame.
- **Per-entity artifacts:** `corridor_trends_weekly_<entity>.parquet` via a `trends_suffix` param (default `_weekly`, backward-compat) threaded through `_detect_creep` / `_detect_volume_anomaly` / `_corridor_real_coverage` / `_build_alerts` / `_build_issues`.
- **Frozen-baseline seed** filtered to the entity (transition guard: a pre-split issues.parquet has no `entity` col → fall back to all, self-corrects next run).
- **`_build_issues` runs per entity** → gap-and-island / dedup / suppression stay within-entity automatically. **No `_issue_key` / `_merge_active_duplicates` edits** — this is the key win: the regression-sensitive logic is untouched. `daily_product` L2 share denominators filtered to the entity (within-entity shares for free).
- `entity` stamped onto `alerts.parquet` / `issues.parquet`. Deviations stay **global** (Deviations tab only; deviation_blowout was demoted out of alerts in [[S076_949a59cf_scm-alert-engine-audit|S076]]).

## Serving

`IssueRow.entity` (types.ts); `entity` query param + `AND entity = ?` on the alerts route (and resolved-count query); optional entity clause on `alerts/detail`; an **All / ORWO / TCG** toggle on the Alerts tab (local state, mirrors `statusView`) threaded through every `/api/alerts` fetch and the drill-down. No global Filters/URL change.

## Validation (offline cache rebuild, 177s, no OOM)

issues ORWO 21 / TCG 162; active 17→20 (ORWO 6 + TCG 14 — per-entity baselines surface ORWO-specific issues previously diluted in shared corridors); **0 impossible impacts** ([[S076_949a59cf_scm-alert-engine-audit|S076]] fixes hold); TCG top set unchanged (DE UPS04STD +147K, DBSCHENKER +88K, MAERSKUK +46K); **0 orphan corridors** (every issue's (entity,country,provider) carries that entity's volume — attribution provably correct); pytest 89/89, tsc clean.

## Reusable pattern

To segment a stabilized pipeline by a new dimension without risking its math: filter the input frame per dimension-value, run the engine as-is in a loop, parametrize shared artifact paths by a suffix, run the grouping/issue-build step per value (so keys stay within-value), and stamp the dimension on the outputs. Avoids re-keying internal group-bys. (Candidate skill — graduate at alching.)

## Related
- [[shipping_costs_monitoring_nextjs_vocab]] — the engine vocab (queues, alert types, issue lifecycle).
- Deploy-ordering hazard for schema-add changes → memory `feedback-schema-add-deploy-ordering`.
