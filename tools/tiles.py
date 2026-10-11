"""Link tiles of the profile README: a 44 px rounded square (the minimum touch target) with
a Tabler icon (3.24.0, MIT), in GitHub's subtle surface and muted text colors per theme.
The tiles float left after the staircase card, which takes 86% of the README column:
- desktop: one tile fits beside the card per line, so they stack; the first tile's desktop
  file carries empty space above it, so the stack sits at the card's vertical middle;
- phone: no tile fits beside the card, so they line up under it; the first tile's phone
  file carries empty space on its left, so the row sits at the column's middle.
Each file has 12 units under the tile, the gap between stacked tiles.
Usage: python3 tools/tiles.py tools/icons assets  (prints the names)"""
import hashlib, re, sys
from pathlib import Path

SRC, OUT = Path(sys.argv[1]), Path(sys.argv[2])
T, ICON, GAP = 44, 22, 12
THEMES = {
    "light": dict(bg="#f6f8fa", border="#d1d9e0", icon="#59636e"),
    "dark": dict(bg="#151b23", border="#3d444d", icon="#9198a1"),
}
# README column on a desktop about 830 px: card 86% of it at 900 x 592 is 470 px tall, and the
# stack 3 x 44 + 2 x 12 = 156 px: (470 - 156) / 2 = 157. On a phone the column is about
# 356 px and the row 3 x 44 + 2 x 20 (GitHub's padding beside a floated image) = 172 px.
LIFT, INDENT = 157, 92
TILES = [("portfolio", "world"), ("email", "mail"), ("linkedin", "brand-linkedin")]


def tile(src, c, delay, left=0, top=0):
    paths = re.findall(r'<path d="([^"]+)"', (SRC / f"{src}.svg").read_text())
    body = "".join(f'<path pathLength="1" d="{d}"/>' for d in paths)
    w, h = left + T, top + T + GAP
    k, o = ICON / 24, (T - ICON) / 2
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
            f'<style>.t{{opacity:0;transform-box:fill-box;transform-origin:center;animation:t .5s cubic-bezier(.34,1.4,.64,1) {delay:.2f}s forwards}}'
            f'.i path{{fill:none;stroke:{c["icon"]};stroke-width:1.7;stroke-linecap:round;stroke-linejoin:round;stroke-dasharray:1;stroke-dashoffset:1;'
            f'animation:d .9s cubic-bezier(.16,1,.3,1) {delay + .15:.2f}s forwards}}'
            f'@keyframes t{{from{{opacity:0;transform:scale(.7)}}to{{opacity:1;transform:none}}}}@keyframes d{{to{{stroke-dashoffset:0}}}}</style>'
            f'<g transform="translate({left} {top})"><rect class="t" x=".5" y=".5" width="{T - 1}" height="{T - 1}" rx="10" fill="{c["bg"]}" stroke="{c["border"]}"/>'
            f'<g class="i" transform="translate({o} {o}) scale({k:.4f})">{body}</g></g></svg>\n')


for f in OUT.glob("tile-*.svg"):
    f.unlink()
for i, (role, src) in enumerate(TILES):
    delay = 2.0 + .12 * i
    variants = [("", 0, 0)] if i else [("desktop-", 0, LIFT), ("phone-", INDENT, 0)]
    for form, left, top in variants:
        for theme, c in THEMES.items():
            svg = tile(src, c, delay, left, top)
            name = f"tile-{role}-{form}{theme}-{hashlib.sha256(svg.encode()).hexdigest()[:8]}.svg"
            (OUT / name).write_text(svg)
            print(name)
