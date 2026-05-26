# D-008 — 2026-05-21 — Visualizer v0 ships as isometric 2D SVG, not three.js 3D

**Context.** [[Q-007]] proposed a Gielinor brain visualizer with replay-from-git-log v0 as the recommended starting point. After the top-down v0 landed, Niklavs asked: "can we make the graphics look like runescape? That would mean 3d." Two paths existed: real 3D via three.js, or fake 3D via handcrafted isometric SVG (the OSRS / Tibia / Ultima Online aesthetic).

**Decision.** Ship the v0 as **isometric 2D SVG, single file, no dependencies**. Reuse the existing engine (event timeline, applyEvent dispatch, CSS-transition movement). Redraw the sprites in iso. No three.js, no canvas, no game engine.

**Alternatives considered.**

- **three.js with low-poly modelled buildings.** A weekend of asset work to look good. A one-shot attempt produces flat-grey boxes on a green plane — *worse* than handcrafted top-down because the player's eye is harsher on bad 3D than on stylised 2D. RuneScape's actual look comes from textures and modelled geometry, not from "having a camera." Rejected for the one-shot timeline.
- **Keep top-down, polish it.** Rejected because Niklavs explicitly named RuneScape as the visual target, and top-down doesn't read as RuneScape — the RS player view is fixed isometric.
- **Pixel-art with a Phaser/Excalibur game engine.** Rejected: violates single-file constraint and introduces a runtime dep that the brain hasn't decided to take on.

**Consequences.**

- The engine becomes asset-agnostic — same `EVENTS` array, same `applyEvent` dispatch, same CSS transitions. The iso swap was purely visual.
- Iso projection chosen: tile size 64×32 (2:1 ratio), pyramidal hipped roofs (two visible triangular slopes), 3-layer building shadows, stone plinths at wall base.
- Buildings are programmatically generated via an `isoBuilding({cx, cy, w, d, h, r, walls, roof, details})` helper rather than hand-coded SVG per building — keeps the file under 1800 lines and makes iteration cheap.
- The natural next step (live mode — see [[Q-007]]) is a substrate change (watcher + hooks emitting events to `state.json` instead of a hardcoded array), *not* a redesign. Iso v0 was chosen with that path in mind.
- If we later go to actual 3D, this v0 still validates the aesthetic vocabulary (palette, building silhouettes, sprite vibe) without committing to the modelling work.

**Session ref.** [[S008_iso_visualizer_v0]].
