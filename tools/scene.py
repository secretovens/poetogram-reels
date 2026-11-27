"""Colourful flat-illustration scene kit for its_poetogram (all original, drawn in code).
A scene = sky + place + people + props, described by a small spec in content.json:
  "scene": {"sky": "golden", "place": "rooftop", "people": [{"who": "man", "pose": "sit", "x": 0.42, "shirt": "#2f6f8f"}, ...],
            "props": ["chai", "kite"], "seed": 4}
sky:   golden | sunrise | dusk | night | rain | day | pink
place: rooftop | city | room | office | park | street | village | station | kitchen | balcony
who:   man | woman | oldman | oldwoman | kid | girl     pose: stand | sit | back | walk
props: chai kite phone laptop swing lamp plant moon birds lights clock suitcase scooter train umbrella books tiffin flowers stars
The upper ~45% stays open sky/wall for the text."""
import math, random

SKIES = {
    "golden":  ["#e9845a", "#f4a06a", "#f78c6b", "#e0607e"],
    "sunrise": ["#6fa8d6", "#b9cfe0", "#ffc8a2", "#ffb08a"],
    "dusk":    ["#3a3a7c", "#7b4f9d", "#d9739b", "#ffb38a"],
    "night":   ["#0e1b3d", "#1d2f63", "#33417a", "#4b4f8c"],
    "rain":    ["#4f6b80", "#6f889a", "#97aab8", "#b9c7d1"],
    "day":     ["#2f8fd0", "#5fb0e6", "#a7d8f5", "#e4f3f8"],
    "pink":    ["#e8728f", "#f29aa8", "#ffb3a7", "#ffd9b3"],
}
SKIN = ["#c98a5b", "#b5764a", "#d9a074", "#a8693f", "#e0b088"]
HAIR = {"young": "#1d1412", "old": "#d9d6d0"}

def _g(rnd, base, spread=12):
    r, g, b = int(base[1:3], 16), int(base[3:5], 16), int(base[5:7], 16)
    f = lambda v: max(0, min(255, v + rnd.randint(-spread, spread)))
    return f"#{f(r):02x}{f(g):02x}{f(b):02x}"

def shade(c, k):
    r, g, b = int(c[1:3], 16), int(c[3:5], 16), int(c[5:7], 16)
    if k < 1: r, g, b = r*k, g*k, b*k
    else: r, g, b = r + (255-r)*(k-1), g + (255-g)*(k-1), b + (255-b)*(k-1)
    return f"#{int(r):02x}{int(g):02x}{int(b):02x}"

class S:
    def __init__(self, W, H, spec):
        self.W, self.H, self.spec = W, H, spec
        self.rnd = random.Random(spec.get("seed", 1))
        self.GY = int(H * (0.76 if H > 1500 else 0.80))   # ground line
        self.k = 1.4 if H > 1500 else 0.9                 # figure scale for carousels
        self.out = []
        self.dark = spec.get("sky") in ("night", "dusk")

    def add(self, s): self.out.append(s)

    # ---------------- sky ----------------
    def sky(self):
        W, H = self.W, self.H; c = SKIES[self.spec.get("sky", "golden")]
        stops = "".join(f'<stop offset="{i/(len(c)-1):.2f}" stop-color="{col}"/>' for i, col in enumerate(c))
        self.add(f'<defs><linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">{stops}</linearGradient>'
                 f'<radialGradient id="glow" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#fff6d8" stop-opacity=".9"/><stop offset="1" stop-color="#fff6d8" stop-opacity="0"/></radialGradient></defs>'
                 f'<rect width="{W}" height="{H}" fill="url(#sky)"/>')
        sk = self.spec.get("sky", "golden")
        if sk in ("golden", "sunrise", "pink", "dusk"):
            sx, sy = self.rnd.randint(int(W*.2), int(W*.8)), self.GY - int(self.H*.07)
            self.add(f'<circle cx="{sx}" cy="{sy}" r="{int(W*.42)}" fill="url(#glow)" opacity=".7"/>'
                     f'<circle cx="{sx}" cy="{sy}" r="{int(W*.11)}" fill="#fff3cf" opacity=".95"/>')
        if sk in ("night", "dusk"):
            for _ in range(90 if sk == "night" else 35):
                self.add(f'<circle cx="{self.rnd.uniform(0,W):.0f}" cy="{self.rnd.uniform(0,self.GY*.7):.0f}" r="{self.rnd.choice([1,1.4,2,2.6])}" fill="#fff" opacity="{self.rnd.uniform(.3,.9):.2f}"/>')
        if sk == "night" or "moon" in self.spec.get("props", []):
            mx, my = self.rnd.choice([int(W*.2), int(W*.8)]), int(self.H*.56)
            self.add(f'<circle cx="{mx}" cy="{my}" r="150" fill="url(#glow)" opacity=".35"/><circle cx="{mx}" cy="{my}" r="52" fill="#fff4d6"/>')
        if sk in ("day", "sunrise", "pink", "golden", "rain"):
            for _ in range(4):
                cx, cy, s = self.rnd.uniform(-50, W), self.rnd.uniform(self.H*.42, self.GY*.92), self.rnd.uniform(.7, 1.4)
                col = "#ffffff" if sk != "golden" else "#ffe3c4"
                self.add(f'<g opacity="{.55 if sk!="rain" else .8}" fill="{col}"><ellipse cx="{cx}" cy="{cy}" rx="{110*s:.0f}" ry="{34*s:.0f}"/>'
                         f'<ellipse cx="{cx+60*s:.0f}" cy="{cy-22*s:.0f}" rx="{70*s:.0f}" ry="{36*s:.0f}"/><ellipse cx="{cx-55*s:.0f}" cy="{cy-10*s:.0f}" rx="{55*s:.0f}" ry="{26*s:.0f}"/></g>')
        if sk == "rain":
            for _ in range(160):
                x, y = self.rnd.uniform(0, W), self.rnd.uniform(0, self.H)
                self.add(f'<line x1="{x:.0f}" y1="{y:.0f}" x2="{x-8:.0f}" y2="{y+34:.0f}" stroke="#ffffff" stroke-width="2" opacity=".35"/>')

    # ---------------- places ----------------
    def skyline(self, base, hmin, hmax, col, lit=None, step=(60, 140)):
        x = -20
        while x < self.W:
            w = self.rnd.randint(*step); h = self.rnd.randint(hmin, hmax)
            self.add(f'<rect x="{x}" y="{base-h}" width="{w}" height="{h+5}" fill="{col}"/>')
            if self.rnd.random() < .35:  # water tank
                self.add(f'<rect x="{x+w*.3:.0f}" y="{base-h-26}" width="{w*.3:.0f}" height="26" rx="6" fill="{col}"/>')
            if lit:
                for wy in range(base-h+18, base-10, 30):
                    for wx in range(x+10, x+w-14, 24):
                        if self.rnd.random() < .3: self.add(f'<rect x="{wx}" y="{wy}" width="10" height="14" fill="{lit}" opacity=".85"/>')
            x += w + self.rnd.randint(-6, 8)

    def place(self):
        W, H, GY = self.W, self.H, self.GY; p = self.spec.get("place", "rooftop"); sk = self.spec.get("sky", "golden")
        far = {"golden": "#c9707a", "sunrise": "#d9a6a0", "dusk": "#5a3b74", "night": "#1a2550", "rain": "#7d93a3", "day": "#9fc3d6", "pink": "#e6a3a8"}[sk]
        near = shade(far, .72)
        lit = "#ffd27a" if sk in ("night", "dusk", "golden") else None
        if p in ("rooftop", "city", "balcony", "street"):
            self.skyline(GY - 60, 120, 380, far, lit)
            self.skyline(GY + 10, 60, 220, near, lit, (90, 180))
        if p == "rooftop":
            wall = shade(near, 1.3) if not self.dark else shade(near, 1.15)
            self.add(f'<rect x="0" y="{GY-8}" width="{W}" height="42" fill="{shade(wall,1.15)}"/>'
                     f'<rect x="0" y="{GY+34}" width="{W}" height="{H-GY}" fill="{wall}"/><rect x="0" y="{GY+34}" width="{W}" height="12" fill="{shade(wall,.8)}"/>')
            for r, y in enumerate(range(GY + 46, H, 56)):
                self.add(f'<line x1="0" y1="{y}" x2="{W}" y2="{y}" stroke="{shade(wall,.85)}" stroke-width="3"/>')
                for x in range(-60 + 60*(r % 2), W, 120): self.add(f'<line x1="{x}" y1="{y}" x2="{x}" y2="{y+56}" stroke="{shade(wall,.85)}" stroke-width="3"/>')
            self.seat_y = GY - 8
        elif p == "balcony":
            self.add(f'<rect x="0" y="{GY+40}" width="{W}" height="{H-GY}" fill="{shade(near,.8)}"/>')
            for x in range(10, W, 46): self.add(f'<rect x="{x}" y="{GY-70}" width="10" height="120" fill="#3b2b2b" opacity=".85"/>')
            self.add(f'<rect x="0" y="{GY-80}" width="{W}" height="16" fill="#3b2b2b"/>')
            self.seat_y = GY + 40
        elif p in ("city", "street"):
            road = "#3a3a46" if self.dark else "#6e6a78"
            self.add(f'<rect x="0" y="{GY}" width="{W}" height="{H-GY}" fill="{road}"/>')
            for x in range(-40, W, 160): self.add(f'<rect x="{x}" y="{GY+90}" width="80" height="10" fill="#f2e6c8" opacity=".7"/>')
            self.seat_y = GY
        elif p == "park":
            hill = {"night": "#1f3b3a", "dusk": "#3e4f5c"}.get(sk, "#7fb069")
            self.add(f'<path d="M0,{GY-40} C{W*.3},{GY-120} {W*.6},{GY+10} {W},{GY-70} L{W},{H} L0,{H} Z" fill="{shade(hill,.85)}"/>'
                     f'<rect x="0" y="{GY}" width="{W}" height="{H-GY}" fill="{hill}"/>')
            for _ in range(3): self.tree(self.rnd.uniform(40, W-40), GY + 5, self.rnd.uniform(.8, 1.3))
            self.seat_y = GY
        elif p == "village":
            fld = {"night": "#22402f", "dusk": "#4a5a3a"}.get(sk, "#c9b458")
            self.add(f'<path d="M0,{GY-60} Q{W*.5},{GY-150} {W},{GY-50} L{W},{H} L0,{H} Z" fill="{shade(fld,.8)}"/><rect x="0" y="{GY}" width="{W}" height="{H-GY}" fill="{fld}"/>')
            self.hut(W*.72, GY, 1.0); self.tree(W*.15, GY, 1.2)
            self.seat_y = GY
        elif p == "station":
            self.add(f'<rect x="0" y="{GY}" width="{W}" height="{H-GY}" fill="#b9a68f"/><rect x="0" y="{GY}" width="{W}" height="14" fill="#f2d14b"/>')
            self.add(f'<rect x="0" y="{GY-520}" width="{W}" height="26" fill="#7a4b3a"/>')
            for x in (120, W-120): self.add(f'<rect x="{x-10}" y="{GY-500}" width="20" height="500" fill="#7a4b3a"/>')
            self.seat_y = GY
        elif p in ("room", "office", "kitchen"):
            wallc = self.rnd.choice(["#c46a4f", "#2f6f73", "#5c4d7d", "#c8843a", "#3f6e8c", "#8c4f6b"])
            if self.dark: wallc = shade(wallc, .62)
            floor = {"room": "#b9825a", "office": "#8d99a6", "kitchen": "#c49a6c"}[p]
            # window showing the sky (sky already painted behind) → paint wall around a window
            wx0, wy0, ww, wh = int(W*.18), int(H*.52), int(W*.64), int(GY - H*.52 - 110)
            self.add(f'<path d="M0,0 H{W} V{H} H0 Z M{wx0},{wy0} V{wy0+wh} H{wx0+ww} V{wy0} Z" fill="{wallc}" fill-rule="evenodd"/>')
            self.add(f'<rect x="{wx0-14}" y="{wy0-14}" width="{ww+28}" height="{wh+28}" fill="none" stroke="#7b5a43" stroke-width="18"/>'
                     f'<line x1="{wx0+ww/2}" y1="{wy0}" x2="{wx0+ww/2}" y2="{wy0+wh}" stroke="#7b5a43" stroke-width="10"/>'
                     f'<rect x="{wx0-40}" y="{wy0+wh+10}" width="{ww+80}" height="20" fill="#7b5a43"/>')
            # curtains
            for cx, d in ((wx0 - 30, 1), (wx0 + ww + 30, -1)):
                self.add(f'<path d="M{cx},{wy0-40} q{60*d},{wh*.5} {10*d},{wh+60} l{-40*d},0 q{-30*d},{-wh*.5} 0,{-wh-60} z" fill="#d96c5f" opacity=".9"/>')
            self.add(f'<rect x="0" y="{GY}" width="{W}" height="{H-GY}" fill="{floor}"/>')
            if p == "office":
                self.add(f'<rect x="{W*.12:.0f}" y="{GY-150}" width="{W*.76:.0f}" height="22" fill="#5b4636"/><rect x="{W*.16:.0f}" y="{GY-128}" width="18" height="128" fill="#5b4636"/><rect x="{W*.82:.0f}" y="{GY-128}" width="18" height="128" fill="#5b4636"/>')
                self.desk_y = GY - 150
            if p == "kitchen":
                self.add(f'<rect x="0" y="{GY-170}" width="{W}" height="170" fill="#a8784f"/><rect x="0" y="{GY-190}" width="{W}" height="24" fill="#d8c3a5"/>')
                self.desk_y = GY - 190
            self.seat_y = GY
        else:
            self.add(f'<rect x="0" y="{GY}" width="{W}" height="{H-GY}" fill="{near}"/>'); self.seat_y = GY

    def tree(self, x, base, s):
        c = "#2f6b4f" if not self.dark else "#1d3b35"
        self.add(f'<rect x="{x-9*s:.0f}" y="{base-150*s:.0f}" width="{18*s:.0f}" height="{150*s:.0f}" fill="#6b4a33"/>'
                 f'<circle cx="{x:.0f}" cy="{base-190*s:.0f}" r="{80*s:.0f}" fill="{c}"/><circle cx="{x-55*s:.0f}" cy="{base-150*s:.0f}" r="{55*s:.0f}" fill="{shade(c,1.15)}"/>'
                 f'<circle cx="{x+55*s:.0f}" cy="{base-155*s:.0f}" r="{58*s:.0f}" fill="{shade(c,.9)}"/>')

    def hut(self, x, base, s):
        self.add(f'<rect x="{x-90*s:.0f}" y="{base-130*s:.0f}" width="{180*s:.0f}" height="{130*s:.0f}" fill="#e8c49a"/>'
                 f'<path d="M{x-120*s:.0f},{base-125*s:.0f} L{x:.0f},{base-230*s:.0f} L{x+120*s:.0f},{base-125*s:.0f} Z" fill="#a0522d"/>'
                 f'<rect x="{x-22*s:.0f}" y="{base-80*s:.0f}" width="{44*s:.0f}" height="{80*s:.0f}" fill="#6b3b22"/>'
                 f'<rect x="{x+40*s:.0f}" y="{base-95*s:.0f}" width="{30*s:.0f}" height="{30*s:.0f}" fill="#ffd27a"/>')

    # ---------------- people (flat, faceless editorial style) ----------------
    def person(self, d):
        rnd = self.rnd; k = self.k * d.get("scale", 1.0)
        who = d.get("who", "man"); pose = d.get("pose", "stand")
        x = d.get("x", .5) * self.W
        old = who.startswith("old"); kid = who in ("kid", "girl")
        fem = who in ("woman", "oldwoman", "girl")
        sz = (0.62 if kid else 1.0) * k
        skin = d.get("skin", SKIN[rnd.randrange(len(SKIN))])
        shirt = d.get("shirt", rnd.choice(["#2f6f8f", "#e07a5f", "#3d405b", "#81b29a", "#f2cc8f", "#9b5de5", "#e63946", "#277da1"]))
        pants = d.get("pants", "#2b2d42" if not old else "#e9e4d8")
        hair = d.get("hair", HAIR["old"] if old else HAIR["young"])
        base = self.seat_y if pose == "sit" else (self.GY + (60 if self.spec.get("place") in ("rooftop",) else 30))
        if pose != "sit" and self.spec.get("place") in ("room", "office", "kitchen", "city", "street", "station", "park", "village"): base = self.GY + 40
        g = []
        hr = 34 * sz                          # head radius
        if pose == "sit":
            hip = base; sh = hip - 150 * sz; hy = sh - hr - 12 * sz
            # legs hanging forward
            g.append(f'<path d="M{x-28*sz:.0f},{hip:.0f} h{56*sz:.0f} l{14*sz:.0f},{110*sz:.0f} h-{26*sz:.0f} l-{8*sz:.0f},-{70*sz:.0f} l-{8*sz:.0f},{70*sz:.0f} h-{26*sz:.0f} z" fill="{pants}"/>')
            g.append(f'<ellipse cx="{x-24*sz:.0f}" cy="{hip+114*sz:.0f}" rx="{18*sz:.0f}" ry="{8*sz:.0f}" fill="#2a1d18"/><ellipse cx="{x+24*sz:.0f}" cy="{hip+114*sz:.0f}" rx="{18*sz:.0f}" ry="{8*sz:.0f}" fill="#2a1d18"/>')
        else:
            hip = base - 170 * sz; sh = hip - 150 * sz; hy = sh - hr - 12 * sz
            step = 26 * sz if pose == "walk" else 0
            if fem and who != "girl":   # saree / long kurta
                g.append(f'<path d="M{x-46*sz:.0f},{hip-10*sz:.0f} L{x+46*sz:.0f},{hip-10*sz:.0f} L{x+62*sz:.0f},{base:.0f} L{x-62*sz:.0f},{base:.0f} Z" fill="{shirt}"/>')
                g.append(f'<path d="M{x-62*sz:.0f},{base-24*sz:.0f} L{x+62*sz:.0f},{base-24*sz:.0f} L{x+62*sz:.0f},{base:.0f} L{x-62*sz:.0f},{base:.0f} Z" fill="{shade(shirt,.7)}"/>')
            else:
                g.append(f'<path d="M{x-30*sz:.0f},{hip:.0f} h{60*sz:.0f} l{4*sz+step:.0f},{170*sz:.0f} h-{28*sz:.0f} l-{6*sz:.0f},-{120*sz:.0f} l-{6*sz:.0f},{120*sz:.0f} h-{28*sz:.0f} z" fill="{pants}"/>')
                g.append(f'<ellipse cx="{x-18*sz-step/2:.0f}" cy="{base:.0f}" rx="{20*sz:.0f}" ry="{8*sz:.0f}" fill="#2a1d18"/><ellipse cx="{x+18*sz+step:.0f}" cy="{base:.0f}" rx="{20*sz:.0f}" ry="{8*sz:.0f}" fill="#2a1d18"/>')
        # torso
        bend = 10 * sz if old else 0
        g.append(f'<path d="M{x-44*sz:.0f},{sh+18*sz:.0f} Q{x-48*sz:.0f},{sh-4*sz:.0f} {x-20*sz+bend:.0f},{sh-6*sz:.0f} L{x+20*sz+bend:.0f},{sh-6*sz:.0f} Q{x+48*sz:.0f},{sh-4*sz:.0f} {x+44*sz:.0f},{sh+18*sz:.0f} L{x+40*sz:.0f},{hip+(14 if fem else 6)*sz:.0f} L{x-40*sz:.0f},{hip+(14 if fem else 6)*sz:.0f} Z" fill="{shirt}"/>')
        if fem and who != "girl":   # pallu
            g.append(f'<path d="M{x+30*sz:.0f},{sh-4*sz:.0f} L{x-40*sz:.0f},{hip:.0f} L{x-26*sz:.0f},{hip+8*sz:.0f} L{x+42*sz:.0f},{sh+10*sz:.0f} Z" fill="{shade(shirt,1.35)}" opacity=".9"/>')
        # arms
        arm = d.get("arm", "lap" if pose == "sit" else "down")
        ends = {"down": ((-50, 135), (50, 135)), "lap": ((-18, 125), (18, 125)), "shoulder": ((-50, 135), (110, 0)),
                "phone": ((-50, 135), (30, 55)), "up": ((-50, 135), (60, -70))}[arm]
        for sgn, (ex, ey) in zip((-1, 1), ends):
            sx0, sy0 = x + sgn*38*sz, sh + 10*sz
            g.append(f'<path d="M{sx0:.0f},{sy0:.0f} Q{sx0+sgn*12*sz:.0f},{sy0+ey*sz*.55:.0f} {x+ex*sz:.0f},{sh+ey*sz:.0f}" fill="none" stroke="{shirt}" stroke-width="{24*sz:.0f}" stroke-linecap="round"/>'
                     f'<circle cx="{x+ex*sz:.0f}" cy="{sh+ey*sz:.0f}" r="{11*sz:.0f}" fill="{skin}"/>')
        if arm == "phone":
            g.append(f'<rect x="{x+20*sz:.0f}" y="{sh+40*sz:.0f}" width="{22*sz:.0f}" height="{38*sz:.0f}" rx="4" fill="#222"/><rect x="{x+23*sz:.0f}" y="{sh+44*sz:.0f}" width="{16*sz:.0f}" height="{28*sz:.0f}" fill="#9ad1ff"/>')
        # neck + head
        g.append(f'<rect x="{x-9*sz:.0f}" y="{hy+hr-6*sz:.0f}" width="{18*sz:.0f}" height="{22*sz:.0f}" fill="{shade(skin,.85)}"/>')
        g.append(f'<circle cx="{x+bend:.0f}" cy="{hy:.0f}" r="{hr:.0f}" fill="{skin}"/>')
        back = pose == "back" or d.get("back")
        if back:
            g.append(f'<path d="M{x+bend-hr:.0f},{hy+4*sz:.0f} a{hr:.0f},{hr:.0f} 0 0 1 {2*hr:.0f},0 q0,{18*sz:.0f} -{6*sz:.0f},{24*sz:.0f} h-{2*hr-12*sz:.0f} q-{6*sz:.0f},-{6*sz:.0f} -{6*sz:.0f},-{24*sz:.0f} z" fill="{hair}"/>')
        else:
            g.append(f'<path d="M{x+bend-hr-2:.0f},{hy+2:.0f} a{hr+2:.0f},{hr+2:.0f} 0 0 1 {2*hr+4:.0f},0 q-{hr*.9:.0f},-{hr*.35:.0f} -{2*hr+4:.0f},0 z" fill="{hair}"/>')
        if fem:
            if who in ("woman", "oldwoman"):
                g.append(f'<circle cx="{x+bend+hr*.8:.0f}" cy="{hy-hr*.1:.0f}" r="{hr*.45:.0f}" fill="{hair}"/>')   # bun
                if not back: g.append(f'<circle cx="{x+bend:.0f}" cy="{hy-hr*.15:.0f}" r="{3*sz:.0f}" fill="#c1121f"/>')  # bindi
            else:
                g.append(f'<path d="M{x-hr:.0f},{hy:.0f} q-{8*sz:.0f},{40*sz:.0f} {6*sz:.0f},{60*sz:.0f} M{x+hr:.0f},{hy:.0f} q{8*sz:.0f},{40*sz:.0f} -{6*sz:.0f},{60*sz:.0f}" stroke="{hair}" stroke-width="{14*sz:.0f}" fill="none" stroke-linecap="round"/>')
        if old and not back:
            g.append(f'<g fill="none" stroke="#2a1d18" stroke-width="{3*sz:.1f}"><circle cx="{x+bend-12*sz:.0f}" cy="{hy+2:.0f}" r="{9*sz:.0f}"/><circle cx="{x+bend+12*sz:.0f}" cy="{hy+2:.0f}" r="{9*sz:.0f}"/><line x1="{x+bend-3*sz:.0f}" y1="{hy+2:.0f}" x2="{x+bend+3*sz:.0f}" y2="{hy+2:.0f}"/></g>')
            if who == "oldman": g.append(f'<path d="M{x+bend-14*sz:.0f},{hy+16*sz:.0f} q{14*sz:.0f},{8*sz:.0f} {28*sz:.0f},0" stroke="{hair}" stroke-width="{6*sz:.0f}" fill="none" stroke-linecap="round"/>')
        # soft ground shadow
        if pose != "sit":
            self.add(f'<ellipse cx="{x:.0f}" cy="{base+4:.0f}" rx="{70*sz:.0f}" ry="{12*sz:.0f}" fill="#000" opacity=".18"/>')
        self.add("".join(g))

    # ---------------- props ----------------
    def props(self):
        W, H, GY = self.W, self.H, self.GY; rnd = self.rnd
        ppl = self.spec.get("people", [])
        px = [p.get("x", .5) * W for p in ppl] or [W * .5]
        for pr in self.spec.get("props", []):
            if pr == "chai":
                cx = sum(px) / len(px); y = getattr(self, "desk_y", self.seat_y)
                for dx in (-22, 22):
                    self.add(f'<path d="M{cx+dx-14:.0f},{y-40} l4,38 h20 l4,-38 z" fill="#f6e7c8" opacity=".85"/><rect x="{cx+dx-11:.0f}" y="{y-26}" width="22" height="22" fill="#b5652b" opacity=".9"/>')
                    self.add(f'<path d="M{cx+dx-4:.0f},{y-48} q-8,-16 2,-30 q8,-12 0,-26" stroke="#fff" stroke-width="3" fill="none" opacity=".6"/>')
            elif pr == "kite":
                kx, ky = rnd.uniform(W*.6, W*.85), H * .47
                self.add(f'<path d="M{kx},{ky-60} l45,60 l-45,70 l-45,-70 z" fill="#e63946"/><path d="M{kx},{ky-60} l45,60 l-45,0 z" fill="#ffd166"/>'
                         f'<path d="M{kx},{ky+70} q-30,60 10,110 q30,40 -10,80" stroke="#e63946" stroke-width="5" fill="none"/>'
                         f'<path d="M{kx},{ky+10} Q{W*.5},{GY-200} {px[0]+30:.0f},{GY-300}" stroke="#fff" stroke-width="2" fill="none" opacity=".8" stroke-dasharray="6 8"/>')
            elif pr == "birds":
                for _ in range(5):
                    bx, by, s = rnd.uniform(W*.1, W*.9), rnd.uniform(H*.45, H*.6), rnd.uniform(.6, 1.2)
                    self.add(f'<path d="M{bx-16*s:.0f},{by:.0f} q{8*s:.0f},-{10*s:.0f} {16*s:.0f},0 q{8*s:.0f},-{10*s:.0f} {16*s:.0f},0" stroke="{"#fff" if self.dark else "#3b2b3b"}" stroke-width="3" fill="none"/>')
            elif pr == "lights":
                y0 = H * .52
                self.add(f'<path d="M0,{y0} Q{W/2},{y0+120} {W},{y0}" stroke="#3b2b2b" stroke-width="2" fill="none"/>')
                for i in range(1, 16):
                    t = i / 16; x = W * t; y = y0 + 120 * 4 * t * (1 - t) * .5 * 2 * .5 * 2
                    self.add(f'<circle cx="{x:.0f}" cy="{y0 + 240*t*(1-t):.0f}" r="9" fill="{rnd.choice(["#ffd166","#ff8fab","#90e0ef","#caffbf"])}"/>')
            elif pr == "laptop":
                y = getattr(self, "desk_y", GY - 150); cx = px[0] + 90
                self.add(f'<path d="M{cx-70},{y} l18,-100 h120 l-6,100 z" fill="#4a4e69"/><path d="M{cx-48},{y-8} l14,-82 h100 l-5,82 z" fill="#bde0fe" opacity=".9"/><rect x="{cx-90}" y="{y-4}" width="190" height="8" fill="#22223b"/>')
            elif pr == "lamp":
                y = getattr(self, "desk_y", GY - 150); cx = px[-1] - 140
                self.add(f'<circle cx="{cx}" cy="{y-110}" r="160" fill="url(#glow)" opacity=".5"/><rect x="{cx-4}" y="{y-110}" width="8" height="110" fill="#333"/><path d="M{cx-40},{y-110} l20,-50 h40 l20,50 z" fill="#ffb703"/>')
            elif pr == "plant":
                x = rnd.choice([W*.1, W*.9]); y = GY + 30
                self.add(f'<path d="M{x-40:.0f},{y} h80 l-12,80 h-56 z" fill="#c8553d"/>')
                for a in range(-60, 61, 30): self.add(f'<path d="M{x:.0f},{y} q{a*1.2:.0f},-90 {a*2:.0f},-150" stroke="#2d6a4f" stroke-width="14" fill="none" stroke-linecap="round"/>')
            elif pr == "clock":
                cx, cy = W * .5, H * .36 if self.spec.get("place") in ("room", "office", "kitchen") else H * .3
                if self.spec.get("place") in ("room", "office", "kitchen"): cx, cy = W * .88, H * .53
                self.add(f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="58" fill="#fff8ec" stroke="#7b5a43" stroke-width="10"/><line x1="{cx:.0f}" y1="{cy:.0f}" x2="{cx:.0f}" y2="{cy-38:.0f}" stroke="#333" stroke-width="6"/><line x1="{cx:.0f}" y1="{cy:.0f}" x2="{cx+28:.0f}" y2="{cy+10:.0f}" stroke="#e63946" stroke-width="5"/>')
            elif pr == "suitcase":
                x = px[-1] + 85; y = self.GY + 40
                self.add(f'<rect x="{x:.0f}" y="{y-110}" width="80" height="110" rx="10" fill="#e76f51"/><rect x="{x+28:.0f}" y="{y-128}" width="24" height="20" rx="5" fill="none" stroke="#6b3b22" stroke-width="6"/>')
            elif pr == "scooter":
                k = self.k; x = px[0] - 230 * k; y = self.GY + 40
                c = "#2a9d8f"
                self.add(f'<g transform="translate({x:.0f},{y}) scale({k})">'
                         f'<circle cx="-70" cy="-34" r="34" fill="#222"/><circle cx="-70" cy="-34" r="14" fill="#999"/>'
                         f'<circle cx="95" cy="-34" r="34" fill="#222"/><circle cx="95" cy="-34" r="14" fill="#999"/>'
                         f'<path d="M-120,-60 Q-118,-150 -40,-150 L20,-150 L40,-70 L130,-70 Q140,-110 110,-130 L100,-130 L80,-230 L60,-230 L80,-130" fill="{c}" stroke="{c}" stroke-width="6" stroke-linejoin="round"/>'
                         f'<path d="M-120,-60 Q-118,-150 -40,-150 L20,-150 L30,-60 Z" fill="{shade(c,.8)}"/>'
                         f'<rect x="-75" y="-172" width="90" height="22" rx="10" fill="#3b2b2b"/>'
                         f'<rect x="50" y="-240" width="60" height="12" rx="6" fill="#333"/><circle cx="90" cy="-215" r="12" fill="#ffe8a3"/></g>')
            elif pr == "swing":
                x = px[0]; top = H * .44
                self.add(f'<line x1="{x-50:.0f}" y1="{top}" x2="{x-50:.0f}" y2="{self.seat_y}" stroke="#6b4a33" stroke-width="5"/><line x1="{x+50:.0f}" y1="{top}" x2="{x+50:.0f}" y2="{self.seat_y}" stroke="#6b4a33" stroke-width="5"/>'
                         f'<rect x="{x-70:.0f}" y="{self.seat_y}" width="140" height="14" fill="#8b5e3c"/>')
            elif pr == "train":
                y = self.GY - 40
                self.add(f'<rect x="-20" y="{y-300}" width="{W+40}" height="300" rx="20" fill="#2a6f97"/><rect x="-20" y="{y-90}" width="{W+40}" height="30" fill="#f2d14b"/>')
                for wx in range(20, W, 170): self.add(f'<rect x="{wx}" y="{y-250}" width="120" height="110" rx="10" fill="#cfe8f3" opacity=".9"/>')
            elif pr == "umbrella":
                x = px[0]; y = self.GY - 360 * self.k
                self.add(f'<path d="M{x-130:.0f},{y:.0f} A130,110 0 0 1 {x+130:.0f},{y:.0f} Q{x+97:.0f},{y-18:.0f} {x+65:.0f},{y:.0f} Q{x+32:.0f},{y-18:.0f} {x:.0f},{y:.0f} Q{x-32:.0f},{y-18:.0f} {x-65:.0f},{y:.0f} Q{x-97:.0f},{y-18:.0f} {x-130:.0f},{y:.0f} Z" fill="#e63946"/><line x1="{x:.0f}" y1="{y:.0f}" x2="{x:.0f}" y2="{y+150:.0f}" stroke="#333" stroke-width="6"/>')
            elif pr == "books":
                x = px[0] - 120; y = getattr(self, "desk_y", self.GY + 40)
                for i, c in enumerate(["#e63946", "#457b9d", "#f4a261", "#2a9d8f"]): self.add(f'<rect x="{x - i*3}" y="{y-26*(i+1)}" width="110" height="24" rx="3" fill="{c}"/>')
            elif pr == "tiffin":
                x = px[0] + 90; y = getattr(self, "desk_y", self.GY + 40)
                for i in range(3): self.add(f'<rect x="{x}" y="{y-34*(i+1)}" width="70" height="32" rx="8" fill="#c0c7cf" stroke="#8d99ae" stroke-width="3"/>')
                self.add(f'<path d="M{x+10},{y-102} q25,-40 50,0" stroke="#8d99ae" stroke-width="6" fill="none"/>')
            elif pr == "flowers":
                for _ in range(14):
                    fx, fy = rnd.uniform(0, W), rnd.uniform(self.GY + 60, H - 20)
                    c = rnd.choice(["#ff9f1c", "#ffbf69", "#f15bb5", "#fee440"])
                    self.add("".join(f'<circle cx="{fx+12*math.cos(a):.0f}" cy="{fy+12*math.sin(a):.0f}" r="9" fill="{c}"/>' for a in [i*1.256 for i in range(5)]) + f'<circle cx="{fx:.0f}" cy="{fy:.0f}" r="6" fill="#7a4b00"/>')
            elif pr == "stars":
                for _ in range(40): self.add(f'<circle cx="{rnd.uniform(0,W):.0f}" cy="{rnd.uniform(0,H*.6):.0f}" r="{rnd.choice([1.5,2,3])}" fill="#fff" opacity=".8"/>')

    def texture(self):
        self.add(f'<filter id="grain"><feTurbulence type="fractalNoise" baseFrequency=".85" numOctaves="2" seed="{self.spec.get("seed",1)}"/>'
                 f'<feColorMatrix values="0 0 0 0 .5  0 0 0 0 .4  0 0 0 0 .3  0 0 0 .13 0"/></filter><rect width="100%" height="100%" filter="url(#grain)"/>')
        # gentle top scrim so text reads well
        top = "#000" if self.dark else "#2b1a12"
        self.add(f'<defs><linearGradient id="scrim" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{top}" stop-opacity="{.30 if self.dark else .2}"/><stop offset=".55" stop-color="{top}" stop-opacity="0"/></linearGradient></defs>'
                 f'<rect width="100%" height="100%" fill="url(#scrim)"/>')

    def render(self):
        self.sky(); self.place()
        # draw people sorted back-to-front; props that sit behind people first
        behind = [p for p in self.spec.get("props", []) if p in ("train", "scooter", "swing", "lamp", "kite", "lights", "birds", "clock", "stars")]
        front = [p for p in self.spec.get("props", []) if p not in behind]
        sp = dict(self.spec); self.spec = dict(sp, props=behind); self.props()
        for p in self.spec.get("people", []): self.person(p)
        self.spec = dict(sp, props=front); self.props(); self.spec = sp
        self.texture()
        return f'<svg class="bg" width="{self.W}" height="{self.H}" viewBox="0 0 {self.W} {self.H}">' + "".join(self.out) + "</svg>"

def scene_svg(W, H, spec):
    return S(W, H, spec).render()
