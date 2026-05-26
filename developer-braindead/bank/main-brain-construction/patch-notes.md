# lorebook/patch-notes.md — factual record of changes

> Auto-appended. A factual log of substantive changes to the system — structure, conventions, decisions landed, bankstanding runs. Distinct from `quest-log/` (which records what happened in a session); this records what changed in the *system*.

## Format

```
## YYYY-MM-DD — <one-line summary>

<paragraph of what changed and why, with cross-links to D-NNN decisions and quest-log entries>
```

Most-recent entries at the top.

## Entries

*(new entries appended above the Day 0 entry)*

## 2026-05-20 — Player invocation rule changed to address-based

[[D-002_player_invocation_by_address]] landed. Player selection moved from a preemptive "which player?" prompt at session start to **address at message start** (`Hey Zezima, ...`, `Hey Jebrim, ...`, `Hey unscoped, ...`). Sticky after addressing. Strict matching — case-insensitive on name, must be at message start, no fuzzy match.

Files changed:
- `CLAUDE.md` — added section *Player invocation by address*.
- `spellbook/rituals/respawn.md` — step 2 rewritten; mini-respawn section clarified to trigger on addressing.

Supersedes [[D-001_phase-1-scaffold]]'s respawn step 2.

## 2026-05-20 — Day 0: gielinor scaffolded

The brain was born today. Phase 1 scaffolding landed:

- Body files at the root (`CLAUDE.md`, `CLAUDE.local.md`, `.mcp.json`, `ticks.md`).
- `meta/` rulebook (`write-rules`, `modes`, `archive-discipline`, `drafts-mechanics`, `death-and-spawn`), imported by `CLAUDE.md`.
- Global cognitive layers (`examine/`, `niksis8/`, `keepsake/`, `lorebook/`, `spellbook/`) each with `_about.md`.
- Rituals (`spellbook/rituals/respawn.md`, `spellbook/rituals/bankstanding.md`).
- Players system (`players/_about.md`, `players/inbox/`) with initial roster: `zezima/` and `jebrim/`. Each player has the full sub-layer template, minimal `_about.md` + `persona.md` + `CLAUDE.md`, and per-layer `_about.md` files.
- Four hooks in `.claude/hooks/` (portable Python), wired via `.claude/settings.json`.
- `niksis8/confirmed/current.md` seeded: "My name is Niklavs." All other `current.md` files are empty placeholders with one-line headers.
- Founding decision [[D-001_phase-1-scaffold]] recorded.

Build session: see the dev brain's [[S003]] for the narrative.

The brain is **0 days old** at landing. Counting starts here.
