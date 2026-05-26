# Close-session ritual adoption

**Date:** 2026-05-20
**Session:** [[S001_2026-05-20_repo-orientation|S001]]

## What changed

Gielinor now has a `spellbook/rituals/close-session.md` ritual — a session-end procedure that codifies wrap-up. Sister to `respawn.md` on the other side of the session lifecycle.

The master `gielinor/CLAUDE.md` gained a "How to close a session" section pointing at the ritual.

## Why

Before this, gielinor had the **receiving** side of the session lifecycle (respawn ritual, reconciliation prompt on next-session start, per-turn quest-log discipline) but no **closing** side. The asymmetry meant:

- Chat-only drafts were volatile across sessions — if a draft hadn't been written to disk before the session ended, it was lost.
- Pending external actions (logged `pending` per `death-and-spawn.md`) could remain dangling, falsely triggering the reconciliation prompt on the next session.
- The in-progress quest-log entry was the rolling state but had no codified procedure forcing it to actually reflect reality at session end.
- Commits weren't routine — sessions could end with the brain in a not-yet-versioned state, removing the recovery floor.

Close-session closes those gaps in one ritual.

## What triggered it

The principal asked in [[S001_2026-05-20_repo-orientation|S001]] how a Jebrim session would hand off to the next session. The agent walked through the respawn-side mechanism (quest-log entry → reconciliation prompt) and admitted three gaps:

1. The shipping-data-mart landing note had been drafted in chat but never persisted — would be lost on restart.
2. External actions weren't being marked `pending` / `completed` per `death-and-spawn.md`.
3. There was no procedure to tighten the in-progress entry into a clean resume-from-here state before close.

The principal then noted that dev-brain has a `close-session` skill that works "great in unison" with `respawn` — and gielinor doesn't. The ritual was proposed, refined, and adopted in the same session.

## What was affected

- New: `gielinor/spellbook/rituals/close-session.md`.
- Edited: `gielinor/CLAUDE.md` — added "How to close a session" section.
- Pending (deferred — not in this entry's scope): `gielinor/meta/drafts-mechanics.md` should add close-session as a fourth draft-surfacing event (alongside `/drafts`, bankstanding, blocking action). Principal kept `meta/` user-only; this edit is pending principal action.

## Key design decisions

- **Per-player coverage.** The ritual scans **all** players' `quest-log/in-progress/` at close, not just the active one — mid-session player switches can leave the previous player's state mid-flight.
- **SNNN — global session counter, prefixed before date.** Format `S{NNN}_{YYYY-MM-DD}_{slug}.md`. Globally numbered across all players (gives chronological session history regardless of who was active). Assigned at first-close of a quest; preserved across subsequent closes (SNNN = birth-session ID, not last-touch).
- **In-progress quest-log entry as rolling state, not a separate `respawn.md`-style file.** Gielinor's per-player model would have duplicated state into a second file. Reuse the substrate already maintained per-turn.
- **Commit every session.** Authorized inside the ritual; standing "always ask before committing" rule (`~/.claude/CLAUDE.md`) is overridden inside this step, not outside.

## Comparison to dev-brain

Dev-brain's `developer-braindead/spellbook/session-close.md` is single-track (no players, one project, one rolling `respawn.md`). Gielinor's variant is multi-player and uses the quest-log entry itself as the rolling state. The two share: SNNN naming, commit discipline, "don't push," "don't `--no-verify`."

## Supersedes / superseded by

First-of-its-kind entry. No supersede chain.
