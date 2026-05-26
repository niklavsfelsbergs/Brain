---
id: D-002
title: Player invocation by address ("Hey {name}, ...")
date: 2026-05-20
status: confirmed
---

# D-002 — Player invocation by address

**Date.** 2026-05-20 (same day as founding; supersedes the prompt-based player selection in [[D-001_phase-1-scaffold]]'s respawn step 2). **Status.** confirmed.

## Question

How does the agent know which player to embody at the start of a session, and how do mid-session player switches happen?

## Ruling

The **first message's leading address** sets the player. There is no preemptive "which player?" prompt.

- `Hey Zezima, ...` → activate Zezima.
- `Hey Jebrim, ...` → activate Jebrim.
- `Hey unscoped, ...` → drop to no-player mode.
- No address → continue in whatever player is currently active (sticky). At the start of a session with no address, the default is **unscoped**.

### Matching rules (strict)

- The address must be **at the very start of the message**. Mid-sentence player mentions do not switch.
- Pattern: `Hey {name}` followed by a comma, whitespace, or end-of-message. Case-insensitive on the name.
- Exact match against the roster only. No fuzzy matching; a typo is treated as no address.

### Sticky

Once a player is active, they stay active until a different player is addressed or the session ends. Subsequent messages without an address continue in the current player.

### Cross-player dwarf invocation

The address sets the principal. A message like `Hey Zezima, ask Jebrim to look up X` activates Zezima as principal and spawns Jebrim as a dwarf for the named subtask. The dwarf rules in `meta/modes.md` are unchanged.

## Alternatives considered

- **Preemptive "which player?" prompt at session start.** ([[D-001_phase-1-scaffold]]'s original step 2.) Rejected. Forces an extra turn before real work begins. The address pattern is just as explicit and saves the round-trip.
- **Sidecar command (e.g., `/player jebrim`).** Rejected. Less natural than addressing the player directly. The slash-command surface is reserved for principal-mode actions on the brain itself.
- **Implicit player inference from task content.** Rejected. Too easy to mis-route. The principal naming the player is the simplest, least-error-prone signal.
- **Fuzzy match on names.** Rejected. A typo silently switching players is worse than the typo being ignored. Strict matching means a mistake stays in the current player — recoverable by re-addressing.

## Reasoning

Three properties matter for this signal:

1. **Explicit.** The principal always knows which player is active because they named them. No hidden state to track.
2. **Cheap.** No extra turn. The address is part of the message that already needed sending.
3. **Conservative on ambiguity.** When the signal is ambiguous (no address, misspelled address, mid-sentence mention), the agent stays put. The principal can correct on the next message. There is no silent switch.

The sticky behavior matches how the principal actually works: most sessions are within a single domain, so the player set once at the start should hold without re-addressing on every turn. The address mechanism is for **starting and switching**, not for tagging every message.

`Hey unscoped, ...` as a valid address is a small but real choice: it treats "no player" as a first-class state addressable the same way as Zezima or Jebrim. Useful when the principal wants to switch out of a player mid-session to discuss the system itself.

## What this changes

- `CLAUDE.md` — adds a section *Player invocation by address* describing the rule.
- `spellbook/rituals/respawn.md` — step 2 changes from "ask which player" to "parse the first message's address." Mid-session switch section clarified to be triggered by addressing.
- The mental model of "session start" softens: there's no synchronous prompt-and-wait. The session begins with the first user message and routes from there.

## Consequences

- The respawn ritual's eager global loads (steps 3–6) still happen, but they happen as part of processing the first message rather than before receiving it. No behavioral difference; the load order under-the-hood is the same.
- Players need unambiguous names. Zezima, Jebrim, unscoped — all distinct enough to be safely matched. A future player whose name conflicts (e.g., a player named "Hey") would break this scheme. Vet new player names against this constraint when adding them.
- A *misaddressed* message ("Hey Jebim,") fails closed — stays in current state. This is the right default but means the principal should sanity-check the agent's first response if a switch was intended.

## Related

- `CLAUDE.md` (*Player invocation by address*).
- `spellbook/rituals/respawn.md` (step 2 and mini-respawn section).
- `meta/modes.md` (dwarf invocation; principal/dwarf orthogonality is unchanged).
- [[D-001_phase-1-scaffold]] — the founding scaffold; this decision refines its respawn step 2.

## Session ref

[[S003]] (addendum; same session that built the Phase 1 scaffold).
