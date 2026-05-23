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

- **`last-alched.md` reads "Never" AND the player is > 0 days old.** (Catches first-life pile-up — Jebrim hitting day 2 with three sessions of work and no alching is the proof case.)
- More than **5** pending drafts across the player's `examine/drafts/`, `niksis8_character/drafts/`, `bank/drafts/notes/`, `spellbook/drafts/skills/`, `keepsake/proposals/`.
- Any of the player's `current.md` files exceeds its budget (~2k for `keepsake/`, ~3k for identity layers).
- The player's `quest-log/in-progress/` turn count has grown by **20+** turns since `last-alched.md`. (Proxy for "harvest backlog accumulating.")
- The player hasn't been alched in **7+** days of activity (read from `last-alched.md`).

These are the load-bearing thresholds as of 2026-05-21 (S018 audit). Tune later if too noisy or too sleepy.

Recommendation shape — one line, surfaced after the Plan per `meta/communication-protocol.md`:

> "Alching for Jebrim is overdue — 1 day old, never alched, 3 pending drafts and 16 quest-log turns since spawn."

If the principal declines, proceed normally. Do not nag again that session.

## Switchboard marker (visualizer concern)

When the agent runs alching **itself** — steps 1–7 personally, not delegated to a gnome — it flags the session so the switchboard renders an `ALCHING` chip:

- **On entry** (before step 0): write `alching` to `.claude/intent/<sid8>.mode` at the brain root, where `<sid8>` is the first 8 chars of `CLAUDE_CODE_SESSION_ID` (the same anchor the intent file uses).
- **On exit** (after step 7, or if alching is abandoned mid-pass): overwrite that file with an empty line to clear it.

`status-sidecar.py` reads the marker and overrides the session's `working` state with `alching` while it's set. The two more-actionable states still win: a draft-approval pause (a `Stop`) reads as `WAITING`, and a spawned gnome reads as `AWAITING CREW`. So an alching session shows `ALCHING` while it churns and `WAITING` when it parks for your approval — both correct.

This is a switchboard concern only — **not architecturally enforced**; a missing marker just means no chip. When alching is **delegated to a gnome** (step 0 spawn-decision fires), the principal's row reads `AWAITING CREW` instead — it is genuinely blocked on its crew — and no alching marker is written.

## The procedure

The agent works through each item below in order, restricted to the active player's namespace. **Propose, never silently destroy.** Surface every move to the principal for confirmation rather than auto-executing.

### 0. Spawn-decision — principal-self or gnome?

Before walking the steps, evaluate the gnome spawn heuristic for alching (per `spellbook/skills/spawning-gnomes.md`):

- **> 20 harvest-target turns** in the player's `quest-log/in-progress/` since `last-alched.md`, OR
- **> 10 pending drafts** across this player's `examine/drafts/`, `niksis8_character/drafts/`, `bank/drafts/notes/`, `spellbook/drafts/skills/`, `keepsake/proposals/`, OR
- **Never-alched AND the player is day-1+.**

If any fires, spawn a **gnome** with the alching brief:

- Ritual: `alching`.
- Player in scope: the active player.
- Inputs: which threshold(s) fired (turn count since alch, drafts pending, never-alched flag).

The gnome runs steps 1–7 in the active player's namespace and returns the structured report. The principal reviews the report and approves/rejects proposals before they canonicalize.

If no threshold fires (e.g., regular ongoing alching with modest pending drafts), run steps 1–7 personally. Routine alching stays with the principal so the procedure doesn't drift.

When alching is **Phase 0 of bankstanding**, the bankstanding ritual spawns one gnome per player needing alching by default — see `spellbook/rituals/bankstanding.md`. The per-player heuristic still applies; a player below all thresholds is alched principal-self even inside Phase 0.

### 1. Review the active player's identity drafts

Surface all pending drafts inside this player's scope:

- `players/<active>/examine/drafts/`
- `players/<active>/niksis8_character/drafts/`
- `players/<active>/keepsake/proposals/`

Group by layer. One-line summary each. Per draft: approve into `confirmed/` (or `current.md` for keepsake), reject into `rejected/`, or edit-and-approve.

### 2. Promote bank drafts, then review `bank/notes/` for staleness

**First, triage `bank/drafts/notes/`.** This holds harvest candidates from session closes (see [[D-012]] in dev brain) and any direct drafts the agent or principal landed mid-session. Per draft:

- **Promote** → move to `bank/notes/<same path>` (preserve folder structure).
- **Reject** → move to `bank/rejected/notes/<same path>`. Kept, not deleted.
- **Edit and promote** → the principal rewrites, then moves.

A draft that contradicts an existing `bank/notes/` entry triggers the "overturning existing knowledge" path: the contradiction surfaces, and either (a) the new draft wins and the old note archives, or (b) the new draft is rejected.

**Then, review `bank/notes/` for staleness.** Walk the player's existing notes. Look for entries that are no longer relevant — superseded by newer notes, about work that's done and won't come back, contradicted by current state. Propose moves to `bank/archive/notes/<same path>`.

### 3. Quest-log compression — graduate **completed** episodes to bank

Walk the player's `quest-log/completed/` **only** (per principal rule: harvest from finished quests, not in-flight). Look for entries whose value has **crystallized into a lasting lesson** — a single quest whose insight should outlive the quest itself.

- Propose drafts to the player's `bank/drafts/notes/` (not directly to `bank/notes/` — bank is drafts-gated).
- Bias: most quest entries do *not* graduate. Only flag ones with reusable cross-quest value.
- This is alching's *integrative* job, scoped within one player: episodic → semantic compression.
- **Self-observation harvest is a separate step** — see step 3a below. Quest-log compression is for domain knowledge; self-observations have a different cadence.

### 3a. Self-observation sweep — scan in-flight turns since last-alched

Self-observations are *about the player*, not about the work — so they don't depend on the underlying quest being closed. Walk the player's `quest-log/in-progress/` entries and read **turns added since `last-alched.md` date** (use turn timestamps or position to bound the scan). For each turn, look for sentences that read like observations about how this player works:

- Bias the player exhibited that helped or hurt.
- Pattern in how the player decomposed work, asked questions, or framed responses.
- Correction the principal landed on the player's behavior (verbatim corrections are gold).
- Mistake the player made and the lesson named in the next turn.

For each candidate observation, propose a draft to `players/<active>/examine/drafts/<YYYY-MM-DD>-<slug>.md`. The draft must cite the specific turn (e.g., "S014 T11, 2026-05-21") and the observation-rule from `meta/drafts-mechanics.md` applies — observation-backed, not aspirational.

**Cap.** 0–3 self-observation drafts per alching pass. Bias to less; not every correction earns a confirmed entry, but every confirmed entry must come from a real correction.

### 4. Enforce size budgets on the player's `current.md` files

For each of the player's `current.md` (examine, niksis8_character, keepsake): check token count against budget. If over, propose rotations to the corresponding `archive/`. The principal approves.

### 5. Review patterns in the player's `rejected/` folders

For this player's `examine/rejected/` and `niksis8_character/rejected/`: look for repeated patterns in what got rejected. A pattern means the agent's model of "what's worth proposing for this character" is miscalibrated. Surface the pattern as a draft to the player's `examine/drafts/` — or, if it implies a *working agreement* for this player specifically, surface it as a candidate for the player's spellbook or persona.

Alching does not write to the global `lorebook/`. If the pattern implies a system-level behavioral change (not player-specific), note it and surface it next bankstanding instead.

### 6. Skill graduation — walk confirmed layers for named-pattern candidates

Per [[D-012]] (dev brain), Pump 3 extends to skill-graduation. Walk these layers looking for patterns that have repeated and earned a name:

- `players/<active>/examine/confirmed/` — patterns in how this character operates that have stabilized.
- `players/<active>/niksis8_character/confirmed/` — patterns in how Niklavs interacts with this character that have stabilized.
- `players/<active>/quest-log/completed/` — repeated procedures across multiple completed quests.

**Threshold.** A pattern earns a skill draft when it has repeated **≥2 times** and the agent can name it concisely. One-off patterns are not skill candidates — they may be examine drafts instead.

**Output.** Draft to `players/<active>/spellbook/drafts/skills/<slug>.md` (per the drafts-gated path established 2026-05-21). Skill drafts follow the same observation-rule as identity drafts: cite the specific repetitions that justified naming the pattern.

**Promote existing skill drafts.** Before drafting new ones, triage what's already in `spellbook/drafts/skills/`. Per draft: approve into `spellbook/skills/`, reject into `spellbook/rejected/skills/`, or edit-and-approve. Pattern parallel to bank-drafts triage in step 2.

**Cap.** 0–2 skill candidates per alching pass. Skills are rare; this step is for genuine pattern-recognition, not for manufacturing skill drafts.

### 7. Update `last-alched.md`

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
