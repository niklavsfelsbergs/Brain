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

One file per **quest** (not per session). A quest is a unit of work with a deliverable; a session is one continuous principal-agent interaction. A single quest may span multiple sessions — see S014_*shipping-data-mart-ttyd* for the proof case (S014/S015/S016 all advanced the same quest file). Filename: `SNNN_YYYY-MM-DD_<slug>.md` (the SNNN is the session the quest opened in; the file persists past that session).

## Discipline (critical for crash recovery)

- A quest log appends to `in-progress/` **every turn**, across however many sessions the quest spans.
- Every external action logs as `pending` before execution, updated to `completed` or `failed` after.
- On **quest close** (deliverable shipped, or principal cues done) — *not on session close* — the file moves from `in-progress/` to `completed/`. Session close leaves quest files in place; they're picked back up next session.
- On crash, file stays in `in-progress/` and is the recovery target.

See `gielinor/meta/death-and-spawn.md`.

## What goes in a quest entry

- Narrative: the ask, the work done, the answer delivered, turn-by-turn.
- Decisions made in-flight (the locked-in answers from clarification rounds).
- Deliverables produced or queries run, with their results or output paths.
- Hand-offs to other players / dwarves.
- Pending/completed/failed action markers.

## What does not go in a quest entry

- **Resume state** — the `Where we are` / `Next concrete step` / "what to do next session" content lives in `inventory/<active-quest>.md`, not at the top of the quest log. Close-session writes it to inventory; respawn reads it back. See `gielinor/meta/layer-routing.md`.
- Reference knowledge — `bank/drafts/notes/`. Sessions may *produce* bankable knowledge; alching proposes the transfer once the quest closes.
- Self-observations — `examine/drafts/`.
- Procedures / methodologies — `spellbook/drafts/skills/`.

## Write rules

Auto-write. See `gielinor/meta/write-rules.md`.

## Related

- `gielinor/spellbook/rituals/respawn.md` for in-progress recovery.
- `gielinor/spellbook/rituals/bankstanding.md` for graduating session insights to bank.
