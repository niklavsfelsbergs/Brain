# Dwarf trace — `received_by_carrier_ts` lineage (bi-etl)

**Spawned by:** principal (Jebrim), parallel to a behavioral/empirical agent on the mart data.
**Question:** what real-world event populates `received_by_carrier_ts` on `shipping_mart.fact_shipments`, and from which feed — (a) carrier TRACKING scan, (b) EDI/manifest/pre-advice handover, or (c) internal label-print echo?
**Repo:** `C:/Users/niklavs.felsbergs/Documents/GitHub/bi-etl` (pulled main, current as of 2026-06-10).
**Status:** RESOLVED for the two systems that populate it (PICT + PicaAPI). Verdict: (a) carrier tracking event. Lineage bottoms out at the Picturator/PicaAPI app event logs — app-side event acquisition is upstream of the warehouse and not documented in bi-etl.

## Lineage chain (gold ← silver/temp ← bronze ← source)

GOLD `shipping_mart.fact_shipments.received_by_carrier_ts`
  ← built in `dags/shipping_mart/fact_shipments/sql/insert_to_silver.sql:1029`
    `ev.received_by_carrier_ts AS received_by_carrier_ts` (date sibling :1028 = `::DATE`)
    `ev` = TEMP `tmp_events_unioned` (:804-819) = UNION ALL of tmp_pict_events + tmp_picaapi_events, LEFT JOINed onto the spine
  ← TEMP `tmp_pict_events` (:746-762):
    `MIN(CASE WHEN event_upper IN ('OUTBOUND','TRANSIT','PICKED_UP') THEN event_ts END)`
    over `tmp_pict_events_base` (:727-743) = `enterprise_bronze.pict_shipmentlogs` (event_ts=`"timestamp"`, event_upper=`UPPER(event)`) JOIN `pict_trackingnumbers`
  ← TEMP `tmp_picaapi_events` (:787-799): same rule over
    `enterprise_bronze.picaapi_shipment_trackings` (event_ts=`tracking_time`, event_upper=`UPPER(status)`) JOIN `picaapi_shipments`
  ← BRONZE `enterprise_bronze.pict_shipmentlogs`
    loaded by `dags/enterprise_bronze/picturator/sql/pict_shipmentlogs.sql` — append-only INSERT from `picturator_federated.shipmentlogs` (cols: id, trackingnumberid, timestamp, event, description)
    DAG `bronze_picturator` reads `picturator_federated` = Redshift federated queries to **Picturator Postgres** (the primary e-commerce platform DB)
  ← BRONZE `enterprise_bronze.picaapi_shipment_trackings`
    loaded by `dags/enterprise_bronze/picaapi/sql/picaapi_shipment_trackings.sql` — append-only from `picaapi_federated.shipment_trackings` (cols: id, shipment_id, tracking_time, status)
  ← SOURCE: Picturator / PicaAPI **application shipment-event logs** (federated app DBs). Event-acquisition mechanism is the app's job, NOT in bi-etl.

## Per-carrier / per-source divergence (IMPORTANT)

Only **PICT (Picturator) and PicaAPI** populate `received_by_carrier_ts`. The other 3 source systems land NULL by design:
- **ORWO** — no carrier event stream. `orwo_orderdeliveryview.sentat` is *production dispatch* (parcel out the door at Wolfen), routed to `order_produced_ts`, NOT here. Corrected per Niklavs 2026-05-21; ORWO `received_by_carrier_ts` now 0% populated (honest NULL). See `dags/shipping_mart/orwo_open_pointers.html` + `insert_to_silver.sql:1024-1027` + DAG header :50-52. NOTE: README.md:140 still has a STALE row claiming ORWO sources it from sentat — contradicted by the live SQL.
- **PCS, Rewallution** — no carrier-pickup event in their feeds → NULL.

So `received_by_carrier_ts` is carrier-event-derived for shop-side (PICT/PicaAPI) shipments only.

## Verdict: (a) carrier TRACKING event — NOT (b) EDI/manifest, NOT (c) label-print echo

Decisive in-repo evidence — the shipment-log vocabulary (`README.md:428-453`, T-11 inspection of the event/status set, identical canonical set across PICT uppercase + PicaAPI lowercase, consistent across 800+ carrier codes):

| Literal | Interpretation (per README) |
|---|---|
| TRANSIT (34.5M) | In motion between facilities |
| OUTBOUND (6.4M) | Left origin facility |
| PICKED_UP (592K) | Carrier took possession |
| OUT_FOR_DELIVERY | With last-mile driver |
| DELIVERED | Final delivery |
| EXCEPTION / DELAYED / NOT_DELIVERED / DESTROYED / AWAITS_PICKUP_BY_RECEIVER | carrier track-and-trace lifecycle states |
| **LABEL_CREATED (6.8M)** | "Label generated — **not shipped**" — explicitly EXCLUDED from the ship rule |
| NOTIFICATION | pre-ship-or-ETA, ambiguous — also excluded |

This is a **carrier track-and-trace lifecycle vocabulary**. The clincher against (c)/(b): `LABEL_CREATED` is a *separate, distinct* event that exists in the same stream and is deliberately excluded; `received_by_carrier_ts` keys on physical-movement events (OUTBOUND/TRANSIT/PICKED_UP), not label creation. If it were a label-print/manifest pseudo-event it would key off LABEL_CREATED. So the *column rule* is explicitly designed to be a movement scan, not a handover ack.

## The caveat that explains Niklavs' suspicion (it lands at our facility)

README.md:436/440 — OUTBOUND = "Left origin facility", TRANSIT = "In motion between facilities". The **earliest movement event** (`MIN`) is taken. For PicaNova's network the first scan/movement event can be at PicaNova's own dispatch/origin facility (carrier collection from our hub / first-mile injection scan), which is *before* the carrier's downstream hub — so the timestamp legitimately lands early/at our facility even though it IS a carrier-network event, not a manifest pseudo-event. Picking OUTBOUND/TRANSIT (the README's "first entered the carrier network / left the production site", source def :63) means: first carrier-network movement scan, which for an origin-facility carrier scan is physically at/near PicaNova. That is real-but-early, not fake.

Portfolio caveat already flagged by the team (README.md:489-492): shipment logs have non-trivial DQ; trustworthy in aggregate, individual shipments may be wrong; OK for cohort/carrier-level, flag in per-shipment reporting.

## How far the trace bottoms out / what's MISSING

The bi-etl warehouse trace is complete to the **Picturator/PicaAPI application event logs** (`picturator_federated.shipmentlogs`, `picaapi_federated.shipment_trackings`). **What bi-etl does NOT document:** how the Picturator/PicaAPI apps themselves acquire these events — i.e. whether the app subscribes to carrier tracking webhooks/APIs directly, via an aggregator (AfterShip/ParcelPerform-style), or some mix. Grepped for aftership/webhook/carrier-api/aggregator across `dags/shipping_mart` — no hits (only Slack alert webhooks). That acquisition layer is upstream of the warehouse and out of this repo's scope. The vocabulary + the explicit LABEL_CREATED exclusion are strong enough to call it (a) carrier tracking; the only thing unconfirmed-in-repo is the exact carrier-feed plumbing inside the source app.

## Key file refs
- `dags/shipping_mart/fact_shipments/sql/insert_to_silver.sql` — :749/:790 (the MIN-event rule), :1024-1029 (gold projection + ORWO-NULL comment), :727-799 (event temps), :804-819 (union)
- `dags/shipping_mart/fact_shipments/shipping_mart_fact_shipments_dag.py` — :1-70 header (Reads/Writes lineage, OUTBOUND/TRANSIT→MIN rule :44, ORWO NULL :50-52)
- `dags/shipping_mart/fact_shipments/README.md` — :428-492 (vocabulary + derivation rules + coverage), :140 (STALE ORWO row)
- `dags/enterprise_bronze/picturator/sql/pict_shipmentlogs.sql` — bronze ingest from picturator_federated
- `dags/enterprise_bronze/picaapi/sql/picaapi_shipment_trackings.sql` — bronze ingest from picaapi_federated
- `dags/enterprise_bronze/picturator/bronze_picturator.py` — :6 federated source = Picturator Postgres
- `data_definition_claude/source_systems.md` — :11-12 (Picturator/PicaAPI = e-commerce platform feeds), :63 sl_shipped def "first entered carrier network / left production site"
- `data_definations_claude/shipping_data_mart_definitions.md` — :63 sl_shipped_date source map
- `dags/shipping_mart/orwo_open_pointers.html` — ORWO received_by_carrier NULL correction
