# Level dip at each note change, grouped by how the next syllable starts. dB below the voice's median.
import wave, array, math, json, sys, collections
sys.path.insert(0, '/tmp/chimera-vocal-synth')
wavf, jsonf = sys.argv[1], sys.argv[2]
w = wave.open(wavf); sr = w.getframerate(); x = array.array('h', w.readframes(w.getnframes())); H = sr // 200
db = [10 * math.log10(sum(v * v for v in x[i:i + H]) / H + 1) for i in range(0, len(x) - H, H)]
m = json.load(open(jsonf)); beat = 60 / m['bpm']; t = m['t0']
starts = []
for midi, b in m['notes']:
    if midi > 0: starts.append(t)
    t += b * beat
seg = [d for d in db if d > max(db) - 30]; med = sorted(seg)[len(seg) // 2]
# the syllables: Hangul blocks and English/~ tokens in order
syl = []
for tok in m['lyrics'].replace(',', ' ').split():
    syl += [tok] if (tok == '~' or tok.isascii()) else list(tok)
ONSET = {}
def kind(s):
    if s == '~': return 'melisma'
    if not ('가' <= s <= '힣'): return 'latin'
    cho = (ord(s) - 0xAC00) // 588
    return ['stop','tense','nasal','stop','tense','liquid','nasal','stop','tense','fric','fric','vowel','affric','tense','affric','stop','stop','stop','h'][cho]
res = collections.defaultdict(list)
for i in range(1, len(starts)):
    a, b = int((starts[i] - 0.12) * 200), int((starts[i] + 0.04) * 200)
    dip = med - min(db[a:b])
    res[kind(syl[i])].append(dip)
for k, v in sorted(res.items(), key=lambda kv: -sum(kv[1]) / len(kv[1])):
    print(f"{k:8s} {len(v):2d} boundaries, median dip {sorted(v)[len(v)//2]:5.1f} dB, max {max(v):5.1f}")
