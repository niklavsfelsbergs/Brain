# respawn.md — dev brain entry point

> Read this first when starting a fresh dev session. It tells you where we are, what was just done, what's blocking, and the next concrete step.
>
> The ritual that reads this file is `spellbook/respawn-ritual.md`. The ritual that *updates* it is `spellbook/session-close.md`.
>
> **Discipline.** Updated at the end of every session, after the quest-log entry lands. Overwritten in place — not append-only. History lives in `quest-log/`.

**Last updated.** 2026-05-21 (end of [[S009]]).

## Where we are

[[S009]] applied the six-delta aesthetic pass from [[S008]]'s respawn to `experiments/visualizer/index.html` — building labels, sky + horizon, ground decoration density, taller buildings + per-building character, COMMS log panel with speaker filtering, active-player focal label. Then one round of principal feedback caught three things and they were fixed: labels moved to a top-layer `<g id="building-labels">` (so they sit above characters and vignette), pond clearance added to flora placement (two trees were standing on the pond), and the tree topology rewritten from iso-coord rings to screen-coord edge loops (trees now frame the map instead of cluttering the interior).

The visualizer is "good enough to show people" — the v0 + aesthetic pass + edge-frame fix produces a coherent scene. [[Q-007]] live-mode (watcher + hooks emitting events to `state.json`) remains open.

## Next concrete step — START HERE

**Continue iterating on the visualizer.** Open question is what to iterate on next. Possible directions, no priority assigned (the principal will pick):

- **More principal review.** Run through what's still off — color balance, building proportions vs each other, label legibility against busy backgrounds, sky-grass seam at the top, scattered-detail density. Iteration in the same vein as the three fixes at the end of [[S009]].
- **Per-building character (deeper).** [[S009]] hit Meta Town Hall, Lorebook Library, Quest Hall, Spellbook Tower. The Inn, Bank, Hall of Mirrors, Keepsake Vault, Inbox Square got only the height bump. Each of those could earn distinct silhouettes (e.g., Bank: vault door, gold spikes; Inn: outdoor seating; Hall of Mirrors: mirror-flash particles).
- **Camera / focal behavior.** Currently the camera is fixed and the active player walks through it. A subtle pan or scale-on-active-player would reinforce attention; the focal label gives a foothold for this.
- **Live-mode escalation.** The original [[Q-007]] open thread. Replay-from-git-log is shipped; live-mode means a file watcher + hooks emitting events into `state.json` and the page polling/SSE'ing them. Bigger lift, separate from aesthetic iteration.

The pragmatic default is: keep the principal-feedback loop tight on the v0, ship a couple more passes, then decide if live-mode is worth it or if replay-from-git-log already covers the use case.

## Open at the start of next session

- Visualizer iteration (above).
- **§C Pilot definition** — data source, "concerning" definition, output channel. Unchanged from prior respawn; visualizer is parallel work.
- **§H.3 brain-zone taxonomy** — content for `player/working-agreements.md`. Not blocking.
- **§H.4 identity ↔ main-brain interaction** — how `examine/I-NNN` entries here interact with main-brain `examine/`. [[I-002]] is a candidate for export.

## Carried-over observations

From [[S009]] (extension of [[I-002]], not yet promoted): **mental UI preview must include z-order and all collision targets**, not just the static layout. The three feedback fixes ([[S009]] item 2) were all collision/layering blind spots — labels rendered below characters because nested in same group; trees rendered on pond because pond wasn't a collision target. The static-layout preview that [[I-002]] codifies is necessary but not sufficient; promote when a second incident confirms.

From [[S008]] (codified as [[I-002]]): **render UI in your head before shipping it.** Applied successfully across the six deltas; failed on the three issues above for the reason just noted.

From [[S003]]–[[S007]] (carried, reaffirmed): **structure-first, content earns its way in.** **Build the verification surface alongside the artifact, not after.** Both still candidate `examine/` entries on the main-brain side.

## Files to read first

1. `respawn.md` (this file)
2. `quest-log/S009_visualizer_six_deltas_and_frame.md` — most recent session
3. `quest-log/S008_iso_visualizer_v0.md` — the v0 build
4. `bank/decisions/D-008_iso_replay_v0_over_three_js.md` — the iso-vs-3D decision
5. `examine/I-002_render_before_shipping_ui.md` — the posture rule
6. `bank/open-questions/Q-007_gielinor_visualizer.md` — still open on live-mode
7. `experiments/visualizer/index.html` — the artifact being iterated. Most recent state has: all six deltas + top-layer building labels + pond clearance + edge-frame tree layout.
8. `bank/plan.md` — current mission state. Visualizer is parallel to plan items.

`bank/decisions/`, `bank/assumptions/`, `bank/open-questions/`, `bank/risks/` are reference material — open as cited.

## Note on the visualizer's engine

The engine (event timeline, `applyEvent` dispatch, CSS-transition movement, RAF tick loop, scrub-seek with `instant` flag) is **asset-agnostic and should not be touched during aesthetic iteration**. State added in [[S009]] (`wispActive`, `currentBuilding`, `LABEL_Y_OFFSET`) and new functions (`ornateLabel`, `buildLabels`, `updateFocalLabel`, `deriveSpeaker`) are layered on top, not changes to the dispatch surface. If a future session needs to change engine behavior (e.g., live-mode events), keep the timeline data structure and `applyEvent` dispatch surface intact — extend, don't rewrite.
