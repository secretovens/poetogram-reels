"""Visual styles shared by reels (1080x1920) and carousels (1080x1350).
Each style = background layer (HTML/SVG) + text colours/fonts. Same brand marks everywhere:
series tag, @its_poetogram, signature. Only FreeSerif/FreeSans have Devanagari here, so variety comes
from layout, colour, texture, art and motion."""
import math, random, re, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import arts

STYLES = ["parchment", "noir", "diary", "night", "poster", "dusk", "chalk"]

P = {  # text colour, accent colour, font, weight, align, reveal mode, small-text colour
    "parchment": dict(fg="#2e2118", acc="#b3261e", font="FreeSerif", align="center", mode="line", sub="#7a5a3c"),
    "noir":      dict(fg="#f4f1ea", acc="#f2b134", font="FreeSans", align="left", mode="word", sub="#8d8a84"),
    "diary":     dict(fg="#1d3576", acc="#c0262d", font="FreeSerif", align="left", mode="line", sub="#5f6f99"),
    "night":     dict(fg="#f3dcae", acc="#ffffff", font="FreeSerif", align="center", mode="line", sub="#9fb0d6"),
    "poster":    dict(fg="#141414", acc="#141414", font="FreeSans", align="left", mode="word", sub="#555"),
    "dusk":      dict(fg="#fff7ee", acc="#ffd58a", font="FreeSerif", align="center", mode="line", sub="#ffe3cc"),
    "chalk":     dict(fg="#f2f2ea", acc="#ffe066", font="FreeSans", align="center", mode="word", sub="#b9cfc4"),
}

def _noise(id_, freq, op, seed=3, tint=(0, 0, 0)):
    r, g, b = tint
    return (f'<filter id="{id_}"><feTurbulence type="fractalNoise" baseFrequency="{freq}" numOctaves="3" seed="{seed}"/>'
            f'<feColorMatrix values="0 0 0 0 {r}  0 0 0 0 {g}  0 0 0 0 {b}  0 0 0 {op} 0"/></filter>'
            f'<rect width="100%" height="100%" filter="url(#{id_})"/>')

def art_svg(name, seed, recolor=None, dy=0, scale=1.0, op=1.0):
    if not name or name not in arts.ARTS and name != "none":
        return ""
    if name == "none": return ""
    random.seed(seed)
    parts = arts.ARTS[name]({})
    s = "\n".join(parts)
    if recolor:
        for a, b in recolor.items(): s = s.replace(a, b)
    return (f'<g transform="translate({540*(1-scale):.0f},{dy}) scale({scale})" opacity="{op}">'
            f'<filter id="wob"><feTurbulence type="fractalNoise" baseFrequency=".03" numOctaves="2" seed="3"/>'
            f'<feDisplacementMap in="SourceGraphic" scale="4"/></filter><g filter="url(#wob)">{s}</g></g>')

def background(style, W, H, seed=1, art=None, art_dy=None):
    rnd = random.Random(seed)
    if style == "parchment":
        dy = (H - 1350) // 2 + 150 if art_dy is None else art_dy
        return (f'<div class="bg" style="background:radial-gradient(ellipse at 50% 40%,#f4e7cb 0%,#ead8b2 60%,#d9c194 100%)"></div>'
                f'<svg class="bg" width="{W}" height="{H}">{_noise("n1", .9, .22, 4, (.35,.25,.12))}{_noise("n2", ".012 .04", .10, 9, (.4,.28,.1))}'
                f'<rect x="34" y="34" width="{W-68}" height="{H-68}" fill="none" stroke="#7a5a3c" stroke-width="1.2" opacity=".45"/>'
                f'{art_svg(art, seed, None, dy)}</svg>')
    if style == "noir":
        return (f'<div class="bg" style="background:radial-gradient(ellipse at 30% 35%,#1d1c20 0%,#0c0c0e 70%)"></div>'
                f'<svg class="bg" width="{W}" height="{H}">{_noise("n1", .85, .16, seed, (1,1,1))}'
                f'<rect x="90" y="{int(H*0.17)}" width="70" height="6" fill="#f2b134"/></svg>')
    if style == "diary":
        top, gap = int(H * 0.16), 74
        lines = "".join(f'<line x1="0" x2="{W}" y1="{y}" y2="{y}" stroke="#9db4dd" stroke-width="2" opacity=".55"/>' for y in range(top, H, gap))
        cx, cy = rnd.randint(700, 900), rnd.randint(int(H*.72), int(H*.82))
        stain = (f'<circle cx="{cx}" cy="{cy}" r="120" fill="none" stroke="#a0703c" stroke-width="10" opacity=".13"/>'
                 f'<circle cx="{cx+6}" cy="{cy-4}" r="112" fill="none" stroke="#a0703c" stroke-width="3" opacity=".12"/>')
        return (f'<div class="bg" style="background:#fbf8ef"></div><svg class="bg" width="{W}" height="{H}">{lines}'
                f'<line x1="120" x2="120" y1="0" y2="{H}" stroke="#e06a6a" stroke-width="3" opacity=".7"/>{stain}'
                f'{_noise("n1", .8, .08, seed, (.3,.25,.1))}</svg>')
    if style == "night":
        stars = "".join(f'<circle cx="{rnd.uniform(0,W):.0f}" cy="{rnd.uniform(0,H*.75):.0f}" r="{rnd.choice([.8,1.1,1.5,2.2]):.1f}" fill="#fff" opacity="{rnd.uniform(.3,.95):.2f}"/>' for _ in range(140))
        mx, my = (200, int(H * 0.63)) if H > 1500 else (W - 170, 170)
        moon = (f'<circle cx="{mx}" cy="{my}" r="70" fill="#f6e7c1"/><circle cx="{mx+28}" cy="{my-16}" r="64" fill="#0e1a38"/>'
                f'<circle cx="{mx}" cy="{my}" r="120" fill="#f6e7c1" opacity=".06"/>')
        dy = H - 1290 if art_dy is None else art_dy
        a = art_svg(art, seed, {"#2e2118": "#cfd9f2", "#b3261e": "#f2c36b", "#f6ecd4": "#13214a", "#5a0f0a": "#f2c36b", "#3a2414": "#cfd9f2"}, dy, 1.0, .9)
        return (f'<div class="bg" style="background:linear-gradient(180deg,#081028 0%,#13214a 60%,#1f2d55 100%)"></div>'
                f'<svg class="bg" width="{W}" height="{H}">{stars}{moon}{a}{_noise("n1", .9, .07, seed, (1,1,1))}</svg>')
    if style == "poster":
        return (f'<div class="bg" style="background:#f2eee6"></div><svg class="bg" width="{W}" height="{H}">'
                f'<text x="70" y="{int(H*0.36)}" font-family="FreeSerif" font-size="360" fill="#d7262e" opacity=".95">“</text>'
                f'<rect x="90" y="{int(H*0.86)}" width="{W-180}" height="3" fill="#141414"/>'
                f'{_noise("n1", .9, .10, seed, (.2,.2,.2))}</svg>')
    if style == "dusk":
        base = H - 60
        bld = ""; x = -20
        while x < W:
            w = rnd.randint(70, 150); h = int(rnd.randint(140, 420) * (1 if H > 1500 else .55))
            bld += f'<rect x="{x}" y="{base-h}" width="{w}" height="{h+60}" fill="#2a1b3d"/>'
            for wy in range(base - h + 25, base - 20, 38):
                for wx in range(x + 14, x + w - 18, 30):
                    if rnd.random() < .28: bld += f'<rect x="{wx}" y="{wy}" width="12" height="16" fill="#ffcf7a" opacity="{rnd.uniform(.5,.95):.2f}"/>'
            x += w + rnd.randint(-10, 12)
        sun = f'<circle cx="{W//2}" cy="{base-120}" r="230" fill="#ffd9a0" opacity=".35"/>'
        return (f'<div class="bg" style="background:linear-gradient(180deg,#3b2a5a 0%,#8a3f6e 38%,#d9666b 66%,#f6a96b 100%)"></div>'
                f'<svg class="bg" width="{W}" height="{H}">{sun}{bld}{_noise("n1", .9, .08, seed, (1,.9,.8))}</svg>')
    if style == "chalk":
        doodles = ""
        for _ in range(6):
            x, y = rnd.uniform(60, W-60), rnd.uniform(H*.08, H*.95)
            doodles += f'<text x="{x:.0f}" y="{y:.0f}" font-family="FreeSans" font-size="{rnd.randint(30,60)}" fill="#e8efe8" opacity=".10">{rnd.choice(["✦","~","○","✕","♡","→"])}</text>'
        return (f'<div class="bg" style="background:radial-gradient(ellipse at 50% 45%,#2d5246 0%,#1c3a31 70%,#132a23 100%)"></div>'
                f'<svg class="bg" width="{W}" height="{H}">{_noise("n1", .7, .18, seed, (1,1,1))}{doodles}'
                f'<rect x="18" y="18" width="{W-36}" height="{H-36}" fill="none" stroke="#7a5a3c" stroke-width="18" opacity=".9"/></svg>')
    raise ValueError(style)

def base_css(style, W, H):
    p = P[style]
    extra = {
        "diary": ".acc{position:relative;color:#c0262d}.acc:after{content:'';position:absolute;left:-14px;right:-14px;top:-2px;bottom:-6px;border:4px solid #c0262d;border-radius:50%;transform:rotate(-3deg);opacity:.8}",
        "poster": ".acc{background:linear-gradient(transparent 55%,#ffd23f 55%,#ffd23f 92%,transparent 92%)}",
        "noir": ".acc{color:#f2b134}",
        "night": ".acc{color:#fff;text-shadow:0 0 22px rgba(255,230,170,.9)}",
        "dusk": ".q{text-shadow:0 3px 18px rgba(40,10,40,.55)}",
        "chalk": ".q{filter:url(#chalkf)}.acc{color:#ffe066}",
        "parchment": ".q{text-shadow:0 1px 0 rgba(255,255,255,.35)}",
    }[style]
    return (f"html,body{{margin:0;padding:0}}.page{{width:{W}px;height:{H}px;position:relative;overflow:hidden;font-family:'{p['font']}'}}"
            f".bg{{position:absolute;inset:0}}.acc{{color:{p['acc']}}}"
            f".q{{color:{p['fg']};font-weight:bold;text-align:{p['align']};line-height:1.5}}"
            f".sub{{color:{p['sub']}}}" + extra)

CHALK_FILTER = ('<svg width="0" height="0" style="position:absolute"><filter id="chalkf"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" seed="2"/>'
                '<feDisplacementMap in="SourceGraphic" scale="3"/></filter></svg>')

def words_with_accent(line, accent):
    acc = set(re.sub(r"[^ऀ-ॿ\w ]", "", accent).split()) if accent else set()
    out = []
    for w in line.split():
        core = re.sub(r"[^ऀ-ॿ\w]", "", w)
        out.append((w, core in acc and core != ""))
    return out
