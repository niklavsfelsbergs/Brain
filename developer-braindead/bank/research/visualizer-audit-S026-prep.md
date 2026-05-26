# Visualizer audit S026 — prep

> **Why this file exists.** [[S025_parallel_player_instances]] closed by shipping [[D-017_parallel_player_instances]] (parallel-player sprite tinting) and [[D-018_parallel_session_substrate_isolation]] chunks 1–3 (per-session substrate isolation in the hook + per-session intent filenames). The next session audits the **visualizer SPA** — `developer-braindead/experiments/visualizer/index.html` (3249 lines) — to fix what's clearly broken and lift the obvious wins. This file is the primer: how the renderer works today, where the bugs are, where the improvements live. Cite line numbers so the audit session goes straight to the lines.
>
> **Recon basis.** Three Explore dwarves (D1 architecture, D2 event dispatch + state, D3 CSS/UX) walked the file in this session. Their findings are merged and de-duped below. Filtered out: findings already closed by D-017/D-018, design choices that read as bugs but aren't (e.g., scrub-back snaps rather than reverse-animates — intentional).
>
> **Predecessor.** [[bank/research/visualizer-audit-S021.md]] is the historical audit that drove S022's fixes. It covered the hook + visualizer together; the issues there are largely closed or moved. This audit is visualizer-scoped.

---

## How it works

### Engine (index.html:2876–3059)

A single-file SPA. The dispatch surface is one `switch` (lines 2886–2990) over 14 event types — `applyEvent(ev, instant)`. Two modes share the same dispatcher:

- **Replay mode** (default). EVENTS is a hardcoded JS array (lines 2125–2239). `tick()` (line 3049) on RAF accumulates `t += dt * speed`, walks the cursor, invokes `applyEvent`. Scrub slider (lines 3040–3047) calls `seekTo()` which resets world on backward jumps and re-runs events up to target with `instant=true`.
- **Live mode** (`?live=1`). `pollLive()` (lines 3184–3245) fetches `state.ndjson?_=<ts>` every 500ms, tails new bytes against `liveBytes`, applies each new line. First poll bootstraps with `instant=true`; later polls animate.

The engine is **asset-agnostic and should not be touched during fix iteration** (per respawn.md). Keep extending; don't rewrite.

### Event dispatch — the 14 cases

| Event | Line | Mutates | DOM/animation |
|---|---|---|---|
| `session-start` | 2887 | `currentSession`, `activePlayer` | topbar text, focal label |
| `log` | 2897 | COMMS log | chat line + ticker |
| `move` | 2901 | `currentBuilding[actorKey]`, `actorPositions`, clears player intents | sprite walks 1800ms cubic-bezier, dust particles, bubble follows |
| `intent` | 2938 | `intents[actorKey]` | speech bubble fade-in 360ms |
| `action` | 2948 | COMMS log | chat speaker line |
| `narrate` | 2966 | COMMS log | system-voice italic |
| `spawn-dwarf` | 2969 | `dwarfNodes`, `dwarfCount`, optional intent | dwarf sprite fade-in 500ms, color from 3-cycle |
| `despawn-dwarf` | 2973 | removes from registries | fade-out 500ms |
| `spawn-gnome` | 2977 | `gnomeNodes`, `gnomeCount` | gnome sprite (taller hat, slimmer) |
| `despawn-gnome` | 2981 | removes from registries | fade-out |
| `spawn-braindead` | 2987 | `braindeadNode`, `braindeadActive` | fade-in |
| `despawn-braindead` | 2988 | clears registries | fade-out |
| `spawn-wisp` / `despawn-wisp` | 2985–2986 | wisp glow sprite | |
| `despawn-instance` | 2956 | for instance ≥ 2 removes node + position + intent; for instance 1 keeps sprite, clears intent | conditional fade-out |
| `commit` | 2989 | COMMS log | dashed-top styled line |

**Routing key.** Every event with `actor` is routed via `instanceKey(actor, instance)` (line 2806): `actor-N` for N>1, bare `actor` for N=1. Static-HTML jebrim/zezima are instance 1 by construction.

### State shapes (in-memory)

| Name | Line | Lifecycle |
|---|---|---|
| `currentBuilding` | 2278 | set on move; cleared on despawn-instance / despawn-braindead |
| `intents` | 2279 | created in `setIntent`; cleared on move for players (line 2911) but **persisted for sub-agents** (line 2912); destroyed on despawn |
| `actorPositions` | 2276 | seeded for jebrim/zezima; set on every spawn + move; deleted on despawn |
| `actorMoveTimers` | 2277 | keyed by **actor (not instanceKey)** — see Bug #2 |
| `dwarfNodes` / `gnomeNodes` | 2266–2267 | populated on spawn-{dwarf,gnome}; deleted on despawn |
| `instanceNodes` | 2286 | secondary sprites for player instance ≥ 2; static HTML covers instance 1 |
| `instanceLastEventAt` | 2285 | timestamp per actorKey; read by 5-min idle-despawn loop (lines 3170–3178) |
| `currentSession` | 2272 | from session-start |
| `activePlayer` | 2275 | drives focal label |
| `dwarfCount` / `gnomeCount` | 2273–2274 | ticker counters |
| `wispActive` / `braindeadActive` | 2269–2271 | gate `ensureActorExists` self-heal |
| `currentEventWallTime` | ~2870 | drives ticker wall-clock |

### SVG layer model (lines 873–923)

z-order, bottom to top: `ground` → `ground-overlays` → `pond` → `paths` → `flora-back` → `buildings` → `flora-front` → `particles` → `characters` → `day-night` overlay → `building-labels` → `speech-bubbles` → `vignette`.

Buildings (10 total) live in `BUILDINGS` (lines 994–1005) with standing spots in `STAND` (lines 1008–1019). Geometry is rendered by `isoBuilding()` (line 1455) with shadow / plinth / two wall faces / two roof slopes / per-building details. Wall + roof textures are SVG `<path>` from `wallTexture()` (1384) and `roofTexture()` (1440).

Ambient particles bake in per building: candle flicker on lorebook windows, parchment flutter on inbox bulletins, smoke from quest-hall / inn / workshop chimneys (different speeds per building), gem-shine on keepsake-vault.

### Actor sprites

- **Static HTML** for jebrim and zezima (lines 882–907) — born in DOM with SMIL `<animateTransform>` idle-breath (vertical 1 → 0.95 → 1, 2.6s / 2.9s). Switched from CSS-keyframe to SMIL after a `.bob` descendant-selector bug in S024.
- **Dynamic spawn** for dwarves (line 2365), gnomes (2419), wisp (2596), braindead (2569), and parallel player instances (2484–2555). Instance ≥ 2 sprites are clones of the static HTML, with hue-rotate filter (`tint-2/3/4`, 140°/220°/80° from D-017) and a small `.instance-badge` gold "·N".
- **Walking** sets `transition: transform 1800ms cubic-bezier(...)`, toggles `.walking` class for jerkier bob, drops dust particles every 240ms.

### Bubble rendering (lines 2686–2772)

`setIntent` lazily creates `<g class="speech-bubble">`, `wrapBubbleText` word-wraps to ≤2 lines × 50 chars, bubble centers above actor with -34px y-offset, follows on move. **Player bubbles clear on building change; sub-agent bubbles persist for the whole task lifetime** — that asymmetry is intentional (player intent expires at the new building; dwarf intent is a task label).

### COMMS panel (lines 356–530, 962–977)

Tan OSRS-style panel with 8 filter tabs. Each tab carries a `data-filter`; the `.log-scroll[data-filter="X"]` selector hides non-matching `.log-entry[data-speaker="X"]` (lines 514–520). Line classes: `.intent`, `.action`, `.narrate`, `.system`, `.read`, `.commit`, `.session-start`. Per-actor color tints come from CSS vars `--<actor>-text` (dark, for the tan background) and `--<actor>-dot` (bright, for the dark frame border). Auto-scroll to bottom on every append (line 2783) with no scroll-lock toggle.

### Day/night overlay (lines 292–299, 914, 3114–3144)

Fullscreen SVG `<rect>` with `mix-blend-mode: multiply`. Four hour-keyed anchor tints (midnight blue → dawn orange → noon transparent → dusk amber) interpolated by wall-clock. Refreshed every 60s. **Wall-clock based in both modes** — see Bug #1.

### Reduced-motion (lines 301–310)

`@media (prefers-reduced-motion: reduce)` zeros `.bob`, `.candle-flicker`, `.parchment-flutter`, `.forge-smoke`, and `display: none`s the day-night overlay entirely. Sprites still render; motion gone.

### Self-healing / reconciliation

`ensureActorExists` (line 2484) fires when a move/intent arrives for an unknown actor. Cases:
- Player instance ≥ 2 → `spawnPlayerInstance()`.
- Braindead/wisp first event without prior spawn → spawn at inferred building.
- Dwarves/gnomes → no self-heal; they only enter via explicit spawn events.

---

## Bugs

Ordered by severity. All have file:line refs.

### B1 — Day/night overlay tracks wall clock in replay mode [med]
Lines 3114–3144. `dayNightFill()` reads `new Date().getHours()`, not the replay timeline `t`. Replay at 3 AM browser time is permanently midnight-blue regardless of where the slider is. Live mode is correct; replay needs the timeline.

### B2 — `actorMoveTimers` keyed by actor, not instanceKey [med]
Line 2277, used at lines 2344–2346. Two parallel instances of jebrim share one timer slot. Second move clobbers first's timer. The CSS transition is the real animation driver, so sprites both move correctly, but the `.walking` class teardown can fire at the wrong time, leaving a sprite in walking-pose after it stopped or stripping the class from a sprite still mid-walk. Re-key to `instanceKey`.

### B3 — Braindead missing from COMMS first-class [med]
Tab HTML absent (around line 973), filter CSS gap at line 518/520, no dot/legend row. The S021 audit flagged this as "C2 structural gap" and it's still open. With dev-brain mode now actively used, Braindead's chat lines have nowhere to land coherently.

### B4 — Sub-agent intent silence on clear [med]
Lines 2686–2703 + 2910–2912. `setIntent("")` calls `clearIntent` — so any caller that empties text drops the bubble. For dwarves/gnomes the bubble is supposed to be a persistent task label; if a flow path ever clears it mid-task, it goes silent until next intent. Worth confirming the existing emit-event path can't trigger this; if it can, gate `clearIntent` on `isSubAgentActor()` returning false.

### B5 — `liveBytes` doesn't recover from `state.ndjson` shrink [med]
Lines 3194–3199. Tail logic compares `text.length` against `liveBytes`. If the file is manually reset / rotated / truncated (e.g., dev-brain cleanup), `liveBytes` stays at the old high-water mark and *all* new events are skipped silently. Reset `liveBytes` when `text.length < liveBytes`.

### B6 — LIVE poll error swallowed silently [low]
Lines around 3222–3226. Fetch + parse errors caught into empty handler. A corrupted state.ndjson or a server hiccup is invisible to the operator. Surface as a console.warn + small UI badge.

### B7 — `instance: 0` collides with base actor [low]
Line 2807. `const n = +instance || 1;` — falsy instance becomes 1, mis-keying to the bare actor name and racing the static HTML sprite. Hook should validate `instance >= 1`; visualizer should reject 0 with a warning.

### B8 — Speech bubble can overflow narrow viewports [low]
Lines 2733–2760. Width grows with longest line × 6.2px, no max-width clamp. At 100-char intent on a narrow window, the bubble runs off-screen. Add a max-width or hard wrap shorter.

### B9 — D-018 read race on `state-actors.json` migration [low — out of audit scope but flagged]
Hook-side, `emit-event.py` lines 167–192. Two parallel sessions reading the legacy flat shape simultaneously then both writing nested can lose one write. Atomic write (B8) means only one survives; the visualizer reads only the event stream so it's not directly affected. Acceptable for now, note for follow-up.

---

## Improvements

Ordered by payoff.

### I1 — Centralize actor color taxonomy [high payoff]
Lines 71–82 vs hardcoded hex at lines 427, 505, etc. (S021 C1, still open). Recoloring an actor today means hunting hex strings across CSS + JS. Convert all per-actor color uses to the `--<actor>-text` / `--<actor>-dot` vars. Payoff: single-source-of-truth.

### I2 — Scroll-lock for COMMS panel [high payoff for users]
Line 2783 unconditionally pins scroll to bottom. Standard pattern: detect "user scrolled up" via `scrollTop < scrollHeight - clientHeight - threshold`, then suppress auto-scroll until they hit a "jump to latest" button. Without it, reading history is impossible during active sessions.

### I3 — Bubble drop-shadow [med payoff]
Lines 2748–2758. Bubbles have no shadow; tan-on-busy-map can blend. Add `filter="drop-shadow(2px 2px 4px rgba(0,0,0,0.25))"` to the bubble `<g>` or via `<defs><filter>`. Small change, big readability win.

### I4 — Filter-tab unread indicator [med payoff]
Lines 468–520. When a filter is active, new matching lines append silently. A small badge count (or pulse) on the tab makes incoming activity visible without forcing a switch.

### I5 — Idle-despawn timeout configurable [med payoff]
Line 2287, `INSTANCE_IDLE_MS = 5 * 60 * 1000`. Fine for sessions firing constantly; cruel for long think-times. Make it a query-string param (`?idle=900`) or bump default to 15–30 minutes.

### I6 — Color cycle wrap visibility for dwarves/gnomes [low payoff]
Lines 2378, 2432 — 3-color palette wraps silently on D4/G4. Either document the wrap, expand the palette to 6, or add a tiny per-actor numeric suffix in the bubble pointer.

### I7 — Building label offsets dynamic from geometry [low payoff]
Lines 2044–2055. `LABEL_Y_OFFSET` is hand-tuned per building; geometry changes would silently detach labels. Compute from `h` + `r` at render time, or comment the dependency loudly.

### I8 — Vignette follows active player [aspirational, low priority]
Line 591. Vignette is centered on viewport, not on active actor. If we ever add a camera-follow, also drift the vignette.

### I9 — Live-mode "freeze" toggle [low payoff]
Line 3241. 500ms polling with full animation is fine for slow sessions; rapid spawn bursts can overwhelm. Add a freeze-and-resume button. Optional batching: collapse a burst into one wave animation.

### I10 — Wisp glow filter precomputed [low payoff]
Line 260. `filter: url(#wispGlow)` rerenders per frame. For a near-static sprite this is wasted GPU. Pre-bake or apply only when moving.

---

## Open questions (verify by running the app)

1. **Cross-browser jitter determinism.** The hash at line 1053 uses signed 32-bit imul; do Firefox / Safari / Chrome produce identical actor positions? If not, parallel-instance sprites might drift.
2. **Parallel-instance tint visibility on limited-gamut monitors.** `hue-rotate(140°/220°/80°)` distinguishes well on calibrated screens; verify it still reads on TN panels or color-blind users.
3. **Live bootstrap performance.** First poll on a state.ndjson with 1000+ events fires 1000 SVG appends with `instant=true`. Modern desktop should be <1s but worth confirming.
4. **Despawn-instance for instance 1.** Lines 2956–2964 — does instance 1's static sprite stay interactive after a `despawn-instance` event with `instance: 1`? Spec says "keep sprite, clear intent only," but worth confirming visually.
5. **Idle-despawn sweep granularity.** Lines 3163–3178 — 30s sweep interval × 5min cutoff means actual despawn lags by up to 30s. Acceptable?
6. **Gnome render path live test.** No `state-gnomes.json` exists on disk yet (D2 dwarf noted). Gnome rendering is wired but unexercised. First live gnome spawn (carried from S020+) is the natural test.

---

## How to start the audit (recommended order)

1. **Open visualizer in live mode**, both parallel Jebrim sessions still running. Confirm the bubble-clobber bug (chunk 3 of D-018) is gone now that this session's protocol edit has landed and any session that re-reads `meta/` adopts per-session intent files.
2. **B1 day/night in replay** — easy + visible. Pick replay or live anchor depending on what reads better.
3. **B3 Braindead COMMS** — small, finishes the S021 C2 gap.
4. **I1 color taxonomy + I2 scroll-lock** — both high-payoff UX wins, contained in CSS + small JS deltas.
5. **B2 actorMoveTimers re-key + B5 liveBytes shrink** — correctness fixes for parallel sessions and dev-brain cleanups respectively.
6. **First live gnome spawn** (from respawn Step 2) — exercises the gnome render path under D-018's session-scoped substate. Open question #6.

Lower-priority items (B4, B6–B8, I3–I10) batch into a polish pass after the high-value items land.

---

## Related

- [[D-014_visualizer_chat_panel]] — narrate/action events + COMMS chat panel.
- [[D-017_parallel_player_instances]] — parallel player instances (sprite tinting + per-instance bubbles + per-instance event routing).
- [[D-018_parallel_session_substrate_isolation]] — per-session substrate isolation (state-actors / state-dwarves / state-gnomes re-key + per-session intent filenames).
- [[Q-008]] — visualizer aliveness picks (deferred wanderers + trail echoes).
- [[bank/research/visualizer-audit-S021.md]] — prior audit; C1 (color taxonomy) and C2 (Braindead COMMS) are still open here as I1 and B3.
