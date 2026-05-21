# Visualizer — how to run

## Replay mode (default, the demo)

Open `index.html` directly in any browser. The baked `EVENTS` array drives the timeline; scrub bar + session jumps work. No server required.

## Live mode (D-009)

Watch the agent operate in real time. Reads `state.ndjson` written by the hook at `developer-braindead/.claude/hooks/emit-event.py`.

**Run a local server from this folder** (Chrome blocks `fetch()` over `file://`):

```powershell
cd developer-braindead/experiments/visualizer
python -m http.server 8765
```

Then open <http://localhost:8765/?live=1>. The autoplay timer stays off; the page polls `state.ndjson` every 500ms and feeds new events through `applyEvent`.

For a hook event to fire, the Claude Code session must be opened at the brain root (or below) so `brain/.claude/settings.json` is picked up.

## Files

- `index.html` — single-file renderer. Engine is asset-agnostic; live + replay share `applyEvent`.
- `path-map.json` — shared lookup (hook + renderer): path → building, path → actor.
- `state.ndjson` — append-only live event log. Gitignored. The hook appends; the renderer tails.
- `brain/.claude/intent/<actor>.txt` — intent narration sidecars (D-010). The agent writes a 2–6 word phrase after stating its Plan; the hook reads the file on write and emits an `intent` event. The renderer hangs a speech bubble over the actor, clearing it when they walk to a new building. Dwarves don't write here — their bubble comes from the Task call's `description` field at spawn time.

## Steps still pending (per [[D-009]])

- Step 3 (this commit): `?live=1` + incremental poll.
- Step 4: Read / Glob / Grep hooks with coalescing.
- Step 5: `Task` tool → spawn / despawn dwarves.
- Step 6: Bootstrap-from-tail (instant replay of existing events when the page opens mid-session).
