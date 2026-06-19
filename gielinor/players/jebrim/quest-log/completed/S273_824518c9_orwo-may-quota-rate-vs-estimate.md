# S273 — ORWO May-vs-April cost-quota rise: rate vs estimate

**Player:** Jebrim · **sid8:** 824518c9 · **Status:** completed (root cause identified; already documented in a sibling session)

## Ask

Niklavs: why did source **ORWO**'s cost quota rise in May 2026 vs April?

## What happened

Spawned the shipping-agent for a May-vs-April quota bridge (quota = `final_shipping_cost_eur ÷ net_revenue_eur`, order-month lens). It returned: quota +1.03pp (15.54% → 16.57%), entirely cost-side, and attributed the cost rise to a **DHL "base-rate increase"** (base bucket €0.749 → €0.878/ship).

Niklavs pushed back on the base-rate claim. Verified it against **raw `enterprise_silver.dhl_orwo_invoices`** (off-contract; ran it myself — shipping-agent is `ship_mart_ro`, DB-denied on silver):

- **No rate increase.** Like-for-like by billed weight band (`wgt_abr`), DE domestic, pickup-month: bands 1–5 (>93% of volume) **flat to the cent** April→May (€3.02 / €3.35). Raw per-parcel base actually flat-to-down (€3.35 → €3.30) despite heavier parcels. Only the thin >5kg tail (≤2% vol) ticked €0.05–0.40, and that's April-blend-converging-to-a-clean-rate, not a card change.
- The agent's "base-rate-led" read was a **mart-bucket artifact** on a partially-invoiced order-month.

Decomposed the mart's +€47.8k cost rise by `cost_source`:

- **`expected` (estimate) bucket = +€33.9k (71%)** — count of uninvoiced ORWO shipments nearly doubled (26.9k → 49.9k); those are priced at €2.2–2.8/ship, ~2.5× ORWO's actual invoiced ~€1. The estimate, not real cost.
- **`invoice` (real) = +€13.9k (29%)** — and even the reliable DHL slice (98% invoiced, +€11.4k, €0.86 → €0.95/ship) is allocation/mix in immature May data, not rate (raw card flat). UPS invoiced per-ship €1.15 → €2.78 is a coverage-selection artifact (May UPS only 38% invoiced).

## Resolution

Niklavs: the rise is **overstated UPS `expected` cost from the distribution of cost for bulky orders** — and a **sibling session already found this**. My decomposition converges on it: the estimate bucket is the dominant driver, and UPS (ORWO's bulky/oversize carrier) is where the estimate runs hottest. No real per-parcel price increase anywhere; the May quota will deflate toward ~15–15.5% as invoices mature. Invoiced-only quota was +0.55pp (12.7% → 13.3%), and even that is mix, not rate.

Nothing new persisted — finding already lives elsewhere.

## Decisions

- The defensible answer: **no rate increase; ~70% estimation artifact (UPS bulky-order expected-cost distribution), ~30% allocation/mix.**
- Open upstream question (not pursued, sibling session owns it): why the `expected` model overstates ORWO at ~€2.5/ship vs ~€1 actual.

## Pending external actions

None pending.

## Cascade.

None — read-only investigation; no mart/SCM/repo changes.

## Main-brain changes.

One examine draft harvested (`examine/drafts/2026-06-19-immature-month-mart-cost-is-estimate-dominated.md`). No confirmed/identity writes.

## Trace

- Sub-agent: `quest-log/archive/traces/S_shipagent_orwo-may-vs-apr-quota-bridge.md`
