# S052 — 2026-05-23 — Switchboard rebuild (map killed, promoted to brain root)

**Session.** `98d4ec5e` (dev-brain mode, opened via "Lets develop gielinor").
**Decision.** [[D-026]].

## Turn-by-turn so far

1. **Opening cue.** Principal: *"fighting with the animation but it doesn't matter — switchboard most useful, chat secondary, kill the map, give it a dedicated space, split into files."* The visualizer's map half had been costing more than it returned for six sessions running (S047–S051 all touched map code; four of those debugged it). Switchboard rows + chat panel were doing the load-bearing work; map was charm tax.

2. **Three parallel dwarves (pre-migration).**
   - **D1 — strip the map.** Excised SVG `<svg class="map">` and the entire isometric stack from `experiments/visualizer/index.html`: building defs, sprite defs, walk animations, wander logic, `applyEvent` map-mutating branches, `relayoutBubbles`, gather-slot tables, sprite-state CSS, day/night vestiges. Switchboard + chat panels left in place. Commit **9854b32**.
   - **D2 — chat.ndjson humanizer + switchboard subtitle.** `emit-event.py` now appends one human-language line per event to `chat.ndjson` (`Braindead is editing index.html`, `Jebrim ran grep over sql/`, idle/spawn/despawn). Chat panel reads the stream directly — prose generation moved from client to hook. Switchboard row's S049 `latest_action` field repurposed as the row subtitle (one-line "what is this session doing right now"). Commit **c03f33b**.
   - **D3 — reference audit.** Read-only walk of the doc surfaces enumerating every `experiments/visualizer/` and `state-switchboard.json` reference across `developer-braindead/`, with grouping by "current state vs historical narrative" so the doc-update wave knew what to touch.

3. **Migration (principal).** `git mv` of the three surviving files (`index.html`, `_README.md`, `path-map.json`) from `developer-braindead/experiments/visualizer/` to `switchboard/`. Hook constants (`VIZ_DIR` in `emit-event.py` and `status-sidecar.py`) updated to the new path. `.gitignore` patterns updated. Commit **1c94a57**.

4. **Second-wave dwarves.**
   - **D4 — ES module split + chat panel wiring + _about.md.** Carved `switchboard/index.html` into `state.js`, `switchboard.js`, `focus.js`. Wrote the new `_about.md` (this dwarf's territory — D5 stays off `switchboard/`). Wired the chat panel to poll `chat.ndjson`.
   - **D5 — doc updates (this dwarf).** Walked the punch list from D3's audit:
     - `developer-braindead/respawn.md` — top entry, Where we are, Step 0, Files to read first, How to run, obsolete sprite TODOs flagged.
     - `D-020_terminal_switchboard.md` — S052 amendment (new path + chat.ndjson sibling).
     - `D-024_parallel_player_coordination.md` — S052 amendment (comms mirror destination moved).
     - `D-025_visualizer_character_audit_findings.md` — S052 amendment (map-targeted carry-forwards obsolete).
     - `D-026_switchboard_promotion.md` — new decision doc.
     - `developer-braindead/comms/active.md` — S052 CLOSING entry.
     - This quest-log entry.

## Files touched (by commit)

- **9854b32** — `developer-braindead/experiments/visualizer/index.html` (map stripped).
- **c03f33b** — `developer-braindead/.claude/hooks/emit-event.py`, `developer-braindead/experiments/visualizer/index.html` (chat panel subtitle wiring).
- **1c94a57** — `developer-braindead/experiments/visualizer/{index.html,_README.md,path-map.json}` → `switchboard/`; `developer-braindead/.claude/hooks/emit-event.py`, `status-sidecar.py` (`VIZ_DIR` constant); `.gitignore`.
- **D4 commit** — `switchboard/{index.html,state.js,switchboard.js,focus.js,_about.md}`.
- **D5 commit (this dwarf)** — files listed in turn 4 above.

## Open

- **Live-verify the rebuilt surface.** `cd brain/switchboard && python -m http.server 8765 && open http://localhost:8765/?live=1`. Confirm: both panels render, switchboard subtitles reflect current activity from a fresh tool call, chat panel grows as the hook fires, click-to-focus still dispatches via the focus.js module.
- **Cleanup pass on `developer-braindead/experiments/visualizer/`.** Sprites/, sprite source PNGs, `slice.py`, `slice_tileset.py`, `subtask_smoketest.py` remain — dead weight from the map era. `experiments/vscode-claude-focus/` is a separate VS Code extension that may or may not still be live; decide whether it gets retired or graduates to its own top-level experiment. Sweep in a future bankstanding pass; never delete.
- **`path-map.json` is now vestigial.** Still consulted by `emit-event.py`'s path classifier to humanize file paths into building names — but no map renders, so the classifier produces labels nobody reads. Simplify or repurpose the hook in a future pass.
- **`_about.md` for `switchboard/`** — written by D4 this session; verify on first respawn that it reads naturally from a fresh session's perspective.
