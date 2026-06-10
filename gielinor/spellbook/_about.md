# spellbook/ — procedures (global rituals + cross-player skills)

**Cognitive role.** Procedural memory. How to do things, not what is known.

**Metaphor.** A spellbook's entries are invoked, not just read. The act of casting is the value. Likewise: rituals here are *performed*, not just consulted.

`spellbook/` exists at two scopes:

- **Global** (this folder): cross-player rituals — `respawn`, `bankstanding`, eventually `ascension` — and any skills that any player can invoke.
- **Per-player** (`players/<name>/spellbook/`): procedures specific to a single character — Jebrim's BI-report drill, Zezima's reading-reflection drill, etc.

## What goes here (global)

- **Rituals** (`spellbook/rituals/`): the named, principal-owned procedures that govern the system's own operation. `respawn.md`, `bankstanding.md`, and later `ascension.md` (migration).
- **Skills** (`spellbook/skills/`): cross-player procedures the agent invokes during work. Mostly empty at Phase 1.

## What does not go here

- Character-specific procedures. Those go in `players/<name>/spellbook/`.
- Knowledge or facts. Those go in `bank/`.
- The agent's reasoning patterns. Those are noticed in `examine/`.

## Structure

```
spellbook/
  _about.md            # this file
  rituals/
    respawn.md         # session-start load order
    bankstanding.md    # periodic active reorganization
  skills/              # cross-player skills (empty Phase 1)
  archive/             # superseded skills/rituals
```

## Write rules

- `rituals/` is **user-only**. The agent does not edit its own core rituals; the principal does. This is a discipline rule, not hook-enforced (a hook restricting writes to `rituals/` would be a reasonable Phase 2 addition).
- `skills/` is draft-then-approve. New skills and modifications to existing ones go through drafts.

See `meta/write-rules.md`.

## Related

- `players/<name>/spellbook/` for character-specific procedures.
- `meta/drafts-mechanics.md` for the skill-modification flow.
- `lorebook/confirmed/` for choices about ritual design.
