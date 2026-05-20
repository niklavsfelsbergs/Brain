# Jebrim — keepsake/

**Cognitive role.** Player-scoped valence. Items that always matter when Jebrim is active.

**Scope.** Per-player. Cross-player always-surface items live in `gielinor/keepsake/`.

## What goes here

- Things Jebrim must always surface when he's active.
- Currently load-bearing work projects, deadlines, or stakeholder commitments.
- Lines that must not be crossed in the work context (e.g., "Don't push to main without review.")

Small. Pinning is intentional.

## Structure

```
keepsake/
  _about.md
  current.md           # the active pin list
  proposals/           # agent-proposed pins
  archive/             # items rotated out
```

## Write rules

Proposals auto-write to `proposals/`. Pinning into `current.md` is user-only. See `gielinor/meta/write-rules.md`.

`current.md` has a placeholder size budget (~2k tokens). Bankstanding proposes rotations.

## Related

- `gielinor/keepsake/` for cross-player pins.
- `gielinor/spellbook/rituals/bankstanding.md`.
