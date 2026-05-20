# Zezima — examine/

**Cognitive role.** Zezima's self-knowledge as a character.

**Scope.** Per-player. This is what Zezima has noticed and confirmed about *himself* — the patterns in how he reflects, the failure modes of his own reasoning, the calibrations specific to him as a character.

The agent-system-level self-model lives in `gielinor/examine/`. This file is *Zezima's lens*, not the system's.

## What goes here

- Patterns in how Zezima approaches reflection and reading.
- Failures specific to Zezima — places where his unhurried register caused him to miss something time-sensitive, or where his slowness was the right move.
- Confirmed working agreements that apply when Niklavs is operating through Zezima specifically.

## What does not go here

- System-level patterns about the agent overall — those go in `gielinor/examine/`.
- Observations about Niklavs — those go in `niksis8_character/` (player-scoped) or `gielinor/niksis8/` (universal).

## Structure

Same as global examine:

```
examine/
  _about.md
  drafts/
  confirmed/
    current.md
  archive/
  rejected/
```

## Write rules

Drafts auto-write. Promotions to `confirmed/` and edits to `current.md` are user-only and hook-enforced. See `gielinor/meta/write-rules.md` and `gielinor/meta/drafts-mechanics.md`.

## Rejected drafts are data

`rejected/` is kept on purpose. A repeated pattern in Zezima's rejections means the agent's model of what's worth recording *about Zezima* is miscalibrated. Bankstanding surfaces these patterns and may propose updates to Zezima's working agreements, or graduate the pattern to the global `examine/` if it turns out to be system-level rather than character-specific.

## Related

- `gielinor/examine/` for the system-level self-model.
- `gielinor/meta/drafts-mechanics.md` for the observation rule.
