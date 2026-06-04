# Universal-from-a-single-verified-case (the session's recurring failure)

**The pattern.** Four times this session I verified ONE instance and stated it as true for the whole class; Niklavs caught each:

1. "DHL Paket Sperrgut = side > 60 cm" — actual trigger (from constants) is longest > 120 OR second > 60; "side>60" was the wrong predicate (38.3% vs the real 21.8%).
2. "chargeable = max(weight, volume/5000)" stated as *the* base-rate driver — it's carrier/lane/service-specific: gross-only (DHL Paket/Hermes/Güll/Austrian Post/Maersk-EU), ÷5000 (DHL Express/DPD PL/FedEx/Maersk-ROW), ÷6000 (GLS-EBP).
3. "dim cliffs are lane-independent" — DHL Paket's bulky *reject* cap is L+girth 360 DE / 300 intl; it moves by lane.
4. "the engines applied the right triggers" (plural) — I'd verified exactly one.

**The mechanism.** I confirm a fact for one entity and silently promote it to a universal — especially under momentum when a clean-sounding generalization is convenient.

**The rule.** In a multi-entity domain (9 carriers, each its own contract), **a carrier-specific mechanic is never stated as universal.** Any "all / every / always / never / each / X is Y" is a hypothesis until verified per-instance *or* proven structural. The tell to self-flag: if I can name the *one* place I checked, I haven't earned the universal.

**The irony worth keeping:** this exact failure kept happening *inside the v2 plan whose entire purpose is to stop it* — including a fix I made in §2 that I left stale in §3. A per-claim verification spine isn't enough; it needs a cross-document consistency pass, because a correction in one place breeds a contradiction in another.

→ generalizes; also written to cross-conversation memory. Sibling of [[2026-06-04-a-question-is-not-a-go-ahead]].
