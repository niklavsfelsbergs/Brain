# Teaching a rule — pair the rule with the CLI affordance

When teaching the agent a chart-hygiene (or analogous behavior) rule that translates to specific CLI calls, write the rulebook update **and** add the CLI flag that makes the rule cheap to follow — in the same pass.

## Why

[[S045_91ee1383_shipping-agent-chart-system-fixes|S045]]: principal cued *"teach the agent that when you filter a chart to 1 dimension, it should show labels."* If only the rule had been written to `how_to.md` §7 Mode 2, the agent would have had to freelance Plotly code to honor it (the existing CLI had no way to mark one trace as focused and others as legend-only). Freelancing is exactly the path that produced the original `,.0f` bug class — agent-authored chart code drifts away from the centralized styling.

Pairing the rule with `--focus <value>` made the rule cheap: the agent calls `build_inline_chart.py --color carrier --focus FEDEX` and the helper handles labels, legend-only siblings, line thickness. No freelance.

## How to apply

- When a principal teaching cue lands on a behavior that maps to a CLI helper, audit the helper first: does it expose the affordance the rule requires? If not, add it.
- The rulebook entry should *name the flag* explicitly: *"…via `--focus <value>` (others rendered as legend-only siblings)…"* — discoverable from the rule alone.
- Both changes ship together. A rule without an affordance is an invitation to freelance.

## Anchor

- `how_to.md` §7 Mode 2 *Direct value labels* (rule update).
- `harness/build_inline_chart.py` `--focus` flag (affordance).
- See [[S045_91ee1383_shipping-agent-chart-system-fixes]] for the full sequence.
