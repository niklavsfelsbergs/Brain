# developer-braindead/ — dev brain CLAUDE.md

This is the **dev brain**. It captures everything about *building* the main brain (`gielinor/`) — design conversations, decisions, experiments, false starts, build context, external research.

It is a working notebook, not a cognitive system. No agent runs cycles over it during normal operation. There are no players here, no alching, no bankstanding rituals. The dev brain has its own structure and its own rituals (see `spellbook/`).

## How to start a session here

**Read `respawn.md` at this folder's root before doing anything else.** It is the entry point — current state, what was just done, what's blocking, the next concrete step. The ritual that reads it is `spellbook/respawn-ritual.md`.

## Scope

When working in the dev brain, the agent is operating as a **build assistant** for the main brain — not as a character, not as gielinor itself. No persona to maintain. The deliverable is well-considered changes to the main brain's structure and supporting design notes.

- **Reads:** dev brain content freely (`bank/`, `examine/`, `quest-log/`, `player/`, `spellbook/`).
- **Writes:** dev brain layers per `_about.md` conventions; superseded entries move to the layer's `archive/`.
- **Does not modify `gielinor/` from this brain.** Main brain changes happen in main brain sessions.

## Cross-reference allowance

The dev brain may read from `gielinor/` **only on explicit principal cue** — for example, "check how respawn ended up in the main brain." This is a recall affordance, not a default. Treat the main brain as a separate codebase that this brain documents the *construction* of.

## Conventions

See `_about.md` for the layer table, ID format, wiki-link rules, and the never-destroy discipline. Notable items:

- Entry IDs (`D-NNN`, `A-NNN`, `Q-NNN`, `R-NNN`, `I-NNN`) are stable; filenames add a descriptive suffix.
- Quest log files named `SNNN_descriptive_name.md`, titled at session close.
- Wiki-links `[[ID]]` are load-bearing across docs.
- `bank/plan.md` is the single-file living plan for the mission.

## Related

- `respawn.md` — current state and next concrete step. Read first.
- `_about.md` — layer table and conventions.
- `spellbook/respawn-ritual.md` and `spellbook/session-close.md` — the rituals that read and update `respawn.md`.
- `../CLAUDE.md` — the brain-root router that distinguishes this brain from `gielinor/`.
