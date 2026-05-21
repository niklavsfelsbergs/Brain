# Zezima — inventory/

**Cognitive role.** Working memory. What Zezima is carrying *right now* — volatile, session-scoped, lost on death. **Primary resume surface** — what gets read at respawn to pick the thread back up.

**Metaphor.** The 28 inventory slots in RuneScape: limited, active, must be managed; dropped on death.

## What goes here

- **Resume state per active quest** — the "where we left off," "the thread that's still hanging," "the question still in the air." One file per in-flight reflection or reading thread, named to match the quest (e.g., `book-of-laughter-resume.md`).
- Open threads carried across turns within a session.
- Today-only context that doesn't belong in bank.
- Working drafts of synthesis that isn't ready to land anywhere yet.

## What does not go here

- Anything that should survive a reset. (Use `bank/` or get it confirmed in `examine/`/`niksis8_character/`.)
- Narrative session content. (Use `quest-log/`.)
- Knowledge about a book, theme, or person. (Use `bank/drafts/notes/`.)

## Structure

Flat. One file per active piece of working memory. Filenames descriptive — for resume files, the convention `<quest-slug>-resume.md` makes them findable at respawn.

```
inventory/
  _about.md
  <quest-slug>-resume.md         # one per in-flight quest
  <free-form files as needed>
```

## Write rules

Auto-write. Volatile by design. See `gielinor/meta/write-rules.md` and `gielinor/meta/death-and-spawn.md`.

## Discipline

- **Close-session ritual writes resume state here, not into the quest log.** Per `gielinor/meta/layer-routing.md`.
- **Respawn ritual reads `inventory/*` as the resume foreground.** First thing Zezima surfaces at session start is the inventory state for in-flight threads.
- Don't let inventory accumulate. If something's worth keeping past today and isn't quest-specific, move it to `bank/` or propose it as an identity-layer draft.
- Inventory is *carried* — meaning the agent looks at it each turn. If you don't need to look at it, it doesn't belong here.
