# S025 — Parallel player instances (D-017 implementation)

**Date.** 2026-05-22.
**Mode.** Dev-brain.
**Outcome.** D-017 designed and shipped end-to-end in one session. Validated live on first run.

## What was asked

Principal flagged a recurring friction: running two sessions of the same player in parallel (typically two Jebrim sessions) caused the visualizer to merge them onto one sprite — intent bubbles overwrite each other, COMMS lines interleave without disambiguation, move events fight for the sprite's position. The fix proposed earlier in [[S024]]'s thread was "papering over" each symptom at the attribution layer; what was needed was a structural change to render the parallel sessions as separate entities.

Principal chose three design knobs during the conversation: 5-minute idle OR session-end despawn, tint-based differentiation, both instances active.

## What was decided ([[D-017]])

A new ID layer for the visualizer: each parallel session of a player gets an `instance` number (1, 2, 3 ...) resolved from session_id. Per-instance sprite, per-instance intent file, per-instance bubble, per-instance COMMS prefix. Sub-agents (dwarves, gnomes), wisp, and braindead stay single-instance for now.

Wrote `bank/decisions/D-017_parallel_player_instances.md`. The decision doc covers naming convention, despawn triggers (idle timer load-bearing, SessionEnd hook bonus per the `claude-code-guide` agent's research), file-schema changes, and explicit out-of-scope items (cross-instance dwarf delegation, accessibility check, sprite collision).

## What was built

### Hook (`developer-braindead/.claude/hooks/emit-event.py`)

- **`PLAYER_ACTORS`** constant — `{"jebrim", "zezima"}`. The actor list that can fork into instances; everything else stays at instance 1.
- **`INSTANCES_PATH`** + **`state-instances.json`** — registry of `(actor, session_id) → instance_number`. Persisted across hook invocations.
- **`resolve_instance(actor, session_id)`** — looks up existing assignment or allocates the next available number. Returns 1 for non-player actors / missing session_id.
- **`append(event)`** auto-stamps `instance` on events whose `actor` is a player. Backwards compat: events without `instance` field default to 1 in the visualizer.
- **`_intent_file_candidates()`** — read-order for per-session intent files: `<actor>-<sid8>.txt` first, fallback `<actor>.txt`.
- **`handle_intent_write()`** parses optional session suffix from intent filename, routes to writing session's instance via append's auto-stamp.
- **`_reemit_intent_after_move()`** updated to read the right per-instance file.
- **`handle_session_end()`** — new handler for SessionEnd payloads. Emits `despawn-instance` events for every instance bound to the ending session and frees the slot in the registry.

### Settings (`brain/.claude/settings.json`)

- **New `SessionEnd` hook entry.** Routes to the same `emit-event.py` script. Best-effort signal per Claude Code docs — fires on graceful exits (`prompt_input_exit`, `clear`, `resume`, `logout`, `other`) but not on forced kills.

### Visualizer (`developer-braindead/experiments/visualizer/index.html`)

- **Routing helpers** — `instanceKey(actor, instance)`, `parseInstanceKey(key)`, `actorBaseName(id)`. Instance 1 keeps the bare actor name (so static-HTML `actor-jebrim` continues to work); 2+ get `-N` suffix.
- **`actorDisplayName()`** now renders `Jebrim·2` when the id has an instance suffix.
- **`spawnPlayerInstance(actor, instance, at)`** — creates a tinted secondary sprite with the SMIL breath animation, an `instance-badge` text element above the head, and a unique element ID. Picks the tint class from a 3-variant cycle.
- **`despawnPlayerInstance(actorKey)`** — fade-out + cleanup of state-map entries.
- **`ensureActorExists()`** extended to spawn parallel player instances on demand.
- **`applyEvent()`** all relevant cases (`move`, `intent`, `action`) compute `actorKey = instanceKey(ev.actor, ev.instance)` and route state-map lookups through it. New case `despawn-instance` handles explicit SessionEnd despawns.
- **`instanceLastEventAt[]`** tracker — updated on every event with an actor.
- **`despawnIdleInstances()`** — sweeps every 30s, fades out instances with no events for 5+ minutes.
- **CSS tint classes** `.parallel-instance.tint-{2,3,4}` — initially shipped with subtle `+25°` hue-rotate. Principal feedback: indistinguishable. Bumped to `+140°/+220°/+80°` with saturation/brightness tweaks. Face shifts too — accepted cost of whole-sprite filter rather than masking skin.
- **`.day-night-overlay`** already existed (Q-008); no change. New animations gated under the existing reduced-motion media query.

## Validation

Validated **live on first run**. Before completing the visualizer edits, `tail state.ndjson` already showed two parallel Jebrim sessions stamped with `"instance":1` and `"instance":2` from the hook's auto-stamp:

```
{"actor":"jebrim","sessionId":"2cc4a3ad-...","instance":1, ...}
{"actor":"jebrim","sessionId":"69ab9081-...","instance":2, ...}
```

And `state-instances.json` registry persisted:

```json
{"jebrim": {"next": 3, "byId": {"2cc4a3ad-...": 1, "69ab9081-...": 2}}}
```

Principal hard-refreshed the visualizer mid-session and confirmed: second Jebrim sprite renders, badge legible, COMMS shows `Jebrim·2:` prefixes, bubble pops over the right instance. First tint pass at +25° was too subtle; bumping to +140° gave clear differentiation.

## Observations worth keeping

**Live-development found the design's UX gap, not the static design.** D-017 specified "tint per instance" with no number on how much shift. First implementation went small (+25°) for accessibility caution; principal couldn't see the difference. The design doc updated to require strong shifts. Pattern: when a design ducks a magnitude question with "tint" instead of "tint by N°", the implementer's first guess is usually too conservative.

**Two parallel Jebrim sessions were already running while we coded the support for them.** A `tail state.ndjson` showed the hook stamping `instance:2` on Jebrim's parallel session before the visualizer side was even merged. The hook side ran in production immediately on every PostToolUse — same workflow as S023's session-gating fix. No special deployment path.

**`claude-code-guide` agent's research was correct and saved a wrong default.** Claude Code's SessionEnd hook exists but is best-effort only — confirmed via the docs. Original D-017 draft would have made it load-bearing; the research forced the right design where the idle timer is the contract and SessionEnd is the speedup.

**The instanceKey() abstraction is doing all the work.** Adopting "instance 1 = bare actor name" as the convention meant the static-HTML jebrim/zezima elements needed zero changes; only instance 2+ paths are new. Most of the visualizer touched lines look like `const actorKey = instanceKey(ev.actor, ev.instance);` followed by mechanical s/ev.actor/actorKey/. Low risk for a sweeping change.

**Hue-rotate on whole sprite shifts skin tone too.** Acceptable for a first cut — the cost of selective tinting is restructuring the sprite into clothing vs skin groups, which is a bigger change than this feature justified. If two Hulk-faced Jebrims become a complaint, that's the next step.

## Files touched

- `developer-braindead/bank/decisions/D-017_parallel_player_instances.md` (new)
- `developer-braindead/.claude/hooks/emit-event.py` (+~95 lines)
- `developer-braindead/experiments/visualizer/index.html` (+~110 lines)
- `brain/.claude/settings.json` (+ SessionEnd entry)
- `developer-braindead/quest-log/S025_parallel_player_instances.md` (this file)
- `developer-braindead/respawn.md` (updated at session close)

## Tail observation — parallel-session git-index race

This session's own commit got eaten by Jebrim's parallel session. While I was writing this quest-log entry, Jebrim's session ran a broad `git add` and then `git commit`, which swept up my dev-brain changes alongside his CSV-export work. The combined commit landed as `5ec5c4c "CSV export rework: unified helper + 9 new buttons (quest log)"`, which contains:

- D-017's decision doc, hook changes, visualizer changes, settings.json, respawn.md update, AND this quest-log file (all mine)
- Plus Jebrim's actual CSV export work in `gielinor/`

The work is safely in the repo, just under a misleading commit message bundled with Jebrim's. No data loss.

**The shape of this race.** D-017 fixed parallel-session visibility *in the visualizer*. It did **not** fix parallel-session interference *at the filesystem / git layer*. Two sessions sharing a working tree share a git index — whichever one calls `git add -A` first sweeps up everything that's staged and stages everything that isn't. The downstream `git commit` then captures whatever's in the index, regardless of authorship intent.

**Worth recording as a `bank/decisions/` candidate at next bankstanding.** Likely shape: *parallel sessions should commit with explicit paths only, never `git add -A` / `git add .`*. The global CLAUDE.md already warns against `git add -A` for a different reason (sensitive file leakage); add this as a second reason. Or: each session writes to a worktree-isolated branch when running in parallel.

**Companion observation about S025 specifically.** It mirrors S024's "watching-it-run finds bugs the audit-and-validate phase missed" pattern at a different layer. The D-017 design was rigorous about which actor owns which sprite — but said nothing about which session owns the git index. The blind spot was real and surfaced only on the commit attempt. Pattern: design docs scope to a layer; cross-layer races only become visible at integration time.

## Open follow-ups

- Cross-instance dwarf delegation — when jebrim-1 spawns D1 and jebrim-2 spawns D2, the dwarves currently attribute to "jebrim" generically. First cut accepts this; revisit if the pattern matters for cross-reference reasoning.
- Accessibility check of the chosen tint palette under common color-blindness simulators.
- Active-player concept currently single-valued — focal label follows whichever Jebrim is "active". D-017 specifies "both active" — needs a `Set<activeInstance>` refactor in a follow-up.
- Same-building sprite stacking — handled by jitter() since the actorKey hashes differ. Likely fine for 2 instances per building; gets tight at 3+.
