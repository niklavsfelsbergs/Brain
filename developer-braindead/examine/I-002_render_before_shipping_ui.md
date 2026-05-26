# I-002 — When generating UI in one shot, render it in your head before shipping

**Date.** 2026-05-21. **Session ref.** [[S008_iso_visualizer_v0]].

**Ruling.** For visual artifacts — SVG, CSS, layout, anything the user *sees* — don't ship until I've mentally rendered what will appear on screen. Code compiling isn't enough. "The transform is set correctly" isn't enough. The discipline is to predict the actual visual outcome before the user has to look at it for me.

**Context.** Six iteration cycles in [[S008_iso_visualizer_v0]] on the iso visualizer, each one a visible bug Niklavs caught from a single screenshot:

- SVG `<symbol>` without explicit `width`/`height` defaults to 100% of viewport — trees and players rendered enormous. I knew the symbol→use pattern but never thought about what size the result would be.
- Grass `ISO.offY=80` put the diamond at the top of the screen instead of centered on buildings. The number 80 came from "small offset from top" without checking *what* it offset.
- Hall of Mirrors dome `rx=34, ry=16` was double the wall-base diameter. Building looked like a UFO. I wrote the numbers without picturing them on the building.
- Trees positioned in screen coords from the old top-down map left them outside the new iso diamond, floating in void. The arrays were carried over without re-projecting.
- Tree sway animation pivoted around SVG viewport origin (missing `transform-box: fill-box`) — trees translated across the map instead of swaying. The CSS was *valid*; the result wasn't.
- Grass diamond mask clipped at viewport corners leaving black wedges.

Each one was visible immediately on first render. None required deep debugging. Niklavs caught all six.

**Why.** I default to "the code is correct" as my completion signal. For UI that's the wrong signal — the only completion signal is "the screen looks right." When I can't run the artifact and look at it, the substitute is mentally rendering the SVG/CSS — playing the result back to myself before committing. Six visible bugs in one session is the threshold for promoting this from a one-off observation to a posture rule. The cost of running the prediction is seconds; the cost of skipping it is a round-trip with the user per bug.

**How to apply.** Before shipping any UI artifact: pick two or three key sprites/positions/animations and step through what they will look like — *not* whether the syntax is correct. Especially: anything involving SVG `<symbol>`/`<use>`, `transform-origin` on SVG, viewBox math, iso projection arithmetic, fixed positions carried across coordinate systems, animation pivots.
