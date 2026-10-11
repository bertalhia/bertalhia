"""Link icons of the profile README: a 32 px button with a thin frame and a 16 px Tabler
icon (3.24.0, MIT). One color set reads on both GitHub themes (a mid gray, a translucent
frame), so each file is picked by width alone: GitHub turns a dark-scheme media query into
one that always matches, which would also drop a width condition beside it.
Two sets of the same links, each shown at one width and an empty 1 px file at the other:
- side rail (wide README columns, see tools/readme.py): the stack card floats right at 86% of the
  column and these float left, one per line beside it, so they stack; the first one's
  file has empty space above it, which puts the stack at the card's vertical middle;
- row (narrower columns): a centered paragraph under the card, so the row is centered at any width
  (the GitHub app included); each file has 10 units on each side, the gap between icons.
Every visible file has 16 units above the icon: the gap between stacked icons on a desktop
and between the card and the row on a phone.
Usage: python3 tools/tiles.py tools/icons assets  (prints the names)"""
import hashlib, re, sys
from pathlib import Path

SRC, OUT = Path(sys.argv[1]), Path(sys.argv[2])
T, ICON, GAP, SIDE = 32, 16, 16, 10
COLOR, FRAME = "#8b949e", "rgba(139,148,158,.45)"  # 3.3:1 on white, 6.3:1 on #0d1117
TILES = [("portfolio", "world"), ("email", "mail"), ("linkedin", "brand-linkedin")]
# The rail sits at the card's vertical middle: the card is 0.86 x 490 / 900 = 0.468 of the
# column tall and the rail 3 x 32 + 2 x 16 = 128 px, so the first icon's file carries
# (0.468 x column - 128) / 2 px above it. GitHub's column changes with the screen, so there
# is one such file for each of these columns, 20 apart; tools/readme.py gives each file the
# columns nearest to it, which keeps the rail within 3 px of the middle.
RAIL_COLUMNS = [*range(545, 836, 20), 846]


def lift(col):
    return round((0.86 * col * 490 / 900 - 128) / 2)


def icon(src, delay, top=GAP, side=0):
    paths = re.findall(r'<path d="([^"]+)"', (SRC / f"{src}.svg").read_text())
    body = "".join(f'<path pathLength="1" d="{d}"/>' for d in paths)
    w, h = T + 2 * side, top + T
    k, o = ICON / 24, (T - ICON) / 2
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
            f'<style>.t{{opacity:0;animation:t .5s ease-out {delay:.2f}s forwards}}'
            f'.i path{{fill:none;stroke:{COLOR};stroke-width:1.75;stroke-linecap:round;stroke-linejoin:round;stroke-dasharray:1;stroke-dashoffset:1;'
            f'animation:d .9s cubic-bezier(.16,1,.3,1) {delay + .1:.2f}s forwards}}'
            f'@keyframes t{{to{{opacity:1}}}}@keyframes d{{to{{stroke-dashoffset:0}}}}</style>'
            f'<g transform="translate({side} {top})"><rect class="t" x=".5" y=".5" width="{T - 1}" height="{T - 1}" rx="8" fill="none" stroke="{FRAME}"/>'
            f'<g class="i" transform="translate({o} {o}) scale({k:.4f})">{body}</g></g></svg>\n')


def write(prefix, svg):
    name = f"{prefix}-{hashlib.sha256(svg.encode()).hexdigest()[:8]}.svg"
    (OUT / name).write_text(svg)
    print(name)


for f in list(OUT.glob("link-*.svg")) + list(OUT.glob("blank-*.svg")):
    f.unlink()
write("blank", '<svg xmlns="http://www.w3.org/2000/svg" width="1" height="1" viewBox="0 0 1 1"/>\n')
for i, (role, src) in enumerate(TILES):
    delay = 2.0 + .12 * i
    if i == 0:
        for col in RAIL_COLUMNS:
            write(f"link-{role}-rail{col}", icon(src, delay, top=lift(col)))
    else:
        write(f"link-{role}-rail", icon(src, delay))
    write(f"link-{role}-row", icon(src, delay, side=SIDE))
