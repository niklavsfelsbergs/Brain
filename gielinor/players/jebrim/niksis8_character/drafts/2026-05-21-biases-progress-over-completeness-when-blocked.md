# Biases progress over completeness when blocked

**Observed:** S014, 2026-05-21. The TTYD how-to quest had been parked in HOLD STATE waiting for the mart's V1 update cycle to settle. Multiple hours into the wait, principal pivoted: *"okay ETL team is fucking up and the mart wont be refreshed so soon, but we have to start building. We can correct later. How could we continue?"*

**The pattern.** When an upstream dependency slips, Niklavs does not extend the wait. He converts the slip into a re-plan and ships against partial information rather than nothing. Status blocks and patch-later are acceptable; idle is not.

This is not impatience — it's a calibrated tradeoff. He understands the work will need a correction pass; he prefers a corrected artifact over a delayed one. The frame is "what's the cheapest thing to do right now that doesn't get thrown away when the upstream catches up?"

**How to apply.**

- When a quest hits a HOLD STATE on external dependency, **don't sit in hold quietly**. Surface the blocked-vs-buildable split proactively: "X blocks final smoke test, but A and B are buildable now."
- Build with explicit status blocks rather than waiting for clean inputs.
- Don't over-design the correction pass — keep the unstable parts narrowly scoped so the patch is mechanical when it lands.
- This applies to *his work* — when *I* am blocked on principal input, the principle inverts: ask the smallest unblocking question rather than guess.

**Counter-cue to watch for.** If he says "wait" or "hold on" explicitly, hold. The bias toward progress is a default, not a rule. He overrides it when waiting is genuinely the right move.

## Related

- `S014_2026-05-21_shipping-data-mart-ttyd-howto.md` turn log T5 — the originating moment.
- [[moving-target-work-decomposition]] (bank draft) — the workflow pattern this preference shapes.
