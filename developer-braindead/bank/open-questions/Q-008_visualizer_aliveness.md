# Q-008 — Make the visualizer world feel alive

**Status.** `partially-answered` — options 1–3 shipped in [[S024]]. Options 4 (NPC wanderers) and 5 (trail echoes) deferred without committed trigger.

## The question

The visualizer currently feels static between events. Sprites stand at building centers, idle. Move events animate walking; buildings sit still. Between turns the world is dead.

What subset of ambient motion is worth building, and when?

## Why this is open

Aesthetic alignment with the project (RuneScape-themed) suggests the visualizer should feel like a *world*, not a status portrait. The audit's I15 ("per-building character") already named the need from a different angle. None of the ideas below change the engine or the dispatch surface — they're additive on top of the existing renderer. Cost is bounded; the question is which to build first and whether the timing is right.

The case *against* building soon: the agent is still settling into its operating rhythm. Sub-agent flows have only just been tested; visualizer audit fixes haven't even shipped a follow-up live gnome spawn yet. Decorating before the operating layer is stable is the [[S008]] anti-pattern.

The case *for* building soon: idle aliveness specifically *makes the dead time legible*. When the agent is thinking and nothing is happening on disk, the world doesn't read as broken — it reads as a place existing between events. That value compounds the longer the visualizer is open.

## Options (ranked rough effort → impact)

1. **Idle sprite breath.** 2–3px vertical sway on a slow loop while actors stand. Pure CSS `@keyframes` on `.actor`. No engine touch. Lowest cost, highest "stops looking dead" payoff.
2. **Per-building ambient particles** (= audit I15). Chimney smoke at `braindead-workshop`, candle flicker at `lorebook-library`, parchment-flutter at `inbox-square`, gem-glow at `keepsake-vault`. SVG animations attached to each building's `<g>`, rendered once at build, no dispatch changes.
3. **Slow day/night hue overlay.** Single fullscreen `<rect>` tinted by real wall-time, warm at noon → cool at night. Lanterns become more prominent in the dark phase. One element, atmospheric payoff.
4. **NPC wanderers.** 2–3 anonymous villager sprites walking random paths between buildings, never claimed by any agent. Pure scenery motion; suggests the world exists beyond the agent. Risk: sprite design must be distinct enough from players/dwarves/gnomes that they don't read as "agents."
5. **Trail echoes when actors walk.** Fading footprint or grass-bend sprite at recent path points. Cheap to draft, easy to overdo. Risk: visual noise that fights chat/COMMS legibility.

## Recommendation when picked up

Ship (1) + (2) first — both are additive, both cover the "static map" complaint, neither touches the engine or `applyEvent`. (3) is the next-best lever and slots in cleanly alongside. (4) is fun but needs a wander engine and the sprite-design discipline to stay distinct. (5) is the riskiest for readability; reserve until (1)–(4) are in and you can judge whether more motion *helps* or competes.

All of these should be gated behind `prefers-reduced-motion` — costs nothing to do at build time, prevents the visualizer from becoming hostile on low-power displays or for accessibility.

## Effort

- (1) idle breath: <30 minutes.
- (2) ambient particles: half-day, one pass per building.
- (3) day/night overlay: 1–2 hours including the warm/cool palette pick.
- (4) NPC wanderers: full day; needs a path-graph for wandering.
- (5) trail echoes: 2–3 hours, plus a tuning pass.

## What "answered" would look like

A `D-NNN` deciding scope (which subset of 1–5, behind a feature flag or always-on, motion-reduce respected). Or a deliberate "defer" with the trigger that would unblock it (e.g., "after the gnome workshop ships," "after first live gnome spawn validates the audit fixes").

## Handoff notes for the next agent

This is **deferred design exploration**, not committed work. The audit fixes from [[S022]] should ship and prove out first — adding more visible motion before the attribution layer is solid would make a chaotic stream chaotically *prettier*, not clearer.

When picked up: start with idle sprite breath (#1). It's the smallest possible change, the easiest to verify, and it tells you whether the GPU cost across all the additive layers is going to be a concern.

Related: audit finding I15 (per-building character) in `bank/research/visualizer-audit-S021.md`; [[D-014]] (chat panel + intent bubbles — already adds some motion); [[Q-007]] (the visualizer's founding question).

## Update — [[S024]] (2026-05-22)

Options 1–3 shipped together in one session. What landed:

- **(1) Idle breath.** Initially attempted via CSS but the `.actor .bob` descendant selector didn't take (cause not pinned — `.wisp-bob` direct class worked fine). Pivoted to inline SMIL `<animateTransform type="scale">` on each player's `.bob` group. Final form is a vertical scale (1 → 0.95 → 1) at 2.6s/2.9s cycles, staggered. Reads as breath rather than float because scale-origin is mid-body, so the head compresses ~1.5px and feet drift only ~0.35px.
- **(2) Ambient particles.** Forge smoke at braindead-workshop; lit candle-flicker windows at lorebook-library (lower-right + upper-left); parchment-flutter on three inbox-square bulletin notes. Keepsake-vault's pre-existing `gem-shine` left alone.
- **(3) Day/night overlay.** Fullscreen `<rect>` below the vignette, `mix-blend-mode: multiply`, JS interpolates between four anchor tints (midnight cool-blue / dawn warm-pink / noon near-transparent / dusk amber) keyed on wall-clock hour, refreshed every 60s.
- **Reduced-motion gate.** `@media (prefers-reduced-motion: reduce)` zeroes the new animations and hides the overlay.

Options 4 (NPC wanderers) and 5 (trail echoes) **deferred without committed trigger**. Recommendation when re-picked: only ship (4) after the operating layer stabilizes further and there's a clear use case for "world exists beyond the agent" cues; only ship (5) if motion legibility complaints emerge that (5) would address. Neither is on the critical path.

**Bug surfaced and fixed during the same session.** Live observation showed Jebrim's intent bubble vanished after a `move` event despite his session actively running tools. Cause: visualizer clears player intents on building change, and `action` events don't repop bubbles. Fix: hook now re-emits the actor's intent file content as an `intent` event right after a move (sub-agents skip — no intent file). See [[S024]] for details and the four-incident pattern context.
