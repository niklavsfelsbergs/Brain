# Checking for a rate change (GRI): verify the all-in per-unit cost over time, not just the base rate

**Observed:** 2026-06-25, [[S367_ae7565da_orwo-methodology-walkthrough|S367]] (ae7565da) — Niklavs asked whether DHL/UPS already took a GRI in 2026.

## What happened

I first checked only the **base freight rate** per band by month, saw it flat, and answered "no GRI." Niklavs pushed back: *"really no GRI in march for DHL?"* — which was right to do, because a rate change frequently does **not** live in the base rate:

- It can hide in the **surcharge layer** (Maut/CO2, energy, peak) — separate prod codes I hadn't summed.
- It can appear as a **new parallel product stream** (DHL `2511`/`2681`/`101510315` showed up in March — but turned out to be a separate ~4.4k/mo flow, not a hike on the existing book).
- A "per-order cost rose in March" signal is often **volume / mix / returns**, not a rate hike (here: the real March event was a DHL *returns* surge, separate thread).

When I re-checked at the **all-in net per parcel** (freight + every surcharge line, fixed product), the answer held — flat / falling into March as Q4 peak unwound — but only the all-in view could actually *prove* it. The base-rate check was necessary but not sufficient.

## How to apply

For any "did the price change?" question, the unit of analysis is the **all-in cost per fixed unit over time**, not the base rate. Steps: (1) hold the product/band constant; (2) sum *all* charge lines per unit (base + every surcharge), not just the freight line; (3) scan for new/parallel codes appearing at the suspected month; (4) before calling a per-order rise a "rate increase," rule out volume/mix/returns. A flat base rate does not prove a flat effective price.

Related: [[2026-06-22-name-the-incumbent-a-switch-exits]]; MEMORY *explain-output-from-data-not-code*, *immature-month-cost-is-estimate-dominated*.
