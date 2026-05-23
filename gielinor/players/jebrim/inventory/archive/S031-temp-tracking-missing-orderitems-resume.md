# S031 — temp%-tracking ↔ missing orderitems — resume

**Quest:** `quest-log/in-progress/S031_2026-05-22_temp-tracking-missing-orderitems.md`
**Status (2026-05-22):** investigation complete; two upstream ETL bugs documented; awaiting principal-side raise to ETL team.

## Where we are

T1–T8 produced a clean two-bug diagnosis. The `temp%` ↔ missing-orderitems correlation is **not a mart-logic issue**; it's the downstream symptom of two stacked upstream failures:

1. **`silver_shipping_data_mart_orchestrator` Phase 0a's `eb_pcs_ingestion` trigger never effectively runs.** Phase 0a is supposed to refresh bronze before silver/mart consume it. In May 2026 zero `eb_pcs_ingestion` runs landed at hour 03/04/05 UTC. The mart's "fresh bronze" guarantee is broken in practice.
2. **Even when `eb_pcs_ingestion` runs (via `bronze_orchestrator_shop_level` at 16:00 UTC), it processes only 5–20K rows/day** despite the SQL being a full 32-day-window DELETE+INSERT that should touch millions. Today's 619K-row catch-up confirms partial historical runs have been leaving gaps.

Result: ~49% miss rate on 2026-05-17 PICT temp cohort. Hundreds of shipments affected, not just MFA19911824351.

Working theory from T14 ("temp_* is a placeholder, items backfill") is **partially correct** — backfill IS the mechanism, but the ETL plumbing is sick. The mart code is sound; its inputs are broken.

## Next concrete step

**Principal action** (external, blocking next agent work):

1. Raise bug #1 to **@lukasz.sendecki** — Phase 0a `eb_pcs_ingestion` trigger never effective; check `max_active_runs=1` conflict with the 16:00 UTC `bronze_orchestrator_shop_level` run.
2. Raise bug #2 to **@pranav.gupta** — `eb_pcs_ingestion` daily runs only touch 5–20K rows; SQL is full 32-day window; either hidden incremental filter or federated pull truncating silently.

**Optional agent follow-ups** (only after ETL team responds):

- Stuck-residual probe: query `fact_shipments WHERE trackingnumber LIKE 'temp%' AND shop_order_created_date <= CURRENT_DATE - 8` by `shipping_provider_group`. Small population (~50–80 Picturator + ~5 PicaAPI), where the real DQ flags live.
- Re-check `MFA19911824351` at +2d (2026-05-24) and +5d (2026-05-27) to watch live backfill.
- Update shipping-agent `reference/known-dq.md` — document `temp_*` lifecycle, age-filter caveat, mart-staleness story.

## Files to read first

1. This file (resume).
2. `quest-log/in-progress/S031_2026-05-22_temp-tracking-missing-orderitems.md` — full investigation including T7/T8 bug evidence.
3. `Documents/GitHub/shipping-agent/reference/known-dq.md` — likely doc-update target.
4. `Documents/GitHub/bi-etl/dags/enterprise_silver/shipping_data_mart/silver_shipping_data_mart_orchestrator.py` line 162 — Phase 0a trigger.
5. `Documents/GitHub/bi-etl/dags/enterprise_bronze/pcs/sql/incremental/pcs_orderitems.sql` — the 32-day-window SQL that isn't behaving.

## Note

This resume file was generated post-hoc during S038 brain-underutilization cleanup (close-session step 3 didn't fire cleanly for S031). The quest is structurally "PAUSED — external dependency" — work is complete on the agent side; further movement waits on ETL team feedback. Consider moving to `completed/` if the doc update lands and ETL raises are tracked elsewhere.
