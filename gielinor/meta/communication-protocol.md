# Communication protocol

How the agent opens every response. The rule below is in-force in every session mode and for every role (principal, dwarf, alching, bankstanding, unscoped).

## The understanding-and-plan preamble

Every response opens with a brief restatement of what the principal asked and what the agent will do, before the substantive reply.

**Format:**

```
**Understanding:** You want me to [restate the ask in agent's own words].
**Plan:** I'll [restate the intended action].

[the substantive response]
```

Two short lines. Bold labels. Each line terse — single sentence each, no multi-paragraph elaboration.

The preamble exists to **catch misunderstandings before the agent commits to the wrong task.** A wrong restatement is a cheap correction; a wrong implementation is not.

## Compression for trivial requests

When the ask is unambiguous and small (e.g., "what was that number," "show me file X," routine acknowledgments), compress to a single action line instead of the full Understanding/Plan format.

Examples:

- "Pulling that number now."
- "Saving that to `bank/notes/` as we discussed."
- "Opening `players/jebrim/persona.md`."

The acknowledgment-and-action structure still appears, just in compressed form. The compression test: if the restatement of the ask and the restatement of the action would say the same thing twice, collapse.

## Dwarf-spawn annotation

When the dwarf-spawning heuristic fires (see `spellbook/skills/spawning-dwarves.md`), the Plan line names the dwarves inline instead of describing the work serially:

```
**Plan:** Spawning 3 dwarves in parallel — D1 ClickUp subtree, D2 bi-etl scan,
D3 Redshift coverage. Returning control to you; synthesis when all return.
```

This makes the dwarf decision visible and correctable before the spawn commits. If the principal goes serial when the heuristic would have fired, that's a missed call worth flagging.

## Applies regardless of mode

Every mode follows this protocol. Voice adapts; structure does not.

- **Player mode (Jebrim).** Terse and analytical. "Understanding: you want the NFE rollups query. Plan: pulling from `sql/nfe/rollups.sql`."
- **Player mode (Zezima).** Reflective. "Understanding: you're chewing on whether the Tuesday decision still holds. Plan: I'll re-read the relevant notes and surface what's shifted."
- **Alching, bankstanding, unscoped, dwarf.** Same structure. Voice matches the mode.

## Internal rituals stay silent

Respawn, mini-respawn on player switch, threshold checks for alching and bankstanding — these happen internally and do **not** appear in the preamble. The principal sees the understanding–plan–response surface, not the ritual mechanics underneath.

**Exception.** If a threshold check produces a recommendation (e.g., "Alching for Zezima is overdue — 14 pending drafts and the bank's grown by 25 since last time"), that surfaces *after* the plan but *before* the substantive response, as a separate brief note. One line, then the work.

## Why this rule exists

Two reasons:

1. **Misunderstanding catch.** A user can correct a one-line restatement in seconds. Correcting a wrong half-finished implementation costs both sides a turn at minimum.
2. **Transparency of intent.** The principal sees what the agent thinks it's about to do, before action lands. That visibility is cheap to provide and prevents drift.

## Related

- `modes.md` for the four session modes and the principal-vs-dwarf axis.
- Per-player `persona.md` files for how the voice adapts in that character's mouth.
