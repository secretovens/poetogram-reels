#!/usr/bin/env python3
"""Original soft, melancholic piano + pad music for its_poetogram reels (royalty-free, generated).
Usage: python3 make_music.py out.wav [seed] [seconds]"""
import sys, numpy as np
from scipy.io import wavfile
from scipy.signal import fftconvolve

out = sys.argv[1]; seed = int(sys.argv[2]) if len(sys.argv) > 2 else 1
DUR = float(sys.argv[3]) if len(sys.argv) > 3 else 8.0
SR = 44100
rng = np.random.default_rng(seed)
t_all = np.arange(int(SR * (DUR + 3))) / SR

def hz(n): return 440 * 2 ** ((n - 69) / 12)

def piano(freq, dur, vel=0.5):
    t = np.arange(int(SR * dur)) / SR
    env = np.exp(-t * 2.2) * (1 - np.exp(-t * 300))
    tone = sum(a * np.sin(2*np.pi*freq*k*t + rng.uniform(0, 6.28)) * np.exp(-t*k*0.6) for k, a in [(1,1),(2,.45),(3,.22),(4,.12),(5,.05)])
    return vel * env * tone

def pad(freqs, dur):
    t = np.arange(int(SR * dur)) / SR
    env = np.minimum(1, t / 0.8) * np.minimum(1, (dur - t) / 0.8)
    s = sum(np.sin(2*np.pi*f*t) + 0.5*np.sin(2*np.pi*f*1.003*t) + 0.3*np.sin(2*np.pi*f*2*t) for f in freqs)
    return 0.05 * env * s / len(freqs)

progs = [
    [(57, [57, 60, 64]), (53, [53, 57, 60]), (48, [48, 52, 55]), (55, [55, 59, 62])],   # Am F C G
    [(57, [57, 60, 64]), (55, [55, 59, 62]), (53, [53, 57, 60]), (52, [52, 56, 59])],   # Am G F E
    [(50, [50, 53, 57]), (57, [57, 60, 64]), (53, [53, 57, 60]), (52, [52, 55, 59])],   # Dm Am F Em
]
prog = progs[seed % len(progs)]
mix = np.zeros_like(t_all)
bar = DUR / len(prog)
for i, (root, chord) in enumerate(prog):
    st = int(i * bar * SR)
    p = pad([hz(n) for n in chord], bar + 0.6); mix[st:st+len(p)] += p
    b = piano(hz(root - 12), bar + 1.5, 0.35); mix[st:st+len(b)] += b
    # gentle arpeggio, 4 notes per bar
    notes = [chord[0] + 12, chord[1] + 12, chord[2] + 12, chord[1] + 12]
    for j, n in enumerate(notes):
        s2 = st + int(j * bar / 4 * SR)
        x = piano(hz(n), 2.5, 0.22 + rng.uniform(-0.04, 0.04)); mix[s2:s2+len(x)] += x
# simple reverb
ir_t = np.arange(int(SR * 2.2)) / SR
ir = rng.normal(0, 1, len(ir_t)) * np.exp(-ir_t * 3)
wet = fftconvolve(mix, ir)[:len(mix)]
mix = mix + 0.12 * wet / np.max(np.abs(wet)) * np.max(np.abs(mix))
mix = mix[:int(SR * DUR)]
fade = int(SR * 1.2)
mix[:int(SR*0.3)] *= np.linspace(0, 1, int(SR*0.3)); mix[-fade:] *= np.linspace(1, 0, fade)
mix = mix / np.max(np.abs(mix)) * 0.6
st = np.stack([mix, np.roll(mix, 220)], 1)
wavfile.write(out, SR, (st * 32767).astype(np.int16))
print("ok", out)
