# S244 (bb5d1f1a) — NA shipping-quota: Torsten follow-ups + revenue-denominator correction

Continuation of the topic-46 NA May-2026 quota work ([[S204_e9dbce2d_na-may-quota-breakdown|S204]]), driven this session by Torsten Harnau's P&L-review pushback (the review was today, 2026-06-15). Started by answering his cost-side challenges; ended by correcting a load-bearing denominator error and rebuilding the bridge on the mart's own revenue.

## What happened (arc)

1. **Torsten's cost-side challenges** — beyond the channel-mix story, he asked for: (a) the new USPS rate card from April, (b) confirmation of the Columbus OnTrac/USPS→FedEx reroute (€48k/+2.2pt Apr, €22k/+1.0pt May), (c) the fuel-surcharge effect per month YoY. Spawned the shipping-agent: NA May cost €599.3k / €10.35 per parcel (ties to topic 46). USPS per-parcel €6.14 (Jan–Mar) → €6.52 (Apr) → €7.19 (May); Columbus reroute confirmed (€51.5k Apr / €23.4k May net); fuel flat at the blend.

2. **Rate-vs-mix probes** — principal pushed on the +17% USPS jump and on whether fuel rose per-carrier. Shipping-agent: USPS rise is ~100% rate (weight-controlled, every band up), but gold can't split USPS *service* level. Per-carrier fuel IS up YoY (FedEx +91%, Asendia +250%) — masked at the blend by the OnTrac/USPS mix. Corrected my earlier "fuel flat" to "mix offset real per-carrier fuel rises."

3. **USPS matched-cohort (upstream)** — went off-contract to `enterprise_silver.usps_invoices`: 100% Ground Advantage (no service mix), same weight×zone rate rose ~11–14% — genuine rate move, ~85% rate / ~15% mix.

4. **USPS fuel surcharge discovered** — principal found a Copilot result; penguin verified against USPS Newsroom (2026-03-25): **first-ever USPS fuel surcharge, flat 8% on base postage, effective Apr 26 2026 → Jan 17 2027, includes Ground Advantage, applies to commercial rates.** It folds into the base bucket in our data (no separate USPS fuel line) — which is why earlier cuts said "USPS carries no fuel." Explains the Apr→May step exactly (started Apr 26).

5. **THE CORRECTION (Q5)** — building the Q1→May bridge, I used **`dw.sales_fact`** for revenue, inherited from topic-46's `decompose_quota.py`. Principal caught it: **revenue is in the shipping_mart.** Recomputed on `fact_shipments.net_revenue_eur`, order-month lens → **reproduces SCM's US May 26.5% exactly (26.52%).** Every prior quota % and the mix bridge had the wrong denominator. Cost-side euros unaffected (always mart cost).

6. **Final per-month NA bridge** (principal: complete NA, isolate country mix). Two bridges below.

## Corrected numbers (mart revenue, order-month lens, final cost)

| Period | US | NA (US+CA) |
|---|---|---|
| Q1-2026 avg | 24.50% | 25.49% |
| April 2026 | — | 28.33% (worst) |
| May 2026 | 26.51% | 27.14% |

CA runs far hotter than US (Q1 ~34% / Apr ~40% / May ~34%) — country mix is a real lever but netted near-zero both months (CA's revenue share fell).

**NA per-month bridge vs Q1 (each component: total cost € / quota pp):**
- April (+2.85pp): channel mix +€32.4k/+1.52; country −€2.8k/−0.13; within-cost +€36.3k/+1.70 (USPS +€9.7k/+0.46, Columbus gross +€63.1k/+2.95, cheaper-carrier −€36.0k/−1.68, other-carrier −€13.5k/−0.63); within-revenue −€5.1k/−0.24. **Cost-led (big reroute), surcharge near-zero.**
- May (+1.66pp): channel mix +€44.0k/+2.03; country −€2.7k/−0.13; within-cost +€36.7k/+1.70 (USPS +€18.7k/+0.87, Columbus gross +€50.6k/+2.34, cheaper-carrier −€26.0k/−1.20, other-carrier −€21.5k/−0.99); within-revenue −€42.1k/−1.95. **Channel mix (+2.03) nearly cancelled by within-cell revenue/AOV (−1.95) → net rise is within-cost-led.**

Both tie out to residual 0.000pp. Columbus net-of-FedEx-base-cuts = €42.4k Apr / €22.3k May (the €22.3k ≈ the €23.4k / ~$26k Torsten has been using).

## Key decisions / corrections

- **Denominator = mart `net_revenue_eur`, NOT `dw.sales_fact`** (principal-corrected). Reproduces SCM. Caveat: for B2C this revenue includes customer-paid shipping — it's the dashboard's quota basis (correct for "quota") but not a pure-product number.
- **Lens = order-month** (reproduces SCM; ship-month/production-month gave 27.2/27.4 and are wrong for this).
- **My earlier "it's all channel mix, cost favorable" was wrong** on two counts: wrong denominator, and the framing lumped within-cost (a real +1.70pp push) with within-revenue. On the corrected basis cost is a genuine driver.

## Decisions log

- Ran close principal-self despite >15-turn gnome heuristic — single-player, and the Q5 correction harvest needed my context.
