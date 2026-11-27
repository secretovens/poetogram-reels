#!/usr/bin/env python3
"""Carousel builder (1080x1350 JPEG slides) in the same 7 styles as the reels.
Usage: python3 tools/carousel.py carousels.json ID [ID ...]
Item: {id, style, art, seed, title, sub, points:[{text, note?} | {a, b}], labels:[A,B]?, end, cta, caption}
Outputs: carousels/ID/01.jpg ..."""
import json, os, sys, html, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from styles import P, background, base_css, CHALK_FILTER
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
W, H = 1080, 1350
e = html.escape

def slide(it, kind, i=0, total=0, pt=None):
    st = it["style"]; p = P[st]; al = p["align"]
    padl = 170 if st == "diary" else 96
    dark_btn = st in ("noir", "night", "dusk", "chalk")
    css = base_css(st, W, H) + f"""
.wrap{{position:absolute;left:{padl}px;right:96px;top:150px;bottom:190px;display:flex;flex-direction:column;justify-content:center;text-align:{al}}}
.lab{{font-size:30px;letter-spacing:4px}} .big{{font-weight:bold;line-height:1.35}} .num{{font:bold 120px FreeSans;line-height:1;margin-bottom:30px;color:{p['acc'] if st!='poster' else '#d7262e'}}}
.note{{font-size:46px;margin-top:34px;line-height:1.45}} .pnote{{color:{p['fg']};opacity:.82;font-weight:bold}} .pair{{margin:0 0 46px}} .pl{{font:bold 30px FreeSans;letter-spacing:3px;margin-bottom:8px;color:{p['acc'] if st!='poster' else '#d7262e'}}}
.foot{{position:absolute;left:{padl}px;right:96px;bottom:80px;display:flex;justify-content:space-between;font-size:28px;letter-spacing:2px}}
.btn{{display:inline-block;margin:10px 8px;padding:16px 30px;border-radius:50px;font:bold 34px FreeSans;background:{p['fg']};color:{'#111' if dark_btn else '#fff'}}}
.top{{position:absolute;top:80px;left:{padl}px;right:96px;text-align:{al};font-size:28px;letter-spacing:4px}}
"""
    art = it.get("art") if kind == "cover" and st in ("parchment", "night") else None
    bg = background(st, W, H, it.get("seed", 1) + i, art, art_dy=60 if st == "parchment" else -30)
    swipe = "स्वाइप करो  →" if kind != "end" else ""
    foot = f'<div class="foot sub"><span>@its_poetogram</span><span>{swipe if kind=="cover" else (f"{i}/{total}" + ("   →" if kind!="end" else ""))}</span></div>'
    if kind == "cover":
        inner = (f'<div class="lab sub">{e(it.get("series","अनकहा सच"))}</div>'
                 f'<div class="big q" id="fit" style="font-size:104px;margin:26px 0">{e(it["title"])}</div>'
                 f'<div class="note sub">{e(it.get("sub",""))}</div>')
        if art: inner = inner.replace('justify-content:center', '')
    elif kind == "point":
        if "a" in pt:
            la, lb = it.get("labels", ["पहले", "अब"])
            inner = (f'<div class="pair"><div class="pl">{e(la)}</div><div class="big q sub" style="font-size:60px;opacity:.75">{e(pt["a"])}</div></div>'
                     f'<div class="pair"><div class="pl">{e(lb)}</div><div class="big q" id="fit" style="font-size:86px">{e(pt["b"])}</div></div>')
        else:
            inner = (f'<div class="num">{i-1:02d}</div><div class="big q" id="fit" style="font-size:90px">{e(pt["text"])}</div>'
                     + (f'<div class="note pnote">{e(pt["note"])}</div>' if pt.get("note") else ""))
    else:
        inner = (f'<div class="big q" id="fit" style="font-size:66px">{e(it["end"])}</div>'
                 f'<div class="note sub" style="margin-top:40px">{e(it["cta"])}</div>'
                 f'<div style="margin-top:44px"><span class="btn">Save</span><span class="btn">Send</span><span class="btn">Follow</span></div>')
    wrap_style = ' style="justify-content:flex-start;top:430px"' if (kind == "cover" and art and st == "night") else ""
    if kind == "cover" and art and st == "parchment": wrap_style = ' style="justify-content:flex-start;top:170px"'
    top = f'<div class="top sub">✦ its_poetogram ✦</div>' if kind != "cover" else ""
    body = (f'<div class="page">{bg}{CHALK_FILTER if st=="chalk" else ""}{top}<div class="wrap"{wrap_style}>{inner}</div>{foot}</div>')
    js = """<script>(()=>{const f=document.getElementById('fit'),w=document.querySelector('.wrap');if(!f)return;
let s=parseFloat(f.style.fontSize);while((w.scrollHeight>w.clientHeight+1||f.scrollWidth>f.clientWidth+2)&&s>34){s-=2;f.style.fontSize=s+'px';}})();</script>"""
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{css}</style></head><body>{body}{js}</body></html>'

def build(it, b):
    out = os.path.join(ROOT, "carousels", it["id"]); os.makedirs(out, exist_ok=True)
    pts = it["points"]; total = len(pts) + 2
    pages = [slide(it, "cover", 1, total)] + [slide(it, "point", k + 2, total, pt) for k, pt in enumerate(pts)] + [slide(it, "end", total, total)]
    for k, h in enumerate(pages, 1):
        pg = b.new_page(viewport={"width": W, "height": H}); pg.set_content(h); pg.wait_for_timeout(120)
        png = f"/tmp/car_{it['id']}_{k}.png"; pg.screenshot(path=png); pg.close()
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", png, "-q:v", "2", os.path.join(out, f"{k:02d}.jpg")], check=True)
    print("ok", it["id"], it["style"], total, "slides", flush=True)

if __name__ == "__main__":
    items = json.load(open(sys.argv[1]))["items"]; want = set(sys.argv[2:])
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        for it in items:
            if it["id"] in want or "all" in want: build(it, b)
        b.close()
