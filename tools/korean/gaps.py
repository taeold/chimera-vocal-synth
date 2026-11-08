# Share of sung time that drops out: 10 ms frames inside the singing (first to last loud frame)
# that fall 25 dB or more below the voice's median level, and how long the dropouts are.
import wave, array, math, sys
for f in sys.argv[1:]:
    w = wave.open(f); sr = w.getframerate(); x = array.array('h', w.readframes(w.getnframes()))
    H = sr // 100
    db = [10 * math.log10(sum(v * v for v in x[i:i + H]) / H + 1) for i in range(0, len(x) - H, H)]
    loud = [i for i, d in enumerate(db) if d > max(db) - 30]
    seg = db[loud[0]:loud[-1]]
    med = sorted(seg)[len(seg) // 2]
    out = []
    for depth in (25, 12):
        low = [d < med - depth for d in seg]
        runs, r = [], 0
        for b in low + [False]:
            if b: r += 1
            elif r: runs.append(r); r = 0
        short = [r for r in runs if r <= 15]  # up to 150 ms: inside phrases, not breaths
        out.append(f"-{depth} dB: {sum(short) / len(seg):5.1%} of sung time in {len(short):3d} dips")
    print(f"{f}:  " + "   ".join(out))
