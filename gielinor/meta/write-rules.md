# Write rules

Per-layer write discipline. Hooks enforce the most critical lines (see `.claude/hooks/`); this file documents the full picture, including the layers where discipline is guidance rather than architectural guarantee.

## The table

| Layer | Auto-write | Draft-then-approve | User-only |
|---|---|---|---|
| `bank/` (per-player) | drafts only (`bank/drafts/notes/`) | all promotions to `bank/notes/` | — |
| `quest-log/` (per-player) | yes (sessions log themselves turn-by-turn) | — | — |
| `spellbook/skills/` (per-player) | drafts only (`spellbook/drafts/skills/`) | all promotions to `spellbook/skills/` | — |
| `spellbook/rituals/` (global and per-player) | — | — | yes — core rituals are user-edited |
| `inventory/` (per-player) | yes (volatile) | — | — |
| `examine/` (global and per-player) | drafts only | all promotions to `confirmed/` | direct edits to confirmed entries |
| `niksis8/` and `niksis8_character/` | drafts only | all promotions to `confirmed/` | direct edits to confirmed entries |
| `keepsake/` (global and per-player) | proposals only (`keepsake/proposals/`) | all pinning to `current.md` | all edits to `current.md` |
| `lorebook/` | drafts only (`lorebook/drafts/`) | all promotions to `confirmed/` | direct edits to confirmed entries |
| `meta/*.md` | — | — | yes |

## The principle

Anything that defines who the agent thinks I am, who the agent (or a player) thinks it is, or what has been decided about the system requires my sign-off. Knowledge accumulates via drafts that I review during alching.

Observations enter the brain freely as drafts. Promotion to canonical knowledge — identity, character, decisions, and per-player bank — is gated.

## Ritual write-reach

Three principal-only rituals each have a bounded write surface, layered on top of the table above. The table above governs *what discipline applies to a write*; the ritual reach governs *which layers a write can touch at all in that ritual*.

| Ritual | Reads | Writes (proposes to) |
|---|---|---|
| Bankstanding | everything (globals + every player) | globals only — `examine/`, `niksis8/`, `keepsake/`, `lorebook/`, `players/inbox/` triage. **Cannot write to per-player layers.** |
| Alching | only the active player's layers | only the active player's layers — `bank/`, `quest-log/`, `inventory/`, `examine/`, `niksis8_character/`, `keepsake/`, `spellbook/drafts/skills/`. **Cannot write to globals or to other players.** |
| Session-close | active player(s) + globals as needed for the harvest pump | drafts, proposals, `quest-log/`, `inventory/`, `players/inbox/`. **No promotions to confirmed; no `keepsake/current.md` pins.** |
| Drafts-triage | drafts/proposals across players + globals | report-only by default; can propose `rejected/` moves with principal sign-off in-session. **No promotions.** |
| Respawn | layers per `spellbook/rituals/respawn.md` | reads only (plus per-turn quest-log discipline once the session is live) |

Dwarves can run none of these rituals. Gnomes can run **session-close**, **alching** (per-player), and **drafts-triage** when spawned by the principal at the ritual's step 0 spawn-decision; bankstanding stays principal-only at the top level (though it can spawn gnomes for its Phase 0 alching loop). See `modes.md` and `spellbook/skills/spawning-gnomes.md` for the gnome write surface and spawn heuristic.

**Voice per ritual.** Bankstanding is performed in the voice of **Guthix**, the brain's caretaker deity (see [[guthix]]) — not the active player and not the wisp. Alching is performed in the voice of the active player. Session-close, drafts-triage, and respawn carry the voice of whichever actor is active when they run (the player, Braindead, or — if unscoped — wisp). Voice is orthogonal to write-reach; it determines the actor on whose intent file the agent speaks and which sprite the visualizer renders.

## What's enforced vs guided

**Hooks enforce (architectural):**

- No writes to any `confirmed/` path. Applies across all scopes — global `examine/`, `niksis8/`, `lorebook/`, per-player `examine/`, `niksis8_character/`.
- No file deletes. The agent moves files into the corresponding `archive/`.
- Dwarf write boundary (see `modes.md`).
- Gnome write boundary (see `modes.md` and `spellbook/skills/spawning-gnomes.md`). Gnomes can write across players to drafts/proposals/inventory/quest-log but are blocked from `confirmed/`, `lorebook/decisions/`, `keepsake/current.md`, `meta/`, `spellbook/rituals/`, and body files.
- No sub-spawning from a dwarf or gnome. Only the principal spawns.

**CLAUDE.md guides (discipline):**

- The "draft-then-approve" rows above. Hooks don't distinguish a proposed promotion from a routine edit, so the agent has to follow the draft flow on its own.
- The bank drafts gate. `bank/notes/` is not hook-enforced; the agent has to write only to `bank/drafts/notes/` on its own and let alching promote. Pattern parallel to identity-layer drafts but without the hook. Reopen if discipline slips.
- The skills drafts gate (added 2026-05-21 via S018 audit). `spellbook/skills/` is not hook-enforced; the agent writes to `spellbook/drafts/skills/` and alching promotes. Replaces the earlier "skills go through `gielinor/lorebook/drafts/`" routing, which was heavyweight for per-player methodology.
- The "overturning existing knowledge" path in `bank/`. A new draft that contradicts an existing `bank/notes/` entry surfaces the contradiction during alching review — either the new draft wins (old note archives) or the new draft is rejected. Major shifts in how the agent operates still warrant a `lorebook/drafts/` entry.
- Treating `meta/` as user-controlled. Hooks could enforce this; for now it's discipline.

## "User-only" with explicit permission

The "User-only" column above is the **default**, not an architectural prohibition. When the principal explicitly authorizes a write to `keepsake/current.md`, `meta/*.md`, or `spellbook/rituals/*.md`, the agent makes the write directly.

Default holds without explicit permission: propose via the appropriate gate (`keepsake/proposals/` for pins; surface the proposed text in chat for `meta/` and `spellbook/rituals/` edits) and let the principal do the edit.

**Not overridable:** hook-enforced lines remain architectural regardless of permission — no writes to `confirmed/`, no deletes, dwarf/gnome write boundaries, no sub-spawning from dwarf/gnome. The user-only override applies *only* to discipline rules, not to the five architectural guarantees in `gielinor/CLAUDE.md`.

The check is *explicit*, not inferred. "Yes, write it" / "go ahead, apply the fix" / "do it" in response to a specific proposal counts. Ambient cooperation, agreement on the substance, or a "sounds good" reaction to general discussion does not.

See [[D-017]] for the founding decision (2026-05-21, S021 alching of Jebrim).

## Related

- `layer-routing.md` for *which* layer a given piece of content belongs in.
- `drafts-mechanics.md` for how the drafts flow actually works.
- `archive-discipline.md` for what "archive only" means structurally.
- `modes.md` for the dwarf-mode subset.
- `lorebook/decisions/` for *why* any of this is the way it is.
