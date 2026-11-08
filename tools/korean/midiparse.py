import struct, sys, collections, json
def parse(path):
    d = open(path, 'rb').read()
    assert d[:4] == b'MThd'
    _, fmt, ntr, div = struct.unpack('>IHHH', d[4:14]); i = 14
    notes, meta, tempos, progs = [], [], [], {}
    for _ in range(ntr):
        assert d[i:i+4] == b'MTrk'; L = struct.unpack('>I', d[i+4:i+8])[0]; j = i + 8; end = j + L; i = end
        t = 0; run = None; on = {}
        def vlq():
            nonlocal j
            v = 0
            while True:
                c = d[j]; j += 1; v = (v << 7) | (c & 0x7f)
                if c < 0x80: return v
        while j < end:
            t += vlq(); st = d[j]
            if st == 0xFF:
                typ = d[j+1]; j += 2; n = vlq(); data = d[j:j+n]; j += n
                if typ == 0x51: tempos.append((t, int.from_bytes(data, 'big')))
                elif typ in (1, 3, 5, 6): meta.append((t, typ, data))
                continue
            if st in (0xF0, 0xF7):
                j += 1; n = vlq(); j += n; continue
            if st & 0x80: run = st; j += 1
            ch, kind = run & 0x0f, run & 0xf0
            if kind in (0xC0, 0xD0): a = d[j]; j += 1; b = 0
            else: a, b = d[j], d[j+1]; j += 2
            if kind == 0xC0: progs.setdefault(ch, a)
            if kind == 0x90 and b > 0: on[(ch, a)] = (t, b)
            elif kind in (0x80, 0x90) and (ch, a) in on:
                t0, v = on.pop((ch, a)); notes.append({'ch': ch, 'pitch': a, 't0': t0, 't1': t, 'vel': v})
    return fmt, div, notes, meta, tempos, progs
if __name__ == '__main__':
    fmt, div, notes, meta, tempos, progs = parse(sys.argv[1])
    print('format', fmt, 'division', div, 'tempos', [(t, round(60e6/u, 1)) for t, u in tempos[:5]], 'programs', progs)
    by = collections.defaultdict(list)
    for n in notes: by[n['ch']].append(n)
    end = max(n['t1'] for n in notes)
    print('notes', len(notes), 'length', end / div, 'beats')
    for ch, ns in sorted(by.items()):
        print(f"ch {ch+1:2d} prog {progs.get(ch)}: {len(ns)} notes, pitch {min(n['pitch'] for n in ns)}-{max(n['pitch'] for n in ns)}, beats {min(n['t0'] for n in ns)/div:.0f}-{max(n['t1'] for n in ns)/div:.0f}")
    for t, typ, data in meta[:12]:
        for enc in ('utf-8', 'cp949'):
            try: s = data.decode(enc); break
            except Exception: s = repr(data)
        print('meta', typ, t / div, s[:60])
