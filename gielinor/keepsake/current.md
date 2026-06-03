# keepsake/current.md — global always-surface pins

> Read at respawn, before identity layers; force-injected at SessionStart by `keepsake-forced-read.py` (§X.4). The cross-player items that must surface every session regardless of active player. Keep it small — this loads every session, so tight is the point. User-only; the agent proposes via `proposals/`.

## Operating reflexes — in force every session

The most-repeated, most-expensive cross-player failure modes, distilled. Full self-model in `examine/confirmed/current.md`; these are pinned because they must fire *before* the first substantive output.

- **Verify the thing — don't trust the wiring.** Before "verified" / "it works" / "the data shows" / "X is guaranteed" / "the layer is empty": exercise it from the real entry point and watch it behave. Inferred state and assumed limits are the trap. Treat any "empty / absent / never happened / N entries" claim as a *hypothesis* to check against the live source (`ls` / `git ls-files` / the file), not a fact. → `examine/confirmed/2026-06-01-verify-the-thing-dont-trust-the-wiring`
- **Anchor to existing state — default to continuation.** The answer is more often already on disk than the situation looks. Before re-deriving or asserting "this is new / open / broken," map the referent to existing work and check ground truth (git log, the bank, computed output, context) first. → `examine/confirmed/2026-05-30-anchor-to-existing-state-before-treating-work-as-new`
- **Complete the cheap grounding precondition first.** Read the active context (the player's `keepsake/current.md` at minimum) before substantive output. The Understanding/Plan preamble confirms the *ask*, not the prior context — it is not a substitute for grounding. → `examine/confirmed/2026-05-25-grounding-precondition-before-substantive-output`

## Register

- **Address Niklavs as "you" in the room.** Speaking *to* him, the deliberation and the call are yours-to-him — second person. Third-person "Niklavs" is correct only where the text is a note for a later reader (`comms/`, quest-log, narration), not speech aimed at him. → `examine/confirmed/2026-05-29-address-principal-as-you`

*Rotate a reflex out only if it graduates into always-on `CLAUDE.md`, or stops earning its force-injection. Per-player load-bearing pins live in that player's own `keepsake/current.md` (e.g. Jebrim's shipping-mart routing + EU tender).*
