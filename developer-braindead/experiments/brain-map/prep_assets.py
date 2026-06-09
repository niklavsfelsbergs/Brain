#!/usr/bin/env python3
"""prep_assets.py — slice the Sprout Lands Basic pack into clean, ready-to-draw
PNGs for the brain-world renderer, and emit a contact sheet to eyeball them.

Sprout Lands © Cup Nooble (Basic pack) — non-commercial, credit required.
See assets/.../read_me.txt. We use it inside this non-commercial brain tool and
credit in CREDITS; we do not redistribute the pack itself.

Source tiles are 16x16; character frames are 48x48 (4 walk frames x 4 facings).
Output: sprites_ready/*.png + sprites_ready/_contact.png
"""
from pathlib import Path
from PIL import Image
import colorsys

HERE = Path(__file__).resolve().parent
PACK = HERE / "assets" / "Sprout Lands - Sprites - Basic pack"
OUT = HERE / "sprites_ready"
OUT.mkdir(exist_ok=True)
T = 16


def load(rel):
    return Image.open(PACK / rel).convert("RGBA")


def crop_cells(img, cx, cy, w, h):
    return img.crop((cx * T, cy * T, (cx + w) * T, (cy + h) * T))


def save(img, name):
    img.save(OUT / f"{name}.png")
    return name


def opacity(img):
    a = img.getchannel("A")
    px = list(a.getdata())
    return sum(1 for v in px if v > 20) / max(1, len(px))


def variance(img):
    rgb = img.convert("RGB").getdata()
    px = list(rgb)
    n = len(px)
    means = [sum(p[c] for p in px) / n for c in range(3)]
    return sum((p[c] - means[c]) ** 2 for p in px for c in range(3)) / n


def tint_hue(img, hue, sat=0.45):
    """Recolor non-transparent pixels to a target hue, MUTED (capped low
    saturation) so roofs read as weathered/earthy rather than candy-bright."""
    img = img.copy()
    px = img.load()
    W, H = img.size
    for y in range(H):
        for x in range(W):
            r, g, b, a = px[x, y]
            if a < 20:
                continue
            _, _, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
            nr, ng, nb = colorsys.hsv_to_rgb(hue, sat, v * 0.92)
            px[x, y] = (int(nr * 255), int(ng * 255), int(nb * 255), a)
    return img


def auto_tile(img, want_green=True):
    """Pick the most solid/uniform 16x16 cell (for a base ground/path fill)."""
    W, H = img.size
    best, best_score = None, -1e9
    for cy in range(H // T):
        for cx in range(W // T):
            c = crop_cells(img, cx, cy, 1, 1)
            op = opacity(c)
            rgb = c.convert("RGB").getdata()
            n = len(rgb)
            mean = [sum(p[i] for p in rgb) / n for i in range(3)]
            greenish = mean[1] - (mean[0] + mean[2]) / 2 if want_green else 0
            # opacity dominates (we want a solid fill tile), then hue/uniformity
            score = op * 100 + greenish - variance(c) / 50
            if score > best_score:
                best_score, best = score, c
    return best


def main():
    made = []

    # ── terrain ──────────────────────────────────────────────────────────
    grass = auto_tile(load("Tilesets/Grass.png"), want_green=True)
    made.append(save(grass, "grass"))
    made.append(save(auto_tile(load("Tilesets/Tilled_Dirt.png"), want_green=False), "path"))
    water = load("Tilesets/Water.png")             # 4 frames horizontally
    made.append(save(crop_cells(water, 0, 0, 1, 1), "water"))

    # ── building: ASSEMBLE a cottage from the roof + walls autotile sets ────
    # walls set (5x3): cols 0/1/2 = left-edge / fill / right-edge; (3,2)=door.
    # roof set (7x5):  cols 0/1/2 = left / fill / right; rows 0,1,2 = ridge /
    # shingle / gutter. Extend width by repeating the fill column.
    roof_ts = load("Tilesets/Wooden_House_Roof_Tilset.png")
    wall_ts = load("Tilesets/Wooden_House_Walls_Tilset.png")

    def edge_col(cx, wt):
        return 0 if cx == 0 else (2 if cx == wt - 1 else 1)

    def compose_house(wt=5, roof_rows=(0, 1, 2), wall_rows=(1, 2)):
        Wpx, Hpx = wt * T, (len(roof_rows) + len(wall_rows)) * T
        img = Image.new("RGBA", (Wpx, Hpx), (0, 0, 0, 0))
        for ri, rr in enumerate(roof_rows):
            for cx in range(wt):
                img.alpha_composite(crop_cells(roof_ts, edge_col(cx, wt), rr, 1, 1), (cx * T, ri * T))
        for wi, wr in enumerate(wall_rows):
            for cx in range(wt):
                y = (len(roof_rows) + wi) * T
                img.alpha_composite(crop_cells(wall_ts, edge_col(cx, wt), wr, 1, 1), (cx * T, y))
        img.alpha_composite(crop_cells(wall_ts, 3, 2, 1, 1), ((wt // 2) * T, Hpx - T))  # door
        return img

    house = compose_house(5)                       # 80x80 — landmark / civic hall
    cottage = compose_house(3, roof_rows=(0, 1), wall_rows=(1, 2))  # 48x64 — a layer
    made.append(save(house, "house"))
    made.append(save(cottage, "cottage"))
    # muted region roof tints (earthy, not candy). hue, saturation.
    REGION = {"civic": (0.10, 0.42), "jebrim": (0.60, 0.40), "zezima": (0.93, 0.40),
              "guthix": (0.34, 0.40), "dev": (0.07, 0.45)}
    for name, (hue, sat) in REGION.items():
        h = house.copy()
        h.paste(tint_hue(h.crop((0, 0, h.width, 3 * T)), hue, sat), (0, 0))
        made.append(save(h, f"house_{name}"))
        c = cottage.copy()
        c.paste(tint_hue(c.crop((0, 0, c.width, 2 * T)), hue, sat), (0, 0))
        made.append(save(c, f"cottage_{name}"))

    # ── props (Basic_Grass_Biom_things.png 9x5) ───────────────────────────
    biom = load("Objects/Basic_Grass_Biom_things.png")
    made.append(save(crop_cells(biom, 1, 0, 2, 2), "tree_big"))     # 32x32
    made.append(save(crop_cells(biom, 0, 0, 1, 2), "tree_small"))   # 16x32
    made.append(save(crop_cells(biom, 3, 0, 2, 2), "tree_fruit"))   # 32x32
    made.append(save(crop_cells(biom, 1, 3, 1, 1), "bush"))
    made.append(save(crop_cells(biom, 0, 3, 1, 1), "bush_berry"))
    made.append(save(crop_cells(biom, 8, 1, 1, 1), "rock"))
    made.append(save(crop_cells(biom, 7, 1, 1, 1), "rock_small"))
    made.append(save(crop_cells(biom, 7, 3, 1, 1), "flower"))
    made.append(save(crop_cells(biom, 8, 2, 1, 2), "sunflower"))    # 16x32
    made.append(save(crop_cells(biom, 5, 0, 1, 1), "mushroom"))
    made.append(save(crop_cells(biom, 5, 2, 1, 1), "log"))
    made.append(save(crop_cells(biom, 3, 2, 1, 1), "stump"))

    # ── ground detail (kills the flat-fill look) ──────────────────────────
    g = load("Tilesets/Grass.png")
    for i, (cx, cy) in enumerate([(0, 5), (1, 5), (3, 5), (2, 6), (4, 6)]):
        made.append(save(crop_cells(g, cx, cy, 1, 1), f"grass_v{i}"))   # full-tile variants
    for i, (cx, cy) in enumerate([(6, 5), (7, 5), (8, 5), (9, 5)]):
        made.append(save(crop_cells(g, cx, cy, 1, 1), f"tuft{i}"))      # transparent overlays
    made.append(save(crop_cells(roof_ts, 4, 0, 1, 1), "chimney"))

    # ── characters: 48x48 frames, rows = down/up/side, cols = 4 walk frames ─
    chars = load("Characters/Basic Charakter Spritesheet.png")
    F = 48
    facings = {"down": 0, "up": 1, "side": 2}
    for fname, row in facings.items():
        for col in range(4):
            fr = chars.crop((col * F, row * F, col * F + F, row * F + F))
            made.append(save(fr, f"char_{fname}_{col}"))

    # ── contact sheet ──────────────────────────────────────────────────────
    SCALE, PAD, COLS = 4, 10, 8
    cells = [(n, Image.open(OUT / f"{n}.png")) for n in made]
    cw = max(im.width for _, im in cells) * SCALE + PAD * 2
    ch = max(im.height for _, im in cells) * SCALE + PAD * 2 + 14
    rows = (len(cells) + COLS - 1) // COLS
    sheet = Image.new("RGB", (cw * COLS, ch * rows), (54, 74, 50))
    from PIL import ImageDraw
    d = ImageDraw.Draw(sheet)
    for i, (n, im) in enumerate(cells):
        gx, gy = (i % COLS) * cw, (i // COLS) * ch
        big = im.resize((im.width * SCALE, im.height * SCALE), Image.NEAREST)
        sheet.paste(big, (gx + PAD, gy + PAD + 14), big)
        d.text((gx + 3, gy + 2), n, fill=(255, 230, 150))
    sheet.save(OUT / "_contact.png")
    print(f"prep_assets: wrote {len(made)} sprites to {OUT}")
    print(f"prep_assets: contact sheet -> {OUT / '_contact.png'}")


if __name__ == "__main__":
    main()
