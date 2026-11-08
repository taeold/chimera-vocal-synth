import struct, collections, json
data = open('os.proto','rb').read()
def varint(b, i):
    r = s = 0
    while True:
        c = b[i]; i += 1; r |= (c & 0x7f) << s; s += 7
        if c < 0x80: return r, i
def fields(b):
    i = 0; out = []
    while i < len(b):
        k, i = varint(b, i); f, w = k >> 3, k & 7
        if w == 0: v, i = varint(b, i)
        elif w == 5: v = struct.unpack('<f', b[i:i+4])[0]; i += 4
        elif w == 1: v = struct.unpack('<d', b[i:i+8])[0]; i += 8
        elif w == 2: n, i = varint(b, i); v = b[i:i+n]; i += n
        out.append((f, v))
    return out
top = fields(data)
settings = dict((f, v) for f, v in fields([v for f, v in top if f == 1][0]) if not isinstance(v, bytes))
notes = []
for f, v in top:
    if f == 2:
        d = dict(fields(v)); notes.append({'type': d.get(1, 0), 'time': d.get(2, 0.0), 'len': d.get(3, 0.0), 'inst': d.get(4, 0), 'vol': d.get(5, 1.0)})
print('settings', settings, 'notes', len(notes))
by = collections.defaultdict(list)
for n in notes: by[n['inst']].append(n)
for inst, ns in sorted(by.items()):
    ts = [n['type'] for n in ns]; tm = [n['time'] for n in ns]
    print(f"inst {inst:3d}: {len(ns):4d} notes  type {min(ts)}-{max(ts)}  time {min(tm):.0f}-{max(tm):.0f}")
json.dump({'bpm': settings.get(1), 'notes': notes}, open('os_notes.json', 'w'))
