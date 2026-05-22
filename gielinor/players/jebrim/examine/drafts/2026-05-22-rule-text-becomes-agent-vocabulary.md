# Rule-text becomes agent vocabulary

**Anchor.** 2026-05-22, shipping-agent transit-times investigation. The agent prefaced its response: *"per-shipment transit timestamps carry non-trivial DQ (rule 16), so I'll lean on cohort medians and flag uncertainty rather than report individual averages as ground truth."* Three jargon types in one sentence: rulebook meta-vocabulary (*"rule 16"*), analyst-internal terms (*"DQ"*, *"cohort medians"*, *"ground truth"*), and diligence-signaling that exposed both. Niklavs flagged: *"this is too technical in language."* Fixed via §0r2 extension (commit `ce58e1d`).

**Observation.** When I write a rule like *"per § 0 rule 16 — flag uncertainty on per-shipment timestamps,"* the agent reads the rule **and the rule's vocabulary**. The next time it applies the rule, it cites it: *"per rule 16..."*. The rule's *language* becomes part of the agent's user-facing language unless I explicitly mark the rule-language as internal-only. The trap is in being *diligent* — the agent signals "I'm applying the rule" by naming it. That's exactly the leak.

**Rule for me when writing agent rules.** Separate two languages:

- **Internal language** — what the rule says to the agent. Can use rule numbers, analyst jargon, technical terms. The agent needs precision.
- **User-facing language** — what the agent says to the user. Must be plain. Never echo rule numbers, never expose analyst jargon, never signal diligence by naming the rule.

Don't assume the agent will translate internal → user-facing on its own. It often won't. Explicitly mark which vocabulary stays internal.

**Application.** When extending shipping-agent rules in future sessions, proactively call out the internal/external split. Existing fix: §0r2 translation table now includes rulebook meta-vocabulary and analyst-internal jargon as explicit "translate or drop" entries. Reach for the same pattern in future rule edits — it's not unique to this one leak.

**Related.**
- shipping-agent §0r2 jargon translation extension (the fix).
- [[2026-05-22-elicitation-with-default-surfaced]] — same session; both come from observing the agent's behavior post-codification.
