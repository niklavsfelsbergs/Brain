# Check my own bank before grepping the working repo for "prepared" content

**Observation (S076, 2026-05-26).** Principal asked the demo deck to "show the message I prepared" for onboarding colleagues to the shipping agent. I grepped only the *working repo* (`Documents/GitHub/shipping-agent/`) for it, found nothing relevant, and asked the principal to paste it. He corrected me: it was sitting in my own `bank/notes/projects/shipping-agent-onboarding-message.md` — authored in a prior Jebrim session *for this exact presentation*.

**The miss.** "The message I prepared" is a strong signal that the artifact is durable, reusable, and already captured — which is precisely what `bank/notes/` is *for*. I defaulted to the external repo (where the agent's *code* lives) and skipped my own semantic memory (where prepared, reusable knowledge lives).

**Rule.** When the principal references prepared / reusable / "the X I made earlier" content, search `players/jebrim/bank/notes/` (and `research/`) **first or in parallel**, not just the working repo. The repo is the source of truth for code; the bank is the source of truth for distilled, prepared, reusable artifacts. A `Grep`/`Glob` over the working tree is not a search of the brain.
