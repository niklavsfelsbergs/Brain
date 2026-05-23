# Dimension-gate carrier-swap savings before sizing

> **Status.** Draft. Authored 2026-05-23 (Jebrim), harvested from a shipping-agent quota-reduction investigation.

## When to use

Any "move volume from carrier A → carrier B to save money" lever — carrier re-routing, market consolidation, oversize-tail repackaging, RFQ targeting. Any time the deliverable is "here's how much we'd save by switching these parcels."

## The skill — gate before you size

Before sizing the saving, gate the candidate volume on the **destination carrier's dimensional envelope**, not just weight + destination:

1. **Establish the destination carrier/product's envelope** — max dimensions + weight. E.g. DHL Paket = 60×60×120 cm / 31.5 kg.
2. **Pull the actual dimensions of the candidate parcels.** Bucket: fits / fails-on-side / fails-on-length.
3. **Size the saving on the eligible subset only.** Report "before dim filter / after dim filter" as two columns so the haircut is visible, not buried.
4. **The ineligible remainder isn't a dead lever — it changes shape.** Oversize-product rate card, repackaging into multiple compliant boxes, or customer surcharge. Re-size against the *right* product; don't drop it silently.
5. **Apply per-carrier.** Each alternative carrier has its own envelope; one gate doesn't transfer across the menu.

## Anti-pattern this replaces

Sizing a swap on weight + destination alone. In the originating case, UPS-DE 2–5 kg → DHL Paket was sized at €460K / 6mo, "high confidence, already audited." Dimension-gated, **70 of 124,777** parcels were eligible (0.06%) — TCG ships canvas (~98×71×5 cm) that busts the 60 cm side limit. The €460K was effectively €0. A whole carrier-routing investigation inherited the blind spot because it bucketed by weight + destination only, so *every* swap in the resulting lever menu was unvalidated.

## Inherited-confidence trap

A "high confidence, already audited" upstream investigation can carry a blind spot. Don't inherit its confidence rating without checking what it gated on. See examine [[2026-05-23-inherited-confidence-not-own-confidence]].

## Related

- Bank [[2026-05-23-package-dimensions-carrier-envelopes]] — the carrier-envelope + TCG-parcel-shape facts.
- [[mart-rate-decomposition-by-drill-down]] — decomposition produces the lever menu; this skill gates each lever's feasibility before it's sized.
