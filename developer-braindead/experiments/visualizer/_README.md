# Visualizer — how to run

The visualizer renders agent activity as a 2D RuneScape-style map. Player sprites walk between buildings as the agent reads/writes files; chat lines stream into a COMMS panel; sub-agents spawn alongside the active player and despawn when they return. Two modes: **replay** (deterministic playback of a baked `EVENTS` array from `git log`) and **live** (tails the hook's `state.ndjson` and renders the agent's current session as it happens).

## Replay mode (default, the demo)

Open `index.html` directly in any browser. The baked `EVENTS` array drives the timeline; scrub bar + session jumps work. No server required.

## Live mode ([[D-009]])

Watch the agent operate in real time. Reads `state.ndjson` written by the hook at `developer-braindead/.claude/hooks/emit-event.py`.

**Run a local server from this folder** (Chrome blocks `fetch()` over `file://`):

```powershell
cd developer-braindead/experiments/visualizer
python -m http.server 8765
```

Then open <http://localhost:8765/?live=1>. The autoplay timer stays off; the page polls `state.ndjson` every 500ms and feeds new events through `applyEvent`.

For a hook event to fire, the Claude Code session must be opened at the brain root (or below) so `brain/.claude/settings.json` is picked up.

## Architecture in one screen

The engine is asset-agnostic and additive — features get bolted onto the `applyEvent` dispatch surface, not by rewriting the engine. The current event vocabulary:

| Event | Fires when | Effect |
|---|---|---|
| `session-start` | Replay session header | Updates ticker + active-player banner |
| `move` | Edit/Write/Read/Glob/Grep on a path that maps to a building | Sprite walks to the building |
| `intent` | Agent writes `.claude/intent/<actor>.txt` (D-010) | Speech bubble over the actor + chat user-line ([[D-014]]) |
| `action` | Edit/Write/Bash/Glob/Grep ([[D-014]]); reads are deliberately silent | Chat user-line "<actor>: editing X" |
| `narrate` | Agent writes `.claude/narration.txt` ([[D-014]]) | System-voice line in COMMS |
| `spawn-dwarf` / `despawn-dwarf` | Task tool Pre / Post | Sub-agent sprite appears next to parent; despawns on return |
| `spawn-gnome` / `despawn-gnome` | Task tool with `subagent_type=gnome` ([[D-016]]) | Same as dwarf, separate color palette + state file |
| `spawn-wisp` / `despawn-wisp` | Unscoped tool calls outside a player session | Wisp drifts in/out |
| `spawn-braindead` / `despawn-braindead` | `.claude/active-mode.txt` flips into/out of dev-brain (S012) | Braindead appears at the workshop / leaves |
| `log` | Hook-emitted narrative breadcrumbs (spawn/despawn lines, mode markers) | Chat line, system-tinted by default |
| `commit` | Replay-only, derived from `git log` | Commit divider in COMMS |

The dispatch lives in `index.html` (`applyEvent`); the emit side lives in `emit-event.py`. Sub-agent shape is parameterized — `dwarfNodes` / `gnomeNodes`, `spawnDwarf` / `spawnGnome`, parallel state files — so adding a third sub-agent kind is mostly mechanical.

## Sub-agent attribution

Tool calls inside a Task/Agent sub-agent carry an `agent_id` field on the hook payload. The hook binds `agent_id → spawn tool_use_id` on first sighting and then attributes subsequent move/action events to the sub-agent's sprite. Two failure modes the maintainer should know:

- **Concurrent same-kind spawns** are inherently ambiguous from the hook's vantage — Claude Code doesn't pass a `parent_tool_use_id` field on sub-calls. The hook uses LIFO binding (most-recent spawn wins) and prints an ambiguity warning to stderr when more than one spawn is pending; this biases toward the typical "I just spawned a dwarf, it immediately did stuff" pattern but can still misattribute under truly concurrent work.
- **Stale spawn entries** (PreToolUse landed but PostToolUse never did, e.g. Claude Code crash) are GC'd after one hour by `gc_stale_subagents`, triggered on the next Task Pre or Post for the same kind.

## Files

- `index.html` — single-file renderer. Engine is asset-agnostic; live + replay share `applyEvent`.
- `path-map.json` — shared lookup (hook + renderer): path → building, path → actor. The hook layers the active-mode marker on top of the actor rules ([[S012]]): when `active-mode.txt` reads `dev-brain` and the path doesn't match an explicit actor rule, the work attributes to Braindead instead of the default actor.
- `state.ndjson` — append-only live event log. Gitignored. The hook appends; the renderer tails.
- `state-actors.json` — current building per main-thread actor + `_mode` marker. Atomically rewritten on each move.
- `state-dwarves.json`, `state-gnomes.json` — per-kind sub-agent state: `nextId`, `byToolUseId`, `byAgentId`, `pendingAgentBind`. Atomic writes via temp+rename ([[S022]]).
- `brain/.claude/intent/<actor>.txt` — intent narration sidecars (D-010). The agent writes a 2–6 word phrase after stating its Plan; the hook reads the file on write and emits an `intent` event. The renderer hangs a speech bubble over the actor, clearing it when they walk to a new building. Sub-agents don't write here — their bubble comes from the Task call's `description` field at spawn time.
- `brain/.claude/narration.txt` — system-voice narration sidecar ([[D-014]]). Overwrite semantics; cap 200 chars. Used for session boundaries, ritual phase transitions, mode switches.
- `brain/.claude/active-mode.txt` — single-line mode marker ([[S012]]): `dev-brain` while in dev-brain mode, `unscoped` (or absent) otherwise. The hook detects transitions and emits `spawn-braindead` / `despawn-braindead` events.

## Decisions worth knowing

- [[D-009]] — the live-mode pipeline (hook → state.ndjson → poll → applyEvent).
- [[D-014]] — chat panel, intent bubbles, action events, narration channel.
- [[D-016]] — gnomes as a structural-housekeeper sub-agent kind, parallel to dwarves but with a different write surface in the main brain.
- [[S012]] — Braindead as the dev-brain construction crew; the `active-mode.txt` marker as the spawn/despawn trigger.
- [[S022]] — audit-driven fix pass: atomic state writes, despawn-on-crash GC, ghost-despawn suppression, color-taxonomy consolidation. See `developer-braindead/quest-log/S022_*.md` for the change list and `developer-braindead/bank/research/visualizer-audit-S021.md` for the findings that drove it.
