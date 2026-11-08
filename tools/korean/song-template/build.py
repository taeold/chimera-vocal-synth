# A song part's three vocal parts from a MIDI, at the octaves the record sings them. This is the
# build for the last chorus of 자전거 탄 풍경 "너에게 난, 나에게 넌" (midiex 113132), with the lyrics
# taken out: fill in MAIN and ECHO for the part, and change the channels, beats, BPM and SHIFT.
# In that song the tune was written an octave above the singer; the other two parts as sung.
#   lead     channel 1, the tune, with the main words (its long 되 split as the harmony splits it)
#   harmony  channel 9 as written (a third above the sung tune), with the tune's syllable at each onset
#   echo     channel 7 as written, the high voice: the echoes, "우" where it hums, the last line on top
# Notes in a phrase run into each other (legato); only rests longer than half a beat breathe.
# Tempo 72.75, the record's (fitted), so the voices sit on the record's own instrumental.
import sys, json, re
sys.path.insert(0, '/tmp'); from midiparse import parse
_, div, notes, *_ = parse(sys.argv[1])
A, B, SING, T0, LEGATO, BPM = 228, 276, 232.9, 0.3, 0.5, 72.75
SHIFT = {'lead': -12, 'harmony': 0, 'echo': 0}
def ch(c): return sorted([n['t0'] / div, n['t1'] / div, n['pitch']] for n in notes if n['ch'] == c and SING <= n['t0'] / div < B)

MAIN = "..."  # the part's words, one syllable per tune note; a comma is a breath
ECHO = [  # (beats in channel 7, words: None hums "우")
    ((235.0, 236.0), "..."),
    ((236.0, 247.0), None),
    ((251.2, 252.8), "..."),
    ((253.0, 255.4), None),
    ((255.5, 259.0), "..."),
    ((260.0, 268.0), "..."),
]

def syllables(text):  # [(syllable, word id)]
    out = []
    for w, word in enumerate(text.split()):
        core = re.sub(r'[,.]', '', word)
        out += [(s, w) for s in (['~'] if core == '~' else list(core))]
    return out

def legato(ns):
    ns = sorted(ns)
    for x, y in zip(ns, ns[1:]):
        if y[0] - x[1] <= LEGATO: x[1] = y[0]
        x[1] = min(x[1], y[0])
    return ns

lead = ch(0)
k = next(i for i, n in enumerate(lead) if abs(n[0] - 245.76) < 0.05)  # 되 → 되 + 고
s, e, p = lead[k]; lead[k:k + 1] = [[s, 246.01, p], [246.01, e, p]]
main = syllables(MAIN)
assert len(main) == len(lead), (len(main), len(lead))
lead = [n + [main[i][0], ('lead', main[i][1])] for i, n in enumerate(legato(lead))]
at = {round(n[0], 1): (n[3], n[4]) for n in lead}

harmony = []
for n in legato(ch(8)):
    syl, key = at.get(round(n[0], 1), ('~', None))
    harmony.append(n + [syl, key])

echo, used = [], 0
for (a, b), words in ECHO:
    ns = [n for n in ch(6) if a <= n[0] < b]; used += len(ns)
    merged = []  # a grace note joins the note after it, which starts in its place
    for n in ns:
        if merged and merged[-1][1] - merged[-1][0] <= 0.1: n = [merged.pop()[0]] + n[1:]
        merged.append(n)
    if words:
        syl = syllables(words)
        assert len(syl) == len(merged), (words, len(syl), len(merged))
        echo += [n + [t, ('echo', words, w)] for n, (t, w) in zip(merged, syl)]
    else:
        echo += [n + ['우', ('hum', a, i)] for i, n in enumerate(merged)]
assert used == len(ch(6)), (used, len(ch(6)))
echo = legato(echo)
for x, y in zip(echo, echo[1:]):  # a hum running straight on from a hum is one held 우
    if y[3] == '우' and x[3] in ('우', '~') and y[4][0] == 'hum' and abs(x[1] - y[0]) < 1e-6: y[3] = '~'

def melody(events, vibrato, shift):
    out, t, toks, prev = [], A, [], None
    for s, e, p, syl, key in events:
        if s > t + 1e-6: out.append([0, round(s - t, 4)])
        out.append([p + shift, round(e - s, 4)]); t = e
        if syl == '~': toks.append(' ~'); prev = None
        else: toks.append(('' if key == prev and key is not None else ' ') + syl); prev = key
    out.append([0, round(B - t, 4)])
    return {'bpm': BPM, 't0': T0, 'vibrato': vibrato, 'lyrics': ''.join(toks).strip(), 'notes': out}

for name, ev, vib in (('lead', lead, 30), ('harmony', harmony, 22), ('echo', echo, 26)):
    m = melody(ev, vib, SHIFT[name])
    json.dump(m, open(f'{name}.json', 'w'), ensure_ascii=False)
    print(f"{name}: {len(ev)} notes  {m['lyrics']}")
