# S051 — 2026-05-23 — Visualizer tree + bubble scale pass

- Trees scaled 3× in the four symbol defs in [[experiments/visualizer/index.html]] (~line 1042–1045): `tree-leafy` 36→108, `tree-pine` 24×38→72×114, `tree-small` 18→54. Anchors shifted so trunks stay rooted at the same ground point; `placeTree` scatter picks up new size automatically since the geometry lives in the symbol, not the `<use>`.
- Speech bubbles scaled 1.25× in `renderIntent` (~3577) and the mirror in `bubbleDims` (~3352): MAX_W 600→750, min 108→135, formula coeffs 12.4/28→15.5/35, lineH 26→32.5, padY 8→10, font-size 22→27.5, outer stroke 2.4→3, inner inset 2.4→3 (w-4.8→w-6), inner stroke 0.8→1, rx/ry 10→12.5 and 7→8.75, baseline 20→25. Wrap char-count cap (50) unchanged — that's a text constraint, not a pixel.
- Both functions carry inline `S049: further 1.25× pass` comment noting the layered scaling history ([[S029_parallel_braindead_and_comms_channel|S029]] was the 2× pass; this is on top).
- No OPEN posted (mid-conversation entry via "lets develop gielinor"). One file touched; pure visual polish, no architectural surface.
- Heads-up carried: `placeTree`'s `clearOfBuildings(160)` / `clearOfPaths(45)` radii were tuned for the small trees and may now read crowded near buildings/paths. Bump if the next live view shows overlap.

**Cascade.** `developer-braindead/experiments/visualizer/index.html` (one file, two surfaces).
**Main-brain changes.** none.
