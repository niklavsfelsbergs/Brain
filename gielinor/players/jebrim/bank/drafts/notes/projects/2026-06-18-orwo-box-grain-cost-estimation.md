# ORWO cost build + the box-grain quota-estimation fix

Draft (2026-06-18, [[S266_e455d12d_orwo-box-grain-quota-estimator|S266]]). Durable mechanism + design. Anchors: [[S266_e455d12d_orwo-box-grain-quota-estimator]],
bi-etl `dags/shipping_mart/`, NFE `shipping_topics/50_orwo_box_grain_quota_estimation`.

## How ORWO shipping cost is built in the mart
- ORWO ships **bulk-mail manifests**: many parcels in one DHL/UPS box, **one carrier charge**. ~20.7%
  of ORWO trackings are these.
- **Real cost** (`fact_shipment_invoice_lines/sql/providers/{ups,dhl}_orwo.sql`, NGE-6129 Step 5): one
  invoice line → matched to parcels via `map_shipment_key`, `DENSE_RANK` by ORWO `sentat DESC`, keep
  parcels tied at latest sentat = `share_n`, split charge equally `charge/share_n`. Total conserved.
- **Expected** (`fact_shipment_cost_summary/sql/update_fact_shipments_cost.sql`): Pass 2a.5 flat
  per-country rate (UPS DE €6.15, DHL DE €3.21) + seasonal lift; Pass 2a.6 dynamic calibration
  `AVG(real)/AVG(expected)` per (keyaccount, carrier). **A flat per-parcel scalar — consolidation-blind.**

## Why the SCM ORWO quota over-reads in immature months
1. **Per-parcel cost = box-charge ÷ parcels-in-box** → ranges 10× (solo ~€5.7, 6+ bulk ~€0.58).
2. **Bulk-mail manifests bill on a LAG.** In an immature month the invoiced data is only the
   low-consolidation **solo** parcels (expensive, real, locked); the cheap bulk sits in `expected`.
3. The flat estimate **over-prices the un-invoiced bulk** (€1.24 vs true ~€0.6).
4. Net: Final quota (all cost ÷ all rev) over-reads; the Invoiced quota (billed ÷ billed-rev) is the
   honest floor. The Invoiced/Final KPI split on SCM is exactly this gap.
- **The over-read is NOT a grain problem.** Aggregate quota is grain-invariant (distribution conserves
  total). It's coverage immaturity + estimate bias. Revenue is complete at order time → no offset.

## The fix: box-grain estimate, then distribute
`expected_parcel_cost = box_rate(carrier, zone) ÷ parcels_in_box` — estimate the BOX (stable), divide
by observed parcels-per-box (= the consolidation adjustment, no tier table). Mirrors the real path;
conserves; keeps per-shipment grain; swaps to real seamlessly when the invoice lands.
- **Box rate is ~6× more stable than per-parcel** (~€5–8/box any size — bulk-mail = flat per manifest).
- **Residual lever = freshness**: box rate drifts ~30% month-to-month → calibrate from the most recent
  mature month, refresh each cycle. This is the dominant error source, not consolidation.
- **Caveats:** small boxes (2–3) bimodal/noisy (shared-tracking is a fuzzy box proxy for pairs) but
  low-volume; weight/dims/packagetype ~77% NULL for ORWO so no weight-aware estimate — box-size is it.
- Plus a **coverage-honest display** for the residual no estimate closes (band/gray immature months;
  Invoiced quota as primary recent signal). SCM already has a `real`-only basis + ORWO/TCG entity split.

**Why it matters:** lets the SCM Final-quota line track reality mid-month for ORWO instead of
overshooting (June 18.9% rests on ~22% real cost). The estimator change lives in
`update_fact_shipments_cost.sql` Pass 2a.5 (replace flat scalar with box_rate/box_n for ORWO).
