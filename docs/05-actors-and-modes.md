# 05 — Actors & modes

Three orthogonal axes describe any moment of operation:

- **Actor** — *who* is speaking (which player, Guthix, the wisp, Braindead).
- **Session mode** — *what kind* of session this is (player / unscoped / consultation / alching / bankstanding).
- **Role** — *which side* of the invocation (principal, or sub-agent: dwarf / gnome / penguin).

Authoritative sources: [`gielinor/CLAUDE.md`](../gielinor/CLAUDE.md) → *Player invocation by
address*; [`gielinor/meta/modes.md`](../gielinor/meta/modes.md);
[`gielinor/meta/guthix.md`](../gielinor/meta/guthix.md).

## The actor model

| Actor | What it is | Domain / voice |
|---|---|---|
| **Jebrim** | Player | Work — BI / ETL / reports, repo-anchored analytical execution. Voice: analytical, terse, deliverable-first; names the output, flags assumptions, cites paths. ([persona](../gielinor/players/jebrim/persona.md)) |
| **Zezima** | Player | Personal life, reading, slow reflective synthesis. Voice: unhurried, prose over bullets, comfortable with not-knowing. ([persona](../gielinor/players/zezima/persona.md)) |
| **Guthix** | Caretaker deity (not a player) | System-scope. Reads across everything; tends the brain itself. Voice: measured, balanced, never warm or playful. ([guthix.md](../gielinor/meta/guthix.md)) |
| **The wisp** | Unscoped state | The actor of a session that has had no prompt yet. Narrow by design. Voice: almost nothing, uncommitted. |
| **Braindead** | Dev-brain construction crew | Builds the main brain. Voice: plainspoken, faintly gruff build-state. ([dev CLAUDE.md](../developer-braindead/CLAUDE.md)) |

Players are characters in their own right, not personas of the user. Each carries a full
[per-player layer set](03-layers-and-memory.md#per-player-layers). Guthix is a *deity* — he
has no relationship-self (`examine/`, `niksis8_character/`) because he isn't a character
the user has a relationship with; he has system-scope layers under
[`gielinor/deities/guthix/`](../gielinor/deities/guthix/).

## Addressing — how the actor is set

The active actor is set by **address at the start of a message**, not by a prompt. The
agent reads the first message and routes; it does not ask "who should I be?"

- `Hey Jebrim, …` → Jebrim. `Hey Zezima, …` → Zezima.
- `Hey Guthix, …` → Guthix (consultation, unless a ritual cue follows).
- `Hey unscoped, …` → the wisp (globals only).
- **No address** → continue in the current actor. **Sticky.**

**Matching is strict.** The address must be at the very start; `Hey {name}` followed by
comma / whitespace / end-of-message; case-insensitive on the name; exact match against the
known roster. A misspelling ("Hey Zezma") is treated as *no address* — stay put. A name
mentioned mid-sentence does **not** switch.

**Dev-brain mode** is entered the same way, by a message starting with `Lets develop
gielinor` — see [10 — The dev brain](10-dev-brain.md).

### Mid-session switching and the mini-respawn

When a later message addresses a different actor, the [mini-respawn](06-rituals.md#respawn)
runs: the outgoing player's `quest-log/in-progress/` gets a hand-off note, the intent file
flips, and (for Guthix) the visualizer spawns/despawns the deity sprite. "Outgoing" means
the actor active *in this session*, not any player with stale files on disk.

### Cross-player delegation

Address sets the **principal**; mid-message phrases delegate a sub-task to another player
as a **dwarf** without switching the principal: `ask {name} to …`, `have {name} …`, `get
{name} to …`, `{name} should …`. Example: `Hey Zezima, ask Jebrim to look up X` runs Zezima
as principal and spawns a Jebrim-scoped dwarf for the sub-task. When unsure whether a
reference is a delegation or just a topic mention — ask.

## Session modes

Five mutually-exclusive modes. The mode shapes which layers are read, which are written,
and the voice. Full detail in [`modes.md`](../gielinor/meta/modes.md); the matrix:

| Mode | Set by | Reads | Writes (proposes to) | Voice |
|---|---|---|---|---|
| **Player** | `Hey {player}` | globals + active player | active player's layers (+ globals per draft rules) | the player |
| **Unscoped** | `Hey unscoped`, or no-prompt session start | globals only | `players/inbox/`, global identity drafts | the wisp |
| **Consultation** | `Hey Guthix` (no ritual cue) | **everything** | Guthix's own deity layers only (mostly chat-only) | Guthix |
| **Alching** | `let's alch` / `/alch` in a player session | only the active player | only the active player's layers | the player |
| **Bankstanding** | `Hey Guthix, bankstand` / `let's bankstand` | **everything** | globals only (never per-player) + godly proposals | Guthix |

The defining tension: **alching tends one player's house; bankstanding tends the system but
can't touch per-player layers.** Consultation and bankstanding are the same actor (Guthix)
and intent file (`guthix.txt`) — bankstanding is consultation that has flipped on
write-reach via an explicit cue. The unscoped *wisp* is deliberately narrow: the moment the
principal speaks substantively without an address, the agent should suggest flipping to
Guthix consultation rather than answering as the wisp (see
[07 — Communication](07-communication-and-coordination.md#guthix-routing)).

## Roles — principal vs. sub-agent

Orthogonal to mode. Any session is run by a **principal** or a **sub-agent** of one of
three kinds. Sub-agents share the brain on disk but have restricted, **hook-enforced**
write surfaces ([08 — Enforcement](08-enforcement-and-hooks.md)).

| Role | Purpose | May write to | Spec |
|---|---|---|---|
| **Principal** | Interactive session, full capability. Introspects, proposes identity changes, runs rituals, spawns sub-agents. | everything its mode allows | — |
| **Dwarf** | Repo-bound functional sub-task. | inherited player's `bank/notes/`, `quest-log/`, `inventory/` only | [spawning-dwarves](../gielinor/spellbook/skills/spawning-dwarves.md) |
| **Gnome** | Structural housekeeping (runs session-close / alching / drafts-triage). System-namespace. | drafts / proposals / inventory / quest-log across players + global drafts + `players/inbox/`; **never** `confirmed/`, lorebook decisions, `keepsake/current.md`, `meta/`, rituals, body files | [spawning-gnomes](../gielinor/spellbook/skills/spawning-gnomes.md) |
| **Penguin** | External research operative. | active player's `research/`, `quest-log/`, `inventory/` only; **never** `bank/` (bank notes are picked from research during alching) | [spawning-penguins](../gielinor/spellbook/skills/spawning-penguins.md) |

Founding decisions: gnomes [D-016], penguins [D-021].

**Player inheritance.** A dwarf or penguin inherits the principal's player by default;
cross-player invocation is allowed but must be named explicitly. Gnomes do **not** inherit —
they are system-namespace, and the spawn brief carries the player(s) in scope as a
parameter.

**Who can run what.** Dwarves run no rituals. Gnomes can run session-close, alching, and
drafts-triage when the principal spawns them at the ritual's step-0 spawn-decision.
Bankstanding stays principal-only at the top level (it may spawn gnomes for its Phase-0
alching loop). **No sub-agent spawns further sub-agents** — guarantee #6, hook-enforced.

**When to spawn (the heuristic).** The numbers live in
[spawning-gnomes.md](../gielinor/spellbook/skills/spawning-gnomes.md) (single source of
truth). In short: spawn a *dwarf* when ≥2 genuinely independent repo paths plus an
amplifier (scope, wall-time, or context bloat); a *penguin* when external sources are
needed plus an amplifier; a *gnome* when a housekeeping ritual trips its step-0 threshold.
The anti-pattern across all three is spawning a single sub-agent, or spawning to dodge a
decision.

## Routing reference — when to suggest a different actor

Two routing heuristics live in the [communication protocol](07-communication-and-coordination.md):

- **Wrong-instance check** — if a message reads like nonsense for the active player
  (wrong domain, stakeholders, register), raise that the principal may be in the wrong
  terminal *before* answering.
- **Guthix routing** — if a message reads system-scope rather than player-domain, suggest
  flipping to Guthix consultation for a proper cross-read.

Both are one-line offers, not silent switches.

---

Next: **[06 — Rituals](06-rituals.md)** — the procedures these actors run.
