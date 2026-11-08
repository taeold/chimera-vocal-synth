# One second singer from harmony.json and echo.json: the high part where it sings, the harmony
# in its gaps (a harmony note is cut where a high note starts, one starting under a high note is
# left out, and so is the rest of a word that loses a note). Words keep their grouping.
import json
A = 228
def events(path, src):
    m = json.load(open(path)); toks = m['lyrics'].replace(',', ' ').split()
    syl = []  # (syllable, word id)
    for w, t in enumerate(toks):
        syl += [(t, (src, w))] if t == '~' else [(c, (src, w)) for c in t]
    out, t, k = [], A, 0
    for p, d in m['notes']:
        if p > 0: out.append([t, t + d, p, *syl[k]]); k += 1
        t += d
    assert k == len(syl), (path, k, len(syl))
    return m, out
hm, harm = events('harmony.json', 'h'); em, high = events('echo.json', 'e')
inside = lambda t: any(s - 1e-6 <= t < e - 1e-6 for s, e, *_ in high)
keep = []
for n in harm:
    if inside(n[0]): continue
    nxt = min((s for s, *_ in high if s > n[0]), default=None)
    if nxt is not None and n[1] > nxt: n[1] = nxt
    keep.append(n)
# a harmony word survives whole or not at all: no fragments like a lone 이 from 없이
size = {}
for n in harm: size[n[4]] = size.get(n[4], 0) + 1
have = {}
for n in keep: have[n[4]] = have.get(n[4], 0) + 1
keep = [n for n in keep if have[n[4]] == size[n[4]]]
ev = sorted(keep + high)
notes, toks, t, prev = [], [], A, None
for s, e, p, syl, key in ev:
    if s > t + 1e-6: notes.append([0, round(s - t, 4)])
    notes.append([p, round(e - s, 4)]); t = e
    if syl == '~':
        toks.append(' ~'); prev = None
    else:
        toks.append(('' if key == prev else ' ') + syl); prev = key
end = A + sum(d for _, d in hm['notes'])
notes.append([0, round(end - t, 4)])
words = ''.join(toks).strip()
json.dump({**em, 'lyrics': words, 'notes': notes}, open('second.json', 'w'), ensure_ascii=False)
print(len(keep), 'harmony notes +', len(high), 'high notes =', len(ev), '\n', words)
