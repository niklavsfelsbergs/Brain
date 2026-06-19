# Shipping-agent trace — non-ORWO non-UPS May 2026 real-vs-expected residual

**Spawned by:** Jebrim (continuation of the non-ORWO expected-understatement arc; sibling to `S277_shipagent_non-orwo-expected-understatement.md`)
**Date:** 2026-06-19
**Tier:** gold-contract (`shipping_mart` only, `ship_mart_ro` via Redshift MCP)
**Ask:** Even with UPS removed there's still a mismatch — investigate. Scope MAY 2026, order-month lens, non-ORWO, exclude UPS. Like-for-like residual on `cost_source='invoice'` rows where `expected_shipping_cost_eur` populated.

## Scope/assumptions
- Population: `source_system <> 'ORWO'` (= Picturator + PicaAPI + PCS); UPS excluded via `UPPER(shipping_provider_group) <> 'UPS'`.
- Lens: `shop_order_created_date` in [2026-05-01, 2026-06-01).
- Like-for-like residual = `real_shipping_cost_eur − expected_shipping_cost_eur` on the SAME invoiced rows (maturity-free).
- Non-UPS May population is ~89.7% invoiced euro-weighted (90.5% rowcount) — mature, no coverage artifact.

## Headline
- Total non-ORWO May residual = €125,422 (UPS €52,364 @1.119× + non-UPS €73,059 @1.057×).
- **Non-UPS = €73,059 = 58.2% of the full non-ORWO May residual.** (UPS = 42% — matches the prior arc's framing.)

## Carrier ranking (non-UPS residual €)
DPD UK €23,709 (1.46×) | OnTrac €14,091 (1.055×) | DPD Poland €8,648 (1.099×) | DHL €8,284 (1.023×) | USPS €8,040 (1.070×) | Asendia USA €4,912 (1.088×) | Maersk €2,751 | DB Schenker €1,211 | FedEx €971 | rest <€300.

## Oversize-vs-other verdict
- has_oversize: €28,683 residual (39%), 7,213 rows (3.1%), 1.223×.
- no_oversize: €44,376 residual (61%), 226,661 rows, 1.039×.
- **Unlike UPS (oversize-dominated), the non-UPS residual is MAJORITY non-oversize (61%)** — a broad ~4% surcharge-driven drift. Oversize tail is real but the minority.
- no-oversize residual rides on surcharge layers the flat per-country scalar can't see: fuel €76.7k, unclassified €66.2k (mostly DB Schenker), truck €72.9k, other €31.3k, residential €19.3k, remote area €18.0k (real-side totals).

## Structural vs dispersion
- **All non-UPS misses are dispersion, not structural.** Every top carrier has a populated rate card (rows with expected≈0 ≈ 0). DB Schenker only 34/1,143 zero-expected; residual €1.2k — its unclassified block is NOT a driver (corrects the prior April DB-Schenker suspicion).
- DPD UK is the standout: even non-oversize DPD UK runs 1.40× (€16.0k), oversize 1.68× (€7.8k) — broad base-rate under-pricing of the UK lane, not just oversize.

## Checks
- Sum-invariance: 11 buckets == total_eur == real = €1,353,154.68 to the cent (COALESCE on credit_note — NULL propagation otherwise). Attribution complete.
- % invoiced reported (89.7% euro-weighted) — rules out coverage artifact; like-for-like is maturity-free regardless.

## Open / gaps
- April suspects (Asendia USA fuel, DPD Poland) confirmed present but small in May; DB Schenker corrected (not a driver).
- Rulebook: no gap surfaced. Estimate model is dimension-/surcharge-blind by construction (flat per-country scalar) — known.

Deliverable: chat-only to Jebrim.
