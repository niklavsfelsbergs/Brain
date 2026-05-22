# S024 — Visualizer aliveness pass (Q-008 options 1–3) + intent re-emit on move

**Date.** 2026-05-22.
**Mode.** Dev-brain.
**Outcome.** Q-008 options 1, 2, 3 shipped; one bug surfaced under live observation and fixed.

## What was asked

Principal entered dev-brain after `/clear` and asked to work on aliveness. Picked the most ambitious slice from the Q-008 menu — all of options 1–3 (idle sprite breath + per-building ambient particles + day/night hue overlay).

## What was built

### 1. Idle sprite breath

First attempt: CSS `@keyframes idle-breath` with `translateY` on `.actor .bob`, three speed buckets via `:nth-of-type` for stagger.

Did not visibly animate. Wisp's CSS animation (`.wisp-bob` direct class) was working — same engine, same `<g>` element shape, just a direct-class selector instead of descendant.

Switched to direct-class selector `.bob` — still nothing visible.

Pivoted to SMIL `<animateTransform>` embedded inline in jebrim's and zezima's `.bob` groups. SVG-native, bypassed whatever CSS quirk was blocking the descendant rule. Worked immediately.

Then the design refinement: principal asked for "less up/down, feet shouldn't move." First tried `type="matrix"` on the SMIL — silent failure, SMIL spec restricts `type` to translate/scale/rotate/skewX/skewY, no matrix. Pivoted to `type="scale"` with `values="1 1; 1 0.95; 1 1"`. Scale origin is `.bob`'s (0,0) — mid-body — so the head/hat compress ~1.5px downward at peak and the feet drift ~0.35px upward (imperceptible). Reads as breath rather than float.

Cycle: jebrim 2.6s, zezima 2.9s, staggered by -0.8s.

### 2. Per-building ambient particles

- **braindead-workshop** — new forge chimney + 3 staggered smoke puffs (`.forge-smoke`, 4.2s linear). Lighter alpha + slower than the inn's hearth smoke.
- **lorebook-library** — lit lower-right window (`#cf9a2c` base + `#ffce5b` flicker pane) and lit upper-left window (`#a87a26` + `#ffd97a` flicker). `.candle-flicker` is `steps(3)` so the light reads as flame not fade.
- **inbox-square** — three bulletin notes get `.parchment-flutter` (`ease-in-out` rotation ±1.4° around `top center` transform-origin), staggered.
- **keepsake-vault** — left alone; pre-existing `.gem-shine` already covers it.

### 3. Day/night hue overlay

New `<rect id="day-night" class="day-night-overlay">` placed below the vignette in DOM order (above characters/buildings, below vignette/labels/bubbles). `mix-blend-mode: multiply`, `pointer-events: none`, `transition: fill 6s linear`.

JS function `dayNightFill()` interpolates between four anchor colors keyed on wall-clock hour:
- 00:00 — deep cool blue `rgba(60,84,138,0.55)`
- 06:00 — warm orange-pink `rgba(246,200,154,0.32)`
- 12:00 — near-transparent `rgba(255,250,240,0.04)`
- 18:00 — warm amber `rgba(236,155,111,0.30)`

`updateDayNight()` runs at boot and every 60 seconds via `setInterval`.

### 4. Reduced-motion gate

`@media (prefers-reduced-motion: reduce)` zeroes `.bob`, `.candle-flicker`, `.parchment-flutter`, `.forge-smoke` animations and `display: none`s the day/night overlay. Per Q-008's accessibility note.

### 5. Intent re-emit on actor move (bug fix)

Principal noticed Jebrim's bubble was gone despite his parallel session being active. Investigation: state.ndjson showed a `move` event for jebrim → quest-hall at 07:21:35, then 4+ `action` events but no `intent` event. The visualizer's move handler clears player intents on building change (`clearIntent(ev.actor)` at line 2803), and the hook only emits `intent` events when the intent *file* changes. Action events don't repop bubbles. So a working session that uses tools but doesn't update its intent file silently loses its bubble after the first move.

Fix in `developer-braindead/.claude/hooks/emit-event.py`: new helper `_reemit_intent_after_move(actor, wall)` reads `.claude/intent/<actor>.txt` and emits a fresh `intent` event with its content. Called right after a `move` event is appended for the main actor (sub-agents skip — their bubbles already persist across moves in the visualizer). Sub-agents have no intent file so the helper's `path.exists()` check early-returns for them.

## Observations worth keeping

**SMIL > CSS for SVG animation when the descendant selector doesn't take.** `.wisp-bob` direct-class worked; `.actor .bob` descendant didn't, despite identical DOM shape. Didn't find the root cause — could be `<g>` element + descendant-selector quirk in Chrome, could be something with the static-HTML actor vs dynamically-created wisp. SMIL `<animateTransform>` sidestepped it cleanly. Worth a `bank/decisions/` note if it comes up again.

**SMIL `animateTransform type="matrix"` is invalid.** Spec restricts `type` to translate/scale/rotate/skewX/skewY. Silent failure, no console error. Burned one iteration on this. For anchored scale, the path is additive composition of scale + translate, or restructuring the symbol with wrapper groups.

**Intent re-emit on move is design-shaped, not just plumbing.** The visualizer's "intents expire on building change" rule was written assuming intent writes were frequent. In practice, a session can run for minutes on tool calls without writing a new intent line — and the bubble vanishes. Re-emit on move papers over this without changing the visualizer's expire-on-move rule. If the pattern recurs (e.g., dwarves/gnomes hit similar silences), the underlying design choice is worth revisiting.

**Watching-it-run found the intent bug, not the audit.** Third-tier observation phase confirms the S023 pattern: code review and validation passed; only sustained live use surfaced the silence. Four-incident pattern now (S014, S022, S023, S024).

## Files touched

- `developer-braindead/experiments/visualizer/index.html` (+118 / −7 from Q-008 work, plus the SMIL iterations)
- `developer-braindead/.claude/hooks/emit-event.py` (+ `_reemit_intent_after_move` helper and one call site)
- `developer-braindead/bank/open-questions/Q-008_visualizer_aliveness.md` — updated status (next entry)
- `developer-braindead/respawn.md` — updated at session close
