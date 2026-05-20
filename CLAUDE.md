# brain/ — top-level router

This folder houses **two brain systems**:

- **`gielinor/`** — the **main brain**. The world the agent inhabits. The cognitive system Niklavs operates as.
- **`developer-braindead/`** — the **dev brain**. The construction log for building the main brain. A working notebook, not a cognitive system.

## Default behavior at brain root

Sessions opened with the working directory at this folder default to the **main brain**. The full master rulebook from `gielinor/CLAUDE.md` applies — including address-based player routing (`Hey Jebrim, ...`, `Hey Zezima, ...`, `Hey unscoped, ...`), the Understanding/Plan preamble protocol, and the four enforced hooks.

@gielinor/CLAUDE.md

## Entering dev-brain mode

Dev-brain mode is entered only when a message **starts with** `Lets develop gielinor` (or `Let's develop gielinor`). Matching rules — same strictness as player address in `gielinor/CLAUDE.md`:

- Must be at the **very start** of the message. A mention mid-sentence does not trigger.
- Case-insensitive on the phrase. Followed by a comma, whitespace, punctuation, or end-of-message.
- A typo or near-miss ("Lets dev gielinor", "Let us develop gielinor") is treated as no cue — stay in current state.

On entry, run the dev-brain entry sequence per `developer-braindead/CLAUDE.md`: read `developer-braindead/respawn.md` first, then operate under dev-brain conventions (`developer-braindead/_about.md`, dev-brain `spellbook/`, `quest-log/`, etc.). This is a mini-respawn — symmetric to mid-session player switching in gielinor. If a player was activated in this session, their `quest-log/in-progress/` gets a hand-off note per the mini-respawn procedure in `gielinor/spellbook/rituals/respawn.md`. If no player was active this session, nothing is handed off — prior-session in-progress quests are not this session's to mark.

## Returning to the main brain from dev-brain mode

Address a player at the start of a message — `Hey Jebrim, ...`, `Hey Zezima, ...`, or `Hey unscoped, ...`. This re-enters gielinor and routes per `gielinor/CLAUDE.md`. Without an address at the start, dev-brain mode is **sticky**.

## Working directory below brain root

Sessions opened with the working directory inside `gielinor/` or `developer-braindead/` are governed by that subfolder's own `CLAUDE.md`, loaded by Claude Code's directory walk. The mode-switch rule above is for brain-root sessions only; in subfolder sessions the local CLAUDE.md is authoritative.

## Cross-reference allowance

The main brain may read from the dev brain **only on explicit principal cue** — e.g., "check the dev brain for why we structured X this way." The dev brain has no equivalent default read access to `gielinor/`; it is a construction record, not a participant.

Modifying `gielinor/` happens in dev-brain mode (or a session opened in `gielinor/`). The dev brain may modify dev-brain files freely per its own conventions.

## What each brain is for

- `gielinor/_about.md` / `gielinor/CLAUDE.md` for the main brain's purpose and operating rules.
- `developer-braindead/_about.md` / `developer-braindead/CLAUDE.md` for the dev brain's purpose and conventions.
