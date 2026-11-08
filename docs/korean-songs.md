# Korean songs on CHIMERA: how a request becomes a duet video

A recipe book for singing a Korean song's part as a duet on the duet page (`?show=<id>`) and
recording it as a video. This branch (`korean-recipes`) carries the engine changes it relies on:
Korean lyrics (PR #29) and softened consonants. Its tools are in `tools/korean/korean/`. Two songs went
through it: BIGBANG "BANG BANG BANG" (verse 1) and 자전거 탄 풍경 "너에게 난, 나에게 넌" (last chorus).
Shows, lyrics, MIDI and audio stay out of git (`public/shows/` is gitignored); only the method
and the tools are here.

## Who does what

Claude can't hear audio and can't log in to sites. Everything else it can do.

| Step | You | Claude |
|---|---|---|
| Pick the song and the part (lyric lines, or a time like 3:00-3:40) | yes | |
| Find a MIDI | optional | searches Online Sequencer and midiex; can't use logins |
| Get the full MIDI from midiex, or a MuseScore file | yes (needs your login) | |
| The original recording (mp3/m4a) of that part | yes, strongly recommended | can't download from YouTube or streaming |
| The lyrics of that part, one line per phrase, marked by who sings: lead / second / together / (echo) | yes | doesn't write out song lyrics itself |
| Ad-lib words ("우", "예", "오") | yes, if you know them | uses "아" otherwise |
| Find the parts, octaves, tempo and structure | | yes (from MIDI + recording) |
| Melody files, rendering, pitch checks, mix, page, video | | yes |
| Judge by ear: words, feel, levels | yes | measures only |

The minimum to start: the song, the part, and the lyrics. The best result also needs a MIDI
with separate tracks and the original recording.

## What each source gives

- **MIDI with separate tracks** (midiex full file, or the preview player's file for its first
  60 beats): exact notes for each part. The best melody source.
- **Online Sequencer** (`onlinesequencer.net/<id>`): often the same MIDI, but some imports merge
  every track into one instrument (5643 notes in one track for 너에게 난), so the tune can't be
  picked out reliably. Fine as a backing source when its tracks are separate (BANG BANG BANG).
- **The original recording**: settles every question the MIDI can't. Each part's octave, the
  real tempo, where the high voice and ad-libs are, and the band itself (the instrumental with the
  vocals removed) as backing. Keep it on the VM, never in git.
- **Your lyrics**: one syllable per note. Hangul is one block per note. `~` holds the last
  vowel over another note.
- **A voice memo of you singing a part** over the original: the cleanest way to give a line the
  MIDI lacks, such as ad-libs.

## The pipeline (about an hour of Claude time per song, plus the video)

1. **Get the MIDI.** `tools/korean/os_search.cjs <title>` and `tools/korean/os_fetch.cjs <id> <out.proto>`,
   then `tools/korean/os_decode.py` for Online Sequencer. For midiex, `preview_src.php?bo_table=midi&wr_id=<id>&file_id=0`
   gives the preview (first ~60 beats); the full file needs your login.
   `tools/korean/midiparse.py file.mid` lists channels, instruments, ranges and beats.
2. **Map the song.** Split the tune channel into phrases at rests of a beat or more. Count each
   phrase's notes against your lyrics' syllables: they must match. That finds the chorus without
   guessing. Look for the vocal-like channels: a harmony moving note for note with the tune, and
   echo or "ooh" lines.
3. **With the recording:** separate the vocals and the band (Demucs: about 1.5 min for 70 s,
   niced, one thread). Draw a pitch map (`tools/korean/sal.py`), fit the MIDI tune to it for tempo,
   offset and octave (`tools/korean/align.py`), and transcribe the vocals into notes (`tools/korean/bp.py`,
   Basic Pitch). Then check every MIDI vocal part at its written octave and an octave down, and use
   the octave the record matches. Also check the alignment over shorter stretches by pitch, not
   by onsets.
4. **Build the melody files** (`tools/korean/song-template/build.py` is the model, lyrics taken out; then
   `second.py` merges parts into two singers). Settings: legato (a note runs into the next unless the rest
   is over half a beat), the tune's syllables mapped onto the harmony by onset, echo words on
   the echo channel, "아" for wordless high notes (the user's ad-lib words when known).
5. **Render** with the branch's CLI: `chimera render notes part.json part <male|female> --tele part.tele`.
6. **Check:** `tools/korean/pitchcheck.py` (notes within 50 cents; it misreads short notes measured on
   their consonant), `tools/korean/gaps.py` (dropouts inside phrases), `tools/korean/dips_by_onset.py`
   (which consonants cut the line).
7. **Mix** (`tools/korean/song-template/mix-duo.sh`) and publish to `dist/shows/<id>/` with a
   `show.json`. Serve with `bun run preview -- --port 8006 --host 0.0.0.0`.
8. **Video:** `tools/korean/record.cjs <show> 30 <seconds> <dir>` captures frame by frame on a fake
   clock, then ffmpeg joins the frames with the mix. About 0.9 s per frame on this VM: a 40 s clip
   takes about 18 minutes. Say so before starting.

The scripts were written for these two songs. Before reusing one, change the song-specific
values at its top: file paths (they point at `/tmp/...` working folders and at a clone in
`/tmp/chimera-vocal-synth`), beat windows, tempo and offset (`BPM, OFF, B0REF`).

## Defaults the user approved

- Two singers, like the record: the lead male, the second singer on the female voice. A male
  falsetto at B4-F5 measures cleaner on the female voice: 3 dB less breath noise above 5 kHz.
- The second singer 2 dB above the lead while singing, after its EQ and a 3:1 compressor
  (threshold 0.08), which keeps its high notes from dipping. Its breath above 5 kHz cut 6 dB.
- Wordless high notes on "아", not "우": [u] is dark and quiet. On the held B4 and F5, "아"
  measured 14-16 dB more energy at 1-5 kHz than "우".
- Reverb light: hall send 0.025, half that on the second singer.
- The band 10 dB under the voices when it's the record's own instrumental. A MIDI band in
  General MIDI sounds needed more distance, and the user still called it too loud at 10.
- Pan the lead a little left and the second a little right. Vibrato 25-30 cents.

## Traps we hit

- **Guessing a melody or where words go.** The first BANG BANG BANG versions came from a fan
  piano transcription and guessed word placement, and sounded "nothing like the song". Use a
  MIDI, and the user's words for placement.
- **A MIDI's octaves differ by track.** In 너에게 난 the tune is written an octave above the
  singer, while the harmony and the high voice are written where they're sung. I lowered all
  three and the harmony sounded wrong from the start. Check each part against the recording.
- **A MIDI "harmony" may sit below the tune.** Moving it up made parallel fourths. Check what the
  record does before rewriting it.
- **"Harmony" can mean ad-libs.** The user's "harmony" was the second singer's high echoes and
  held notes. Ask, or look at the recording.
- **Staccato came from consonants, not timing.** The engine's stops close fully: a voiced stop
  between vowels was a 40-66 dB gap. Fixed in the engine (patch 0002): soften lax ㄱ ㄷ ㅂ ㅈ
  between voiced sounds, across spaces within a phrase. Shorter consonants alone didn't help.
- **ffmpeg `afir dry=` is the input gain**, not a dry/wet mix: `dry=0` gives silence. Use
  `dry=1:wet=1:gtype=none` and mix the wet signal in at about 0.025.
- **Re-running a build script overwrites hand-made files** (it once replaced a new harmony with an
  old one). Render, then check that the JSON and the audio agree.
- **Headless Chromium's audio clock runs fast.** Seek with the slider for screenshots, and use
  the fake clock in `record.cjs` for video.
- **Onset correlation between synth and real voices is noise.** Check timing by pitch.
- **The engine's female voice is quieter at its top** (F5 about 10 dB under its other held
  notes on "우"). An open vowel and the compressor fix it; check long notes' levels by pitch.

## Known limits

- Every note is sung at the same strength: the MIDI's velocities aren't used yet.
- No tense consonants in the engine (ㄲ ㄸ ㅃ ㅉ ㅆ are soft). ㅎ and aspirated ㅊ ㅍ ㅋ still cut the
  line; that's mostly faithful to Korean.
- Two singers can't stack three record notes (the 너에게 난 ending loses its middle note).
- The page writes words under the chin when panels are narrow (three or more heads).

## Where things stand (2026-11-08)

- PR https://github.com/jamesondh/chimera-vocal-synth/pull/29: Korean lyrics. Open, no reply yet.
- Softened consonants and the `consonants` option: the commit under this guide on this branch
  (`cargo test --workspace` passes). Not in PR #29.
- The one-line Hangul fix for PR #24's MusicXML converter: not posted.
- Tools need: Rust with wasm32, Bun, ffmpeg, fluidsynth with FluidR3_GM, and a Python venv. Make
  the venv with `python3 -m venv /tmp/anv`, then
  `pip install numpy torch torchaudio --index-url https://download.pytorch.org/whl/cpu`, then
  `pip install demucs soundfile onnxruntime librosa mir_eval pretty_midi resampy scipy`, and
  `basic-pitch` with `--no-deps`.
