#!/usr/bin/env python3
"""Code-drawn ink-sketch illustrations for its_poetogram v6 (cream paper, black ink, ONE red object).
Each scene returns SVG (1080x1920); drawing lives in the lower ~55% so the text sits on empty paper above.
Wobbly hand-drawn line via feTurbulence + feDisplacementMap; hatching via clipped line patterns.
Usage: python3 tools/sketch.py SCENE out.png [seed]"""
import sys, math, random, os
from playwright.sync_api import sync_playwright

W, H = 1080, 1920
INK, RED, PAPER = "#1d1a16", "#a3161c", "#efe6d2"

def defs(seed):
    return f"""<defs>
<filter id="ink" x="-5%" y="-5%" width="110%" height="110%"><feTurbulence type="fractalNoise" baseFrequency="0.035" numOctaves="2" seed="{seed}"/>
<feDisplacementMap in="SourceGraphic" scale="5"/></filter>
<filter id="wash" x="-10%" y="-10%" width="120%" height="120%"><feTurbulence type="fractalNoise" baseFrequency="0.02" numOctaves="3" seed="{seed+3}"/>
<feDisplacementMap in="SourceGraphic" scale="14"/><feGaussianBlur stdDeviation="1.2"/></filter>
<filter id="paper"><feTurbulence type="fractalNoise" baseFrequency=".8" numOctaves="3" seed="{seed+9}"/>
<feColorMatrix values="0 0 0 0 .45 0 0 0 0 .38 0 0 0 0 .28 0 0 0 .10 0"/></filter>
<filter id="blot"><feTurbulence type="fractalNoise" baseFrequency=".006" numOctaves="2" seed="{seed+5}"/>
<feColorMatrix values="0 0 0 0 .55 0 0 0 0 .45 0 0 0 0 .30 0 0 0 .5 -.18"/></filter>
<pattern id="hatch" width="9" height="9" patternUnits="userSpaceOnUse" patternTransform="rotate(40)"><line x1="0" y1="0" x2="0" y2="9" stroke="{INK}" stroke-width="1.6"/></pattern>
<pattern id="hatch2" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(-50)"><line x1="0" y1="0" x2="0" y2="8" stroke="{INK}" stroke-width="1.4"/></pattern>
<pattern id="rhatch" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(35)"><line x1="0" y1="0" x2="0" y2="7" stroke="{RED}" stroke-width="2"/></pattern>
</defs>"""

def paper():
    return (f'<rect width="{W}" height="{H}" fill="{PAPER}"/><rect width="{W}" height="{H}" filter="url(#blot)"/>'
            f'<rect width="{W}" height="{H}" filter="url(#paper)"/>')

def stroke(d, w=4, col=INK, op=1, fill="none"):
    return f'<path d="{d}" fill="{fill}" stroke="{col}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round" opacity="{op}"/>'

def scribble_lines(r, x0, y0, x1, y1, n, w=2, ang=40, col=INK, op=.8):
    s = []
    for i in range(n):
        t = i / max(1, n - 1); x = x0 + (x1 - x0) * t; y = y0 + (y1 - y0) * t
        L = r.uniform(18, 40); a = math.radians(ang)
        s.append(stroke(f"M{x:.0f},{y:.0f} l{L*math.cos(a):.0f},{L*math.sin(a):.0f}", w, col, op))
    return "".join(s)

def rain(r, n=170, y0=1000, y1=1850, x0=30, x1=1050):
    return "".join(stroke(f"M{(x:=r.uniform(x0,x1)):.0f},{(y:=r.uniform(y0,y1)):.0f} l-8,{r.uniform(26,48):.0f}", 1.6, INK, r.uniform(.25,.6)) for _ in range(n))

def person_stand(x, base, sc=1.0, facing=1, hood=True, arm_up=False, hatch="hatch"):
    """standing figure, feet at (x, base); returns svg. facing 1 = right."""
    f = facing; s = sc
    def P(dx, dy): return f"{x + dx*s*f:.0f},{base + dy*s:.0f}"
    head = f'<circle cx="{x + 4*s*f:.0f}" cy="{base-300*s:.0f}" r="{26*s:.0f}" fill="{PAPER}" stroke="{INK}" stroke-width="{4*s:.1f}"/>'
    hair = stroke(f"M{P(-24,-306)} Q{P(-8,-340)} {P(26,-318)} Q{P(8,-328)} {P(-20,-300)} Z", 3*s, INK, 1, INK)
    body = stroke(f"M{P(-30,-262)} Q{P(-44,-180)} {P(-34,-128)} L{P(36,-128)} Q{P(44,-200)} {P(28,-262)} Q{P(0,-276)} {P(-30,-262)} Z", 4*s, INK, 1, f"url(#{hatch})")
    if hood: body += stroke(f"M{P(-28,-262)} Q{P(-36,-300)} {P(-14,-318)}", 4*s)
    legs = (stroke(f"M{P(-22,-130)} L{P(-26,-8)} L{P(-4,-4)} L{P(-2,-128)}", 4*s, INK, 1, PAPER)
            + stroke(f"M{P(4,-130)} L{P(14,-8)} L{P(38,-4)} L{P(28,-128)}", 4*s, INK, 1, PAPER)
            + stroke(f"M{P(-28,-2)} L{P(0,-2)} M{P(12,-2)} L{P(44,-2)}", 6*s))
    arm = stroke(f"M{P(20,-250)} Q{P(70,-230)} {P(82,-300)}", 5*s) if arm_up else stroke(f"M{P(22,-250)} Q{P(40,-200)} {P(30,-150)}", 5*s)
    return legs + body + arm + head + hair

def person_small(x, base, sc, r, facing=1, fill="hatch2"):
    f = facing; s = sc
    def P(dx, dy): return f"{x + dx*s*f:.0f},{base + dy*s:.0f}"
    return (stroke(f"M{P(-18,-130)} L{P(-20,-4)} M{P(14,-130)} L{P(18,-4)}", 4*s)
            + stroke(f"M{P(-26,-250)} Q{P(-38,-180)} {P(-28,-126)} L{P(30,-126)} Q{P(38,-190)} {P(24,-250)} Q{P(0,-262)} {P(-26,-250)} Z", 3.5*s, INK, 1, f"url(#{fill})")
            + f'<circle cx="{x:.0f}" cy="{base-282*s:.0f}" r="{24*s:.0f}" fill="{PAPER}" stroke="{INK}" stroke-width="{3.5*s:.1f}"/>'
            + stroke(f"M{P(-22,-288)} Q{P(0,-318)} {P(24,-290)}", 6*s))

# ---------------- scenes ----------------
def sc_umbrella(r):
    g = [rain(r)]
    gx = 640; base = 1720
    # group under umbrella
    for i, (dx, sc, fc) in enumerate([(-120, .92, 1), (-40, 1.0, -1), (50, .95, 1), (130, .9, -1)]):
        g.append(person_small(gx + dx, base - i % 2 * 6, sc, r, fc, "hatch2" if i % 2 else "hatch"))
    # umbrella held by the lone man at left, he stands outside it
    mx = 300
    g.append(person_stand(mx, base + 4, 1.05, 1, True, True))
    hx, hy = mx + 86, base - 318          # hand
    cx, cy = 640, 1250                   # canopy centre
    g.append(stroke(f"M{hx},{hy} L{cx-10},{cy+10}", 5))
    canopy = f"M{cx-300},{cy+70} Q{cx-260},{cy-150} {cx},{cy-170} Q{cx+260},{cy-150} {cx+300},{cy+70} Q{cx+225},{cy+40} {cx+150},{cy+70} Q{cx+75},{cy+40} {cx},{cy+70} Q{cx-75},{cy+40} {cx-150},{cy+70} Q{cx-225},{cy+40} {cx-300},{cy+70} Z"
    g.append(f'<path d="{canopy}" fill="{RED}" opacity=".88" filter="url(#wash)"/>')
    g.append(f'<path d="{canopy}" fill="url(#rhatch)" opacity=".35"/>')
    g.append(stroke(canopy, 4))
    for k in (-150, 0, 150): g.append(stroke(f"M{cx},{cy-170} Q{cx+k*.6},{cy-60} {cx+k},{cy+70}", 2.5))
    g.append(stroke(f"M{cx},{cy-170} l0,-26", 5))
    # dry ground under group, puddles near him
    g.append(stroke(f"M80,{base+2} L1000,{base+2}", 3, INK, .7))
    for px in (220, 360):
        g.append(f'<ellipse cx="{px}" cy="{base+26}" rx="70" ry="9" fill="none" stroke="{INK}" stroke-width="2" opacity=".6"/>')
    g.append(scribble_lines(r, 230, 1430, 370, 1470, 12, 2, 70, INK, .5))  # rain hitting his shoulders
    return "".join(g)

def sc_phone(r):
    g = []
    # window with crescent moon
    wx, wy = 640, 1060
    g.append(stroke(f"M{wx},{wy} L{wx+300},{wy} L{wx+300},{wy+360} L{wx},{wy+360} Z M{wx+150},{wy} L{wx+150},{wy+360} M{wx},{wy+180} L{wx+300},{wy+180}", 5))
    g.append(f'<path d="M{wx+5},{wy+5} h290 v350 h-290 Z" fill="url(#hatch)" opacity=".55"/>')
    g.append(f'<circle cx="{wx+215}" cy="{wy+80}" r="38" fill="{PAPER}"/><circle cx="{wx+232}" cy="{wy+68}" r="34" fill="url(#hatch)"/>')
    # bed
    by = 1620
    g.append(stroke(f"M120,{by} L980,{by} L980,{by+90} L120,{by+90} Z", 5, INK, 1, PAPER))
    g.append(stroke(f"M120,{by+90} L120,{by+190} M980,{by+90} L980,{by+190}", 6))
    g.append(scribble_lines(r, 140, by + 60, 960, by + 60, 40, 1.8, 20, INK, .45))
    # phone glow (red) on the sheet + phone face down
    px, py = 640, by - 6
    g.append(f'<ellipse cx="{px}" cy="{py+8}" rx="120" ry="26" fill="{RED}" opacity=".55" filter="url(#wash)"/>')
    g.append(stroke(f"M{px-46},{py-6} L{px+46},{py-6} L{px+52},{py+8} L{px-52},{py+8} Z", 4, INK, 1, INK))
    # man sitting on bed edge, seen from behind, elbows on knees, head bowed
    mx, my = 360, by
    g.append(stroke(f"M{mx-70},{my-10} Q{mx-80},{my-150} {mx-40},{my-250} Q{mx},{my-280} {mx+40},{my-250} Q{mx+80},{my-150} {mx+70},{my-10} Z", 5, INK, 1, "url(#hatch)"))
    g.append(stroke(f"M{mx-38},{my-250} Q{mx},{my-268} {mx+38},{my-250}", 4))
    g.append(f'<circle cx="{mx+6}" cy="{my-290}" r="40" fill="{PAPER}" stroke="{INK}" stroke-width="5"/>')
    g.append(stroke(f"M{mx-34},{my-300} Q{mx+6},{my-350} {mx+46},{my-296} Q{mx+6},{my-318} {mx-34},{my-300} Z", 3, INK, 1, INK))
    g.append(stroke(f"M{mx-60},{my-190} Q{mx-110},{my-110} {mx-60},{my-60} M{mx+60},{my-190} Q{mx+110},{my-110} {mx+60},{my-60}", 5))
    g.append(stroke(f"M{mx-70},{my-4} L{mx-70},{my+180} M{mx+70},{my-4} L{mx+70},{my+180}", 6))
    # floor
    g.append(stroke(f"M60,{by+192} L1020,{by+192}", 3, INK, .7))
    return "".join(g)

def sc_tape(r):
    g = []
    cx, base = 520, 1700
    # loops of red tape around him
    for i in range(7):
        rx = 240 + i * 26 + r.uniform(-10, 10); ry = 120 + i * 30; cy = 1440 - i * 18
        rot = r.uniform(-18, 18)
        g.append(f'<ellipse cx="{cx+r.uniform(-20,20):.0f}" cy="{cy:.0f}" rx="{rx:.0f}" ry="{ry:.0f}" fill="none" stroke="{RED}" stroke-width="{r.uniform(3,5):.1f}" opacity=".85" transform="rotate({rot:.0f} {cx} {cy:.0f})" filter="url(#wash)"/>')
    # man sitting on floor hugging knees (side view)
    def P(dx, dy): return f"{cx+dx:.0f},{base+dy:.0f}"
    g.append(stroke(f"M{P(-110,0)} Q{P(-130,-120)} {P(-90,-230)} Q{P(-60,-260)} {P(-20,-240)} L{P(30,-110)} L{P(-40,0)} Z", 5, INK, 1, "url(#hatch)"))  # back/torso
    g.append(stroke(f"M{P(-40,-4)} L{P(60,-170)} L{P(100,-170)} L{P(110,0)}", 6, INK, 1, PAPER))   # legs/knees
    g.append(stroke(f"M{P(-40,-170)} Q{P(40,-200)} {P(80,-150)}", 6))                              # arm around knees
    g.append(f'<circle cx="{cx-40}" cy="{base-285}" r="42" fill="{PAPER}" stroke="{INK}" stroke-width="5"/>')
    g.append(stroke(f"M{P(-80,-290)} Q{P(-50,-345)} {P(0,-300)} Q{P(-40,-318)} {P(-80,-290)} Z", 3, INK, 1, INK))
    # cassette on floor
    kx, ky = cx + 230, base - 40
    g.append(stroke(f"M{kx},{ky} l150,0 l0,80 l-150,0 Z", 4, INK, 1, PAPER))
    g.append(f'<circle cx="{kx+45}" cy="{ky+38}" r="16" fill="none" stroke="{INK}" stroke-width="3"/><circle cx="{kx+105}" cy="{ky+38}" r="16" fill="none" stroke="{INK}" stroke-width="3"/>')
    g.append(stroke(f"M{kx+45},{ky+80} Q{kx-40},{ky+150} {cx},{base+40} Q{cx-300},{base+10} {cx-260},{base-120}", 4, RED, .9))
    g.append(stroke(f"M60,{base+2} L1020,{base+2}", 3, INK, .7))
    return "".join(g)

SCENES = {"umbrella": sc_umbrella, "phone": sc_phone, "tape": sc_tape}

def render(scene, out, seed=11):
    r = random.Random(seed)
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}">{defs(seed)}{paper()}<g filter="url(#ink)">{SCENES[scene](r)}</g></svg>'
    with sync_playwright() as pw:
        b = pw.chromium.launch(); pg = b.new_page(viewport={"width": W, "height": H})
        pg.set_content(f'<html><body style="margin:0">{svg}</body></html>'); pg.wait_for_timeout(200)
        pg.screenshot(path=out); b.close()

if __name__ == "__main__":
    render(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 11)
