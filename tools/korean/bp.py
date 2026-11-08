import json, warnings; warnings.filterwarnings('ignore')
from basic_pitch.inference import predict
from basic_pitch import ICASSP_2022_MODEL_PATH
import os
_, _, ev = predict('/tmp/orig/sep/htdemucs/final_st/vocals.wav', os.path.join(os.path.dirname(ICASSP_2022_MODEL_PATH), 'nmp.onnx'),
                   onset_threshold=0.5, frame_threshold=0.3, minimum_note_length=80, minimum_frequency=90, maximum_frequency=900)
notes = sorted([[float(s), float(e), int(p), float(a)] for s, e, p, a, *_ in ev])
json.dump(notes, open('/tmp/orig/bp_notes.json', 'w'))
print(len(notes), 'notes')
