---
id: D-001
title: Phase 1 scaffold — the shape of the brain at birth
date: 2026-05-20
status: confirmed
---

# D-001 — Phase 1 scaffold

**Date.** 2026-05-20. **Status.** confirmed (founding decision).

This is the founding decision. The brain's birthdate. Day 0.

## Question

What shape does the main brain (gielinor/) take on its first day, and what principles govern that shape?

## Ruling

A personal AI agent built as a structured markdown brain organized around RuneScape-themed cognitive layers, with two scopes (global and per-player), four architectural hooks, and an initial roster of two players (Zezima and Jebrim). The body — `CLAUDE.md`, `CLAUDE.local.md`, `.mcp.json`, `ticks.md` — is user-edited; the brain layers grow through use under explicit write rules.

### Structure landed today

- **Body files** at the gielinor/ root: `CLAUDE.md` (master, imports the rulebook from `meta/`), `CLAUDE.local.md` (gitignored), `.mcp.json` (empty), `ticks.md` (dormant, scheduling slot).
- **Hooks** in `.claude/hooks/`: four portable Python scripts enforcing (1) no writes to `confirmed/`, (2) no deletes, (3) dwarf write boundary, (4) no sub-dwarf spawning. Wired via `.claude/settings.json`.
- **`meta/`** — current rulebook (write rules, modes, archive discipline, drafts mechanics, death-and-spawn). Imported by `CLAUDE.md`.
- **Global cognitive layers** — `examine/`, `niksis8/`, `keepsake/`, `lorebook/`, `spellbook/`. Each has an `_about.md`.
- **`spellbook/rituals/`** — `respawn.md` and `bankstanding.md` defined.
- **`players/`** — `_about.md` documenting the system, an `inbox/`, and per-player namespaces for `zezima/` (personal life, reading, reflection) and `jebrim/` (work, focused analytical execution). Each player has the full sub-layer template plus minimal `_about.md`, `persona.md`, and `CLAUDE.md`.

### Initial content

- `niksis8/confirmed/current.md` seeded with: "My name is Niklavs."
- All other `confirmed/current.md` and `keepsake/current.md` files are empty placeholders with one-line headers explaining what they're for.
- `lorebook/assumptions.md` empty, with a format spec for future entries.
- `lorebook/patch-notes.md` gets a Day 0 entry.
- All `_about.md` files written.

## Alternatives considered

- **Front-load `niksis8/confirmed/current.md`** with a briefing on Niklavs (role, life context, communication preferences). Rejected. Risk of installing claims the agent should be earning through observation. The seed stays "My name is Niklavs."
- **Full biographies for Zezima and Jebrim** in their `_about.md` and `persona.md`. Rejected. Same reason — characters develop through use; over-specifying voice up front would either constrain or quickly drift from real behavior.
- **One-shot ingestion** of Jebrim's source repos (`bi-analytics-main/NFE/`, `bi-etl/`) into his `bank/`. Rejected. Bank grows through real work, not via passive scraping. Notes link back to source paths; the repos remain the source of truth.
- **Spec the deferred mechanisms** (`/drafts` command shape, bankstanding triggers, crash-reconciliation prompt wording, `inventory/` mechanics, cross-player retrieval) before scaffolding. Rejected. Theoretical design without real use produces brittle specs. Defer to real use.
- **`meta/` collapsed into `lorebook/conventions/`.** Rejected. Two lifetimes: `meta/` is the current rulebook (rewrites in place); `lorebook/` is history (only grows). Keeping them distinct preserves the asymmetry.
- **PowerShell hooks** (Windows-native). Rejected in favor of portable Python. The brain may travel to a different substrate in Phase 3; hooks should travel with it.

## Reasoning

The hard parts of this design are not the folder shape — they're the discipline rules. The folder shape exists to *anchor* the rules: each `_about.md` reminds the agent what belongs in this layer and how to write to it; each `meta/*.md` file states a rule that CLAUDE.md re-imports every session; each hook guarantees a line that cannot be crossed regardless of agent intent.

Most folders start empty by design. The goal is **structure-first** — the agent knows where things go when they happen. Pre-filling content would either install claims that haven't been earned, or shape future content to match the pre-fill rather than reality.

The four hook lines (no `confirmed/` writes, no deletes, dwarf write boundary, no sub-dwarf spawn) define the trust boundary. Inside the boundary, the agent has wide latitude — drafts, bank notes, quest-logs, inventory, patch-notes all auto-write. Outside, the principal is the only mover.

Players are characters, not personas of Niklavs. Zezima and Jebrim are named deliberately — historical RuneScape figures whose registers (patience and depth; focus and grind) match the domains they serve. Cross-player invocation (dwarf in another player's namespace) is allowed, must be explicit, and writes to the inherited player's quest-log.

## Cross-references

- `meta/write-rules.md` — the per-layer write discipline this decision encodes.
- `meta/modes.md` — principal vs dwarf, the orthogonality with players.
- `meta/archive-discipline.md` — the never-delete rule that hook #2 enforces.
- `meta/drafts-mechanics.md` — the draft/confirmed/rejected flow.
- `meta/death-and-spawn.md` — what survives crash and reset.
- `spellbook/rituals/respawn.md` — the session-start ritual.
- `spellbook/rituals/bankstanding.md` — the reorganization ritual.
- `players/_about.md` — players system + roster.
- The dev brain's session [[S003_main_brain_phase_1_scaffold]] for the build narrative.

## Open at landing

The deferred mechanisms (cited under "Alternatives considered" above) remain to be designed against real use. They are explicitly *not* blockers for Phase 1 operation; the system is meant to run with them undefined until friction surfaces the right shape.
