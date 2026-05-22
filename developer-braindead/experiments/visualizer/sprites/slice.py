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
SRC = HERE / "_source" / "sheet-2026-05-22-v2.png"

# Reading order matches the v2 prompt: row 1 actors (5), row 2 sub-agents (3),
# row 3 buildings A (5), row 4 buildings B (5), row 5 iceberg + tree (2).
NAMES = [
    ["jebrim", "zezima", "wisp", "braindead", "guthix"],
    ["dwarf", "gnome", "penguin"],
    ["inbox-square", "meta-town-hall", "lorebook-library", "bank", "examine-hall"],
    ["quest-hall", "spellbook-tower", "keepsake-vault", "inn", "braindead-workshop"],
    ["iceberg", "tree"],
]

# Color distance tolerance for "this pixel is background" during flood-fill.
BG_TOL = 22
# Row bands hardcoded from inspection of the 2026-05-22 sheet (1536×1024).
# Auto-detect doesn't work cleanly here: label text bridges rows 2-4 (forcing
# a high threshold), but the lone tree on row 5 sits below any high threshold.
# Bands are inclusive y-ranges spanning art + label; LABEL_TRIM_FRAC cuts the
# label off afterward.
ROW_Y_RANGES = [
    (40, 225),   # row 1: 5 actors
    (280, 445),  # row 2: 3 sub-agents
    (480, 685),  # row 3: 5 buildings
    (730, 925),  # row 4: 5 buildings
    (960, 1075), # row 5: iceberg + tree
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


def edge_alpha(arr: np.ndarray, bg: np.ndarray, halo: int = 4, soft_tol: int = 60) -> np.ndarray:
    """Compute smooth alpha to remove anti-aliased halos at sprite edges.

    For pixels that are NOT in the flood-filled bg but lie within `halo` pixels
    of one, compute alpha based on color-distance to the nearest seed color.
    Pixels close to bg color get reduced alpha (eaten into transparency);
    pixels far from bg keep full alpha. This trims the white/grey halo that
    flood-fill misses on anti-aliased sprite outlines.
    """
    h, w, _ = arr.shape
    seed_colors = np.array([
        arr[0, 0], arr[0, w - 1], arr[h - 1, 0], arr[h - 1, w - 1]
    ], dtype=np.int16)
    # Distance transform (cheap): is this fg pixel adjacent to a bg pixel?
    near_bg = np.zeros((h, w), dtype=bool)
    for dy in range(-halo, halo + 1):
        for dx in range(-halo, halo + 1):
            if dy == 0 and dx == 0:
                continue
            ys = slice(max(0, dy), min(h, h + dy))
            xs = slice(max(0, dx), min(w, w + dx))
            ys2 = slice(max(0, -dy), min(h, h - dy))
            xs2 = slice(max(0, -dx), min(w, w - dx))
            near_bg[ys2, xs2] |= bg[ys, xs]
    fg = ~bg
    edge_mask = fg & near_bg
    # Min color-distance to any seed color for edge pixels.
    arr_i = arr.astype(np.int16)
    dists = np.full((h, w), 1e9, dtype=np.float32)
    for c in seed_colors:
        d = np.max(np.abs(arr_i - c), axis=2).astype(np.float32)
        dists = np.minimum(dists, d)
    # alpha = 0 at dist=0 (pure bg), 255 at dist >= soft_tol (pure fg).
    soft = np.clip(dists / soft_tol, 0.0, 1.0)
    alpha = (fg.astype(np.uint8)) * 255
    # Where edge_mask, blend in the soft alpha (only reduces alpha, never adds)
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
    alpha = edge_alpha(arr, bg, halo=4, soft_tol=60)

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
