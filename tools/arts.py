"""Original ink-sketch motifs for its_poetogram cards. Each returns a list of SVG strings.
Drawing area: roughly x 80-1000, y 560-1260. Ink brown + one red accent."""
import math, random

INK = "#2e2118"; RED = "#b3261e"; GOLD = "#d9a441"

def densify(points, closed=False, step=18):
    src = list(points) + ([points[0]] if closed else [])
    out = [src[0]]
    for (x0, y0), (x1, y1) in zip(src, src[1:]):
        n = max(1, int(math.hypot(x1-x0, y1-y0) // step))
        out += [(x0 + (x1-x0)*i/n, y0 + (y1-y0)*i/n) for i in range(1, n+1)]
    return out

def jp(points, j=1.6, closed=False):
    points = densify(points, closed)
    pts = [(x + random.uniform(-j, j), y + random.uniform(-j, j)) for x, y in points]
    d = f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"
    for i in range(1, len(pts) - 1):
        mx, my = (pts[i][0] + pts[i+1][0]) / 2, (pts[i][1] + pts[i+1][1]) / 2
        d += f" Q{pts[i][0]:.1f},{pts[i][1]:.1f} {mx:.1f},{my:.1f}"
    d += f" L{pts[-1][0]:.1f},{pts[-1][1]:.1f}"
    return d

def sketch(points, w=2.2, passes=3, closed=False, j=1.8, color=INK):
    out = []
    for k in range(passes):
        d = jp(points, j, closed)
        out.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{max(w - k*0.7, 0.7):.1f}" stroke-linecap="round" stroke-linejoin="round" opacity="{0.95 - k*0.22:.2f}"/>')
    return out

def fillpoly(points, color=RED, op=0.85):
    d = jp(points, 0.6, True) + " Z"
    return f'<path d="{d}" fill="{color}" fill-opacity="{op}"/>'

def hatch(x0, y0, x1, y1, step=9, ang=1.0, clip=None, op=0.4):
    out = []
    cp = f' clip-path="url(#{clip})"' if clip else ""
    out.append(f"<g{cp}>")
    x = x0 - (y1 - y0)
    while x < x1:
        out.append(f'<path d="M{x:.0f},{y1} l{(y1-y0)*ang:.0f},{-(y1-y0)}" stroke="{INK}" stroke-width="0.8" opacity="{op}"/>')
        x += step
    out.append("</g>")
    return out

def arc_pts(cx, cy, rx, ry, a0, a1, n=24):
    return [(cx + rx*math.cos(math.radians(a0 + (a1-a0)*i/n)), cy + ry*math.sin(math.radians(a0 + (a1-a0)*i/n))) for i in range(n+1)]

def splatter(n=14, y0=600, y1=1250):
    return [f'<circle cx="{random.uniform(90,990):.0f}" cy="{random.uniform(y0,y1):.0f}" r="{random.uniform(0.8,3):.1f}" fill="{INK}" opacity="0.35"/>' for _ in range(n)]

def wave_rows(y0, rows, x0=150, x1=930, amp=8, gap=34, op0=0.8):
    out = []
    for r in range(rows):
        y = y0 + r*gap
        pts = [(x, y + amp*math.sin(x/38 + r)) for x in range(int(x0 + r*25), int(x1 - r*25), 18)]
        out += sketch(pts, w=1.6, passes=2, j=1.2)[:1]
        out[-1] = out[-1].replace('opacity="0.95"', f'opacity="{op0 - r*0.15:.2f}"')
    return out

# ---------------- motifs ----------------
def paper_boat(g):
    s = []
    hull = [(360, 990), (720, 990), (650, 1062), (430, 1062)]
    sail_l = [(430, 990), (540, 840), (540, 990)]
    sail_r = [(540, 840), (650, 990), (540, 990)]
    s.append(fillpoly(hull, RED, 0.85)); s.append(fillpoly(sail_l, RED, 0.55)); s.append(fillpoly(sail_r, RED, 0.75))
    s += sketch(hull, closed=True); s += sketch(sail_l, closed=True); s += sketch(sail_r, closed=True)
    s += sketch([(430, 990), (470, 1030), (540, 990), (610, 1030), (650, 990)], w=1.2, passes=1)
    # water + ripples
    s += wave_rows(1075, 5)
    # a second, smaller half-sunk boat in the distance
    s.append(fillpoly([(800, 870), (880, 870), (865, 885), (815, 885)], RED, 0.4))
    s += sketch([(800, 870), (840, 838), (880, 870)], w=1.2, passes=2)
    s += sketch([(770, 888), (910, 888)], w=1, passes=1)
    # rain drops
    for _ in range(26):
        x, y = random.uniform(120, 960), random.uniform(600, 940)
        s.append(f'<path d="M{x:.0f},{y:.0f} l-6,18" stroke="{INK}" stroke-width="1.2" opacity="0.35" stroke-linecap="round"/>')
    return s + splatter(8)

def diya(g):
    s = []
    cx = 540
    # glow
    s.append(f'<defs><radialGradient id="glow"><stop offset="0" stop-color="#ffcf6b" stop-opacity=".75"/><stop offset=".45" stop-color="#f1b04c" stop-opacity=".28"/><stop offset="1" stop-color="#f1b04c" stop-opacity="0"/></radialGradient>'
             f'<linearGradient id="fl" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="{RED}"/><stop offset=".55" stop-color="#e8832a"/><stop offset="1" stop-color="#ffd36e"/></linearGradient>'
             f'<clipPath id="bowl"><path d="M330,1050 Q540,1250 750,1050 Z"/></clipPath></defs>')
    s.append(f'<circle cx="770" cy="880" r="320" fill="url(#glow)"/>')
    # bowl
    bowl = [(330, 1050)] + [(330 + 420*t, 1050 + 150*math.sin(math.pi*t)) for t in [i/20 for i in range(1, 20)]] + [(750, 1050)]
    s.append(fillpoly(bowl, "#8c2a1a", 0.85))
    s += hatch(320, 1050, 760, 1210, step=10, clip="bowl", op=0.45)
    s += sketch(bowl, closed=True, w=2.6)
    s += sketch(arc_pts(540, 1050, 210, 26, 180, 360), w=2)
    s += sketch(arc_pts(540, 1050, 210, 26, 0, 180), w=1.4, passes=2)
    # spout + wick
    s += sketch([(700, 1045), (790, 1010), (760, 1050)], w=2)
    s += sketch([(760, 1012), (770, 990)], w=2.4, passes=1)
    # decorative dots on bowl
    for i in range(9):
        x = 380 + i*40; y = 1050 + 150*math.sin(math.pi*(x-330)/420)*0.55
        s.append(f'<circle cx="{x}" cy="{y:.0f}" r="5" fill="{GOLD}" stroke="{INK}" stroke-width="1"/>')
    # flame
    fx, fy = 770, 985
    flame = f"M{fx},{fy} C{fx-38},{fy-40} {fx-20},{fy-110} {fx+4},{fy-175} C{fx+22},{fy-110} {fx+42},{fy-45} {fx},{fy} Z"
    s.append(f'<path d="{flame}" fill="url(#fl)" stroke="{INK}" stroke-width="1.6"/>')
    s.append(f'<path d="M{fx},{fy-8} C{fx-12},{fy-30} {fx-5},{fy-60} {fx+3},{fy-85} C{fx+10},{fy-60} {fx+14},{fy-30} {fx},{fy-8} Z" fill="#fff3c4" opacity=".9"/>')
    s.append(f'<defs/><circle cx="{fx}" cy="{fy-90}" r="130" fill="url(#glow)"/>')
    # rays
    for k in range(9):
        ang = math.radians(-160 + k*17.5)
        r0, r1 = 120, 165 + random.uniform(-10, 15)
        s.append(f'<path d="M{fx + r0*math.cos(ang):.0f},{fy-90 + r0*math.sin(ang):.0f} L{fx + r1*math.cos(ang):.0f},{fy-90 + r1*math.sin(ang):.0f}" stroke="{INK}" stroke-width="1.2" opacity=".35" stroke-linecap="round"/>')
    # ground shadow
    s += sketch([(280, 1225), (800, 1225)], w=1.4, passes=2)
    s += hatch(300, 1205, 780, 1225, step=7, op=0.25)
    return s + splatter(6)

def chai(g):
    s = []
    glass_out = [(455, 900), (625, 900), (607, 1150), (473, 1150)]
    tea_top = 960
    tea = [(450 + 5*(tea_top-900)/250*1, tea_top), (630 - 5, tea_top), (607, 1150), (473, 1150)]
    s.append(f'<defs><clipPath id="gl"><path d="M455,900 L625,900 L607,1150 L473,1150 Z"/></clipPath></defs>')
    s.append(fillpoly([(452, tea_top), (628, tea_top), (607, 1150), (473, 1150)], "#9a3b1c", 0.85))
    s += hatch(440, tea_top, 640, 1150, step=11, clip="gl", op=0.35)
    # ridges of cutting-chai glass
    for i in range(8):
        x0 = 468 + i*20; x1 = 482 + i*17.5
        s += sketch([(x0, 905), (x1, 1145)], w=0.9, passes=1)
    s += sketch(glass_out, closed=True, w=2.6)
    s += sketch(arc_pts(540, 900, 85, 12, 0, 360, 30), w=1.8, passes=2)
    s += sketch(arc_pts(540, tea_top, 88, 10, 0, 180), w=1.2, passes=1)
    # steam
    for k, x in enumerate((505, 545, 585)):
        pts = [(x + 16*math.sin(t/22 + k), 880 - t) for t in range(0, 230, 14)]
        s += sketch(pts, w=1.8 - k*0.2, passes=2, j=1)
    # saucer-less table line + biscuit
    s += sketch([(250, 1160), (840, 1160)], w=1.6, passes=2)
    s.append(f'<rect x="660" y="1118" width="120" height="40" rx="8" fill="{GOLD}" fill-opacity=".55"/>')
    s += sketch([(660, 1118), (780, 1118), (780, 1158), (660, 1158)], closed=True, w=1.6, passes=2)
    for i in range(6):
        s.append(f'<circle cx="{675+i*19}" cy="1138" r="2.2" fill="{INK}" opacity=".7"/>')
    # a red rose petal / heart doodle next to the glass (accent memory)
    s.append(f'<path d="M360,1100 c-30,-40 -80,-5 -40,30 l40,32 l40,-32 c40,-35 -10,-70 -40,-30z" fill="{RED}" fill-opacity=".85" stroke="{INK}" stroke-width="1.6"/>')
    return s + splatter(8)

def kite(g):
    s = []
    top, right, bottom, left = (760, 600), (860, 710), (760, 850), (660, 710)
    k = [top, right, bottom, left]
    s.append(fillpoly([top, right, bottom], RED, 0.9)); s.append(fillpoly([top, left, bottom], RED, 0.7))
    s += sketch(k, closed=True, w=2.4)
    s += sketch([top, bottom], w=1.4, passes=2); s += sketch(arc_pts(760, 740, 100, 40, 180, 360), w=1.4, passes=2)
    # tail
    tail = [(760, 850), (740, 890), (765, 930), (745, 970)]
    s += sketch(tail, w=1.6, passes=2)
    s.append(f'<path d="M745,880 l-18,-10 0,22z M765,925 l18,-10 0,22z" fill="{RED}" stroke="{INK}" stroke-width="1"/>')
    # string that is cut: from kite to mid, then gap, then the rest falling to the bottom-left (roof line)
    s += sketch([(760, 780), (640, 900), (560, 990)], w=1.3, passes=2, j=1)
    s += sketch([(530, 1030), (450, 1110), (380, 1180), (300, 1210)], w=1.3, passes=2, j=1)
    # cut marks
    s.append(f'<path d="M548,1003 l14,-6 M542,1016 l16,0" stroke="{RED}" stroke-width="2" stroke-linecap="round"/>')
    # rooftop + charkhi (spool)
    s += sketch([(90, 1230), (420, 1230)], w=2.2)
    s += hatch(90, 1230, 420, 1265, step=8, op=0.3)
    s += sketch(arc_pts(300, 1205, 22, 22, 0, 360, 20), closed=True, w=1.8, passes=2)
    s += sketch([(270, 1205), (330, 1205)], w=1.6, passes=1)
    # birds far away
    for (x, y, sc) in [(260, 700, 1), (320, 660, .8), (380, 720, .6)]:
        s.append(f'<path d="M{x},{y} q{12*sc},{-12*sc} {24*sc},0 q{12*sc},{-12*sc} {24*sc},0" fill="none" stroke="{INK}" stroke-width="1.6" stroke-linecap="round" opacity=".7"/>')
    return s + splatter(8)

def cage_bird(g):
    s = []
    cx, top, bot, r = 360, 860, 1200, 130
    # cage dome + base
    dome = arc_pts(cx, top + 70, r, 90, 180, 360)
    s += sketch(dome, w=2.4)
    s += sketch([(cx - r, top + 70), (cx - r, bot)], w=2.2); s += sketch([(cx + r, top + 70), (cx + r, bot)], w=2.2)
    s += sketch([(cx - r - 15, bot), (cx + r + 15, bot)], w=3)
    s += sketch([(cx - r, bot - 25), (cx + r, bot - 25)], w=1.6, passes=2)
    for i in range(1, 8):
        x = cx - r + i * (2*r/8)
        ytop = top + 70 - 90*math.sqrt(max(0, 1 - ((x-cx)/r)**2))
        if 3 <= i <= 5:  # gap where the door is open
            continue
        s += sketch([(x, ytop), (x, bot)], w=1.3, passes=2, j=1)
    s += sketch([(cx, top - 20), (cx, top - 60)], w=2); s += sketch(arc_pts(cx, top - 72, 14, 14, 0, 360, 16), closed=True, w=1.8, passes=2)
    # open door swung out
    door = [(cx - 50, 980), (cx - 150, 1010), (cx - 150, 1150), (cx - 50, 1150)]
    s += sketch(door, w=1.6, passes=2)
    for i in range(1, 4):
        s += sketch([(cx - 50 - i*25, 980 + i*7.5), (cx - 50 - i*25, 1150)], w=1, passes=1)
    # gold tint on cage
    s.append(f'<path d="M{cx-r},{bot} L{cx-r},{top+70} A{r},90 0 0 1 {cx+r},{top+70} L{cx+r},{bot} Z" fill="{GOLD}" fill-opacity=".14"/>')
    # red bird flying out upper-right
    def bird(x, y, sc, op=1):
        body = f"M{x},{y} c{30*sc},{-8*sc} {60*sc},{-4*sc} {80*sc},{8*sc} c{-25*sc},{10*sc} {-55*sc},{12*sc} {-80*sc},{-8*sc}z"
        wing = f"M{x+30*sc},{y} c{10*sc},{-60*sc} {50*sc},{-90*sc} {90*sc},{-100*sc} c{-20*sc},{40*sc} {-35*sc},{80*sc} {-60*sc},{100*sc}z"
        wing2 = f"M{x+35*sc},{y+4*sc} c{-30*sc},{-40*sc} {-60*sc},{-55*sc} {-95*sc},{-55*sc} c{25*sc},{25*sc} {50*sc},{50*sc} {80*sc},{58*sc}z"
        tail = f"M{x},{y} l{-40*sc},{-12*sc} l{6*sc},{14*sc} l{-30*sc},{8*sc}z"
        return [f'<g opacity="{op}">'] + [f'<path d="{d}" fill="{RED}" fill-opacity=".88" stroke="{INK}" stroke-width="{1.8*max(sc,.6):.1f}" stroke-linejoin="round"/>' for d in (wing2, tail, body, wing)] + \
               [f'<circle cx="{x+68*sc}" cy="{y+1*sc}" r="{3*sc}" fill="{INK}"/>', f'<path d="M{x+80*sc},{y+6*sc} l{12*sc},{2*sc} l{-12*sc},{4*sc}z" fill="{GOLD}" stroke="{INK}" stroke-width="1"/>', "</g>"]
    s += bird(680, 780, 1.5)
    # dashed flight path from cage door
    s.append(f'<path d="M{cx-60},1000 C450,900 560,880 680,800" fill="none" stroke="{INK}" stroke-width="1.3" stroke-dasharray="12 10" opacity=".45"/>')
    # floating feather
    s.append(f'<path d="M600,1080 c20,-30 50,-40 70,-35 c-10,25 -40,45 -70,35z" fill="{RED}" fill-opacity=".6" stroke="{INK}" stroke-width="1.2"/>')
    s += sketch([(595, 1088), (668, 1045)], w=1, passes=1)
    return s + splatter(8)

def thali(g):
    s = []
    cx, cy = 540, 1090
    s.append(f'<defs><clipPath id="pl"><ellipse cx="{cx}" cy="{cy}" rx="300" ry="95"/></clipPath></defs>')
    s.append(f'<ellipse cx="{cx}" cy="{cy}" rx="300" ry="95" fill="#c9b48a" fill-opacity=".45"/>')
    s += sketch(arc_pts(cx, cy, 300, 95, 0, 360, 40), closed=True, w=2.6)
    s += sketch(arc_pts(cx, cy, 262, 78, 0, 360, 40), closed=True, w=1.2, passes=1)
    s += hatch(cx - 300, cy + 40, cx + 300, cy + 95, step=8, clip="pl", op=0.35)
    # katori (bowl) with dal in red
    for (kx, ky, col) in [(430, 1060, "#c8641e"), (560, 1040, RED)]:
        s.append(f'<ellipse cx="{kx}" cy="{ky}" rx="62" ry="20" fill="{col}" fill-opacity=".85"/>')
        s += sketch(arc_pts(kx, ky, 62, 20, 0, 360, 24), closed=True, w=1.8, passes=2)
        s += sketch(arc_pts(kx, ky + 2, 62, 46, 0, 180, 16), w=2, passes=2)
    # rotis stacked
    for i in range(3):
        rx, ry = 690, 1085 - i*9
        s.append(f'<ellipse cx="{rx}" cy="{ry}" rx="78" ry="26" fill="#e6c27a"/>')
        s += sketch(arc_pts(rx, ry, 78, 26, 0, 360, 24), closed=True, w=1.6, passes=1)
    for _ in range(14):
        s.append(f'<circle cx="{690 + random.uniform(-55,55):.0f}" cy="{1067 + random.uniform(-12,12):.0f}" r="{random.uniform(2,4):.1f}" fill="#7a4a1c" opacity=".6"/>')
    # steam from dal + rotis
    for k, x in enumerate((540, 580, 680, 710)):
        pts = [(x + 12*math.sin(t/20 + k), 1010 - t) for t in range(0, 170, 14)]
        s += sketch(pts, w=1.5, passes=1, j=1)
    s += sketch([(170, 1210), (910, 1210)], w=1.4, passes=2)
    return s + splatter(6)

ARTS = {"boat": paper_boat, "diya": diya, "chai": chai, "kite": kite, "cage": cage_bird, "thali": thali}

def _rot(pts, cx, cy, ang):
    c, s_ = math.cos(ang), math.sin(ang)
    return [(cx + (x-cx)*c - (y-cy)*s_, cy + (x-cx)*s_ + (y-cy)*c) for x, y in pts]

def chappal(g):
    s = []
    # door frame + threshold
    s += sketch([(170, 780), (170, 1160)], w=2.6); s += sketch([(910, 780), (910, 1160)], w=2.6)
    s += sketch([(120, 1160), (960, 1160)], w=2.8)
    s += hatch(120, 1160, 960, 1235, step=10, op=0.3)
    # light falling from door
    s.append(f'<path d="M190,790 L890,790 L960,1150 L120,1150 Z" fill="{GOLD}" fill-opacity=".10"/>')
    def slipper(cx, cy, ang, flip=1):
        sole = []
        for i in range(36):
            t = 2*math.pi*i/36
            y = 125*math.sin(t)
            w = 52*(0.78 + 0.22*(-math.sin(t)))  # toe wider than heel
            sole.append((cx + flip*w*math.cos(t), cy + y))
        sole = _rot(sole, cx, cy, ang)
        out = [fillpoly(sole, "#8a6a48", 0.55)]
        out += sketch(sole, closed=True, w=2.4)
        inner = _rot([(cx + 0.82*(x-cx), cy + 0.88*(y-cy)) for x, y in sole[:]], cx, cy, 0)
        out += sketch(inner, closed=True, w=1, passes=1)
        toe = _rot([(cx, cy - 92)], cx, cy, ang)[0]
        l = _rot([(cx - 50, cy - 10)], cx, cy, ang)[0]; r = _rot([(cx + 50, cy - 10)], cx, cy, ang)[0]
        for p in (l, r):
            out.append(f'<path d="M{toe[0]:.0f},{toe[1]:.0f} Q{(toe[0]+p[0])/2:.0f},{(toe[1]+p[1])/2 - 22:.0f} {p[0]:.0f},{p[1]:.0f}" fill="none" stroke="{RED}" stroke-width="11" stroke-linecap="round"/>')
            out.append(f'<path d="M{toe[0]:.0f},{toe[1]:.0f} Q{(toe[0]+p[0])/2:.0f},{(toe[1]+p[1])/2 - 22:.0f} {p[0]:.0f},{p[1]:.0f}" fill="none" stroke="{INK}" stroke-width="1.4"/>')
        # worn heel crack
        h = _rot([(cx - 18, cy + 95), (cx, cy + 82), (cx + 14, cy + 100)], cx, cy, ang)
        out += sketch(h, w=1, passes=1)
        return out
    s += slipper(450, 1000, math.radians(-12))
    s += slipper(620, 1010, math.radians(10))
    # walking stick leaning on door frame
    s += sketch([(860, 1155), (890, 800)], w=4, passes=2)
    s += sketch(arc_pts(865, 800, 25, 25, 180, 360, 12), w=4, passes=2)
    return s + splatter(6)

def clock(g):
    s = []
    cx, cy, R = 540, 960, 165
    s.append(f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="#f6ecd4" fill-opacity=".7"/>')
    s += sketch(arc_pts(cx, cy, R, R, 0, 360, 48), closed=True, w=3)
    s += sketch(arc_pts(cx, cy, R - 14, R - 14, 0, 360, 48), closed=True, w=1.2, passes=1)
    for i in range(60):
        a = math.radians(i*6)
        r0 = R - 30 if i % 5 == 0 else R - 22
        s.append(f'<path d="M{cx + r0*math.cos(a):.1f},{cy + r0*math.sin(a):.1f} L{cx + (R-16)*math.cos(a):.1f},{cy + (R-16)*math.sin(a):.1f}" stroke="{INK}" stroke-width="{2.6 if i%5==0 else 1}" opacity=".85"/>')
    # hands: hour ~ 11, minute ~ 58 (time is almost up)
    for ang, L, w, col in [(-120, 80, 7, INK), (-96, 125, 4, INK), (60, 135, 2, RED)]:
        a = math.radians(ang)
        s.append(f'<path d="M{cx - 18*math.cos(a):.1f},{cy - 18*math.sin(a):.1f} L{cx + L*math.cos(a):.1f},{cy + L*math.sin(a):.1f}" stroke="{col}" stroke-width="{w}" stroke-linecap="round"/>')
    s.append(f'<circle cx="{cx}" cy="{cy}" r="9" fill="{RED}" stroke="{INK}" stroke-width="2"/>')
    # cracked glass
    s += sketch([(cx + 40, cy - 150), (cx + 60, cy - 90), (cx + 35, cy - 40), (cx + 80, cy + 10)], w=1.2, passes=1, j=0.5)
    s += sketch([(cx + 60, cy - 90), (cx + 110, cy - 80)], w=1, passes=1, j=0.5)
    # nail + string
    s.append(f'<circle cx="{cx}" cy="660" r="5" fill="{INK}"/>')
    s += sketch([(cx, 660), (cx - 110, cy - R + 25)], w=1.4, passes=2, j=0.6)
    s += sketch([(cx, 660), (cx + 110, cy - R + 25)], w=1.4, passes=2, j=0.6)
    # falling sand-like dots below (time slipping)
    for i in range(22):
        x = cx + random.uniform(-40, 40); y = cy + R + 25 + i*6 + random.uniform(-3, 3)
        if y < 1235:
            s.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{random.uniform(1,2.4):.1f}" fill="{RED}" opacity="{0.8 - i*0.03:.2f}"/>')
    return s + splatter(6)

def mask(g):
    s = []
    cx, cy = 560, 965
    face = [(cx + 125*math.cos(t)*(0.86 + 0.14*math.sin(t)), cy + 165*math.sin(t)) for t in [2*math.pi*i/40 for i in range(40)]]
    face = _rot(face, cx, cy, math.radians(-14))
    s.append(f'<defs><clipPath id="mk"><path d="{jp(face, 0, True)} Z"/></clipPath></defs>')
    s.append(fillpoly(face, "#f2e3c2", 0.95))
    # right half red
    s.append(f'<g clip-path="url(#mk)"><path d="M{cx+12},{cy-260} L{cx+300},{cy-260} L{cx+300},{cy+260} L{cx-22},{cy+260} Z" fill="{RED}" fill-opacity=".85"/></g>')
    s += hatch(cx - 140, cy - 170, cx + 20, cy + 170, step=12, clip="mk", op=0.22)
    s += sketch(face, closed=True, w=2.6)
    # eyes (holes) + brows
    for ex, ey in [(cx - 52, cy - 40), (cx + 48, cy - 52)]:
        eye = _rot([(ex + 32*math.cos(t), ey + 14*math.sin(t)*(1 if math.sin(t) > 0 else 0.6)) for t in [2*math.pi*i/20 for i in range(20)]], ex, ey, math.radians(-14))
        s.append(fillpoly(eye, "#1e140d", 0.95))
        s += sketch([(ex - 34, ey - 30), (ex, ey - 40), (ex + 32, ey - 32)], w=1.8, passes=1)
    # smile on the mask
    s.append(f'<path d="M{cx-60},{cy+75} Q{cx-5},{cy+120} {cx+55},{cy+55}" fill="none" stroke="#1e140d" stroke-width="6" stroke-linecap="round"/>')
    # a single tear line under left eye (truth behind the smile)
    s.append(f'<path d="M{cx-58},{cy-22} q-4,30 2,55" fill="none" stroke="{INK}" stroke-width="1.6" stroke-dasharray="5 5"/>')
    # strings hanging (mask taken off)
    s += sketch([(cx - 122, cy - 20), (cx - 165, cy + 30), (cx - 150, cy + 95)], w=1.6, passes=2)
    s += sketch([(cx + 114, cy - 60), (cx + 160, cy - 20), (cx + 170, cy + 45)], w=1.6, passes=2)
    # shadow on ground
    s += sketch([(300, 1205), (820, 1205)], w=1.4, passes=2)
    return s + splatter(6)

ARTS.update({"chappal": chappal, "clock": clock, "mask": mask})
