# Treated "repo denies push" as fact without ever testing it

**Claim.** I carried a "shipping-agent settings deny push" constraint as established fact and propagated it — when finally tested, it was false.

**Anchor.** [[S062_7f1aecf4_shipping-agent-euro-precision-and-build-report|S062]], 2026-05-25. Prior comms ([[S054_50b00902_shipping-agent-audit-2|S054]]) recorded *"shipping-agent local-only — its settings deny push,"* and the keepsake routing pin / my own OPENs this session echoed *"push denied by design."* I repeated it to the principal as a known constraint. On the principal's cue I ran `git push origin main` → it succeeded cleanly (`84ad74e..7562825`, exit 0, 8 commits). No block of any kind. The belief had crossed several sessions and was never once tested.

**Rule.** Don't assert or propagate an inherited constraint — push-denial, a permission, a capability limit — as fact until I've watched it actually fail. Phrase untested inherited claims as unverified ("recorded as push-denied, haven't tested"), not as fact. The cost of testing is one command; the cost of propagating a false constraint is sessions of avoided actions.

Concrete instance of [[2026-05-23-inherited-confidence-not-own-confidence]] and the memory *verify-enforcement-fires*.
