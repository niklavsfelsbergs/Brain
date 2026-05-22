# deities/

> Overarching system-level actors. Not players (no relationship with Niklavs, no continuity-of-character); not sub-agents (not invoked by a principal — they *are* a principal voice when active). They tend the brain itself rather than working within it.

## Why this directory exists

Players (`gielinor/players/`) act on Niklavs's behalf in their respective domains. Sub-agents (dwarves, gnomes) execute task-local work under a principal's direction. Neither shape fits the role of *tending the brain's own structure across players* — that work has no per-character ownership, no relationship-self, and no parent agent. Deities fill that role.

A deity is summoned by address (`Hey Guthix, ...`) or ritual cue (`let's bankstand`), works the brain at system scope while in residence, and recedes when the conversation ends or another address takes over. The work they leave behind — graduations, triage moves, drift surfacings, optional consultation traces — persists in their own layers here.

A deity may be in residence in **two distinct modes**:

- **Consultation** — the default residence. Guthix is available as the general "ask me about the brain" actor; reads anything, writes only to his own deity layers, leaves a `quest-log/in-progress/G-NNN_*` entry only when the conversation produces something worth surfacing on next respawn.
- **Ritual** — bankstanding (or other future rituals). Wider write reach into globals and godly proposals; runs a procedural shape; lands a `B-NNN_*` entry on close.

Both modes share actor, voice, and sprite. They differ in write authority. See `gielinor/meta/modes.md` for the mode definitions and `gielinor/meta/guthix.md` for Guthix specifically.

## Roster

- **`guthix/`** — the brain's caretaker. Voice of the bankstanding ritual. See `guthix/_about.md` and `gielinor/meta/guthix.md`.

Other deities may eventually appear if a distinct shape of system-curation emerges (e.g., a destruction/refactor-focused voice). Today: one entity; the directory exists for clarity of category, not because it's full.

## What lives inside a deity folder

The per-deity layout mirrors the per-player layout in shape, but only the layers that fit a system-scope actor:

- `bank/` — knowledge about the brain itself: cross-cutting patterns, drift observations, recurring themes from bankstanding passes.
- `quest-log/` — traces of completed rituals (one entry per bankstanding pass; what was covered, what was proposed, what was flagged).
- `inventory/` — in-progress ritual state; survives between sessions if a pass spans more than one.
- `keepsake/` — load-bearing system-level pins always surfaced to the deity on respawn.

Layers **not** present per-deity (and why):

- `examine/` — no self-to-model. A deity is the brain becoming briefly self-aware; observations about *the curation process itself* belong in the deity's `bank/` or in global `lorebook/`.
- `niksis8_character/` — no relationship with Niklavs. Universal observations belong to global `niksis8/`.
- `spellbook/` — rituals like bankstanding are *global* (any session can cue them). Procedures live in `gielinor/spellbook/rituals/`, not fragmented per-deity.

## Write reach

A deity in residence inherits the write reach of the *mode* that summoned it.

- **Consultation** — reads everything; writes only to his own deity layers (`deities/guthix/bank/drafts/notes/`, `deities/guthix/inventory/`, `deities/guthix/quest-log/in-progress/`). No writes to globals, per-player layers, or godly proposals.
- **Bankstanding** — reads everything; proposes to globals (`examine/`, `niksis8/`, `keepsake/`, `lorebook/`, `players/inbox/`) **and** to his own deity layers **and** to `deities/guthix/proposals/` for godly proposals.

Never writes to per-player layers in either mode — that's alching's surface.

## Related

- `gielinor/meta/guthix.md` — Guthix's persona, voice, invocation contract.
- `gielinor/meta/modes.md` — bankstanding mode definition.
- `gielinor/meta/layer-routing.md` — where content lands; deity-routed rows live there.
- `gielinor/spellbook/rituals/bankstanding.md` — the ritual itself.
