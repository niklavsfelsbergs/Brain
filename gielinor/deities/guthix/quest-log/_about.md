# guthix/quest-log/

**Cognitive role.** Episodic memory at system scope. One entry per bankstanding ritual run.

**Distinction from a player's quest-log.** A player's quest-log tracks sessions advancing a player's quests. Guthix's quest-log tracks bankstanding *passes* — each is a ritual run, regardless of which session cued it. Numbering uses **B-NNN** (for *bankstanding*) to keep it distinct from any player's S-NNN.

## Structure

```
quest-log/
  _about.md
  in-progress/          # active ritual; appended every turn while Guthix is in residence
  completed/            # finished passes
  archive/              # abandoned in-progress, plus aged completed
```

## Filename pattern

`B-NNN_YYYY-MM-DD_<slug>.md` — examples:

- `B-001_2026-05-22_first-bankstanding.md`
- `B-002_2026-06-05_post-S031-drift-sweep.md`

The B-NNN counter belongs to Guthix and increments monotonically across all bankstanding passes. A single bankstanding pass that spans multiple sessions stays in one file.

## What an entry records

- **Phase trace.** What ran (Phase 0 alching for which players, Phase 1+ global synthesis).
- **What was covered.** Which layers were read, which players were sampled, what cross-references were followed.
- **What was proposed.** Links to drafts created — `[[bank/drafts/notes/...]]`, `[[lorebook/drafts/...]]`, `[[keepsake/proposals/...]]`. Guthix's quest-log is the index back into his own work.
- **What was flagged for follow-up.** Things he noticed but didn't act on — handed forward to the next pass or to a player.
- **Voice.** Measured, balanced, system-scope. Past tense in completed/; present tense in in-progress/.

## Discipline

- **Append every turn while in residence.** Bankstanding spans many turns; the in-progress file grows turn by turn. Crash recovery depends on this.
- **Move to completed/ when the ritual closes.** Triggered by the agent flipping intent away from `guthix.txt` (which fires `despawn-guthix` in the hook).
- **Archive abandoned passes.** If a bankstanding session crashes without clean despawn and the next-pass-Guthix decides not to resume, move the in-progress entry to `archive/in-progress/`.

## Related

- `gielinor/spellbook/rituals/bankstanding.md` — the ritual procedure.
- `gielinor/meta/death-and-spawn.md` — crash recovery discipline.
- `gielinor/meta/archive-discipline.md` — what archive moves preserve.
