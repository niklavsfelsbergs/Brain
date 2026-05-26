# Defensive rules need counter-pressure rules

## What happened ([[S015_2026-05-21_ttyd-review-and-dry-run|S015]] dogfood)

Test question: "how many packages did we ship in April?"

**Before fix** — 20-line response with five clarifying questions and zero numbers. The agent was rule-following perfectly: every cautionary rule fired ("state assumptions," "be honest about missing," "sanity-check surprises," "clarify before answering"), and they all pushed the same direction. Result: a useful-shaped refusal.

**After fix** — same question landed *"~502K packages in April (calendar April 2026, all production lines combined)"* in one beat.

The change wasn't subtracting cautionary rules. It was *adding* counter-pressure rules — rules that push toward delivery: "answer first, caveats after," "partial answer beats refusal," "default confidently — the parenthesis lets the user correct one input rather than answer five questions."

## The rule

When authoring a behavior spec, the rule set needs internal tension. Cautionary rules balanced against delivery rules. A spec of only cautionary rules produces an agent that's careful at the expense of being useful.

## How to apply

When reviewing or authoring a §0-style behavior spec:

1. List rules pushing toward caution / disclosure / clarification.
2. List rules pushing toward delivery / commitment / partial-progress.
3. If column 1 dominates, the agent will gate. Add to column 2.

## Anchor

[[S015_2026-05-21_ttyd-review-and-dry-run|S015]] quest, two dogfood runs of the shipping-agent §0 spec. The shipping-agent's §0 rules 1, 3, 6 are the column-2 anchors (answer-first, length-matches-question, partial-beats-refusal) — load-bearing, not flair.
