# S031 — visualizer: world scale, side-by-side layout, lane-based thought-trail bubbles

**Date.** 2026-05-22 (evening)
**Mode.** Dev-brain (Braindead).
**Status.** Final lane-based bubble layout is **not yet confirmed to work**. Everything else verified visually with screenshots during the session.

## What shipped

All changes are in `developer-braindead/experiments/visualizer/index.html` (one file).

### 1. World scaled 1.4×

Principal asked at [[S028_subtask_channel_and_guthix|S028]] close: *"give the map room to breathe."* Scaled the world coordinate space by 1.4× in viewBox units. Container size unchanged so it stays on-screen.

- `viewBox` 1200×820 → 1680×1148.
- `BUILDINGS`, `STAND`: all x/y × 1.4 (10 buildings).
- `GATHER_SLOTS`: dx/dy/bubbleY × 1.4 (10 slots).
- `LABEL_Y_OFFSET`: × 1.4 (10 entries).
- `TILE_W` 64→90, `TILE_H` 32→45. `ISO.offX/Y` 600/440 → 840/616.
- `ACTOR_Y_OFFSET.guthix` -48 → -67.
- `actorPositions['zezima']` offset -30 → -42 (in both initial seed and `resetWorld`).
- Each building's group transform: `translate(b.x, b.y)` → `translate(b.x, b.y) scale(1.4)`. Same for label groups. Means building art grows 1.4× via the transform without touching the local SVG coords of each building.
- Sky group wrapped in `transform="scale(1.4)"` so clouds + mountain layers + tree-line bezier all scale in one shot (avoids editing the 60+ polygon coordinates).
- `buildGround` viewport crop, vignette center/edges, building-clearance radius all × 1.4.
- `buildPond` cx/cy + every ring/foam/ripple/lily coordinate × 1.4.
- `buildFlora` placeTree bounds, edgeDistNorm, candidate scatter (130→180), placeIfClear bounds, bush/flower/rock scatter bounds and counts all × 1.4.
- Void backdrop, day-night-overlay (later deleted), vignette rect: width/height grown to 1680×1148.
- Initial static jebrim/zezima sprite translates × 1.4.

**Container behaviour.** Principal initially asked for "everything visually bigger" so I bumped `.stage max-width` 1380→1932 too. They reported "doesn't fit on the screen" — reverted to 1380. Net effect: same screen footprint, world is 1.4× larger in viewBox units = sprites render proportionally smaller, giving cluster members more relative breathing room.

### 2. Side-by-side layout

Principal: *"lets make the chat vertically tall, put it on the right side. The header can disappear."*

- `.topbar { display: none }` (replaced the existing `display: grid` rule, since CSS source-order matters — first attempt added a later rule that was getting overridden).
- `.crumb { display: none }` — the live-mode breadcrumb was claiming horizontal space as a flex sibling and pushing the chat away from the right edge.
- `.stage`: `max-width: none`, `display: flex`, `gap: 14px`, `height: 100vh` (explicit, not just min-height — needed for `align-items: stretch` to resolve cross-axis cleanly).
- `.world`: `flex: 1`, `position: relative`, `overflow: hidden`, `display: flex` so `.map-wrap` can be a `flex: 1` child filling the frame.
- `.map-wrap`: `flex: 1`, `min-width: 0`. (Tried `position: absolute; inset: 6px` first — also worked.)
- `svg.map`: `width: 100%; height: 100%`. preserveAspectRatio="xMidYMid meet" handles letterboxing.
- `.logbox`: `width: 380px`, `flex-shrink: 0`, `align-self: stretch`, internal `display: flex; flex-direction: column`. `.log-scroll` becomes `flex: 1`.
- `body { overflow: hidden }` to suppress page-level scrollbars.

### 3. Day-night overlay removed

Principal reported map "turns black after 3 seconds" on load. Spawned an Explore dwarf to investigate — best-supported hypothesis: `#day-night` rect with `mix-blend-mode: multiply` and a 6-second CSS transition on `fill`. Initial inline fill is fully transparent; `updateDayNight()` reads wall-clock and sets the night/dusk anchor (`rgba(60,84,138,0.55)` or `rgba(236,155,111,0.30)`); CSS transition fades to that over 6s. Multiply blend with those anchors near-blacks the map.

First fix: hide overlay in live mode CSS. Still black. Second fix: deleted the `<rect id="day-night">` element entirely. Still black on reload — but it was a browser cache. Hard refresh (Ctrl+Shift+R) confirmed the deletion fixed it.

`updateDayNight()` and `dayNightFill()` still in JS but no-op via `if (el)` guard. Left them in place; can be cleaned up next bankstanding pass.

### 4. Bubble dims scaled 2×

Principal: *"make the speech bubbles like 3x bigger"* → tried 3× → *"a bit smaller"* → settled on 2×.

In both `bubbleDims` (collision math) and `renderIntent` (rendering): MAX_BUBBLE_W 300→600, width formula coeffs 6.2/14→12.4/28, min-width 54→108, lineH 13→26, padY 4→8, font-size 11→22, baseY offset 10→20, rect rx/ry 5/3.5→10/7, inner-rect inset 1.2/2.4→2.4/4.8, stroke widths 0.7/0.4→1.4/0.8 / 1.4→2.4. Natural-Y fallback -34→-68.

### 5. Per-actor bubble accent

Principal: *"we can't see which sprite is saying what."*

- Added `ACTOR_ACCENT` map: jebrim #2e4d75, zezima #a85a2a, braindead #4c6478, guthix #2f6a44, wisp #8a7846 (--wisp-core is too light for cream-fill bubble border).
- Added `actorAccentColor(actorKey)` — reads ACTOR_ACCENT for known names; reads `dwarfNodes[id].color` / `gnomeNodes[id].color` / `penguinNodes[id].color` for sub-agents (these store the hat hex on spawn); fallback to swatch colors.
- `spawnDwarf` and `spawnGnome` now persist `color: hat` on their node entries (was hardcoded into the sprite art only).
- `renderIntent` uses `accent` for outer-rect stroke + pointer-triangle stroke (later removed) + thought-trail stroke.

### 6. Sprites enlarged

Principal: *"sprites... they are barely visible."*

- Jebrim/zezima/parallel-instance/braindead sprite `<use>` transforms: `scale(1.4)` → `scale(2.4)`.
- Wisp/guthix `<use>` added `transform="scale(1.7)"` (no prior scale).
- Dwarf and gnome inline pixel art: wrapped contents of `.bob` with `<g transform="scale(1.7)">`.

Sprite glow ellipses stay at their original radius (not scaled) — could enlarge in a future pass if visual balance feels off.

### 7. Thought-trail (replacing leader line + pointer triangle)

User: *"can't we make them thought bubbles with bubbly trails which space out nicely?"*

- Added `<g id="leader-lines">` SVG layer BEFORE `<g id="speech-bubbles">` — leader/trail elements paint underneath bubbles so any crossing rect cleanly hides them.
- `setIntent` creates `<g class="thought-trail">` element in `leaderLayer` and stores on `entry.leaderNode`. `clearIntent` removes both bubble node and trail node (with fade for non-instant). `resetWorld` removes both.
- `renderIntent` rebuilds the trail group's `innerHTML` each render: four `<circle>` elements distributed along the path from sprite head (0, -8) to bubble pointer (xOff, yOff), at parametric stops [0.20, 0.45, 0.70, 0.95] with radii [3, 5, 7.5, 10]. Cream fill + accent stroke. Group is `transform="translate(pos.x, pos.y)"`.
- Removed the pointer triangle polygon and pointer-base line from the bubble's `entry.node.innerHTML`. The biggest trail circle (r=10 at t=0.95) overlaps the bubble's bottom edge and visually anchors it.

### 8. Lane-based bubble layout — UNVERIFIED

User: *"its supposed to be that no bubble and no spec cloud overlaps."* Asked: *"is that possible?"* Answered yes via horizontal-spread approach. User: *"ok try it."*

Refactored `relayoutBubbles`:

1. Snapshot every bubble's natural state (spriteX, spriteY, naturalYOff, dims).
2. Cluster bubbles by sprite X-proximity — sprites within `CLUSTER_RADIUS = 140` share a cluster.
3. For each multi-bubble cluster: tile bubbles horizontally above the cluster's mean X. Each gets its own X lane. All share the highest (most negative) pointer Y in the cluster.
4. Inter-cluster collision fallback — classic left-to-right upward push for any wide rows that still overlap a neighbour.
5. Apply resolved `layoutXOff` AND `layoutYOff` to each entry.

`renderIntent` consumes both offsets:
- `entry.node.setAttribute('transform', \`translate(${pos.x + xOff}, ${pos.y})\`)` — bubble shifts horizontally.
- Trail circles' `cx = c.t * xOff` — diagonal from sprite to bubble.

**Not verified visually.** Live test pending. Watch for:
- Clusters too wide on small screens — leftmost/rightmost bubbles clipping off the viewBox.
- Inter-cluster Y overlap (e.g., when quest-hall row collides with keepsake-vault row).
- Single-bubble fallback path (cluster.length === 1) — `continue` keeps natural cx/pointerY, xOff = 0. Should match pre-S029 behaviour.
- Trail diagonal angle when xOff is large — does the 4-circle pattern still read as "thinking" or does it look like a connector line?

## Mid-session debugging notes

- **Browser cache bit us.** "Map turns black" appeared to persist after my fixes. Hard refresh (Ctrl+Shift+R) was the actual unlocker. Should have asked for hard refresh sooner.
- **CSS source-order matters.** First attempt at hiding the topbar added `.topbar { display: none }` BEFORE the existing `.topbar { display: grid }` rule. Source-order applied `grid` last, won. Fixed by editing the original rule instead of adding a later one.
- **File-modified-mid-edit twice.** Got "File has been modified since read" errors twice during the lane-layout edit. No obvious cause — possibly a hook touching the file during the edit. Re-read + retry worked each time. Track if it recurs.
- **ensureActorExists warning.** Console showed `visualizer: ensureActorExists has no spawn path for actor braindead-ed610cbe`. The braindead-{sid8} suffix-strip isn't covering some code path. Not related to map disappearing, but worth fixing — small follow-up.

## Carried-forward

- **Lane-based bubble layout untested.** Step 0 next session.
- **ensureActorExists braindead suffix bug.** Find the path that didn't strip; align with `NON_PLAYER_SUFFIX_ACTORS` from [[S028_subtask_channel_and_guthix|S028]].
- Plus everything carried from [[S030_penguins_subagent_and_research_folder|S030]]: live-test penguins, live-test parallel Braindead, etc.

## Files of note

- `developer-braindead/experiments/visualizer/index.html` — only touched file.
- `developer-braindead/respawn.md` — updated for next session.
