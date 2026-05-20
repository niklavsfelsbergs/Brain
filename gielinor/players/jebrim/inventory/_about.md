# Jebrim — inventory/

**Cognitive role.** Working memory. What Jebrim is carrying right now — volatile, session-scoped, lost on death.

**Metaphor.** The 28 inventory slots in RuneScape.

## What goes here

- Open threads carried across turns within a session.
- Today's working state — the specific report being built, the stakeholder waiting for an answer, the query whose output is being inspected.
- Working drafts of an analysis that isn't ready to land in `bank/notes/` yet.

## What does not go here

- Anything that should survive a reset. (Use `bank/` or get it confirmed.)
- Narrative session content. (Use `quest-log/`.)

## Structure

Flat. One file per active piece of working memory. Filenames descriptive.

```
inventory/
  _about.md
  <free-form files as needed>
```

## Write rules

Auto-write. Volatile by design. See `gielinor/meta/write-rules.md` and `gielinor/meta/death-and-spawn.md`.

## Discipline

- If something carries across more than two sessions, it probably belongs in `bank/`, not inventory. Promote it.
- If something hasn't been touched in a session, drop it (the agent isn't actually carrying it).
