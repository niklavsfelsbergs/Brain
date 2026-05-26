# S052 — 2026-05-23 — Switchboard rebuild (map killed, promoted to brain root)

**Session.** `98d4ec5e` (dev-brain mode, opened via "Lets develop gielinor").
**Decision.** [[D-026_switchboard_promotion]].

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

5. **Denest (principal).** First live run revealed the migration target was wrong: `git mv` had been issued as `brain/switchboard/` *relative to the repo root* — but the repo is itself named `brain`, so that created a redundant nested `brain/brain/switchboard/`. Meanwhile the hooks' `DEV_BRAIN.parent / "switchboard"` correctly resolved to `<repo>/switchboard/` and had been writing runtime state there the whole time — source files and live state were one directory apart. Symptom: the new UI rendered but every panel was empty. Fix: `git mv` all tracked files from `brain/switchboard/` → `switchboard/`, swept the `brain/switchboard` → `switchboard` path strings across all docs + `_about.md` + hook comments, fixed `.gitignore`. Commit **d0638dc**.

6. **Switchboard scale-up (principal).** Principal wanted the switchboard pane bigger all around. Went to ~1.7× the original after a 2× pass read too large: width 280→480px, header 20→34px, row name 13→22px, state chip 11→18px, dot 10→17px, subtitle 12→18px. Added a `?v=N` cache-buster on the `styles.css` link in `index.html` after the first scale-up didn't show (browser had cached the stylesheet). Not yet committed at close — folds into the wrap-up commit.

7. **`CLAUDE_PROJECT_DIR` hook-path hardening (principal).** Principal asked why *this* session never appeared on the board. Diagnosis: zero events from `98d4ec5e` in `chat.ndjson`/`state.ndjson`, no `~/.claude/status/98d4ec5e.json` — all hooks silently no-op'd. Root cause: this session was launched from inside `experiments/visualizer/`, where Claude Code left `CLAUDE_PROJECT_DIR` empty; the registered hook command `python "${CLAUDE_PROJECT_DIR}/developer-braindead/.claude/hooks/..."` expanded to a broken `/developer-braindead/...` path. Sessions launched from the repo root (jebrim, guthix) were unaffected. Fix: replaced `${CLAUDE_PROJECT_DIR}` with the absolute hook path in `brain/.claude/settings.json` (6 commands), documented inline via `_comment_abs_path`. Machine-specific but acceptable until ascension. settings.json hot-reloads, so this session begins reporting on its next fire.

## Files touched (by commit)

- **9854b32** — `developer-braindead/experiments/visualizer/index.html` (map stripped).
- **c03f33b** — `developer-braindead/.claude/hooks/emit-event.py`, `developer-braindead/experiments/visualizer/index.html` (chat panel subtitle wiring).
- **1c94a57** — `developer-braindead/experiments/visualizer/{index.html,_README.md,path-map.json}` → `switchboard/`; `developer-braindead/.claude/hooks/emit-event.py`, `status-sidecar.py` (`VIZ_DIR` constant); `.gitignore`.
- **31844e3** — `switchboard/{index.html,app.js,chat.js,state.js,switchboard.js,focus.js,styles.css,_about.md}` (D4 ES module split).
- **ca02dde** — D5 doc updates (respawn, D-020/24/25/26, comms, quest log).
- **d0638dc** — denest `brain/switchboard/` → `switchboard/` + path-string sweep across docs.
- **wrap-up commit** — `switchboard/styles.css` + `index.html` (scale-up), `brain/.claude/settings.json` (abs-path hardening), this quest log, respawn.md, comms CLOSING.

## Open

- ~~**Live-verify the rebuilt surface.**~~ Done at close: UI renders both panels correctly; scale-up confirmed. *Caveat:* this very session (`98d4ec5e`) did not appear on the board — diagnosed to the `CLAUDE_PROJECT_DIR` hook-path bug (turn 7), now fixed. Still unverified end-to-end: chat panel growing live from `chat.ndjson`, switchboard subtitle ticking, click-to-focus via `focus.js`. Next session launched from repo root should self-report and confirm all three. Run: `cd switchboard && python -m http.server 8765 && open http://localhost:8765/?live=1`.
- **Cleanup pass on `developer-braindead/experiments/visualizer/`.** Sprites/, sprite source PNGs, `slice.py`, `slice_tileset.py`, `subtask_smoketest.py` remain — dead weight from the map era. `experiments/vscode-claude-focus/` is a separate VS Code extension that may or may not still be live; decide whether it gets retired or graduates to its own top-level experiment. Sweep in a future bankstanding pass; never delete.
- **`path-map.json` is now vestigial.** Still consulted by `emit-event.py`'s path classifier to humanize file paths into building names — but no map renders, so the classifier produces labels nobody reads. Simplify or repurpose the hook in a future pass.
- **`_about.md` for `switchboard/`** — written by D4 this session; verify on first respawn that it reads naturally from a fresh session's perspective.
