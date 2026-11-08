# Pitch salience: for each frame and candidate fundamental (MIDI lo..hi in 1/3 semitones), the
# weighted sum of spectral magnitude at its first 8 harmonics, less half the energy halfway between
# them (so a note's octave-below doesn't light up). Saved as .npy and drawn like pmap.py.
#   sal.py in.wav out.png t0 t1 [lo hi] [px_per_s]
import sys, numpy as np, subprocess, wave
f, out, t0, t1 = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4])
lo, hi = (int(sys.argv[5]), int(sys.argv[6])) if len(sys.argv) > 6 else (45, 84)
pps = float(sys.argv[7]) if len(sys.argv) > 7 else 30
w = wave.open(f); sr = w.getframerate(); x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32)
x = x[int(t0 * sr):int(t1 * sr)]
N, hop = 4096, int(sr / pps); win = np.hanning(N)
cands = np.arange(lo, hi + 1e-9, 1 / 3); f0 = 440 * 2 ** ((cands - 69) / 12)
binhz = sr / N
S = []
for i in range(0, len(x) - N, hop):
    mag = np.abs(np.fft.rfft(x[i:i + N] * win)); mag = np.log1p(mag / 50)
    s = np.zeros(len(cands))
    for h in range(1, 9):
        b = f0 * h / binhz; b2 = f0 * (h - 0.5) / binhz
        ok = b < len(mag) - 1
        s[ok] += 0.85 ** (h - 1) * (np.interp(b[ok], np.arange(len(mag)), mag) - 0.5 * np.interp(b2[ok], np.arange(len(mag)), mag))
    S.append(s)
S = np.array(S).T  # cands x frames
np.save(out.replace('.png', '.npy'), S)
img = np.clip(S / np.percentile(S, 99.5), 0, 1)
pst = 3; rows = len(cands)
big = np.repeat(img[::-1], pst, axis=0)
rgb = np.stack([big ** 1.5, big, big ** 0.6], -1) * 255
for k, m in enumerate(cands):
    if abs(m - round(m)) < 1e-6 and int(round(m)) % 12 in (0, 7):
        y = (rows - 1 - k) * pst + 1; rgb[y, :, :] = np.maximum(rgb[y, :, :], [110, 40, 40] if int(round(m)) % 12 == 0 else [40, 40, 90])
for j in range(rgb.shape[1]):
    t = t0 + j / pps
    if abs(t * pps - round(t) * pps) < 0.5: rgb[-8 if round(t) % 5 else -16:, j, :] = 255 if round(t) % 5 == 0 else 120
h, wd = rgb.shape[:2]
subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{wd}x{h}', '-i', '-', out], input=rgb.astype(np.uint8).tobytes())
print(out, wd, 'x', h, f'{t0}-{t1}s MIDI {lo}-{hi} (C red, G blue; tick 1 s, long tick 5 s)')
