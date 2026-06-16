# SCM — OnTrac oversize root-cause fix + Overview labels + Breakdown 503

**Player:** Jebrim. **sid8:** 52414165. **Date:** 2026-06-16.
**Repos touched:** `bi-analytics-main/NFE/dashboards/shipping_costs_monitoring_nextjs` (all changes committed + pushed to `picanova/bi-analytics` main).

## Ask(s)
Four threads, all SCM dashboard:
1. OnTrac "Oversize/overweight" bucket flat €0.00 (Jul 25–Jan 26) then onset Feb 2026 — investigate.
2. Overview weekly/daily + invoiced cost: no point labels (monthly showed them).
3. "View from Alerts → Breakdown" + changing min/max cost filter → memory spike → 503.
4. Monthly Overview labels only every-other (follow-on to #2's fix).

## What happened / decisions
- **OnTrac (thread 1):** spawned shipping-agent. Verdict = **dashboard classification gap, not a cost event** (cause #2). Gold mart has classified OnTrac oversize correctly every month since mid-2025 (~€1–8/shipment); same charge-descriptions pre- and post-Feb; no re-bucketing, no step-up. Full investigation → [[S247_shipagent_ontrac-oversize-feb-onset-scm]] (completed/).
- **Root cause located (principal side):** the SCM pipeline's incremental `--refresh` re-pulls only the last 3 months (`INCREMENTAL_MONTHS=3`) and merges onto cached `raw.parquet` older rows kept verbatim (`pull_raw` `pipeline.py:521`). Bucket cols are pulled per-shipment from the gold mart, so each cached month froze at its pull-time classification. The mart's bucket-mapping was rebuilt 2026-04-23 (silver `shipping_charge_bucket_mapping`); the rolling window re-pulled only recent months from the corrected mart → false Feb onset = the oldest month the window re-touched. Confirmed the principal's own hypothesis against the code.
- **Fix (thread 1) — two parts:**
  - One-off: deleted `s3://etl-poc-dev/nextjs_dashboards_data/shipping_costs_monitoring/raw_cache/raw.parquet` (via `aws s3api delete-object`; bucket is versioned → soft delete). Principal runs Airflow → `refresh.sh`'s `cp ... || true` finds it gone → full pull from `FULL_DATE_FROM` rebuilds all partitions from the corrected mart. This is the script's documented fallback.
  - Permanent: changed `refresh.sh` `--refresh` → `--refresh-full` so every run re-pulls all history (no incremental cache freeze). DAG docstring updated. Commit `56c5d9b`.
  - **Deploy-topology correction:** the live DAG is in **bi-etl** (`dags/AI_Automations/nextjs_dashboard_dags/shipping-costs-monitoring-dag/`), already at `execution_timeout=60min` (sized for a full pull) — the bi-analytics copy I first read was a STALE source copy at 30min. Reconciled the stale copy to 60; no timeout change needed live. `refresh.sh` deploys via the ECR image; the DAG file deploys via bi-etl.
- **Overview labels (thread 2):** `CostTrend.tsx` LabelList is gated only on `singleLine` (no granularity gate), so labels DID render for weekly/daily — recharts has no collision avoidance, so dense series (tens/hundreds of points) overlapped into an illegible smear = "no labels." Added density thinning: `labelStep = ceil(points/target)`. Commit `64edeec`.
- **Breakdown 503 (thread 3):** two compounding causes — (a) min/max cost inputs not debounced (request per keystroke), (b) `minCost`/`maxCost` baked into the `bd_<hash>` cache-table fingerprint (`breakdown/route.ts`), so each value forced a full-scan `CREATE TABLE` rebuild + resident materialization (serialized, LRU=8) → memory pile-up → 503. "View from Alerts" worsens it: nav clears all sidebar dim filters → bd_ table materializes all corridors. Fix: debounce inputs (~400ms) + take cost range OUT of the fingerprint, apply as a validated numeric-literal WHERE (wrap the cached table for level/tooltip; inject into total's parquet scan). Verified vs local 970K-row parquet: wrap==baked identical, nested UNNEST valid. Commit `6ad550d`.
- **Monthly labels (thread 4):** the flat `/14` thinning regressed monthly — an 18-month view → `ceil(18/14)=2` → every-other. Gave monthly a larger budget (`target=24`, weekly/daily stay 14). Commit `eb6bdee`. **This was a regression from my own thread-2 fix that the principal caught** — see examine harvest.

## Pending external actions
None pending. All four fixes committed + pushed to `picanova/bi-analytics` main (`56c5d9b`, `64edeec`, `6ad550d`, `eb6bdee` — note OnTrac+DAG landed as `56c5d9b`; order in session was labels→DAG→breakdown→monthly). CI rebuilds `:latest`; serving changes land on next pod pickup.

## Open / carry-forward
- Verify OnTrac oversize series reads its true ~€1–8/shipment back to mid-2025 after the principal's next full-refresh Airflow run (the deploy is done; this is the post-run confirmation).
- Optional cosmetic: the *live* bi-etl DAG docstring/comments still describe the old incremental behavior — offered, not yet done (separate bi-etl commit).
