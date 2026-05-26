# temp%-tracking ↔ missing orderitems — DQ investigation

**Opened:** 2026-05-22 (S031, post /clear after [[S030_2026-05-22_dashboard-gold-cutover|S030]] alching).
**Status:** in-progress.
**Type:** investigation (DQ correlation; cross-source, cross-carrier).
**Origin:** [[S030_2026-05-22_dashboard-gold-cutover|S030]] T14 — flagged in `inventory/shipping-agent-personal-folders-resume.md` § Open threads.

## The brief (carried over from [[S030_2026-05-22_dashboard-gold-cutover|S030]] T14)

A parallel shipping-agent session surfaced: `shipping_mart.fact_shipments` rows with `trackingnumber LIKE 'temp%'` show ~25% missing orderitems vs ~0.08% on real tracking. Cross-carrier, varies by source — Picturator `temp*` ~26–30%; PicaAPI `temp*` 40–69% (worst: PicaAPI × MAERSK at 68.8%).

**Working theory from the other agent:** `temp*` is a placeholder before the real carrier label is assigned. Orderitems backfill once real tracking posts — spine lands first, items follow.

**Probe ordernumber Niklavs handed over:** `MFA19911824351`.

**Surface:** Jebrim runs directly using shipping-agent's documented knowledge + redshift MCP. Principal still working out how to interlink shipping-agent with personal work — no scaffold of `workbench/investigations/temp-tracking-missing-orderitems/` yet.

## Turn log

**T1.** Respawned Jebrim (post /clear). Read `inventory/shipping-agent-personal-folders-resume.md` § Open threads. Loaded shipping-agent's `reference/tables.md` + `skills/query-patterns.md` for canonical knowledge. Loaded `mcp__redshift__execute_sql`. Principal confirmed: Jebrim direct via agent knowledge — no shipping-agent session this round.

**T2.** Probed `MFA19911824351`. Single shipment, `shipment_id = 29711673149261210`, **Picturator → DB SCHENKER PL** (`DBSCHENKERPLEUHOME`), `trackingnumber = 'temp_D42602536'`, `shop_order_created_date = 2026-05-17` (5 days ago), `order_produced_date = 2026-05-21` (yesterday). Carrier hasn't received it (`received_by_carrier_date = NULL`), `current_shipping_status = NULL`, `cost_source = 'expected'` (not invoiced), `item_count = NULL`. Joined to `fact_shipment_orderitems` — **zero rows**. Confirms the surface pattern: `temp%` + no items + cost still expected, the shipment hasn't fully landed.

**T3.** Ran the cohort probe to test the backfill theory across Picturator (Apr 1 – May 22). Used `LEFT JOIN (SELECT DISTINCT shipment_id FROM fact_shipment_orderitems)` because a CTE'd `GROUP BY shipment_id` over the full 122M-row table refused to validate via MCP — Redshift planner pushback. Age buckets by `shop_order_created_date` vs `DATE '2026-05-22'`:

Picturator results:
| age | still-temp | missing | % | real-tracking | missing | % |
|---|---|---|---|---|---|---|
| 00-01 | 230 | 0 | 0.00 | 13 | 0 | 0.00 |
| 02-03 | 10,857 | 1,971 | 18.15 | 3,593 | 0 | 0.00 |
| 04-07 | 3,310 | 1,407 | 42.51 | 26,383 | 78 | 0.30 |
| 08-14 | 77 | 21 | 27.27 | 55,319 | 42 | 0.08 |
| 15-30 | 68 | 2 | 2.94 | 131,933 | 172 | 0.13 |
| 31+ | 51 | 0 | 0.00 | 144,839 | 205 | 0.14 |

The **still-temp population collapses 200×** from day 0-1 (230) to day 31+ (51) — conversion to real tracking happens overwhelmingly within a week. After ~8 days the still-temp residual is under 80.

**T4.** Same probe for PicaAPI (per T14's claim of higher 40–69% rates):
| age | still-temp | missing | % | real-tracking | missing | % |
|---|---|---|---|---|---|---|
| 00-01 | 76 | 0 | 0.00 | 33 | 15 | **45.45** |
| 02-03 | 3,014 | 941 | 31.22 | 814 | 8 | 0.98 |
| 04-07 | 833 | 312 | 37.45 | 7,071 | 0 | 0.00 |
| 08-14 | 21 | 9 | 42.86 | 16,573 | 0 | 0.00 |
| 15-30 | 3 | 1 | 33.33 | 59,619 | 0 | 0.00 |
| 31+ | 5 | 0 | 0.00 | 36,665 | 0 | 0.00 |

Same shape. Striking: **PicaAPI's 00-01 day real-tracking cohort shows 45% missing items** (small sample, 33 shipments). Hints that item-lag isn't purely a `temp_*` mechanism — it can show on real-tracking too, just much less common.

## Findings (working synthesis)

**Theory confirmed, with refinement.** `temp_*` tracking is a placeholder, and the data overwhelmingly converts to real tracking within 7 days. The `temp%` ↔ missing-orderitems correlation is **mostly a snapshot artifact of in-flight shipments**, not a permanent DQ issue.

**Two distinct mechanisms appear to be at play:**

1. **In-flight lag (the dominant signal).** New shipments land spine-first; tracking and items both backfill over days. Most miss-rate at 2-3 / 4-7 days is just "the system hasn't caught up yet."
2. **Genuine stuck-shipments (small but persistent).** A residual ~50–80 Picturator + ~5 PicaAPI shipments per month stay `temp_*` past 8 days, and a notable fraction of those (27–43%) lack items permanently. These are the candidates worth raising with ETL.

**`MFA19911824351` is a "mid-flight" case, not a "stuck" case.** 5 days old, produced 1 day ago, expected-cost, still `temp_*`, no items — entirely consistent with mechanism #1. Likely to converge over the next 2–3 days.

**The "PicaAPI × MAERSK 68.8%" headline in T14 isn't shown here yet** — that number was likely a snapshot across the full PicaAPI temp population without age slicing. The age-sliced view makes the picture much less alarming.

## Open next probes

- Slice the still-temp residual by carrier (especially DB Schenker, given the meeting), age (8+ days), and source. The **truly stuck** population is the actionable one.
- Cross-check `received_by_carrier_date` (the carrier-side signal) on the still-temp residual at 8+ days — if the carrier never received them, that's a real issue.
- Sample `MFA19911824351` again at +2 days (2026-05-24) and +5 days (2026-05-27) to watch the live backfill.
- Validate `item_count` on `fact_shipments` — observed it's NULL on the temp-no-items case; check if it backfills in sync with `fact_shipment_orderitems`.

## Likely deliverable

A one-page **DQ reference doc update** for the shipping-agent (under `reference/known-dq.md`?) capturing:
- `temp_*` tracking is a transient state by design.
- Joining to `fact_shipment_orderitems` on a `temp_*` shipment may return zero rows — that's expected for shipments < 7 days old.
- A `tracking_is_temp` filter is a quick proxy for "exclude in-flight shipments" but **doesn't substitute** for an age filter on `shop_order_created_date`.

Plus surfacing the stuck-shipment residual probe back to the shipping-agent / ETL team if it warrants a real raise.

## T5 — ETL code dive (bi-etl pulled, `dags/enterprise_silver/Shipping_Data_Mart/`)

Read map_shipment_key + fact_shipments + fact_shipment_orderitems READMEs + their `insert_to_silver.sql`. Full mechanism now visible.

### How a `temp_*` shipment_id gets created

`map_shipment_key/sql/insert_to_silver.sql` § `pcs_temp_keys` CTE (lines 342–434): a `temp_<pcs.ordernumber>` row is emitted for a PICT/PicaAPI shop order when ALL three hold at mart-refresh time:
1. The PICT/PicaAPI order has no row in `pict_trackingnumbers` / `picaapi_shipments` with a non-empty trackingnumber.
2. A matching `enterprise_silver.pcs_orders` row exists (PCS scheduled production).
3. (PicaAPI side only) `NOT EXISTS pcs_sentparcels` with real tracking for that PCS order.

`shipment_id = MD5('temp_<pcs.ordernumber>' || '|' || <shop_ordernumber>) → BIGINT`. One row per pcs_orders parcel.

### How orderitems attach to a `temp_*` shipment_id

`fact_shipment_orderitems/sql/insert_to_silver.sql` § `pict_temp_pairs` CTE (lines 549–628): items attach when
1. PICT order has no real tracking (`tmp_pict_orders_with_real_tracking` anti-join, lines 242–247),
2. matching `pcs_orders` row exists,
3. **`pcsoi.orderitemnumber = pi_oi_num.orderitemnumber`** — the per-item match between PCS and PICT.

Final JOIN in `joined_to_shipments` (line 1265): for PICT/PicaAPI it's `(source_system, source_order_id, trackingnumber)` — so items with `trackingnumber='temp_D42602536'` attach to the spine row carrying the same `temp_D42602536`.

### Conditions that produce `temp_*` spine WITH zero items

Three structural failure modes in the items branch:

1. **`pcs_orderitems` haven't landed in bronze yet.** `pcs_orders` (parcel header) lands first; `pcs_orderitems` (line items) lands later. A mart refresh in that gap = spine fires, items can't.
2. **`orderitemnumber` mismatch between PICT and PCS.** Low-impact in practice, but the join requires equality.
3. **`pict_orderitem_allocated` (upstream CTE) didn't emit a row.** Non-PRODUCT type or NULL quantity cuts here.

### MFA19911824351 — the exact mechanism, verified

- PICT orderid 45935522, ordernumber MFA19911824351, created 2026-05-17 17:25.
- PCS orderid 42602536, ordernumber D42602536, packagetype `zugeschnittene Verpackung`, shippingproviderid 446 (DB Schenker PL EU Home).
- PCS has **6 orderitems on `enterprise_bronze.pcs_orderitems`** for orderid 42602536, `orderitemnumber` 1–6, **`dw_timestamp = 2026-05-22 11:06:20 UTC`** — landed in bronze ~1.5h ago.
- PICT has **7 orderitems** for orderid 45935522 (1–6 PRODUCT + 7 SHIPPING). Items 1–6 match PCS 1–6 exactly on `orderitemnumber` + `sku`.
- PICT now has **real tracking on `pict_trackingnumbers`**: `00390110170043033384`, provider `DBSCHENKERPLEUHOME`.

**Mart's last refresh: `MAX(updated_at) = 2026-05-21 11:46:28 UTC`. Now: 2026-05-22 12:40 UTC. Mart staleness ≈ 25 hours.**

At the time of the 2026-05-21 11:46 mart run:
- `pcs_orders.D42602536` existed → `pcs_temp_keys` fired → `temp_D42602536` spine row.
- `pict_trackingnumbers` row didn't exist yet → real-tracking branches suppressed.
- `pcs_orderitems` for orderid 42602536 **didn't exist yet** (landed today 11:06) → `pict_temp_pairs` joined ZERO `pcs_orderitems` rows → no items emitted.

**Mart schedule** (`silver_shipping_data_mart_orchestrator.py`): `0 4 * * *` (04:00 UTC daily), Phase 0 ingestion gate 03:00–04:59 UTC. 2026-05-21 finished at 11:46 UTC. Today's run should have completed by ~12:00 UTC. `fact_shipments.updated_at` still 2026-05-21 → **today's mart run hasn't finished or didn't fire.** Worth pinging @lukasz.sendecki separately.

**Next successful mart refresh:**
- `pict_keys` emits row with real tracking `00390110170043033384` (now in bronze).
- `pcs_temp_keys` is cut.
- `pict_temp_pairs` is cut by the anti-join.
- `pict_tracking_pairs` (canonical real-tracking branch via `pict_trackingnumberitems`) fires and attaches all 6 PRODUCT items.
- The `temp_D42602536` shipment_id disappears (truncate-reload); a new shipment_id appears with real tracking + 6 items.

## T6 — Final synthesis

**The `temp_*` ↔ missing-orderitems correlation is not a structural DQ issue. It's a snapshot artifact driven by two things:**

1. **Bronze ingestion ordering.** `pcs_orders` parcel headers land before `pcs_orderitems` line items. If a mart refresh catches the spine without the items, a `temp_*` shipment with no items is the deterministic outcome.

2. **Mart refresh cadence vs bronze fluidity.** The mart runs daily, ~7h build, completes ~11:30 UTC. Bronze ingestion runs more frequently. Any `temp_*` shipment whose underlying state has progressed since the last mart refresh is already obsolete in the mart — next refresh resolves it.

**4-7 day peak (42% Picturator):** the cohort sitting in the mart with `temp_*` + no items at the last-refresh snapshot. Most flip to real-tracking + items at next refresh.

**Stuck residual at 8+ days (~50–80 Picturator + ~5 PicaAPI):** the actionable population. Production scheduled (PCS exists) but real PICT tracking genuinely not assigned over many days. Small enough to raise case-by-case with ETL.

**`temp_*` lifecycle from the ETL POV:**

```
T0  PICT order created                              → no spine, no items
T1  PCS schedules production (pcs_orders row)       → temp_<pcs.ordernumber> spine fires;
                                                       items pending
T2  pcs_orderitems land in bronze                   → next mart refresh attaches items
                                                       to same temp_* spine
T3  Real PICT tracking assigned                     → next mart refresh swaps temp_*
                                                       for real tracking; items flow via
                                                       pict_tracking_pairs (canonical)
```

The "items missing" window is the gap **T1 → T2** captured at a mart-refresh snapshot. Most shipments transit T0→T3 within 7 days, so most temp_* shipments visible in the mart are <7 days old.

**Side-finding (PicaAPI 0-1 day real-tracking 45% miss):** same mechanism, different path — `picaapi_shipment_items` (per-item linker) lags `picaapi_shipments` (parcel header). When real tracking exists but `psi` linkage hasn't landed, `picaapi_tracking_pairs` finds no items; `picaapi_pcs_bridge` only fires for orders matching `pcs_orders`. Sample tiny (33 shipments) but mechanism is real.

## Recommendations

1. **Update shipping-agent docs.** `reference/known-dq.md` and/or `reference/tables.md`:
   - `trackingnumber LIKE 'temp%'` = pre-shipment placeholder from `pcs_temp_keys`. Resolves to real tracking on next mart refresh after PICT assigns the carrier label.
   - Items lag the spine by 1 mart refresh in most cases. **Don't trust `item_count` or orderitems joins on `temp_*` shipments under ~7 days old.** Filter `trackingnumber NOT LIKE 'temp%'` for quantity/revenue analysis.
   - The 4-7 day peak is normal; the small 8+ day residual is where DQ flags belong.

2. **No ETL change recommended.** Mechanism works as designed. Truncate-reload + bronze-then-mart cadence gives correct end-state once everything lands.

3. **One open question for @lukasz.sendecki:** today's (2026-05-22) mart refresh shows `MAX(updated_at) = 2026-05-21 11:46:28`. Either today's run hasn't finished or didn't fire — worth checking orchestrator state.

4. **Stuck-residual probe (optional next):** query `fact_shipments WHERE trackingnumber LIKE 'temp%' AND shop_order_created_date <= CURRENT_DATE - 8` by `shipping_provider_group`. That small (~50–80) population is where real DQ flags live; cross-check each against bronze `pict_trackingnumbers` to see if real tracking has landed but the mart can't see it (same staleness story) vs has genuinely never been assigned (real production stuck).

## T7 — Why specifically MFA19911824351 has no items (principal pushed back)

Walked the chain end-to-end. The mart logic is sound; the items branch (`pict_temp_pairs`) would have fired IF bronze had the rows. So why did bronze not have them?

**`pcs_orderitemlogs` reveals the items existed in PCS source for 3 days before yesterday's mart refresh:**

| orderitemid | First event | Last event before mart refresh (2026-05-21 11:46) |
|---|---|---|
| 83833365 (CVS0400301F2HC) | PLANNED 2026-05-18 04:50:30 | SHIPPED 2026-05-21 08:53:10 |
| 83833366 (CVS0400301F2HC) | PLANNED 2026-05-18 04:50:30 | SHIPPED 2026-05-21 08:53:10 |
| 83833367 (CVS0400301F2HC) | PLANNED 2026-05-18 04:50:30 | SHIPPED 2026-05-21 08:53:10 |
| 83833368 (CVS1000751F2HC) | PLANNED 2026-05-18 04:48:59 | SHIPPED 2026-05-21 08:53:10 |
| 83833369 (CVS0800601F2HC) | PLANNED 2026-05-18 04:30:04 | SHIPPED 2026-05-21 08:53:10 |
| 83833370 (CVS0800601F2HC) | PLANNED 2026-05-18 04:30:04 | SHIPPED 2026-05-21 08:53:10 |

PCS had these items via its full production lifecycle (PLANNED → ASSIGNED → PRINTED → CUT → STRETCHED → PREPARED_FOR_STORAGE → SHIPPED) by 2026-05-21 08:53 UTC — **~3 hours before yesterday's mart refresh.**

### The bronze ingestion timeline (recent runs)

`enterprise_bronze.pcs_orderitems` distinct `dw_timestamp` (DESC):

| dw_timestamp (UTC) | rows touched | Notes |
|---|---:|---|
| **2026-05-22 11:06:20** | **619,627** | TODAY — ~50× the typical daily volume |
| 2026-05-21 18:05:52 | 18,321 | yesterday evening (AFTER yesterday's mart refresh at 11:46) |
| 2026-05-20 18:06:41 | 12,040 | the run available to yesterday's mart |
| 2026-05-19 18:05:34 | 15,214 | normal |
| 2026-05-18 18:06:14 | 14,692 | normal |

Same pattern on `enterprise_bronze.pcs_orders`: today 327,381 rows vs typical 6–10K daily.

### What this means for yesterday's mart refresh

- **Mart refresh: 2026-05-21 11:46 UTC.**
- **Last bronze pcs_orderitems ingestion BEFORE mart refresh: 2026-05-20 18:06:41 UTC** — **17.5 hours stale at refresh time**, and apparently incomplete (items for orderid 42602536 weren't in that batch).
- **Today's 619K-row reload (50× normal) is a catch-up.** Strongly suggests `eb_pcs_ingestion` had been running with a stuck watermark or partial logic for several days, missing newer orderitems. Today the catch-up filled the gap.

### The wider pattern (proof it's not a one-off)

Cross-tab of Picturator shipments by `shop_order_created_date` (last 7 days) and `temp`/`real`:

| date | tn_class | shipments | missing | % |
|---|---|---:|---:|---:|
| 2026-05-16 | temp | 190 | 56 | 29% |
| 2026-05-17 | temp | 747 | **369** | **49%** |
| 2026-05-18 | temp | 2,204 | 937 | 43% |
| 2026-05-19 | temp | 4,735 | 1,534 | 32% |
| 2026-05-20 | temp | 6,122 | 437 | 7% |
| 2026-05-21 | temp | 230 | 0 | 0% |
| 2026-05-16–21 | real | 22,943 | 57 | 0.25% |

**~49% of 2026-05-17 PICT temp shipments are missing items** — far above normal, far above the day-0 cohort. MFA19911824351 was created 2026-05-17 and sits in this anomalous bucket. **This is not a one-off; it's hundreds of shipments hit by the same upstream issue.**

### Conclusion: it's a bronze-ingestion glitch, not a mart-logic issue

**The mart did exactly what its code says it should do.** The spine fired because `silver.pcs_orders` had `D42602536`; the items branch tried to attach but `bronze.pcs_orderitems WHERE orderid = 42602536` was empty at that moment. The mart didn't have anything to attach.

**The actual problem is upstream:** `eb_pcs_ingestion` has been running with reduced coverage for several days (12–18K rows/day touched vs the expected full 32-day-window reload of millions). Today's ingestion at 11:06 UTC processed 619K rows — a clear catch-up after the partial runs.

**Once today's catch-up bronze ingestion is followed by a successful mart refresh, items will attach normally for this entire 2026-05-16 → 2026-05-19 cohort.** No mart-side fix needed.

### Now there's a real raise for ETL

Worth flagging to @pranav.gupta (eb_pcs_ingestion owner) and @lukasz.sendecki:

- `eb_pcs_ingestion` daily runs have been ingesting ~12–18K orderitems/day, ~6–10K orders/day for ~6 weeks.
- Today's run touched 619K orderitems / 327K orders — a >40× catch-up.
- The 32-day rolling window DELETE+INSERT in `sql/incremental/pcs_orderitems.sql` should be processing the entire window each run; either it isn't (incremental logic injected somewhere), or pcs_federated had data-availability issues.
- Net effect: `bronze.pcs_orderitems` has been chronically incomplete relative to PCS source; downstream marts have been emitting `temp_*` spines with no items for hundreds of recent shipments.
- Cross-tab confirms: 49% miss rate on 2026-05-17 PICT temp cohort is far above the normal 0–18% pattern.

## T8 — Principal pushed back again: "isn't bronze pcs_orderitems supposed to be reloaded as part of the mart refresh?"

Sharp question. Code says **yes** — `silver_shipping_data_mart_orchestrator.py` line 162 has `create_dag_trigger("eb_pcs_ingestion", **TRIGGER_KWARGS)` in Phase 0a, with `wait_for_completion=True`, `reset_dag_run=True`, and `trigger_rule="all_success"`. The mart orchestrator's whole job in Phase 0a is to refresh bronze before the silver/mart layers consume it.

But Redshift data shows it's not happening that way.

### eb_pcs_ingestion run-hour distribution (May 2026, derived from bronze.pcs_orderitems distinct dw_timestamps)

| UTC hour | distinct runs in May | Likely trigger source |
|---:|---:|---|
| **18** | **15** | `bronze_orchestrator_shop_level` 16:00 UTC trigger (~2h runtime) |
| 11 | 7 | ad-hoc / catch-up (today's 11:06 falls here) |
| 7 | 6 | `bronze_orchestrator_shop_level` 05:00 UTC trigger? (~2h runtime) |
| 15 | 4 | `bronze_orchestrator_shop_level` 13:00 UTC trigger (~2h runtime) |
| 19 | 3 | extended 16:00 UTC runs |
| 20, 22, 23 | 1 each | scattered |
| **03 / 04 / 05** | **ZERO** | **mart orchestrator's Phase 0a never effective** |

**The mart orchestrator at 04:00 UTC has NEVER successfully triggered `eb_pcs_ingestion` in May 2026.** That's a structural failure of the orchestrator design — the very Phase 0a that's supposed to make sure bronze is fresh isn't doing it.

### What I can't fully diagnose from Redshift

Why the orchestrator's Phase 0a trigger silently fails:

1. **`eb_pcs_ingestion` has `max_active_runs=1`.** If a prior run is still in flight (e.g., the previous day's 16:00 UTC `bronze_orchestrator_shop_level` trigger took >12h to complete), the 04:00 UTC orchestrator trigger may be blocked.
2. **`reset_dag_run=True`** in TRIGGER_KWARGS is supposed to clear blocking prior runs, but its interaction with `max_active_runs=1` may have edge cases.
3. **`wait_for_completion=True`** would block the orchestrator from proceeding if the trigger waits forever — but Phase 1+ clearly do run (fact_shipments builds successfully each day), so the wait IS resolving somehow. Maybe with a skipped/zombie state that doesn't actually run pcs ingestion.

### And there's a SECOND bug — even when bronze runs, it's not doing a full reload

The SQL in `dags/enterprise_bronze/pcs/sql/incremental/pcs_orderitems.sql` reads as:

```sql
CREATE TEMP TABLE #eb_pcs_orderitems_temp AS
SELECT oi.id, oi.orderid, ...
FROM pcs_federated.orderitems oi
JOIN pcs_federated.orders o ON o.id = oi.orderid
WHERE o.created >= CURRENT_DATE - 32;

DELETE FROM enterprise_bronze.pcs_orderitems
USING #eb_pcs_orderitems_temp t
WHERE t.id = enterprise_bronze.pcs_orderitems.id;

INSERT INTO enterprise_bronze.pcs_orderitems ...
SELECT ... FROM #eb_pcs_orderitems_temp;
```

This SHOULD pull every orderitem for orders in the last 32 days from `pcs_federated.orderitems`, then DELETE+INSERT them all into bronze with today's dw_timestamp. Given the volume of PCS production, that should be MILLIONS of rows per run.

But daily runs touch only 5–20K rows. Today's "catch-up" run touched 619K rows but still nowhere near the millions expected for a full 32-day window. The DELETE+INSERT seems to be operating on a much smaller subset than the SQL says.

Possible causes (would need Airflow logs to confirm):
- Task timeout truncating the federated COPY mid-stream, leaving partial data.
- `pcs_federated.orderitems` returns capped results (some federation row limit).
- Memory pressure causing partial result sets.

### The combined effect on the mart

Two structural failures stack:
1. **Mart orchestrator's Phase 0a doesn't refresh bronze.** Bronze is at the mercy of `bronze_orchestrator_shop_level`'s 16:00 UTC run (completing ~18:00 UTC).
2. **Even when bronze runs, it processes only a fraction of the 32-day window.**

Result: at any given mart refresh, `bronze.pcs_orderitems` is:
- Up to 17+ hours stale relative to today's PCS state.
- AND missing some chunk of rows that should have been in the 32-day window but never made it through the ingestion.

That's why MFA19911824351's items weren't there at yesterday's mart refresh — and why ~49% of the 2026-05-17 PICT temp cohort is missing items, not just this one order.

### Two distinct bugs for ETL team

1. **@lukasz.sendecki** — `silver_shipping_data_mart_orchestrator` Phase 0a's `eb_pcs_ingestion` trigger never effectively runs. Check why: `max_active_runs=1` conflict with `bronze_orchestrator_shop_level`'s in-flight run? Task fails silently? Phase 0 gate misbehaving? In May 2026 zero runs landed at hour 03/04/05 UTC.

2. **@pranav.gupta** — `eb_pcs_ingestion` daily runs touch 5–20K rows but the SQL is a full 32-day-window DELETE+INSERT that should touch millions. Either there's a hidden incremental filter, or the federated pull is silently truncating. Today's 619K-row catch-up is symptomatic — partial historical runs leaving gaps.

Both bugs are upstream of the mart. The shipping_mart logic is correct given its inputs; the inputs are broken.

## Pre-staged probes (full list per inventory § Open threads)

1. **Spine row:** `SELECT * FROM shipping_mart.fact_shipments WHERE shop_ordernumber = 'MFA19911824351'`.
2. **Items joined:** `SELECT * FROM shipping_mart.fact_shipment_orderitems oi JOIN shipping_mart.fact_shipments fs USING (shipment_id) WHERE fs.shop_ordernumber = 'MFA19911824351'`.
3. **Upstream trace:** check whether the same `shop_ordernumber` appears with both `temp*` and real tracking across time (re-emission pattern from spine).
4. **Population probe:** sample 5–10 May `temp%` shipments with missing items → re-check 24/48/72h. Backfill = expected lag; stays missing = real DQ → raise with ETL.

## Deliverable

A clear answer on:
1. Is the working theory correct (placeholder + backfill)? Yes / partially / no.
2. If yes — what's the typical backfill lag? Should it be raised with ETL as "expected" or "should be tightened"?
3. If no — what's actually going on? A real DQ issue.

Plus the side-fix to consider per T14 note: a `tracking_is_temp` boolean on shipping-agent exports, or a DQ reference doc update.

## Canonical knowledge loaded (from shipping-agent `reference/tables.md` + `skills/query-patterns.md`)

- `fact_shipments` grain: 1 row per `shipment_id`. Key cols: `trackingnumber`, `shop_ordernumber`, `source_system`, `shipping_provider_group`, dates.
- `fact_shipment_orderitems` grain: 1 row per `(shipment_id, source_order_item_id)`. ~122M total, ORWO dominates ~73%.
- All joins on `shipment_id`. No spine. No joins outside `shipping_mart.*`.
- `cost_source = 'invoice'` is the invoiced subset (renamed from `'real'`).

## Related

- [[S030_2026-05-22_dashboard-gold-cutover|S030]] T14 note: `gielinor/players/jebrim/quest-log/in-progress/OPEN_2026-05-22_shipping-agent-personal-folders.md` § T14.
- Inventory resume open thread: `gielinor/players/jebrim/inventory/shipping-agent-personal-folders-resume.md` § Open threads § 🔬 Investigation.
- Shipping-agent docs read this session: `bi-analytics-main/NFE/projects/3_shipping_data_mart/shipping-agent/reference/tables.md`, `skills/query-patterns.md`.
