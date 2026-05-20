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

4. **Read `examine/confirmed/current.md` (global).** The agent-system self-model.

5. **Read `niksis8/confirmed/current.md` (global).** Universal facts about Niklavs.

6. **Read `lorebook/assumptions.md`.** The working assumptions the system is built on. Knowing what is currently *assumed* prevents the agent from acting as if those assumptions were proven.

7. **If a player is active, scope them in:**

   a. Read `players/<name>/CLAUDE.md`. (Claude Code's hierarchy may handle this automatically if the session was opened in the player's folder; if running from the brain root, the agent reads it explicitly.)

   b. Read `players/<name>/_about.md` — who this character is.

   c. Read `players/<name>/persona.md` — how they speak and act.

   d. Read `players/<name>/keepsake/current.md`.

   e. Read `players/<name>/examine/confirmed/current.md`.

   f. Read `players/<name>/niksis8_character/confirmed/current.md`.

   g. Check `players/<name>/quest-log/in-progress/`. If any file is present, run the **reconciliation prompt** (below) before accepting new input.

8. **If dwarf mode:** skip the unfinished-business check. Read the task brief from the principal. Operate within the dwarf write boundary (`meta/modes.md`). Write findings to the inherited player's `quest-log/in-progress/`; return a summary to the principal.

9. **Cued retrieval during the session.** Other layers are not preloaded — `bank/`, `spellbook/skills/`, the rest of `lorebook/`. The agent reads them as the task requires.

10. **Acknowledge readiness. Await input.** Briefly — name the active player and confirm any in-progress state. Don't recite the whole load.

## Reconciliation prompt

When `quest-log/in-progress/` contains a file at session start, an in-flight session was interrupted. Procedure:

1. Read the most recent in-progress entry.
2. Surface to the principal: what was being worked on, what action was last logged as `pending`, what the last completed turn said.
3. Ask: **resume**, **abandon** (move to `archive/in-progress/`, never delete), or **mark complete by hand** (principal edits and moves to `completed/`).
4. Do not start new work until the in-progress state is resolved.

The exact prompt wording is deferred to real use.

## Mini-respawn — mid-session player switch

Triggered when a later message addresses a **different** player than the currently active one (or addresses `unscoped` when scoped, or names a player when unscoped). The address rules in `CLAUDE.md` (*Player invocation by address*) govern detection.

1. Note in the *outgoing* player's `quest-log/in-progress/` that the session is handing off — record what's in flight, who's incoming, and the message that triggered the switch.
2. Re-run step 7 of the load order for the new player (read their `CLAUDE.md`, `_about.md`, `persona.md`, `keepsake/current.md`, `examine/confirmed/current.md`, `niksis8_character/confirmed/current.md`).
3. Check the new player's `quest-log/in-progress/`. If unfinished business → reconciliation prompt. If dwarf mode → task brief from principal.
4. Acknowledge briefly and continue with the new player as active.

Global identity (`examine/`, `niksis8/`, `keepsake/`, `lorebook/assumptions.md`) is already loaded from the original respawn — do not re-read.

A switch to **unscoped** mode runs the same hand-off note in the outgoing player's quest-log, then skips step 2 (no player-specific load) and proceeds.

## Per-turn discipline

After respawn, the agent maintains the in-progress quest-log entry **every turn**:

- Append a brief narrative line for what happened this turn.
- For any external action: log `pending` before the call, update to `completed` or `failed` after.

This is the crash-recovery substrate. Without it, death-as-crash recovery is impossible. See `meta/death-and-spawn.md`.

## Related

- `bankstanding.md` for the periodic reorganization ritual.
- `meta/death-and-spawn.md` for what survives a crash or reset.
- `meta/modes.md` for principal vs dwarf behavior in step 8.
- `lorebook/decisions/` for the choices that shaped this load order.
