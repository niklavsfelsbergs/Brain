# respawn.md — dev brain entry point

> Read this first when starting a fresh dev session. It tells you where we are, what was just done, what's blocking, and the next concrete step.
>
> The ritual that reads this file is `spellbook/respawn-ritual.md`. The ritual that *updates* it is `spellbook/session-close.md`.
>
> **Discipline.** Updated at the end of every session, after the quest-log entry lands. Overwritten in place — not append-only. History lives in `quest-log/`.

**Last updated.** 2026-05-21 (end of [[S008]]).

## Where we are

[[S008]] was a dev-brain session (same calendar day as [[S006]] and [[S007]]) that built the [[Q-007]] visualizer's **replay-from-git-log v0** as an iso 2D SVG. Single self-contained HTML at `experiments/visualizer/index.html`, ~1700 lines, no dependencies (Google Fonts is the only network ref; pure monospace fallback works offline). Animates the real S001→S007 + Q-007 git history: Jebrim walks between buildings, three dwarves spawn at Quest Hall for the S002 wave, wisp appears for unscoped sessions, commits fire in the event log.

[[D-008]] landed the decision *iso 2D over three.js 3D* — Niklavs proposed 3D, the v0 went iso instead because (a) one-shot three.js produces flat-grey-box demos, not RuneScape, and (b) the engine is asset-agnostic so a real 3D pass later is a sprite swap, not a redesign. [[Q-007]] flipped `open → working`; live-mode (watcher + hooks) is still open.

[[I-002]] landed: *render UI in your head before shipping it*. Six visible bugs over the session that a single screenshot would have caught. Promoted from observation to posture rule.

## Next concrete step — START HERE

**Continue [[S008]] — apply the inspiration-image pass to the visualizer.** Late in the session Niklavs shared a reference pixel-art game screenshot (saved screenshot reference is in chat, not on disk). Six concrete deltas were agreed on, in priority order. The visualizer file is already iterating; each delta is a localized change.

### The six deltas (do them in this order)

1. **Always-on building labels with ornate gold-bracketed frames.** Replace the current hover-only `<text class="plaque">` with permanent labels below each building. Format like `◆ QUEST HALL ◆` in Jacquard 12, gold text, dark backdrop chip. Big readability win. *(~15 min)*

2. **Sky + horizon strip above the grass.** The black void above the iso diamond is dead weight. Add a sky band at the top of the SVG: linear gradient (light blue → pale yellow) → distant mountain silhouettes (3-4 layers, decreasing opacity) → tree line. The grass diamond can stay below it; just kill the void above. *(~30 min)*

3. **Ground decoration density.** The grass tiles are clean; the reference image has ~3-4× more ground detail. Sprinkle grass tufts, mushrooms, pebbles, small flowers, mushroom rings. Use the existing `overlays` layer; add 5-6 new tiny sprites in `<defs>` and seed them across the diamond. *(~20 min)*

4. **Taller buildings + per-building character pass.** The single biggest visual impact. Our buildings are squat iso pyramids; the reference has tall, ornate structures. Push the proportions: increase `h` and `r` per building. Add per-building character — Spellbook Tower should rival the reference's "Vericity" for verticality, Meta Town Hall should feel like a castle (multiple spires, banners), Lorebook Library should be a building of consequence not a shed with books stuck on top. *(~1-2 hr — biggest delta, save until 1-3 land)*

5. **COMMS-style log panel restyle.** The reference's `● JUSTS ● KHA'AN ● JEFF ● TEACHER` colored-dot speaker tabs are a beautiful nav pattern. Adapt to ours: `● JEBRIM ● ZEZIMA ● DWARVES ● WISP ● COMMITS` as filterable tabs above the event log. Each click filters log entries. Keep the existing log content; restyle the header and add tab filtering. *(~30 min)*

6. **Active-player focal label.** Like the reference's `◆ VERICITY ◆` label that says "this is the place" — float a label above the currently active player showing `◆ JEBRIM AT QUEST HALL ◆` (or whichever building). Updates on every move event. Reinforces the camera/attention. *(~15 min)*

### What NOT to take from the reference (decided in [[S008]], do not relitigate)

- The HUD top-left (`PLAYGROUND / HEALTH 100 / CYCLE 90 / SLEEPING`). Game-stat metaphor; the brain isn't a game with health.
- The `HOME / BRAIN 3D / DASHBOARD` nav. Implies multiple pages that don't exist.
- Multi-character COMMS content. The aesthetic yes; the chatroom no.
- Side-scroller perspective. The iso diamond is what makes 9 buildings work — flatten it and only 3 fit.
- Hyper-detailed building textures (every brick). Weekend of asset work; one-shot fidelity should stay at RS-Classic level, not OSRS-modern.

## Open at the start of next session

- All six deltas above (the main work).
- After the deltas land, consider whether the v0 is "good enough to show people" or whether to escalate to live-mode (watcher + hooks emitting events to `state.json`). Live mode is the still-open part of [[Q-007]].
- **§C Pilot definition** — data source, "concerning" definition, output channel. Drives §B-class architecture refinements through real use. *(Unchanged from prior respawn; visualizer is parallel work.)*
- **§H.3 brain-zone taxonomy** — content for `player/working-agreements.md`. Not blocking.
- **§H.4 identity ↔ main-brain interaction** — how `examine/I-NNN` entries here interact with main-brain `examine/`. [[I-002]] is a candidate for export.

## Carried-over observations

From [[S008]] (now codified as [[I-002]]): **render UI in your head before shipping it.** Six iteration cycles for visible bugs this session — the cost of mentally previewing the SVG/CSS is seconds, the cost of skipping it is a round-trip per bug.

From [[S003]]–[[S007]] (carried, reaffirmed): **structure-first, content earns its way in.** **Build the verification surface alongside the artifact, not after.** Both still candidate `examine/` entries on the main-brain side.

## Files to read first

1. `respawn.md` (this file)
2. `quest-log/S008_iso_visualizer_v0.md` — most recent session
3. `bank/decisions/D-008_iso_replay_v0_over_three_js.md` — the iso-vs-3D decision
4. `examine/I-002_render_before_shipping_ui.md` — the new posture rule
5. `bank/open-questions/Q-007_gielinor_visualizer.md` — updated status
6. `experiments/visualizer/index.html` — the artifact being iterated. Most recent state has: iso projection, grass filling viewport (no diamond clip), pyramidal building roofs, three-layer shadows + stone plinths, iso-coord-based flora, stationary trees (sway killed), compass rose, multi-letter directions.
7. `quest-log/S007_bankstanding_phase_0_alching.md` — prior session
8. `bank/plan.md` — current mission state. Visualizer is parallel to plan items; not on the plan.

`bank/decisions/`, `bank/assumptions/`, `bank/open-questions/`, `bank/risks/` are reference material — open as cited.

## Note on the visualizer's engine

The engine (event timeline, `applyEvent` dispatch, CSS-transition movement, RAF tick loop, scrub-seek with `instant` flag) is **asset-agnostic and should not be touched during the six deltas**. All six deltas are visual layer changes. If the next session needs to change engine behavior (e.g., adding tab filtering for delta 5), keep the timeline data structure and dispatch surface intact — only add filter state on top.
