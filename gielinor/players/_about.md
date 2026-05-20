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

At respawn the principal is asked which player to embody. Options:

- **A specific player** — the active player's per-player layers are scoped in; the respawn ritual reads their `CLAUDE.md`, `_about.md`, `persona.md`, `keepsake/current.md`, `examine/confirmed/current.md`, and `niksis8_character/confirmed/current.md`. Then checks `quest-log/in-progress/` for unfinished business.
- **Unscoped** — no player is active; the session reads only global layers. Use for design work, meta-discussion, structural changes to the system.

Mid-session player switch triggers a **mini-respawn** for the new player. See `spellbook/rituals/respawn.md`.

## Cross-player invocation (dwarf)

A principal of one player can spawn a dwarf in *another* player's namespace. Example: Zezima (principal) spawns a Jebrim-dwarf to handle a work task on the side. The Jebrim-dwarf reads Jebrim's layers, writes to Jebrim's quest-log, and returns a summary to the Zezima-principal. Zezima then notes in her own quest-log that she delegated.

Must be explicit. The principal names which player to invoke.

## The inbox

`players/inbox/` is a holding pen for **unscoped writes** — captures the agent made without yet knowing which player they belong to. Bankstanding triages items: assign each to a player, archive it, or drop it. Items have a max age (~4 weeks); after that, bankstanding surfaces them for explicit keep-or-drop.

## Related

- `spellbook/rituals/respawn.md` for the load order at session start and player switch.
- `meta/modes.md` for principal vs dwarf, with the cross-player dwarf flow.
- `lorebook/decisions/` for the choices behind this structure.
