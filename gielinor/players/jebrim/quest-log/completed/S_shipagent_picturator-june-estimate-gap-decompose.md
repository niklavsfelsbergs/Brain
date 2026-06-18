# Picturator June 2026 — estimate-gap decomposition (sibling to quota-maturity investigation)

**Spawned by:** Jebrim (principal), shipping-agent emulation
**Tier:** gold-contract (`shipping_mart` only; no CLAUDE.local.md → gold perimeter absolute)
**Scope:** Picturator (`source_system = 'Picturator'`), order-month (`shop_order_created_date`), June 2026 partial through 06-17
**Sibling:** `S_shipagent_picturator-june-quota-maturity.md` (parent investigation)

## Ask
Pinpoint WHICH expected/estimate costs drag the June quota down. Decompose by cost-source tier, then by carrier (estimate vs same carrier's matured invoiced), flag worst offenders + missing-fallback lanes, attribute the ~2.9pp quota gap by carrier.

## Status trace
- Tier split done: June Picturator = 75.5% expected / 22.2% invoice / 2.2% null / 0.06% avg. Expected per-parcel €5.96, early-invoiced €5.20 (cheap biased sample), avg €11.25 (tiny).
- Per-carrier estimate-vs-matured gaps mostly SMALL: UPS €2.00, DPD-PL €0.39, DHL €0.02, several NEGATIVE (Maersk -0.52, FedEx -2.79, OnTrac -0.29). Per-carrier under-fill sums ~€39k, not enough for 2.9pp.
- **Re-cost each non-invoiced parcel at its OWN carrier's mature rate → quota only 16.54% (net) / ~18.5% (floored-at-zero).** The prior trace's flat €6.69 benchmark → 19% DOUBLE-COUNTS the carrier-mix effect.
- **Real mechanism = invoice-timing-driven carrier-mix bias, not uniform under-estimation.** June invoiced set is 92.6% DHL (cheapest, €3.35); UPS only 7.4% invoiced vs 27.3% of all; Maersk 0% invoiced vs 22.6% of all. DHL bills fast, UPS/Maersk bill slow.
- **UPS is the single dominant under-filler:** estimate €6.72 vs May-invoiced €9.28 / Jan-Apr mature €8.59 → €1.87-2.56 low. €44k under-fill / 1.11pp. Nearly half the gap.
- DHL/Maersk/DPD-PL/OnTrac estimates accurate (±€0.50). `OTHER`+`(NONE)` = 6,842 parcels (~6%) cheap (€2.83/€3.36) with NO mature benchmark — minor fallback hole.

## Verdict
Concentrated, NOT uniform. The estimate model is broadly fine carrier-by-carrier EXCEPT **UPS** (structurally ~25% low) and a small no-benchmark cheap bucket. The headline 16.06% is depressed by two compounding maturation effects: (1) UPS's estimate under-prices its actuals; (2) the early-invoiced sample is almost pure cheap-DHL because DHL bills fast and UPS/Maersk bill slow. Both self-correct as UPS/Maersk invoices land. Honest implied-mature quota ~17.5-18.5% (UPS-driven), narrower than the prior trace's 19%.

## Checks
- Tier shares reconcile to 100%, cost shares sum to 100%.
- Maersk surge verified real (Maersk-branded UK/FR/SE last-mile, 99.9% expected, not a relabel).
- Maturation proxy via May order-month: UPS May-invoiced €9.28 > Jan-Apr €8.59 → early sample biased cheap, confirmed.
- Invoiced-mix vs all-mix per month: DHL 92.6% of June invoiced vs 50.1% all → invoice-timing bias is the driver. Decisive.
- Net vs floored re-cost reconciled — explained the prior-trace 19% overstatement (flat benchmark double-counts mix).

## Deliverable
Chat-only findings + SQL returned to principal. No chart requested.
