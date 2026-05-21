# D-016 — 2026-05-21 — Gnomes — system-namespace sub-agent for closing, alching, and drafts-triage

**Context.** [[S018]] surfaced two pressures that point at the same shape of sub-agent. (1) The session-close ritual is mechanical, multi-step, and runs in every session — perfect work for delegation, but [[D-012]]'s harvest-pump architecture has been the principal doing it personally. (2) Per-player alching, especially first-time runs on long-lived players (Jebrim, 16+ turns of S014 to walk), is a 20+ turn slog of read-and-propose work that doesn't need principal introspection — it needs a checklist runner. Niklavs cued at S018 post-close: *"we should define a subagent specifically for closing sessions and organizing, we could call them gnomes."*

Dwarves already exist ([[D-006]] modes axis, dwarf-write-boundary hook) but they're scoped wrong for this work. A dwarf is **functional, task-local** — it executes a narrow query and returns. The rituals here are **structural, repository-wide** — walk many layers, propose many writes, hold a checklist across many turns. Dwarves also can't write to drafts/proposals (deliberate, per `meta/modes.md`) — exactly the surface this work needs.

Gnomes are the third role: structural housekeepers. Functional like dwarves (no introspection), but with a different write surface aimed at the housekeeping rituals.

**Decision.** Introduce **gnome** as a new value on the principal/dwarf axis (now principal/dwarf/gnome) in `meta/modes.md`, with the following spec:

### Scope

Gnomes run three rituals:

1. **Session-close** — the close-session.md procedure, end to end, including the `quest-log/in-progress/` → `completed/` transitions, inventory resume writes, harvest-pump proposals, and commit.
2. **Per-player alching** — the alching.md procedure for a named player, including step 3 (`completed/` walk for bank-note drafts), step 3a (`in-progress/` self-observation sweep), step 6 (skills graduation triage), and proposal writes to that player's drafts/proposals.
3. **Drafts-triage proposals** — surfacing the current state of `drafts/`, `proposals/`, and `keepsake/proposals/` across players when invoked outside a full alching pass. Stops short of approval (principal-only).

Bankstanding remains principal-only — its read-across-all-players + write-to-globals reach is identity-shaped work, not housekeeping. A bankstanding session can still spawn gnomes for its Phase 0 alching loop (one gnome per player needing alching).

### Write boundary

Gnomes can write to:

- Any player's `bank/drafts/`, `bank/notes/` (the latter via alching-promotion path).
- Any player's `quest-log/in-progress/`, `quest-log/completed/`, `quest-log/archive/`.
- Any player's `inventory/`.
- Any player's `examine/drafts/`, `niksis8_character/drafts/`.
- Any player's `keepsake/proposals/`.
- Any player's `spellbook/drafts/skills/`, `spellbook/skills/` (the latter via alching-promotion path).
- Global `examine/drafts/`, `niksis8/drafts/`, `keepsake/proposals/`, `lorebook/drafts/`.
- `players/inbox/` (for unscoped capture triage during session-close).
- Any `archive/` or `rejected/` path (housekeeping moves).

Gnomes **cannot** write to:

- Any `confirmed/` path — same line dwarves hold; identity gating is unchanged.
- `lorebook/decisions/` (only the principal canonicalizes; gnomes draft).
- `keepsake/current.md` (user-only pin surface).
- `meta/` (user-only rulebook).
- `spellbook/rituals/` (user-only at every scope).
- `gielinor/CLAUDE.md` or any other principal-edited body file.

Enforced architecturally by a new `gnome-write-boundary.py` hook (parallel to `dwarf-write-boundary.py`), gated on env var `CLAUDE_BRAIN_GNOME=1` set by the spawning agent. Existing `block-confirmed-writes.py` and `block-deletes.py` still apply.

Gnomes also **cannot spawn further sub-agents**. The existing `block-sub-dwarf-spawn.py` hook is generalized to fire on either `CLAUDE_BRAIN_DWARF=1` or `CLAUDE_BRAIN_GNOME=1`.

### Namespace

Gnomes are **system-namespace**, not player-namespace. There is one gnome agent config (`gielinor/.claude/agents/gnome.md`) regardless of which ritual or which player. The spawn brief carries the player as a parameter; the gnome reads that player's layers and writes to that player's drafts/proposals — but its identity is "gnome," not "gnome-of-Jebrim." Voice is system-flavored: checklist-driven, terse status updates, third-person about the player ("Jebrim's `completed/` has 0 files — nothing to harvest").

Consequence: a single gnome invocation can in principle touch multiple players (e.g., bankstanding Phase 0 spawning *one* gnome per player would be the per-player model; spawning one gnome that walks all players is also possible but discouraged for context-window reasons). Practical pattern: one gnome per player per alching pass; one gnome for the whole session-close.

### Spawn trigger

Heuristic auto-spawn — the principal evaluates against these criteria at ritual entry and delegates if any fires:

- **Session-close:** > 15 turns in the active session OR ≥ 2 players touched in the session OR > 5 pending drafts to triage. Light closes (read-only, no changes, < 10 turns) stay principal-self.
- **Alching:** > 20 harvest-target turns in the player's `in-progress/` since last-alched OR > 10 pending drafts OR never-alched-and-day-1+.
- **Drafts-triage:** > 10 pending drafts across the brain.

The numeric thresholds live in `gielinor/spellbook/skills/spawning-gnomes.md` (single source) and are referenced by `close-session.md`, `alching.md`, and any future drafts-triage ritual. Tuning happens in one place.

When the heuristic does not fire, the principal runs the ritual personally — keeps the procedure from drifting, since the principal walks the steps periodically and notices when they need editing.

### Persona

`gielinor/spellbook/skills/spawning-gnomes.md` carries the gnome's full operating spec: scope, write boundary (referencing the hook), spawn trigger (the heuristic), persona, communication discipline. The persona is intentionally thin — gnomes are functional, not introspective. They report in checklist form ("step 3 complete: 0 files in `completed/`, 0 bank drafts proposed"), don't speculate, don't write `examine/drafts/` about themselves.

**Alternatives considered.**

- **Per-player gnomes.** Considered. Would make the persona player-flavored (a Jebrim-gnome speaks in Jebrim's terse-analytical voice). Rejected: gnomes do housekeeping, not analysis — the player voice is the wrong fit for "step 3 complete: 0 files." Also forces N agent configs instead of one, with no win.
- **Extend dwarves instead.** Considered. Dwarves are deliberately scoped *away* from drafts/proposals writes ([[modes.md]] discipline). Widening their write surface conflates two legitimately different roles (narrow query-execution vs. structural housekeeping) and would silently expand dwarves' reach in every existing ritual that spawns one. Cleaner to add a new role.
- **One gnome that walks all players in a single invocation (bankstanding-style).** Considered for bankstanding Phase 0. Rejected as default: context-window blast radius is large, and a per-player gnome can be re-spawned cheaply. The principal can still choose to spawn one cross-player gnome for a small-brain pass (e.g., only Zezima and Jebrim, both with sparse changes) if it's cheaper.
- **Gnomes can promote drafts to confirmed.** Considered. Rejected — confirmed is identity-shaped, principal-gated by hook. Gnomes propose; principal approves. Same line dwarves hold.
- **Gnomes can write to `lorebook/decisions/` directly.** Considered (since gnomes write to `lorebook/drafts/`). Rejected — the canonical decision number `D-NNN` is a principal commitment, not a housekeeping artifact. Gnomes draft; principal canonicalizes.
- **No hook enforcement, discipline-only.** Considered. Rejected on the same grounds as the dwarf-write-boundary: housekeeping bugs are exactly the place where silent drift into identity layers is most likely (the gnome is *next to* the drafts already; one wrong path component lands it in `confirmed/`). Hook is cheap; risk is real.
- **Gnomes inherit the active player when spawned during a player session.** Considered as a hedge. Rejected — system-namespace is cleaner and the brief already carries player scope as a parameter. No inheritance needed; the gnome reads whichever player(s) the brief names.

**Consequences.**

*Files added.*

- `gielinor/.claude/hooks/gnome-write-boundary.py` — the allow-list hook, gated on `CLAUDE_BRAIN_GNOME=1`.
- `gielinor/.claude/agents/gnome.md` — Claude Code agent config. Tools: Read, Edit, Write, Glob, Grep, Bash. No Agent/Task tool (cannot spawn sub-agents).
- `gielinor/spellbook/skills/spawning-gnomes.md` — operating spec, single source of truth for spawn heuristics and persona.
- This file.

*Files modified.*

- `gielinor/.claude/settings.json` — register `gnome-write-boundary.py` in the PreToolUse Edit/Write matcher.
- `gielinor/.claude/hooks/block-sub-dwarf-spawn.py` — generalize the env-var gate to fire on either `CLAUDE_BRAIN_DWARF=1` or `CLAUDE_BRAIN_GNOME=1`. Rename optional; functional generalization is enough.
- `gielinor/meta/modes.md` — add gnome as the third value on the principal/dwarf axis. Document scope, write reach, spawn trigger (with `→ spellbook/skills/spawning-gnomes.md` for the source of truth on numeric thresholds), namespace, persona pointer.
- `gielinor/meta/write-rules.md` — add a gnome row to the ritual write-reach table.
- `gielinor/CLAUDE.md` — fifth architectural guarantee: gnome write boundary, mirroring the dwarf entry.
- `gielinor/spellbook/rituals/close-session.md` — add step 0 spawn-decision (heuristic check + gnome brief on hit).
- `gielinor/spellbook/rituals/alching.md` — same pattern, per-player.

*Spec changes that propagate.* Any new ritual that does structural housekeeping should consider gnome-delegation at step 0. The gnome write-reach is a *ceiling*, not a default — individual rituals can scope tighter via their step instructions to the gnome.

*Things explicitly deferred.*

- **Drafts-triage as a standalone ritual.** `spellbook/rituals/drafts-triage.md` deferred until the existing alching + bankstanding flow proves insufficient. The third-scope gnome can do it on demand without a dedicated ritual doc.
- **Visualizer integration.** Gnome sprite, workshop building, spawn/despawn events on agent invocation — deferred. Reuse dwarf-spawn semantics for now; the gnome shows up as a generic sub-agent in the COMMS panel until a sprite lands.
- **Cross-player gnome optimization.** Single-gnome-multi-player pass (one invocation covers all players needing alching) deferred — wait for a real bankstanding pass to see if the context cost matters.
- **Heuristic threshold tuning.** Shipped numbers are conservative. First few real spawns will tell us whether they fire too often or too rarely.

## Supersedes / superseded by

- Extends [[D-012]] (close-session harvest-pump) — gnomes are the *runners* of the harvest pump when it's heavy. The pump itself is unchanged.
- Extends [[D-015]] (Jebrim layer audit) — the alching procedure D-015 patched now has a designated runner for first-time / heavy passes.
- Extends `meta/modes.md` principal/dwarf axis to principal/dwarf/gnome. No supersession — both prior roles still operate as before.

## Anchor

- [[S019]] in dev brain — the implementation session.
- `gielinor/spellbook/skills/spawning-gnomes.md` — operating spec; single source of truth.
- `gielinor/.claude/hooks/gnome-write-boundary.py` — enforcement.
- `gielinor/.claude/agents/gnome.md` — agent config.
