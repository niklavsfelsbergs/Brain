# On a partially-invoiced order-month, a mart cost-bucket move is estimate-dominated — split by cost_source before attributing it to rate

**Date:** 2026-06-19 · **sid8:** 824518c9 · **Quest:** [[S273_824518c9_orwo-may-quota-rate-vs-estimate|S273]] (ORWO May quota)

## The moment

The shipping-agent reported ORWO's May cost-quota rise as a **DHL "base-rate increase"**, reading it off the mart's `base_rate_eur` bucket rising per-ship (€0.749 → €0.878). Niklavs pushed back. Verifying against raw `dhl_orwo_invoices`, the per-weight-band base rate was **flat to the cent** (>93% of volume). The real driver: **71% of the cost rise sat in the `expected` (estimate) bucket** — uninvoiced May shipments priced at ~2.5× ORWO's actual invoiced rate, with the uninvoiced count nearly doubling as the month matures.

## The lesson

On an **order-month** basis, the current/recent month is only partially invoiced. `final_shipping_cost_eur` blends real invoiced cost with the `expected`/`avg` estimate, and the estimate can be badly miscalibrated for a source (here ORWO, ~€2.5 est vs ~€1 actual). So a month-over-month cost or quota *rise* on an immature month is **dominated by the estimate, not by carrier rates** — and attributing it to a rate change is wrong by default.

**Discipline before naming a cause for a cost/quota movement on a recent month:**

1. **Split by `cost_source`** (`invoice` vs `expected` vs `avg`/`null`). Size how much of the delta is real-invoiced vs estimated. If the estimate bucket carries most of it, the movement is a coverage artifact that reverses as invoices land.
2. **A mart cost-bucket (e.g. `base_rate_eur`) is a derived/allocated figure, not the carrier's billed rate.** To test "did the carrier raise prices," go to the raw invoice and compare **like-for-like** (same weight band, same zone) — an average-per-ship can move on mix alone.
3. Treat a sub-agent's load-bearing causal claim as a **hypothesis** (verify-subagent-findings): grep/query the ground truth before relaying it.

Secondary, same session: I **over-spawned** the shipping-agent for a one-source two-month bridge that I could have run myself once the reference was loaded (Niklavs flagged it; consistent with the 2026-06-17 spawn-policy change + the S260 litmus). The off-contract raw-invoice check, by contrast, *had* to be me — `ship_mart_ro` is DB-denied on silver. So the routing split is: bounded mart pulls → run myself; agent-shaped fan-out → spawn.

## Related

- Reinforces: verify-subagent-findings, populated-column-is-not-a-measurement, explain-output-from-data-not-code, decompose-before-attributing-a-cost-gap, distinguish-fixture-from-live.
- Domain: [[shipping-mart]] cost-basis (`cost_source` mix), the order-month quota lens.
