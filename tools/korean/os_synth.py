# Plays the Online Sequencer arrangement back as plain tones (no drums), so a listener can say
# which bars are the part they mean. MIDI = OS note type; one OS time unit = a 16th at 135 BPM.
import json, math, wave, array, sys
N = json.load(open('/tmp/mxl-test/os_notes.json'))['notes']
SR, BPM = 22050, 135
U = 60 / BPM / 4
a, b = (int(sys.argv[1]), int(sys.argv[2])) if len(sys.argv) > 2 else (0, 48)
out = [0.0] * int(((b - a) * 16 * U + 1) * SR)
for n in N:
    if n['inst'] in (2, 31) or not (a * 16 <= n['time'] < b * 16): continue
    f = 440 * 2 ** ((n['type'] - 69) / 12)
    s0 = int((n['time'] - a * 16) * U * SR); L = int(max(n['len'], 1) * U * SR)
    v = 0.12 * n.get('vol', 1)
    for i in range(L + int(0.05 * SR)):
        t = i / SR
        env = min(1, t / 0.005) * (math.exp(-3 * t) if i < L else math.exp(-3 * t) * (1 - (i - L) / (0.05 * SR)))
        out[s0 + i] += v * env * (math.sin(2 * math.pi * f * t) + 0.3 * math.sin(4 * math.pi * f * t))
pk = max(abs(x) for x in out) or 1
w = wave.open(sys.argv[3] if len(sys.argv) > 3 else 'seq.wav', 'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
w.writeframes(array.array('h', (int(0.9 * 32767 * x / pk) for x in out)).tobytes()); w.close()
