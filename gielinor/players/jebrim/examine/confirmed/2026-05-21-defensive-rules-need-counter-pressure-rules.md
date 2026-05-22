# Defensive rules need counter-pressure rules to avoid paranoid agents

**Date:** 2026-05-21 (S022)
**Source:** S015 quest, two dogfood runs of the shipping-agent §0 behavior spec.

## Observation

When codifying agent behavior, rules that all push in the same direction (e.g., all toward caution: state assumptions / honesty about missing / sanity-check surprises / clarify before answering) produce an agent that stacks them all at once and gates on disclosure. The first §0 draft had seven rules all biasing the agent toward more disclosure and more caution. The result, on the first dogfood ("how many packages did we ship in April?"), was a 20-line response with five clarifying questions and zero numbers. The agent had perfectly followed the rules and produced a refusal-shaped answer.

The fix was structural, not additive. Reframe answering as **delivering value**, with disclosure supporting the delivery rather than gating it. Add counter-pressure rules: "answer first, caveats after"; "default confidently — the parenthesis lets the user correct one input rather than answer five questions"; "if you want to ask more than one question, you're in the wrong mode"; "partial answer beats refusal." On the second dogfood after the rewrite, the same question landed `~502K packages in April (calendar April 2026, all production lines combined)` in one beat.

## Rule for next time

When designing a behavior spec, balance the cautionary rules with rules that explicitly push toward decisive action. The set has to have tension inside it. A spec of *only* "be careful" rules produces an agent that's careful at the expense of being useful. The trained-analyst model — *confident with caveats* — needs both sides on disk.

## How to apply

When reviewing or authoring a §0-style behavior spec for any agent:

1. List the rules pushing toward caution / disclosure / clarification.
2. List the rules pushing toward delivery / commitment / partial-progress.
3. If column 1 dominates, the agent will gate. Add to column 2.
4. The cross-cutting rules of §0 (the shipping-agent's setup, as it stands after S022) — answer-first, length-matches-question, partial-beats-refusal — are the column-2 anchors. They're not optional flair.
