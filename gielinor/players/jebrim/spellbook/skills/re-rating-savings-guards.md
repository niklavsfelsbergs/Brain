# Re-rating for savings — the trust-gate + mirage-guard pipeline

> **Status.** Draft (skill graduation, alching 2026-06-11, gnome g1 / sid8 03c3dbd4). Names a pattern that has repeated ≥2× and earned a name: the disciplined order-of-operations for turning a re-rating engine's output into a *defensible* savings claim. Principal NOD given in the prior alch pass (2nd recurrence [[S191_36b49f0c_eu-tender-annualization-report|S191]] accepted); today's [[S213_9ac35cce_ups-engine-vs-current-cost|S213]] go-forward catch is a further recurrence on the comparison-basis half.

## When to use

Any task that prices a **plan / engine / optimizer / scenario** against **actuals** and reports a saving — re-rating a carrier book, scoring a tender offer, "what would we save if we routed X to Y," sizing a lever. The deliverable is a € saving, and the failure mode is a confident headline that is half (or wholly) mirage.

## The pipeline (run in order — front-load the honesty gate)

1. **Trust-gate each engine against its OWN actuals first.** Before an engine is trusted as an *alternative*, validate it reprices the carrier's own current book within tolerance. Quarantine the biased ones; never fudge a bias ratio to make a lane work. Running the trust-gate *before* building any savings number is what surfaces untrustworthy engines before a fake number rests on them. → examine [[2026-05-31-rerating-mirage-guard-capability-and-noise]].

2. **Gate at the grain the bias + cost-basis actually live at.** A bias read at engine grain hides good lanes behind bad ones (a quarantined aggregate buries a valid lane) *and* hides bad lanes behind good ones. If the bias ratio's IQR is wide or multi-modal, split to lane/service grain and validate each. Confirm the **cost basis matches** (door-to-door vs last-mile-only / self-injection trucking) before reading a ratio as bias — a basis mismatch masquerades as engine error. → examine [[2026-05-31-rerating-trust-gate-grain-and-cost-basis]].

3. **Lane-aggregate — necessary but not sufficient.** Never headline a per-parcel cherry-pick. But aggregation alone doesn't kill the mirage; two more guards follow.

4. **Strip lanes that fail capability.** A freight→parcel swap is not like-for-like — a parcel engine will happily price palletized freight at €12. Gate each lane on service / weight / dim / freight class before it counts. The biggest "saving" is often physically impossible. → examine [[2026-05-31-rerating-mirage-guard-capability-and-noise]].

5. **Strip sub-resolution deltas.** A per-parcel saving below the destination engine's own self-error (and below a euro floor) summed over huge volume = the aggregation mirage (noise leaning one way × volume = a fake headline). → same anchor.

6. **Reconcile the model against ground-truth actuals before reporting the net delta.** When a ground-truth cost exists, reconcile model-vs-actual per slice; the gap reveals omitted components, and a flat fee can flip the sign. → examine [[2026-06-09-reconciliation-gap-is-the-rerate-completeness-check]], [[2026-06-09-decompose-cost-gap-before-attributing-cause]].

7. **Compare on the engine's go-forward / decision column, not the raw repriced column.** The raw per-unit repriced column prices units the plan never moves (rejected, unquoted, out-of-scope tail) at a fictional fallback — inflating or inverting the headline. Use the column that encodes which units actually switch vs stay (`go_forward_eur`, `stays_current`, `decision_*`). Before summing a "what would the offer cost" column, ask: does the plan actually move 100% of this population? → examine [[2026-06-11-go-forward-not-raw-reprice-when-comparing-plan-vs-actual]].

## The report shape

Report **PAPER vs DEFENSIBLE** explicitly — the gap between them *is* the mirage, and showing it is the credibility (the founding case: drop-DPD was €726k paper / ~€0 real). Keep the dispute-grade / contingent slice a visible separate line, never folded into the firm number. → examine [[2026-06-10-headline-the-bankable-floor-gate-the-contingent]].

## The repetitions that named it

- **[[S132_32ff1025_shipping-savings-routing-optimization|S132]] (2026-05-31)** — the founding pass: trust-gate-first surfaced 8/12 engines untrustworthy; lane-aggregation alone still left a €1.75M headline ~50% mirage; capability + noise-floor guards were the missing pieces (both confirmed examine entries).
- **[[S191_36b49f0c_eu-tender-annualization-report|S191]] (2nd recurrence, principal-accepted)** — the NOD to graduate this to a skill.
- **[[S211_dcd18cfd_ups-savings-dbschenker-reroute-investigation|S211]] (2026-06-11)** — population/selection-mismatch produced a "saving is illusory" alarm reversed twice in one session (confirm-same-population).
- **[[S213_9ac35cce_ups-engine-vs-current-cost|S213]] (2026-06-11)** — the go-forward-vs-raw-reprice catch (step 7); raw-column sum over-stated the engine ~€116k and inverted the offer's competitiveness.

## Related

- [[savings-investigation-deliverable-shape]] — how to *present* the resulting lever menu (lead with moves, net overlap).
- [[dimension-gate-carrier-swap-savings]] — the capability-gate (step 4) as its own skill.
- [[mart-rate-decomposition-by-drill-down]] — produces the per-lane decomposition steps 2–5 operate on.
