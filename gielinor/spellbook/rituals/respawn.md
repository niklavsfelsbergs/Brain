# respawn — session-start ritual

The procedure the agent runs at the start of every session, and as a **mini-respawn** when the principal switches players mid-session.

This file is the canonical ritual. The agent performs it; the principal owns its definition.

## Why this ritual exists

Context is finite and recall degrades as it fills (context rot). Respawn answers: of everything in the brain, what *must* be loaded before the agent can act, and what can wait for cued retrieval?

The load order below front-loads only the durable, in-force, identity-shaped material. Reference material is left for cued retrieval during the session.

## Load order — session start

1. **Body — handled by Claude Code.** Master `CLAUDE.md` and `CLAUDE.local.md` are read automatically by Claude Code at session start. They `@import` from `meta/`, so the rulebook is in context before the agent does anything else. Confirm the imports landed; if they didn't, surface a warning and stop.

2. **Player is set by address at message start — do not prompt.** Parse the first user message for the invocation pattern (see `CLAUDE.md` → *Player invocation by address*):
   - `Hey {name}, ...` at message start → that player is active.
   - `Hey unscoped, ...` → unscoped mode.
   - No address on the first message → start **unscoped** by default.
   
   Do not ask "which player?" — the address is the authoritative signal. A misspelled or partial address does **not** trigger a switch; treat it as no address.

3. **Read `keepsake/current.md` (global).** Full read. These are the always-surface items; they must be in working context.

4. **Read every `.md` file in `examine/confirmed/` (global).** The agent-system self-model. Each file is an atomic confirmed observation; all are in force. `current.md`, if present, is an optional hand-curated executive summary — read alongside the atomic entries, not in place of them.

5. **Read every `.md` file in `niksis8/confirmed/` (global).** Universal facts about Niklavs. Same shape — atomic confirmed observations, `current.md` optional executive summary.

6. **If a player is active, scope them in:**

   a. Read `players/<name>/CLAUDE.md`. (Claude Code's hierarchy may handle this automatically if the session was opened in the player's folder; if running from the brain root, the agent reads it explicitly.)

   b. Read `players/<name>/_about.md` — who this character is.

   c. Read `players/<name>/persona.md` — how they speak and act.

   d. Read `players/<name>/keepsake/current.md`.

   e. Read every `.md` file in `players/<name>/examine/confirmed/`. Atomic confirmed observations; `current.md` optional executive summary.

   f. Read every `.md` file in `players/<name>/niksis8_character/confirmed/`. Same shape.

   g. Check `players/<name>/quest-log/in-progress/`. If any file is present, the player has in-flight quests. Run the **reconciliation prompt** (below) before accepting new input.

   h. **Sibling detection + comms read.** Per [[D-024]] (dev brain). Two ground-truth sources, both required:

      - **Sidecar manifest** at `~/.claude/status/*.json`. Filter for `state ≠ ended AND last_event_ts < 5 minutes AND actor ∈ {jebrim, zezima, guthix, …}`. Each match is a confirmed-live sibling session — own `sid8` excluded.
      - **`gielinor/comms/active.md`**. Read the tail. Cross-reference each live `sid8` from the sidecar against the log: any live id with an `OPEN` (or `UPDATE`) but no matching `CLOSING` is in-flight; any id with a stale `OPEN` and no recent sidecar entry is a candidate for `ABANDONED` synthesis (surface, don't auto-synthesize).

      Surface to the principal before posting OPEN if anything looks ambiguous — three fresh respawns within seconds can all see "no siblings" before any posts.

   i. **Read `players/<name>/inventory/*__<sid8>.md` and `*-resume.md`** — the resume foreground. Per [[D-024]]:

      - **Prefer `<topic>__<own-sid8>.md` if present** — this session's own prior inventory state. Read it directly.
      - **Otherwise list all `<topic>__<sid8>.md` files** for matching topics. Cross-reference each `sid8` against the comms log + sidecar manifest from step h:
        - Clean `CLOSING` in comms + sidecar `ended` → recoverable; safe to read and adopt.
        - No `CLOSING` and sidecar shows session ended/stale → crashed; surface the candidate for the principal to authorize adoption.
        - Live sibling per step h → **don't touch** their inventory. The other session owns it.
      - **Legacy unsuffixed `<topic>-resume.md` files** (pre-[[D-024]]) are treated as own-session state: read directly. The next close-session pass writes the suffixed form going forward.

      Each file carries the `Where we are` / `Next concrete step` / `Files to read first` state populated by close-session step 3. **This is what the reconciliation prompt surfaces** — not the quest-log file's body, which is the turn-by-turn history. If inventory has no resume files but `quest-log/in-progress/` is non-empty, surface the gap (close-session step 3 didn't populate inventory) and read the quest log directly as a fallback. Note the gap for the next close-session pass.

   j. **Post `OPEN` entry to `gielinor/comms/active.md`.** Per [[D-024]] and `comms/_about.md`. Header `[YYYY-MM-DD HH:MM] <player>-<sid8> OPEN` (use Guthix in consultation/bankstanding mode). Body lines as needed:

      - `Targets:` — what this session intends to work on, named by inventory topic or quest slug.
      - `Steering clear of:` — surfaces other live siblings have claimed (from step h's read) or shared globals this session won't touch.
      - `Open to handoff:` — items the principal might pick up from another terminal.

      Skip the post entirely only if the session is **trivially scoped** (e.g., a one-off "show me file X" with no writes). When in doubt, post — the cost is one append.

   k. **Alching threshold check.** Read `players/<name>/last-alched.md` and count drafts across the player's `examine/drafts/`, `niksis8_character/drafts/`, `bank/drafts/notes/`, `spellbook/drafts/skills/`, `keepsake/proposals/`. If any threshold in `spellbook/rituals/alching.md` § *Recommendation thresholds* is breached, surface a one-line recommendation per `meta/communication-protocol.md` § *Internal rituals stay silent* (the threshold-recommendation exception). The principal decides whether to alch now or later.

7. **If dwarf mode:** skip the unfinished-business check. Read the task brief from the principal. Operate within the dwarf write boundary (`meta/modes.md`). Write findings to the inherited player's `quest-log/in-progress/`; return a summary to the principal.

8. **Cued retrieval during the session.** Other layers are not preloaded — `bank/`, `spellbook/skills/`, `lorebook/`. The agent reads them as the task requires.

9. **Acknowledge readiness. Await input.** Briefly — name the active player, confirm any in-progress state, surface the alching recommendation if step 6.i fired. Don't recite the whole load.

## Reconciliation prompt

When `quest-log/in-progress/` contains a file at session start, an in-flight quest exists. Procedure:

The resume foreground for each in-flight quest lives in `inventory/<quest-slug>-resume.md` — populated by `close-session.md` step 3. **This prompt reads from inventory, not the quest log.** The quest log carries history; the inventory resume file carries foreground.

1. Read each `inventory/*-resume.md` for the active player. (If none exist but `quest-log/in-progress/` is non-empty, fall back to reading the quest log itself — and surface that the resume state is missing, so the next close-session pass fixes it.)
2. **Surface to the principal — the resume foreground, not the history:**
   - The **quest title** (from the resume file's heading or the matching quest-log filename slug).
   - The **Where we are** section verbatim — current state across open threads.
   - The **Next concrete step** section verbatim — what next session is meant to do.
   - The **Files / paths to read first** list — so the principal sees the load plan.
   - The **last logged `pending` action**, if any — separate from the above; this is the crash-recovery signal. (This is still pulled from the quest log itself, where per-turn pending markers live.)

   Do not surface the per-turn narrative log. That's history; the inventory resume file is foreground. If multiple in-flight quests exist for the player, surface each in order — most-recently-touched first.
3. **Ask explicitly** — present the three options:
   - **Resume** — continue from where the session left off; assume the pending action did not complete.
   - **Abandon** — move the file to `quest-log/archive/in-progress/` (never delete) and start fresh.
   - **Reconcile the pending action externally first** — the principal checks whether the last `pending` action actually completed on the outside world (e.g., a file was written, a message was sent), then tells the agent to mark it `completed` or `failed` by hand before resuming.
4. **Do not auto-resume.** Do not start new work until the principal has chosen. Auto-resuming risks re-running an action that already completed and re-doubling its side effect.

See `meta/death-and-spawn.md` for the full crash-recovery model.

## Mini-respawn — mid-session player switch

Triggered when a later message addresses a **different** player than the currently active one (or addresses `unscoped` when scoped, or names a player when unscoped). The address rules in `CLAUDE.md` (*Player invocation by address*) govern detection.

**Precondition.** A hand-off note is only written if a player was activated *in this session*. If the session opened unscoped (or in dev-brain mode) and no player has been addressed since, there is no outgoing player and step 1 is skipped. Prior sessions' in-progress quests on disk are not this session's to mark — the reconciliation prompt (above) handles those at respawn.

1. **If an outgoing player exists this session**, append a brief hand-off note to their `quest-log/in-progress/` entry:
   - One line: today's date, the trigger message, the incoming mode/player.
   - Optionally, one line for any pending action this session put in flight.
   - **Do not re-read or summarize the quest's existing content.** The hand-off note is a marker, not a recap. The quest's own "Next concrete step" section carries resume context for the next session that lands on it.
2. **Archive the outgoing actor's per-session intent file.** Move `brain/.claude/intent/<outgoing-actor>-<sid8>.txt` into `brain/.claude/intent/archive/` (preserving the filename). Leaving it in place means two intent files exist for the same `sid8`, which the switchboard's `_detect_actor` reads as ambiguous → `actor: unknown` in the sidebar. The status-sidecar will catch it on the next `UserPromptSubmit` anyway, but moving it here closes the gap within the same turn.
3. **Comms hand-off.** If the outgoing actor posted an `OPEN` (or `UPDATE`) to `gielinor/comms/active.md` earlier this session and has not yet posted a `CLOSING`, post a `CLOSING` under their identity now — short body, one or two lines on what was completed and what's being handed off. Then re-run step 6.h–6.j of the load order for the new actor (sibling detection + comms read + new `OPEN`). The sibling detection re-read is cheap and catches any sibling who landed in the interval since the original respawn.
4. Re-run step 6 of the load order for the new player (read their `CLAUDE.md`, `_about.md`, `persona.md`, `keepsake/current.md`, `examine/confirmed/current.md`, `niksis8_character/confirmed/current.md`).
5. Check the new player's `quest-log/in-progress/`. If unfinished business → reconciliation prompt. If dwarf mode → task brief from principal.
6. Acknowledge briefly and continue with the new player as active.

Global identity (`examine/`, `niksis8/`, `keepsake/`) is already loaded from the original respawn — do not re-read.

A switch to **unscoped** mode runs the same hand-off note in the outgoing player's quest-log, then skips step 2 (no player-specific load) and proceeds.

## Per-turn discipline

After respawn, the agent maintains the in-progress quest-log entry **every turn**:

- Append a brief narrative line for what happened this turn.
- For any external action: log `pending` before the call, update to `completed` or `failed` after.

This is the crash-recovery substrate. Without it, death-as-crash recovery is impossible. See `meta/death-and-spawn.md`.

## Related

- `bankstanding.md` for the periodic reorganization ritual.
- `meta/death-and-spawn.md` for what survives a crash or reset.
- `meta/modes.md` for principal vs dwarf behavior in step 7, and the three session modes (player/unscoped/bankstanding).
