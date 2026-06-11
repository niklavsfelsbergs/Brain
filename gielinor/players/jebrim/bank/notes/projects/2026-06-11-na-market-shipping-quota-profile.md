# NA market shipping profile — carriers, channels, quota mechanics

**As of:** 2026-06-11 ([[S204_e9dbce2d_na-may-quota-breakdown|S204]]/e9dbce2d, NA May-2026 quota breakdown). Source: `bi-analytics-main/NFE/shipping_topics/46_na_market_quota_may_2026/` (findings.md + parquets; dw.sales_fact order lens + shipping_mart ship-month lens).

- **NA = destination US (~94%) + CA (~6%).** MX/PR negligible. Channels via `dim_shops.shoptype`: D2C (Core Business), Reseller (API) = `PicaAPI`, minor B2B/Marketplace.
- **Carrier timeline:** until mid-2025 FedEx-dominated (May-25: 81% @ €12.10/ship) + Asendia USA + DHL eCommerce. OnTrac entered Jul-2025, USPS Jul/Aug-2025, DHL exited ~Sep-2025. May-26 mix: OnTrac 50% @ €9.36, USPS 31% @ €7.19, FedEx 13% @ €17.22, Asendia 5% @ €21.08. This mix shift is why NA cost/parcel fell −10.8% YoY on +10.7% volume.
- **Channel economics:** API orders ≈ €31 net product revenue vs D2C ≈ €48, at similar shipping cost → API channel shipping quota ~34–36% vs D2C ~22–24%. API revenue share 12% (May-25) → 34% (May-26): blended-quota mix effect ≈ +3.1pp YoY. **We pay the shipping on API orders** (principal-confirmed 2026-06-11); `sales_fact.shipping_amount_eur` on PicaAPI orders is NOT recharge income — exact meaning unverified, don't reuse without pinning it.
- **Apr/May-2026 cost event:** CMH OnTrac/USPS→FedEx HD diversion (~€11/parcel penalty): Apr ≈ €48k/+2.2 quota pts, May ≈ €22k/+1.0pt, fading. Detail: topic 41 + topic 46 `cmh_ontrac_fedex.parquet`.
- **DQ:** Oct-2025 PicaAPI expected costs near-zero garbage (5,099 NA ships → €96); Sep–Nov-2025 buckets noisy from OnTrac credit notes (−€97k Oct). USPS cost coverage ~100% from entry — YoY comparisons not coverage-biased.
- **Method pointer:** Bennet/midpoint quota decomposition (mix + within-channel cost/revenue split) in `decompose_quota.py` — reusable for any cost-ratio driver breakdown.
