#!/usr/bin/env python3
"""Cinematic background score for its_poetogram Nazariya reels (original, generated here, royalty-free).
Layers: felt-piano motif + broken chords, warm string pad, cello root, soft pulse that enters after the hook,
shimmer on the last slide, and a whoosh + low boom on every slide change.
Usage: python3 music3.py out.wav SEED SECONDS [t1,t2,t3 transition times] [mood]
mood: dark | hopeful | eastern | tense   (default from seed); 6th arg "soft" = no pulse, gentle transitions (Alfaaz)"""
import sys, numpy as np
from scipy.io import wavfile
from scipy.signal import fftconvolve, butter, lfilter, sosfilt

SR = 44100
def hz(n): return 440 * 2 ** ((n - 69) / 12)
def lp(x, f, o=2): return lfilter(*butter(o, min(f, SR/2-100) / (SR / 2)), x)
def hp(x, f): return lfilter(*butter(2, f / (SR / 2), "high"), x)

def add(mix, x, t, g=1.0):
    s = int(t * SR)
    if s >= len(mix) or s < 0: return
    m = min(len(x), len(mix) - s); mix[s:s+m] += g * x[:m]

def felt_piano(f, dur, vel, rng):
    t = np.arange(int(SR * dur)) / SR
    s = np.zeros_like(t)
    for k, a in [(1,1),(2,.55),(3,.3),(4,.16),(5,.08),(6,.05),(7,.03)]:
        inh = 1 + 0.00035 * k * k
        s += a * np.sin(2*np.pi*f*k*inh*t + rng.uniform(0, 6.28)) * np.exp(-t * (1.1 + .55*k))
    s += 0.003 * rng.normal(0, 1, len(t)) * np.exp(-t * 60)          # hammer
    env = (1 - np.exp(-t * 180)) * np.exp(-t * 0.9)
    return lp(vel * env * s, 3800 + 2000 * vel)

def pad(freqs, dur, vol, bright=2500):
    t = np.arange(int(SR * dur)) / SR
    env = np.minimum(1, t / 1.6) * np.minimum(1, np.maximum(0, dur - t) / 1.4)
    s = np.zeros_like(t)
    for f in freqs:
        for det in (-.004, 0, .004):
            ph = 2*np.pi*f*(1+det)*t + 0.004*np.sin(2*np.pi*5.2*t)*f/100
            s += sum(np.sin(k*ph) / k for k in range(1, 9))
    return vol * env * lp(s / (3*len(freqs)), bright)

def cello(f, dur, vol):
    t = np.arange(int(SR * dur)) / SR
    env = np.minimum(1, t / .9) * np.minimum(1, np.maximum(0, dur - t) / .9)
    ph = 2*np.pi*f*t + 0.02*np.sin(2*np.pi*5*t)
    return vol * env * lp(sum(np.sin(k*ph)/k**1.3 for k in range(1, 7)), 900)

def kick(vol):
    t = np.arange(int(SR * .5)) / SR
    return vol * np.sin(2*np.pi*(42 + 70*np.exp(-t*28))*t) * np.exp(-t*7)

def whoosh(dur, rng, vol):
    n = int(SR * dur); t = np.arange(n) / SR
    noise = rng.normal(0, 1, n); out = np.zeros(n)
    # sweep a band-pass by filtering blocks
    blk = 1024
    for i in range(0, n, blk):
        p = i / n; fc = 300 + 5200 * np.sin(np.pi * p) ** 1.5
        seg = noise[i:i+blk]
        sos = butter(2, [max(80, fc*.6), min(fc*1.6, SR/2-200)], "band", fs=SR, output="sos")
        out[i:i+blk] = sosfilt(sos, seg)
    env = np.sin(np.pi * t / dur) ** 2
    return vol * out * env

def boom(vol):
    t = np.arange(int(SR * 1.8)) / SR
    return vol * (np.sin(2*np.pi*38*t) * np.exp(-t*2.2) + 0.4*np.sin(2*np.pi*76*t)*np.exp(-t*4))

MOODS = {
    "dark":    dict(prog=[[57,60,64],[53,57,60],[48,52,55],[52,55,59]], motif=[4,2,1,0,1,2,4,5]),        # Am F C Em
    "hopeful": dict(prog=[[48,52,55],[55,59,62],[57,60,64],[53,57,60]], motif=[0,2,4,5,4,2,7,4]),        # C G Am F
    "eastern": dict(prog=[[50,53,57],[48,51,55],[46,50,53],[48,51,55]], motif=[0,1,4,5,4,1,0,-1]),       # Dm Cm Bb Cm (phrygian-ish)
    "tense":   dict(prog=[[52,55,59],[48,52,55],[50,53,57],[47,50,54]], motif=[0,1,0,3,2,1,0,-2]),       # Em C Dm Bdim
}

def compose(seed, dur, trans, mood=None, soft=False):
    rng = np.random.default_rng(seed)
    mood = mood or list(MOODS)[seed % len(MOODS)]
    M = MOODS[mood]; prog = M["prog"]
    bpm = 70 + (seed % 3) * 4; beat = 60 / bpm; bar = beat * 4
    mix = np.zeros(int(SR * (dur + 3)))
    first = trans[0] if trans else 3.0; last = trans[-1] if trans else dur * .7
    nb = int(np.ceil(dur / bar)) + 1
    scale = sorted(set(n % 12 for ch in prog for n in ch))
    for b in range(nb):
        ch = prog[b % 4]; t0 = b * bar
        add(mix, pad([hz(n) for n in ch], bar + 1.5, .05 if t0 < first else .075), t0)
        add(mix, cello(hz(ch[0] - 12), bar + .6, .09 if t0 >= first else .05), t0)
        # broken chords (left hand)
        for j, n in enumerate([ch[0]-12, ch[2]-12, ch[1], ch[2]-12]):
            add(mix, felt_piano(hz(n), 3.0, .22, rng), t0 + j * beat)
        # motif (right hand), sparse during hook, full later
        mot = M["motif"]
        for j in range(4 if t0 < first else 8):
            deg = mot[(j + b * 2) % len(mot)]
            base = ch[0] + 12
            n = base + [0, 2, 3, 5, 7, 8, 10, 12, 14][deg % 8] - (12 if deg < 0 else 0) if mood != "hopeful" else base + [0,2,4,5,7,9,11,12][deg % 8]
            if (j % 2 == 1) and rng.random() < .3: continue
            add(mix, felt_piano(hz(n), 2.4, .26 + rng.uniform(-.04, .04), rng), t0 + j * beat / 2 + (beat if t0 < first else 0))
        # pulse after hook
        if t0 >= first - 0.01 and not soft:
            add(mix, kick(.32), t0); add(mix, kick(.22), t0 + 2 * beat)
        # shimmer on last slide
        if t0 >= last - bar * .5:
            for j in range(8):
                add(mix, felt_piano(hz(ch[j % 3] + 24), 1.6, .09, rng), t0 + j * beat / 2)
    # transitions
    for t in trans:
        add(mix, whoosh(.7, rng, .05 if soft else .10), t - .45); add(mix, boom(.14 if soft else .3), t - .05)
    # reverb
    ir_t = np.arange(int(SR * 2.8)) / SR
    ir = rng.normal(0, 1, len(ir_t)) * np.exp(-ir_t * 2.3)
    wet = fftconvolve(mix, ir)[:len(mix)]
    mix = mix + .22 * wet / (np.max(np.abs(wet)) + 1e-9) * np.max(np.abs(mix))
    mix = hp(mix, 30)[:int(SR * dur)]
    fi, fo = int(SR * .15), int(SR * 1.6)
    mix[:fi] *= np.linspace(0, 1, fi); mix[-fo:] *= np.linspace(1, 0, fo)
    mix = mix / (np.max(np.abs(mix)) + 1e-9) * .9
    L = mix; R = np.roll(mix, 300) * .96 + .04 * mix
    return np.stack([L, R], 1), mood

if __name__ == "__main__":
    out, seed, dur = sys.argv[1], int(sys.argv[2]), float(sys.argv[3])
    trans = [float(x) for x in sys.argv[4].split(",")] if len(sys.argv) > 4 and sys.argv[4] else []
    mood = sys.argv[5] if len(sys.argv) > 5 and sys.argv[5] else None
    soft = len(sys.argv) > 6 and sys.argv[6] == 'soft'
    st, mood = compose(seed, dur, trans, mood, soft)
    wavfile.write(out, SR, (np.clip(st, -1, 1) * 32767).astype(np.int16)); print("ok", out, mood)
