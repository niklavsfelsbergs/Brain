# Inherited confidence is not my confidence

**2026-05-23.** In a shipping-agent quota-reduction investigation I framed "move UPS-DE 2–5 kg → DHL Paket" as a high-confidence, already-audited €460K / 6mo lever — citing a prior carrier-routing investigation. The principal asked whether I'd accounted for package dimensions (DHL Paket caps at 60×60×120 cm). I hadn't. The feeding investigation had gated on weight + destination only; I carried its confidence rating forward without checking what it actually controlled for. Dimension-gated, the lever was 70 of 124,777 parcels — effectively €0, and the same blind spot infected every other swap in the menu I built on top of it.

**Rule.** When reusing a prior investigation's finding as a high-confidence input, verify *what it gated on* before inheriting its confidence. A finding's confidence rating describes the checks that produced it, not the checks my current use requires. State the inherited assumption explicitly ("this assumes the feeding audit gated on X") so the gap is visible and correctable rather than silently propagated.

**Related:** skill [[dimension-gate-carrier-swap-savings]]; [[2026-05-22-audit-finding-vs-ground-truth]].
