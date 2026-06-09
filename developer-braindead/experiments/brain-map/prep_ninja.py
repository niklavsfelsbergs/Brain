#!/usr/bin/env python3
"""prep_ninja.py — slice the Ninja Adventure pack (CC0, pixel-boy) into the
sprites the renderer uses. Grittier/medieval, less cottagecore.

Ninja Adventure © pixel-boy — CC0 (public domain). Source: assets/ninja-src.

Buildings/props are taken from VERIFIED connected-component bounding boxes of
the village sheet (each box = one complete discrete sprite). Terrain tiles are
auto-picked by strict colour targeting. Characters sliced 16x16.
Output: sprites_ready/*.png
"""
from pathlib import Path
from PIL import Image

HERE = Path(__file__).resolve().parent
SRC = HERE / "assets" / "ninja-src" / "content"
OUT = HERE / "sprites_ready"
OUT.mkdir(exist_ok=True)
T = 16


def load(rel): return Image.open(SRC / rel).convert("RGBA")
def save(im, n): im.save(OUT / f"{n}.png"); return n
def px(im, x, y, w, h): return im.crop((x, y, x + w, y + h))            # raw-pixel crop
def cell(im, cx, cy, w=1, h=1): return im.crop((cx*T, cy*T, (cx+w)*T, (cy+h)*T))


def opacity(im):
    a = list(im.getchannel("A").getdata()); return sum(1 for v in a if v > 30)/max(1, len(a))
def mean_var(im):
    rgb = list(im.convert("RGB").getdata()); n = len(rgb)
    m = [sum(p[i] for p in rgb)/n for i in range(3)]
    v = sum((p[i]-m[i])**2 for p in rgb for i in range(3))/n
    return m, v
def best(im, x0, y0, x1, y1, score):
    bt, bs = None, -1e9
    for cy in range(y0, y1):
        for cx in range(x0, x1):
            c = cell(im, cx, cy)
            if opacity(c) < 0.97: continue
            m, v = mean_var(c); s = score(m, v)
            if s > bs: bs, bt = s, c
    return bt


def main():
    made = []
    floor = load("map/tileset_floor.png")            # 22x26 multi-biome
    cols, rows = floor.width//T, floor.height//T
    # grass: DETERMINISTIC deep-green grass tile. Picked by per-tile numeric
    # scan (flattest tiles in the green-green family, not the yellow lime at
    # 0,12). cell(15,12) = mean[115,162,53], var~87 — subtle texture, no flowers.
    # Auto-"greenest" scoring kept grabbing flowered/decorated tiles (the quilt).
    made.append(save(cell(floor, 15, 12), "grass"))
    # dirt path: brown/tan solid (r,g close & both > b), search whole sheet
    def brownscore(m, v):
        if not (m[0] > 95 and m[1] > 80 and m[2] < min(m[0], m[1]) - 18): return -1e9
        return m[0] - m[2] - abs(m[0]-m[1]) - v/90
    made.append(save(best(floor, 0, 0, cols, rows, brownscore) or cell(floor, 0, 0), "path"))
    # water: bluest solid (b clearly dominant)
    def bluescore(m, v):
        if not (m[2] > m[0] + 18 and m[2] > m[1] + 4): return -1e9
        return m[2] - (m[0]+m[1])/2 - v/120
    made.append(save(best(floor, 0, 0, cols, rows, bluescore) or cell(floor, 0, 0), "water"))
    # tufts (small grass decor, animated grass sheet = 4 frames)
    gdec = load("destroyable/grass.png")
    for i in range(min(4, gdec.width//T)):
        made.append(save(cell(gdec, i, 0), f"tuft{i}"))

    # ── buildings + props: verified connected-component bounding boxes ─────
    vil = load("map/tileset_village_abandoned.png")
    manor_im = px(vil, 193, 98, 62, 78)                    # clean timber 2-storey
    made.append(save(manor_im, "manor"))
    # hut = the SAME timber house, scaled down → a cottage. (The sheet's only
    # small standalone building was an orange market-stall that read as a cart.)
    made.append(save(manor_im.resize((46, 58), Image.NEAREST), "hut"))
    made.append(save(px(vil, 0, 49, 96, 95),   "ruin"))    # stone ruin / rock pillars
    # GREEN foliage — verified connected-component bboxes (the village sheet's
    # foliage block is the only green; the rest of the sheet is autumn-orange).
    made.append(save(px(vil, 1, 145, 62, 44),  "tree_big"))  # big green tree clump
    made.append(save(px(vil, 1, 97, 62, 39),   "tree2"))     # second tree variant
    made.append(save(px(vil, 65, 98, 30, 22),  "bush"))      # green bush (hedges)
    made.append(save(px(vil, 65, 146, 30, 22), "bush2"))     # green bush variant (gardens)

    # ── character: col0=down, col1=up, col2=side; rows 0-3 walk frames ─────
    ch = load("character/samurai_blue/sprite.png")
    for face, c in {"down": 0, "up": 1, "side": 2}.items():
        for r in range(4):
            made.append(save(cell(ch, c, r), f"char_{face}_{r}"))

    print(f"prep_ninja: wrote {len(made)} sprites to {OUT}")


if __name__ == "__main__":
    main()
