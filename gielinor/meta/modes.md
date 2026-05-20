# Modes — principal and dwarf

The agent operates in one of two modes per invocation. Mode is orthogonal to player: any player can run as either a principal or a dwarf.

## Principal mode

Interactive session with the user. Full capabilities. The agent can introspect, propose changes to identity layers, run the bankstanding ritual, spawn dwarves, switch players mid-session.

This is the default mode when a session starts.

## Dwarf mode

The agent has been invoked as a sub-agent by another agent (a principal, or — with principal approval — another dwarf). Dwarves share the same brain on disk, but write capabilities are restricted.

**A dwarf may write to:**

- `bank/notes/` of its inherited player.
- `quest-log/in-progress/` and `quest-log/completed/` of its inherited player.
- `inventory/` of its inherited player.
- `lorebook/patch-notes.md` (factual record of changes).

**A dwarf may not:**

- Write to any `confirmed/` path (hook-enforced).
- Write to any `drafts/` path. Observations from dwarf work go in the quest-log entry; the principal decides whether they become drafts later.
- Touch `keepsake/` at any level.
- Touch `lorebook/decisions/` or `lorebook/assumptions.md`.
- Touch any file in `spellbook/rituals/`.
- Touch `meta/`.
- Promote drafts to confirmed.
- Spawn further dwarves (hook-enforced).

These restrictions are partly hook-enforced and partly discipline. See `.claude/hooks/` for the architectural lines; the rest the agent must hold itself to.

## Player inheritance

By default, a dwarf inherits the principal's player. A Zezima-spawned dwarf operates in Zezima's namespace — reads from Zezima's `bank/`, writes its quest-log entry to Zezima's `quest-log/`.

**Cross-player invocation** is allowed but must be explicit. The principal names which player the dwarf should embody. Example: Zezima (principal) spawns Jebrim as a dwarf to handle a work-flavored task on the side. The Jebrim-dwarf operates in *Jebrim's* namespace — reads Jebrim's bank, writes its findings to Jebrim's quest-log — and returns a summary to the Zezima-principal. The Zezima-principal then notes in *her* quest-log that she delegated the task.

## Principle

Principals are introspective. Dwarves are functional.

Principals can change who the agent (or a player) thinks it is. Dwarves can only do the work they were invoked for and leave a trace.

## Related

- `write-rules.md` for the full per-layer table; this file documents the dwarf subset.
- `.claude/hooks/dwarf-write-boundary.py` and `.claude/hooks/block-sub-dwarf-spawn.py` for the enforcement.
- `lorebook/decisions/` for the choices that shaped this split.
