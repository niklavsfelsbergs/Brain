# brain-map — top-down world visualizer (prototype, PARKED)

A 2D top-down (Stardew-style) render of the brain's structure: each player gets a
**cul-de-sac** (a hedged plot with a big **manor** = their home + small **cottages**
= their layers), a central **Commons** for shared layers, **Braindead's Workshop**
for the dev brain, **roads = rituals**, and **characters = sessions** that walk around.

Open `index.html` in a browser. Drag to pan, wheel to zoom, **F** to fit.

## Status

Prototype. Standalone (static art, not live-wired to the real brain yet). **Parked
2026-06-09 (S185)** — Niklavs doesn't like the current look; may return. The plumbing
works (camera, depth-sort, deterministic scatter confined to wilderness, walking chars,
dusk/glow); the open question is art direction.

## Regenerating sprites

Raw sprite packs live in `assets/` (gitignored, 14M). Re-fetch then slice:

```
python prep_ninja.py     # Ninja Adventure (CC0) -> sprites_ready/*.png  (current)
python prep_assets.py     # Sprout Lands (non-commercial) -> superseded by ninja
```

Sprite crops are pinned **deterministically** (numeric color/variance scan + connected-
component bboxes), not auto-"greenest/brownest" scoring — that silently grabbed flowered
grass and autumn-orange bushes from the multi-biome / autumn-palette source sheets.

## Art credits / license

- **Ninja Adventure** by *pixel-boy* — **CC0** (public domain). Current sprites.
- **Sprout Lands (Basic)** by *Cup Nooble* — non-commercial, credit required, no
  redistribution of the pack itself. Superseded; kept for reference only.
