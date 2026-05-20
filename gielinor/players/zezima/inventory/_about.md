# Zezima — inventory/

**Cognitive role.** Working memory. What Zezima is carrying *right now* — volatile, session-scoped, lost on death.

**Metaphor.** The 28 inventory slots in RuneScape: limited, active, must be managed; dropped on death.

## What goes here

- Open threads carried across turns within a session.
- Today-only context that doesn't belong in bank.
- Working drafts of synthesis that isn't ready to land anywhere yet.

## What does not go here

- Anything that should survive a reset. (Use `bank/` or get it confirmed in `examine/`/`niksis8_character/`.)
- Narrative session content. (Use `quest-log/`.)

## Structure

Flat. One file per active piece of working memory. Filenames descriptive. No subfolders required.

```
inventory/
  _about.md
  <free-form files as needed>
```

## Write rules

Auto-write. Volatile by design. See `gielinor/meta/write-rules.md` and `gielinor/meta/death-and-spawn.md`.

## Discipline

- Don't let inventory accumulate. If something's worth keeping past today, move it to `bank/` or propose it as an identity-layer draft.
- Inventory is *carried* — meaning the agent looks at it each turn. If you don't need to look at it, it doesn't belong here.
