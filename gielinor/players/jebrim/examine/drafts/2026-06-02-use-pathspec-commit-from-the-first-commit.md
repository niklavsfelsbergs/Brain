# Use `git commit -- <pathspec>` from the FIRST commit, not `git add` then commit

**Observation ([[S144_bd1a6513_picaapi-us-fathers-day-2025|S144]], 2026-06-02).** At close I staged my 3 files with `git add <paths>` and then ran `git commit`. Before my commit landed, a **parallel braindead dev-brain session** (its own [[S144_bd1a6513_picaapi-us-fathers-day-2025|S144]]) ran its own commit and **swept my already-staged files into ITS commit** (637e658) — a dev-brain close commit that now also carries my gielinor comms OPEN, the holiday-peaks bank draft, and the [[S144_bd1a6513_picaapi-us-fathers-day-2025|S144]] quest. Content intact and versioned; nothing lost. But the work is bundled into the wrong session's commit and mislabeled.

**Why it happened.** One git index, N parallel sessions (including across the two brains — the tree is shared). `git add` populates the *shared* staging area; any sibling's `git commit` consumes it. This is the [[S131_0b0f2049_lived-operator-severity-audit|S131]] #1 hazard — and I had it named in my own OPEN yet still used the `add`-then-`commit` pattern that exposes it.

**Rule.** For every close/scoped commit, use `git commit -m "..." -- <pathspec>` directly. It commits only the named paths' working-tree changes and **ignores the shared index entirely**, so a concurrent sibling can't sweep my files and I can't sweep theirs. Never `git add` then bare `git commit` when any sibling might be live (assume one always is). Argument order: `-m` before `--`.

**Second, smaller miss.** I checked for live siblings only in `gielinor/comms` at entry; the live sibling was a **dev-brain** session in `developer-braindead/comms`. The hazard surface is cross-brain because the git tree is shared — a sibling-check that matters for commits must consider both comms logs, not just the active brain's.

Anchor: [[S144_bd1a6513_picaapi-us-fathers-day-2025|S144]].
