#!/usr/bin/env python3
"""its_poetogram "नज़रिया / PERSPECTIVE" reels — editorial, brand-grade, 4 slides (~20 s):
  1 hook (provocative claim, Hindi)  2 quote (original English + author, work, year; optional Hindi gist)
  3 perspective (Hindi, 2-4 lines, example / twist)  4 debate (question + option A / option B + CTA)
Visual language: a quiet field of identical marks (the crowd) with ONE gold mark that differs (the individual).
Usage: python3 tools/think.py thoughts.json ID [ID ...]   → reels/ID.mp4, covers/ID.jpg"""
import json, os, sys, math, random, html, subprocess
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
W, H = 1080, 1920
e = html.escape
THEMES = {
    "ink":   dict(bg="#101012", bg2="#1b1b1f", fg="#f2ede4", sub="#8f8a80", mark="#f2ede4", markop=.13, gold="#c9a25a"),
    "ivory": dict(bg="#f1ece2", bg2="#e6dfd2", fg="#17150f", sub="#6f675a", mark="#17150f", markop=.12, gold="#b07b2c"),
    "slate": dict(bg="#18222b", bg2="#22303b", fg="#eef1f2", sub="#8a9aa6", mark="#eef1f2", markop=.12, gold="#d1a95e"),
    "wine":  dict(bg="#2a1418", bg2="#3a1d22", fg="#f4e9e4", sub="#a8888a", mark="#f4e9e4", markop=.12, gold="#d8b06a"),
}

# ---------------- motifs: (theme, slide index 0..3, rnd) -> svg ----------------
def m_grid(t, k, r):
    s = []; gx, gy = 9, 15; sp = W / gx
    ox, oy = 4, 9
    for i in range(gx):
        for j in range(gy):
            if (i, j) == (ox, oy): continue
            s.append(f'<circle cx="{(i+.5)*sp:.0f}" cy="{(j+.5)*sp*1.02+30:.0f}" r="7" fill="{t["mark"]}" opacity="{t["markop"]*1.6:.2f}"/>')
    dx = k * 26; dy = -k * 34
    s.append(f'<circle cx="{(ox+.5)*sp+dx:.0f}" cy="{(oy+.5)*sp*1.02+30+dy:.0f}" r="11" fill="{t["gold"]}"/>')
    return s

def bird(x, y, sc, col, op, flip=False):
    f = -1 if flip else 1
    return (f'<path d="M{x-22*sc*f:.0f},{y-6*sc:.0f} Q{x-10*sc*f:.0f},{y-14*sc:.0f} {x:.0f},{y:.0f} Q{x+10*sc*f:.0f},{y-14*sc:.0f} {x+22*sc*f:.0f},{y-6*sc:.0f}" '
            f'fill="none" stroke="{col}" stroke-width="{3*sc:.1f}" stroke-linecap="round" opacity="{op}"/>')

def m_flock(t, k, r):
    s = []
    for _ in range(85):
        x, y = r.uniform(40, W - 40), r.uniform(1050, 1800)
        s.append(bird(x - k * 18, y, r.uniform(.8, 1.4), t["mark"], f'{t["markop"]*2:.2f}'))
    s.append(bird(W * .7 + k * 40, 1320 - k * 30, 1.8, t["gold"], 1))
    return s

def m_people(t, k, r):
    s = []; base = 1700
    for i in range(22):
        x = 60 + i * 44; h = r.uniform(130, 150)
        s.append(f'<rect x="{x-6}" y="{base-h:.0f}" width="12" height="{h:.0f}" rx="6" fill="{t["mark"]}" opacity="{t["markop"]*2:.2f}"/>'
                 f'<circle cx="{x}" cy="{base-h-16:.0f}" r="11" fill="{t["mark"]}" opacity="{t["markop"]*2:.2f}"/>')
    gx = W * .5 + 60 + k * 30; gb = base - 300 - k * 20
    s.append(f'<rect x="{gx-7:.0f}" y="{gb-160:.0f}" width="14" height="160" rx="7" fill="{t["gold"]}"/><circle cx="{gx:.0f}" cy="{gb-178:.0f}" r="13" fill="{t["gold"]}"/>')
    s.append(f'<line x1="40" y1="{base}" x2="{W-40}" y2="{base}" stroke="{t["mark"]}" stroke-width="2" opacity="{t["markop"]*2:.2f}"/>')
    return s

def m_steps(t, k, r):
    s = []
    for col in range(5):
        x0 = 120 + col * 200
        for i in range(9):
            y = 1820 - i * 80
            s.append(f'<ellipse cx="{x0 + (14 if i%2 else -14)}" cy="{y}" rx="9" ry="16" fill="{t["mark"]}" opacity="{t["markop"]*1.8:.2f}"/>')
    # gold path curving away
    for i in range(9 + k):
        a = i / 8
        x = 520 + 380 * a * a + (14 if i % 2 else -14); y = 1820 - i * 80
        s.append(f'<ellipse cx="{x:.0f}" cy="{y}" rx="10" ry="17" fill="{t["gold"]}" opacity="{min(1,.35 + i*.08):.2f}" transform="rotate({35*a:.0f} {x:.0f} {y})"/>')
    return s

def m_chairs(t, k, r):
    s = []
    def chair(x, y, col, op, rot=0):
        return (f'<g transform="rotate({rot} {x} {y})" opacity="{op}"><rect x="{x-20}" y="{y-20}" width="40" height="8" fill="{col}"/>'
                f'<rect x="{x-20}" y="{y-60}" width="6" height="48" fill="{col}"/><rect x="{x-20}" y="{y-12}" width="5" height="34" fill="{col}"/><rect x="{x+15}" y="{y-12}" width="5" height="34" fill="{col}"/></g>')
    for row in range(6):
        for c in range(8):
            if (row, c) == (3, 5): continue
            s.append(chair(110 + c * 122, 1180 + row * 110, t["mark"], f'{t["markop"]*2:.2f}'))
    s.append(chair(110 + 5 * 122, 1180 + 3 * 110, t["gold"], 1, 180 if k >= 1 else 0))
    return s

def m_ripple(t, k, r):
    s = []; cx, cy = W * .5, 1420
    for i in range(1, 16):
        s.append(f'<circle cx="{cx:.0f}" cy="{cy}" r="{i*48 + k*10}" fill="none" stroke="{t["mark"]}" stroke-width="2" opacity="{t["markop"]*1.8*(1-i/18):.2f}"/>')
    s.append(f'<circle cx="{cx:.0f}" cy="{cy}" r="12" fill="{t["gold"]}"/>')
    return s

def m_arrows(t, k, r):
    s = []
    def arrow(x, y, ang, col, op, sc=1):
        return (f'<g transform="translate({x},{y}) rotate({ang}) scale({sc})" opacity="{op}"><line x1="-22" y1="0" x2="18" y2="0" stroke="{col}" stroke-width="4" stroke-linecap="round"/>'
                f'<path d="M8,-10 L22,0 L8,10" fill="none" stroke="{col}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/></g>')
    for i in range(8):
        for j in range(9):
            if (i, j) == (5, 4): continue
            s.append(arrow(95 + i * 128, 1060 + j * 92, 0, t["mark"], f'{t["markop"]*2:.2f}'))
    s.append(arrow(95 + 5 * 128, 1060 + 4 * 92, 180 - k * 20, t["gold"], 1, 1.4))
    return s

def m_umbrellas(t, k, r):
    s = []
    for i in range(7):
        for j in range(6):
            x, y = 110 + i * 145 + (70 if j % 2 else 0), 1100 + j * 130
            if (i, j) == (3, 3): continue
            if x > W - 40: continue
            s.append(f'<circle cx="{x}" cy="{y+80}" r="56" fill="{t["mark"]}" opacity="{t["markop"]*.8:.2f}"/>'
                     + "".join(f'<line x1="{x}" y1="{y+80}" x2="{x+56*math.cos(a):.0f}" y2="{y+80+56*math.sin(a):.0f}" stroke="{t["bg"]}" stroke-width="2" opacity=".5"/>' for a in [n*math.pi/4 for n in range(8)]))
    x, y = 110 + 3 * 145 + 70, 1180 + 3 * 130 - k * 12
    s.append(f'<circle cx="{x}" cy="{y}" r="62" fill="{t["gold"]}"/>' + "".join(f'<line x1="{x}" y1="{y}" x2="{x+62*math.cos(a):.0f}" y2="{y+62*math.sin(a):.0f}" stroke="{t["bg"]}" stroke-width="2" opacity=".35"/>' for a in [n*math.pi/4 for n in range(8)]))
    return s

def m_hill(t, k, r):
    s = [f'<path d="M-20,1880 L{W*.82:.0f},1060 L{W+20},1180 L{W+20},1920 L-20,1920 Z" fill="{t["mark"]}" opacity="{t["markop"]*1.1:.2f}"/>']
    p = .45 + k * .06; x = -20 + (W * .82 + 20) * p; y = 1880 - (820) * p
    s.append(f'<circle cx="{x+18:.0f}" cy="{y-40:.0f}" r="38" fill="{t["gold"]}"/>')
    s.append(f'<rect x="{x-30:.0f}" y="{y-96:.0f}" width="12" height="70" rx="6" fill="{t["fg"]}" opacity=".75" transform="rotate(30 {x-24:.0f} {y-60:.0f})"/><circle cx="{x-44:.0f}" cy="{y-108:.0f}" r="11" fill="{t["fg"]}" opacity=".75"/>')
    return s

def m_door(t, k, r):
    s = []
    for i in range(7):
        x = 90 + i * 140
        if i == 4: continue
        s.append(f'<rect x="{x}" y="1150" width="90" height="190" rx="45" fill="none" stroke="{t["mark"]}" stroke-width="3" opacity="{t["markop"]*2.4:.2f}"/>')
    s.append(f'<rect x="{90+4*140}" y="1150" width="90" height="190" rx="45" fill="{t["gold"]}" opacity="{.55+k*.15:.2f}"/>')
    s.append(f'<path d="M{90+4*140},1340 L{90+4*140-120-k*20},1820 L{90+4*140+210+k*20},1820 L{90+4*140+90},1340 Z" fill="{t["gold"]}" opacity=".12"/>')
    return s

MOTIFS = {"grid": m_grid, "flock": m_flock, "people": m_people, "steps": m_steps, "chairs": m_chairs,
          "ripple": m_ripple, "arrows": m_arrows, "umbrellas": m_umbrellas, "hill": m_hill, "door": m_door}

def slide_html(it, k, t):
    rnd = random.Random(it.get("seed", 1))
    motif = "".join(MOTIFS[it.get("motif", "grid")](t, k, rnd))
    no = it["no"]
    head = (f'<div class="brand">its_poetogram</div>'
            f'<div class="series"><span>नज़रिया</span> <i>·</i> {no:02d} <i>·</i> <em>PERSPECTIVE</em></div>')
    if k == 0:
        body = f'<div class="box"><div class="big" id="fit" style="font-size:92px">{e(it["hook"])}</div><div class="rule"></div></div>'
    elif k == 1:
        q = it["quote"]
        gist = f'<div class="gist">{e(q["hi"])}</div>' if q.get("hi") else ""
        body = (f'<div class="box"><div class="qm">“</div><div class="quote" id="fit" style="font-size:{q.get("size",64)}px">{e(q["text"])}</div>'
                f'<div class="who">— {e(q["author"]).upper()}</div><div class="work">{e(q["work"])}</div>{gist}</div>')
    elif k == 2:
        lines = "".join(f'<div class="pl">{e(l)}</div>' for l in it["perspective"])
        body = f'<div class="box"><div class="lab">एक अलग नज़रिया</div><div class="persp" id="fit" style="font-size:66px">{lines}</div></div>'
    else:
        body = (f'<div class="box"><div class="lab">आप किस तरफ़ हो?</div><div class="ques" id="fit" style="font-size:66px">{e(it["question"])}</div>'
                f'<div class="opts"><div class="opt"><b>A</b>{e(it["a"])}</div><div class="opt"><b>B</b>{e(it["b"])}</div></div>'
                f'<div class="cta">Comment में A या B लिखो — वजह के साथ</div></div>')
    css = f"""html,body{{margin:0}}.page{{width:{W}px;height:{H}px;position:relative;overflow:hidden;
background:radial-gradient(ellipse at 50% 30%,{t['bg2']} 0%,{t['bg']} 70%);font-family:FreeSerif;color:{t['fg']}}}
svg.m{{position:absolute;inset:0}}
.brand{{position:absolute;top:150px;width:100%;text-align:center;font:24px FreeSerif;letter-spacing:10px;text-transform:uppercase;color:{t['sub']}}}
.series{{position:absolute;top:196px;width:100%;text-align:center;font-size:30px;letter-spacing:3px;color:{t['gold']}}}
.series i{{font-style:normal;color:{t['sub']}}} .series em{{font-style:normal;font-size:22px;letter-spacing:8px;color:{t['sub']}}}
.box{{position:absolute;left:96px;right:96px;top:320px;height:780px;display:flex;flex-direction:column;justify-content:center}}
.big{{font-weight:bold;line-height:1.38;text-align:left}}
.rule{{width:90px;height:4px;background:{t['gold']};margin-top:46px}}
.qm{{font-size:200px;line-height:.6;color:{t['gold']};height:90px}}
.quote{{font-style:italic;line-height:1.35}}
.who{{margin-top:40px;font-size:30px;letter-spacing:5px;color:{t['gold']}}} .work{{font-size:30px;font-style:italic;color:{t['sub']};margin-top:6px}}
.gist{{margin-top:34px;font-size:38px;color:{t['sub']};line-height:1.45;border-left:3px solid {t['gold']};padding-left:22px}}
.lab{{font-size:30px;letter-spacing:4px;color:{t['gold']};margin-bottom:30px}}
.persp{{font-weight:bold;line-height:1.42}} .pl{{margin-bottom:.35em}}
.ques{{font-weight:bold;line-height:1.38}}
.opts{{margin-top:40px}} .opt{{font-size:40px;line-height:1.35;padding:18px 0;border-top:1px solid {t['sub']};display:flex;gap:26px}}
.opt b{{color:{t['gold']};font-family:FreeSans;font-size:34px;min-width:30px}}
.cta{{margin-top:30px;font-size:30px;color:{t['sub']};letter-spacing:1px}}
.foot{{position:absolute;bottom:250px;width:100%;text-align:center;font-size:26px;letter-spacing:6px;color:{t['sub']}}}
"""
    foot = '<div class="foot">SAVE · SHARE · FOLLOW</div>' if k == 3 else ""
    js = """<script>(()=>{const f=document.getElementById('fit'),b=document.querySelector('.box');if(!f)return;let s=parseFloat(f.style.fontSize);
while((b.scrollHeight>b.clientHeight+1||f.scrollWidth>f.clientWidth+14)&&s>30){s-=2;f.style.fontSize=s+'px';}})();</script>"""
    grain = (f'<filter id="g"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" seed="{it.get("seed",1)}"/>'
             f'<feColorMatrix values="0 0 0 0 .5 0 0 0 0 .5 0 0 0 0 .5 0 0 0 .08 0"/></filter><rect width="100%" height="100%" filter="url(#g)"/>')
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{css}</style></head><body><div class="page">'
            f'<svg class="m" width="{W}" height="{H}">{motif}{grain}</svg>{head}{body}{foot}</div>{js}</body></html>')

def build(it, b, tmp):
    t = THEMES[it.get("theme", "ink")]
    pngs = []
    for k in range(4):
        pg = b.new_page(viewport={"width": W, "height": H}); pg.set_content(slide_html(it, k, t)); pg.wait_for_timeout(120)
        fn = f"{tmp}/{it['id']}_{k}.png"; pg.screenshot(path=fn); pg.close(); pngs.append(fn)
    q = it["quote"]["text"]
    durs = [3.4, max(5.5, 2.5 + len(q) / 22), 2.2 + 0.9 * len(it["perspective"]) + sum(len(l) for l in it["perspective"]) / 45, 6.0]
    xf = 0.5; total = sum(durs) - xf * 3
    music = f"{tmp}/{it['id']}.wav"
    trans, o = [], 0.0
    for d in durs[:-1]:
        o += d - xf; trans.append(o + xf / 2)
    moodmap = {"piano": "dark", "strings": "tense", "guitar": "hopeful", "sitar": "eastern"}
    mood = it.get("mood") or moodmap.get(it.get("music", ""), None)
    subprocess.run(["python3", os.path.join(HERE, "music3.py"), music, str(it.get("seed", 1)), f"{total:.2f}",
                    ",".join(f"{t:.2f}" for t in trans)] + ([mood] if mood else []), check=True, capture_output=True)
    cmd = ["ffmpeg", "-y", "-loglevel", "error"]
    for p, d in zip(pngs, durs): cmd += ["-loop", "1", "-t", f"{d:.2f}", "-framerate", "30", "-i", p]
    cmd += ["-i", music]
    fc, last, off = [], "[0:v]", 0.0
    for i in range(1, 4):
        off += durs[i - 1] - xf
        fc.append(f"{last}[{i}:v]xfade=transition=fade:duration={xf}:offset={off:.2f}[x{i}]"); last = f"[x{i}]"
    N = int(total * 30)
    fc.append(f"{last}scale=2160:3840,zoompan=z='1+0.035*on/{N}':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps=30,format=yuv420p[v]")
    out = os.path.join(ROOT, "reels", it["id"] + ".mp4")
    cmd += ["-filter_complex", ";".join(fc), "-map", "[v]", "-map", "4:a", "-t", f"{total:.2f}", "-c:v", "libx264", "-preset", "medium",
            "-crf", "20", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", "48000", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out]
    subprocess.run(cmd, check=True, capture_output=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", pngs[0], "-q:v", "2", os.path.join(ROOT, "covers", it["id"] + ".jpg")], check=True)
    print("ok", it["id"], it.get("motif"), it.get("theme"), f"{total:.1f}s", flush=True)

if __name__ == "__main__":
    items = json.load(open(sys.argv[1]))["items"]; want = set(sys.argv[2:])
    tmp = "/tmp/think"; os.makedirs(tmp, exist_ok=True)
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        for it in items:
            if it["id"] in want or "all" in want: build(it, b, tmp)
        b.close()
