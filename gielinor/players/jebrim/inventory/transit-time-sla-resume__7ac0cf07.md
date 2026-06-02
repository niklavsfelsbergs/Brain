---
quest: S145_transit-time-sla-build
sid8: 7ac0cf07
ts: 2026-06-02 11:50
open_dep: principal review of dim_carrier_sla v1 + 3 judgement calls (Switzerland-PL standard blank / PCS-PL→US zone collapse / low-coverage directional lanes)
---

# Resume — transit-time SLA build (S145, 7ac0cf07)

**Where we are:** dim_carrier_sla DRAFT v1 BUILT (`44_transit_time_sla/outputs/dim_carrier_sla_v1.xlsx`). Awaiting Niklavs' review + judgement edits. Steps done: grounding, core transit pull, US clustering, site-grain re-agg, dim Excel build.

**Build artifacts (outside brain):** `bi-analytics-main/NFE/shipping_topics/44_transit_time_sla/` — `build_dim_carrier_sla.py`, `outputs/dim_carrier_sla_v1.xlsx`, `data/*` (per-shipment v2 + evidence tables), `sql/*`.

**BUG caught+fixed in build:** undelivered shipments store `transit_bd` = **NaN** (not null); polars sorts NaN largest → quantile/coverage wrong + lanes >10% undelivered blanked. Fix: NaN→null before all stats. (Same NaN-vs-null family as S124.)

**Headline selected SLAs (standard BD, ceil pooled-p90):** US CMH zones 1/2/3/4 = 3/4/5/9; DE 4, NL 4, AT 4, BE 4, UK 5*, IT 6, ES 6, FR 6*, SE 8*, CA 11, AU 13* (* = low delivered-cov, directional). Switzerland PL standard = BLANK (0% delivered). DB Schenker oversized 7-19.

**Open judgement points (for Niklavs):** (1) Switzerland blank — leave/impute; (2) low-cov directional lanes; (3) PCS PL→US zone-split noisy on 682 ships — maybe collapse to one row.

**Next after review:** apply judgement edits → this Excel = the dummy/structure list for BI (mid-next-week commitment) → later seeds the mart `dim_carrier_sla`.

---
PRIOR STATE (plan lock):

**Quest:** [[S145_7ac0cf07_transit-time-sla-build]] (extends [[S124_fd13a7a7_carrier-proxy-sla-2026q1|S124]]).

## Next concrete step
Spawn shipping-agent (read-only, gold contract, NO raw) for the grounding pass — confirm before any number:
1. Timestamps present in gold mart + coverage each: production / truck-closed? / carrier_received / delivered.
2. US state/ZIP destination field.
3. The TCG `source_system` set (don't hardcode — agent resolves from contract).
4. Decimal-business-days-from-timestamps as the basis (NOT the mart's rounded BD field).

## Build checklist (after grounding)
- [ ] Grounding pass (shipping-agent) — schema/coverage/TCG-set/state-field
- [ ] Scaffold `NFE/shipping_topics/NN_transit_time_sla/` (port S124 cohort+transit logic)
- [ ] Cohort: All TCG, rolling ~3mo, delivered, is_returned=false, settle-tail excluded
- [ ] Per extkey×country: p90 BD transit (carrier_received→delivered, computed) + volume share + coverage
- [ ] Collapse → 1 SLA/country/bracket (standard = ex-DBSchenker; oversized = DB Schenker), volume-weighted JUDGEMENT
- [ ] Full lead time per extkey×country (mart timestamps only, coverage per dimension) → line-haul flag
- [ ] US: shipping-agent state-cluster investigation → 3–4 clusters (final cut ours)
- [ ] Evidence sheet + dummy/structure list for BI (mid next week commitment)
- [ ] (LAST) propose `dim_carrier_sla` mart table shape

## Locked decisions (FINAL — all confirmed 2026-06-02)
- **Metric:** p90 decimal **business days**, computed from `received_by_carrier_ts` → `delivered_by_carrier_ts`. AVOID mart's `transit_time_business_days` (int, rounded, drops ship day) + `transit_time_days` (calendar).
- **Vertical:** TCG = `source_system IN ('Picturator','PicaAPI')` (excl PCS, Rewallution, ORWO).
- **Returns:** `COALESCE(is_returned,false)=false` (keep ~12% NULLs; drop only confirmed returns).
- **Window:** ship-anchored (`received_by_carrier_date`) `>= 2026-03-01` AND `< today-14d` (~2026-05-19) — excludes still-undelivered recent tail. ≈660K cohort.
- **Brackets:** standard = `shipping_provider_group <> 'DB SCHENKER'`; oversized = `= 'DB SCHENKER'`.
- **Grain:** per `shippingprovider_extkey` × `destination_country`; collapse to 1 SLA/country/bracket by volume-weighted JUDGEMENT (evidence prepared, call is ours). Refines meeting's "take longer" — tell Andrea (he).
- **Coverage:** exclude **DPD UK only** (0% delivered, structural); all others computed on available, coverage shown beside each SLA. Tier for judgement: >96% rank-freely / 80–89% directional.
- **Full lead time / line-haul:** decompose `produced → truck_departure → carrier_received → delivered` using `fact_truck_charges.departure_ts` JOIN on `truckload_id`. Segments: produced→departure (our-side), departure→received (TRUE line-haul), received→delivered (headline transit). Coverage noted per dimension (truck scans ~80-90% per meeting — VERIFY). Mart-only, no raw.
- **US:** zone clusters from `shipping_zipcode` (100%, 906 zip3) + US-slice state names (`shipping_region`, 99.9% clean for US); shipping-agent proposes 3–4 clusters, final cut ours. US carriers: OnTrac/USPS/FedEx.
- **End-state:** `dim_carrier_sla` — LOCKED design (2026-06-02). Excel deliverable first → seeds the mart dim. Columns: `production_site`, `destination_country`, `shippingprovider_extkey`, `sla_business_days`, `valid_from`, `valid_to`. Grain = site × country × extkey (extkeys mostly belong to one site). SCD via valid_from/valid_to (`valid_from=2026-07-01`, `valid_to`=NULL/open). **Imputation:** per (site, country) one standard `sla_business_days` written across all non-DB-Schenker extkeys; DB Schenker rows get the oversized value. `sla_business_days = ceil(p90)` (generous round-up); decimal p90/p95 kept in evidence. US needs a zone/region column (TBD after clustering — dim_country='US' splits into 3-4 zone rows). This dim is OPERATIONAL (join shipments to measure); customer-facing per-country number is a rollup on top.
- **Idle/lead-time (REVISED 2026-06-02):** `departure_ts` is a modeled same-day stamp (logged to shipping-agent known-dq.md) — line-haul split DEAD in gold. 2-segment model: idle = `order_produced_ts → received_by_carrier_ts` (our-side+injection combined); transit = `received_by_carrier_ts → delivered_by_carrier_ts` (headline SLA basis).

## Grounding done (shipping-agent, sid ad0463d9 trace = quest-log/in-progress/S145_7ac0cf07_transit-sla-grounding.md)
All components verdicted READY on gold. Carrier volumes (Mar–May TCG): DHL 271K, UPS 133K, Maersk 84K, OnTrac 73K, DPD-PL 65K, USPS 51K, DPD-UK 26K, FedEx 20K, Asendia 10K, Yodel 7K, DB Schenker 6.7K, Direct Link 4.3K. Delivered coverage: DHL/OnTrac/Yodel ~98%, Maersk 79.8%, DPD-UK 0%.
OUTSTANDING VERIFY: `fact_truck_charges` join + `departure_ts` coverage in cohort (agent missed the column first pass — Niklavs supplied it).
