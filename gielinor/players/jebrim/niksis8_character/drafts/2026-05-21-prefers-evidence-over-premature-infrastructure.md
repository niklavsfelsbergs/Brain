# Niklavs — accepts deferral of infrastructure when evidence is absent

When offered the recommendation to defer building a piece of infrastructure (agent, skill, persistent scaffold) until evidence justifies it, Niklavs accepts the deferral. He is open to "test first, design second" framing even when his initial instinct was to build the infrastructure directly.

## Observation

S015 (2026-05-21). Niklavs proposed building a specialized shipping-data-mart agent for Jebrim to invoke when shipping questions come up. I pushed back with the reasoning that the specialist might solve the wrong problem (discoverability vs expertise) and that we'd lose the diagnostic if we built it before running the dogfood test. He accepted without resistance — "ok but what points the dwarf to all the TTYD relevant docs?" — pivoting straight into investigating the existing chain.

The pivot wasn't reluctant. He genuinely engaged with the investigation and accepted the smaller fixes (keepsake pin + one-line NFE callout patch) as the right move for now.

## Working implication for Jebrim

When proposing infrastructure that hasn't been built yet, **include the evidence** that justifies building it *now*. If evidence is absent, surface that absence and suggest the cheapest measurement first. Niklavs accepts the deferral when the reasoning is sound — he doesn't need to be sold on building.

The converse: a bare recommendation to build infrastructure, without an evidence anchor, may not land well. Lead with the evidence question, not the build question.

## Caveat

One data point. The deferral cost was low here (run a dogfood test next session vs. build an agent now). Watch whether this pattern holds when:

- The deferral cost is higher (delays a deliverable, blocks a downstream stakeholder).
- His instinct is stronger (he's already partway into building).
- The evidence framing is less crisp.

If the pattern survives those, it's a confirmed working trait.
