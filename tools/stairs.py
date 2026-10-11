"""Profile README card, v3: an isometric staircase of the stack. The steps go from the
database to the API to the screens, on the platform that ships them, each with the
logos of its technologies standing on it. Blocks drop in, logos land and then float.
Four files: desktop and phone, light and dark, named by content hash.
Usage: python3 tools/stairs.py tools/logos assets"""
import hashlib, re, sys
from pathlib import Path

LOGOS_DIR, OUT = Path(sys.argv[1]), Path(sys.argv[2])
C, S = 0.866, 0.5
D, W_STEP, H_STEP = 100, 190, 34  # a long, low staircase: about 1.44 wide for 1 tall
LOGO = 40  # canvas units; the phone card, drawn smaller, takes larger logos
BOX = [1e9, 1e9, -1e9, -1e9]  # extent of the tower, filled while drawing
FONT = "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace"
MONOCHROME = {"next-js", "expo", "prisma"}  # black marks: black on light, white on dark

THEMES = {
    "light": dict(fg="#1f2328", muted="#59636e", top="#f3f5f6", front="#e3e8ea", side="#d3dadd", edge="#b9c3c7",
                  plate="#eaeef0", mono="#000000", shadow="rgba(31,35,40,.16)"),
    "dark": dict(fg="#f0f6fc", muted="#9198a1", top="#262c33", front="#1b2026", side="#151a1f", edge="#3a434c",
                 plate="#1d2329", mono="#ffffff", shadow="rgba(0,0,0,.45)"),
}
TINT = {"database": "#4169E1", "api": "#E0234E", "screens": "#55C0DD"}
STEPS = [
    ("database", ["postgresql", "prisma", "drizzle"]),
    ("api", ["nestjs", "trpc", "typescript"]),
    ("screens", ["next-js", "react", "expo", "swiftui"]),
]
PLATFORM = ("platform", ["docker", "github-actions", "cloudflare", "aws"])
NAMES = {"postgresql": "PostgreSQL", "prisma": "Prisma", "drizzle": "Drizzle", "nestjs": "NestJS", "trpc": "tRPC",
         "typescript": "TypeScript", "next-js": "Next.js", "react": "React", "expo": "Expo", "swiftui": "SwiftUI",
         "docker": "Docker", "github-actions": "GitHub Actions", "cloudflare": "Cloudflare", "aws": "AWS"}
HEADLINE = ["I build products end to end,", "from the database to the screen,", "and the platform that ships them."]
TITLE = ("Leandro Bertalhia's stack as a staircase, from the database to the screen, "
         "on the platform that ships them: PostgreSQL, Prisma and Drizzle; NestJS, tRPC and TypeScript; "
         "Next.js, React, Expo and SwiftUI; on Docker, GitHub Actions, Cloudflare and AWS.")


def P(x, y, z):
    return ((x - y) * C, (x + y) * S - z)


def grow(sx, sy):
    BOX[0], BOX[1] = min(BOX[0], sx), min(BOX[1], sy)
    BOX[2], BOX[3] = max(BOX[2], sx), max(BOX[3], sy)


def poly(points, fill, stroke, extra=""):
    projected = [P(*p) for p in points]
    for a, b in projected:
        grow(a, b)
    pts = " ".join(f"{a:.1f},{b:.1f}" for a, b in projected)
    return f'<polygon points="{pts}" fill="{fill}" stroke="{stroke}" stroke-width="1" stroke-linejoin="round"{extra}/>'


def symbol(name, c):
    svg = (LOGOS_DIR / f"{name}.svg").read_text()
    box = re.search(r'viewBox="([^"]+)"', svg).group(1)
    inner = re.search(r"<svg[^>]*>(.*)</svg>", svg, re.S).group(1)
    inner = re.sub(r"<title>.*?</title>", "", inner, flags=re.S)
    inner = re.sub(r'\s(id)="[^"]*"', "", inner)
    if name in MONOCHROME:
        inner = re.sub(r'fill="#[0-9A-Fa-f]{3,6}"', f'fill="{c["mono"]}"', inner)
    return f'<symbol id="{name}" viewBox="{box}">{inner}</symbol>'


def face_label(text, x, y_from, z, c):
    """Text laid on a front face (x = const), running along -y, baseline at height z."""
    sx, sy = P(x, y_from, z)
    return (f'<text transform="matrix({C} {-S} 0 1 {sx:.1f} {sy:.1f})" font-family="{MONO}" font-size="13" '
            f'letter-spacing=".6" fill="{c["muted"]}">{text}</text>')


def logo(name, x, y, z, size, delay, float_delay, c):
    sx, sy = P(x, y, z)
    grow(sx - size / 2, sy - size - 8)
    grow(sx + size / 2, sy)
    return (f'<g class="drop" style="animation-delay:{delay:.2f}s"><ellipse cx="{sx:.1f}" cy="{sy:.1f}" rx="{size * .42:.1f}" ry="{size * .17:.1f}" fill="{c["shadow"]}"/>'
            f'<g class="float" style="animation-delay:{float_delay:.2f}s"><use href="#{name}" x="{sx - size / 2:.1f}" y="{sy - size - 4:.1f}" width="{size}" height="{size}"/></g></g>')


def tower(c, t0):
    out = []
    # the platform under everything
    px0, px1, py0, py1, pz = -34, D + 74, -3 * W_STEP - 34, 46, 10
    plate = [
        poly([(px0, py0, 0), (px1, py0, 0), (px1, py1, 0), (px0, py1, 0)], c["plate"], c["edge"]),
        poly([(px1, py0, -pz), (px1, py1, -pz), (px1, py1, 0), (px1, py0, 0)], c["front"], c["edge"]),
        poly([(px0, py1, -pz), (px1, py1, -pz), (px1, py1, 0), (px0, py1, 0)], c["side"], c["edge"]),
        face_label(PLATFORM[0], px1, py1 - 14, -2.5, c),
    ]
    out.append(f'<g class="rise" style="animation-delay:{t0:.2f}s">{"".join(plate)}</g>')
    # steps, back to front, each dropping in after the one below it lands
    for k in reversed(range(len(STEPS))):
        label, names = STEPS[k]
        y0, y1, h = -(k + 1) * W_STEP, -k * W_STEP, (k + 1) * H_STEP
        tint = TINT[label]
        delay = t0 + .3 + .28 * k
        faces = [
            poly([(0, y0, h), (D, y0, h), (D, y1, h), (0, y1, h)], c["top"], c["edge"]),
            poly([(0, y0, h), (D, y0, h), (D, y1, h), (0, y1, h)], tint, "none", ' fill-opacity=".10"'),
            poly([(D, y0, 0), (D, y1, 0), (D, y1, h), (D, y0, h)], c["front"], c["edge"]),
            poly([(0, y1, 0), (D, y1, 0), (D, y1, h), (0, y1, h)], c["side"], c["edge"]),
            # a line of the layer's color along the front top edge
            f'<line x1="{P(D, y0, h)[0]:.1f}" y1="{P(D, y0, h)[1]:.1f}" x2="{P(D, y1, h)[0]:.1f}" y2="{P(D, y1, h)[1]:.1f}" stroke="{tint}" stroke-width="2.5" stroke-linecap="round"/>',
            face_label(label, D, y1 - 14, h - 20, c),
        ]
        out.append(f'<g class="step" style="animation-delay:{delay:.2f}s">{"".join(faces)}</g>')
        # a zigzag across the step: neighbours differ in depth, so no two logos touch
        spots = {3: [(.25, .2), (.75, .5), (.25, .8)], 4: [(.25, .14), (.75, .38), (.25, .62), (.75, .86)]}[len(names)]
        placed = sorted(((fx * D, y0 + fy * W_STEP, n) for (fx, fy), n in zip(spots, names)), key=lambda p: P(p[0], p[1], 0)[1])
        for i, (x, y, n) in enumerate(placed):
            out.append(logo(n, x, y, h, LOGO, delay + .35 + .09 * i, (i * .37 + k * .5) % 2.4, c))
    # the platform's own logos stand in front of the steps
    for i, (n, y) in enumerate(zip(PLATFORM[1], (-2.62 * W_STEP, -1.9 * W_STEP, -1.18 * W_STEP, -.46 * W_STEP))):
        out.append(logo(n, D + 44, y, 0, LOGO, t0 + .15 + .1 * i, 1.1 + i * .6, c))
    return "".join(out)


def style(c):
    ease = "cubic-bezier(.16,1,.3,1)"
    return f"""<style>
.eyebrow{{font:500 13px {MONO};letter-spacing:.8px;fill:{c['muted']}}}
.name{{font:800 56px {FONT};letter-spacing:-2px;fill:{c['fg']}}}
.line{{font:400 17px {FONT};fill:{c['muted']}}}
.in{{opacity:0;animation:in .7s {ease} forwards}}
.rise{{opacity:0;animation:in .6s {ease} forwards}}
.step{{opacity:0;animation:step .7s cubic-bezier(.34,1.4,.64,1) forwards}}
.drop{{opacity:0;animation:drop .55s cubic-bezier(.34,1.5,.64,1) forwards}}
.float{{animation:float 3.2s ease-in-out infinite}}
@keyframes in{{from{{opacity:0;transform:translateY(10px)}}to{{opacity:1;transform:none}}}}
@keyframes step{{from{{opacity:0;transform:translateY(-46px)}}to{{opacity:1;transform:none}}}}
@keyframes drop{{from{{opacity:0;transform:translateY(-24px)}}to{{opacity:1;transform:none}}}}
@keyframes float{{0%,100%{{transform:none}}50%{{transform:translateY(-4px)}}}}
</style>"""


def card(form, theme):
    c = THEMES[theme]
    defs = "".join(symbol(n, c) for n in NAMES)
    global LOGO
    if form == "desktop":
        w, h, target, LOGO = 900, 592, (50, 18, 850, 574), 40
    else:
        w, h, target, LOGO = 440, 312, (30, 14, 440, 298), 45
    text = ""
    BOX[:] = [1e9, 1e9, -1e9, -1e9]
    drawn = tower(c, .35)
    bw, bh = BOX[2] - BOX[0], BOX[3] - BOX[1]
    tw, th = target[2] - target[0], target[3] - target[1]
    k = min(tw / bw, th / bh)
    tx = target[0] + (tw - bw * k) / 2 - BOX[0] * k
    ty = target[1] + (th - bh * k) / 2 - BOX[1] * k
    place = f"translate({tx:.1f} {ty:.1f}) scale({k:.3f})"
    return f"""<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="t">
<title id="t">{TITLE}</title>
{style(c)}
<defs>{defs}</defs>
{text}
<g transform="{place}">{drawn}</g>
</svg>
"""


OUT.mkdir(parents=True, exist_ok=True)
for f in OUT.glob("*.svg"):
    f.unlink()
for form in ("desktop", "phone"):
    for theme in THEMES:
        body = card(form, theme)
        name = f"stack-{form}-{theme}-{hashlib.sha256(body.encode()).hexdigest()[:8]}.svg"
        (OUT / name).write_text(body)
        print(name)
