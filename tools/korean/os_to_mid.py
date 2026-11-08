# The Online Sequencer arrangement (os_notes.json) → a General MIDI file, bars a..b (16ths), with
# some tracks left out. OS time unit = a 16th; OS note type = MIDI note (drum kits: GM drum note).
#   python3 os_to_mid.py out.mid START_16TH END_16TH [skip,inst,ids]
import json, struct, sys
N = json.load(open('/tmp/mxl-test/os_notes.json'))['notes']
out, a, b = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
skip = {int(x) for x in sys.argv[4].split(',')} if len(sys.argv) > 4 and sys.argv[4] else set()
# OS instrument → GM program (None: drums on channel 10)
GM = {0: 4, 1: 25, 3: 81, 5: 33, 8: 0, 10: 57, 13: 62, 16: 62, 19: 13, 20: 45, 21: 114,
      25: 3, 33: 107, 34: 11, 2: None, 31: None, 36: None}
TPQ = 96; T16 = TPQ // 4
def vlq(n):
    bs = [n & 0x7f]; n >>= 7
    while n: bs.insert(0, (n & 0x7f) | 0x80); n >>= 7
    return bytes(bs)
tracks, ch = [], 0
tempo = bytes([0x00, 0xFF, 0x51, 0x03]) + (int(60e6 / 135)).to_bytes(3, 'big')
tracks.append(tempo + b'\x00\xff\x2f\x00')
for inst in sorted({n['inst'] for n in N}):
    if inst in skip: continue
    prog = GM.get(inst, 0)
    c = 9 if prog is None else ch
    if prog is not None:
        ch += 1
        if ch == 9: ch = 10
    evs = []
    for n in N:
        if n['inst'] != inst or not (a <= n['time'] < b): continue
        t0 = round((n['time'] - a) * T16); t1 = t0 + max(1, round(n['len'] * T16))
        vel = max(1, min(127, int(100 * n.get('vol', 1))))
        evs.append((t0, 1, bytes([0x90 | c, n['type'], vel])))
        evs.append((t1, 0, bytes([0x80 | c, n['type'], 0])))
    if not evs: continue
    data = b'' if prog is None else b'\x00' + bytes([0xC0 | c, prog])
    t = 0
    for tt, _, e in sorted(evs, key=lambda e: (e[0], e[1])):
        data += vlq(tt - t) + e; t = tt
    tracks.append(data + b'\x00\xff\x2f\x00')
with open(out, 'wb') as f:
    f.write(b'MThd' + struct.pack('>IHHH', 6, 1, len(tracks), TPQ))
    for tr in tracks: f.write(b'MTrk' + struct.pack('>I', len(tr)) + tr)
print(out, len(tracks) - 1, 'tracks')
