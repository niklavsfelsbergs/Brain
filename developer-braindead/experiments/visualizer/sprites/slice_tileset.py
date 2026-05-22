"""Slice the v3 environment tileset into individual transparent PNGs.

Different shape from `slice.py` — the tileset isn't a uniform grid, so we
detect rows by horizontal projection, then columns within each row, and save
each cell with positional names (tile_r{row}_c{col}.png) plus a friendly
alias from the NAMES_BY_POS table below.
"""

from __future__ import annotations
from pathlib import Path
from PIL import Image
import numpy as np
from collections import deque

HERE = Path(__file__).parent
SRC = HERE / "_source" / "tileset-2026-05-22.png"
OUT = HERE / "tiles"

# (row, col) -> friendly name. Anything missing gets only the positional name.
NAMES_BY_POS = {
    # Row 0 — 9 trees
    (0, 0): "tree-leafy-1",
    (0, 1): "tree-leafy-2",
    (0, 2): "tree-leafy-3",
    (0, 3): "tree-leafy-4",
    (0, 4): "tree-pine-1",
    (0, 5): "tree-pine-2",
    (0, 6): "tree-pine-3",
    (0, 7): "tree-dead",
    (0, 8): "tree-autumn",
    # Row 1 — 13 small flora / decor
    (1, 0): "bush-1",
    (1, 1): "bush-2",
    (1, 2): "bush-3",
    (1, 3): "grass-tall",
    (1, 4): "bush-low",
    (1, 5): "sapling",
    (1, 6): "flower-cluster",
    (1, 7): "stump",
    (1, 8): "log",
    (1, 9): "rock-large",
    (1, 10): "rock-medium",
    (1, 11): "rock-pebble-cluster",
    (1, 12): "dead-bush",
    # Row 2 — 7 ground tiles (iso diamonds)
    (2, 0): "ground-grass",
    (2, 1): "ground-meadow",
    (2, 2): "ground-wheat",
    (2, 3): "ground-earth",
    (2, 4): "ground-cobble",
    (2, 5): "ground-stone",
    (2, 6): "ground-compass",
    # Row 3 — 6 water tiles
    (3, 0): "water-pond-1",
    (3, 1): "water-bend",
    (3, 2): "water-lily",
    (3, 3): "water-pond-large",
    (3, 4): "water-fall",
    (3, 5): "water-stream",
    # Row 4 — 8 terrain shapes
    (4, 0): "terrain-corner-1",
    (4, 1): "terrain-corner-2",
    (4, 2): "terrain-cross",
    (4, 3): "terrain-plus",
    (4, 4): "terrain-edge",
    (4, 5): "plaza-round",
    (4, 6): "path-stone",
    (4, 7): "stairs-stone",
    # Row 5 — 12 props
    (5, 0): "prop-signpost",
    (5, 1): "prop-lantern",
    (5, 2): "prop-bench",
    (5, 3): "prop-crate",
    (5, 4): "prop-barrel",
    (5, 5): "prop-cart",
    (5, 6): "prop-fence-panel",
    (5, 7): "prop-fence-gate",
    (5, 8): "prop-stone-wall",
    (5, 9): "prop-stone-wall-2",
    (5, 10): "prop-banner-red",
    (5, 11): "prop-banner-gold",
    # Row 6 — 10 animals
    (6, 0): "horse-brown",
    (6, 1): "horse-grey",
    (6, 2): "horse-paint",
    (6, 3): "horse-black",
    (6, 4): "horse-bay",
    (6, 5): "dog-1",
    (6, 6): "dog-2",
    (6, 7): "dog-3",
    (6, 8): "dog-4",
    (6, 9): "dog-5",
}

# Hardcoded row Y-ranges from profile.
ROW_Y = [(48, 209), (261, 331), (375, 490), (514, 669), (694, 825), (864, 956), (1007, 1111)]

BG_TOL = 15
MIN_COL_W = 25


def flood_fill_bg(arr: np.ndarray, tol: int) -> np.ndarray:
    h, w, _ = arr.shape
    mask = np.zeros((h, w), dtype=bool)
    seeds = [(0, 0), (0, w - 1), (h - 1, 0), (h - 1, w - 1)]
    seed_colors = [arr[y, x].astype(np.int16) for (y, x) in seeds]
    q: deque[tuple[int, int]] = deque()
    for (y, x), c in zip(seeds, seed_colors):
        mask[y, x] = True
        q.append((y, x))
    while q:
        y, x = q.popleft()
        for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w and not mask[ny, nx]:
                p = arr[ny, nx].astype(np.int16)
                if any(np.max(np.abs(p - c)) <= tol for c in seed_colors):
                    mask[ny, nx] = True
                    q.append((ny, nx))
    return mask


def find_cols(prof: np.ndarray, min_w: int) -> list[tuple[int, int]]:
    in_band = False
    bands = []
    start = 0
    for x, v in enumerate(prof):
        if v > 5 and not in_band:
            in_band = True
            start = x
        elif v <= 5 and in_band:
            in_band = False
            if x - start >= min_w:
                bands.append((start, x))
    if in_band and len(prof) - start >= min_w:
        bands.append((start, len(prof)))
    return bands


def main() -> None:
    OUT.mkdir(exist_ok=True)
    print(f"loading {SRC}")
    im = Image.open(SRC).convert("RGB")
    arr = np.array(im)
    bg = flood_fill_bg(arr, BG_TOL)
    fg = ~bg
    alpha = (fg.astype(np.uint8)) * 255
    rgba = np.dstack([arr, alpha])

    written = 0
    for row_idx, (y0, y1) in enumerate(ROW_Y):
        cols = find_cols(fg[y0:y1].sum(axis=0), MIN_COL_W)
        print(f"row {row_idx} y={y0}-{y1}: {len(cols)} cols")
        for col_idx, (x0, x1) in enumerate(cols):
            cell = rgba[y0:y1, x0:x1]
            cell_alpha = cell[:, :, 3] > 0
            if not cell_alpha.any():
                continue
            ys, xs = np.where(cell_alpha)
            top, bot = ys.min(), ys.max() + 1
            left, right = xs.min(), xs.max() + 1
            tight = cell[top:bot, left:right]

            name = NAMES_BY_POS.get((row_idx, col_idx), f"tile_r{row_idx}_c{col_idx}")
            path = OUT / f"{name}.png"
            Image.fromarray(tight, mode="RGBA").save(path)
            written += 1
            print(f"    {path.name}  ({tight.shape[1]}x{tight.shape[0]})")
    print(f"done — wrote {written} tiles to {OUT}")


if __name__ == "__main__":
    main()
