"""Profile README card: the stack as isometric layers, from the database to the API to the
screens, on the platform that ships them, each layer with the logos of its technologies
standing on it. Layers drop in, logos land and then float, over a faint dot grid that
drifts, with a wave of brighter dots now and then. Two files, both read on GitHub's light and dark themes (clay-gray blocks, a gray
grid), so the README picks one by width alone: GitHub turns a dark-scheme media query
into one that always matches and drops a width condition beside it.
- desktop: a long staircase, which fits the wide README column and stays short;
- phone (max-width: 600px): the same layers stacked into a tower, so the logos stay large
  on a narrow column.
The card floats right at 87% of the README column, so the column's middle falls at
(0.5 - 0.13) / 0.87 = 42.5% of the card: the drawing is centered there.
Usage: python3 tools/stack.py tools/logos assets  (prints the names)"""
import hashlib, re, sys
from pathlib import Path

LOGOS_DIR, OUT = Path(sys.argv[1]), Path(sys.argv[2])
C, S = 0.866, 0.5
FONT = "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace"
# Clay: light, opaque grays that read on a white page and on GitHub's #0d1117 alike.
CLAY = dict(top="#eef1f3", front="#d6dce1", side="#c2cad1", edge="#a9b3bb", label="#59636e",
            mono="#1f2328", shadow="rgba(31,35,40,.2)", grid="#8b949e")
TINT = {"database": "#4169E1", "api": "#E0234E", "screens": "#2ea8c8", "platform": "#8b949e"}
LAYERS = [
    ("database", ["postgresql", "prisma", "drizzle"]),
    ("api", ["nestjs", "trpc", "typescript"]),
    # the black marks go to the front spots, over the block, never against a dark page
    ("screens", ["react", "swiftui", "next-js", "expo"]),
]
PLATFORM = ("platform", ["docker", "github-actions", "cloudflare", "aws"])
MONOCHROME = {"next-js", "expo", "prisma"}
TITLE = ("Leandro Bertalhia's stack, from the database to the screen, on the platform that ships them: "
         "PostgreSQL, Prisma and Drizzle; NestJS, tRPC and TypeScript; Next.js, React, Expo and SwiftUI; "
         "on Docker, GitHub Actions, Cloudflare and AWS.")
BOX = [1e9, 1e9, -1e9, -1e9]


def P(x, y, z):
    return ((x - y) * C, (x + y) * S - z)


def grow(sx, sy):
    BOX[0], BOX[1] = min(BOX[0], sx), min(BOX[1], sy)
    BOX[2], BOX[3] = max(BOX[2], sx), max(BOX[3], sy)


def poly(points, fill, stroke=CLAY["edge"], extra=""):
    pr = [P(*p) for p in points]
    for a, b in pr:
        grow(a, b)
    return (f'<polygon points="{" ".join(f"{a:.1f},{b:.1f}" for a, b in pr)}" fill="{fill}" stroke="{stroke}" '
            f'stroke-width="1" stroke-linejoin="round"{extra}/>')


def symbol(name):
    svg = (LOGOS_DIR / f"{name}.svg").read_text()
    box = re.search(r'viewBox="([^"]+)"', svg).group(1)
    inner = re.search(r"<svg[^>]*>(.*)</svg>", svg, re.S).group(1)
    inner = re.sub(r"<title>.*?</title>", "", inner, flags=re.S)
    inner = re.sub(r'\s(id)="[^"]*"', "", inner)
    if name in MONOCHROME:
        inner = re.sub(r'fill="#[0-9A-Fa-f]{3,6}"', f'fill="{CLAY["mono"]}"', inner)
    return f'<symbol id="{name}" viewBox="{box}">{inner}</symbol>'


def label(text, x, y_from, z):
    """Text on a face that looks right-down (x constant), running along -y."""
    sx, sy = P(x, y_from, z)
    return (f'<text transform="matrix({C} {-S} 0 1 {sx:.1f} {sy:.1f})" font-family="{MONO}" font-size="13" '
            f'letter-spacing=".6" fill="{CLAY["label"]}">{text}</text>')


def logo(name, x, y, z, size, delay, float_delay):
    sx, sy = P(x, y, z)
    grow(sx - size / 2, sy - size - 8)
    grow(sx + size / 2, sy)
    return (f'<g class="drop" style="animation-delay:{delay:.2f}s"><ellipse cx="{sx:.1f}" cy="{sy:.1f}" rx="{size * .42:.1f}" '
            f'ry="{size * .17:.1f}" fill="{CLAY["shadow"]}"/><g class="float" style="animation-delay:{float_delay:.2f}s">'
            f'<use href="#{name}" x="{sx - size / 2:.1f}" y="{sy - size - 4:.1f}" width="{size}" height="{size}"/></g></g>')


def block(x0, x1, y0, y1, z0, z1, name, top_line=True):
    """A box seen from the front: its top, its right-down face and its left-down face."""
    tint = TINT[name]
    faces = [
        poly([(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)], CLAY["top"]),
        poly([(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)], tint, "none", ' fill-opacity=".10"'),
        poly([(x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1)], CLAY["front"]),
        poly([(x0, y1, z0), (x1, y1, z0), (x1, y1, z1), (x0, y1, z1)], CLAY["side"]),
    ]
    if top_line:
        (ax, ay), (bx, by) = P(x1, y0, z1), P(x1, y1, z1)
        faces.append(f'<line x1="{ax:.1f}" y1="{ay:.1f}" x2="{bx:.1f}" y2="{by:.1f}" stroke="{tint}" stroke-width="2.5" stroke-linecap="round"/>')
    return "".join(faces)


def staircase(t0):
    """Desktop: the steps climb to the back right, the platform under them."""
    D, W, H, size = 96, 205, 30, 44
    out = []
    plate = block(-34, D + 74, -3 * W - 34, 46, -10, 0, "platform", top_line=False) + label("platform", D + 74, 46 - 14, -2.5)
    out.append(f'<g class="rise" style="animation-delay:{t0:.2f}s">{plate}</g>')
    for k in reversed(range(len(LAYERS))):
        name, logos = LAYERS[k]
        y0, y1, h = -(k + 1) * W, -k * W, (k + 1) * H
        delay = t0 + .3 + .28 * k
        out.append(f'<g class="step" style="animation-delay:{delay:.2f}s">{block(0, D, y0, y1, 0, h, name)}{label(name, D, y1 - 14, h - 20)}</g>')
        spots = {3: [(.25, .2), (.75, .5), (.25, .8)], 4: [(.25, .14), (.75, .38), (.25, .62), (.75, .86)]}[len(logos)]
        placed = sorted(((fx * D, y0 + fy * W, n) for (fx, fy), n in zip(spots, logos)), key=lambda p: P(p[0], p[1], 0)[1])
        for i, (x, y, n) in enumerate(placed):
            out.append(logo(n, x, y, h, size, delay + .35 + .09 * i, (i * .37 + k * .5) % 2.4))
    for i, (n, y) in enumerate(zip(PLATFORM[1], (-2.62 * W, -1.9 * W, -1.18 * W, -.46 * W))):
        out.append(logo(n, D + 44, y, 0, size, t0 + .15 + .1 * i, 1.1 + i * .6))
    return "".join(out)


def tower(t0):
    """Phone: the layers stacked, platform at the bottom; each layer's logos stand in a V
    over its front half, under the next layer, which floats high enough to leave them clear."""
    h, hp, thick, gap, size = 110, 118, 26, 128, 50
    out = []
    plate = block(-hp, hp, -hp, hp, -12, 0, "platform", top_line=False) + label("platform", hp, hp - 14, -3)
    rows = [(PLATFORM[1], hp, 0)]
    out.append(f'<g class="rise" style="animation-delay:{t0:.2f}s">{plate}</g>')
    z = 0
    for k, (name, logos) in enumerate(LAYERS):
        z0, z1 = z + gap, z + gap + thick
        rows.append((logos, h, z1))
        z = z1
    # draw bottom-up: each layer, then its own row of logos, then the next layer above
    for k, (logos, half, ztop) in enumerate(rows):
        if k:
            name = LAYERS[k - 1][0]
            delay = t0 + .3 + .28 * (k - 1)
            out.append(f'<g class="step" style="animation-delay:{delay:.2f}s">{block(-half, half, -half, half, ztop - thick, ztop, name)}'
                       f'{label(name, half, half - 14, ztop - thick + 7)}</g>')
            base = delay + .35
        else:
            base = t0 + .15
        # Each spot is (x - y, x + y) / half. Under another layer the logos make a V over the
        # front half: the middle ones at the front, the outer ones further back and out to the
        # sides, where the layer above rises. The top layer has nothing above it, so its four
        # logos take its four corners; the black marks go to the side and the front, over the
        # block, and the colored ones to the back, where they stand out against the page.
        if k == len(rows) - 1:
            corner = {"react": (0, -1.24), "next-js": (-1.24, 0), "swiftui": (1.24, 0), "expo": (0, 1.24)}
            spots = [corner[name] for name in logos]
        else:
            spots = {3: [(-.85, .25), (0, .95), (.85, .25)], 4: [(-.95, .25), (-.32, .95), (.32, .95), (.95, .25)]}[len(logos)]
        placed = sorted((((c + u) * half / 2, (c - u) * half / 2, name) for (u, c), name in zip(spots, logos)),
                        key=lambda p: P(p[0], p[1], 0)[1])
        for i, (x, y, name) in enumerate(placed):
            out.append(logo(name, x, y, ztop, size, base + .09 * i, (i * .37 + k * .5) % 2.4))
    return "".join(out)


def grid(w, h, cx, cy):
    """A faint isometric dot grid that drifts by one tile every 16 s and fades at the edges;
    every 7 s a wave of brighter dots rises from the middle of the drawing and spreads out.
    A README image does not react to the mouse, so the wave keeps its own time."""
    pw, ph, dot = 27.7, 16, CLAY["grid"]

    def dots(pid, r):
        return (f'<pattern id="{pid}" width="{pw}" height="{ph}" patternUnits="userSpaceOnUse">'
                + "".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{dot}"/>' for x, y in ((0, 0), (pw / 2, ph / 2), (pw, 0), (0, ph), (pw, ph)))
                + '</pattern>')
    reach = .62 * max(w, h)  # the wave fades out about where the grid does
    return (f'<defs>{dots("dots", 1.1)}{dots("bright", 1.7)}'
            f'<radialGradient id="fade" cx="50%" cy="50%" r="60%"><stop offset="0" stop-color="#fff" stop-opacity=".55"/>'
            f'<stop offset=".7" stop-color="#fff" stop-opacity=".2"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>'
            f'<mask id="vignette" maskUnits="userSpaceOnUse" x="0" y="0" width="{w}" height="{h}"><rect width="{w}" height="{h}" fill="url(#fade)"/></mask>'
            f'<radialGradient id="glowfade" cx="42.5%" cy="50%" r="55%"><stop offset="0" stop-color="#fff" stop-opacity=".9"/>'
            f'<stop offset=".75" stop-color="#fff" stop-opacity=".45"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>'
            f'<mask id="glow" maskUnits="userSpaceOnUse" x="0" y="0" width="{w}" height="{h}"><rect width="{w}" height="{h}" fill="url(#glowfade)"/></mask>'
            f'<mask id="wave" maskUnits="userSpaceOnUse" x="0" y="0" width="{w}" height="{h}"><g transform="translate({cx:.1f} {cy:.1f})">'
            f'<circle class="ring" r="{reach:.0f}" fill="none" stroke="#fff" stroke-width="{reach * .14:.0f}"/></g></mask></defs>'
            f'<g mask="url(#vignette)" class="grid-in"><rect class="drift" x="{-pw}" y="{-ph}" width="{w + 2 * pw}" height="{h + 2 * ph}" fill="url(#dots)"/>'
            f'</g><g mask="url(#glow)" class="grid-in"><g mask="url(#wave)"><rect class="drift" x="{-pw}" y="{-ph}" width="{w + 2 * pw}" height="{h + 2 * ph}" fill="url(#bright)"/></g></g>'
            f'<style>.drift{{animation:drift 16s linear infinite}}@keyframes drift{{to{{transform:translate({pw}px,{ph}px)}}}}'
            f'.grid-in{{opacity:0;animation:in 1.2s ease-out forwards}}'
            f'.ring{{opacity:0;transform:scale(.04);animation:wave 7s linear 2.2s infinite}}'
            f'@keyframes wave{{0%{{opacity:0;transform:scale(.04)}}8%{{opacity:1}}60%{{opacity:.7}}85%,100%{{opacity:0;transform:scale(1)}}}}</style>')


STYLE = """<style>
.rise{opacity:0;animation:in .6s cubic-bezier(.16,1,.3,1) forwards}
.step{opacity:0;animation:step .7s cubic-bezier(.34,1.4,.64,1) forwards}
.drop{opacity:0;animation:drop .55s cubic-bezier(.34,1.5,.64,1) forwards}
.float{animation:float 3.2s ease-in-out infinite}
@keyframes in{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}
@keyframes step{from{opacity:0;transform:translateY(-46px)}to{opacity:1;transform:none}}
@keyframes drop{from{opacity:0;transform:translateY(-24px)}to{opacity:1;transform:none}}
@keyframes float{0%,100%{transform:none}50%{transform:translateY(-4px)}}
</style>"""


def card(draw, w, h, pad):
    BOX[:] = [1e9, 1e9, -1e9, -1e9]
    drawn = draw(.35)
    bw, bh = BOX[2] - BOX[0], BOX[3] - BOX[1]
    room = 2 * min(.425 * w, w - .425 * w) - 2 * pad  # widest drawing centered at 42.5%
    k = room / bw if h is None else min(room / bw, (h - 2 * pad) / bh)
    if h is None:  # the phone card is as tall as its drawing
        h = round(bh * k + 2 * pad)
    tx = .425 * w - (BOX[0] + bw / 2) * k
    ty = (h - bh * k) / 2 - BOX[1] * k
    defs = "".join(symbol(n) for n in [*sum((l for _, l in LAYERS), []), *PLATFORM[1]])
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="t">'
            f'<title id="t">{TITLE}</title>{STYLE}{grid(w, h, .425 * w, h / 2)}<defs>{defs}</defs>'
            f'<g transform="translate({tx:.1f} {ty:.1f}) scale({k:.3f})">{drawn}</g></svg>\n')


OUT.mkdir(parents=True, exist_ok=True)
for f in OUT.glob("stack-*.svg"):
    f.unlink()
# desktop: 900 x 490 shows about 400 px tall at 87% of GitHub's 846 px column
for form, draw, w, h, pad in (("desktop", staircase, 900, 490, 14), ("phone", tower, 440, None, 10)):
    body = card(draw, w, h, pad)
    name = f"stack-{form}-{hashlib.sha256(body.encode()).hexdigest()[:8]}.svg"
    (OUT / name).write_text(body)
    print(name)
