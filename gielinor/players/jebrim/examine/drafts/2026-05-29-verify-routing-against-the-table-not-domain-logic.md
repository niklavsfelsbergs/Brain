# Verify a routing/coverage claim against the table, not from domain logic

**Observation ([[S122_330dea7d_eu-tender-switchable-incumbent-open-qs|S122]], 2026-05-29).** Asked whether Maersk's new offer covers the countries we currently ship with them, I stated that **GB routes through the ROW / FedEx-Economy branch** — reasoning from "post-Brexit, UK is non-EU, so it falls to ROW." It sounded right and I asserted it without checking. The principal's next message ("so no UK ... in the offer?") prompted me to actually query `row_zones.parquet` — **GB is absent there too**, served by neither branch. The claim was wrong; I corrected it.

**Rule.** When stating which branch / lane / code-path handles a specific case, **check the data or the table before asserting** — plausible domain logic (Brexit → ROW) is a hypothesis, not a finding. Cheapest fix is to run the one-line lookup first, then speak. Especially when the claim is a factual coverage statement the principal will act on.

**Generalizes.** Same family as [[check-record-before-defending-a-design-story]] / "verify enforcement fires" — don't assert system behaviour because it sounds architecturally right; ground it. Here the entry point was a *factual* coverage claim rather than a design story, but the failure mode is identical: confident inference standing in for a check.

## Anchor [[S122_330dea7d_eu-tender-switchable-incumbent-open-qs|S122]]
