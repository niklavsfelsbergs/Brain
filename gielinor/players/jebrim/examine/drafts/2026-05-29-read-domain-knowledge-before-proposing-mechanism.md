# Read the domain's canonical knowledge before proposing a mechanism

**Observation ([[S124_61d62e21_shipping-agent-report|S124]], 2026-05-29).** Designing the weekly shipping report, I made two proposals from raw schema intuition that the principal corrected — both already answered in the shipping-agent's own reference docs:

1. I proposed `received_by_carrier_date` as the ship/cohort anchor. Principal: it's carrier-log quality, poor. `known-dq.md` confirms — 100% NULL by design for PCS/Rewallution/ORWO + large Picturator extkey gaps. The agent's canonical anchor is `shop_order_created_date`.
2. I suspected `PCS CMH` was a typo for `PCS CGN`. It's a real site (Camp Hill; PCS sites = CGN/PL/MI/PX/CMH per `sources.md`).

Both were one `get_object_details` / one `Read` of the agent's reference away. I had read keepsake but reached for the schema and intuition before the hardened knowledge base.

**Rule.** When designing over a domain that has a canonical knowledge base (the shipping-agent's `reference/*.md` for the mart), **read it before proposing a column, anchor, scope mapping, or value semantics** — don't infer from raw schema, and don't assume an unfamiliar value is a typo. The raw schema tells you a column exists; the reference tells you whether it's trustworthy. Sibling to [[2026-05-29-verify-routing-against-the-table-not-domain-logic|the verify-against-the-table rule]] and the recall-shaped read in the five-lens preamble.
