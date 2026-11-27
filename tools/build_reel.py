#!/usr/bin/env python3
"""Build a line-by-line reveal reel for its_poetogram.
Usage: python3 build_reel.py content.json ID [ID ...]   (or 'all')
content.json: {"items":[{"id":"sach07","lines":[...],"accent":"...","art":"tie","tag":"अनकहा सच · 07","seed":7}]}
Outputs (repo root): reels/ID.mp4 (1080x1920), covers/ID.jpg, cards/ID.png"""
import json, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
TMP = "/tmp/reelbuild"; os.makedirs(TMP, exist_ok=True)
for d in ("reels", "covers", "cards"): os.makedirs(os.path.join(ROOT, d), exist_ok=True)
BG = "split[a][b];[a]scale=1536:1920,crop=1080:1920,boxblur=28:2,eq=brightness=-0.04[bg];[bg][b]overlay=0:285"

def run(cmd): subprocess.run(cmd, check=True, capture_output=True)

def build(it):
    n = len(it["lines"]); base = ["python3", os.path.join(HERE, "make_card.py")]
    opts = ["--accent", it.get("accent", ""), "--art", it["art"], "--tag", it.get("tag", "")]
    stages = []
    for k in range(1, n + 1):
        out = f"{TMP}/{it['id']}_{k}.png"
        run(base + [out] + it["lines"] + opts + ["--reveal", str(k), "--artop", "1" if k == n else "0"])
        stages.append(out)
    card = os.path.join(ROOT, "cards", it["id"] + ".png")
    os.replace(stages[-1], card); stages[-1] = card
    durs = [2.3] * (n - 1) + [5.5]; xf = 0.45
    total = sum(durs) - xf * (n - 1)
    music = f"{TMP}/{it['id']}.wav"
    run(["python3", os.path.join(HERE, "make_music.py"), music, str(it.get("seed", 1)), f"{total:.2f}"])
    cmd = ["ffmpeg", "-y", "-loglevel", "error"]
    for st, d in zip(stages, durs): cmd += ["-loop", "1", "-t", f"{d}", "-framerate", "30", "-i", st]
    cmd += ["-i", music]
    fc, last, off = [], "[0:v]", 0.0
    for i in range(1, n):
        off += durs[i - 1] - xf
        lab = f"[x{i}]"
        fc.append(f"{last}[{i}:v]xfade=transition=fade:duration={xf}:offset={off:.2f}{lab}"); last = lab
    fc.append(f"{last}{BG},format=yuv420p[v]")
    cmd += ["-filter_complex", ";".join(fc), "-map", "[v]", "-map", f"{n}:a", "-t", f"{total:.2f}",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-r", "30", "-c:a", "aac", "-b:a", "160k",
            "-movflags", "+faststart", os.path.join(ROOT, "reels", it["id"] + ".mp4")]
    run(cmd)
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", card, "-filter_complex", BG, "-q:v", "3", os.path.join(ROOT, "covers", it["id"] + ".jpg")])
    print("ok", it["id"], f"{total:.1f}s")

data = json.load(open(sys.argv[1]))["items"]
want = sys.argv[2:]
for it in data:
    if "all" in want or it["id"] in want: build(it)
