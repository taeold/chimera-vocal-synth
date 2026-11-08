# Pitch map: semitone-resolution spectrogram (MIDI lo..hi) of a mono wav, written as a PNG via
# ffmpeg. Brightness is log magnitude; a line every C (bright) and G (dim); a tick every 5 s
# (bright every 30 s) along the bottom.
#   pmap.py in.wav out.png [t0 t1] [lo hi] [px_per_s] [px_per_semitone]
import sys, numpy as np, subprocess, wave
f, out = sys.argv[1], sys.argv[2]
t0, t1 = (float(sys.argv[3]), float(sys.argv[4])) if len(sys.argv) > 4 else (0, None)
lo, hi = (int(sys.argv[5]), int(sys.argv[6])) if len(sys.argv) > 6 else (45, 84)
pps = float(sys.argv[7]) if len(sys.argv) > 7 else 20; pst = int(sys.argv[8]) if len(sys.argv) > 8 else 6
w = wave.open(f); sr = w.getframerate(); x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32)
x = x[int(t0 * sr): int(t1 * sr) if t1 else None]
N, hop = 8192, int(sr / pps)
win = np.hanning(N)
frames = range(0, len(x) - N, hop)
freqs = np.fft.rfftfreq(N, 1 / sr)
midi = 69 + 12 * np.log2(np.maximum(freqs, 1) / 440)
rows = hi - lo + 1
img = np.zeros((rows * pst, len(frames)))
for j, i in enumerate(frames):
    mag = np.abs(np.fft.rfft(x[i:i + N] * win))
    for k in range(rows):
        m = lo + k
        sel = (midi >= m - 0.5) & (midi < m + 0.5)
        v = mag[sel].max() if sel.any() else 0
        img[(rows - 1 - k) * pst:(rows - k) * pst, j] = v
img = 20 * np.log10(img + 1e-3); img -= img.max(); img = np.clip((img + 50) / 50, 0, 1)
rgb = np.stack([img ** 1.5, img, img ** 0.7], -1) * 255
for k in range(rows):
    m = lo + k
    if m % 12 in (0, 7):
        y = (rows - 1 - k) * pst + pst // 2
        rgb[y, :, :] = np.maximum(rgb[y, :, :], [90, 40, 40] if m % 12 == 0 else [40, 40, 70])
for j in range(len(frames)):
    t = t0 + j / pps
    if abs(t * pps - round(t / 5) * 5 * pps) < 0.5:
        rgb[-12:, j, :] = 255 if round(t) % 30 == 0 else 140
h, wd = rgb.shape[:2]
p = subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{wd}x{h}', '-i', '-', out], input=rgb.astype(np.uint8).tobytes())
print(out, wd, 'x', h, f'({t0}-{t0 + len(frames) / pps:.1f} s, MIDI {lo}-{hi}; C lines red, G lines blue)')
