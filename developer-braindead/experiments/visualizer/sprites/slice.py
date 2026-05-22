"""Slice the ChatGPT sprite sheet into 20 transparent PNGs.

Run from this folder: `python slice.py`. Source at `_source/sheet-2026-05-22.png`,
outputs land alongside this script.

Approach: flood-fill background from corners to mask it (safer than color-key —
internal grey-toned sprite pixels stay opaque). Project alpha onto axes to find
row bands and per-row column bands. Tight-crop each cell, drop the label band
at the bottom, save as PNG with alpha.
"""

from __future__ import annotations
from pathlib import Path
from PIL import Image
import numpy as np
from collections import deque

HERE = Path(__file__).parent
SRC = HERE / "_source" / "sheet-2026-05-22-v4.png"

# v4 layout — 6 rows but the last two run into each other in the profile.
# Row 1: 5 actors, Row 2: 3 sub-agents + 2 trees, Row 3: bush+flower+rock+
# ground+path, Row 4: 5 buildings, Row 5: 5 buildings, Row 6: iceberg + tree.
NAMES = [
    ["jebrim", "zezima", "wisp", "braindead", "guthix"],
    ["dwarf", "gnome", "penguin", "tree-leafy", "tree-pine"],
    ["bush", "flower", "rock", "ground-tile", "path-tile"],
    ["inbox-square", "meta-town-hall", "lorebook-library", "bank", "examine-hall"],
    ["quest-hall", "spellbook-tower", "keepsake-vault", "inn", "braindead-workshop"],
    ["iceberg", "tree-small"],
]

# Color distance tolerance for "this pixel is background" during flood-fill.
# Bumped 22→60 to eat anti-aliased halos around sprites (mid-grey pixels at
# the boundary between dark outline and white bg). Risk: light interior
# highlights might get classified as bg, but the flood-fill is connected so
# only halo pixels reachable from a corner get caught.
BG_TOL = 60
# Row bands hardcoded from inspection of the 2026-05-22 sheet (1536×1024).
# Auto-detect doesn't work cleanly here: label text bridges rows 2-4 (forcing
# a high threshold), but the lone tree on row 5 sits below any high threshold.
# Bands are inclusive y-ranges spanning art + label; LABEL_TRIM_FRAC cuts the
# label off afterward.
ROW_Y_RANGES = [
    (46, 243),   # v4 row 1: 5 actors
    (266, 450),  # v4 row 2: 3 sub-agents + 2 trees
    (476, 607),  # v4 row 3: bush, flower, rock, ground tile, path tile
    (623, 819),  # v4 row 4: 5 buildings A
    (823, 1010), # v4 row 5: 5 buildings B
    (1015, 1103),# v4 row 6: iceberg + small tree
]
COL_GAP_FRAC = 0.04
# Min sprite width. Filters narrow noise (e.g., a building spire poking into
# the next row's y-range). Real sprites in this sheet are all ≥120px wide.
MIN_COL_W = 80
# After cropping a cell to its tight bbox, trim this fraction off the bottom
# to drop the small label text under each sprite.
LABEL_TRIM_FRAC = 0.16


def flood_fill_bg(arr: np.ndarray, tol: int) -> np.ndarray:
    """Flood-fill from all four corners, marking reachable bg-similar pixels."""
    h, w, _ = arr.shape
    mask = np.zeros((h, w), dtype=bool)  # True = background
    seeds = [(0, 0), (0, w - 1), (h - 1, 0), (h - 1, w - 1)]
    seed_colors = [arr[y, x].astype(np.int16) for (y, x) in seeds]

    q: deque[tuple[int, int]] = deque()
    for (y, x), c in zip(seeds, seed_colors):
        if not mask[y, x]:
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


def dilate_bg(bg: np.ndarray, n: int) -> np.ndarray:
    """Expand the bg mask outward by n pixels in 4-connectivity."""
    h, w = bg.shape
    out = bg.copy()
    for _ in range(n):
        # Shift in 4 directions and OR in
        nxt = out.copy()
        nxt[1:, :] |= out[:-1, :]
        nxt[:-1, :] |= out[1:, :]
        nxt[:, 1:] |= out[:, :-1]
        nxt[:, :-1] |= out[:, 1:]
        out = nxt
    return out


def edge_alpha(arr: np.ndarray, bg: np.ndarray, dilate: int = 2, halo: int = 3, soft_tol: int = 120) -> np.ndarray:
    """Compute alpha mask that eats the halo around sprites.

    Step 1: dilate the bg mask outward by `dilate` pixels — eats the very edge
            (the brightest halo pixels) unconditionally.
    Step 2: for the pixels just inside the dilated boundary, fade alpha based
            on color-distance to the nearest seed color.
    """
    h, w, _ = arr.shape
    seed_colors = np.array([
        arr[0, 0], arr[0, w - 1], arr[h - 1, 0], arr[h - 1, w - 1]
    ], dtype=np.int16)
    # Dilate bg to consume halo pixels close to the original bg.
    bg_dilated = dilate_bg(bg, dilate)
    fg = ~bg_dilated

    # Min color-distance to any seed color (for the soft-edge band).
    arr_i = arr.astype(np.int16)
    dists = np.full((h, w), 1e9, dtype=np.float32)
    for c in seed_colors:
        d = np.max(np.abs(arr_i - c), axis=2).astype(np.float32)
        dists = np.minimum(dists, d)

    # `near_dilated_bg` = pixels within `halo` of the dilated bg (these get soft alpha)
    near_bg = np.zeros((h, w), dtype=bool)
    for dy in range(-halo, halo + 1):
        for dx in range(-halo, halo + 1):
            if dy == 0 and dx == 0:
                continue
            ys = slice(max(0, dy), min(h, h + dy))
            xs = slice(max(0, dx), min(w, w + dx))
            ys2 = slice(max(0, -dy), min(h, h - dy))
            xs2 = slice(max(0, -dx), min(w, w - dx))
            near_bg[ys2, xs2] |= bg_dilated[ys, xs]
    edge_mask = fg & near_bg

    soft = np.clip(dists / soft_tol, 0.0, 1.0)
    alpha = (fg.astype(np.uint8)) * 255
    soft_alpha = (soft * 255).astype(np.uint8)
    alpha = np.where(edge_mask, np.minimum(alpha, soft_alpha), alpha)
    return alpha


def find_bands(profile: np.ndarray, gap_frac: float, min_size: int) -> list[tuple[int, int]]:
    """Given a 1D opacity-density profile, return [(start, end), ...] bands."""
    threshold = profile.max() * gap_frac
    in_band = False
    bands: list[tuple[int, int]] = []
    start = 0
    for i, v in enumerate(profile):
        if v > threshold and not in_band:
            in_band = True
            start = i
        elif v <= threshold and in_band:
            in_band = False
            if i - start >= min_size:
                bands.append((start, i))
    if in_band and len(profile) - start >= min_size:
        bands.append((start, len(profile)))
    return bands


def main() -> None:
    print(f"loading {SRC}")
    im = Image.open(SRC).convert("RGB")
    arr = np.array(im)
    h, w, _ = arr.shape

    print("flood-filling background from corners…")
    bg = flood_fill_bg(arr, BG_TOL)
    fg = ~bg
    print("computing soft edge alpha…")
    alpha = edge_alpha(arr, bg, dilate=3, halo=3, soft_tol=140)

    # Build RGBA image
    rgba = np.dstack([arr, alpha])

    row_bands = ROW_Y_RANGES
    print(f"using {len(row_bands)} hardcoded row bands")
    assert len(row_bands) == len(NAMES)

    out_count = 0
    for row_idx, (y0, y1) in enumerate(row_bands):
        row_names = NAMES[row_idx]
        row_fg = fg[y0:y1]
        col_profile = row_fg.sum(axis=0)
        col_bands = find_bands(col_profile, COL_GAP_FRAC, MIN_COL_W)
        print(f"  row {row_idx}: {len(col_bands)} columns")
        assert len(col_bands) == len(row_names), (
            f"row {row_idx}: expected {len(row_names)} cols, got {len(col_bands)}"
        )
        for col_idx, (x0, x1) in enumerate(col_bands):
            name = row_names[col_idx]
            cell = rgba[y0:y1, x0:x1]
            cell_alpha = cell[:, :, 3] > 0
            if not cell_alpha.any():
                print(f"    SKIP {name}: empty cell")
                continue
            ys, xs = np.where(cell_alpha)
            top, bot = ys.min(), ys.max() + 1
            left, right = xs.min(), xs.max() + 1
            tight = cell[top:bot, left:right]

            out_path = HERE / f"{name}.png"
            Image.fromarray(tight, mode="RGBA").save(out_path)
            print(f"    wrote {out_path.name}  ({tight.shape[1]}x{tight.shape[0]})")
            out_count += 1

    print(f"done — wrote {out_count} sprites")


if __name__ == "__main__":
    main()
