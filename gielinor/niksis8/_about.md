# niksis8/ — universal facts about Niklavs (global)

**Cognitive role.** Model of the user. What the agent knows about Niklavs-the-human, universally — facts that hold regardless of which player is active.

**Metaphor.** `niksis8` is Niklavs' RuneScape username. The folder is named after the user, on purpose, so the layer is unambiguously about him.

## What goes here

- Stable facts. Name, location-class, role-class, family/work shape at a level of abstraction that doesn't decay weekly.
- Communication preferences that hold across all players. ("Defaults to terse responses; tolerates length when the task is genuinely long.")
- Long-running constraints and contexts. ("Operates on Windows; PowerShell is the local shell.")
- Pattern observations about how Niklavs makes decisions or works, when they apply universally rather than within a player's domain.

## What does not go here

- What Zezima knows about Niklavs that Jebrim wouldn't, or vice versa. That's per-player — `players/<name>/niksis8_character/`.
- Day-to-day state — what's currently on his calendar, what he's worrying about this week. That belongs in the active player's `inventory/` or `bank/` (if it's lasting context, not just today).
- The agent's own observations about itself. Those go in `examine/`.
- Aspirational claims with no observation backing them.

## Seed

On day one, this layer holds exactly: **My name is Niklavs.**

Everything else is learned over time through use, drafts, and approvals. Front-loading "facts about me" risks installing claims the agent should actually be earning through observation. The seed is small on purpose.

## Structure

```
niksis8/
  _about.md            # this file
  drafts/              # observations proposed but not yet approved
  confirmed/
    current.md         # the rolling, in-force model — read at respawn
  archive/             # superseded confirmed entries (mirrors confirmed/)
  rejected/            # drafts the principal turned down (mirrors drafts/)
```

## Write rules

Drafts auto-write. Promotions and edits to `confirmed/` are user-only and hook-enforced. See `meta/write-rules.md`.

## Related

- `players/<name>/niksis8_character/` for what each player knows about Niklavs through their specific relationship.
- `examine/` for the agent's self-model.
- `keepsake/` for facts about Niklavs that have become valence-bearing — pinned and surfaced every session.
- `meta/drafts-mechanics.md` for the observation rule.
