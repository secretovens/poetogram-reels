#!/usr/bin/env python3
"""its_poetogram "अल्फ़ाज़ · WORDS THAT STAY" reels — literary, emotional, personal (~22-26 s):
  1 hook (personal, Hindi)  2 the quote, revealed line by line (original Urdu/Hindi or English) + author/work + Hindi meaning
  3 the feeling (Hindi, lines revealed one by one)  4 close (send / save / comment ask)
Visual language: dark/warm literary palettes with a quiet illustrated motif that moves slightly from slide to slide
(moon, stars, candle, lamp, rain, leaves, sprout, mirror, sun, feather, ink mountains, path).
Fonts (OFL) in tools/fonts: Tiro Devanagari Hindi (quotes), Noto Serif Devanagari (Hindi text), Cormorant Garamond (English quotes).
Usage: python3 tools/alfaaz.py alfaaz.json ID [ID ...] | all   → reels/ID.mp4, covers/ID.jpg"""
import json, os, sys, math, random, html, subprocess
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
FONTS = os.path.join(HERE, "fonts")
W, H = 1080, 1920
e = html.escape
THEMES = {
    "night":     dict(bg="#0a0f24", bg2="#18224a", fg="#f4ecdc", sub="#9196b3", gold="#e8c77d", art="#f4ecdc"),
    "dusk":      dict(bg="#1a1128", bg2="#43233f", fg="#f7e9de", sub="#b392a0", gold="#f2b884", art="#f7e9de"),
    "parchment": dict(bg="#e9dcc0", bg2="#f5ecd8", fg="#2b2015", sub="#7c6b52", gold="#9b5a22", art="#5a4630"),
    "candle":    dict(bg="#0b0805", bg2="#24170b", fg="#f6e8cf", sub="#a08f74", gold="#f3b65c", art="#f6e8cf"),
    "rain":      dict(bg="#0d1820", bg2="#1d3040", fg="#ecf2f4", sub="#8ea2ae", gold="#e6bb72", art="#cfe0ea"),
    "autumn":    dict(bg="#241009", bg2="#4a2217", fg="#f8eadb", sub="#bb9580", gold="#eda25a", art="#f8eadb"),
    "dawn":      dict(bg="#f3d9c6", bg2="#fbeee2", fg="#3a1f19", sub="#8f6a5b", gold="#c45a35", art="#7a3b2a"),
}

# ---------------- motifs: (theme, slide k 0..3, rnd) -> svg string ----------------
GLOW = '<filter id="blur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="40"/></filter><filter id="blur2" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="10"/></filter>'

def stars(t, r, n=90, y0=40, y1=1900, op=.55):
    s = []
    for _ in range(n):
        x, y = r.uniform(20, W - 20), r.uniform(y0, y1); rr = r.choice([1.2, 1.6, 2.2, 2.8])
        s.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{rr}" fill="{t["art"]}" opacity="{r.uniform(.15, op):.2f}"/>')
    return "".join(s)

def sparkle(x, y, sz, col, op=1):
    return (f'<path d="M{x},{y-sz} Q{x},{y} {x+sz},{y} Q{x},{y} {x},{y+sz} Q{x},{y} {x-sz},{y} Q{x},{y} {x},{y-sz} Z" fill="{col}" opacity="{op}"/>')

def m_moon(t, k, r):
    cx, cy, R = 770, 1420 - k * 14, 120
    s = [f'<circle cx="{cx}" cy="{cy}" r="{R*2.2}" fill="{t["gold"]}" opacity=".10" filter="url(#blur)"/>',
         f'<mask id="cr"><rect width="{W}" height="{H}" fill="white"/><circle cx="{cx+52}" cy="{cy-34}" r="{R*.92}" fill="black"/></mask>',
         f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="{t["gold"]}" mask="url(#cr)" opacity=".92"/>', stars(t, r, 70, 1150, 1880)]
    for i in range(3):
        y = 1560 + i * 90; x = 120 + i * 160 - k * 20
        s.append(f'<rect x="{x}" y="{y}" width="{420 - i*60}" height="16" rx="8" fill="{t["art"]}" opacity=".07"/>')
    return "".join(s)

def m_stars(t, k, r):
    s = [stars(t, r, 160, 60, 1900, .7)]
    for (x, y, sz) in [(180, 1300, 22), (860, 1520, 30), (420, 1700, 16), (700, 1240, 14)]:
        s.append(sparkle(x, y, sz, t["gold"], .9))
    sx = 980 - k * 120; sy = 1150 + k * 60
    s.append(f'<line x1="{sx}" y1="{sy}" x2="{sx-220}" y2="{sy+110}" stroke="{t["gold"]}" stroke-width="3" stroke-linecap="round" opacity=".7"/>'
             f'<circle cx="{sx}" cy="{sy}" r="5" fill="{t["gold"]}"/>')
    s.append(f'<path d="M0,1800 Q270,1730 540,1790 T1080,1770 L1080,1920 L0,1920 Z" fill="{t["bg"]}" opacity=".9"/>')
    return "".join(s)

def m_sprout(t, k, r):
    gy = 1740; h = 70 + k * 85; x = 540
    s = [f'<circle cx="{x}" cy="{gy-h}" r="260" fill="{t["gold"]}" opacity=".10" filter="url(#blur)"/>',
         f'<path d="M60,{gy} Q540,{gy-26} 1020,{gy}" fill="none" stroke="{t["art"]}" stroke-width="3" opacity=".45"/>',
         f'<path d="M{x-46},{gy-4} q20,-40 40,-6 z" fill="{t["art"]}" opacity=".5"/><path d="M{x+8},{gy-6} q26,-34 46,2 z" fill="{t["art"]}" opacity=".5"/>',
         f'<path d="M{x},{gy-6} C{x-10},{gy-h*.4} {x+12},{gy-h*.7} {x},{gy-h}" fill="none" stroke="{t["gold"]}" stroke-width="7" stroke-linecap="round"/>']
    if k >= 1:
        sc = .6 + .25 * k
        s.append(f'<path d="M{x},{gy-h+10} c-{60*sc:.0f},-{10*sc:.0f} -{90*sc:.0f},-{60*sc:.0f} -{80*sc:.0f},-{70*sc:.0f} c{40*sc:.0f},-{4*sc:.0f} {80*sc:.0f},{30*sc:.0f} {80*sc:.0f},{70*sc:.0f} z" fill="{t["gold"]}"/>'
                 f'<path d="M{x},{gy-h+4} c{60*sc:.0f},-{14*sc:.0f} {84*sc:.0f},-{66*sc:.0f} {74*sc:.0f},-{76*sc:.0f} c-{40*sc:.0f},0 -{74*sc:.0f},{34*sc:.0f} -{74*sc:.0f},{76*sc:.0f} z" fill="{t["gold"]}" opacity=".85"/>')
    for _ in range(30):
        s.append(f'<circle cx="{r.uniform(80,1000):.0f}" cy="{r.uniform(1250,1700):.0f}" r="{r.uniform(1.5,3.5):.1f}" fill="{t["gold"]}" opacity="{r.uniform(.15,.45):.2f}"/>')
    return "".join(s)

def m_mirror(t, k, r):
    cx, cy = 540, 1500
    s = [f'<ellipse cx="{cx}" cy="{cy}" rx="230" ry="290" fill="{t["gold"]}" opacity=".08" filter="url(#blur)"/>',
         f'<ellipse cx="{cx}" cy="{cy}" rx="170" ry="225" fill="none" stroke="{t["gold"]}" stroke-width="6" opacity=".85"/>',
         f'<ellipse cx="{cx}" cy="{cy}" rx="150" ry="205" fill="{t["art"]}" opacity=".05"/>',
         f'<g opacity="{.18 + k*.08:.2f}"><circle cx="{cx}" cy="{cy-60}" r="44" fill="{t["art"]}"/><path d="M{cx-90},{cy+150} Q{cx-80},{cy+10} {cx},{cy+5} Q{cx+80},{cy+10} {cx+90},{cy+150} Z" fill="{t["art"]}"/></g>',
         f'<line x1="{cx-110}" y1="{cy-150}" x2="{cx-60}" y2="{cy-200}" stroke="{t["art"]}" stroke-width="4" opacity=".25" stroke-linecap="round"/>',
         f'<rect x="{cx-14}" y="{cy+225}" width="28" height="140" fill="{t["gold"]}" opacity=".6"/><rect x="{cx-90}" y="{cy+360}" width="180" height="12" rx="6" fill="{t["gold"]}" opacity=".6"/>']
    return "".join(s)

def m_rain(t, k, r):
    s = []
    for _ in range(14):
        x, y = r.uniform(60, 1020), r.uniform(1100, 1850); rr = r.uniform(30, 90)
        s.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{rr:.0f}" fill="{t["gold"]}" opacity="{r.uniform(.05,.14):.2f}" filter="url(#blur2)"/>')
    for _ in range(140):
        x, y = r.uniform(0, W), r.uniform(0, H) + k * 40; L = r.uniform(30, 90)
        s.append(f'<line x1="{x:.0f}" y1="{y:.0f}" x2="{x-L*.18:.0f}" y2="{y+L:.0f}" stroke="{t["art"]}" stroke-width="1.6" opacity="{r.uniform(.06,.2):.2f}"/>')
    for _ in range(40):
        x, y = r.uniform(40, 1040), r.uniform(1150, 1880)
        s.append(f'<ellipse cx="{x:.0f}" cy="{y:.0f}" rx="{r.uniform(3,7):.1f}" ry="{r.uniform(5,10):.1f}" fill="none" stroke="{t["art"]}" stroke-width="1.5" opacity=".28"/>')
    return "".join(s)

def leaf(x, y, sz, rot, col, op):
    return (f'<g transform="translate({x:.0f},{y:.0f}) rotate({rot:.0f}) scale({sz:.2f})" opacity="{op:.2f}">'
            f'<path d="M0,-40 C26,-26 26,22 0,40 C-26,22 -26,-26 0,-40 Z" fill="{col}"/><line x1="0" y1="-36" x2="0" y2="46" stroke="{col}" stroke-width="3" opacity=".6"/></g>')

def m_leaves(t, k, r):
    s = []; cols = [t["gold"], "#c4552f", "#e3b05a", "#9e3d22"]
    for _ in range(26):
        x, y = r.uniform(40, 1040), r.uniform(1280, 1860); rot = r.uniform(0, 360)
        s.append(leaf(x + k * r.uniform(-12, 12), y + k * r.uniform(30, 60), r.uniform(.6, 1.5), rot + k * 25, r.choice(cols), r.uniform(.35, .85)))
    s.append(f'<path d="M0,1860 Q540,1820 1080,1860 L1080,1920 L0,1920Z" fill="{t["gold"]}" opacity=".15"/>')
    return "".join(s)

def m_lamp(t, k, r):
    x, y = 780, 1460
    s = [f'<circle cx="{x}" cy="{y}" r="{260 + k*10}" fill="{t["gold"]}" opacity=".14" filter="url(#blur)"/>',
         f'<line x1="{x}" y1="1150" x2="{x}" y2="{y-110}" stroke="{t["art"]}" stroke-width="3" opacity=".5"/>',
         f'<path d="M{x-50},{y-110} L{x+50},{y-110} L{x+70},{y-80} L{x-70},{y-80} Z" fill="{t["art"]}" opacity=".7"/>',
         f'<path d="M{x-60},{y-80} L{x+60},{y-80} L{x+48},{y+90} L{x-48},{y+90} Z" fill="{t["gold"]}" opacity=".30"/>',
         f'<path d="M{x-60},{y-80} L{x+60},{y-80} L{x+48},{y+90} L{x-48},{y+90} Z" fill="none" stroke="{t["art"]}" stroke-width="4" opacity=".7"/>',
         f'<path d="M{x},{y-30} C{x+22},{y+5} {x+16},{y+45} {x},{y+50} C{x-16},{y+45} {x-22},{y+5} {x},{y-30}Z" fill="{t["gold"]}"/>',
         f'<rect x="{x-58}" y="{y+90}" width="116" height="18" rx="6" fill="{t["art"]}" opacity=".7"/>', stars(t, r, 40, 1150, 1880, .4)]
    return "".join(s)

def m_candle(t, k, r):
    x, base, hgt = 540, 1820, 250
    top = base - hgt; fl = 1 + (.06 if k % 2 else -.04)
    s = [f'<circle cx="{x}" cy="{top-60}" r="{300 + k*12}" fill="{t["gold"]}" opacity=".16" filter="url(#blur)"/>',
         f'<rect x="{x-42}" y="{top}" width="84" height="{hgt}" rx="10" fill="{t["art"]}" opacity=".85"/>',
         f'<path d="M{x-42},{top+8} q20,30 0,60" fill="none" stroke="{t["bg"]}" stroke-width="5" opacity=".25"/>',
         f'<line x1="{x}" y1="{top}" x2="{x}" y2="{top-18}" stroke="{t["bg"]}" stroke-width="4"/>',
         f'<g transform="translate({x},{top-18}) scale(1,{fl:.2f})"><path d="M0,-110 C34,-60 36,-10 0,0 C-36,-10 -34,-60 0,-110Z" fill="{t["gold"]}"/>'
         f'<path d="M0,-60 C14,-36 14,-8 0,-2 C-14,-8 -14,-36 0,-60Z" fill="#fff4d6" opacity=".9"/></g>',
         f'<ellipse cx="{x}" cy="{base+6}" rx="160" ry="16" fill="{t["gold"]}" opacity=".18"/>']
    return "".join(s)

def m_sun(t, k, r):
    hy = 1720; cy = hy + 40 - k * 45
    s = [f'<circle cx="540" cy="{cy}" r="420" fill="{t["gold"]}" opacity=".12" filter="url(#blur)"/>',
         f'<clipPath id="hz"><rect x="0" y="0" width="{W}" height="{hy}"/></clipPath>',
         f'<circle cx="540" cy="{cy}" r="170" fill="{t["gold"]}" opacity=".85" clip-path="url(#hz)"/>',
         f'<line x1="40" y1="{hy}" x2="1040" y2="{hy}" stroke="{t["art"]}" stroke-width="3" opacity=".4"/>']
    for i in range(4):
        s.append(f'<line x1="{200+i*40}" y1="{hy+40+i*34}" x2="{880-i*40}" y2="{hy+40+i*34}" stroke="{t["gold"]}" stroke-width="5" stroke-linecap="round" opacity="{.35-i*.07:.2f}"/>')
    for j in range(3):
        bx = 230 + j * 70 + k * 30; by = 1380 + j * 40 - k * 20
        s.append(f'<path d="M{bx-16},{by-4} Q{bx-8},{by-12} {bx},{by} Q{bx+8},{by-12} {bx+16},{by-4}" fill="none" stroke="{t["art"]}" stroke-width="3" stroke-linecap="round" opacity=".6"/>')
    return "".join(s)

def m_feather(t, k, r):
    s = [f'<circle cx="320" cy="1560" r="300" fill="{t["gold"]}" opacity=".10" filter="url(#blur)"/>',
         f'<g transform="translate(300,1620) rotate({-28 + k*3})">'
         f'<path d="M0,-300 C110,-200 120,40 10,240 C-90,60 -90,-200 0,-300Z" fill="{t["gold"]}" opacity=".75"/>'
         f'<path d="M0,-290 C6,-100 10,80 10,330" fill="none" stroke="{t["art"]}" stroke-width="5" opacity=".7"/>'
         + "".join(f'<line x1="{6}" y1="{-230+i*40}" x2="{80 - abs(i-4)*6}" y2="{-270+i*40}" stroke="{t["bg"]}" stroke-width="3" opacity=".35"/>'
                   f'<line x1="{4}" y1="{-230+i*40}" x2="{-70 + abs(i-4)*6}" y2="{-266+i*40}" stroke="{t["bg"]}" stroke-width="3" opacity=".35"/>' for i in range(10))
         + '</g>']
    bx, by = 760 + k * 50, 1300 - k * 40
    s.append(f'<path d="M{bx-40},{by-8} Q{bx-20},{by-30} {bx},{by} Q{bx+20},{by-30} {bx+40},{by-8}" fill="none" stroke="{t["art"]}" stroke-width="5" stroke-linecap="round" opacity=".75"/>')
    return "".join(s)

def m_ink(t, k, r):
    s = [f'<circle cx="760" cy="1240" r="70" fill="{t["gold"]}" opacity=".8"/><circle cx="760" cy="1240" r="200" fill="{t["gold"]}" opacity=".12" filter="url(#blur)"/>']
    for i, (base, amp, op) in enumerate([(1500, 160, .16), (1620, 130, .24), (1740, 110, .34), (1840, 70, .5)]):
        pts = []; ph = r.uniform(0, 6) + k * .08 * (i + 1)
        for x in range(-20, W + 41, 40):
            y = base - amp * (.5 + .5 * math.sin(x / 170 + ph)) * (.6 + .4 * math.sin(x / 61 + ph * 2))
            pts.append(f"{x},{y:.0f}")
        s.append(f'<polygon points="-20,1920 {" ".join(pts)} {W+40},1920" fill="{t["art"]}" opacity="{op}"/>')
    return "".join(s)

def m_path(t, k, r):
    hy = 1260
    s = [f'<circle cx="540" cy="{hy}" r="260" fill="{t["gold"]}" opacity=".14" filter="url(#blur)"/>',
         f'<line x1="0" y1="{hy}" x2="{W}" y2="{hy}" stroke="{t["art"]}" stroke-width="2" opacity=".3"/>',
         f'<path d="M300,1920 C420,1700 640,1560 560,1420 C500,1330 540,1290 548,{hy} L556,{hy} C560,1300 600,1340 640,1420 C760,1580 640,1720 820,1920 Z" fill="{t["gold"]}" opacity=".28"/>']
    for _ in range(18):
        x = r.choice([r.uniform(30, 300), r.uniform(800, 1050)]); y = r.uniform(1300, 1880)
        s.append(leaf(x, y, r.uniform(.5, 1.1), r.uniform(0, 360), t["gold"], r.uniform(.25, .6)))
    fx = [610, 585, 560, 552][k]; fy = [1720, 1580, 1450, 1340][k]; sc = [1.0, .75, .55, .4][k]
    s.append(f'<g transform="translate({fx},{fy}) scale({sc})" fill="{t["art"]}" opacity=".85"><circle cx="0" cy="-130" r="22"/><rect x="-16" y="-104" width="32" height="90" rx="14"/>'
             f'<rect x="-14" y="-24" width="11" height="70" rx="5"/><rect x="3" y="-24" width="11" height="70" rx="5"/></g>')
    return "".join(s)

MOTIFS = {"moon": m_moon, "stars": m_stars, "sprout": m_sprout, "mirror": m_mirror, "rain": m_rain, "leaves": m_leaves,
          "lamp": m_lamp, "candle": m_candle, "sun": m_sun, "feather": m_feather, "ink": m_ink, "path": m_path}

def lines_html(lines, shown, cls):
    return "".join(f'<div class="{cls}{"" if i < shown else " h"}">{e(l)}</div>' for i, l in enumerate(lines))

def slide_html(it, k, state, t):
    rnd = random.Random(it.get("seed", 1))
    art = MOTIFS[it.get("motif", "moon")](t, k, rnd)
    head = (f'<div class="brand">its_poetogram</div>'
            f'<div class="series">अल्फ़ाज़ <i>·</i> {it["no"]:02d}</div>')
    q = it["quote"]
    if k == 0:
        body = f'<div class="box left"><div class="hook" id="fit" style="font-size:84px">{e(it["hook"])}</div><div class="rule"></div></div>'
    elif k == 1:
        L = len(q["lines"]); shown = min(state, L)
        qcls = "qen" if q["lang"] == "en" else "qhi"
        size = 88 if q["lang"] == "en" else 74
        gist = f'<div class="gist{"" if state >= L + 2 else " h"}">{e(it["gist"])}</div>' if it.get("gist") else ""
        body = (f'<div class="box center"><div id="fit" style="font-size:{size}px"><div class="qm">“</div>'
                f'<div class="{qcls}">{lines_html(q["lines"], shown, "ql")}</div>'
                f'<div class="att{"" if state > L else " h"}"><div class="who">— {e(q["author"])}</div><div class="work">{e(q["work"])}</div></div>'
                f'{gist}</div></div>')
    elif k == 2:
        body = (f'<div class="box left"><div class="lab">इसका मतलब समझो, तो…</div>'
                f'<div class="feel" id="fit" style="font-size:66px">{lines_html(it["feel"], state, "fl")}</div></div>')
    else:
        body = (f'<div class="box center"><div id="fit" style="font-size:70px"><div class="close">{e(it["close"])}</div>'
                f'<div class="ask">{e(it["ask"])}</div></div></div>'
                f'<div class="foot">SAVE <i>·</i> SEND <i>·</i> FOLLOW</div>')
    ff = f"file://{FONTS}"
    css = f"""
@font-face{{font-family:Tiro;src:url('{ff}/TiroDevanagariHindi-Regular.ttf')}}
@font-face{{font-family:Tiro;font-style:italic;src:url('{ff}/TiroDevanagariHindi-Italic.ttf')}}
@font-face{{font-family:NSD;src:url('{ff}/NotoSerifDevanagari%5Bwdth,wght%5D.ttf');font-weight:100 900}}
@font-face{{font-family:Corm;src:url('{ff}/CormorantGaramond%5Bwght%5D.ttf');font-weight:300 700}}
@font-face{{font-family:Corm;font-style:italic;src:url('{ff}/CormorantGaramond-Italic%5Bwght%5D.ttf');font-weight:300 700}}
html,body{{margin:0}}.page{{width:{W}px;height:{H}px;position:relative;overflow:hidden;
background:radial-gradient(ellipse 120% 80% at 50% 28%,{t['bg2']} 0%,{t['bg']} 72%);font-family:NSD,Tiro,serif;color:{t['fg']}}}
svg.m{{position:absolute;inset:0}}
.brand{{position:absolute;top:150px;width:100%;text-align:center;font:500 25px Corm;letter-spacing:12px;text-transform:uppercase;color:{t['sub']}}}
.series{{position:absolute;top:192px;width:100%;text-align:center;font:34px Tiro;letter-spacing:2px;color:{t['gold']}}}
.series i{{font-style:normal;color:{t['sub']}}}
.box{{position:absolute;left:92px;right:92px;top:300px;height:880px;display:flex;flex-direction:column;justify-content:center}}
.box.center{{text-align:center;align-items:center}} .box.center>#fit{{width:100%}}
.h{{opacity:0}}
.hook{{font-weight:600;line-height:1.42}}
.rule{{width:90px;height:4px;background:{t['gold']};margin-top:48px}}
.qm{{font:180px/0.5 Corm;color:{t['gold']};height:80px;opacity:.9}}
.qhi{{font-family:Tiro;line-height:1.55}} .qhi .ql:nth-child(2n){{margin-bottom:.45em}}
.qen{{font-family:Corm;font-style:italic;font-weight:500;line-height:1.22}}
.att{{margin-top:36px}} .who{{font:600 .44em NSD;letter-spacing:2px;color:{t['gold']}}} .work{{font:italic .4em Corm,Tiro;color:{t['sub']};margin-top:6px}}
.gist{{margin:34px auto 0;max-width:820px;font:400 .42em/1.5 NSD;color:{t['sub']};border-top:1px solid {t['sub']};padding-top:26px}}
.lab{{font:500 30px NSD;letter-spacing:2px;color:{t['gold']};margin-bottom:34px}}
.feel{{font-weight:600;line-height:1.45}} .fl{{margin-bottom:.4em}}
.close{{font-weight:600;line-height:1.42}}
.ask{{margin-top:42px;font:400 .52em NSD;color:{t['gold']}}}
.foot{{position:absolute;top:1230px;width:100%;text-align:center;font:600 28px Corm;letter-spacing:10px;color:{t['sub']}}}
.foot i{{font-style:normal;color:{t['gold']}}}
"""
    js = """<script>document.fonts.ready.then(()=>{const f=document.getElementById('fit'),b=document.querySelector('.box');if(f){let s=parseFloat(f.style.fontSize);
while((b.scrollHeight>b.clientHeight+1||f.scrollWidth>f.clientWidth+4)&&s>30){s-=2;f.style.fontSize=s+'px';}}document.body.dataset.ready=1;});</script>"""
    grain = (f'<filter id="g"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" seed="{it.get("seed",1)}"/>'
             f'<feColorMatrix values="0 0 0 0 .5 0 0 0 0 .5 0 0 0 0 .5 0 0 0 .07 0"/></filter><rect width="100%" height="100%" filter="url(#g)"/>')
    vign = f'<radialGradient id="vg" cx="50%" cy="45%" r="75%"><stop offset="60%" stop-color="#000" stop-opacity="0"/><stop offset="100%" stop-color="#000" stop-opacity=".35"/></radialGradient><rect width="100%" height="100%" fill="url(#vg)"/>'
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{css}</style></head><body><div class="page">'
            f'<svg class="m" width="{W}" height="{H}"><defs>{GLOW}</defs>{art}{vign}{grain}</svg>{head}{body}</div>{js}</body></html>')

def plan(it):
    """list of (k, state, duration). Durations tuned for reading speed."""
    q = it["quote"]; L = len(q["lines"]); P = []
    P.append((0, 0, 3.4))
    for i in range(1, L + 1):
        P.append((1, i, max(1.5, 0.7 + len(q["lines"][i - 1]) / 18)))
    P.append((1, L + 1, 2.0))
    if it.get("gist"): P.append((1, L + 2, max(3.2, 1.2 + len(it["gist"]) / 18)))
    else: P[-1] = (1, L + 1, 3.0)
    F = it["feel"]
    for i in range(1, len(F) + 1):
        P.append((2, i, 1.1 + len(F[i - 1]) / 24 + (1.0 if i == len(F) else 0)))
    P.append((3, 1, 4.3))
    return P

def build(it, b, tmp):
    t = THEMES[it.get("theme", "night")]
    P = plan(it); pngs = []
    for n, (k, st, d) in enumerate(P):
        fn_html = f"{tmp}/{it['id']}_{n}.html"; open(fn_html, "w").write(slide_html(it, k, st, t))
        pg = b.new_page(viewport={"width": W, "height": H}); pg.goto("file://" + fn_html)
        pg.wait_for_selector("body[data-ready]", timeout=15000); pg.wait_for_timeout(80)
        fn = f"{tmp}/{it['id']}_{n}.png"; pg.screenshot(path=fn); pg.close(); pngs.append(fn)
    xfs = [(0.75 if P[i][0] != P[i - 1][0] else 0.4) for i in range(1, len(P))]
    durs = [d for _, _, d in P]
    total = sum(durs) - sum(xfs)
    offs, o = [], 0.0
    for i in range(1, len(P)):
        o += durs[i - 1] - xfs[i - 1]; offs.append(o)
    trans = [offs[i - 1] + xfs[i - 1] / 2 for i in range(1, len(P)) if P[i][0] != P[i - 1][0]]
    music = f"{tmp}/{it['id']}.wav"
    subprocess.run(["python3", os.path.join(HERE, "music3.py"), music, str(it.get("seed", 1)), f"{total:.2f}",
                    ",".join(f"{x:.2f}" for x in trans), it.get("mood", ""), "soft"], check=True, capture_output=True)
    cmd = ["ffmpeg", "-y", "-loglevel", "error"]
    for p, d in zip(pngs, durs): cmd += ["-loop", "1", "-t", f"{d:.2f}", "-framerate", "30", "-i", p]
    cmd += ["-i", music]
    fc, last = [], "[0:v]"
    for i in range(1, len(P)):
        fc.append(f"{last}[{i}:v]xfade=transition=fade:duration={xfs[i-1]}:offset={offs[i-1]:.2f}[x{i}]"); last = f"[x{i}]"
    N = int(total * 30)
    fc.append(f"{last}scale=2160:3840,zoompan=z='1+0.04*on/{N}':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps=30,format=yuv420p[v]")
    out = os.path.join(ROOT, "reels", it["id"] + ".mp4")
    cmd += ["-filter_complex", ";".join(fc), "-map", "[v]", "-map", f"{len(P)}:a", "-t", f"{total:.2f}", "-c:v", "libx264", "-preset", "medium",
            "-crf", "20", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", "48000", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out]
    subprocess.run(cmd, check=True, capture_output=True)
    # cover = full quote slide (most shareable frame)
    qi = max(i for i, (k, _, _) in enumerate(P) if k == 1)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", pngs[qi], "-q:v", "2", os.path.join(ROOT, "covers", it["id"] + ".jpg")], check=True)
    print("ok", it["id"], it.get("motif"), it.get("theme"), f"{total:.1f}s", flush=True)

def caption(it):
    q = it["quote"]
    parts = [it["hook"], "", "“" + "\n".join(q["lines"]) + "”", f"— {q['author']}, {q['work']}"]
    if it.get("gist"): parts += ["", it["gist"]]
    parts += ["", "\n".join(it["feel"]), "", f"{it['close']} {it['ask']} 👇", "",
              "Save karo, aur us insaan ko bhejo jise aaj ye padhna zaroori hai.",
              "Follow @its_poetogram — roz ek line, jo dil mein reh jaaye.", "",
              f"अल्फ़ाज़ · {it['no']:02d}", "", it["kw"], "", it["tags"]]
    return "\n".join(parts)

if __name__ == "__main__":
    path = sys.argv[1]; data = json.load(open(path)); items = data["items"]; want = set(sys.argv[2:])
    for n, it in enumerate(items, 1):
        it.setdefault("no", n); it.setdefault("seed", 300 + n); it["caption"] = caption(it)
    json.dump(data, open(path, "w"), ensure_ascii=False, indent=1)
    tmp = "/tmp/alfaaz"; os.makedirs(tmp, exist_ok=True)
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        for it in items:
            if it["id"] in want or "all" in want: build(it, b, tmp)
        b.close()
