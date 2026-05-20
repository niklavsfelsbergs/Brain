# bankstanding — periodic active reorganization

The procedure the agent runs to tend its own brain. Active, not unconscious — the agent steps away from external work and turns inward.

Named for the RuneScape activity of standing in the bank to reorganize inventory and stored items between trips.

## Bankstanding is its own mode

Bankstanding is **a distinct session mode**, separate from player mode and unscoped mode. While bankstanding is running, the agent is not Zezima, not Jebrim, not a no-player ad-hoc operator — it is **the system tending its own brain.** The active persona is "gielinor reflecting on itself," not any character.

Three session modes exist:

- **Player mode** — a character (Zezima, Jebrim, future) is active, bounded to that character's domain.
- **Unscoped mode** — no character active; reads globals, writes go to `players/inbox/` for triage.
- **Bankstanding mode** — cross-cutting; the agent reads every layer (global + all players), proposes writes to any layer subject to draft-approval rules, exercises responsibilities no single player has.

See `meta/modes.md` for the full picture, including how this axis is orthogonal to principal-vs-dwarf.

## Reach

In bankstanding, the agent reads everything: all global layers (`examine/`, `niksis8/`, `keepsake/`, `lorebook/`, `players/inbox/`) and all per-player content (every player's `bank/`, `examine/`, `niksis8_character/`, `keepsake/`, `quest-log/`, `inventory/`).

It proposes writes to any layer the standard write rules permit (see `meta/write-rules.md`). Identity-shaped layers go through drafts; auto-write layers are touched only with care.

## Why this ritual exists

The brain accumulates. Drafts pile up. Notes go stale. Keepsake creeps past its size budget. Inbox items linger past their expiration. Per-player observations recur across players in ways that should graduate to the global layer. Episodic memory accrues without ever crystallizing into semantic memory.

Without periodic reorganization, the system slowly loses coherence — and worse, slowly loses retrieval quality, because relevant material gets buried in stale material.

Bankstanding is the principal-supervised cleanup that keeps the system retrievable.

## When it runs

Phase 1: **on principal cue.** The principal asks ("let's bankstand"). The agent doesn't trigger it autonomously yet.

Auto-triggers (scheduled, on size-budget threshold, on draft-count threshold) are deferred to real use — we'll figure out the right cadence after running the system for a while.

## The procedure

The agent works through each item below in order. **Propose, never silently destroy.** Especially in the early phase, surface every move to the principal for confirmation rather than auto-executing.

### 1. Triage `players/inbox/`

For each file in the inbox:

- Read it.
- Propose a destination: a specific player's `bank/notes/`, `examine/drafts/`, `keepsake/proposals/`, or `archive/`.
- **Flag anything older than ~4 weeks** for explicit keep-or-drop. The age limit prevents the inbox from quietly accumulating forgotten items; if a capture has sat unsorted for a month, the principal decides whether it still earns its place.

### 2. Review identity drafts (global + per-player, together)

Surface all pending drafts across all identity layers:

- `examine/drafts/`
- `niksis8/drafts/`
- `lorebook/drafts/`
- per-player `examine/drafts/` (every active player)
- per-player `niksis8_character/drafts/` (every active player)

Group by layer. One-line summary each. The principal decides on each: approve to `confirmed/`, reject to `rejected/`, or edit-and-approve.

This is the same surface as the `/drafts` command — bankstanding is one of the contexts in which drafts are reviewed in bulk.

### 3. Cross-player synthesis — promote recurring patterns to the global layer

Walk through what's been confirmed in each player's `examine/` and `niksis8_character/`. Look for **patterns that recur across players**:

- A self-observation Zezima has confirmed that also shows up confirmed in Jebrim → propose graduating to **global** `examine/drafts/`. The pattern transcends the character; the global layer is where it belongs.
- A fact about Niklavs that both Zezima and Jebrim have independently arrived at → propose graduating to **global** `niksis8/drafts/`.
- An item pinned in multiple per-player `keepsake/current.md` → propose adding to **global** `keepsake/proposals/`.

This is bankstanding's *integrative* job: per-player observations that prove cross-cutting belong at the global layer. Without this step, the global layer never accumulates from real per-player operation.

### 4. Decay/compression — graduate quest-log episodes to bank

Review recent `quest-log/completed/` entries across all players. Look for entries whose insight has **crystallized into a lasting lesson** — a single session whose value should outlive the session itself.

- Propose drafts for the relevant player's `bank/notes/` (or `examine/drafts/` if it's character-self-knowledge, or `niksis8_character/drafts/` if it's about Niklavs).
- The bias: most session entries do *not* graduate. Only flag ones with reusable cross-session value.

Episodic memory compressing into semantic memory is bankstanding's job. The respawn ritual doesn't preload `quest-log/`; the principal won't go looking through old sessions on demand. If a lesson lives only in an old quest-log file, it's effectively lost.

### 5. Review `bank/notes/` for staleness (per player)

For each player's `bank/notes/`:

- Look for entries no longer relevant — superseded by newer notes, about work that's done and won't come back, contradicted by current state.
- Propose moves to `bank/archive/notes/<same path>`.

### 6. Enforce size budgets on `current.md` files

For each `current.md` (global `examine/`, `niksis8/`, `keepsake/`; per-player `examine/`, `niksis8_character/`, `keepsake/`):

- Check token count against the placeholder budget (~2k for `keepsake/`, ~3k for identity layers).
- If over budget, propose rotations:
  - Which entries are still load-bearing every session? Keep.
  - Which can rotate to `archive/` — still preserved, no longer surfaced? Move.

The principal approves rotations.

### 7. Review patterns in `rejected/` (all identity layers)

For each identity layer's `rejected/` folder (global `examine/`, `niksis8/`, `lorebook/`; per-player `examine/`, `niksis8_character/`):

- Look for repeated patterns in what got rejected. A pattern in rejections means the agent's model of "what's worth proposing" is miscalibrated.
- Surface the pattern as an `examine/drafts/` entry — the agent observing its own miscalibration.
- If the pattern implies a *change in how the agent operates*, also surface a `lorebook/drafts/` entry — that's exactly what the lorebook is for.

This is a feedback loop. Without it, the same rejected drafts get re-proposed.

### 8. If anything in this bankstanding round changed how the agent operates — log it in lorebook

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

- `respawn.md` for the other primary ritual.
- `meta/modes.md` for the three-session-modes framing and the principal-vs-dwarf axis.
- `meta/drafts-mechanics.md` for the drafts-review machinery used in steps 2 and 7.
- `meta/archive-discipline.md` for the moving-not-deleting rules.
- `lorebook/_about.md` for what the self-improvement log captures and what it doesn't.
