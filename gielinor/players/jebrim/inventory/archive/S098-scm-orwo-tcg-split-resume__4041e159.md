# S098 — SCM alerts ORWO/TCG split — resume

**Session:** 4041e159 · **Quest:** `quest-log/in-progress/S098_4041e159_scm-alerts-orwo-tcg-split-plan.md`
**Repo:** `Documents/GitHub/bi-analytics` — `NFE/dashboards/shipping_costs_monitoring_nextjs/`. READ-ONLY so far.

## Status: DONE — shipped + deployed + verified working in prod.

## Where we are
COMPLETE. Built (Option B per-entity loop), validated offline (clean, no OOM), committed `54cde63`, merged to origin/main `3535229` (CICD), DAG re-ran → entity-tagged parquets live, serving deployed. Principal verified the ORWO/TCG toggle works in prod ("my bad it worked"). Quest moved to completed/.

## Next concrete step
None — quest closed. (Branch `scm-alerts-entity-split` can be deleted on origin once main is confirmed stable; optional cleanup of the orphaned unsuffixed `corridor_trends_weekly.parquet`, harmless.)

## Decisions locked
- Split at **detection grain** (entity as a corridor dimension), not presentation filter.
- `ORWO = order_source=='ORWO'`; `TCG = PicaAPI + PCS + Picturator`.
- Recommended strategy: **Option B** — per-entity detection loop (treat the S055/S076-stabilized engine as a black box run twice), over Option A (re-key all ~20 corridor group-bys).

## Next concrete step
Principal go/no-go on implementation. If go → build as a tracked checklist (harness list + this mirror):

## Implementation checklist (Option B) — DONE bar commit/deploy
- [x] 0. order_source → FRAMEWORK_COLS; `_entity_expr()` derives entity on df_weekly. (processed carries order_source — confirmed in run.)
- [x] 1. TS serving read (db.ts, alerts route, detail route, AlertsTab, types.ts).
- [x] 2. Per-entity loop via new `_entity_period_alerts` helper; engine on entity-filtered frame; alerts entity-tagged; concat.
- [x] 3. Per-entity `corridor_trends_weekly_<entity>.parquet`; `trends_suffix` param threaded to creep/volume_anomaly/coverage/build_alerts/build_issues (default `_weekly`, backward-compat).
- [x] 4. Frozen-baseline seed filtered by entity (transition guard for pre-S098 issues.parquet) + daily_product L2 shares filtered by entity.
- [x] 5. RE-SCOPED: no `_issue_key`/dedup/suppression edits — per-entity `_build_issues` keeps them within-entity; entity stamped on outputs instead.
- [x] 6. `entity` stamped onto alerts.parquet / issues.parquet.
- [x] 7. Serving: alerts + detail route entity param/WHERE; AlertsTab All/ORWO/TCG toggle (local state) threaded to all fetches + drill-down.
- [x] 8. Offline validation: 177s clean, no OOM; diff (ORWO 21/TCG 162, active 20, 0 impossible, 0 orphans); pytest 89/89; tsc clean.
- [ ] 9. Present diff for review — reported to principal. Awaiting go.
- [ ] 10. Deploy: push → main → CICD → DAG re-trigger (principal-gated); OOM/timeout watch.

## Reference
- Volume-check script: `%TEMP%/scm_volume_check.py` (read-only off data/daily.parquet).
- Engine vocab: `bank/notes/projects/shipping_costs_monitoring_nextjs_vocab.md`.
- Prior alert work: S055 (cutover review+fixes), S076 (alert-engine audit, deviation/severity/lifecycle fixes — shipped to prod main).

## Discipline
READ-ONLY until go. `git commit -- <pathspec>` only (shared-index hazard, 006248ef). polars prints need `PYTHONIOENCODING=utf-8`. Live effect needs a pipeline refresh (principal-gated).
