# Zezima — quest-log/

**Cognitive role.** Episodic memory. What happened in each session, in narrative form.

**Metaphor.** A quest journal: time-bound narrative arcs, started and completed, sometimes paused.

## Structure

```
quest-log/
  _about.md
  in-progress/          # active sessions; appended every turn
  completed/            # finished session entries
  archive/              # abandoned in-progress entries, plus aged completed entries
```

One file per **quest** (not per session). A quest is a unit of reflection or reading with a thread; a session is one continuous principal-agent interaction. A single quest may span multiple sessions — a long reflection on a particular book, a slow synthesis across weeks, etc. Filename: `SNNN_YYYY-MM-DD_<slug>.md` (the SNNN is the session the quest opened in; the file persists past that session).

## Discipline (critical for crash recovery)

- A quest log appends to `in-progress/` **every turn**, across however many sessions the quest spans.
- Every external action logs as `pending` before execution, updated to `completed` or `failed` after.
- On **quest close** (the thread reaches a resting point, or the principal signals done) — *not on session close* — the file moves from `in-progress/` to `completed/`. Session close leaves quest files in place; they're picked back up next session.
- On crash, the file stays in `in-progress/` and is the recovery target — the respawn ritual surfaces it.

See `gielinor/meta/death-and-spawn.md` for the full crash-recovery story.

## What goes in a quest entry

- Narrative: what the principal asked, what was reflected on, what was said.
- Decisions made within the session.
- Open threads, hand-offs, follow-ups.
- Pending/completed/failed action markers.

## What does not go in a quest entry

- **Resume state** — the "where we are" / "next time, pick back up here" content lives in `inventory/<active-quest>.md`, not at the top of the quest log. Close-session writes it; respawn reads it back. See `gielinor/meta/layer-routing.md`.
- Reference knowledge — that's `bank/drafts/notes/`. A session may *produce* knowledge worth banking; alching proposes it once the quest closes.
- Self-observations — that's `examine/drafts/`.
- Procedures / methodologies — that's `spellbook/drafts/skills/`.

## Write rules

Auto-write. The session logs itself. See `gielinor/meta/write-rules.md`.

## Related

- `gielinor/spellbook/rituals/respawn.md` for how in-progress entries are recovered.
- `gielinor/spellbook/rituals/bankstanding.md` for graduating session insights to bank.
