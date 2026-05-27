# [[S049_17e701eb_visualizer_state_aware_motion_and_action_line|S049]] · D1 — wander animation fix

**Scope:** fix sprite ambient-wander so sprites visibly drift smoothly within ±18px instead of standing still / teleporting. Hypothesis from principal: CSS `.wander { transition: transform 1200ms }` transitions only the CSS `transform` property, but JS sets the SVG `transform` attribute — mismatch = instant change, no animation.

**Started:** 2026-05-23 (session sid8 `17e701eb`, Braindead dwarf).

## Turn log

- Read `index.html:280–330` (CSS). Confirmed line 305: `.wander { transition: transform 1200ms ease-in-out; }`. CSS transition targets the CSS `transform` property.
- Read `index.html:2380–2400` (`wrapWander`). Confirmed line 2391: `wander.setAttribute('transform', 'translate(0,0)')` — SVG attribute, no CSS-property mirror.
- Read `index.html:2624–2638` (`tickWanderForActor`). Confirmed line 2637: `wander.setAttribute('transform', \`translate(${dx},${dy})\`)` — SVG attribute, same shape.
- Read `index.html:2695–2716` (`moveActor`). Confirmed line 2713: `wanderInner.setAttribute('transform', 'translate(0,0)')` — third site, same shape.
- Grepped `wander` and `\.walking` across the whole file. No other code path applies any CSS `transform` style to `.wander` elements. Only three writes touch the wander transform; only one comment (line 2625) references a "CSS rule snaps wander to 0,0 during .walking via transition:none" but that rule does **not** exist in the CSS — only the JS-side guards (`tickWanderForActor` early-exit on `.walking`, `moveActor` reset) keep the wander from interfering during walks. So the fix is purely the three call-sites; no extra CSS coordination needed.
- **Hypothesis confirmed.** The CSS animates a property the JS never sets.

## Fix applied

Switch all three wander transform writes from SVG attribute → CSS style, with `px` unit suffix:

- `index.html:2391` (`wrapWander` init) — `setAttribute('transform','translate(0,0)')` → `style.transform = 'translate(0px,0px)'`.
- `index.html:2637` (`tickWanderForActor`) — `setAttribute('transform', \`translate(${dx},${dy})\`)` → `style.transform = \`translate(${dx}px,${dy}px)\``.
- `index.html:2713` (`moveActor` clear-on-move) — same shape as `wrapWander` init.

SVG attribute is not removed: the wander group is created fresh in `wrapWander` and never had the attribute set by anything else, so there is no shadowing SVG attribute to strip in the steady-state path. (The initial `setAttribute('transform','translate(0,0)')` in `wrapWander` is the line we're replacing — so after the swap, no SVG `transform` attribute is ever written on `.wander` elements.)

## Verification

What I could verify from the dwarf shell (no browser GUI available to me directly):

- **Sanity check on the edits.** Grepped `wander\.(setAttribute|style)|wanderInner\.(setAttribute|style)` across `index.html`. Four hits, all expected:
  - `2390: wander.setAttribute('class', 'wander')` — class assignment, untouched (correct).
  - `2394: wander.style.transform = 'translate(0px,0px)'` — `wrapWander` init, new shape.
  - `2642: wander.style.transform = \`translate(${dx}px,${dy}px)\`` — `tickWanderForActor`, new shape.
  - `2718: wanderInner.style.transform = 'translate(0px,0px)'` — `moveActor` reset, new shape.
  No stray `setAttribute('transform', ...)` on wander elements remains.
- **Server stood up.** `python -m http.server 8765` in `developer-braindead/experiments/visualizer/`. `http://localhost:8765/` returns 200; `state-switchboard.json` carries 4 live sessions including this dwarf's own braindead-instance-2 at `braindead-workshop`, jebrim-2 at `bank`, and guthix-1.
- **Wander candidates in the live manifest** that would visibly drift after the fix: `braindead` (instance 2) and `jebrim` (instance 2). `guthix` is excluded via `NO_WANDER_ACTORS`. Bonus: any static `jebrim`/`zezima` revealed by `syncSpritesFromManifest` would also wander, but only `jebrim` has a session right now and it's instance 2 (parallel-instance sprite).

What I want the principal to confirm visually with `http://localhost:8765/?live=1`:

- Braindead sprite at `braindead-workshop` drifts smoothly within ±18px over ~1.2s every 4–12s.
- Drift is suppressed during a `.walking` transition (existing guard at line 2631 plus the manifest sync's `moveActor` call).
- Speech bubble (intent `"Spawning S049 map-fix dwarves"` on Braindead, `"Bankstanding B-003 — Phase 0 decision pending"` on Guthix) stays anchored to the building, NOT following the wander offset. Wander is on the inner `<g class="wander">`; bubble position is computed from the outer actor transform → bubble should not move with the drift.
- No console errors.

## Notes on broader pattern (do not fix — out of scope per brief)

`setActorTransform` (line 2688) and the outer-actor walking animation at line 2722 use the **same SVG-attribute-vs-CSS-transition pattern** that broke wander (`.actor { transition: transform 1800ms ... }` at line 225 + `el.setAttribute('transform', ...)` everywhere). It apparently works in practice in modern browsers (Chrome/Edge/Firefox do transition the SVG `transform` attribute via the CSS Transforms Level 2 path for SVG elements), and the principal has scoped my work to wander only. So I'm not touching it — but flagging here for awareness in case the wander symptom turns out to be browser-specific. If after the fix wander still doesn't animate in the principal's browser, the next hypothesis is that this browser engine simply doesn't bridge SVG-attribute transitions and we need to switch `setActorTransform` to CSS `transform` too. (The actor walking has historically been observed to work, so the bridge is likely active for that path; the question is why it apparently isn't active for wander on the same element. Possible answer: walking gets an explicit `el.style.transition = '...'` set on the element via JS, which sometimes nudges the browser into property-mode transitions; wander relies purely on the static CSS rule. The CSS-property shape we just applied side-steps the question.)

## Verdict

- **Hypothesis confirmed:** yes. CSS rule at `index.html:305` transitions the CSS `transform` *property*; all three wander writes were setting the SVG `transform` *attribute*. Property and attribute are distinct surfaces in the CSS-vs-SVG transitions story; the transition was not animating the writes.

- **What changed (3 sites in `developer-braindead/experiments/visualizer/index.html`):**
  - **L2391 → L2394** (`wrapWander` init): swapped `wander.setAttribute('transform', 'translate(0,0)')` for `wander.style.transform = 'translate(0px,0px)'`. Added comment explaining the CSS-vs-SVG distinction.
  - **L2637 → L2642** (`tickWanderForActor`): swapped `wander.setAttribute('transform', \`translate(${dx},${dy})\`)` for `wander.style.transform = \`translate(${dx}px,${dy}px)\``. Added comment about `px` unit requirement on the CSS side.
  - **L2713 → L2718** (`moveActor` clear-on-move): swapped `wanderInner.setAttribute('transform', 'translate(0,0)')` for `wanderInner.style.transform = 'translate(0px,0px)'`.
  - SVG `transform` attribute is no longer set on `.wander` elements anywhere → no shadowing of the CSS property.

- **How verified:**
  - Code-level: grep confirms only the three intended writes exist; no stray writes; no other code path touches `.wander` styling.
  - Server-level: visualizer at `http://localhost:8765/?live=1` is reachable; manifest carries this Braindead session at workshop and a Jebrim-2 at bank — both should now visibly wander. Server left running in background (task `bt83pweka`) for principal to confirm.
  - Constants untouched: `WANDER_MAX_PX = 18`, `WANDER_MIN_INTERVAL_MS = 4000`, `WANDER_MAX_INTERVAL_MS = 12000`.

- **Open notes for principal:**
  - Out-of-scope pattern flag (above): `setActorTransform` uses the same SVG-attribute pattern as the pre-fix wander code, but actor walking is observed to work — likely a CSS Transforms L2 SVG bridge that activates differently. Not touching per brief. If wander still doesn't visibly animate after this fix, that's the next hypothesis to chase.
  - The visualizer's HTTP server is still running on `:8765` in this dwarf's shell (background task `bt83pweka`). Stop with TaskStop or `taskkill` on the python process when done.

