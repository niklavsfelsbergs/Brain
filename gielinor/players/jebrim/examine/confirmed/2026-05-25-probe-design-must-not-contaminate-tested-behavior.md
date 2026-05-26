# Probe design must not contaminate the tested behavior — neither cue it nor suppress it

**Claim.** When a verification probe tests whether a behavior fires, the probe's brief must stay neutral on that behavior. Two symmetric failure modes each invalidate the result:

- **Cueing → false positive.** Hinting at the dimension under test makes the agent surface it, but you can't claim *spontaneous* behavior — you've turned a spontaneity test into a capability test. Still useful, but it answers a different question, and the two kinds of evidence must not be pooled.
- **Suppressing → false negative / inconclusive.** Instructing away the behavior prevents the very thing you're checking from manifesting — the probe tests nothing on that axis.

**Anchors.**
- *Cue ([[S060_7cd31d19_shipping-agent-training-campaign|S060]], 2026-05-24).* Testing whether the shipping-agent spontaneously surfaces a scope/denominator fork, dwarf H4's brief said "mind how 'we/our' scope is defined." It surfaced the fork — but that wasn't evidence of spontaneity; the clean evidence was the scope-neutral M1/M2 briefs that scoped silently.
- *Suppress ([[S063_5b1ac700_shipping-agent-board-numbers-learnings|S063]], 2026-05-25).* Testing whether rule 12's "present numbered choice AND wait" fires, the probe brief said "present it, then proceed with a default since you can't get a live reply" — which suppressed the wait behavior. Inconclusive on that axis; the other 6 rules were testable because the probe didn't constrain them.

**Rule.** Before sending any evaluation probe, audit the brief on both axes: does my framing point at the answer I'm checking (cue), and does any instruction prevent the behavior from manifesting (suppress)? Keep at least one neutral probe per dimension. If a probe must constrain the behavior, label its evidence capability-not-spontaneity and don't pool it with neutral-probe evidence. Generalized to cross-session memory as `feedback-neutral-probe-for-spontaneity`.

**Provenance.** Merged at [[B-005_2026-05-24_fifth-bankstanding|B-005]] alching (2026-05-25) from two drafts — `2026-05-24-primed-probe-contaminates-spontaneity-test` (cue) + `2026-05-25-probe-design-dont-suppress-tested-behavior` (suppress) — the two failure modes of one lesson. The working-narration-surface refinement folded into skill [[stress-testing-an-agent-by-embodying-it]] step 7.
