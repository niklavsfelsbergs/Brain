# S041 — 2026-05-22 — Parallel player coordination design (D-024)

> Short dev-brain session. Principal asked whether anything enforces parallel player sessions not stepping over each other. Walked the existing guards ([[D-017]] / [[D-018]] / [[D-019]] / [[D-020]]), identified the disk-side gaps D-019 explicitly punted, drafted [[D-024]] as a design proposal. No scaffolding, no hook changes, no visualizer changes — design doc only.

## What landed

- `developer-braindead/bank/decisions/D-024_parallel_player_coordination.md` — the decision draft.
  - Shared `gielinor/comms/active.md` (one file, all players + Guthix), same protocol as the dev-brain comms.
  - Liveness via the [[D-020]] status sidecar (`state ≠ ended AND last_event_ts < 5min`), not intent-file mtime — strictly stronger per S032 carry-forward.
  - Session-suffix only true state files: `inventory/<topic>__<sid8>.md` and `quest-log/in-progress/SNNN_<sid8>_<slug>.md`. Drafts stay plain.
  - Respawn rule for inventory recovery: own sid8 first, else surface live-sibling candidates to principal.
  - Tolerated: SNNN race window, draft filename collisions. Deferred: cross-brain (player ↔ Braindead) coordination — same posture D-019 took.

## What didn't ship

- **No scaffolding of `gielinor/comms/`.** Decision-only session.
- **No ritual updates.** `respawn.md` and `close-session.md` in `gielinor/spellbook/rituals/` untouched.
- **No `meta/layer-routing.md` updates** for the new suffixed shape (principal touched layer-routing.md mid-session for an unrelated ideas-folder row; the D-024 suffix update is a separate pass).

## Observations worth carrying

- **D-019 documented the gap two decisions ago.** Its §"Out of scope for the first cut" §4 says "Jebrim and a Braindead session running in parallel … might collide on intent ... The current architecture has no answer; leave for a future decision." Half-true now — D-024 covers parallel players, still no cross-brain bridge. Pattern: deferred-branch debt is the first place to look when a parallel-session question lands.
- **Pressure-test before drafting.** Principal asked "will this work?" before committing the draft. The honest answer surfaced three soft spots (inventory recovery rule needed, SNNN race tolerated, cross-brain still nothing) that would have been embarrassing to find later. Cheap turn; high yield.
- **D-020 keeps paying off.** The status sidecar — built for the switchboard UI — turned out to be the right liveness signal for D-024. S032 already flagged this. Infrastructure that earns multiple uses without modification is a strong signal it sat at the right abstraction.

## Cascade

`developer-braindead/bank/decisions/D-024_parallel_player_coordination.md` (new), `developer-braindead/quest-log/S041_parallel_player_coordination_design.md` (this file), `developer-braindead/respawn.md` (updated), `developer-braindead/comms/active.md` (CLOSING entry appended), `brain/.claude/active-mode.txt` (set then cleared).

## Main-brain changes

None. D-024 proposes main-brain changes (`gielinor/comms/active.md`, ritual updates, suffix conventions) but doesn't land them. Layer-routing and CLAUDE.md edits during this session were principal-driven and unrelated to D-024.
