# meta — the current rulebook

**What this is.** `meta/` is the agent's current rulebook. The conventions, write rules, mode definitions, and discipline that govern how the agent operates *right now*. Master `CLAUDE.md` `@import`s from here so these rules are in-context every session.

**What it is not.** It is not history. The record of *how* a rule came to be — the decision, the alternatives, the trade-offs — lives in `lorebook/confirmed/`. When a rule changes, the new version lands here and the old version is archived; the decision that produced the change is recorded in `lorebook/`.

**Two lifetimes.** `meta/` files are rewritten in place when rules change. `lorebook/` files only grow. If you need to understand *why* the rulebook says what it does, follow the cross-links from these files into `lorebook/confirmed/`.

**Files here.**

- `write-rules.md` — what each layer accepts: auto, draft-then-approve, or user-only.
- `modes.md` — principal vs dwarf, player×mode orthogonality, what each can write.
- `archive-discipline.md` — nothing is destroyed; archive mirrors active structure.
- `drafts-mechanics.md` — the drafts → confirmed flow, the observation rule, the `/drafts` command.
- `death-and-spawn.md` — crash recovery, reset behavior, migration (deferred).

**Edits.** Treat `meta/` as a user-controlled layer. The agent proposes changes via drafts in `lorebook/drafts/` (since rule changes are decisions); the principal applies them here.
