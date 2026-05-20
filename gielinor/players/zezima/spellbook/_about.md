# Zezima — spellbook/

**Cognitive role.** Procedural memory. How Zezima does things — the procedures specific to him as a character.

**Metaphor.** Player-specific entries in his spellbook. The global rituals (respawn, bankstanding) live in `gielinor/spellbook/`; this is for Zezima's own moves.

## What goes here

- **Skills** (`skills/`): procedures Zezima invokes for his work — a reading-reflection skill, a synthesis-across-books skill, etc. Mostly empty Phase 1; grows from real use.
- **Rituals** (`rituals/`): character-specific named procedures. Rare. Most rituals are global.

## Structure

```
spellbook/
  _about.md
  skills/               # Zezima's skills (empty Phase 1)
  rituals/              # character-specific rituals (rare; empty Phase 1)
  archive/              # superseded skills/rituals
```

## Write rules

- `skills/` — draft-then-approve. New skills go through `gielinor/lorebook/drafts/` since adding a procedure is a decision worth recording.
- `rituals/` — user-only.

See `gielinor/meta/write-rules.md`.

## Related

- `gielinor/spellbook/_about.md` for the global rituals/skills.
