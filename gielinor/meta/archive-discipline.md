# Archive discipline — nothing is destroyed

The hardest rule in the system: **the agent never deletes content. It only moves it.**

A delete hook (`.claude/hooks/block-deletes.py`) enforces this on the file-system level. The agent cannot bypass it.

## Why

Three reasons:

1. **Recoverability.** A wrong move stays recoverable forever.
2. **Pattern memory.** Things the agent proposed that were rejected, or facts the user superseded, are themselves data — patterns in rejections reveal where the agent's model is drifting.
3. **Trust.** The principal can authorize the agent to reorganize aggressively because reorganization is never destructive.

## Structure

Each layer has an `archive/` subfolder that **mirrors the structure of its active content**. When bankstanding moves a file out of active use, it preserves the file's relative path inside `archive/`.

Example:

```
bank/
  notes/
    cognition/
      working-memory.md          # active
  archive/
    notes/
      cognition/
        working-memory.md        # superseded version, moved here
```

Identity layers (`examine/`, `niksis8/`, `niksis8_character/`) keep **two** historical folders, with different meanings:

```
examine/
  drafts/                         # proposals awaiting review
  confirmed/                      # approved, currently in force
  archive/                        # mirrors confirmed/ — superseded entries
  rejected/                       # mirrors drafts/ — proposals turned down
```

- `archive/` = "this used to be true; it isn't anymore."
- `rejected/` = "this was proposed; it never qualified."

Different histories. Both kept.

## Operational rules

- **No delete operations on any file under the brain folder.** Use moves.
- **Moves into `archive/` preserve the source's relative path.** A file at `bank/notes/x/y/z.md` archives to `bank/archive/notes/x/y/z.md`.
- **Moves into `rejected/` likewise preserve the path inside `drafts/`.** A draft at `examine/drafts/some-observation.md` rejects to `examine/rejected/some-observation.md`.
- **Filenames remain unique within their final destination.** If a collision occurs, append a timestamp suffix; do not overwrite.
- **Bankstanding proposes moves; the principal approves them.** Especially in the early phase, surface moves rather than auto-executing them.

## What this does not cover

This file is about content discipline. *Reset* behavior (which layers persist across deliberate restarts, which are lost) lives in `death-and-spawn.md`.

## Related

- `.claude/hooks/block-deletes.py` for the enforcement.
- `drafts-mechanics.md` for the `rejected/` flow.
- `death-and-spawn.md` for what survives reset.
