# D-026 — 2026-05-23 — Switchboard promotion: kill the map, move to brain root

**Context.** [[D-009]] launched the visualizer as a live-mode self-observation surface — an isometric map showing Braindead at his workshop, Jebrim at the desk, Guthix wherever he descended, sprites walking between buildings as the hook stream ticked. The map carried character; the switchboard ([[D-020]] Phase 2) and the COMMS chat panel ([[D-014]] / S044 wiring) layered on top as auxiliary views.

By [[S047]]–[[S051]] the load balance had inverted. The switchboard rows were where the operator actually looked: *which terminal is waiting for me, what is it doing, click to focus.* The chat panel surfaced the action stream. The map was a charming aesthetic floating above two views that were doing the real work — with every session also paying the cost of map bugs (sprite anchor drift [[D-025]] #2, parallel-Braindead spawn races S047/S048, despawn timeout closures S050, tree/bubble scale knobs S051). Six recent sessions in a row touched the map; four of them were debugging it.

Principal called it: *"fighting with the animation but it doesn't matter — switchboard most useful, chat secondary, kill the map, give it a dedicated space, split into files."*

## Decision

Collapse the visualizer to its two load-bearing panels (switchboard + chat) and promote the surviving surface to `switchboard/`. Conceptually rename from "visualizer" to "switchboard" — the load-bearing pane earns the name.

Three commits this session land it:

- **9854b32** — strip the map. SVG `<svg class="map">`, all building defs, sprite defs, walk animations, wander logic, `applyEvent` map-mutating branches, `relayoutBubbles`, gather-slot tables, and the underlying state files for sprite positions deleted from `index.html`. Switchboard + chat panels remain, fed by `state-switchboard.json` and `chat.ndjson`.
- **c03f33b** — `chat.ndjson` as a hook-side humanized stream. `emit-event.py` now appends one human-language line per event (`Braindead is editing index.html`, `Jebrim ran grep over sql/`, `Guthix is reading bank/notes/`, idle/spawn/despawn). The chat panel reads this directly — no more deriving prose from raw event verbs client-side. Switchboard row subtitle (the `latest_action` slot from S049) repurposed as a one-line "what is this session doing right now."
- **1c94a57** — `git mv` migration. `index.html`, `_README.md`, `path-map.json` moved from `developer-braindead/experiments/visualizer/` to `switchboard/`. Hook constants (`emit-event.py` and `status-sidecar.py` `VIZ_DIR`) updated. `.gitignore` patterns updated for the new path.

## Why brain root, not gielinor or dev-brain

The switchboard observes **both brains**. Player sessions (Jebrim, Zezima — gielinor namespace), Braindead sessions (dev-brain namespace), Guthix (system-scope deity), Wisp (unscoped). One surface, all actors. The original location at `developer-braindead/experiments/` was a dev-brain artifact by accident of birth — it shipped with [[D-009]] when the dev brain was the only brain that needed observation. The other brain showed up later.

Hosting it under `gielinor/` would be similarly wrong (Braindead is not a gielinor actor). Hosting under `developer-braindead/` made the wrong rule visible — the dev brain's `_about.md` says it's a construction notebook, not a runtime surface, and the visualizer was always the awkward exception. Brain root resolves the asymmetry: a runtime surface that watches both brains belongs above both, not inside one.

The "experiments/" prefix also stopped reading honestly the moment the switchboard became routine operating infrastructure. Promotion sheds the prefix along with the location.

## Architectural consequences

- **Hooks unchanged in shape.** `emit-event.py` and `status-sidecar.py` continue writing to the same filenames; only the directory constant moved. The hook-as-instrumentation contract holds.
- **State files now gitignored at the new path.** `.gitignore` lists `switchboard/state.ndjson`, `state-actors.json`, `state-instances.json`, `state-switchboard.json`, `state-comms-*.md`, `chat.ndjson` etc. Same volatile-runtime discipline that the old viz dir had.
- **`path-map.json` is vestigial.** It still lives next to `index.html` because `emit-event.py`'s path classifier reads it to humanize file paths into building names. Now that no map renders, that classifier is producing a label nobody reads. Either simplify the hook (drop the classifier, emit raw paths to chat.ndjson) or repurpose path-map as a chat-prose helper. Defer until the chat humanizer's first real-use pass surfaces what's needed.
- **The dev-brain `experiments/visualizer/` directory remains on disk** with sprites/, sprite source PNGs, slice scripts (`slice.py`, `slice_tileset.py`), `subtask_smoketest.py`, and the `vscode-claude-focus/` sibling project. All dead weight from the map era except `vscode-claude-focus/`, which is a separate VS Code extension and may still be relevant. Sweep in a future bankstanding pass — never delete.
- **ES modules.** Sibling dwarf split `index.html` into `state.js`, `switchboard.js`, `focus.js`. The shell HTML loads them via `<script type="module">`. Easier to scan; easier to swap one panel without touching the other.

## Open follow-ups

- Live-verify the rebuilt surface end-to-end — `cd brain/switchboard && python -m http.server 8765 && open http://localhost:8765/?live=1`. Both panels render; switchboard subtitles reflect current activity; chat panel shows the humanized stream growing; click-to-focus still dispatches.
- Simplify `emit-event.py`'s path classifier (drop or repurpose `path-map.json`).
- Cleanup pass on `developer-braindead/experiments/visualizer/` — archive sprites/, slice scripts, smoketest; decide whether `vscode-claude-focus/` belongs as its own top-level experiment or gets retired.
- Switchboard `_about.md` — written this session by the sibling dwarf; verify on first respawn that the new location reads naturally from a fresh session's perspective.

## Related

- [[D-009]] — visualizer live mode v0; the surface this decision retires the map half of.
- [[D-010]] — visualizer intent narration; consumed by both the chat panel and the switchboard subtitle.
- [[D-014]] — visualizer chat panel; absorbed into the new shape.
- [[D-020]] — terminal switchboard origin; the pane that earned the name.
- [[D-024]] — parallel coordination; comms mirror destinations follow the new path.
- [[D-025]] — visualizer character audit; map-targeted carry-forwards now obsolete.
- [[S052]] — quest-log entry capturing the construction.
