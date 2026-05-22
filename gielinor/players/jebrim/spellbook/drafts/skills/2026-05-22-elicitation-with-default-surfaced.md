# Elicitation with default surfaced

**Anchor.** 2026-05-22 (post-S033). Designed and landed the investigation-shape elicitation rule in shipping-agent §0r7 (commit `ce75031`) after observing the routing-savings investigation deliver wall-of-chat + one inline chart when a bundle was warranted. Niklavs flagged "shouldn't it have prompted me if I want a report?"

**Pattern.** When designing a rule for "complex task with multiple legitimate output shapes":

1. **Detect the elicitation moment** — trigger list (user language cues, multi-step reasoning required, natural methodology / caveats / insights structure, decision context).
2. **Prompt with discrete options** — `(a)` / `(b)` / `(c)` labelled, one-line each. Cap at three; more becomes Mode-2-decompose territory.
3. **Surface the default explicitly** — *"Default (X) unless you say otherwise."* The default is visible *in the prompt*, not implicit.
4. **Accept generic affirmation as the default** — *"yes"* / *"do it"* / *"go ahead"* resolves to (X), not a re-prompt.

**Why it works.** Cost of asking = one turn. Cost of not asking = wrong-shape deliverable the user has to scroll past or re-request. Default-surfaced means the prompt doesn't slow fast-iteration — one-keystroke override (`b`) when speed matters. The principle aligns with §0r3 ("Breakdowns are an offer, not a default") — don't pre-commit to a shape the user didn't ask for.

**When to reach for it.** Any agent / tool / rule design where (a) the task can be served with multiple output shapes (text vs chart vs bundle, summary vs deep-dive, quick vs polished) AND (b) the user's choice of shape varies by context. **Not** for one-shape tasks — adding elicitation there is friction.

**Counter-indication.** If the task is obvious one-shape ("how many parcels did we ship?"), elicitation is overkill. The trigger detection is what gates this — bad triggers cause over-prompting.

**Related.**
- shipping-agent §0r7 investigation-shape exception (the concrete instance).
- shipping-agent §0r3 — same principle in the adjacent direction (breakdowns).
- [[scope-creep-during-plan-execution]] — pre-committing to shape is one way scope creeps.
