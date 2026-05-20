# bankstanding — periodic active reorganization

The procedure the agent runs to tend its own brain. Active, not unconscious — the agent steps away from external work and turns inward.

Named for the RuneScape activity of standing in the bank to reorganize inventory and stored items between trips.

## Why this ritual exists

The brain accumulates. Drafts pile up. Notes go stale. Keepsake creeps past its size budget. Inbox items linger past their expiration. Without periodic reorganization, the system slowly loses coherence — and worse, slowly loses retrieval quality, because relevant material gets buried in stale material.

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
- Flag anything older than ~4 weeks for explicit keep-or-drop.

### 2. Review recent `quest-log/completed/` entries (active player or all players)

Look for entries that have decayed into **lasting lessons** — single sessions whose insight should outlive the session. Propose drafts for `bank/notes/` (or `examine/drafts/` if the insight is self-knowledge, or `niksis8/drafts/` if it's about the user).

The bias: most session entries do *not* graduate. Only flag ones with reusable, cross-session value.

### 3. Review `bank/notes/` for staleness

Look for entries that are no longer relevant — superseded by newer notes, about work that's done and won't come back, contradicted by current state. Propose moves to `bank/archive/notes/<same path>`.

### 4. Review identity drafts together with the principal

Surface all pending drafts in `examine/drafts/`, `niksis8/drafts/`, and active player(s)' `niksis8_character/drafts/`. Group by layer. One-line summary each.

The principal decides on each: approve to `confirmed/`, reject to `rejected/`, or edit-and-approve.

This is the same surface as the `/drafts` command — bankstanding is one of the contexts in which drafts are reviewed in bulk.

### 5. Review `keepsake/` against size budget

For each `keepsake/current.md` (global and per-player), check token count against the placeholder budget (~2k tokens). If over budget, propose rotations:

- Which pins are still load-bearing every session?
- Which can rotate to `keepsake/archive/` — still preserved, no longer surfaced?

The principal approves rotations.

### 6. Review patterns in `rejected/` folders

For each identity layer's `rejected/`:

- Look for repeated patterns in what got rejected. A pattern in rejections means the agent's model of what's worth proposing is miscalibrated.
- Surface the pattern as an `examine/drafts/` entry — the agent observing its own miscalibration.

This is a feedback loop. Without it, the same rejected drafts get re-proposed.

### 7. Update `lorebook/assumptions.md` if needed

Walk through the assumptions list. For each:

- Has it been challenged by observation since last bankstanding? If yes, propose a change (via `lorebook/drafts/`) — either invalidate the assumption or refine it.
- Has it become a confirmed decision rather than an assumption? If yes, propose moving it to a `D-NNN` entry.

### 8. Append to `lorebook/patch-notes.md`

The bankstanding session itself is a substantive change. Append a brief factual entry: what was reviewed, what was archived, what drafts were approved/rejected. Auto-write — no approval needed.

## Discipline

- **Propose, don't destroy.** Even when the move is obviously right, surface it.
- **Mirror paths into archive.** A note at `bank/notes/foo/bar.md` moves to `bank/archive/notes/foo/bar.md`. Never flatten.
- **Never delete.** Hook-enforced (`block-deletes.py`), but worth restating: bankstanding is a *moving* activity, not a *removing* one.
- **Stop when fatigued.** Bankstanding is high-effort. If the principal is tired or the session is getting long, leave items for next time. Better incomplete bankstanding than a rushed bad call on an identity draft.

## Related

- `respawn.md` for the other primary ritual.
- `meta/drafts-mechanics.md` for the drafts-review machinery used in step 4.
- `meta/archive-discipline.md` for the moving-not-deleting rules.
- `lorebook/decisions/` for the choices that shaped this ritual.
