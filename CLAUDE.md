# brain/ — top-level router

This folder houses **two separate brain systems**:

- **`gielinor/`** — the **main brain**. The world the agent inhabits. Born 2026-05-20. The cognitive system Niklavs operates as.
- **`developer-braindead/`** — the **dev brain**. The construction log for building the main brain. A working notebook, not a cognitive system.

They are deliberately kept separate. Two brains, two audiences, two lifetimes.

## Routing rule

- **Working directory inside `gielinor/`** → read and follow `gielinor/CLAUDE.md`.
- **Working directory inside `developer-braindead/`** → read and follow `developer-braindead/CLAUDE.md`.

Do **not** cross-read by default. The main brain does not read dev brain content during normal operation, and vice versa.

## Cross-reference allowance

The main brain may read from the dev brain **only on explicit principal cue** — for example, "check the dev brain for why we structured X this way." The dev brain has no equivalent read access to the main brain in normal operation; it is a construction record, not a participant.

The dev brain may modify dev brain files. Changes to `gielinor/` happen in `gielinor/` sessions, not from inside the dev brain.

## What each brain is for

- `gielinor/_about.md` / `gielinor/CLAUDE.md` for the main brain's purpose and operating rules.
- `developer-braindead/_about.md` / `developer-braindead/CLAUDE.md` for the dev brain's purpose and conventions.

This file is a router. It does not duplicate any rules from either brain's own CLAUDE.md.
