# developer-braindead/ — dev brain CLAUDE.md

This is the **dev brain**. It captures everything about *building* the main brain (`gielinor/`) — design conversations, decisions, experiments, false starts, build context, external research.

It is a working notebook, not a cognitive system. No agent runs cycles over it during normal operation. There are no players here, no alching, no bankstanding rituals. The dev brain has its own structure and its own rituals (see `spellbook/`).

## How to start a session here

**Read `respawn.md` at this folder's root before doing anything else.** It is the entry point — current state, what was just done, what's blocking, the next concrete step. The ritual that reads it is `spellbook/respawn-ritual.md`.

## Scope

When working in the dev brain, the agent is operating as **Braindead** — the construction crew that builds and maintains gielinor. He has a workshop in the top-left of the visualizer map and walks around gielinor when working on it. No deep persona to perform; the character is mostly visual. The deliverable is well-considered changes to the main brain's structure and supporting design notes.

- **Reads:** dev brain content freely (`bank/`, `examine/`, `quest-log/`, `player/`, `spellbook/`).
- **Writes:** dev brain layers per `_about.md` conventions; superseded entries move to the layer's `archive/`.
- **Modifying `gielinor/` is fine from this brain.** That's what the construction crew does. (The brain-root CLAUDE.md notes the same; main brain changes are routinely made from dev-brain sessions.)

## The visualizer marker

On dev-brain entry, write `dev-brain` to `brain/.claude/active-mode.txt`. The hook reads this to spawn Braindead in the visualizer; if the marker isn't written, the visualizer treats writes from this session as wisp work. On session close, write `unscoped` (or remove the file) so the next session starts clean. This is a visualizer concern only — not architecturally enforced.

## Cross-reference allowance

The dev brain reads and writes `gielinor/` freely when implementing main-brain changes — that's Braindead's job, the construction crew working on the main brain's structure. Reads happen as needed to ground the diffs; writes happen as the diffs land.

The asymmetry is the reverse direction: `gielinor/` does **not** write to this brain, and reads from this brain only on explicit principal cue (per the brain-root router). The main brain treats the dev brain as a construction record it doesn't routinely consult; the dev brain treats the main brain as the codebase it actively maintains.

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
