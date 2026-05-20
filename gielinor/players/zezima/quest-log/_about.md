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

One file per session. Filename: `YYYY-MM-DD_<slug>.md`. Date is the session start date.

## Discipline (critical for crash recovery)

- A session log appends to `in-progress/` **every turn**, not at session end.
- Every external action logs as `pending` before execution, updated to `completed` or `failed` after.
- On clean session end, the file moves from `in-progress/` to `completed/`.
- On crash, the file stays in `in-progress/` and is the recovery target — the respawn ritual surfaces it.

See `gielinor/meta/death-and-spawn.md` for the full crash-recovery story.

## What goes in a session entry

- Narrative: what the principal asked, what was done, what was said.
- Decisions made within the session.
- Open threads, hand-offs, follow-ups.
- Pending/completed/failed action markers.

## What does not go in a session entry

- Reference knowledge — that's `bank/`. (A session may *produce* knowledge worth banking; the bankstanding ritual proposes it later.)
- Self-observations — that's `examine/drafts/`.

## Write rules

Auto-write. The session logs itself. See `gielinor/meta/write-rules.md`.

## Related

- `gielinor/spellbook/rituals/respawn.md` for how in-progress entries are recovered.
- `gielinor/spellbook/rituals/bankstanding.md` for graduating session insights to bank.
