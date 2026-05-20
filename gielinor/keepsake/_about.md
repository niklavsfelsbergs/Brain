# keepsake/ — always-surface items (global)

**Cognitive role.** Valence. High-priority items that always matter, surfaced first at respawn, never lost.

**Metaphor.** The keepsake box in RuneScape: cosmetic and sentimental items kept on death, separately from inventory. Here it's the things the agent must not forget — small, dense, persistent.

This layer is **global** — cross-player keepsakes apply regardless of who's active. Each player has its own `players/<name>/keepsake/` for player-relevant pins.

## What goes here

- Things the agent must surface or honor every session, regardless of context.
- A small handful of items, not a long list. The point is priority, not coverage.
- Currently load-bearing relationships, ongoing commitments, lines that must not be crossed.

If something is *always* important, it belongs here. If it's important *right now* it belongs in `inventory/` or `bank/`.

## What does not go here

- Reference material. (Use `bank/`.)
- Time-sensitive working state. (Use `inventory/`.)
- Things the agent thinks are probably important. Pinning is intentional — the principal pins; the agent only proposes.

## Structure

```
keepsake/
  _about.md            # this file
  current.md           # the active pin list — read at respawn, after CLAUDE.md
  proposals/           # agent-proposed pins, awaiting principal's decision
  archive/             # items rotated out of current.md (also rotated proposals)
```

## Write rules

The agent writes proposed additions only — files in `keepsake/proposals/`. The principal pins by editing `current.md` directly. Proposals that get pinned are archived (so the original proposal is preserved); proposals that don't are left in `proposals/` for bankstanding to triage. See `meta/write-rules.md`.

`current.md` has a size budget (placeholder ~2k tokens). Bankstanding's job is keeping it under budget by proposing rotations to `archive/`.

## Related

- `players/<name>/keepsake/` for player-scoped pins.
- `examine/` and `niksis8/` for the observations that may eventually graduate to keepsake-level pins.
- `meta/drafts-mechanics.md` for the proposal flow.
- `lorebook/decisions/` for the choice to keep this layer small.
