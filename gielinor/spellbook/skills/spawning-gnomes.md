# Gnomes — skill

> The operating spec for **gnomes**: when to spawn one, how to brief one, where they're allowed to write, and what their report back to the principal looks like. Single source of truth for the spawn heuristic numbers — `close-session.md` and `alching.md` reference this file at their step 0 spawn-decision rather than carrying the thresholds themselves.

See [[D-016]] (dev brain) for the founding decision. **Read `gielinor/meta/modes.md` when you spawn a gnome** — it left the eager `@import` chain (§X Stage B), so the principal/dwarf/gnome axis and the gnome role-framing load here, at spawn time. The full gnome write surface is also restated inline below.

## What a gnome is

A **structural housekeeper** sub-agent. Functional like a dwarf (no introspection, no design decisions), but with a different write surface aimed at the housekeeping rituals — session-close, per-player alching, drafts-triage.

System-namespace. One agent config (`gielinor/.claude/agents/gnome.md`); the spawn brief carries the player(s) in scope as a parameter. Voice is system-flavored, checklist-driven, third-person about the player.

## When this fires — the spawn heuristic

At the start of each housekeeping ritual, evaluate the heuristic for that ritual. **If any criterion fires, spawn a gnome instead of running personally.** Light rituals stay with the principal so the procedure doesn't drift from disuse.

### Session-close

Spawn a gnome if **any** of the following:

- **> 15 turns** in the active session.
- **≥ 2 players touched** in the session (mid-session player switches, dwarf invocations across players).
- **> 5 pending drafts** to triage at close-time (sum across `examine/drafts/`, `niksis8_character/drafts/`, `bank/drafts/`, `spellbook/drafts/skills/`, `keepsake/proposals/`, `lorebook/drafts/`).

Stay principal-self if the session was **< 10 turns AND read-only / no on-disk changes**. Brief sessions don't earn the spawn cost.

### Per-player alching

Spawn a gnome if **any** of the following for the target player:

- **> 20 harvest-target turns** in the player's `quest-log/in-progress/` since `last-alched.md` date.
- **> 10 pending drafts** across the player's `examine/drafts/`, `niksis8_character/drafts/`, `bank/drafts/notes/`, `spellbook/drafts/skills/`, `keepsake/proposals/`.
- **Never-alched AND day 1+.** First-time alching for any non-newborn player is gnome work — the walk through `completed/` + the step 3a in-progress sweep is too long for principal-self.

A bankstanding-spawned Phase 0 loop spawns one gnome per player needing alching (the practical default; see below).

### Drafts-triage

Spawn a gnome if **> 10 pending drafts** across the brain (globals + all players). Below that, principal-self is fine.

### Numeric tuning

Shipped numbers above are conservative — first few real spawns will tell us whether they fire too often or too rarely. Tune **here**, in this file. The rituals don't carry copies of the numbers.

## Pre-flight check (at ritual step 0)

Before running a housekeeping ritual personally, evaluate the heuristic for that ritual. If it fires, mention the spawn decision in the Plan line (per `meta/communication-protocol.md` dwarf-spawn annotation) and brief the gnome. If the principal has explicitly asked for principal-self, respect that — the heuristic is a default, not an override.

Briefing template per gnome:

- **Ritual.** `session-close` | `alching` | `drafts-triage`.
- **Player(s) in scope.** Named players (e.g., `Jebrim`); `system` for an unscoped session-close.
- **Inputs.** The numbers that fired the heuristic (turn count, drafts pending, days since alch). Lets the gnome state in its report which threshold triggered the spawn.
- **Out of scope.** Anything the principal wants explicitly excluded — e.g., "do not touch Zezima's drafts this pass."
- **Sibling file path.** Where the gnome writes its run-log entry — typically `players/<scope>/quest-log/in-progress/SNNN_gN_<ritual>.md` (gN = gnome 1, 2, ...). For unscoped session-close, `players/inbox/SNNN_gN_<ritual>.md`.

## Write surface — what the gnome can touch

**Allowed** (hook-enforced by `.claude/hooks/gnome-write-boundary.py`):

- Any player's `bank/drafts/`, `bank/notes/` (the latter via alching-promotion path).
- Any player's `quest-log/in-progress/`, `quest-log/completed/`, `quest-log/archive/`.
- Any player's `inventory/`.
- Any player's `examine/drafts/`, `niksis8_character/drafts/`.
- Any player's `keepsake/proposals/`.
- Any player's `spellbook/drafts/skills/`, `spellbook/skills/` (the latter via alching-promotion).
- Any player's `last-alched.md` (the alching stamp — gnomes run alching, so they write its closing step; widened [[B-010_2026-05-29_tenth-bankstanding|B-010]] 2026-05-29).
- Global `examine/drafts/`, `niksis8/drafts/`, `keepsake/proposals/`, `lorebook/drafts/`.
- `players/inbox/`.
- Any `archive/` or `rejected/` path (housekeeping moves).

**Blocked** (same hook):

- Any `confirmed/` path. Also blocked by `block-confirmed-writes.py`.
- `lorebook/confirmed/` — principal canonicalizes.
- `keepsake/current.md` — user-only pin surface.
- `meta/` — user-only rulebook.
- `spellbook/rituals/` — user-only at every scope.
- `CLAUDE.md` / `CLAUDE.local.md`, `.mcp.json`, `ticks.md`, `.claude/settings*`, `.claude/agents/`, `.claude/hooks/`.

**Cannot spawn sub-agents** (`block-sub-spawn.py` hook). If more agents are needed mid-ritual, return to the principal.

## Discipline

- **Checklist-driven.** Walk the ritual's steps in order. State which step, state its result, move on. No flourish.
- **Terse status.** "Step 3 complete: 0 files in `completed/`, 0 bank drafts proposed." Not "I have now thoroughly reviewed..."
- **Third-person about the player.** Gnomes are system voice. "Jebrim's `keepsake/current.md` is empty" — not "my keepsake is empty."
- **Propose, don't approve.** Drafts → `drafts/`, proposals → `proposals/`. Promotion is principal work.
- **No introspection.** Gnomes don't write `examine/drafts/` about gnome behavior. If the *ritual itself* needs flagging, surface in the final report; the principal decides whether it earns a `lorebook/drafts/` entry.
- **Never delete.** Moves into `archive/` only (per `meta/archive-discipline.md`).
- **No `--no-verify` on commits.** Standard close-session commit discipline applies.

## Reporting format

The gnome returns a structured report to the principal at the end of its invocation:

```
## Ritual: <session-close | alching | drafts-triage>
## Player(s) in scope: <names or "system">
## Spawned because: <which threshold(s) fired>

### Steps walked
- Step N — <one-line result>

### Proposals written
- <path> — <one-line summary>

### Moves performed
- <from> → <to>

### Anomalies / things needing principal attention
- <one-line item>

### Commit (session-close only)
- <hash> or "no commit; tree clean"
```

The principal reads the report, can dive into individual diffs, and approves/rejects proposals as usual.

## Cross-player gnomes vs per-player gnomes

**Default: per-player gnomes** for alching, one gnome covering the whole session-close.

A **bankstanding Phase 0** loop spawns one gnome per player needing alching — same as the principal-self pattern. Single-invocation cross-player gnomes (one gnome walks two or more players' alching passes) are possible but discouraged for context-window reasons. Use only when the brains being touched are small (e.g., two players with sparse changes).

## Anti-patterns

- **Spawning a gnome for a 5-turn read-only session.** The heuristic explicitly excludes this; principal-self is faster.
- **Letting a gnome propose to `confirmed/`.** Hook blocks; if a gnome's brief implies promoting to `confirmed/`, the brief is wrong.
- **Gnome → gnome chain.** Hook blocks sub-spawning; if a ritual needs N gnomes, the principal spawns N separately.
- **Gnome writing `lorebook/confirmed/D-NNN_*.md`.** Allowed only via `lorebook/drafts/`; the canonical `D-NNN` filename is a principal commitment.
- **Mixing the heuristic across files.** If a ritual carries a numeric threshold, this file is wrong. Move the number here and reference.

## Related

- [[D-016]] (dev brain) — the founding decision.
- `meta/modes.md` — principal/dwarf/gnome axis.
- `meta/write-rules.md` — per-layer discipline and ritual write-reach table.
- `spellbook/rituals/close-session.md` — step 0 references this skill.
- `spellbook/rituals/alching.md` — step 0 references this skill.
- `spellbook/skills/spawning-dwarves.md` — the companion skill for the functional sub-agent.
- `gielinor/.claude/agents/gnome.md` — the agent config (system prompt + tools).
- `.claude/hooks/gnome-write-boundary.py` — the enforcement.
- `.claude/hooks/block-sub-spawn.py` — sub-spawn block.
