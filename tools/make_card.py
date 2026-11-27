#!/usr/bin/env python3
"""Poetogram quote card generator.
Usage: python3 make_card.py out.png "line 1" "line 2" [--accent WORD]
Theme: warm parchment, ink-sketch drawing, single red accent, Poetogram signature.
"""
import sys, math, random, subprocess, os, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
random.seed(7)

p = argparse.ArgumentParser()
p.add_argument("out")
p.add_argument("lines", nargs="+")
p.add_argument("--accent", default="")
p.add_argument("--art", default="flower")
p.add_argument("--size", type=int, default=0)
p.add_argument("--tag", default="")
p.add_argument("--reveal", type=int, default=99)
p.add_argument("--artop", type=float, default=1.0)
a = p.parse_args()

W, H = 1080, 1350
INK = "#2e2118"
RED = "#b3261e"
random.seed(7)

def jitter_path(points, j=1.6):
    pts = [(x + random.uniform(-j, j), y + random.uniform(-j, j)) for x, y in points]
    d = f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"
    for i in range(1, len(pts) - 1):
        mx, my = (pts[i][0] + pts[i+1][0]) / 2, (pts[i][1] + pts[i+1][1]) / 2
        d += f" Q{pts[i][0]:.1f},{pts[i][1]:.1f} {mx:.1f},{my:.1f}"
    d += f" L{pts[-1][0]:.1f},{pts[-1][1]:.1f}"
    return d

def petal(cx, cy, ang, length, width, fill=True, strokes=2):
    """Elongated daisy-like petal from (cx,cy) in direction ang."""
    out = []
    ca, sa = math.cos(ang), math.sin(ang)
    def tr(u, v):
        return (cx + u * ca - v * sa, cy + u * sa + v * ca)
    outline = []
    for t in [i / 14 for i in range(15)]:
        outline.append(tr(t * length, width * math.sin(math.pi * t) ** 0.8 * (1 - 0.25 * t)))
    for t in [1 - i / 14 for i in range(15)]:
        outline.append(tr(t * length, -width * math.sin(math.pi * t) ** 0.8 * (1 - 0.25 * t)))
    d = jitter_path(outline, 0.8) + " Z"
    if fill:
        out.append(f'<path d="{d}" fill="{RED}" fill-opacity="0.88"/>')
    for s in range(strokes):
        out.append(f'<path d="{jitter_path(outline, 1.2)}" fill="none" stroke="{INK}" stroke-width="{1.6 if s==0 else 0.9}" stroke-linecap="round" opacity="{0.9 if s==0 else 0.5}"/>')
    # vein hatch
    for k in (-0.35, 0, 0.35):
        p1, p2 = tr(length * 0.12, width * k * 0.4), tr(length * 0.8, width * k * 0.5)
        out.append(f'<path d="M{p1[0]:.1f},{p1[1]:.1f} L{p2[0]:.1f},{p2[1]:.1f}" stroke="#5a0f0a" stroke-width="0.8" opacity="0.55"/>')
    return "\n".join(out)

def art_flower():
    svg = []
    # ---------- stem ----------
    stem_pts = [(470, 1290), (478, 1220), (492, 1150), (508, 1080), (522, 1010), (536, 950), (548, 905)]
    for k in range(3):
        svg.append(f'<path d="{jitter_path(stem_pts, 2.2)}" fill="none" stroke="{INK}" stroke-width="{3.2 - k}" stroke-linecap="round" opacity="{0.95 - k*0.25}"/>')
    # leaves
    def leaf(bx, by, ang, L, Wd):
        return petal(bx, by, ang, L, Wd, fill=False, strokes=3)
    svg.append(leaf(492, 1150, math.radians(200), 120, 30))
    svg.append(leaf(515, 1050, math.radians(-20), 110, 26))
    # leaf hatching
    for i in range(9):
        x = 400 + i * 9; svg.append(f'<path d="M{x},{1125+i*2} l18,30" stroke="{INK}" stroke-width="0.8" opacity="0.45"/>')
    # ---------- flower head ----------
    FX, FY = 552, 880
    n = 13
    missing = {1, 2, 3}  # petals that have flown away (upper-right)
    for i in range(n):
        if i in missing: continue
        ang = math.radians(-90 + i * 360 / n + random.uniform(-5, 5))
        svg.append(petal(FX, FY, ang, 120 + random.uniform(-10, 10), 24 + random.uniform(-3, 3)))
    # centre
    svg.append(f'<circle cx="{FX}" cy="{FY}" r="26" fill="#3a2414"/>')
    for i in range(60):
        r = random.uniform(4, 24); t = random.uniform(0, 6.283)
        svg.append(f'<circle cx="{FX + r*math.cos(t):.1f}" cy="{FY + r*math.sin(t):.1f}" r="{random.uniform(1.2,2.6):.1f}" fill="#d9a441" opacity="0.8"/>')
    svg.append(f'<circle cx="{FX}" cy="{FY}" r="27" fill="none" stroke="{INK}" stroke-width="2"/>')
    # ---------- flying petals (losing, with a smile) ----------
    flying = [(700, 760, -10, 0.95), (790, 690, 35, 0.85), (870, 640, 80, 0.75), (945, 575, 140, 0.62)]
    for x, y, rot, sc in flying:
        svg.append(f'<g opacity="{0.6 + sc*0.4:.2f}">' + petal(x, y, math.radians(rot), 95 * sc, 20 * sc) + "</g>")
    # wind lines
    for (x, y, L) in [(640, 820, 140), (720, 740, 170), (820, 670, 120)]:
        svg.append(f'<path d="M{x},{y} q{L/2},-{L/5} {L},-{L/3}" fill="none" stroke="{INK}" stroke-width="1.2" stroke-dasharray="14 9" opacity="0.45"/>')
    # ink splatter
    for _ in range(18):
        svg.append(f'<circle cx="{random.uniform(80,1000):.0f}" cy="{random.uniform(560,1250):.0f}" r="{random.uniform(0.8,3):.1f}" fill="{INK}" opacity="0.35"/>')
    return svg

from arts import ARTS
ARTS['flower'] = art_flower
svg = ARTS[a.art](globals()) if a.art != 'flower' else art_flower()
art = "\n".join(svg)

# ---------- quote text ----------
def fmt(line):
    import re
    if a.accent:
        pat = r'(?<![\u0900-\u097F])' + re.escape(a.accent) + r'(?![\u0900-\u097F])'
        return re.sub(pat, f'<span class="acc">{a.accent}</span>', line)
    return line
quote_html = "<br>".join(f'<span style="visibility:{"visible" if i < a.reveal else "hidden"}">{fmt(l)}</span>' for i, l in enumerate(a.lines))
ORN_VIS = "visible" if a.reveal >= len(a.lines) else "hidden"
mx = max(len(l) for l in a.lines)
tag_html = f'<div class="tag">— {a.tag} —</div>' if a.tag else ''
FS = a.size or (66 if mx <= 30 else 58 if mx <= 36 else 50)

html = f"""<!doctype html><html><head><meta charset="utf-8"><style>
html,body{{margin:0;padding:0}}
.card{{width:{W}px;height:{H}px;position:relative;overflow:hidden;
 background:radial-gradient(ellipse at 50% 40%, #f4e7cb 0%, #ead8b2 60%, #d9c194 100%);font-family:'FreeSerif',serif}}
.grain{{position:absolute;inset:0}}
.top{{position:absolute;top:70px;width:100%;text-align:center;letter-spacing:6px;font-size:24px;color:#7a5a3c;font-family:'FreeSerif';}}
.top b{{color:{RED};font-weight:normal}}
.quote{{position:absolute;top:190px;left:70px;right:70px;text-align:center;color:{INK};
 font-size:{FS}px;font-weight:bold;line-height:1.55;text-shadow:0 1px 0 rgba(255,255,255,.35)}}
.acc{{color:{RED}}}
.tag{{font-size:26px;font-weight:normal;color:{RED};letter-spacing:3px;margin-bottom:26px;line-height:1}}
.orn{{margin-top:34px;text-align:center;line-height:0;visibility:{ORN_VIS}}}
.sig{{position:absolute;right:70px;bottom:70px;text-align:right;color:{INK}}}
.sig .name{{font-family:'FreeSerif';font-style:italic;font-weight:bold;font-size:58px;transform:rotate(-6deg);display:inline-block}}
.handle{{position:absolute;left:70px;bottom:78px;font-size:24px;color:#6b4f35;letter-spacing:2px}}
</style></head><body><div class="card">
<svg class="grain" width="{W}" height="{H}"><filter id="n"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="3" seed="4"/><feColorMatrix values="0 0 0 0 .35  0 0 0 0 .25  0 0 0 0 .12  0 0 0 .22 0"/></filter>
<filter id="fib"><feTurbulence type="fractalNoise" baseFrequency=".012 .04" numOctaves="2" seed="9"/><feColorMatrix values="0 0 0 0 .4  0 0 0 0 .28  0 0 0 0 .1  0 0 0 .10 0"/></filter>
<rect width="100%" height="100%" filter="url(#fib)"/><rect width="100%" height="100%" filter="url(#n)"/>
<rect x="34" y="34" width="{W-68}" height="{H-68}" fill="none" stroke="#7a5a3c" stroke-width="1.2" opacity=".45"/>
<rect x="44" y="44" width="{W-88}" height="{H-88}" fill="none" stroke="#7a5a3c" stroke-width=".6" opacity=".35"/>
<filter id="wob"><feTurbulence type="fractalNoise" baseFrequency=".03" numOctaves="2" seed="3"/><feDisplacementMap in="SourceGraphic" scale="4"/></filter>
<g filter="url(#wob)" opacity="{a.artop}">{art}</g>
<!-- signature flourish -->
<path d="M650,1300 C780,1284 920,1292 1012,1262 c-30,2 -55,12 -70,26" fill="none" stroke="{RED}" stroke-width="2.4" stroke-linecap="round"/>
</svg>
<div class="top">✦ <b>its_poetogram</b> ✦</div>
<div class="quote">{tag_html}{quote_html}<div class="orn"><svg width="260" height="20"><path d="M10,10 H110 M150,10 H250" stroke="#7a5a3c" stroke-width="1.2"/><path d="M130,2 l8,8 -8,8 -8,-8z" fill="{RED}"/></svg></div></div>
<div class="handle">@its_poetogram</div>
<div class="sig"><span class="name">its_poetogram</span></div>
</div></body></html>"""

base = os.path.splitext(a.out)[0]
open(base + ".html", "w").write(html)
subprocess.run(["google-chrome", "--headless=new", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
                f"--window-size={W},{H}", f"--screenshot={os.path.abspath(a.out)}", "file://" + os.path.abspath(base + ".html")],
               check=True, capture_output=True)
print("ok", a.out)
