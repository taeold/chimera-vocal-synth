# For each sung note: autocorrelation pitch over the middle of the note's vowel, compared with
# the note's MIDI. Pure Python on a 12 kHz decimation, so it's slow but small.
import wave, array, json, math, sys
name = sys.argv[1]
w = wave.open(f"{name}.wav"); sr = w.getframerate(); x = array.array('h', w.readframes(w.getnframes()))
D = 4; y = [sum(x[i:i+D]) / D for i in range(0, len(x) - D, D)]; fs = sr / D
m = json.load(open(f"{name}.json")); beat = 60 / m["bpm"]; t = m.get("t0", 0.3)
bad = 0; rows = []
for midi, beats in m["notes"]:
    dur = beats * beat
    if midi > 0:
        a = int((t + dur * 0.35) * fs); n = int(min(dur * 0.3, 0.08) * fs)
        seg = y[a:a + n]
        f_ref = 440 * 2 ** ((midi - 69) / 12)
        best, lag_best = -1, None
        for lag in range(int(fs / (f_ref * 1.5)), int(fs / (f_ref / 1.5)) + 1):
            s = sum(seg[i] * seg[i + lag] for i in range(len(seg) - lag))
            e = math.sqrt(sum(v * v for v in seg[:len(seg) - lag]) * sum(v * v for v in seg[lag:])) or 1
            if s / e > best: best, lag_best = s / e, lag
        f = fs / lag_best; cents = 1200 * math.log2(f / f_ref)
        off = abs(cents) > 50
        bad += off; rows.append(f"{midi}:{cents:+.0f}{'!' if off else ''}")
    t += dur
print(name, f"{len(rows)} notes, {bad} off by >50 cents:", " ".join(rows))
