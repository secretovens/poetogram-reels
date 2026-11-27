#!/usr/bin/env python3
"""v3 reel builder: 7 rotating visual styles, line- or word-reveal, hook text on top, CTA at the end,
slow camera push-in, original music in 6 moods.
Usage: python3 tools/reel3.py content.json ID [ID ...]
Item fields used: id, lines, accent, art, tag, seed, style, music, hook, cta
Outputs: reels/ID.mp4 (1080x1920, H.264/AAC), covers/ID.jpg"""
import json, os, subprocess, sys, html, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from styles import P, background, base_css, words_with_accent, CHALK_FILTER
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
W, H = 1080, 1920
ZONES = {  # quote block top/bottom in px
    "scene": (350, 900),
    "parchment": (430, 980), "noir": (400, 1300), "diary": (440, 1260), "night": (420, 1120),
    "poster": (560, 1460), "dusk": (420, 1240), "chalk": (420, 1300)}
F0 = {"scene": 84, "parchment": 76, "noir": 96, "diary": 76, "night": 78, "poster": 100, "dusk": 80, "chalk": 88}
MOOD = {"scene": "guitar", "parchment": "piano", "noir": "strings", "diary": "guitar", "night": "sitar",
        "poster": "piano", "dusk": "santoor", "chalk": "musicbox"}
CTAS = {
    "send": "उसे भेजो, जिसे ये सुनना ज़रूरी है  ↗",
    "save": "Save कर लो — किसी दिन ये याद आएगा",
    "comment": "सच है या नहीं? Comment में बताओ",
    "tag": "उस दोस्त को टैग करो जो ये समझेगा",
}

def page_html(it):
    st = it["style"]; p = P[st]; top, bot = ZONES[st]
    units, ui = [], 0
    lines_html = []
    for li, line in enumerate(it["lines"]):
        ws = words_with_accent(line, it.get("accent", ""))
        if p["mode"] == "line":
            inner = " ".join(f'<span class="acc">{html.escape(w)}</span>' if a else html.escape(w) for w, a in ws)
            lines_html.append(f'<span class="u" data-i="{ui}">{inner}</span>'); ui += 1
        else:
            spans = []
            for w, a in ws:
                spans.append(f'<span class="u{" acc" if a else ""}" data-i="{ui}">{html.escape(w)}</span>'); ui += 1
            lines_html.append(" ".join(spans))
    n_units = ui
    tag = html.escape(it.get("tag", ""))
    hook = html.escape(it.get("hook", ""))
    cta = html.escape(CTAS.get(it.get("cta", "send"), it.get("cta", "")))
    align = p["align"]
    pad_l = 170 if st == "diary" else 90
    css = base_css(st, W, H) + f"""
.u{{opacity:0}}.ln{{white-space:nowrap}}
.hook{{position:absolute;top:{200 if st=='scene' else 235}px;left:{pad_l}px;right:90px;text-align:{align};font-size:50px;line-height:1.35;font-weight:bold}}
.zone{{position:absolute;top:{top}px;left:{pad_l}px;right:90px;height:{bot-top}px;display:flex;flex-direction:column;justify-content:center}}
.tag{{font-size:30px;letter-spacing:3px;margin-bottom:28px;text-align:{align};font-weight:normal}}
.handle{{font-size:28px;letter-spacing:2px;margin-top:34px;text-align:{align};font-weight:normal;opacity:0}}
.cta{{position:absolute;left:0;right:0;top:{min(bot + 60, 1480)}px;text-align:center;opacity:0}}
.cta span{{display:inline-block;padding:20px 36px;border-radius:60px;font:bold 38px FreeSans;
  background:{p['fg']};color:{'#111' if st in ('noir','night','dusk','chalk','scene') else '#fff'}}}
"""
    if st == "diary":
        css += ".q{line-height:74px}.zone{justify-content:flex-start;padding-top:20px}"
    body = (f'<div class="page">{background(st, W, H, it.get("seed", 1), it.get("art"), None, it.get("scene"))}{CHALK_FILTER if st == "chalk" else ""}'
            f'<div class="hook sub">{hook}</div>'
            f'<div class="zone"><div class="tag sub">{"— " + tag + " —" if align == "center" else tag}</div>'
            f'<div class="q" id="q">{"<br>".join(chr(60)+"span class=ln"+chr(62)+l+"</span>" for l in lines_html)}</div><div class="handle sub" id="h">@its_poetogram</div></div>'
            f'<div class="cta" id="cta"><span>{cta}</span></div></div>')
    js = f"""<script>
(()=>{{const q=document.getElementById('q'), z=document.querySelector('.zone');
let f={F0[st]}; q.style.fontSize=f+'px';
function fits(){{ return z.scrollHeight<= z.clientHeight+1 && q.scrollWidth<=q.clientWidth+2 }}
while(!fits() && f>40){{ f-=2; q.style.fontSize=f+'px'; }}
{"q.style.lineHeight=Math.max(74, Math.round(f*1.3))+'px';" if st=='diary' else ""}
window.setState=(n,a,cta,handle)=>{{
  document.querySelectorAll('.u').forEach(e=>{{const i=+e.dataset.i; e.style.opacity = i<n?1:(i==n?a:0);}});
  document.getElementById('cta').style.opacity=cta; document.getElementById('h').style.opacity=handle;
}};}})();
</script>"""
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{css}</style></head><body>{body}{js}</body></html>', n_units

def timeline(it, n_units):
    st = it["style"]; mode = P[st]["mode"]
    fr = [((0, 0, 0, 0), 0.55)]
    if mode == "line":
        for i, line in enumerate(it["lines"]):
            for a in (.3, .65): fr.append(((i, a, 0, 0), 0.08))
            last = i == len(it["lines"]) - 1
            fr.append(((i + 1, 0, 0, 1 if last else 0), 3.3 if last else 0.75 + 0.16 * len(line.split())))
    else:
        ends = []; k = 0
        for line in it["lines"]:
            k += len(line.split()); ends.append(k)
        for i in range(n_units):
            fr.append(((i, .5, 0, 0), 0.06))
            last = i == n_units - 1
            hold = 3.3 if last else (0.30 + (0.42 if (i + 1) in ends else 0))
            fr.append(((i + 1, 0, 0, 1 if last else 0), hold))
    n = n_units
    for a in (.35, .7): fr.append(((n, 0, a, 1), 0.08))
    fr.append(((n, 0, 1, 1), 2.6))
    return fr

def build(it, pw_page, tmp):
    html_s, n_units = page_html(it)
    pw_page.set_content(html_s); pw_page.wait_for_timeout(150)
    frames = timeline(it, n_units)
    lst = []
    for k, ((n, a, c, h), d) in enumerate(frames):
        pw_page.evaluate(f"setState({n},{a},{c},{h})")
        fn = f"{tmp}/{it['id']}_{k:03d}.png"; pw_page.screenshot(path=fn); lst.append((fn, d))
    # cover = full text, no CTA
    pw_page.evaluate(f"setState({n_units},0,0,1)")
    cover_png = f"{tmp}/{it['id']}_cover.png"; pw_page.screenshot(path=cover_png)
    total = sum(d for _, d in lst)
    with open(f"{tmp}/{it['id']}.txt", "w") as f:
        for fn, d in lst: f.write(f"file '{fn}'\nduration {d:.3f}\n")
        f.write(f"file '{lst[-1][0]}'\n")
    music = f"{tmp}/{it['id']}.wav"
    SKYMOOD = {"golden": "guitar", "sunrise": "santoor", "dusk": "strings", "night": "sitar", "rain": "piano", "day": "musicbox", "pink": "musicbox"}
    mood = it.get("music") or (SKYMOOD.get(it.get("scene", {}).get("sky"), "guitar") if it["style"] == "scene" else MOOD[it["style"]])
    subprocess.run(["python3", os.path.join(HERE, "music2.py"), music, mood, str(it.get("seed", 1)), f"{total:.2f}"], check=True, capture_output=True)
    out = os.path.join(ROOT, "reels", it["id"] + ".mp4")
    zoom = "scale=2160:3840,zoompan=z='1+0.05*on/{N}':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps=30".replace("{N}", str(int(total * 30)))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", f"{tmp}/{it['id']}.txt", "-i", music,
                    "-vf", f"fps=30,{zoom},format=yuv420p", "-map", "0:v", "-map", "1:a", "-t", f"{total:.2f}",
                    "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out],
                   check=True, capture_output=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", cover_png, "-q:v", "2", os.path.join(ROOT, "covers", it["id"] + ".jpg")], check=True)
    print("ok", it["id"], it["style"], mood, f"{total:.1f}s", flush=True)

if __name__ == "__main__":
    items = json.load(open(sys.argv[1]))["items"]; want = set(sys.argv[2:])
    tmp = "/tmp/reel3"; os.makedirs(tmp, exist_ok=True)
    for d in ("reels", "covers"): os.makedirs(os.path.join(ROOT, d), exist_ok=True)
    with sync_playwright() as pw:
        b = pw.chromium.launch(); pg = b.new_page(viewport={"width": W, "height": H})
        for it in items:
            if it["id"] in want or "all" in want:
                pg = b.new_page(viewport={"width": W, "height": H}); build(it, pg, tmp); pg.close()
        b.close()
