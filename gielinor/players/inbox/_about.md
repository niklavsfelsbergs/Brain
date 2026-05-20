# inbox/ — unscoped writes holding pen

**What this is.** A flat folder for captures that the agent made without yet knowing which player they belong to. Triage happens during bankstanding.

## When to write here

- A capture happens during an **unscoped session** (no player active).
- A capture happens in a session where the active player is clearly wrong for it, *and* the right player isn't obvious.
- A capture's player assignment is genuinely ambiguous — could be Zezima or Jebrim, depending on framing.

Default bias: when in doubt during an active-player session, write to the active player's `bank/notes/` and let bankstanding re-route if needed. Use the inbox sparingly — it's the overflow path, not the default.

## Format

One file per capture. Filename: `YYYY-MM-DD_<slug>.md`. Use the date of the capture, not of the triage.

Contents: free-form. Just write what was observed and what's unclear about its scope.

## Triage during bankstanding

For each file:

1. Read it. Decide which player it belongs to (or that it belongs to no one).
2. If a player fits → move to that player's `bank/notes/` (or `examine/drafts/` or `keepsake/proposals/`, depending on the nature of the capture).
3. If no player fits but it's worth keeping → ask the principal whether to spawn a new player or whether the capture is actually a global observation.
4. If it's stale or has no continued value → archive to `players/inbox/archive/`. Never delete.

## Age limit

Items in `inbox/` get a soft max age of **~4 weeks**. Bankstanding surfaces anything older than that for explicit keep-or-drop. The bias is: if it's sat for a month without anyone knowing where to file it, the answer is probably "drop it" — but the principal makes that call, not the agent.

## Related

- `spellbook/rituals/bankstanding.md` for the triage step.
- `players/_about.md` for the discipline around not creating speculative players just to absorb inbox items.
