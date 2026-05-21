# Jebrim — inventory/

**Cognitive role.** Working memory. What Jebrim is carrying right now — volatile, session-scoped, lost on death. **Primary resume surface** — what gets read at respawn to pick up where the last session left off.

**Metaphor.** The 28 inventory slots in RuneScape.

## What goes here

- **Resume state per active quest** — the "where we are," "next concrete step," open task list, decisions to load verbatim into next session's context. One file per in-flight quest, named to match the quest (e.g., `S014-ttyd-resume.md`).
- Open threads carried across turns within a session.
- Today's working state — the specific report being built, the stakeholder waiting for an answer, the query whose output is being inspected.
- Working drafts of an analysis that isn't ready to land in `bank/drafts/notes/` yet.

## What does not go here

- Anything that should survive a reset. (Use `bank/` or get it confirmed.)
- Narrative session content — turn log, decisions made in-flight. (Use `quest-log/`.)
- Knowledge about a project, query, or stakeholder. (Use `bank/drafts/notes/`.)

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

- **Close-session ritual writes resume state here, not into the quest log.** Per `gielinor/meta/layer-routing.md`. If a resume block ends up at the top of a quest log, route it to inventory instead.
- **Respawn ritual reads `inventory/*` as the resume foreground.** The first thing the agent surfaces at session start is the inventory state for in-flight quests.
- If something carries across more than two sessions and isn't quest-specific, it probably belongs in `bank/`, not inventory. Promote it.
- If something hasn't been touched in a session, drop it (the agent isn't actually carrying it).
