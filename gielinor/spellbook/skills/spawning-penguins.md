# Spawning penguins — skill

When to spawn a penguin instead of running research personally, how to brief one, and how to keep the principal reporting on progress while it runs.

See `gielinor/meta/modes.md` for the role definition and `gielinor/.claude/agents/penguin.md` for the agent config.

## What a penguin is

A **research-operative** sub-agent. Functional like a dwarf, but for external sources. Its write surface is the active player's `research/` folder; its tool surface adds `WebSearch` and `WebFetch`.

System namesake: in RS lore, penguins are intelligence operatives. They go past Gielinor's gates, gather intel, return with anchored findings. Same here — penguins do external research; dwarves do internal-repo work.

## When this fires — the spawn heuristic

Two conditions:

1. **External work required.** The question needs sources outside the brain — current state, regulations, vendor docs, news, anything `WebSearch` / `WebFetch` reaches. If the work is repo-bound, it's dwarf-shaped, not penguin-shaped.
2. **At least one amplifier:**
   - **Source-map size** — looks like >5 fetches; the read volume would crush principal context.
   - **Parallel clusters** — ≥2 independent source clusters (e.g., regulatory framework vs vendor landscape vs internal constraints).
   - **Wall-time pressure** — deadline tight enough that serial principal-self pacing matters.

Both must hold. A two-fetch lookup is just a lookup — don't spawn for it.

Concrete example (good): EU Tender 2026 research — three clusters (procurement law, member-state implementation timelines, vendor pricing). Spawn 3 penguins; weave findings.

Concrete example (not penguin-shaped): *"what's the current version of polars?"* — one fetch, do it inline.

Concrete example (dwarf-shaped, not penguin): *"scan bi-etl for all references to deprecated function X"* — repo-bound; dwarf.

## Pre-flight check

Before starting principal-self research on any external topic, evaluate: is this >5 fetches or ≥2 independent clusters? If yes, propose penguins in the Plan line (per `meta/communication-protocol.md` dwarf-spawn annotation, which applies to penguins too). The principal may want to veto; the call should be visible.

If the principal has explicitly asked for principal-self, respect that. The heuristic is a default, not an override.

## Briefing template

Per penguin, before spawning:

- **Topic.** One sentence — what this penguin is researching.
- **Active player.** Whose `research/` folder the writeup lands in. Default: the principal's player. Cross-player overrides are explicit (*"for Jebrim"*, *"for Zezima"*).
- **Question.** The specific question this penguin answers. Not the whole topic — the slice.
- **Source map (if pre-staged).** Bulleted list of candidate sources the principal already knows about. Optional.
- **Deliverable.** File path — typically `players/<player>/research/<YYYY-MM-DD>-<slug>.md`. Sections per `research.md` body shape.
- **Out of scope.** What this penguin does *not* touch (prevents overlap with siblings).
- **Sibling file path.** Where the penguin writes its run-log trace — `players/<player>/quest-log/traces/SNNN_pN_<slug>.md` (pN = penguin 1, 2, ...; [[B-020_2026-06-18_memory-cap-trim-and-graduation-retire|B-020]]: a sub-agent run-log is a *trace*, not a quest — `quest-log/traces/`, not `in-progress/`). The research writeup itself lands in `research/` per the Deliverable above.

**Read `meta/modes.md` now** before briefing — it left the eager `@import` chain (§X Stage B), so the penguin write boundary loads here, at spawn time. Hook-enforced boundary: `research/`, `quest-log/`, `inventory/` only. No `bank/`, no `drafts/`, no sub-spawning.

## Channel — background by default

Penguins are spawned with `run_in_background=true`. The principal returns control to the user **immediately** after spawning, with a manifest:

- One line per penguin — ID, topic, sibling file path.
- A close — *"Ping me with 'status?' anytime. Synthesis when all return."*

The principal does **not** block waiting for penguins. The conversation stays alive.

## Status-on-ping

When the user asks for status, the principal:

1. Pulls task state for each penguin — running, completed, failed.
2. Tails the sibling quest-log file for each running penguin — **only the lines since the last status check**, not the whole file.
3. Reports one block per penguin — state, last quest-log line, source-map size if visible.

Tail-since-last, not full-read. Otherwise status checks balloon principal context across long-running research waves.

## Completion-weave

When a penguin completes mid-conversation, the harness surfaces a notification. The principal weaves it into the **next response** — does not auto-resume work, does not jump to synthesis prematurely.

Synthesis is gated on **all** penguins returning, unless the principal cues otherwise (*"synthesize what we have, drop P3"*).

## Penguin discipline — quest-log streaming

Each penguin appends a brief turn-by-turn line to its sibling quest-log file as it works — not just the final deliverable. This is what gives status-on-ping something real to surface.

Currently discipline, not hook-enforced. Hardening deferred until real use shows drift.

## Anti-patterns

- **Single penguin for a one-fetch lookup.** No parallelism gain — call the `WebFetch` directly in principal context.
- **Pseudo-independent clusters.** If P2 needs P1's findings to interpret its own sources, they're not parallel; you're hiding a sequence behind concurrent spawn.
- **Bulk-reading sibling on status check.** Tail since last check.
- **Auto-synthesizing on partial returns.** Wait for all.
- **Spawning a penguin for repo-bound work.** That's dwarf territory. Penguins are for outside-the-gates.
- **Penguin writing into `bank/`.** Hook blocks; if a brief implies it, the brief is wrong. Picking happens during alching, not at research time.

## Related

- `meta/modes.md` — the penguin write boundary.
- `meta/communication-protocol.md` — the Plan-line annotation when this skill fires.
- `spellbook/skills/research.md` — the methodology penguins (and principals) use.
- `spellbook/skills/spawning-dwarves.md` — companion skill for repo-bound parallel work.
- `spellbook/skills/spawning-gnomes.md` — companion skill for structural housekeeping.
- `.claude/agents/penguin.md` — the agent config (system prompt + tools).
- `.claude/hooks/penguin-write-boundary.py` — the enforcement.
- `.claude/hooks/block-sub-spawn.py` — sub-spawn block.
