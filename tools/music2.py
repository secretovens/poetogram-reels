#!/usr/bin/env python3
"""Original background music for its_poetogram (synthesised here, royalty-free, owned by the account).
Usage: python3 music2.py out.wav MOOD SEED SECONDS
MOODS: piano, sitar, strings, guitar, musicbox, santoor"""
import sys, numpy as np
from scipy.io import wavfile
from scipy.signal import fftconvolve, butter, lfilter

SR = 44100
def hz(n): return 440 * 2 ** ((n - 69) / 12)

def lowpass(x, f):
    b, a = butter(2, f / (SR / 2)); return lfilter(b, a, x)

def env_ad(n, att, dec):
    t = np.arange(n) / SR
    return np.minimum(1, t / max(att, 1e-4)) * np.exp(-t * dec)

def piano(f, dur, vel, rng):
    t = np.arange(int(SR * dur)) / SR
    e = np.exp(-t * 2.0) * (1 - np.exp(-t * 300))
    s = sum(a * np.sin(2*np.pi*f*k*t*(1+0.0004*k*k) + rng.uniform(0, 6.28)) * np.exp(-t*k*0.5)
            for k, a in [(1,1),(2,.5),(3,.25),(4,.12),(5,.06),(6,.03)])
    return vel * e * s

def pluck(f, dur, vel, rng, bright=0.5, decay=0.996):
    """Karplus-Strong plucked string (guitar / sitar-ish)."""
    n = int(SR * dur); N = max(2, int(SR / f))
    buf = rng.uniform(-1, 1, N); buf = lowpass(buf, 2000 + 8000 * bright) if N > 12 else buf
    out = np.zeros(n); idx = 0
    for i in range(n):
        out[i] = buf[idx]
        nxt = (idx + 1) % N
        buf[idx] = decay * 0.5 * (buf[idx] + buf[nxt])
        idx = nxt
    return vel * out

def sitar(f, dur, vel, rng):
    x = pluck(f, dur, vel, rng, 0.9, 0.9975)
    t = np.arange(len(x)) / SR
    buzz = np.tanh(3 * x) * 0.5 + x * 0.5            # jawari-like buzz
    sym = 0.15 * np.sin(2*np.pi*f*2*t) * np.exp(-t*1.5) * vel  # sympathetic shimmer
    return buzz + sym

def bell(f, dur, vel, rng):
    t = np.arange(int(SR * dur)) / SR
    s = sum(a * np.sin(2*np.pi*f*r*t) * np.exp(-t*d) for r, a, d in [(1,1,2.2),(2.76,.4,4),(5.4,.18,7),(8.9,.06,10)])
    return vel * s * (1 - np.exp(-t * 800))

def pad(freqs, dur, vol=0.05, bright=1.0):
    t = np.arange(int(SR * dur)) / SR
    e = np.minimum(1, t / 1.2) * np.minimum(1, np.maximum(0, (dur - t)) / 1.2)
    s = sum(np.sin(2*np.pi*f*t) + 0.6*np.sin(2*np.pi*f*1.004*t + 1) + 0.6*np.sin(2*np.pi*f*0.996*t + 2)
            + 0.25*bright*np.sin(2*np.pi*f*2*t) for f in freqs)
    return vol * e * s / len(freqs)

def drone(root, dur):
    """Tanpura-like Pa-Sa-Sa-Sa cycle."""
    out = np.zeros(int(SR * dur)); cyc = 2.4; rng = np.random.default_rng(1)
    k = 0; t0 = 0.0
    while t0 < dur:
        n = [root + 7, root + 12, root + 12, root][k % 4]
        x = pluck(hz(n), 3.0, 0.11, rng, 0.6, 0.9992)
        s = int(t0 * SR); out[s:s+len(x)] += x[:len(out)-s]
        t0 += cyc / 4; k += 1
    return out

def add(mix, x, t):
    s = int(t * SR)
    if s >= len(mix): return
    m = min(len(x), len(mix) - s); mix[s:s+m] += x[:m]

PROGS = {
    "minor": [[57,60,64],[53,57,60],[48,52,55],[55,59,62]],      # Am F C G
    "minor2": [[50,53,57],[57,60,64],[53,57,60],[52,55,59]],     # Dm Am F Em
    "major": [[48,52,55],[55,59,62],[57,60,64],[53,57,60]],      # C G Am F
    "warm": [[53,57,60],[48,52,55],[50,53,57],[55,59,62]],       # F C Dm G
}
# Bhairav-ish / Yaman-ish melodic sets (MIDI offsets from root)
RAGA = {"bhairavi": [0,1,3,5,7,8,10,12], "yaman": [0,2,4,6,7,9,11,12], "kafi": [0,2,3,5,7,9,10,12]}

def melody(rng, scale, n, root):
    cur = 4; notes = []
    for _ in range(n):
        cur = int(np.clip(cur + rng.choice([-2,-1,-1,0,1,1,2]), 0, len(scale)-1))
        notes.append(root + scale[cur])
    notes[-1] = root + scale[0] + (12 if notes[-2] > root + 6 else 0)
    return notes

def compose(mood, seed, dur):
    rng = np.random.default_rng(seed)
    mix = np.zeros(int(SR * (dur + 3)))
    if mood == "piano":
        prog = PROGS[["minor","minor2","warm"][seed % 3]]; bar = dur / 4
        for i, ch in enumerate(prog):
            add(mix, pad([hz(n) for n in ch], bar + 1, 0.04), i*bar)
            add(mix, piano(hz(ch[0]-12), bar+1.5, .32, rng), i*bar)
            for j, n in enumerate([ch[0]+12, ch[2]+12, ch[1]+12, ch[2]+12]):
                add(mix, piano(hz(n), 2.6, .2 + rng.uniform(-.04,.04), rng), i*bar + j*bar/4)
            if i in (1, 3): add(mix, piano(hz(ch[2]+24), 2.5, .12, rng), i*bar + bar*0.62)
    elif mood == "sitar":
        root = 50; add(mix, drone(root - 12, dur + 2), 0)
        sc = RAGA[["bhairavi","yaman","kafi"][seed % 3]]
        notes = melody(rng, sc, 9, root + 12); t = 0.6
        for k, n in enumerate(notes):
            add(mix, sitar(hz(n), 2.2, .32, rng), t)
            if rng.random() < .35: add(mix, sitar(hz(n), 1.2, .14, rng), t + .22)  # grace re-strike
            t += rng.choice([0.6, 0.9, 1.2]) * dur / 11
    elif mood == "strings":
        prog = PROGS[["minor","minor2"][seed % 2]]; bar = dur / 4
        for i, ch in enumerate(prog):
            add(mix, pad([hz(n) for n in ch] + [hz(ch[0]-12)], bar + 1.6, 0.07 + 0.015*i, 1.4), i*bar)
            add(mix, piano(hz(ch[0]-24), bar+2, .25, rng), i*bar)
            add(mix, piano(hz(ch[2]+12), 3, .14, rng), i*bar + bar*0.5)
    elif mood == "guitar":
        prog = PROGS[["major","warm"][seed % 2]]; bar = dur / 4
        for i, ch in enumerate(prog):
            pat = [ch[0]-12, ch[1], ch[2], ch[1]+12, ch[2], ch[1]]
            for j, n in enumerate(pat):
                add(mix, pluck(hz(n), 2.4, .3 + rng.uniform(-.05,.05), rng, 0.4, 0.997), i*bar + j*bar/6)
            add(mix, pad([hz(n) for n in ch], bar+1, 0.025), i*bar)
        # soft lo-fi pulse + vinyl
        beat = dur / 16
        for k in range(16):
            t = np.arange(int(SR*.25))/SR
            kick = .25*np.sin(2*np.pi*(55+60*np.exp(-t*30))*t)*np.exp(-t*12)
            if k % 4 == 0: add(mix, kick, k*beat)
        mix[:] += 0.004 * lowpass(rng.normal(0, 1, len(mix)), 3000) * (rng.random(len(mix)) < 0.002) * 40
    elif mood == "musicbox":
        prog = PROGS[["major","warm","minor"][seed % 3]]; bar = dur / 4
        for i, ch in enumerate(prog):
            add(mix, pad([hz(n) for n in ch], bar+1, 0.035), i*bar)
            for j, n in enumerate([ch[0]+24, ch[2]+12, ch[1]+24, ch[2]+24]):
                add(mix, bell(hz(n), 2.5, .18, rng), i*bar + j*bar/4)
    elif mood == "santoor":
        root = 52; add(mix, drone(root - 12, dur + 2), 0)
        sc = RAGA[["yaman","kafi","bhairavi"][seed % 3]]
        notes = melody(rng, sc, 12, root + 12); step = dur / 13
        for k, n in enumerate(notes):
            for r in range(3 if k % 3 == 2 else 1):      # tremolo on every third note
                add(mix, pluck(hz(n), 1.6, .22, rng, 1.0, 0.995), 0.5 + k*step + r*0.09)
    else:
        raise SystemExit("unknown mood " + mood)
    # room reverb
    ir_t = np.arange(int(SR * 2.4)) / SR
    ir = rng.normal(0, 1, len(ir_t)) * np.exp(-ir_t * 2.6)
    wet = fftconvolve(mix, ir)[:len(mix)]
    mix = mix + 0.16 * wet / (np.max(np.abs(wet)) + 1e-9) * np.max(np.abs(mix))
    mix = lowpass(mix, 9000)[:int(SR * dur)]
    fi, fo = int(SR * .25), int(SR * 1.4)
    mix[:fi] *= np.linspace(0, 1, fi); mix[-fo:] *= np.linspace(1, 0, fo)
    mix = mix / (np.sqrt(np.mean(mix ** 2)) + 1e-9) * 0.075   # same loudness for every mood
    mix = 0.7 * np.tanh(mix / 0.7)                              # soft limiter
    return np.stack([mix, np.roll(mix, 260)], 1)

if __name__ == "__main__":
    out, mood, seed, dur = sys.argv[1], sys.argv[2], int(sys.argv[3]), float(sys.argv[4])
    st = compose(mood, seed, dur)
    wavfile.write(out, SR, (st * 32767).astype(np.int16)); print("ok", out, mood)
