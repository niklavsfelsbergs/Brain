# lorebook/ — build log (global)

**Cognitive role.** The history of how the agent came to be the way it is. Decisions, assumptions, and a factual record of changes.

**Metaphor.** In-game lore plus patch notes. The lore explains the world; the patch notes track what changed.

This layer is **global only.** Players don't have their own lorebooks — the build history is a property of the system, not of any character.

## What goes here

- **Decisions.** Numbered `D-NNN` entries — the choices that shaped the system. Each entry records the question, the ruling, the alternatives considered, and the reasoning. Wiki-linked from other layers.
- **Assumptions.** A single file (`assumptions.md`) listing the working assumptions the system is built on. These are explicitly invalidatable — if an assumption is broken by observation, bankstanding flags it.
- **Patch notes.** A factual change log (`patch-notes.md`). Auto-appended whenever the agent makes a substantive structural or content change. Distinct from quest-log: this is "what changed in the system" rather than "what we did in a session."

## What does not go here

- Active rules. The current state of the rulebook lives in `meta/`. Lorebook records the *decision* that produced a rule; meta holds the *rule itself*.
- Quest narratives. Episodic session content goes in the active player's `quest-log/`.
- Knowledge about content domains. That's `bank/`.

## Structure

```
lorebook/
  _about.md            # this file
  decisions/           # D-NNN_<slug>.md files, principal-approved
  drafts/              # proposed decisions and assumption changes
  assumptions.md       # working assumptions, user-edited
  patch-notes.md       # auto-appended factual record of changes
```

## Write rules

- `decisions/` and `assumptions.md` are user-only for confirmed content; the agent proposes via `lorebook/drafts/`.
- `patch-notes.md` is auto-write — the agent appends factual change records as they happen.

See `meta/write-rules.md` for the full picture.

## Decision numbering

Decisions are numbered globally and never renumbered. `D-001` is the founding decision (Phase 1 scaffold) and stays `D-001` forever. Archived/superseded decisions get a `superseded-by: D-NNN` field in their frontmatter; they aren't renumbered or removed.

## Brain birthdate

The brain was born **2026-05-20** — the day Phase 1 scaffolding landed. See `patch-notes.md` for the Day 0 entry and `decisions/D-001_phase-1-scaffold.md` for the founding decision.

## Related

- `meta/` for the current rulebook these decisions produced.
- Every other layer's `_about.md` for cross-links into the decisions that shaped them.
