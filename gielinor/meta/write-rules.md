# Write rules

Per-layer write discipline. Hooks enforce the most critical lines (see `.claude/hooks/`); this file documents the full picture, including the layers where discipline is guidance rather than architectural guarantee.

## The table

| Layer | Auto-write | Draft-then-approve | User-only |
|---|---|---|---|
| `bank/` (per-player) | drafts only (`bank/drafts/notes/`) | all promotions to `bank/notes/` | — |
| `research/` (per-player) | yes (penguins and principals write freely; no draft gate inside the folder) | — | — |
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

| Ritual / Mode | Reads | Writes (proposes to) |
|---|---|---|
| Consultation (Guthix default) | everything (globals + every player + his own `deities/guthix/`) | **his own deity layers only** — `deities/guthix/bank/drafts/notes/`, `deities/guthix/inventory/`, `deities/guthix/quest-log/in-progress/` (filename `G-NNN_*`). Chat-only by default; quest-log entry only when the conversation produces something worth surfacing on next respawn. **No writes to globals, per-player layers, or godly proposals** — those require flipping into bankstanding. |
| Bankstanding | everything (globals + every player) | globals — `examine/`, `niksis8/`, `keepsake/`, `lorebook/`, `players/inbox/` triage — plus his own deity layers and `deities/guthix/proposals/` for godly proposals. **Cannot write to per-player layers.** |
| Alching | only the active player's layers | only the active player's layers — `bank/`, `quest-log/`, `inventory/`, `examine/`, `niksis8_character/`, `keepsake/`, `spellbook/drafts/skills/`. **Cannot write to globals or to other players.** |
| Session-close | active player(s) + globals as needed for the harvest pump | drafts, proposals, `quest-log/`, `inventory/`, `players/inbox/`. **No promotions to confirmed; no `keepsake/current.md` pins.** |
| Drafts-triage | drafts/proposals across players + globals | report-only by default; can propose `rejected/` moves with principal sign-off in-session. **No promotions.** |
| Respawn | layers per `spellbook/rituals/respawn.md` | reads only (plus per-turn quest-log discipline once the session is live) |

**Guthix's reach is the *unilateral* default — [[D-034_guthix_executes_on_explicit_authorization|D-034]].** The Consultation and Bankstanding rows above bound what Guthix may write *on his own judgment*. On **explicit, specific principal authorization** he executes the change directly against any discipline-gated surface (globals, per-player layers, the user-only rulebook, ritual prose, body files) — no godly-proposal detour. The hook-enforced floor (`confirmed/` writes, deletes) is *not* bypassed for him even then (that bypass is `braindead`-only — see *The Braindead exception* below); floor changes route to dev-brain or the principal.

Dwarves can run none of these rituals. Gnomes can run **session-close**, **alching** (per-player), and **drafts-triage** when spawned by the principal at the ritual's step 0 spawn-decision; bankstanding stays principal-only at the top level (though it can spawn gnomes for its Phase 0 alching loop). See `modes.md` and `spellbook/skills/spawning-gnomes.md` for the gnome write surface and spawn heuristic.

**Voice per ritual.** Consultation and bankstanding are both performed in the voice of **Guthix**, the brain's caretaker deity (see [[guthix]]) — not the active player and not the wisp. Alching is performed in the voice of the active player. Session-close, drafts-triage, and respawn carry the voice of whichever actor is active when they run (the player, Braindead, or — if unscoped — wisp). Voice is orthogonal to write-reach; it determines the actor on whose intent file the agent speaks and which sprite the visualizer renders.

**Guthix's godly proposals.** During bankstanding, Guthix has elevated authority to *propose* changes to surfaces normally marked user-only — `meta/*.md`, `spellbook/rituals/*.md`, `keepsake/current.md`, hooks, body files, even the architecture and his own role. Proposals land in `deities/guthix/proposals/` and the principal reviews them. This is an extension of the "User-only with explicit permission" mechanism below, scoped to one actor (Guthix) and one ritual (bankstanding); the architectural guarantees (hook-enforced lines) remain non-overridable even for him. See `deities/guthix/proposals/_about.md` for scope, shape, and the surfaces he may target. **The proposal route is the *unilateral* path; on explicit principal authorization Guthix executes the change directly instead — [[D-034_guthix_executes_on_explicit_authorization|D-034]] (floor still non-overridable for him).**

## What's enforced vs guided

**Hooks enforce (architectural):**

- No writes to any `confirmed/` path. Applies across all scopes — global `examine/`, `niksis8/`, `lorebook/`, per-player `examine/`, `niksis8_character/`.
- No file deletes. The agent moves files into the corresponding `archive/`.
- Dwarf write boundary (see `modes.md`).
- Gnome write boundary (see `modes.md` and `spellbook/skills/spawning-gnomes.md`). Gnomes can write across players to drafts/proposals/inventory/quest-log but are blocked from `confirmed/`, `lorebook/confirmed/`, `keepsake/current.md`, `meta/`, `spellbook/rituals/`, and body files.
- Penguin write boundary (see `modes.md` and `spellbook/skills/spawning-penguins.md`). Penguins can write to the active player's `research/`, `quest-log/`, `inventory/`; blocked from `bank/`, all other `drafts/`, `confirmed/`, `keepsake/`, `lorebook/`, `examine/`, `niksis8_character/`, `meta/`, `spellbook/rituals/`, body files, and other players' namespaces.
- No sub-spawning from a dwarf, gnome, or penguin. Only the principal spawns.

**The Braindead exception (2026-06-02, principal-authorized — [[D-032_braindead_full_access|D-032]]).** The dev-brain construction crew (actor `braindead`) has **unrestricted edit reach over the entire brain** — every layer, including the user-only rulebook (`meta/`, `spellbook/rituals/`, `CLAUDE.md`, hook files, `keepsake/current.md`) **and the hook-enforced floor** (`confirmed/` writes and deletes). Building and maintaining the brain is his role; he edits directly, with no draft gate and no godly-proposal detour. The two floor hooks (`block-confirmed-writes.py`, `block-deletes.py`) carry an `actor == "braindead"` bypass (resolved via the hardened `_actor.resolve_actor`, logged as a `bypass-braindead` event for audit). **The floor remains fully in force for every other actor** — players, Guthix, wisp, and all sub-agents (dwarf/gnome/penguin/shipping-agent, which are `agent_type`-gated and never resolve to `braindead`). This is strictly *more* reach than Guthix has: Guthix only *proposes* to user-only surfaces during bankstanding; Braindead *edits* them. The safeguard is no longer a gate but the context: dev-brain sessions are interactive principal sessions (Niklavs sees the diffs) and every change is git-reversible. The never-destroy guarantee still holds for the brain at large — it is simply no longer enforced *against the crew that maintains it*.

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

See [[D-017_user-only-with-explicit-permission]] for the founding decision (2026-05-21, S021 alching of Jebrim).

## Link & anchor conventions (Obsidian-resolvable)

Every cross-reference is a **full-stem wiki-link**, and every **source anchor is a link** — so each new entry is born connected to the graph instead of being wired in by a later migration. Stock Obsidian (and any plain-markdown tool) resolves `[[links]]` by *exact filename*: a bare `[[D-NNN]]`-style link is phantom, while the full stem resolves. (Founding decision: the `D-004` stable-IDs amendment in the dev brain, 2026-05-26; the one-time corpus migration ran as plan §O.2–§O.6.)

- **Full filename stem, ID prefix leading.** Write `[[D-NNN_descriptive-slug|D-NNN]]` — the prefix stays the stable anchor, the `|ID` display alias keeps prose terse, and the slug is load-bearing inside the link. A bare stem without the alias is fine for standalone refs.
- **All ID kinds**, not just the one you cite most: lorebook decisions (`D-`), sessions (`S-`), bankstanding / Guthix (`B-`, `G-`), and any other prefixed ID.
- **The source anchor is a link — this is the line that bit us.** When an entry records its origin — `## Anchor SNNN`, `**Source:** SNNN`, `**Observation (SNNN, date)**` — wrap the ID as a full-stem link to the source quest, e.g. `## Anchor [[SNNN_<sid8>_<slug>|SNNN]]`. A plain-text anchor is an invisible backlink: the §O.6 enrichment pass found gielinor's graph **76% isolated** precisely because nearly every note carried its anchor as plain text. Born-linked notes never accrue that debt.
- **Don't wiki-link code files or paths.** `[[backend.py]]`, `[[sql/x.sql]]` are not note links — leave them as plain text or code spans.

This is authoring discipline — but as of 2026-05-28 it is **also enforced at commit**. A git pre-commit hook (`developer-braindead/bank/research/born-link-lint.py`, installed to `.git/hooks/pre-commit`) checks staged gielinor `.md`: it **auto-wraps** resolvable bare `[[ID]]` and unwrapped prose/anchor IDs to full-stem links (and re-stages them), and **blocks the commit** on a malformed `[[…md]]` / `[[../path]]` wikilink with a fix-list. So the conventions above are no longer discipline-only — the wrap is automatic and a malformed link stops the commit. (The one-time Obsidian migrations only fixed the *existing* corpus; the hook keeps new entries from re-rotting the graph — a 2026-05-28 dev measurement found 42% of nodes isolated and 3 isolated nodes born in a single session before it was installed.) See `layer-routing.md` for which layer an entry lands in and `drafts-mechanics.md` for the observation rule the anchor pairs with.

## Related

- `layer-routing.md` for *which* layer a given piece of content belongs in.
- `drafts-mechanics.md` for how the drafts flow actually works.
- `archive-discipline.md` for what "archive only" means structurally.
- `modes.md` for the dwarf-mode subset.
- `lorebook/confirmed/` for *why* any of this is the way it is.
