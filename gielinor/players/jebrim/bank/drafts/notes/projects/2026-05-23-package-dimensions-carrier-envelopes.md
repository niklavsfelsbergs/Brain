# Package dimensions — carrier envelopes vs TCG's canvas-shaped parcels

**As-of:** 2026-05-23. Harvested from a shipping-agent quota-reduction investigation (out-of-tree). Carrier-envelope figures and the parcel-shape numbers are from that investigation's pull — **re-verify the dimension column names on `shipping_mart.fact_shipments` against gold before relying on the parcel-shape stats.**

## The two facts that interact

1. **Carrier dimensional envelopes are hard cutoffs, independent of weight.**
   - **DHL Paket: max 60 × 60 × 120 cm, up to 31.5 kg.** A parcel over the envelope cannot ride DHL Paket — it goes on a DHL *oversize* product (Sperrgut / Großstück / similar), a different rate card and transit profile.
   - Every carrier has its own envelope. A weight + destination match does **not** imply the destination carrier can physically take the parcel.

2. **TCG's volume is canvas-dominated — long, flat, narrow.** On the UPS-Germany 2–5 kg lane the average parcel is ~98 × 71 × 5 cm, ~3 kg. These bust the DHL Paket 60 cm second-side limit *by design, not by exception*. They are prints, not boxes.

## Why it matters (the collapse)

In the quota-reduction investigation, "move UPS-Germany 2–5 kg → DHL Paket" was sized at €460K / 6mo and labelled high-confidence / already-audited. Dimension-gated against the 60×60×120 envelope, only **70 of 124,777** parcels (0.06%) were eligible:

- 87.0% fail on second-longest side > 60 cm (avg 98×71×5 cm)
- 12.9% fail on longest side > 120 cm (avg 121×90×6 cm)

The €460K lever was effectively **€0** as framed. The ~86K parcels DHL already moves on this lane can't all be on Paket either — they ride a DHL oversize product. The real lever is "UPS-DE canvas flow → DHL's *oversize* product," a different rate-card comparison.

## Useful column

`shippingprovider_extkey` on `fact_shipments` carries the DHL **service-tier / product** (Paket vs oversize variants). To learn which DHL product actually moves the canvas flow, pull the `shippingprovider_extkey` distribution for the parcels DHL already handles on the lane.

## Rule of thumb

Any carrier-swap savings number is invalid until the alternative carrier's dimensional envelope is gated against the actual parcel dimensions of the candidate volume. See skill [[dimension-gate-carrier-swap-savings]].

## Related

- [[shipping_mart_cost_vocabulary_2026-05-22]] — cost columns on the same fact.
- Skill [[dimension-gate-carrier-swap-savings]] — the methodology this fact feeds.
- Examine [[2026-05-23-inherited-confidence-not-own-confidence]] — how the blind spot propagated.
