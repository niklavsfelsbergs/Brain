# S086 — full technical documentation of the brain system

**Session:** braindead-e668ec7e · 2026-05-24 · dev-brain via "lets develop gielinor"
**Status:** IN PROGRESS — docs tree built, awaiting principal review + commit decision.

## Ask

Principal: "build a full technical documentation of the brain system. About the cockpit
just a section of how it enables working with the brain system. Let me know what you would
include in it."

## Scope (confirmed via AskUserQuestion, all 3 = recommended defaults)

- **Audience:** the principal + future sessions (a navigable architecture reference).
- **Home & shape:** repo-root `docs/` tree, multi-file with an index.
- **Depth:** comprehensive **map that links out** to canonical files (meta/, _about.md,
  rituals) rather than copying them — so it won't drift.

## What was built — `docs/` (12 files)

README (index/navigation/map-not-territory principle) + 01-orientation, 02-glossary,
03-layers-and-memory, 04-write-discipline, 05-actors-and-modes, 06-rituals,
07-communication-and-coordination, 08-enforcement-and-hooks, 09-cockpit (the one
"how you drive it" section), 10-dev-brain, 11-appendix (ideas/body files/source x-ref index).

Method: 3 read-only recon dwarves (rituals / hooks+machinery / cockpit+actors) sourced the
clusters not already in context; Braindead authored all 12 files for single-author
coherence and cross-linking. All ~45 individually-linked source files verified to exist
(link-check clean). No `gielinor/` or `cockpit/` writes — docs only.

## Notable facts the recon surfaced (folded into the docs)

- **S085** wired the enforcement hooks at brain-root `.claude/settings.json` with absolute
  paths — the six guarantees were previously prompt-discipline-only for brain-root/cockpit
  sessions (an `rm` at brain root was proven not blocked). Role hooks (dwarf/gnome/penguin)
  are inert for a principal (gated on `agent_type`, absent on principal calls) → a principal
  is constrained only by block-confirmed-writes + block-deletes.
- **Bug documented (not fixed):** `emit-commit-event.py` still writes to the legacy
  `experiments/visualizer/state.ndjson`; every other hook moved to `switchboard/` in S052.
  Commit events land in the stale stream. Flagged in docs/08.
- Cockpit billing rationale (2026-06-15 headless metering → real PTY stays on subscription)
  is the load-bearing "why" of the cockpit; captured in docs/09.

## Open / next

- Principal review of the docs tree; then **commit** (not done — global rule "ask before
  committing"; not in a close ritual yet).
- If kept: a one-line pointer could be added to `developer-braindead/respawn.md` / the
  root README, and `bank/` could note the docs/ artifact exists. Deferred to principal.
- The `emit-commit-event.py` legacy-path bug is now documented — could be a quick future fix.

## Comms

OPEN + UPDATE posted (e668ec7e). No live Braindead siblings the whole session; one
ABANDONED candidate (5f93bb32, read-only Codex triage = S085, no collision). active-mode.txt
left `dev-brain`.
