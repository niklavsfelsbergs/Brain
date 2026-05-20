# Jebrim — quest-log/

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

One file per session. Filename: `YYYY-MM-DD_<slug>.md`.

## Discipline (critical for crash recovery)

- A session log appends to `in-progress/` **every turn**.
- Every external action logs as `pending` before execution, updated to `completed` or `failed` after.
- On clean session end, file moves from `in-progress/` to `completed/`.
- On crash, file stays in `in-progress/` and is the recovery target.

See `gielinor/meta/death-and-spawn.md`.

## What goes in a session entry

- Narrative: the ask, the work done, the answer delivered.
- Deliverables produced or queries run, with their results or output paths.
- Open threads, hand-offs, follow-ups.
- Pending/completed/failed action markers.

## What does not go in a session entry

- Reference knowledge — `bank/`. Sessions may *produce* bankable knowledge; bankstanding proposes the transfer.
- Self-observations — `examine/drafts/`.

## Write rules

Auto-write. See `gielinor/meta/write-rules.md`.

## Related

- `gielinor/spellbook/rituals/respawn.md` for in-progress recovery.
- `gielinor/spellbook/rituals/bankstanding.md` for graduating session insights to bank.
