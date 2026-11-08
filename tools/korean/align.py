# Fit the MIDI tune (channel 1, beats B0..B1) to the vocal salience: time = off + beat*60/bpm,
# pitch = written + shift. Score: mean salience along the notes. Coarse grid, then fine.
import sys, numpy as np
sys.path.insert(0, '/tmp'); from midiparse import parse
_, div, notes, *_ = parse('/tmp/jtp/full.mid')
S = np.load('/tmp/orig/sall.npy'); lo, pps = 40, 30
B0, B1 = float(sys.argv[1]), float(sys.argv[2])
tune = [(n['t0'] / div, n['t1'] / div, n['pitch']) for n in notes if n['ch'] == 0 and B0 <= n['t0'] / div < B1]
Sz = (S - S.mean(1, keepdims=True)) / (S.std() + 1e-9)
def score(bpm, off, shift):
    tot = cnt = 0
    for b0, b1, p in tune:
        k = int(round((p + shift - lo) * 3))
        if not (0 <= k < S.shape[0]): continue
        j0, j1 = int((off + (b0 - B0) * 60 / bpm) * pps), int((off + (b1 - B0) * 60 / bpm) * pps)
        if j1 > S.shape[1] or j0 < 0: return -9
        tot += Sz[max(0, k - 1):k + 2, j0:max(j0 + 1, j1)].max(0).sum(); cnt += max(1, j1 - j0)
    return tot / cnt
best = []
for shift in (-24, -12, 0):
    for bpm in np.arange(68, 78.01, 0.25):
        for off in np.arange(0, 71 - (B1 - B0) * 60 / bpm, 0.1):
            best.append((score(bpm, off, shift), bpm, off, shift))
best.sort(reverse=True)
print('coarse best:', [(round(s, 3), round(b, 2), round(o, 2), sh) for s, b, o, sh in best[:5]])
s, bpm, off, shift = best[0]
fine = max((score(b, o, shift), b, o) for b in np.arange(bpm - 0.3, bpm + 0.31, 0.05) for o in np.arange(off - 0.15, off + 0.151, 0.02))
print('fine:', [round(v, 3) for v in fine], 'shift', shift)
