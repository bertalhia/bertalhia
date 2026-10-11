"""Link icons of the profile README: a 32 px button with a thin frame and a 16 px Tabler
icon (3.24.0, MIT). One color set reads on both GitHub themes (a mid gray, a translucent
frame), so no file is picked by color scheme: GitHub turns a dark-scheme media query into
one that always matches, which would also drop a width condition beside it. That keeps a
plain width query free for the first icon:
- desktop (its default file): the staircase card floats right at 87% of the README column,
  one icon fits left of it per line, so the icons stack there; the first one's file has
  empty space above it, which puts the stack at the card's vertical middle;
- phone (max-width: 600px): no icon fits beside the card, so they line up under it; the
  first one's file has empty space on its left, which centers the row.
Each file has 10 units under the icon: the gap between stacked icons.
Usage: python3 tools/tiles.py tools/icons assets  (prints the names)"""
import hashlib, re, sys
from pathlib import Path

SRC, OUT = Path(sys.argv[1]), Path(sys.argv[2])
T, ICON, GAP = 32, 16, 10
COLOR, FRAME = "#8b949e", "rgba(139,148,158,.45)"  # 3.3:1 on white, 6.3:1 on #0d1117
TILES = [("portfolio", "world"), ("email", "mail"), ("linkedin", "brand-linkedin")]
# Desktop: GitHub's README column is 846 px, so the card is 0.87 x 846 x 490 / 900 = 401 px
# tall and the stack 3 x 32 + 2 x 10 = 116 px: (401 - 116) / 2 = 142 above the first icon.
# Phone: a 390 px screen leaves a 358 px column and the row is 3 x 32 + 2 x 20 (GitHub's
# padding beside a floated image) = 136 px: (358 - 136) / 2 = 111 left of the first icon.
LIFT, INDENT = 142, 111


def icon(src, delay, left=0, top=0):
    paths = re.findall(r'<path d="([^"]+)"', (SRC / f"{src}.svg").read_text())
    body = "".join(f'<path pathLength="1" d="{d}"/>' for d in paths)
    w, h = left + T, top + T + GAP
    k, o = ICON / 24, (T - ICON) / 2
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
            f'<style>.t{{opacity:0;animation:t .5s ease-out {delay:.2f}s forwards}}'
            f'.i path{{fill:none;stroke:{COLOR};stroke-width:1.75;stroke-linecap:round;stroke-linejoin:round;stroke-dasharray:1;stroke-dashoffset:1;'
            f'animation:d .9s cubic-bezier(.16,1,.3,1) {delay + .1:.2f}s forwards}}'
            f'@keyframes t{{to{{opacity:1}}}}@keyframes d{{to{{stroke-dashoffset:0}}}}</style>'
            f'<g transform="translate({left} {top})"><rect class="t" x=".5" y=".5" width="{T - 1}" height="{T - 1}" rx="8" fill="none" stroke="{FRAME}"/>'
            f'<g class="i" transform="translate({o} {o}) scale({k:.4f})">{body}</g></g></svg>\n')


for f in list(OUT.glob("tile-*.svg")) + list(OUT.glob("spacer-*.svg")) + list(OUT.glob("link-*.svg")):
    f.unlink()
for i, (role, src) in enumerate(TILES):
    variants = [("", 0, 0)] if i else [("desktop-", 0, LIFT), ("phone-", INDENT, 0)]
    for form, left, top in variants:
        svg = icon(src, 2.0 + .12 * i, left, top)
        name = f"link-{role}-{form}{hashlib.sha256(svg.encode()).hexdigest()[:8]}.svg"
        (OUT / name).write_text(svg)
        print(name)
