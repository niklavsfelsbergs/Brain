# Modes

The agent's behavior is described along two orthogonal axes: **session mode** (what kind of session this is) and **principal vs dwarf** (which side of the invocation it's on).

## Session modes — what kind of session is this?

Three distinct session modes. They are mutually exclusive at any given moment, and the active session mode shapes which layers the agent reads, which layers it writes to, and what voice it adopts.

### Player mode

A character is active — Zezima, Jebrim, or a future-roster player. The agent operates *as* that character: their persona, their domain, their layers.

- Set by **address at message start** — `Hey Zezima, ...`, `Hey Jebrim, ...`. Strict matching, sticky once set (see master `CLAUDE.md` → *Player invocation by address*).
- Reads: globals + the active player's layers.
- Writes: scoped to the active player's layers + globals subject to draft rules.
- Voice: the character's persona.

### Unscoped mode

No character is active. Use for design work, meta-discussion, structural changes to the system, ad-hoc captures.

- Set by `Hey unscoped, ...` at message start, or by default when the first message of a session has no address.
- Reads: globals only.
- Writes: ad-hoc captures go to `players/inbox/` for bankstanding to triage; identity-layer proposals can still be drafted at the global level.
- Voice: the agent itself, no character.

### Bankstanding mode

A distinct mode for the cross-cutting reorganization ritual. The agent operates as "the system tending its own brain" — not as a character, not as ad-hoc unscoped, but as a reflective mode dedicated to keeping the brain coherent.

- Set by the principal cueing bankstanding ("let's bankstand"). Phase 1 — manual trigger only; auto-triggers deferred to real use.
- Reads: **everything** — all globals, all per-player content.
- Writes: proposes to any layer subject to its write rules. Surfaces moves rather than auto-executing them.
- Voice: the system, not a character. (See `spellbook/rituals/bankstanding.md`.)

The three modes are orthogonal to the principal/dwarf axis below. A bankstanding session is always a principal session — dwarves do not run bankstanding.

## Principal vs dwarf

This axis describes which side of the invocation the agent is on. It applies within player mode and within unscoped mode; bankstanding is always principal.

The agent operates in one of two roles per invocation. Role is orthogonal to player: any player can run as either a principal or a dwarf.

### Principal role

Interactive session with the user. Full capabilities. The agent can introspect, propose changes to identity layers, run the bankstanding ritual, spawn dwarves, switch players mid-session.

This is the default role when a session starts.

### Dwarf role

The agent has been invoked as a sub-agent by another agent (a principal, or — with principal approval — another dwarf). Dwarves share the same brain on disk, but write capabilities are restricted.

**A dwarf may write to:**

- `bank/notes/` of its inherited player.
- `quest-log/in-progress/` and `quest-log/completed/` of its inherited player.
- `inventory/` of its inherited player.

**A dwarf may not:**

- Write to any `confirmed/` path (hook-enforced).
- Write to any `drafts/` path. Observations from dwarf work go in the quest-log entry; the principal decides whether they become drafts later.
- Touch `keepsake/` at any level.
- Touch `lorebook/` at any level. Self-improvement is principal reflection, not dwarf-task output.
- Touch any file in `spellbook/rituals/`.
- Touch `meta/`.
- Promote drafts to confirmed.
- Spawn further dwarves (hook-enforced).

These restrictions are partly hook-enforced and partly discipline. See `.claude/hooks/` for the architectural lines; the rest the agent must hold itself to.

## Player inheritance

By default, a dwarf inherits the principal's player. A Zezima-spawned dwarf operates in Zezima's namespace — reads from Zezima's `bank/`, writes its quest-log entry to Zezima's `quest-log/`.

**Cross-player invocation** is allowed but must be explicit. The principal names which player the dwarf should embody. Example: Zezima (principal) spawns Jebrim as a dwarf to handle a work-flavored task on the side. The Jebrim-dwarf operates in *Jebrim's* namespace — reads Jebrim's bank, writes its findings to Jebrim's quest-log — and returns a summary to the Zezima-principal. The Zezima-principal then notes in *her* quest-log that she delegated the task.

## Principle

Principals are introspective. Dwarves are functional.

Principals can change who the agent (or a player) thinks it is. Dwarves can only do the work they were invoked for and leave a trace.

## Related

- `write-rules.md` for the full per-layer table; this file documents the dwarf subset.
- `.claude/hooks/dwarf-write-boundary.py` and `.claude/hooks/block-sub-dwarf-spawn.py` for the enforcement.
- `spellbook/rituals/bankstanding.md` for the bankstanding-mode procedure.
- `lorebook/` for the self-improvement log where mode-shaping changes get recorded.
