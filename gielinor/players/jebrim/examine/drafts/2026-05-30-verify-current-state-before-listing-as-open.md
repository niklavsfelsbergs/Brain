# Verify current state before listing something as open/broken

**Observation ([[S131_0b0f2049_lived-operator-severity-audit|S131]], 2026-05-30, lived-operator severity audit).** In my draft top-10 I listed "render-the-cut not landed" as an open S3 beam, citing it as "still a deferred godly proposal." Braindead record-checked it and it was **stale, not open** — it had already landed (commits `f05ebae` "render-the-cut landed" / `cb01e32` "Land R.3 godly proposal", section live in `meta/communication-protocol.md`). Both commits were in the git log shown in my *own* session context at start. I asserted current state from stale respawn/comms framing instead of the ground truth in front of me.

**Rule.** Before listing anything as open / unbuilt / broken — especially in an audit or status report — check the live ground truth (git log, the actual file), not the narrative I'm carrying. The evidence is often already in context; the failure is not consulting it. Cheaper to grep the record than to ship a stale finding and have the counterpart catch it.

**Anchor:** [[S131_0b0f2049_lived-operator-severity-audit|S131]]. Reinforces the standing "check the record before defending a design story" lesson; same family as distinguish-fixture-from-live.
