# Dwarf trace — NA shipping-quota bridge Q1-2026 → May-2026 (for Torsten)

**Spawned:** 2026-06-15, Jebrim dwarf. **Source:** `bi-analytics-main/NFE/shipping_topics/46_na_market_quota_may_2026/`.
**Task:** decompose the +1.5pp NA quota change (Q1 avg 24.6% → May 26.1%) into all effects, in EUR + quota pp, defensible for finance.

## Reproduction (gate before trusting the rest) — PASSED

Quota = NA shipping cost ÷ NA net product revenue (order-date lens, `monthly_revenue_quota_by_channel.parquet`).
- Q1-2026 pooled (Σcost/Σrev) = **24.62%** (topic says 24.6 ✓)
- May-2026 = **26.15%** (topic says 26.1 ✓)
- ΔQ = **+1.53pp**

Monthly: Jan 24.93 / Feb 23.92 / Mar 24.94 / Apr 27.15 / May 26.15.

## Bennet (midpoint) channel decomposition — order-date lens

Ran the existing `decompose_quota.py` logic (it already carries a `q1_26 → may26` call); reproduced the channel split. Effects sum **exactly** to ΔQ (Bennet midpoint = no residual).

| channel | rev-share Q1→May | chan-quota Q1→May | mix pp | within pp | (cost/ord pp | rev/ord pp) |
|---|---|---|---|---|---|---|
| D2C | 82.6→65.5 | 22.4→23.2 | −3.91 | +0.56 | +0.51 | +0.05 |
| Reseller API | 16.4→33.7 | 35.2→31.8 | +5.81 | −0.85 | +1.19 | −2.03 |
| Other | 1.0→0.8 | 32.8→30.1 | −0.06 | −0.02 | +0.01 | −0.04 |
| **TOTAL** | | | **+1.83** | **−0.31** | **+1.71** | **−2.02** |

Net mix **+1.83pp**; within-channel **−0.31pp** (cost/order +1.71pp, rev/order −2.02pp). Sum +1.53pp ✓.
Matches findings.md (net mix +1.84, D2C cost +0.51, API within −0.85).

EUR-equivalents on May denominator (NA net product rev = €2,178,691):
mix +1.83pp = +€39.9k · within-cost +1.71pp = +€37.3k · within-rev −2.02pp = −€44.0k.

## Absolute-EUR cost sub-effects — SHIP-MONTH lens (`monthly_by_carrier`, `cmh_ontrac_fedex`)

NOTE basis difference: cost lens May = €599.8k vs order-date May = €569.7k (grain/month/scope, ~5%, per findings). These sub-effects reconcile *against* the +1.71pp within-channel cost piece — NOT additive on top of mix.

Carrier shift-share Q1/mo → May (ties out exactly): ΔCost +€63.1k = volume +€40.7k + carrier-mix +€33.5k + within-carrier rate −€11.1k.
Per-carrier mix (at May vol): FedEx +€70.7k (CMH reroute), OnTrac +€9.5k, USPS −€20.1k, Asendia −€20.6k, UPS −€6.0k.

- **CMH OnTrac/USPS→FedEx reroute:** CMH FedEx 3,650 (Feb–Mar base) → 7,310 May, excess 3,660 ships @ €17.22 vs OnTrac €9.36 = **+€28.8k** vs OnTrac counterfactual (+€32.1k vs ~€8.45 blend). Topic-46/41 headline ≈ €22–23.4k uses the net-of-base-cuts figure; range €23–29k depending on counterfactual. Brief's €23.4k sits at the low end (net of FedEx base-rate cuts + Ground-Economy parity).
- **USPS step:** rate-only **+€18.8k** (cpp €6.14→€7.19 × 17,912 May ships) — the €19k Torsten cited. USPS *total* spend only +€9.3k because USPS volume fell −1,534 ships (−€9.4k). The €19k = the per-parcel rate increase. Surcharge split (≈€9–10k 8% USPS fuel eff. Apr-26 + ~€5k base + ~€3–4k heavier/farther) is **externally confirmed (penguin), not reproducible from these parquets** — bucket data is NA-total, not USPS-specific.
- **Offsetting cheaper-carrier mix benefit:** USPS share 36.1→30.9 (−€20.1k mix) + Asendia 7.1→5.4 (−€20.6k) + UPS (−€6.0k) = **−€46.7k** the mix shift toward cheaper carriers SUBTRACTS — but it's swamped by the FedEx CMH reroute (+€70.7k). Net carrier-mix = +€33.5k.

## Verdict basis
Of +1.5pp: channel mix +1.83pp (= practically the whole rise + more); net within-channel −0.31pp (cost/order +1.71, rev/order −2.02 — the rev/order term is a measurement artifact of API rev/order being lower; the true structural within-cost is small/favorable). Torsten's CMH (€23–29k) + USPS (€19k rate) cost increases are real but partly offset by the −€47k cheaper-carrier mix; net carrier cost change is a small +€11–33k vs the €40k+ from pure volume — carrier unit costs are not the quota driver. Mix is.
