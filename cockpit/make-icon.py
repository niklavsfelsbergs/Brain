"""Generate icon.ico — the cockpit's wood/gold "SB" monogram (SB = Switchboard).

A dark wood rounded panel with a gold bevel and a bold gold "SB", matching the
cockpit's OSRS skin (web/styles.css: --bg #17120b, --panel #2a2114,
--gold #e3b73c, --gold-dk #8f6d1e, --ink #f1e7c4).

Run once after editing (writes icon.ico + a preview PNG next to this file):

    cockpit\\.venv\\Scripts\\python.exe -m pip install pillow
    cockpit\\.venv\\Scripts\\python.exe cockpit\\make-icon.py
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# --- cockpit palette (web/styles.css :root) ---
BG       = (23, 18, 11, 255)    # --bg   #17120b
PANEL    = (42, 33, 20, 255)    # --panel #2a2114
GOLD     = (227, 183, 60, 255)  # --gold  #e3b73c
GOLD_DK  = (143, 109, 30, 255)  # --gold-dk #8f6d1e
INK      = (241, 231, 196, 255) # --ink   #f1e7c4

# Render at 4x then downsample for clean antialiased edges in the .ico.
SCALE = 4
S = 256 * SCALE

img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
d = ImageDraw.Draw(img)


def rr(box, radius, **kw):
    d.rounded_rectangle([v * SCALE for v in box], radius=radius * SCALE, **kw)


# Panel: dark-wood fill, thick gold-dk border, then a thin inner gold bevel line.
rr([16, 16, 240, 240], 48, fill=PANEL, outline=GOLD_DK, width=10)
rr([28, 28, 228, 228], 38, outline=GOLD, width=3)

# --- the "SB" monogram ---
text = "SB"
font_path = "C:/Windows/Fonts/ariblk.ttf"  # Arial Black — heavy, survives 16px
try:
    font = ImageFont.truetype(font_path, 118 * SCALE)
except OSError:
    font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 118 * SCALE)

# Center precisely off the glyph bbox (Arial Black carries asymmetric bearings).
l, t, r, b = d.textbbox((0, 0), text, font=font)
tx = (S - (r - l)) / 2 - l
ty = (S - (b - t)) / 2 - t
# A thin engrave under the gold so the letters seat into the panel (not a drop shadow).
d.text((tx, ty + 2 * SCALE), text, font=font, fill=(0, 0, 0, 90))
d.text((tx, ty), text, font=font, fill=GOLD)

out_dir = Path(__file__).resolve().parent
final = img.resize((256, 256), Image.LANCZOS)
ico_sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]

# 1) Shortcut + window icon (cockpit/icon.ico) and a preview to eyeball.
final.save(out_dir / "icon.ico", sizes=ico_sizes)
final.save(out_dir / "icon-preview.png")

# 2) Web favicons (served from web/ by backend.static_handler) — browser tab and
#    the iOS home-screen tile when the cockpit is opened on a phone.
web = out_dir / "web"
final.save(web / "favicon.ico", sizes=ico_sizes)
final.resize((180, 180), Image.LANCZOS).save(web / "apple-touch-icon.png")
print("wrote", out_dir / "icon.ico", "+ preview, web/favicon.ico, web/apple-touch-icon.png")
