---
quest: S204_na-may-quota-breakdown
sid8: e9dbce2d
ts: 2026-06-11 15:05
open_dep: bi-analytics topic-46 commit cue + optional finance-formula reconciliation
---

# Resume — NA May-2026 shipping-quota breakdown (P&L review Mon 2026-06-15)

## Status

in-progress (deliverable shipped; open deps only)

## Where we are

Analysis complete, finance message delivered to Niklavs in chat (full text preserved in the quest log). Verdict: mix-driven (API revenue share 12%→34% YoY = net +3.1pp; cost/parcel −10.8% YoY, no surcharge story); the one real cost event is the Columbus OnTrac/USPS→FedEx rerouting (Apr ≈ €48k/+2.2pt, May ≈ €22k/+1.0pt, fading). PRINCIPAL CORRECTION applied: we PAY shipping on API orders — `shipping_amount_eur` is NOT recharge income; the "optical/break-even" framing was struck; the mix effect is a real P&L effect, lever is commercial (API shipping pricing/terms).

## Next concrete step

Blocked on Niklavs: (1) commit cue for `NFE/shipping_topics/46_na_market_quota_may_2026/` in bi-analytics (uncommitted there); (2) if finance's quota number diverges from ours (26.1% May / cost÷net-product-revenue), get their exact formula and re-run `decompose_quota.py` on that basis — direction holds, magnitudes shift; (3) known-dq.md edit for Oct-2025 PicaAPI expected-cost garbage; (4) pin the true meaning of `shipping_amount_eur` on PicaAPI orders before anyone reuses it.

## Files / paths to read first

- `bi-analytics-main/NFE/shipping_topics/46_na_market_quota_may_2026/findings.md` (final, correction marked)
- `.../data/quota_decomposition.parquet`, `monthly_by_{channel,bucket,carrier}.parquet`
- Quest log `S204_e9dbce2d_na-may-quota-breakdown.md` (incl. the delivered message verbatim)

## Pending drafts

None beyond the close harvest (surfaced at close).
