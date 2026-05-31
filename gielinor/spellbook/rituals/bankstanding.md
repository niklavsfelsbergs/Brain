# bankstanding — periodic active reorganization

The procedure the agent runs to tend its own brain. Active, not unconscious — the agent steps away from external work and turns inward.

Named for the RuneScape activity of standing in the bank to reorganize inventory and stored items between trips.

## Bankstanding is its own mode

Bankstanding is **a distinct session mode**, separate from player mode, unscoped mode, consultation, and alching. While bankstanding is running, the agent is not Zezima, not Jebrim, not a no-player ad-hoc operator — it is **the system tending its own brain.** The active persona is "gielinor reflecting on itself," not any character.

Five session modes exist:

- **Player mode** — a character (Zezima, Jebrim, future) is active, bounded to that character's domain.
- **Unscoped mode** — narrow: a session that has truly had no prompt yet. The wisp holds the floor until something gets asked. See `meta/modes.md`.
- **Consultation mode** — Guthix is in residence for general questions, cross-cutting lookups, system-shaped reflection. Reads everything; writes only to his own deity layers; chat-only by default. The default for any non-player-scoped question.
- **Alching mode** — per-player tending ritual; reach restricted to the active player's content. See `spellbook/rituals/alching.md`.
- **Bankstanding mode** — system-level cross-cutting ritual; reach is global, with read access across all players. See below.

Consultation and bankstanding share an actor (Guthix), a voice, and a sprite — they differ in write authority and procedural shape. A consultation can flip into bankstanding on explicit principal cue when the conversation surfaces enough work to warrant the ritual.

See `meta/modes.md` for the full picture, including how this axis is orthogonal to principal-vs-dwarf.

## Reach — strictly global

Bankstanding is the **strictly global** ritual. Its primary work happens in the global layers; per-player tending is alching's job.

- **Writes:** proposes writes only to global layers — `examine/`, `niksis8/`, `keepsake/`, `lorebook/`, and triage of `players/inbox/`. Subject to the standard draft-approval rules in `meta/write-rules.md`.
- **Reads:** reads everything — all global layers and all per-player content. The read-across-all-players capability exists specifically so bankstanding can detect cross-cutting patterns and propose graduations to the global layer.
- **Does not write to per-player layers.** If a player's content needs tending, bankstanding flags it (and may recommend alching for that player); it does not perform the per-player work itself.

## Why this ritual exists

The brain accumulates. Drafts pile up. Notes go stale. Keepsake creeps past its size budget. Inbox items linger past their expiration. Per-player observations recur across players in ways that should graduate to the global layer. Episodic memory accrues without ever crystallizing into semantic memory.

Without periodic reorganization, the system slowly loses coherence — and worse, slowly loses retrieval quality, because relevant material gets buried in stale material.

Bankstanding is the principal-supervised cleanup that keeps the system retrievable.

## When it runs

Phase 1: **on principal cue.** The principal asks ("let's bankstand"). The agent doesn't trigger it autonomously yet.

Auto-triggers (scheduled, on size-budget threshold, on draft-count threshold) are deferred to real use — we'll figure out the right cadence after running the system for a while.

## The procedure

The agent works through each item below in order. **Propose, never silently destroy.** Especially in the early phase, surface every move to the principal for confirmation rather than auto-executing.

**Switchboard marker.** Bankstanding flags the session so the board renders a `bankstanding` flavor chip instead of a bare `BUSY` (mirrors alching's marker; see `alching.md` and `meta/communication-protocol.md` → *Mode marker sidecar*):

- **On entry** (before Phase 0): write `bankstanding` to `.claude/intent/<sid8>.mode` at the brain root (`<sid8>` = first 8 chars of `CLAUDE_CODE_SESSION_ID`).
- **During Phase 0**: each per-player alching sub-pass writes `alching` per `alching.md`; **on Phase 0 exit, restore `bankstanding`** so the chip reflects the ritual you're back in.
- **On close** (or if abandoned): overwrite with an empty line to clear it.

Switchboard-only — not architecturally enforced; a missing marker just means no chip.

### 0. Alch each changed player first

Before bankstanding's own work begins, walk the player roster. For each player, compare the most recent change in their namespace against `players/<name>/last-alched.md`.

**"Changes since last alching" — any of:**

- A new or modified file in `quest-log/in-progress/`, `quest-log/completed/`, or `quest-log/sessions/`.
- A new or modified file in `bank/notes/`.
- A new or modified file in `examine/drafts/`, `niksis8_character/drafts/`, or `keepsake/proposals/`.
- A modification to `inventory/` (volatile, but the mtime is the signal).

The comparison is file mtime vs the timestamp in `last-alched.md`. Any file newer than `last-alched.md` qualifies the player as changed.

**Per player:**

- **No changes since last alching** → skip silently. Move to next player.
- **Has changes, no in-progress quest** → switch to **alching mode** for that player and run the alching procedure (`spellbook/rituals/alching.md`) to completion. Standard alching: per-player scope, principal approves each draft, `last-alched.md` updated at the end.
- **Has changes but has an in-progress quest** → flag and ask the principal. Alching a player mid-quest is unusual; the in-progress work may not be "settled enough" to tend. Default: skip the player for this bankstanding round, log the skip in the post-check at step 6.

Once Phase 0 completes for the last changed player (or completes empty, if no player had changes), transition back to **bankstanding mode** and proceed to step 1.

**Mode-transition note.** During Phase 0, the agent is in alching mode per the player being alched — per-player writes are permitted, global writes are forbidden. When Phase 0 ends, the agent transitions back to bankstanding mode — global writes permitted, per-player writes forbidden. This is the only sanctioned mid-ritual mode transition; see `meta/modes.md`.

### 1. Triage `players/inbox/`

For each file in the inbox:

- Read it.
- Propose a destination: a specific player's `bank/notes/`, `examine/drafts/`, `keepsake/proposals/`, or `archive/`.
- **Flag anything older than ~4 weeks** for explicit keep-or-drop. The age limit prevents the inbox from quietly accumulating forgotten items; if a capture has sat unsorted for a month, the principal decides whether it still earns its place.

### 2. Review identity drafts in the global layers

Surface all pending drafts across the **global** identity layers:

- `examine/drafts/`
- `niksis8/drafts/`
- `lorebook/drafts/`
- `keepsake/proposals/`

Group by layer. One-line summary each. The principal decides on each: approve to `confirmed/`, reject to `rejected/`, or edit-and-approve.

This is the same surface as the `/drafts` command, scoped to globals — bankstanding is one of the contexts in which global drafts are reviewed in bulk. **Per-player drafts are alching's job, not bankstanding's.**

### 3. Cross-player synthesis — promote recurring patterns to the global layer

**Dormancy gate.** This step requires ≥2 players carrying confirmed content in `examine/` or `niksis8_character/`. If only one player is operational (others pre-operational / placeholder), the step is structurally dormant — there is no cross-player recurrence to detect. Note "step 3 dormant (N=1)" in the trace and move on; do not re-deliberate. Re-activate when a second player has confirmed entries.

Read across what's been confirmed in each player's `examine/` and `niksis8_character/`. Look for **patterns that recur across players**:

- A self-observation Zezima has confirmed that also shows up confirmed in Jebrim → propose graduating to **global** `examine/drafts/`. The pattern transcends the character; the global layer is where it belongs.
- A fact about Niklavs that both Zezima and Jebrim have independently arrived at → propose graduating to **global** `niksis8/drafts/`.
- An item pinned in multiple per-player `keepsake/current.md` → propose adding to **global** `keepsake/proposals/`.

This is bankstanding's *integrative* job: per-player observations that prove cross-cutting belong at the global layer. The read crosses every player; the write lands in globals. Without this step, the global layer never accumulates from real per-player operation.

### 4. Enforce size budgets on the global `current.md` files

For each global `current.md` (`examine/`, `niksis8/`, `keepsake/`):

- Check token count against the placeholder budget (~2k for `keepsake/`, ~3k for identity layers).
- If over budget, propose rotations:
  - Which entries are still load-bearing every session? Keep.
  - Which can rotate to `archive/` — still preserved, no longer surfaced? Move.

The principal approves rotations. **Per-player `current.md` budgets are alching's responsibility.**

### 5. Review patterns in the global `rejected/` folders

For each global identity layer's `rejected/` folder (`examine/`, `niksis8/`, `lorebook/`):

- Look for repeated patterns in what got rejected. A pattern in rejections means the agent's model of "what's worth proposing" is miscalibrated at the system level.
- Surface the pattern as an `examine/drafts/` entry — the agent observing its own miscalibration.
- If the pattern implies a *change in how the agent operates*, also surface a `lorebook/drafts/` entry — that's exactly what the lorebook is for.

This is a feedback loop. Per-player `rejected/` patterns are alching's job.

### 6. Final alching-cadence audit

Phase 0 has already alched players with changes. This step is the **post-check**: list any player skipped during Phase 0 (e.g., mid-quest skip), and any player whose `last-alched.md` is aging despite no recent activity (so the principal can decide whether to alch defensively). For most rounds this is empty.

### 7. If anything in this bankstanding round changed how the agent operates — log it in lorebook

A bankstanding round that just triages inbox items and rotates keepsake doesn't need a lorebook entry. But if the round produced *behavioral changes* — a new working agreement, a refined ritual, a rule the agent will hold itself to going forward — write a `lorebook/drafts/` entry capturing:

- What changed in how the agent operates.
- Why.
- What triggered the change (which observation, which rejection pattern, which user feedback in this round).

The principal then promotes the draft to `lorebook/confirmed/` if it stands.

No separate `patch-notes.md` is maintained — the lorebook entries themselves are the chronological record of the system's evolution.

## Discipline

- **Propose, don't destroy.** Even when the move is obviously right, surface it.
- **Mirror paths into archive.** A note at `bank/notes/foo/bar.md` moves to `bank/archive/notes/foo/bar.md`. Never flatten.
- **Never delete.** Hook-enforced (`block-deletes.py`), but worth restating: bankstanding is a *moving* activity, not a *removing* one.
- **Cross-cutting, not character-bound.** While bankstanding is running, do not adopt a player's voice or scope. The system tends itself; it is not Zezima cleaning house.
- **Stop when fatigued.** Bankstanding is high-effort. If the principal is tired or the session is getting long, leave items for next time. Better incomplete bankstanding than a rushed bad call on an identity draft.

## Related

- `respawn.md` for the session-start ritual.
- `alching.md` for the per-player counterpart to bankstanding.
- `meta/modes.md` for the four-session-modes framing and the principal-vs-dwarf axis.
- `meta/drafts-mechanics.md` for the drafts-review machinery used in steps 2 and 5.
- `meta/archive-discipline.md` for the moving-not-deleting rules.
- `lorebook/_about.md` for what the self-improvement log captures and what it doesn't.
