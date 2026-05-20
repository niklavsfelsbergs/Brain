# Jebrim — spellbook/

**Cognitive role.** Procedural memory. How Jebrim does things — the procedures specific to him.

**Metaphor.** Player-specific entries in his spellbook. Global rituals live in `gielinor/spellbook/`.

## What goes here

- **Skills** (`skills/`): procedures Jebrim invokes — running a recurring BI report, doing a standard ETL fix, generating a stakeholder summary, etc. Mostly empty Phase 1; grows from real use.
- **Rituals** (`rituals/`): character-specific named procedures. Rare. Most rituals are global.

## Structure

```
spellbook/
  _about.md
  skills/               # Jebrim's skills (empty Phase 1)
  rituals/              # character-specific rituals (rare; empty Phase 1)
  archive/              # superseded skills/rituals
```

## Write rules

- `skills/` — draft-then-approve via `gielinor/lorebook/drafts/`.
- `rituals/` — user-only.

See `gielinor/meta/write-rules.md`.

## Discipline

When a recurring work task settles into a stable shape — same inputs, same steps, same shape of output — propose it as a skill. Don't write speculative skills; write skills for procedures that have already happened a few times.

## Related

- `gielinor/spellbook/_about.md` for the global rituals/skills.
