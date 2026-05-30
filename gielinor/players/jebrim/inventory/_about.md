# Jebrim — inventory/

**Cognitive role.** Working memory. What Jebrim is carrying right now — volatile, session-scoped, lost on death. **Primary resume surface** — what gets read at respawn to pick up where the last session left off.

**Metaphor.** The 28 inventory slots in RuneScape.

## What goes here

- **Resume state per active quest** — the "where we are," "next concrete step," open task list, decisions to load verbatim into next session's context. One file per in-flight quest, named to match the quest (e.g., `S014-ttyd-resume.md`).
- Open threads carried across turns within a session.
- Today's working state — the specific report being built, the stakeholder waiting for an answer, the query whose output is being inspected.
- Working drafts of an analysis that isn't ready to land in `bank/drafts/notes/` yet.

## What does not go here

- Anything that should survive a reset. (Use `bank/` or get it confirmed.)
- Narrative session content — turn log, decisions made in-flight. (Use `quest-log/`.)
- Knowledge about a project, query, or stakeholder. (Use `bank/drafts/notes/`.)

## Structure

Flat. One file per active piece of working memory. Filenames descriptive — for resume files, the convention `<quest-slug>-resume.md` makes them findable at respawn.

```
inventory/
  _about.md
  <quest-slug>-resume.md         # one per in-flight quest
  <free-form files as needed>
```

## Freshness header

Resume files (`<quest-slug>-resume__<sid8>.md`) open with a small machine-readable header so a future respawn can tell whether the state still fits the task it's resuming — the gielinor port of Khaan's context-hash freshness primitive (dev brain S116/S118; pairs with the [[D-024_scope-git-commits-with-pathspecs-parallel-sessions]] staleness model). Four fields, **no cryptographic hash**:

```
---
quest: SNNN_<slug>      # the quest-log entry this resume serves (or topic slug if multi-session)
sid8: <sid8>            # session that last wrote it
ts: YYYY-MM-DD HH:MM    # last-write time
open_dep: none          # or a one-line name of what blocks closing (player-declared)
---
```

- **The fields ARE the identity check.** `quest` + `sid8` answer "is this state for the task I'm resuming, and which session wrote it"; `ts` answers "how old." A `sha256(prompt)` stamp was deliberately rejected — the prompt changes every turn, so a content-hash reads stale immediately and false-trips every respawn (the brittleness that held Khaan item G, dev brain S116).
- **Read, not enforced.** Respawn's reconciliation surfaces age + any `quest`/`sid8` mismatch as a *note* ("this resume is N days old / tagged for a different quest — stale?"); it never hard-blocks a resume. The principal decides.
- **`open_dep` is the graduation discriminator the player owns.** `none` declares the quest carries no named open dependency; otherwise name the blocker in one line (e.g. `open_dep: awaiting principal sign-off on the 2 ritual one-liners`). Close-session's stale-done scan reads it ([[D-029_auto-graduate-unambiguous-complete-ready-quests|D-029]]): `open_dep: none` on a shipped + committed quest → **unambiguous, graduates silently** this close; a named dep → **ambiguous, held for veto/approval**; the field absent (legacy resumes) → the agent falls back to inferring from the body. The point (§R.2, dev brain 2026-05-30): the player alone cheaply knows whether a dep is open, so a one-line declaration beats the agent inferring it from prose — and `Next concrete step: none` is *not* the same as `no open dependency` (work can be done while sign-off is still pending).
- Written by `close-session.md` step 3; surfaced by `respawn.md`'s reconciliation prompt; presence on this session's own resume verified by `close_check.py --ritual player`.

## Write rules

Auto-write. Volatile by design. See `gielinor/meta/write-rules.md` and `gielinor/meta/death-and-spawn.md`.

## Discipline

- **Close-session ritual writes resume state here, not into the quest log.** Per `gielinor/meta/layer-routing.md`. If a resume block ends up at the top of a quest log, route it to inventory instead.
- **Respawn ritual reads `inventory/*` as the resume foreground.** The first thing the agent surfaces at session start is the inventory state for in-flight quests.
- If something carries across more than two sessions and isn't quest-specific, it probably belongs in `bank/`, not inventory. Promote it.
- If something hasn't been touched in a session, drop it (the agent isn't actually carrying it).
