---
name: quest-log-opening-when-work-is-in-additional-working-dir
description: When a session's substantive work is in an additional working directory, the gielinor quest-log entry still needs to be opened on turn 1 — the externality of the work makes the discipline gap more important, not less.
metadata:
  type: examine
---

# Quest-log opening when substantive work is in an additional working dir

## Observation

2026-05-21 (S024): The session opened with `hey jebrim` at message start. Jebrim activated cleanly per the address rule. All substantive work for the next ~15 turns landed in the **additional working directory** (`bi-analytics-main/NFE/projects/3_shipping_data_mart/shipping-agent/`) — edits to `how_to.md`, the new `build_inline_chart.py`, four iterations on scope and narration rules. Zero writes happened in `gielinor/`. The session-log discipline gap (per `meta/death-and-spawn.md` — "every turn appends to `quest-log/in-progress/` of the active player") was invisible until T11 when the principal asked "do you have any quests open and stuff?". By then the lapse had run the whole session.

## What went wrong

The default heuristic for "should I open a quest-log entry" appears to be: *am I about to write anything to gielinor?* If yes, open one. If no, skip. That heuristic fails exactly when the substantive work lands in an additional working directory — which is *more* of a reason to open a gielinor entry, not less, because the external work otherwise leaves no trace on the brain side at all.

The crash-recovery model assumes the quest-log entry is the source of truth for what's in flight. A 15-turn session of edits to an external repo with no gielinor entry means: a crash mid-session would surface nothing on respawn. The next session would have no idea this session ran.

## Rule (for future Jebrim sessions)

On the **first turn** of a Jebrim session, open a quest-log entry in `players/jebrim/quest-log/in-progress/` — regardless of where the substantive work will land. The trigger is "Jebrim activated," not "Jebrim about to write to gielinor."

Edge case: if the session turns out to be a one-shot read-only Q&A (no work at all), the entry remains short but still gets opened — it captures that the session happened, which is itself recoverable signal. The empty-entry cost is one file; the missed-entry cost is the entire session falling off the recoverable record.

## How to apply

- **Trigger:** address-at-start activates a player → open the entry on turn 1.
- **Filename:** can use `OPEN_YYYY-MM-DD_<slug>.md` (pre-SNNN) and let close-session rename to `S{NNN}_...` per the SNNN rule.
- **Content on turn 1:** trigger statement + scope sketch. Turn log appends from there.
- **Do not wait until "work crystallizes" to open.** The whole point is to log work-in-progress.

## Why this matters

Quest-log entries are the only durable trace of session activity for content that doesn't land in canonical layers. The brain's recoverability model assumes the entry exists; the lapse breaks that assumption silently.

## Anchor

S024 session, T11. Principal cued "do you have any quest open and stuff?" — surfacing the gap after 15 unlogged turns of shipping-agent rule revisions.
