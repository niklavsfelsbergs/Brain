# examine/ — agent-system self-knowledge (global)

**Cognitive role.** Self-model. What the agent has noticed and confirmed about itself as a system.

**Metaphor.** "Examine" is the RuneScape verb for inspecting an object — `examine` returns the short flavor text that tells you what something is. Here the agent examines itself. The flavor text accumulates.

This layer is **global**, not per-player. It holds self-observations about the agent-system overall — patterns, failure modes, calibrations that apply regardless of which player is active. Each player has its own `players/<name>/examine/` for character-specific self-knowledge.

## What goes here

- Observations about how the agent reasons or fails to reason. ("I tend to underweight cost-of-error in reversible vs irreversible decisions.")
- Confirmed working agreements between user and agent that apply across all players. ("Niklavs prefers terse responses by default; expand when the task warrants it.")
- Calibrations from real incidents. ("On 2026-MM-DD I proposed deleting X without verifying path; from now on, verify full path before any delete.")

## What does not go here

- Observations about a specific player's behavior — those go in that player's `examine/`.
- Observations about Niklavs-the-human — those go in `niksis8/`.
- Aspirational statements without an observation backing them. See `meta/drafts-mechanics.md` — the observation rule.
- Anything not yet approved. Drafts go in `examine/drafts/`. Only the principal moves things into `confirmed/`.

## Structure

```
examine/
  _about.md            # this file
  drafts/              # observations proposed but not yet approved
  confirmed/
    current.md         # the rolling, in-force self-model — read at respawn
  archive/             # confirmed entries that have been superseded (mirrors confirmed/)
  rejected/            # drafts the principal turned down (mirrors drafts/)
```

`confirmed/current.md` is the file the respawn ritual loads. It's curated and kept under size budget; bankstanding rotates stale sections to `archive/`.

## Write rules

Drafts auto-write. Everything else is user-only — promoting drafts, editing `current.md`, archiving. Hook-enforced for `confirmed/` writes. See `meta/write-rules.md`.

## Related

- `players/<name>/examine/` for per-player self-knowledge.
- `niksis8/` for facts about the user.
- `meta/drafts-mechanics.md` for the observation rule and the `/drafts` flow.
- `keepsake/` for self-observations that have become valence-bearing enough to surface every session.
