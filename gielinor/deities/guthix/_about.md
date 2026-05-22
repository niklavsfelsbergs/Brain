# guthix/

> The brain's caretaker. This folder is his on-disk presence — the only persistent state of a deity who is otherwise transient.

See `gielinor/meta/guthix.md` for persona, voice, write reach, and invocation contract. This file documents the on-disk layout.

## Layers

```
guthix/
  _about.md             # this file
  bank/                 # cross-cutting knowledge
    _about.md
    drafts/notes/       # observations awaiting bankstanding review
    notes/              # promoted knowledge; canonical
  quest-log/            # one entry per bankstanding ritual run
    _about.md
    in-progress/        # active ritual entry; appended every turn
    completed/          # finished ritual entries
    archive/            # abandoned or aged entries
  inventory/            # in-progress ritual state (volatile-ish; survives ritual but not reset)
    _about.md
  keepsake/             # load-bearing system-level pins
    _about.md
    proposals/          # proposed pins
    current.md          # active pins surfaced on Guthix respawn
  proposals/            # godly proposals — anything in the system, no scope limit
    _about.md
    rejected/           # rejections preserved (archive discipline)
```

## What goes where

- **`bank/`** — Patterns Guthix has noticed across the brain. "Players X and Y both have stale shipping-data drafts dating from before the schema change." "The respawn ritual is referenced from N files but the load order isn't enumerated in any single place." Cross-cutting; system-scope; not per-player.
- **`quest-log/`** — One file per bankstanding pass. Filename: `B-NNN_YYYY-MM-DD_<slug>.md` (B for *bankstanding*; the counter is for Guthix's own ritual history, distinct from any player's S-NNN). The entry records what he covered, what he proposed, what he flagged for follow-up.
- **`inventory/`** — Resume state for the *current* bankstanding pass: "Phase 0 done for Jebrim, Zezima next." "Drafts triage covered examine/, niksis8/ remaining." When the ritual closes cleanly, this clears or moves to the matching quest-log entry. When the ritual spans sessions, this is what next-session-Guthix reads first.
- **`keepsake/`** — Pins that should always surface to Guthix at respawn. "Last bankstanding was 8 sessions ago — overdue." "Player Z's bank hasn't grown since 2026-04-12; check if quiet by design or quiet by neglect."
- **`proposals/`** — Godly proposals for *changes* to how the system is structured. Architectural shifts, meta-rule changes, ritual changes, even self-modifying changes to Guthix's own role. Drafted only during bankstanding. The principal reviews and lands or rejects. See `proposals/_about.md` for scope and shape.

## Discipline

The draft-then-promote pattern from per-player `bank/` applies here. New observations land in `bank/drafts/notes/`; review (next bankstanding) promotes to `bank/notes/`. The `_guthix_session_id` marker in `state-actors.json` ensures only the in-residence Guthix-session writes — parallel sessions can't see this surface.

## What does not live here

- Decisions about how the brain *operates going forward* — those belong in global `gielinor/lorebook/drafts/` and graduate to `lorebook/decisions/D-NNN_*.md` with principal approval. Guthix proposes; the principal decides.
- Per-player knowledge — never written here. Guthix may *read* a player's bank but does not write into it (alching's surface).
- Ritual procedure — `gielinor/spellbook/rituals/bankstanding.md` holds the procedure; this folder holds the *output* of running it.

## Related

- `gielinor/deities/_about.md` — why deities exist as a category.
- `gielinor/meta/guthix.md` — persona, voice, write reach.
- `gielinor/meta/layer-routing.md` — full mapping of content-shape to layer.
- `gielinor/meta/modes.md` — bankstanding mode definition.
