# players/ — character namespaces

**What this is.** The players folder. Each subfolder is one **player** — a coherent character with its own personality, knowledge, self-model, and working memory.

**Players are not personas of Niklavs.** Zezima is Zezima, not Niklavs-in-personal-mode. Each player has its own voice, its own knowledge, its own self-knowledge. They *happen* to act on Niklavs' behalf and to know things about him, but they are characters in their own right.

## Current roster

- **`zezima/`** — personal life, reading, reflection.
- **`jebrim/`** — work, focused analytical execution.

Initial roster only. New players are added when content genuinely doesn't fit existing ones **and** there's enough volume to justify the overhead. Don't pre-create speculative players. Don't split a player just because their domain feels broad.

## How a player is structured

Each player gets the same folder template:

```
players/<name>/
  _about.md                       # who this character is
  persona.md                      # how they speak and act
  CLAUDE.md                       # minimal, imports master + adds character specifics
  examine/                        # this character's self-knowledge
    drafts/  confirmed/  archive/  rejected/
  niksis8_character/              # what this player knows about Niklavs through their relationship
    drafts/  confirmed/  archive/  rejected/
  keepsake/
    current.md  proposals/  archive/
  bank/
    _about.md  notes/  archive/
  quest-log/
    _about.md  in-progress/  completed/  archive/
  spellbook/
    _about.md  skills/  rituals/  archive/
  inventory/
    _about.md
```

`bank/`, `quest-log/`, `spellbook/`, `inventory/` exist *only* per-player — knowledge, episodes, procedures, and working memory are character-bound.

`examine/`, `niksis8_character/`, `keepsake/` exist at both scopes (global and per-player). The per-player versions are scoped to that character's lens.

## How to invoke a player

Players are invoked by **direct address at the start of a message**. There is no preemptive "which player?" prompt at session start.

- `Hey Zezima, ...` → activate Zezima.
- `Hey Jebrim, ...` → activate Jebrim.
- `Hey unscoped, ...` → drop to no-player mode.
- **No address** on a subsequent message → continue in whatever player is currently active. **Sticky.**

### First message of a session

- **First message has an address** → the named player is active from the start. The respawn ritual loads their context fully before responding (the agent reads their `CLAUDE.md`, `_about.md`, `persona.md`, `keepsake/current.md`, `examine/confirmed/current.md`, `niksis8_character/confirmed/current.md`, then checks `quest-log/in-progress/`).
- **First message has no address** → start in **unscoped** mode. No per-player loads run. Use for design work, meta-discussion, ad-hoc captures, or system-level conversation.

### Strict matching rules

- The address must be at the very start of the message. A player mentioned mid-sentence does **not** trigger a switch.
- Pattern: `Hey {name}` followed by a comma, whitespace, or end-of-message. Case-insensitive on the name.
- Exact match against the roster only (currently: Zezima, Jebrim, unscoped). No fuzzy matching. A typo is treated as no address — the current player stays active.

### Mid-session player switch

A later message addressing a *different* player than the currently active one (or addressing `unscoped` when scoped, or naming a player when unscoped) triggers a **mini-respawn** for the new player. See `spellbook/rituals/respawn.md` for the procedure.

### Unscoped mode

`Hey unscoped, ...` is a first-class addressable state. Use it when you want to operate outside any character — design work, meta-discussion, structural changes to the system. Captures made in unscoped mode go to `players/inbox/` for bankstanding to triage. The session reads only global layers.

## Cross-player invocation (dwarf)

The address at message start sets the **principal**. Mid-message phrases delegate to another player as a dwarf without changing the principal. Trigger patterns include `ask {name} to ...`, `have {name} ...`, `get {name} to ...`, `let {name} ...`, `{name} should ...` (when used as a delegation).

Example: `Hey Zezima, ask Jebrim to look up X` activates Zezima as principal *and* spawns Jebrim as a dwarf for that sub-task. The Jebrim-dwarf reads Jebrim's layers, writes to Jebrim's `quest-log/in-progress/`, and returns a summary to the Zezima-principal. Zezima then notes in *her* quest-log that she delegated.

Must be explicit. The principal names which player to invoke. When in doubt about whether a mid-message reference is a delegation or just a topic mention, the agent asks.

## Per-player tending — alching

Each player has its own tending cadence, tracked in `players/<name>/last-alched.md`. **Alching** is the per-player ritual: the agent and principal walk through one player's drafts, bank, quest-log, keepsake, and rejection patterns, scoped strictly to that player's namespace. See `spellbook/rituals/alching.md`.

Bankstanding handles the global, cross-cutting tending and can flag a player as overdue for alching, but it does not perform the per-player work itself. Alching and bankstanding pair: per-player and system-wide.

## The inbox

`players/inbox/` is a holding pen for **unscoped writes** — captures the agent made without yet knowing which player they belong to. Bankstanding triages items: assign each to a player, archive it, or drop it. Items have a max age (~4 weeks); after that, bankstanding surfaces them for explicit keep-or-drop.

## Related

- `spellbook/rituals/respawn.md` for the load order at session start and player switch.
- `meta/modes.md` for principal vs dwarf, with the cross-player dwarf flow.
- `lorebook/decisions/` for the choices behind this structure.
