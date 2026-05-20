# alching — per-player tending ritual

The procedure the agent runs to tend a **single player's** content. Active, not unconscious — the agent steps away from external work and turns inward, but only inside the active player's namespace.

Named for the RuneScape High Alchemy spell: cast on items in your inventory to convert them into something more useful. A tidying-while-extracting-value ritual you do to your own stuff.

## Alching is its own mode

Alching is **a distinct session mode**, separate from player mode, unscoped mode, and bankstanding. While alching is running, the agent is the active player tending its own house — not adventuring, not the system-as-a-whole.

Pairs with bankstanding in the vocabulary:

- **Alching** is per-player. Reach: only the active player's content.
- **Bankstanding** is system-wide. Reach: globals and read-across-all-players.

Both are "stop adventuring, tend to your stuff" activities. Different scopes.

See `meta/modes.md` for the four-mode framing and how it sits orthogonal to principal-vs-dwarf.

## Scope

Alching operates **within a single active player's scope.** It is invoked while a player is active. It tends *that player's* content only:

- `players/<active>/bank/`
- `players/<active>/quest-log/`
- `players/<active>/inventory/`
- `players/<active>/examine/`
- `players/<active>/niksis8_character/`
- `players/<active>/keepsake/`

It **does not touch globals.** It **does not touch other players' content.** Cross-player promotions and global identity-layer work are bankstanding's job, not alching's.

## Why this ritual exists

Per-player drafts pile up. A player's `bank/` accumulates entries that have gone stale. Session entries crystallize into lessons that should outlive the session. Keepsake creeps past budget. Without a per-player tending pass, the principal either ignores it (rot) or has to wait for the next bankstanding (which is system-level and may not happen often enough for any single player).

Alching is the per-player counterpart to bankstanding. Same discipline (propose, never destroy), narrower reach.

## When it runs

**Three invocation modes:**

- **Explicit.** The principal cues alching during a player session — `Hey Zezima, let's alch` or `/alch`.
- **Recommended at respawn** when per-player thresholds are breached (see below). The agent mentions it once and proceeds normally if the principal declines.
- **As Phase 0 of bankstanding.** When the principal cues bankstanding, the ritual begins with a Phase 0 that runs alching for each player with changes since their last alch. The alching procedure itself is unchanged — only the invoker (the bankstanding ritual) and the sequencing (multiple players in a row, one after another) differ. See `spellbook/rituals/bankstanding.md` for the Phase 0 spec.

The agent never auto-runs alching. As with bankstanding, principal-supervised only.

## Recommendation thresholds (informational, not blocking)

Surface a recommendation when **any** of these is true for the active player at respawn:

- More than ~10 pending drafts across the player's `examine/drafts/`, `niksis8_character/drafts/`, `keepsake/proposals/`.
- Any of the player's `current.md` files exceeds its budget (~2k for `keepsake/`, ~3k for identity layers).
- The player's `bank/` has grown by ~20+ entries since last alching.
- The player's `quest-log/sessions/` has accumulated ~15+ entries since last alching.
- The player hasn't been alched in 30+ days of activity (read from `last-alched.md`).

Recommendation shape — one line:

> "Alching for Zezima is overdue — 14 pending drafts and the bank's grown by 25 since last time. Want to handle that now?"

If the principal declines, proceed normally. Do not nag again that session.

## The procedure

The agent works through each item below in order, restricted to the active player's namespace. **Propose, never silently destroy.** Surface every move to the principal for confirmation rather than auto-executing.

### 1. Review the active player's identity drafts

Surface all pending drafts inside this player's scope:

- `players/<active>/examine/drafts/`
- `players/<active>/niksis8_character/drafts/`
- `players/<active>/keepsake/proposals/`

Group by layer. One-line summary each. Per draft: approve into `confirmed/` (or `current.md` for keepsake), reject into `rejected/`, or edit-and-approve.

### 2. Review the active player's `bank/` for staleness

Walk the player's `bank/notes/`. Look for entries that are no longer relevant — superseded by newer notes, about work that's done and won't come back, contradicted by current state. Propose moves to `bank/archive/notes/<same path>`.

### 3. Quest-log compression — graduate episodes to bank

Walk the player's `quest-log/completed/` (and `quest-log/sessions/` if that's where session entries live in this player's structure). Look for entries whose value has **crystallized into a lasting lesson** — a single session whose insight should outlive the session itself.

- Propose drafts to the player's `bank/notes/` (or `examine/drafts/` if it's character-self-knowledge, or `niksis8_character/drafts/` if it's about Niklavs).
- Bias: most session entries do *not* graduate. Only flag ones with reusable cross-session value.
- This is alching's *integrative* job, scoped within one player: episodic → semantic compression.

### 4. Enforce size budgets on the player's `current.md` files

For each of the player's `current.md` (examine, niksis8_character, keepsake): check token count against budget. If over, propose rotations to the corresponding `archive/`. The principal approves.

### 5. Review patterns in the player's `rejected/` folders

For this player's `examine/rejected/` and `niksis8_character/rejected/`: look for repeated patterns in what got rejected. A pattern means the agent's model of "what's worth proposing for this character" is miscalibrated. Surface the pattern as a draft to the player's `examine/drafts/` — or, if it implies a *working agreement* for this player specifically, surface it as a candidate for the player's spellbook or persona.

Alching does not write to the global `lorebook/`. If the pattern implies a system-level behavioral change (not player-specific), note it and surface it next bankstanding instead.

### 6. Update `last-alched.md`

Write today's date into `players/<active>/last-alched.md`. This is what the threshold checks read; without the update, the next respawn will keep flagging the player as overdue.

## What alching does not do

- Does not touch globals (`examine/`, `niksis8/`, `keepsake/`, `lorebook/`, `meta/`, `spellbook/`). Those are bankstanding's reach.
- Does not touch other players' content. A Zezima alching session does not read or modify Jebrim's layers.
- Does not promote cross-player patterns to the global layer. That is explicitly bankstanding's integrative job, not alching's.
- Does not write to the global lorebook even when a behavioral change is implied. Flag for bankstanding instead.

## Discipline

- **Propose, don't destroy.** Same as bankstanding.
- **Mirror paths into archive.** A note at `bank/notes/foo/bar.md` moves to `bank/archive/notes/foo/bar.md`. Never flatten.
- **Never delete.** Hook-enforced (`block-deletes.py`).
- **Stay in scope.** While alching is running, do not read or write outside the active player's namespace. If something cross-cutting surfaces, note it for next bankstanding and move on.
- **Stop when fatigued.** Alching is high-effort. Better incomplete alching than rushed identity decisions.

## Related

- `bankstanding.md` for the system-level counterpart and its sharpened global-only scope.
- `meta/modes.md` for the four-mode framing.
- `meta/write-rules.md` for the per-layer write discipline alching operates under.
- `meta/drafts-mechanics.md` for the drafts-review machinery used in step 1.
- `meta/archive-discipline.md` for moving-not-deleting.
