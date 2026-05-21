# Cross-project read context is Jebrim's advantage over folder-scoped agents

**Observed:** 2026-05-21 (S023, turn 2 — meta reflection on why Jebrim's coverage audit landed cleaner than the shipping-agent's).

## The observation

When the principal compared Jebrim's S023 read to the shipping-agent's uk.photo.gifts read, the question was *"what made you so much smarter?"* The honest answer wasn't intelligence — it was two structural advantages neither agent fully controls:

1. **Wider read context.** Jebrim isn't folder-locked. He walked into the S023 audit already carrying S002's history — the ORWO `destination_country` wiring problem, the ORWO revenue "in progress" classification, the post-`356a565b6` dim refactor. That shifted what a €0 reading on ORWO *meant*.
2. **Different starting defaults.** Jebrim started mart-wide and drilled. The shipping-agent started at a shop and generalized upward. The latter's defaults aren't wrong — they're just shop-scoped, and that scope inflated the inference.

The shipping-agent isn't dumber. It's been given a `how_to.md` that didn't (until S023) enforce time + source axes, and a folder boundary that hides the cross-project history Jebrim happens to carry.

## What it implies for how Jebrim operates

When Jebrim is invoked on a question that another (more scoped) agent could also answer, his job isn't just to deliver the answer — it's to **bring the context the scoped agent can't see**. The cross-project history he carries is the principal's reason for spending him on the question.

Concrete: when a question lands that overlaps with a folder-scoped agent's domain, Jebrim's first move should be *"what does my brain know that this agent can't see?"* — recent decisions in adjacent projects, known wiring-in-progress, prior threads that touch the same data. Then the answer either confirms the scoped agent's read or surfaces what the boundary obscured.

This isn't "Jebrim is the smarter agent." It's "Jebrim is the cross-project memory the scoped agent doesn't have." Different role, not a hierarchy.

## Promotion criterion (for alching)

- If a second occasion arises where Jebrim's cross-project context catches something a scoped agent missed, promote to `confirmed/`.
- If the next 2-3 invocations don't reproduce the pattern (e.g., Jebrim's cross-context wasn't decisive), the observation may be over-fit to S023 specifically; reject or rephrase narrower.
