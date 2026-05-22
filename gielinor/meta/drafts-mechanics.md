# Drafts mechanics

For `examine/`, `niksis8/`, `niksis8_character/` (and by extension for `lorebook/confirmed/` and `keepsake/` pins, with slightly different folder names).

## Flow

1. **Capture.** The agent writes an observation as a file in `drafts/` whenever it notices something worth recording — about itself, about the user, about a player's relationship to the user.
2. **Review.** The principal runs `/drafts` to surface pending drafts grouped by layer, one-line summary each.
3. **Decision.** Per draft, the principal:
   - **Approves** → file moves to `confirmed/`.
   - **Rejects** → file moves to `rejected/` with a note. Kept, not deleted; patterns in rejections matter.
   - **Edits and approves** → the principal rewrites, then moves.

For `keepsake/` the equivalent is `keepsake/proposals/` → pinning into `current.md` (the proposal file moves to `keepsake/archive/proposals/` once pinned, so the original proposal is preserved).

For `lorebook/confirmed/` the equivalent is `lorebook/drafts/` → `lorebook/confirmed/D-NNN_<slug>.md`.

## The observation rule

Drafts must be **observation-backed, not aspirational.**

- **Bad:** "I should be more careful about deletes."
- **Good:** "2026-05-12: I proposed deleting the wrong file because I matched on filename without checking path. From now on, confirm full path before any delete operation."

Specificity is what makes self-knowledge actionable. A draft that doesn't cite an observation isn't ready; rewrite it or drop it.

The same rule applies to `niksis8/` drafts about the user. Not "Niklavs prefers tight responses" with no anchor — instead, "Niklavs corrected three responses in S007 for being too long; preference is short responses, tolerate length only when the underlying task is long." Memory beats inference.

## When the agent drafts vs lets it pass

Deferred to real use. The exact threshold ("when should I bother writing this down") will emerge from seeing what drafts get approved and what gets rejected. Early-phase bias: **draft when in doubt.** A rejection is cheap; a missed observation is invisible.

## Surface discipline

**The agent does not push drafts at session start.** Drafts surface only when:

- the principal runs `/drafts`,
- bankstanding is happening, or
- a draft is *blocking* an action (e.g., the agent wants to act on a self-observation that hasn't been confirmed yet — it surfaces the draft and asks for a ruling).

The respawn ritual reads every `.md` in `confirmed/` — atomic confirmed entries plus the optional `current.md` executive summary. Drafts are not read at respawn (see `spellbook/rituals/respawn.md` steps 4, 5, 6.e, 6.f).

## File naming

Use slug filenames with a date prefix so chronological order is preserved and the file is searchable: `2026-05-20-observation-about-deletes.md`. Date is when the observation happened, not when it was drafted.

## `/drafts` command

Implemented as a slash command at `.claude/commands/drafts.md`, backed by the ritual at `spellbook/rituals/drafts-triage.md`. The lightweight promotion gate — invocable any time, scoped to the active player's drafts + global identity drafts. Excludes Guthix layers (bankstanding territory) and other players (their own alching).

Behavior in short:

1. Survey all pending drafts in scope, numbered consecutively across layers.
2. Surface each with one-line claim, anchor, and agent recommendation (y/n/edit + reason).
3. Principal triages in batch (`1y 2y 3n 4: edit "..."`); generic affirmation (`yes`, `go`) resolves to "approve every `y` recommendation."
4. Agent executes via `git mv` (Bash bypasses the `confirmed/` write hook for player-owned moves); surfaces user-only layers (keepsake pins, lorebook decisions) for principal-side writes.
5. Does not update `last-alched.md` — this is partial-promotion, not full alching.

See `spellbook/rituals/drafts-triage.md` for the full procedure including scope-by-mode, recommendation rubric, and the verdict-execution table.

## Related

- `archive-discipline.md` for what happens to rejected drafts and superseded confirmed entries.
- `write-rules.md` for the full per-layer picture.
- `lorebook/confirmed/` for the founding choice to gate identity behind drafts.
