#!/usr/bin/env python3
"""its_poetogram v6 "sketchbook" still reels (from 28 Nov 2026).
One ink illustration (cream paper, one red object) + two lines (line 1 ink, line 2 red) + handwritten signature,
slow 4% push-in, soft original music, ~10 s. Text is set by code (never AI-drawn).
Input: lines.json items {id, line1, line2, art (path to the illustration png/jpg), mood?, seed?, caption}
Usage: python3 tools/still.py lines.json ID [ID ...] | all   -> reels/ID.mp4, covers/ID.jpg"""
import json, os, sys, html, subprocess
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); FONTS = os.path.join(HERE, "fonts")
W, H = 1080, 1920; DUR = 10.0
INK, RED = "#1c1915", "#a3161c"
e = html.escape

def page(it):
    art = "file://" + os.path.abspath(os.path.join(ROOT, it["art"]))
    ff = "file://" + FONTS
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:NSD;src:url('{ff}/NotoSerifDevanagari%5Bwdth,wght%5D.ttf');font-weight:100 900}}
@font-face{{font-family:Cav;src:url('{ff}/Caveat%5Bwght%5D.ttf');font-weight:400 700}}
html,body{{margin:0}} .p{{width:{W}px;height:{H}px;position:relative;overflow:hidden;background:#efe6d3}}
.art{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}}
.txt{{position:absolute;left:90px;right:90px;top:300px;height:520px;display:flex;flex-direction:column;justify-content:center;text-align:center;font-family:NSD}}
.l1{{color:{INK};font-weight:600;line-height:1.4;white-space:nowrap}} .l2{{color:{RED};font-weight:700;line-height:1.4;margin-top:.25em;white-space:nowrap}}
.sig{{position:absolute;left:0;right:0;bottom:120px;text-align:center;font:600 50px Cav;color:{INK};opacity:.85;transform:rotate(-3deg)}}
.sig b{{color:{RED};font-weight:600}}
</style></head><body><div class="p"><img class="art" src="{art}">
<div class="txt" id="t" style="font-size:68px"><div class="l1">{e(it['line1'])}</div><div class="l2">{e(it['line2'])}</div></div>
<div class="sig">its<b>_</b>poetogram</div></div>
<script>document.fonts.ready.then(()=>{{const t=document.getElementById('t');let s=68;
while(t.scrollHeight>t.clientHeight+1&&s>36){{s-=2;t.style.fontSize=s+'px';}}
for(const d of t.children){{while(d.scrollWidth>d.clientWidth+2&&s>36){{s-=2;t.style.fontSize=s+'px';}}}}
document.body.dataset.ready=1;}});</script></body></html>"""

def build(it, b, tmp):
    fh = f"{tmp}/{it['id']}.html"; open(fh, "w").write(page(it))
    pg = b.new_page(viewport={"width": W, "height": H}); pg.goto("file://" + fh)
    pg.wait_for_selector("body[data-ready]", timeout=15000); pg.wait_for_timeout(150)
    png = f"{tmp}/{it['id']}.png"; pg.screenshot(path=png); pg.close()
    wav = f"{tmp}/{it['id']}.wav"
    subprocess.run(["python3", os.path.join(HERE, "music3.py"), wav, str(it.get("seed", 7)), f"{DUR}", "", it.get("mood", "dark"), "soft"],
                   check=True, capture_output=True)
    N = int(DUR * 30); out = os.path.join(ROOT, "reels", it["id"] + ".mp4")
    vf = (f"scale=2160:3840,zoompan=z='1+0.04*on/{N}':d={N}:x='iw/2-(iw/zoom/2)':y='ih*0.42-(ih/zoom*0.42)':s=1080x1920:fps=30,"
          f"noise=alls=4:allf=t,format=yuv420p")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-framerate", "30", "-t", f"{DUR}", "-i", png, "-i", wav,
                    "-vf", vf, "-t", f"{DUR}", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                    "-af", "loudnorm=I=-14:TP=-1.5:LRA=11,afade=t=in:d=0.3,afade=t=out:st=8.6:d=1.4", "-ar", "48000",
                    "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out], check=True, capture_output=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", png, "-q:v", "2", os.path.join(ROOT, "covers", it["id"] + ".jpg")], check=True)
    print("ok", it["id"], flush=True)

if __name__ == "__main__":
    items = json.load(open(sys.argv[1]))["items"]; want = set(sys.argv[2:])
    tmp = "/tmp/still"; os.makedirs(tmp, exist_ok=True)
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        for it in items:
            if it["id"] in want or "all" in want: build(it, b, tmp)
        b.close()
