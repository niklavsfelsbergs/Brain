# Spawning dwarves — skill

When to spawn parallel dwarves instead of working serially, how to brief them, and how to keep the principal reporting on progress while they run.

## When this fires

Two conditions:

1. **≥2 independent paths.** Sub-tasks that do not depend on each other's output. If path B needs path A's result, it's serial — do not spawn.
2. **At least one amplifier:**
   - **Scope size** — combined reads would crush context if done serially.
   - **Wall-time pressure** — deadline tight enough that serial wall-time matters.
   - **Context-bloat** — even one path's read alone is heavy enough to want isolation.

Both must hold. A two-path task with no amplifier is just two quick reads.

Concrete example (good): S002 shipping data mart — ClickUp tree + bi-etl scan + Redshift probe, three independent paths, V1 in 2 days, each path is a heavy read.

Concrete example (not dwarf-shaped): "read file X and update line 12" — one path, no parallelism.

## Pre-flight check

Before starting serial work on any multi-path task, evaluate: are the paths actually independent? Does an amplifier apply? If yes, propose dwarves in the Plan line. Do not just start serial — the principal may want to veto, but the call should be visible.

If the principal has explicitly asked for serial, respect that. The heuristic is a default, not a override.

## Briefing template

Per dwarf, before spawning:

- **Scope.** One sentence — what this dwarf is responsible for.
- **Reads.** Concrete paths / sources / queries.
- **Deliverable.** What file the dwarf writes, what sections it must contain.
- **Out of scope.** What this dwarf does *not* touch (prevents overlap with siblings).
- **Sibling file path.** Where the dwarf writes its quest-log entry — typically `quest-log/in-progress/SNNN_dN_<slug>.md` next to the parent quest.

Hook-enforced write boundary (see `meta/modes.md`) still applies: no `confirmed/`, no `drafts/`, no `spellbook/rituals/`, no sub-dwarf spawning.

## Channel — background by default

Dwarves are spawned with `run_in_background=true`. The principal returns control to the user **immediately** after spawning, with a manifest:

- One line per dwarf — ID, one-line scope, sibling file path.
- A close — "Ping me with 'status?' anytime. Synthesis when all return."

The principal does **not** block waiting for dwarves. The conversation stays alive.

## Status-on-ping

When the user asks for status (any phrasing — "status?", "where are we?", "how's it going?"), the principal:

1. Pulls task state for each dwarf — running, completed, failed.
2. Tails the sibling quest-log file for each running dwarf — **only the lines since the last status check**, not the whole file.
3. Reports one block per dwarf — state, last quest-log line, blockers if any.

Tail-since-last, not full-read. Otherwise status checks balloon principal context across long-running waves.

## Completion-weave

When a dwarf completes mid-conversation, the harness surfaces a notification. The principal weaves it into the **next response** — does not auto-resume work, does not jump to synthesis prematurely.

Synthesis is gated on **all** dwarves returning, unless the principal cues otherwise ("synthesize what we have, drop D3").

## Dwarf discipline — quest-log streaming

Each dwarf appends a brief turn-by-turn line to its sibling quest-log file as it works — not just the final deliverable. This is what gives status-on-ping something real to surface.

Currently discipline, not hook-enforced. Hardening deferred until real use shows drift.

## Anti-patterns

- **Single dwarf.** No parallelism gain — call the work directly in principal context.
- **Pseudo-independent paths.** If D2 needs D1's output to be interpretable, they're not parallel; you're hiding a sequence behind concurrent spawn.
- **Bulk-reading sibling on status check.** Tail since last check.
- **Auto-synthesizing on partial returns.** Wait for all.
- **Spawning to avoid thinking.** Dwarves are for parallelism, not for offloading a decision.

## Related

- `meta/modes.md` — the principal-vs-dwarf write boundary.
- `meta/communication-protocol.md` — the Plan-line annotation when this skill fires.
- `.claude/hooks/` — the architectural lines (dwarf write boundary, no sub-dwarf spawning).
