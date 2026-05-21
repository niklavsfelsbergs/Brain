# Zezima — bank/

**Cognitive role.** Semantic memory. What Zezima knows that's worth keeping across sessions.

**Metaphor.** The bank: items sorted, kept, withdrawn on demand, reorganized during bankstanding.

## What goes here

- Notes from books, articles, essays Niklavs reads through Zezima.
- Connections across readings — synthesis that survives a single session.
- Reflection-derived knowledge: "I've noticed that [pattern] in my own life across these contexts."
- Reference material Zezima needs at hand: lists of works, recurring themes, ongoing reading projects.

## What does not go here

- Today-only context. That's `inventory/`.
- Session narrative. That's `quest-log/`.
- Self-observations. That's `examine/`.
- Observations about Niklavs as a person. That's `niksis8_character/`.
- **Procedures / methodology / how-to.** That's `spellbook/drafts/skills/`. Bank holds knowledge *about* what's been read or considered; skills hold *how* Zezima approaches a class of reflection (e.g., a "reading-with-resistance" method, a "compare-across-three-readings" workflow). See `gielinor/meta/layer-routing.md`.

## Structure

```
bank/
  _about.md
  drafts/notes/         # harvest candidates + chat-initiated drafts; promoted by alching
  notes/                # the active knowledge graph (markdown, freely wiki-linked)
  rejected/notes/       # drafts the principal turned down (kept; patterns matter)
  archive/              # mirrors notes/ — superseded entries
```

Free to subfolder `notes/` (and `drafts/notes/`) by topic as it grows. No pre-imposed taxonomy.

## Write rules

Drafts-gated as of [[D-012]] (dev brain) / 2026-05-21. Zezima writes to `bank/drafts/notes/`; alching promotes to `bank/notes/` or rejects to `bank/rejected/notes/`. Overturning existing knowledge surfaces as a contradiction during alching review. Major shifts in how the agent operates still warrant a `gielinor/lorebook/drafts/` entry. See `gielinor/meta/write-rules.md`.

## Related

- `gielinor/spellbook/rituals/bankstanding.md` for periodic review.
- `quest-log/` (Zezima's) for the session entries that may graduate into bank notes.
