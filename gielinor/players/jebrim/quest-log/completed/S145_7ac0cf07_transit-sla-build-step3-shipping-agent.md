# Transit-time SLA build — step 3 (shipping-agent trace)

**Player:** Jebrim | **Session:** 7ac0cf07 | **Date:** 2026-06-02 | **Role:** shipping-agent (emulation) | **Status:** delivered

Sibling trace to [[S145_7ac0cf07_transit-time-sla-build|S145 build quest]]. Extends [[S124_fd13a7a7_carrier-proxy-sla-2026q1|S124]]. Design LOCKED; this run did two scoped tasks against the gold contract (read-only, no raw layer).

## Asked
(A) US zone clustering by p90 decimal-business-day transit; (B) re-aggregate the transit evidence with `production_site` added to the grain + lane rollup + idle segment.

## Cohort (locked, used exactly)
- Vertical `source_system IN ('Picturator','PicaAPI')`; window `received_by_carrier_date >= '2026-03-01' AND < (current_date - 14)`; `COALESCE(is_returned,false)=false`.
- Transit = decimal BD `received_by_carrier_ts → delivered_by_carrier_ts` (numpy busday_count + intra-day fraction, clamp >=0). DPD UK excluded from percentiles (not present in US slice anyway).
- Idle = decimal BD `order_produced_ts → received_by_carrier_ts` (LOCKED; departure_ts dropped — modeled stamp, clamps to ~0 per v1's own DQ verdict).
- Cohort row count **650,400 — exact match to prior run.**

## Turn log
- Confirmed live-mart fields: US dest = `'United States'`/`'US'` (127,682); state field `shipping_region` = clean full state names (58 distinct, 115 null = 0.09%, ~9 stray 2-letter codes normalized); `shipping_zipcode` 100% present, numeric-leading.
- production_site values in cohort: PCS PL 506,814 / PCS CMH 136,499 / Allcop 7,078 / Wolfen 3 / PCS PX 2 / PL 2 / OPT OnDemand 2. **No `'Other'` — the LIKE-map-miss DQ note does NOT bite this cohort (0%).**
- US carriers (all standard): OnTrac 63,730 / USPS 43,973 / FedEx 19,294 (FXEHD+FXESPPS+FXEINTECON) / UPS 685. FXESPPS delivered-cov only 54% — carried in per-carrier breakout.
- Built v2 SQL + build script; reran after recutting cluster bands to the actual p90 distribution (no state hits p90<=2 BD; fastest is Ohio 2.64).

## Headline results
**(A) US clusters (standard, p90 decimal BD, vol-weighted):**
- 1 fast/near — 2.87 BD — 23.3% (29,810): CT, DC, MD, MA, MI, NJ, NY, OH, PA, RI
- 2 mid — 3.78 BD — 38.8% (49,579): DE, FL, GA, IL, IN, KY, NC, NH, TN, TX, VA, WV, WI
- 3 far — 4.65 BD — 37.5% (47,901): West/Mountain/Plains/deep South (26 states incl CA 4.21, AZ 4.27, WA 5.30, OR 5.19)
- 4 remote/offshore — 7.96 BD — 0.3% (392): AK, HI, PR, VI
- Cluster p90 monotonic [2.87, 3.78, 4.65, 7.96]; volume reconciles to 127,682 exactly.
- **Finding for the meeting:** the hoped-for 1-2 BD "fast" bucket does NOT exist at p90 — fastest cluster is ~3 BD. Per-carrier: OnTrac/FedEx ~2 BD on near states, **USPS the laggard everywhere (~4-5 BD)** — clusters differ by carrier, USPS dispersion drives the country-level p90.

**(B) Site grain:**
- PCS CMH → US lane p90 = 4.11 BD (126,998); **PCS PL → US lane p90 = 15.23 BD** (682) — Poland-produced transatlantic US orders are a structurally separate, far slower lane. Adding production_site is exactly what separates them.
- PCS PL → Germany 3.15 BD (279k, 99% cov); PCS PL → UK 4.21 (65.9% cov); PCS CMH → Canada 10.26 (95%).
- Idle segment (produced→received): 98.9% coverage cohort-wide, median 0.35-1.0 BD on main lanes — our-side processing is fast, transit dominates. Allcop idle 0% cov (no order_produced_ts); PCS CMH→Canada idle=0 (same-stamp DQ quirk).

## Checks (all pass)
- Cohort 650,400 (target met). production_site 'Other' = 0%. Percentile monotonicity: 0 violations (B1 site×extkey, A state). Cluster p90 monotonic fast→remote. US volume reconciles. Idle coverage 98.9%.

## DQ caveats surfaced
- Per-shipment transit DQ caveat applies (aggregate trustworthy; individual timestamps can be flaky).
- `carrier_p90_spread` extreme on thin lanes (Spain 27.1, US-from-CMH 9.52) — lane p90 hides per-carrier dispersion; column flags it.
- PCS PL → Switzerland 0% delivered cov (6,542) auto-excluded from percentiles (NA), DPD-UK-style structural gap.
- US state field has 115 nulls + ~9 stray abbreviations (normalized for clustering).

## Artifacts (outside brain — NFE work folder)
- SQL: `bi-analytics-main/NFE/shipping_topics/44_transit_time_sla/sql/20260602-02_transit_sla_per_shipment_v2.sql`, `.../sql/build_transit_sla_v2.py`
- Data: `.../data/transit_sla_per_shipment_v2.parquet`; clustering CSVs (`us_clustering_per_state`, `_per_zip3`, `_candidate_clusters`, `_per_state_with_cluster`); site evidence (`evidence_transit_sla_by_site_extkey`, `evidence_idle_segment_by_site_extkey`, `evidence_lane_rollup_site_country_bracket`) — CSV + parquet each.

## Open / for principal
- Cluster bands are data-fit; final cut is human judgement (esp. whether to split cluster 3 West-coast vs Plains, and whether USPS lag warrants a carrier-aware SLA).
- The PCS PL → US 15-BD lane: confirm it's intended in the US customer-facing SLA, or whether US SLA should be PCS-CMH-only.
