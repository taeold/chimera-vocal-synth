# Basic Pitch notes on the beat grid, sorted against the aligned MIDI tune: on it (red), above it
# (cyan), below it (green); drawn over the salience map. Prints the notes above the lead.
import sys, json, numpy as np, subprocess
sys.path.insert(0, '/tmp'); from midiparse import parse
_, div, notes, *_ = parse('/tmp/jtp/full.mid')
S = np.load('/tmp/orig/sall.npy'); lo, pps = 40, 30
BPM, OFF, B0REF = 72.75, 9.47, 200
T = lambda b: OFF + (b - B0REF) * 60 / BPM; Bt = lambda t: B0REF + (t - OFF) * BPM / 60
b0, b1, out = float(sys.argv[1]), float(sys.argv[2]), sys.argv[3]
tune = sorted((n['t0'] / div, n['t1'] / div, n['pitch'] - 12) for n in notes if n['ch'] == 0)
def lead_at(b):
    c = [p for s, e, p in tune if s - 0.15 <= b < e + 0.15]
    return c
bp = [(Bt(s), Bt(e), p, a) for s, e, p, a in json.load(open('/tmp/orig/bp_notes.json')) if b0 <= Bt(s) < b1]
cls = []
for s, e, p, a in bp:
    l = lead_at(s + 0.05)
    if l and min(abs(p - x) for x in l) <= 1: c = 'lead'
    elif l and p > max(l): c = 'above'
    elif l: c = 'below'
    else: c = 'free'  # no lead note now
    cls.append((s, e, p, a, c))
img = np.clip(S[(48 - lo) * 3:(84 - lo) * 3 + 1, int(T(b0) * pps):int(T(b1) * pps)] / np.percentile(S, 99.5), 0, 1)
XS, YS = 4, 4; big = np.kron(img[::-1], np.ones((YS, XS))); rgb = np.stack([big] * 3, -1) * 150; H = big.shape[0]
yof = lambda m: int(H - ((m - 48) * 3 + 0.5) * YS); j0 = int(T(b0) * pps)
for m in range(48, 85):
    if m % 12 in (0, 7): rgb[yof(m), :, :] += [80, 20, 20] if m % 12 == 0 else [20, 20, 80]
for bb in np.arange(np.ceil(b0), b1):
    x = int((T(bb) * pps - j0) * XS)
    if 0 <= x < rgb.shape[1]: rgb[:, x, :] += 80 if bb % 4 == 0 else 25
col = {'lead': [255, 80, 80], 'above': [60, 230, 255], 'below': [90, 255, 90], 'free': [255, 220, 60]}
for s, e, p, a, c in cls:
    x0, x1 = int((T(s) * pps - j0) * XS), int((T(e) * pps - j0) * XS); y = yof(p)
    if 0 <= y < H: rgb[max(0, y - 2):y + 3, max(0, x0):max(0, min(rgb.shape[1], x1)), :] = col[c]
rgb = np.clip(rgb, 0, 255); h, wd = rgb.shape[:2]
subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{wd}x{h}', '-i', '-', out], input=rgb.astype(np.uint8).tobytes())
nm = lambda m: ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B'][m % 12] + str(m // 12 - 1)
from collections import Counter
print(out, Counter(c for *_, c in cls))
for s, e, p, a, c in cls:
    if c in ('above', 'free') and p >= 64:
        print(f"  {c:5s} bar {int(s//4)} beat {s%4+1:4.2f}  {e-s:4.2f} beats  {nm(p)}  amp {a:.2f}  lead {','.join(nm(x) for x in lead_at(s+0.05)) or '-'}")
