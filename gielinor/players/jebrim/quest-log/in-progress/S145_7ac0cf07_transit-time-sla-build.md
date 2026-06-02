# Transit-time SLA build — TCG carrier proxy-SLA, productionized

**Player:** Jebrim | **Session:** 7ac0cf07 | **Date:** 2026-06-02 | **Status:** in-progress (PLAN LOCKED, build not started)

Extends [[S124_fd13a7a7_carrier-proxy-sla-2026q1|S124]] (the carrier proxy-SLA / transit-time baseline xlsx). This is the productionized build coming out of the 2026-06-02 SLA meeting.

## Asked
Build the transit-time SLA the business communicates to customers, empirically from our own delivered shipments (no carrier files for now). Came out of a meeting (Niklavs, Andrea Rampinini, Sven Neu, Torsten Harnau, Justus Kaiser). Discussion-only this session — converge on a clear plan, build later.

## What the meeting agreed (resolution-backed; see the recap)
- Granularity = **per country**, with a **standard / oversized** split. Customer sees one number per country per bracket — no per-SKU/per-service/per-carrier.
- Multi-carrier country: meeting said "take the longer of the two"; **Niklavs refined this** to volume-weighted judgement (a thin slow tail shouldn't drag the country). Tell Andrea (he) we're refining it.
- US → 3–4 zone/state clusters, not 50 states, not one US number.
- Transit time = carrier entry-scan → delivery; +1 on line-haul legs (deferred).
- Lead time = sum of components (each a sample), not per-order end-to-end.
- Be generous now (revisit end of summer). Source from carrier files later; validate against data.

## Locked plan (Niklavs' decisions folded in)
**Scope/cohort**
- Vertical: **All TCG** — exact `source_system` set resolved via shipping-agent contract, NOT hardcoded.
- Window: rolling last full ~3 months, delivery present, `is_returned = false`, exclude still-settling tail.
- Brackets: **standard** (all carriers except DB Schenker) + **oversized** (DB Schenker is the oversized carrier — included after all).
- Metric: **p90 decimal BUSINESS days**, computed by us from `carrier_received` + `delivered` timestamps. Do NOT use the mart's pre-rounded business-day field (rounded = bad). Business days, not calendar (calendar deferred if customer comms needs it).

**Analysis grain → outputs**
- Per **extkey (carrier-service) × country**: p90 BD transit + volume (+share) + **coverage %**.
- Collapse to one SLA per country per bracket by **volume-weighted judgement** (evidence prepared, call is ours — don't mechanize; cf. [[don't-mechanize-judgment-in-analytical-reports]]).
- **Full lead time per extkey × country**, mart timestamps only, **coverage noted per dimension** — exposes which carriers carry a big pre-`carrier_received` gap (line-haul/processing). Computed only where timestamps exist. Line-haul stays OUT of the headline SLA.
- **US:** shipping-agent investigates state-level transit → proposes 3–4 clusters; final cut is ours.

**Data routing**
- All mart pulls via the **shipping-agent** (gold contract, **NO raw access** — use what's in the mart).
- Agent's first pass confirms before any number: timestamps present in gold + coverage (production / truck-closed? / carrier_received / delivered); US **state/ZIP** field; **TCG** `source_system` set; decimal-BD-from-timestamps basis.

**Deliverable**
- Near-term: analysis output (per-country SLA standard+oversized, US clusters, evidence sheet: per-extkey p90 / volume share / coverage / full-lead-time gap) + a **dummy/structure list for BI by mid next week** (meeting commitment).
- End-state: a **`dim_carrier_sla`** table in the shipping mart — defined LAST, once the analysis tells us its shape (carrier group / service extkey / dest country or US zone / bracket / agreed p90 BD SLA + alert columns). Not designed up front.

**Project**
- New `NFE/shipping_topics/NN_transit_time_sla/` (`sql/ data/ notebooks/ README`), porting S124 baseline cohort + transit logic rather than rebuilding.

## Next step (awaiting explicit go)
Spawn shipping-agent (read-only) for the grounding pass — schema/coverage/TCG-set/state-field — report back before any SLA numbers. Build has NOT started; Niklavs confirms before kickoff.

## Turn log
- 2026-06-02: recap of the meeting (corrected a granularity slip — see harvest), then planning. Methodology harvest landed (read-for-the-governing-signal global skill; act-only-when-merited lorebook + niksis8 drafts). Plan locked this turn; persisted here + inventory resume. No build.
- 2026-06-02: **shipping-agent run (step 2: truck-join verify + core pull).** Gold contract, read-only, NO raw layer. Cohort = 650,400 TCG shipments (Picturator+PicaAPI, received 2026-03-01..current-14, non-returned).
  - **(A) Truck-join verdict:** `fact_truck_charges.truckload_id` = `fact_shipments.truckload_id`. Grain **1:1** — truckload_id unique in truck table (2,361 rows / 2,361 distinct / 0 dup), rows-after-join = cohort size, **no fan-out**. `departure_ts` 100% present on matched truck rows but overall cohort coverage only **47.5%** (NOT the meeting's 80-90%) — loss is entirely at the join: of 590,212 shipments carrying a truckload_id, only 308,867 (52%) match a truck-charges row. Structural: truck table covers only truck-leg carriers. By carrier: UPS 97%, DHL 71.5%, DPD UK 67%, MAERSK 18%; ONTRAC/DPD PL/USPS/FEDEX/ASENDIA/DB SCHENKER/DIRECT LINK all 0%.
  - **(B) Headline:** overall **p90 transit = 4.18 decimal business days** (median 2.14, p95 5.15), basis 600,710 delivered ex-DPD-UK. Standard country p90: Germany 3.14, US 4.14, UK 4.21 (cov only 66%), France 5.21, NL 3.94, Italy 5.12, Spain 5.49, Canada 10.25. Oversized (DB Schenker) p90: Germany 6.24, France 11.07, Italy 10.16.
  - **DQ — line-haul segment dead in gold:** `departure_ts` is a same-day modeled truckload stamp ~3.92h AFTER carrier-received (99.3% same calendar day); departure->received clamps to ~0 for 99.9% of rows. **No extkey×country carries a material line-haul segment** on the brief's definition — flagged to Niklavs. Meaningful our-side segment is produced->departure (median 0.78 BD, p90 1.16).
  - Checks: monotonicity 0 violations; clock inversions transit 2,163 / seg1 3,671 / seg2 308,551 (the line-haul artifact); decomposition seg3-cov vs delivered-cov reconcile max diff 0.0; null destination_country 810 (0.12%). Low-coverage rows to treat describe-only: Switzerland standard 2.1%, Finland oversized 2.8%.
  - **Artifacts (outside brain):** `bi-analytics-main/NFE/shipping_topics/44_transit_time_sla/` — `sql/20260602-01_transit_sla_per_shipment.sql`, `sql/build_transit_sla.py`, `data/transit_sla_per_shipment.parquet` (650,400 rows), `data/evidence_transit_sla_by_extkey.{csv,parquet}` (138 rows), `data/evidence_transit_sla_country_bracket_rollup.{csv,parquet}` (60 rows), `data/evidence_leadtime_decomposition_by_extkey.{csv,parquet}` (138 rows).
  - Not done (separate steps, per brief): US zone clustering; collapse to single per-country SLA (human judgement). Open for Niklavs: the line-haul segment can't come from gold's departure_ts — needs carrier files or a different anchor if line-haul attribution is required.
- 2026-06-02: **US clustering + site-grain re-agg (shipping-agent step 3)** — 4 US zones (1_fast_near 2.87 / 2_mid 3.78 / 3_far 4.65 / 4_remote 7.96 p90), no real 1-2d bucket, USPS the laggard. Sites: PCS PL (507K, EU) + PCS CMH (136K, US) dominate; PCS PL→US is a rare 15-BD transatlantic lane. departure_ts confirmed a modeled same-day stamp → logged to shipping-agent known-dq.md; idle = produced→received.
- 2026-06-02: **Built dim_carrier_sla DRAFT v1** (`44_transit_time_sla/build_dim_carrier_sla.py` → `outputs/dim_carrier_sla_v1.xlsx`, 3 sheets: dim_carrier_sla full per-extkey + sla_summary lane-level target + definitions). Imputation: selected = ceil(pooled-lane-p90), one std value per (site,country/zone), DB Schenker oversized its own. Decisions locked: p90 BD, All TCG (Picturator+PicaAPI), DB Schenker=oversized, ceil round-up generous, valid_from 2026-07-01, US zone column added, volume<50 floor, null-country dropped (810).
  - **3 bugs caught+fixed during build:** (1) transit_bd stores NaN (not null) for undelivered → polars sorts NaN largest → quantile/coverage wrong + lanes >10% undelivered blanked; fix NaN→null. (2) join on null destination_region key (null≠null) blanked `selected` for all non-US lanes; fix null-safe sentinel key. (3) PermissionError — file open in Excel blocked write.
  - **Switzerland-PL standard = no SLA derivable:** ~100% UPS04STD, which has 0 delivered events on non-EU lanes (CH + AU both 0%, all EU ~99%) — a UPS non-EU delivery-feed ingestion gap, not a country blackout. Candidate known-dq note (not yet written).
- 2026-06-02: **Built region_zone_crosswalk** (`44_transit_time_sla/build_region_zone_crosswalk.py` → `outputs/region_zone_crosswalk.{xlsx,csv,parquet}`). The US `destination_region` (zone) in dim_carrier_sla is zip3-clustered and **not joinable** to the mart's `shipping_region` (state name) — this is the missing state→zone bridge. 59 rows: all 50 states + DC + PR + VI → zone + per-site standard SLA. Three joinability fixes baked in: (1) **alias rows** for the 5 states the mart also stores as 2-letter codes (MN/OH/PA/NY/NJ — region_clean normalized them in the build, so a raw join on shipping_region would silently drop coded rows); (2) **blank-region** row (US blank shipping_region was modal-bucketed to 2_mid, 115 ships); (3) **per-site SLA** columns — sla_bd_cmh (PCS CMH = US site, ~99.5% vol; zones 1/2/3/4 = 3/4/5/9) + sla_bd_pl_transatlantic (rare PL→US, 15-17 BD). Caveat flagged: zone-4 PL SLA (=4) is a 1-shipment artifact, ignore. xlsx = crosswalk + zone_summary + definitions sheets.
- 2026-06-02: **Folded by-state view into the deliverable** — added `dim_carrier_sla_by_state` sheet to `dim_carrier_sla_v1.xlsx` (extended `build_dim_carrier_sla.py`, re-ran; sheets now: dim_carrier_sla / dim_carrier_sla_by_state / sla_summary / definitions). Same columns as dim_carrier_sla, each US zone row exploded to its states (destination_region = state name, joinable to mart shipping_region); states inherit the zone's selected SLA + stats (volume/stats are ZONE-level copied, not per-state — flagged in defs). 334 rows, 278 US (50 states+DC+PR+VI + MN/OH/PA/NY/NJ 2-letter alias rows). **`selected` is authoritative from the dim** (volume<50 floor applied) — note zone-4 remote/offshore CMH = 8 here vs the standalone crosswalk's 9 (crosswalk didn't apply the floor; the by-state sheet is the one to use).
- 2026-06-02: **Added `sla_summary_by_state` sheet** too (same explode applied to the lane-summary sheet). Workbook now 5 sheets: dim_carrier_sla / dim_carrier_sla_by_state / sla_summary / sla_summary_by_state / definitions. 142 rows / 112 US. Same zone-level-volume + alias-row caveats, documented in definitions.
- 2026-06-02: **CLOSE (S145).** Quest stays in-progress — deliverable v1 built, judgement layer pending. No pending external actions. NFE project files (`44_transit_time_sla/*`) on disk in bi-analytics-main, NOT committed (separate principal repo). shipping-agent `reference/known-dq.md` edited (departure_ts note, authorized) NOT committed (separate repo). Harvest: 3 brain drafts written mid-session (read-for-the-governing-signal skill, act-only-when-merited lorebook, niklavs-asks-to-explore niksis8) + 1 cross-conv memory. Brain commit scoped to my 7ac0cf07 pathspecs only (NOT the broad-tree dirty/untracked from sibling sessions — [[S131_0b0f2049_lived-operator-severity-audit|S131]] #1 hazard).
