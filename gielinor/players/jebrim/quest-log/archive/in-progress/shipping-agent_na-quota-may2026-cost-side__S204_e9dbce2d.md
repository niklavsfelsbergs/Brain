# S204 (shipping-agent emulation) — NA market quota May-2026, cost side

> Sub-agent trace; SNNN provisional — renumber if the principal session claimed S204.
> Spawned by Jebrim principal session, 2026-06-11. Brief: cost side + scope profiling of the
> finance-reported high May-2026 NA shipping quota (TCG only, dest US/CA/MX, 2025-01..2026-05, ship-date basis).

## Scope used
- TCG = Picturator + PicaAPI; NA pinned to US+CA (MX = 40 ships once, PR = 2 — trace).
- Ship-month = COALESCE(received_by_carrier_date, order_produced_date, shop_order_created_date)
  — PicaAPI handover ingestion only landed 2025-11, pure ship-date would erase its 2025 baseline.
- Tier: gold contract only (shipping_mart.*, via Redshift MCP). CLAUDE.local.md present but upstream not needed.

## Turn log
- Country profile + date-coverage probe: NA = US+CA; PicaAPI pre-Nov-2025 100% NULL on handover → fallback chosen.
- Channel pull: May-2026 = 58,014 ships / €599,835 final cost / 97.2% invoiced euro-weighted.
- Bucket pull (invoiced): May vs Apr — base −28.2k, discounts +21.6k (net base −6.6k), fuel −3.0k. No surcharge story.
- Carrier pull: landscape flipped H2-2025 FedEx(81%)→OnTrac+USPS(81%); YoY per-ship −11% is mix.
- CMH probe: FedEx HD 3,639(Feb)/3,491(Mar)/7,794(Apr)/5,557(May) — diversion persists May at ~half April strength, ≈ €20k excess in May vs ≈ €45k April.
- Revenue verdict: gold HAS revenue (fact_shipments.net_revenue_eur, orderitems.revenue_eur) → revenue parquet produced.
- Reconciliation: channel = carrier = bucket totals (asserted in build script, passed).

## Headline
May-2026 NA TCG: €599,835 total (final basis), €10.35/ship; MoM total −0.1%, YoY −1.2% on +10.7% volume.
Cost is NOT the quota driver — revenue mix is (Reseller API rev share 13.2%→35.6% YoY, quota 33.5% vs own-shops 25.1%, ≈ +1.9pt mix effect on blended quota).

## DQ flags
- Oct-2025 PicaAPI expected-cost artifact: 5,099 ships @ ~€0.02 estimates (€96 total) — month unusable as baseline.
- Sep–Nov 2025 credit-note negatives = OnTrac credits (known refund channel).
- Bucket base/discounts swing on FedEx gross-accounting vs OnTrac/USPS net — always net them across the mix flip.

## Deliverables (outside brain)
- C:\Users\niklavs.felsbergs\Documents\GitHub\bi-analytics-main\NFE\shipping_topics\46_na_market_quota_may_2026\
  - data\*.parquet (7 files), sql\2026-06-11_na_quota_cost_side_pulls.sql, build_data.py
  - findings.md NOT written — harness blocks sub-agent report files; content returned in final message to principal.
