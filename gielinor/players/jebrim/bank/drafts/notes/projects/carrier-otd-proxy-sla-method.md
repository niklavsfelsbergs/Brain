# Carrier on-time-delivery proxy-SLA method

**Source:** [[S124_fd13a7a7_carrier-proxy-sla-2026q1|S124]] (2026-05-29). Need: track carrier OTD rates with no contractual transit SLAs on hand.

## The method
When no carrier transit SLA exists, derive a **proxy SLA** from our own observed transit distribution and freeze it:

- Per segment, threshold = the transit value capturing **p90** of delivered shipments (i.e. `numpy.percentile(transit, 90)`), computed over a clean settled window. That frozen number *is* the SLA.
- Then `OTD(segment, period) = % of delivered shipments with transit ≤ frozen threshold`. Value is in tracking drift against the frozen line + comparing carriers on the same lane — not the baseline % (which is ~90 by construction).

## Grain that's load-bearing
Carrier × **service** × **destination_country**. Both axes matter:
- **Service** = `shippingprovider_extkey` (NOT `shipping_provider_group`, which is carrier-only). extkey encodes the product: UPS `UPS04STD` ≈ 3 BD vs `UPSWWECON` ≈ 12–16 BD — collapsing them is meaningless.
- **Country**: same `UPS04STD` is p90 ≈ 3 BD to DE/AT/NL but 5–6 BD to IT/ES/GB.

## Mart facts (`shipping_mart.fact_shipments`, gold)
- Transit clock already on the fact: `received_by_carrier_ts/date` → `delivered_by_carrier_ts/date`, pre-computed into `transit_time_days` (numeric) and `transit_time_business_days` (**integer** — coarse; recompute decimal if precision wanted).
- **Decimal business days** = `numpy.busday_count(handover_date, delivery_date)` + intra-day `(delivery_tod − handover_tod)/24h`, clamp ≥ 0.
- Production time = `order_produced_ts − production_order_created_ts` (≈3.2 calendar days; ~98.6% populated). Order→produced ≈3.7 d; produced→handover ≈1.2 d.
- Delivery coverage 90–99% on **settled** months; recent months dip from censoring (in-transit) → baseline off a window lagged ~30–45 d.
- `is_returned` flag to exclude returns.

## Caveats
- Denominator = **delivered only** → this is a transit-distribution baseline, **not a true OTD%-with-misses**. A lane that strands parcels still looks fast. True OTD% needs the full received-cohort denominator (count never-delivered as misses) + a chosen target threshold.
- MCP read-only validator rejects `percentile_cont`/`median`/`datediff` — compute percentiles via the shipping-agent harness (direct psycopg) or a cumulative-band SQL trick (`sum() over` + min-band where cum_share ≥ 0.9).

Routing/connection per [[keepsake]] mart pin. Deliverable shape: Excel in the shipping-agent workbench, not the brain.
