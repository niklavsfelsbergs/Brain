# respawn.md — dev brain entry point

> Read this first when starting a fresh dev session. It tells you where we are, what was just done, what's blocking, and the next concrete step.
>
> The ritual that reads this file is `spellbook/respawn-ritual.md`. The ritual that *updates* it is `spellbook/session-close.md`.
>
> **Discipline.** Updated at the end of every session, after the quest-log entry lands. Overwritten in place — not append-only. History lives in `quest-log/`.

**Last updated.** 2026-05-21 (end of [[S014]], pre-commit).

## Where we are

[[S014]] was two visualizer rounds plus a hook fix. **Round 1 — polish:** players solid + 1.4×, building labels above roofs, pond gone, hover descriptions per building, live-mode timestamps fixed, renderer self-heals when a dynamic actor receives a move/intent without a prior spawn event. **Round 2 — aesthetics:** paths are quadratic-bezier curves, trees are a deterministic perimeter-weighted scatter (130 candidates after the 4× reduction), stone/wood wall textures + roof shingle rows on all 9 buildings.

**Hook fix.** Brain-root `.claude/settings.json` only matched `Task`; upstream renamed the tool to `Agent`. Jebrim's S014 dwarf spawns went unhooked and the dwarves' writes leaked onto Jebrim. Widened matchers to `Agent|Task` and updated `emit-event.py`'s dispatch. `gielinor/.claude/settings.json` was already correct.

**Post-commit emitter.** `developer-braindead/.claude/hooks/emit-commit-event.py` + `.git/hooks/post-commit` (per-clone). COMMITS lane now surfaces every git commit, not just baked replay events.

Two commits this session: `4585a12` (round 1 + hook fix) and `15c8de8` (round 2 aesthetics + emitter helper).

## Next concrete step — START HERE

**Visualizer iteration continues.** Round 2 just landed; eyeball it (`python -m http.server 8765` from `developer-braindead/experiments/visualizer/`, then `?live=1`) and pick what bothers you. Likely candidates from the screenshots so far:

- **Curve magnitude.** 14–22% of segment length might over- or under-bow some pairs. Single-line knob in `pathControl()`.
- **Tree distribution.** 130 candidates, perimeter-weighted. If middle still reads bare or edges still read thick, tune `TREE_CANDIDATES` and the `accept = (1 - edge) * 0.85 + 0.06` mix.
- **Wall texture density.** `wallTexture()` derives course count from `h / 14` for stone, and uses 6 planks for wood. Tower and small workshop may want different counts.
- **Roof shingle rows.** `roofTexture()` derives from `r / 14`. The tall Spellbook Tower has r=84 → 6 rows, might be too busy; the workshop has r=14 → 1 row, might be too sparse.
- **Per-building polish backlog from [[S009]].** The Inn, Bank, Hall of Mirrors, Keepsake Vault, Inbox Square could still use idiosyncratic character beyond the generic stone-vs-wood split.

Other live threads:

- **Thread A from S013 — verify visualizer feature set end-to-end.** Still outstanding from S011/S012/S013. Especially worth re-running now that ensureActorExists self-heals the braindead/wisp sprite case.
- **Thread B — observe the harvest pump.** No code; watch what the next 3–5 sessions' harvests produce, drift to aspirational drafts, bank drafts-gate friction.

Iteration menu (deferred from earlier, no priority assigned):

- **Idle indicator / watchdog for non-Claude writes / smarter active-player inference / SSE upgrade.** D-009 deferred.
- **Aesthetic backlog from [[S009]].** Per-building character (see above).
- **Read-event noise tuning.**

## Open at the start of next session

- Visualizer Round 3 iteration (whatever bothers you when you look at the new map).
- Browser-side verification (Thread A — outstanding since S011).
- Harvest pump observation (Thread B).
- **§C Pilot definition** — data source, "concerning" definition, output channel. Unchanged.
- **§H.3 brain-zone taxonomy** — content for `player/working-agreements.md`. Not blocking.
- **§H.4 identity ↔ main-brain interaction** — how `examine/I-NNN` entries here interact with main-brain `examine/`. [[I-002]] is a candidate for export.

## Carried-over observations

From [[S014]] (new, two-incident pattern strengthening): **the renderer needs to be self-healing because the hook stream is a lossy substrate.** Two distinct bugs this session boiled down to "the event the renderer needed was never emitted" — Braindead's `spawn-braindead` skipped because `state-actors.json _mode` was stale, and Jebrim's `spawn-dwarf` skipped because the brain-root matcher was on the old tool name. The first I fixed in the renderer (auto-spawn on first move/intent); the second I fixed at the hook layer. Pattern: **don't assume the upstream emitted what you'd render against — defend in the renderer too.** Companion to [[I-002]] (render in your head before shipping it) — this is the runtime version: render assuming partial data, because the upstream is allowed to be imperfect.

From [[S014]] (one incident): **tool renames upstream are silent regressions.** `Task → Agent` broke the brain-root hook with no error message — just zero events on a path that used to fire. Worth checking the other side: are there places where the renderer or other hooks key off a tool name that may have already moved?

From [[S013]] (still candidate, two incidents now): **the procedure was right; the procedure assumed a state that didn't exist.** First Jebrim alching (S012/S013) found near-empty layers because Pump 2 wasn't installed yet — the same shape as S010's live-vs-replay miss ([[I-002]]). Today's two renderer/hook bugs are the same shape: the *renderer* assumed `spawn-*` would arrive; the *hook* assumed the tool was still named `Task`. Pattern now at 4 incidents — strong enough to draft an `I-NNN` if/when bankstanding next runs.

From [[S013]] (separate observation): **uncommitted work occupies the ID space.** Confirmed pattern; nothing new here.

From [[S010]]: **the visual sameness between live and replay was an [[I-002]] miss.**

From [[S009]]: **mental UI preview must include z-order and all collision targets.**

From [[S008]] (codified as [[I-002]]): **render UI in your head before shipping it.**

From [[S003]]–[[S007]]: **structure-first, content earns its way in.** **Build the verification surface alongside the artifact, not after.**

## Files to read first

1. `respawn.md` (this file)
2. `quest-log/S014_visualizer_polish_and_aesthetics_pass.md` — most recent session
3. `quest-log/S013_close_session_harvest_pump.md` — harvest pump
4. `bank/decisions/D-012_close_session_harvest_pump.md`
5. `bank/decisions/D-013_braindead_character_and_workshop.md`
6. `bank/decisions/D-010_visualizer_intent_narration.md`
7. `bank/decisions/D-009_visualizer_live_mode_v0.md`
8. `bank/decisions/D-008_iso_replay_v0_over_three_js.md` — iso-vs-3D (still load-bearing)
9. `experiments/visualizer/index.html` — the artifact being iterated
10. `experiments/visualizer/_README.md` — how to run both modes
11. `experiments/visualizer/path-map.json` — shared lookup (hook + renderer)
12. `.claude/hooks/emit-event.py` (under `developer-braindead/`) — live-mode + intent + mode-marker hook; now Agent|Task aware
13. `.claude/hooks/emit-commit-event.py` (under `developer-braindead/`) — post-commit emitter for the COMMITS lane
14. `bank/open-questions/Q-007_gielinor_visualizer.md` — points at D-009; deferred follow-ups
15. `bank/plan.md` — current mission state

`bank/decisions/`, `bank/assumptions/`, `bank/open-questions/`, `bank/risks/` are reference material — open as cited.

## Note on the visualizer's engine

The engine (event timeline, `applyEvent` dispatch, CSS-transition movement, RAF tick loop, scrub-seek with `instant` flag) is **asset-agnostic and should not be touched during aesthetic iteration**. State additions across S009–S014 are layered on top of the dispatch surface, not changes to it. Keep extending, don't rewrite.

S014 added one minor protocol extension: `applyEvent` now reads `ev.wallTime` to support live-mode timestamps, and `ensureActorExists()` runs at the head of `move` + `intent`. Both are additive; the dispatch surface is unchanged.

## How to run

- **Replay mode (the demo).** Open `experiments/visualizer/index.html` directly in a browser. Default URL, no server needed.
- **Live mode (self-observation).** `cd developer-braindead/experiments/visualizer && python -m http.server 8765`, then open `http://localhost:8765/?live=1`. Requires Claude Code session opened at brain/ root so `brain/.claude/settings.json` loads and the hook fires.
