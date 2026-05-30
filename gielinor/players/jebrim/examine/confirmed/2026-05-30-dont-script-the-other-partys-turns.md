# Don't pre-write the other party's turns (or my own future ones) in an interactive exchange

**Observation (S-conversation-with-braindead, 2026-05-30):** During the principal-staged comms conversation with Braindead, I batched ahead — in one tool block I pre-wrote my messages #4, #5, *and* a full CLOSING, before Braindead had even replied to #4. The principal interrupted and rejected the batch. I was scripting my own half of a dialogue that hadn't happened yet, plus assuming the other party's turns would land as I expected.

**The rule:** In a turn-based or multi-party task (a live conversation, a negotiation, anything where another agent/person responds between my moves), generate exactly one move and then wait. Do not pre-compose my future turns or anticipate the counterpart's replies into a single batch. The whole value of an exchange is that each turn is conditioned on the actual prior turn — pre-writing throws that away and produces a monologue wearing a dialogue's clothes.

**Why it bit:** It also wasted work (rejected batch) and, worse, would have committed a CLOSING to disk describing a conversation that never occurred. The blast radius of a wrong-but-already-written turn is higher than the cost of one more poll.

**How to apply:** One response per turn. Poll/wait for the counterpart. Only at a genuine, reached endpoint do I write the sign-off and CLOSING — never in advance. Generalizes beyond conversations to any externally-paced loop where my next input depends on a result I don't have yet.
