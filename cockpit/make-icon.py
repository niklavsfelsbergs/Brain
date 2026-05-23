"""Generate icon.ico — a clean-modern switchboard glyph: a dark rounded panel
with a 2x2 grid of status dots (the board's state colors). Run once:

    cockpit\\.venv\\Scripts\\python.exe -m pip install pillow
    cockpit\\.venv\\Scripts\\python.exe cockpit\\make-icon.py
"""
from pathlib import Path

from PIL import Image, ImageDraw

S = 256
img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
d = ImageDraw.Draw(img)

d.rounded_rectangle([16, 16, 240, 240], radius=46, fill=(22, 27, 34, 255), outline=(42, 50, 61, 255), width=5)

colors = [(63, 185, 80), (240, 160, 32), (74, 144, 217), (163, 113, 247)]
pts = [(x, y) for y in (98, 162) for x in (94, 162)]
for (x, y), c in zip(pts, colors):
    d.ellipse([x - 24, y - 24, x + 24, y + 24], fill=c)

out = Path(__file__).resolve().parent / "icon.ico"
img.save(out, sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
print("wrote", out)
