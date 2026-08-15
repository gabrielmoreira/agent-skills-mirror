---
name: timed-lyric-transcription
description: "Produces word- and segment-timed transcripts with WhisperX or faster-whisper, optional Demucs vocal stems, then SRT, VTT, ASS karaoke, or JSON for lip-sync. Trigger on timestamped lyrics, karaoke from MP3, force-align lyrics, viseme tracks, or Whisper JSON to SRT. Do not use for livestream captioning or DRM-encrypted audio."
version: 1.0.1
---

# Timed Lyric Transcription

Turns an audio file into precisely-timed text in whatever format the downstream task needs: SRT/VTT for video subtitles, ASS for karaoke-style highlighting, or JSON for programmatic lip-sync and animation. Music and lyrics are the specialty — vocal isolation, forced alignment, karaoke output — but plain speech (podcasts, dialog, lectures) works through a simpler subset of the same pipeline.

The pieces are bundled together because they're coupled: the model you pick constrains what timestamps you can get, vocal isolation changes what the model sees, and the output format determines whether word-level timing is needed at all. Picking them in isolation tends to mean re-running the pipeline — expensive on long audio, free on short clips. When in doubt, prototype on a 30–60 s slice first.

## When to Use

Use this skill when any of the following apply:

- You need **SRT, VTT, or ASS subtitles** from an audio or video file.
- You need **word-level timestamps** for karaoke, lip-sync, viseme tracks, or animation.
- You need to **force-align known lyrics** to audio (lyrics text already exists, only timing is needed).
- You need to **isolate vocals** from a music track before transcribing.
- You need to **fix subtitle drift** or convert Whisper JSON to SRT/VTT/ASS.
- You need **speaker labels with timing** (diarization for dialog/podcast content).
- Triggers: "transcribe with timestamps", "lyrics with timing", "sync lyrics to audio", "make subtitles or captions", "SRT/VTT/ASS from audio", "karaoke from MP3", "lip-sync timing", "viseme timing", "word-level timestamps", "force-align lyrics", "fix subtitle drift", "convert Whisper JSON to SRT", "speaker labels with timing", "isolate vocals and transcribe".

### Decision flow — read first

Walk these in order. Each answer rules out a chunk of the document.

1. **Music or speech?**
   - **Speech** (podcast, dialog, lecture, interview, voiceover): skip vocal isolation — there's nothing to isolate from, and Demucs on plain speech wastes minutes. `faster-whisper` is usually enough.
   - **Music with vocals**: isolating vocals first (Demucs) almost always improves accuracy on dense mixes (rock, pop, metal, orchestral); on light acoustic backing it's usually a wash. Use WhisperX for tight word timing.
   - **Mixed content** (podcast with music bed, interview with stings, ad-reads with music behind voice): treat as speech and skip Demucs. The bed is usually quiet enough that Whisper copes; Demucs on a speech-bed mix often damages the speech stem because it isn't a separation case the model trained on. See *Pitfalls → Mixed content*.

2. **Are the lyrics already known as text?**
   - **Yes**: prefer forced alignment. The model is constrained to text you provide, so it can't invent or substitute words. Accuracy is much higher and the run is faster.
   - **No, or rough/partial**: open-transcribe. Also do this if the supplied text is missing ad-libs, differs between repeated choruses, or omits intro/outro — forced alignment fails badly when the audio contains words the text doesn't.

3. **Required output format?**
   - **SRT/VTT only**: segment-level timing is enough, which keeps the pipeline simple.
   - **ASS karaoke, lip-sync, animation, viseme tracks**: word-level timing is required — that means WhisperX (best) or `faster-whisper` with `word_timestamps=True`.

4. **Language?** Any model handles English; for other languages, check whether a wav2vec2 alignment model exists for it, or accept Whisper's coarser native word timings. See *Pitfalls → Non-English alignment*.

5. **GPU available?**
   - **Yes**: `device="cuda"`, `compute_type="float16"`. See *Prerequisites → Model selection* for size choice by VRAM.
   - **No**: `device="cpu"`, `compute_type="int8"`. Drop to `small` or `medium` unless quality is critical — CPU runtime on `large-v3` is often slower than realtime, painful on multi-minute audio.

## Prerequisites

### System tools (install separately from Python deps)

```powershell
# Windows (PowerShell) — primary host
scoop install ffmpeg mpv
# or
winget install Gyan.FFmpeg mpv.mpv

# Aegisub (for ASS karaoke preview — separate install)
winget install Aegisub.Aegisub
```

On Linux/macOS: `brew install ffmpeg mpv` or `apt install ffmpeg mpv`.

Verify all are present before starting:

```powershell
ffprobe -version
ffmpeg -version
mpv --version
```

### Python packages

```powershell
pip install whisperx faster-whisper openai-whisper
pip install demucs  # vocal isolation
# Optional: diarization
pip install pyannote.audio
# Optional: lip-sync viseme conversion
pip install g2p_en
```

### Hugging Face auth (for diarization and some align models)

```powershell
huggingface-cli login
```

You must accept terms on **both** the `pyannote/speaker-diarization-3.1` and `pyannote/segmentation-3.0` model pages before diarization will work.

### First-run download budget

- `large-v3`: ~3 GB
- wav2vec2 align models: ~1 GB
- pyannote diarization: ~500 MB

Set `HF_HOME` if disk is tight or to share caches across projects.

### Model selection

Pick the smallest model that meets the quality bar for *this* audio. Bigger models compound runtime, VRAM, and download cost.

**For lyrics**, the smallest viable model is usually still `large-v3-turbo` or `large-v3`. Singing diction, sustained vowels, and overlapping instrumentation degrade smaller models very quickly — `medium` will drop syllables and substitute homophones routinely.

**For short clips (<1 min)**, iteration is cheap enough that you don't need to agonise. For multi-minute files, lock the choice on a 30–60 s prototype slice before the full run.

| Tool | Best for | Word timestamps | Notes |
|------|----------|-----------------|-------|
| `openai-whisper` (reference) | Fidelity benchmarks, short clips | Segment-level; word-level approximate | Slowest implementation. Pick only when replicating a reference result that depends on this exact decoder. |
| `faster-whisper` (CTranslate2) | Speech (podcasts, dialog, lectures), pipeline integration | Yes, via `word_timestamps=True` | ~4× faster than reference at equal accuracy. The decision-flow default for non-music. |
| `whisperx` | Music, lyrics, lip-sync, karaoke, anything needing tight word timing | Yes, via wav2vec2 forced alignment | The decision-flow default for music/lyrics. The forced-alignment pass brings word boundaries inside ~80 ms, which makes karaoke highlights track the audio visibly accurately at 24–30 fps. |
| `whisper.cpp` | CPU-only / embedded targets | Yes, via `--output-words` | Reasonable quality without CUDA. Good fallback when PyTorch isn't viable. |
| Cloud APIs (Deepgram, AssemblyAI, OpenAI Whisper API) | One-shot quick captions, no local GPU | Provider-dependent — some offer word timing, often centisecond-rounded | Not suitable for karaoke or lip-sync where boundaries need to be tight; usable for subtitle-only work. Benchmark on your audio before committing. |

Model sizes (quality vs. VRAM/runtime):

- `tiny` / `base`: drafts, fast iteration on short clips.
- `small`: ~2 GB VRAM, fast, acceptable for clean English speech.
- `medium`: balanced for English speech in noisy environments. Sane choice for clean speech on 4–5 GB GPUs where `large-v3-turbo` won't fit alongside VAD and align models.
- `large-v3`: best raw quality. ~10 GB VRAM, slow. Worth it for unclear vocals, accents, non-English, or dense lyrics.
- `large-v3-turbo`: near-`large-v3` quality at roughly 3× the speed. Fits in ~6 GB VRAM with `float16`, or ~3.5 GB with `int8_float16`. Default when those numbers fit; otherwise step down to `medium`.

`compute_type` options:

- `float16` (GPU, default): best accuracy, full VRAM cost.
- `int8_float16` (GPU): halves VRAM with a small accuracy hit. Reach for it when `float16` OOMs and you don't want to drop model size.
- `int8` (CPU): only sensible CPU option for the larger models.

## Procedure

### Step 1 — Probe the input

Run `ffprobe` first so you know what you're feeding the model:

```powershell
ffprobe -v error -show_streams -show_format "input.ext"
```

Check:
- **Container.** Whisper-family tools accept anything ffmpeg can decode: MP3, WAV, FLAC, OGG, M4A, MP4, MKV, WebM. Video containers are handled internally — no manual demux needed unless chunking.
- **DRM / encrypted streams.** `ffprobe` will surface `encrypted=1` or fail to read streams from DRM-protected files. Whisper can't transcribe these directly. Source un-DRM'd audio or skip.
- **Sample rate / channels.** Models work internally at 16 kHz mono and libraries resample automatically. On very long files, pre-converting saves a few seconds per run and avoids the offset-quirk failure mode:
  ```powershell
  ffmpeg -i "input.mp4" -ac 1 -ar 16000 -vn "input_16k.wav"
  ```
- **Whisper's 30 s window.** Whisper encodes audio in fixed 30 s windows. For audio longer than that, it slides the window forward and conditions on previously-decoded text — which is where drift and "previous-text hallucination" come from on long files. Audio under ~30 s sees no sliding and is usually clean. When chunking very long files, chunks that are a small multiple of 30 s (e.g., 600 s = 20 windows) align cleanly with the encoder boundary.
- **Length.** Files past ~30 minutes start accumulating drift and risk OOM on `large-v3`. A 35-min interview is usually fine — silence between turns lets Whisper "reset" its internal state. A 35-min live concert is not — constant audio energy means no reset points, and drift compounds. Chunk when in doubt.

### Step 2 — Isolate vocals (music only, skip for speech)

When vocals sit under heavy instrumentation (rock, metal, dense pop, orchestral), isolating vocals first dramatically improves accuracy. Whisper was trained mostly on speech, so instrumental energy both shifts its timestamps and triggers hallucinated words.

```powershell
# Demucs — highest quality of the open-source separators, PyTorch-based, GPU recommended
python -m demucs --two-stems=vocals -o separated "input.mp3"
# → separated/htdemucs/input/vocals.wav
```

**Skip vocal isolation when:**
- Plain speech — nothing to isolate from.
- Mixed content (podcasts with music beds, interviews with stings) — Demucs on speech-bed mixes can degrade the speech stem.
- Acoustic ballads with light backing — Whisper usually handles these cleanly.

If unsure whether isolation will help, run both on a 30 s slice and listen to the resulting transcripts — the difference is usually obvious within one verse.

### Step 3 — Transcribe with timing

#### Option A — WhisperX (default for music/lyrics)

```powershell
pip install whisperx

whisperx "vocals.wav" `
  --model large-v3 `
  --language en `
  --align_model WAV2VEC2_ASR_LARGE_LV60K_960H `
  --vad_filter True `
  --output_format srt --output_format json --output_format vtt `
  --output_dir out/
```

Why these flags:
- `--align_model` runs a second pass with wav2vec2 (a phoneme-level acoustic model trained on raw audio) over Whisper's draft text, sharpening word timings. Without it, WhisperX is essentially Whisper with extra setup cost.
- `--vad_filter` (voice-activity detection) trims silence before transcription. Speeds runs up and prevents Whisper's most common failure on songs: hallucinating during instrumental gaps. Leave it on. The signal that it's *too* aggressive is missing transcript content over passages where vocals were definitely present (a whispered bridge, a sustained held note at low volume) — when you see that, rerun a 30 s slice with VAD off and compare.
- `--diarize` (optional) tags speakers. Useful for dialog, irrelevant for solo vocals. Requires HF auth and accepted licences on both the diarization pipeline and the underlying segmentation model.

> **HARD RULE:** CLI flag spelling and form drift between WhisperX versions — some builds want `--vad_filter` as a bare switch and reject `True` as an argument, newer builds use `--vad_method silero|pyannote` instead. If a flag is rejected, check `whisperx --help` for the current spelling. Do not invent flags.

#### Option B — faster-whisper via Python (when pipeline control matters)

```python
from faster_whisper import WhisperModel

# GPU
model = WhisperModel("large-v3", device="cuda", compute_type="float16")
# CPU fallback
# model = WhisperModel("medium", device="cpu", compute_type="int8")

segments, info = model.transcribe(
    "vocals.wav",
    word_timestamps=True,
    vad_filter=True,
    beam_size=5,
    language="en",  # omit on clean 30s+ samples if unsure — auto-detect is reliable there
)

# Wrap in {"segments": [...]} so downstream writers (SRT/ASS/JSON below)
# see the same shape as WhisperX's native output.
result = {"segments": []}
for seg in segments:
    result["segments"].append({
        "start": seg.start,
        "end": seg.end,
        "text": seg.text,
        "words": [
            {"start": w.start, "end": w.end, "word": w.word, "prob": w.probability}
            for w in (seg.words or [])
        ],
    })
```

#### Chunked processing for long files (>30 min)

For files past ~30 min, chunk to bound memory use and prevent drift. The `ffmpeg` segment muxer doesn't natively support overlapping chunks (`-segment_overlap` is not a real flag), so produce overlapping chunks by issuing one ffmpeg per chunk with `-ss` and `-t`:

```python
import subprocess, math

def probe_duration(path):
    out = subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "csv=p=0", path,
    ])
    return float(out.strip())

src = "input.wav"
chunk_s, overlap_s = 600, 5         # 10 min chunks with 5 s overlap
step_s = chunk_s - overlap_s
n_chunks = math.ceil(probe_duration(src) / step_s)

for i in range(n_chunks):
    start = i * step_s
    subprocess.run([
        "ffmpeg", "-y", "-ss", str(start), "-t", str(chunk_s),
        "-i", src, "-c", "copy", f"chunk_{i:03d}.wav",
    ], check=True)
```

Transcribe each chunk independently, then stitch:

1. Compute each chunk's absolute start time: `i * step_s`.
2. Shift every word's `start` and `end` in that chunk by the offset.
3. For each chunk past the first, drop words whose `start` falls inside the previous chunk's tail overlap window (i.e., within the final `overlap_s` seconds of the previous chunk's range). This prevents double-counting words spoken across the boundary.

Chunk size choice: 600 s aligns to twenty 30 s Whisper windows, which keeps internal drift modest. Larger chunks (1200 s, 1800 s) work too but compound drift; smaller chunks (300 s, 60 s) eliminate drift entirely at the cost of more stitching overhead.

### Step 4 — Forced alignment (when lyrics text is already known)

When the user supplies lyrics text alongside the audio and only needs timing, prefer forced alignment over open transcription. The model is constrained to the provided text, so it can't invent or substitute words.

> **HARD RULE:** Fall back to open transcription if the lyrics are incomplete, include different ad-libs, or change between verse repetitions — alignment fails badly when the audio contains text the lyrics don't.

Building segments from a plain `lyrics.txt` (one lyric line per line):

```python
import json, whisperx

audio = whisperx.load_audio("vocals.wav")
align_model, metadata = whisperx.load_align_model(language_code="en", device="cuda")

# Coarse segments — alignment refines timings, so start/end only need to be a rough hint.
# Even-division works when line density is roughly uniform across the song.
# Sanity-check the first 60 s of output on real audio before committing to a full run:
# if lines are heavily front- or back-loaded (long instrumental intro, slow outro),
# the alignment search can mis-anchor and you may need to provide better seed times
# (e.g., from a chorus marker file or a short Whisper pre-pass).
with open("lyrics.txt", encoding="utf-8") as f:
    lines = [ln.strip() for ln in f if ln.strip()]

audio_duration = len(audio) / 16000  # whisperx loads at 16 kHz
slot = audio_duration / len(lines)
segments = [
    {"start": i * slot, "end": (i + 1) * slot, "text": line}
    for i, line in enumerate(lines)
]

aligned = whisperx.align(
    segments, align_model, metadata, audio, device="cuda",
    return_char_alignments=False,
)

# `aligned` has the same shape as a WhisperX transcription result:
# {"segments": [{"start", "end", "text", "words": [{"start", "end", "word", "prob"}]}]}
```

### Step 5 — Format the output

The canonical intermediate structure (emitted by both WhisperX and the faster-whisper wrapper above):

```json
{
  "segments": [
    {
      "start": 1.23,
      "end": 4.56,
      "text": "Hello world",
      "words": [
        {"start": 1.23, "end": 1.89, "word": "Hello", "prob": 0.95},
        {"start": 1.89, "end": 4.56, "word": "world", "prob": 0.91}
      ]
    }
  ]
}
```

#### SRT

```python
def to_srt(result, max_chars=42):
    entries = []
    for i, seg in enumerate(result["segments"], 1):
        start = fmt_ts(seg["start"])
        end = fmt_ts(seg["end"])
        text = reflow(seg["text"], max_chars)
        entries.append(f"{i}\n{start} --> {end}\n{text}\n")
    return "\n".join(entries)

def fmt_ts(s):
    h = int(s // 3600)
    m = int((s % 3600) // 60)
    sec = int(s % 60)
    ms = int((s - int(s)) * 1000)
    return f"{h:02d}:{m:02d}:{sec:02d},{ms:03d}"
```

#### VTT

Same as SRT but: `.` instead of `,` for the millisecond separator, header line `WEBVTT`, and no segment index numbers.

#### ASS karaoke

ASS karaoke uses `{\k<centiseconds>}` before each word; the number is how long that word stays highlighted before the next one takes over.

```python
def to_ass_karaoke_line(words):
    parts = []
    for w in words:
        cs = max(1, round((w["end"] - w["start"]) * 100))
        parts.append(f"{{\\k{cs}}}{w['word']}")
    return "".join(parts)
```

Wrap the output in a standard ASS header with `[Script Info]`, `[V4+ Styles]`, and `[Events]` sections. For RTL languages, set the style's `Encoding` field appropriately and verify in Aegisub — some renderers mishandle RTL inside `\k` blocks. Preview in Aegisub (separate install); its timeline shows karaoke fills visually, which surfaces timing problems much faster than reading numbers.

#### JSON (lip-sync, animation, programmatic consumers)

Ship the canonical structure above (`{segments: [{start, end, text, words: [...]}]}`) unless the consumer specifies a different schema. This shape preserves both segment hierarchy (for caption-style use) and flat word timing (for animation), and matches what WhisperX and faster-whisper emit natively, so it minimises mapping work.

For lip-sync, consumers usually want **visemes** (mouth shapes) rather than phonemes. `g2p_en` converts words to ARPAbet phonemes (e.g. `HELLO → HH AH L OW`); mapping phonemes to visemes is a separate step using whichever inventory the renderer expects. Common inventories differ in both count and grouping — Oculus uses 15 visemes, Preston Blair's classic animation set has 10 mouth shapes, Rhubarb Lip Sync ships with 9 by default. There is no universal phoneme→viseme map; pick the one matching the target rig, otherwise the mouth shapes will be subtly off (e.g., `f` and `v` collapsed wrongly).

### Step 6 — Preview

```powershell
# Audible playback with subs — drift is obvious by ear
mpv "song.mp3" --sub-file=out/song.srt

# For ASS karaoke, preview in Aegisub — scrub the timeline to see karaoke fills
```

### End-to-end example (canonical music-to-karaoke pipeline)

English pop track, GPU available:

```powershell
# 1. Isolate vocals
python -m demucs --two-stems=vocals -o separated "song.mp3"

# 2. Transcribe + align — WhisperX writes SRT, VTT, and JSON in a single pass
whisperx "separated/htdemucs/song/vocals.wav" `
  --model large-v3 `
  --language en `
  --align_model WAV2VEC2_ASR_LARGE_LV60K_960H `
  --vad_filter True `
  --output_format srt --output_format vtt --output_format json `
  --output_dir out/

# 3. Convert WhisperX JSON to ASS karaoke (builder shown in ASS section above)
python build_ass_karaoke.py out/vocals.json > out/song.ass

# 4. Preview against the original mix
mpv "song.mp3" --sub-file=out/song.ass
```

For speech (podcast, dialog), drop steps 1 and 3 and consider `medium` or `large-v3-turbo` in step 2 — those are usually quality-sufficient on speech and significantly faster than `large-v3`.

## Pitfalls

### Failure-mode cheat sheet

Skim this first when something looks wrong. Most rows are fixable without rerunning the full pipeline.

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Hallucinated words during instrumental sections | Whisper fills silence with plausible-sounding text when no VAD gate is present | Enable `vad_filter=True` (Python) or VAD flag (CLI) — VAD trims non-speech before the model ever sees it |
| Word timings drift later in long files | Whisper's per-segment positional bias accumulates over long audio | Use WhisperX forced alignment (re-anchors timings to acoustic features); for very long files, chunk to ≤10 min pieces and stitch |
| Lyrics partially or mostly wrong | Vocals buried under instrumentation; Whisper can't hear the words clearly | Run Demucs to isolate the vocal stem, then transcribe that |
| Karaoke highlights lag the singing | Whisper's native word timings are coarse (empirically ~±200–500 ms) — fine for subs, visibly wrong for karaoke | Use WhisperX; the wav2vec2 alignment pass tightens boundaries to ~±20–80 ms on clean English (own measurements; varies by language and audio) |
| Wrong language auto-detected | Detection sampled the intro, which was silence or instrumental | Pass `--language` explicitly — one flag, saves a full re-run |
| OOM on `large-v3` | Model + audio + activations exceed VRAM | Use `large-v3-turbo` (smaller, comparable quality), drop to `medium`, or set `compute_type="int8_float16"` — roughly half the VRAM with a small accuracy hit |
| Timestamps off by a constant offset | Sample-rate or encoder-delay quirk in the input confused the decoder | Re-encode to 16 kHz mono WAV (see *Procedure → Step 1*) and re-run — post-shifting hides the root cause and re-bites on the next file from the same source |
| Punctuation missing in aligned output | WhisperX alignment strips punctuation during tokenization | Keep the pre-alignment text and re-merge punctuation back into aligned words by index |
| Diarization fails to start | pyannote needs HF auth and accepted licences on both the pipeline and segmentation models | `huggingface-cli login`; accept terms on `pyannote/speaker-diarization-3.1` *and* `pyannote/segmentation-3.0` model pages |
| Demucs install fails (CUDA mismatch, torch ABI) | PyTorch wheel doesn't match the local CUDA toolkit | Try CPU Demucs (`-d cpu`, much slower but works); fall back to UVR-MDX or Spleeter; or skip isolation and transcribe the original mix with reduced accuracy |
| `mpv` / `aegisub` / `ffprobe` not found | These ship separately from the Python deps | Install via package manager (`scoop`, `winget`, `brew`, `apt`) |

### Non-English alignment

WhisperX needs a wav2vec2 model matching the language. `WAV2VEC2_ASR_LARGE_LV60K_960H` is English-only; WhisperX ships pretrained defaults for ~20 languages (fr, de, es, it, pt, nl, ja, zh, ko, ar, hi, ru, pl, uk, cs, fa, el, tr, da, he, vi, and more — the set grows). For languages without a pretrained wav2vec2, WhisperX silently falls back to Whisper's native (coarser) word timings. Usable for subtitles, looser for karaoke (highlights may visibly trail by a syllable).

### Multilingual / code-switched audio

No single alignment model covers arbitrary mixes (K-pop English-Korean lines, Spanglish, etc.). Two practical options: run WhisperX twice with different `--language` settings on the relevant sections and merge, or accept Whisper's native multilingual word stamps and skip alignment.

### Rap and very fast delivery

Small and medium models drop syllables on dense flows. Use `large-v3` or `large-v3-turbo`; for very dense bars (e.g., 8+ syllables per second), enable character-level alignment (`return_char_alignments=True`) so highlights can land mid-word.

### Duets and overlapping vocals

Whisper merges them into a single text stream regardless of source. Demucs returns one combined vocal stem, not split voices. Diarization (pyannote) helps on spoken dialog but rarely on singing — pyannote is trained on speech, not vocals. For studio tracks where each voice exists on a separate stem upstream, transcribe each stem and merge results.

### Auto-tuned, vocoded, or talkbox vocals

Demucs may not separate cleanly when processing is heavy — the "vocal" stem can come back robotic and *less* intelligible than the original mix. If isolation hurts intelligibility, transcribe the original mix and accept lower accuracy.

### Very short clips (<5 s)

Auto language detection is unreliable on these — too little audio to sample. Pass `--language` explicitly.

### Mixed content (podcast with music bed, interview with stings, ad-reads)

The music is usually quiet enough that Whisper copes without isolation; running Demucs on this kind of mix tends to degrade the speech stem because the network wasn't trained on speech-over-music separation. Treat as speech.

### Non-speech audio events for accessibility-grade captions

Whisper sometimes emits annotations like `[Music]` or `[Applause]` (a side-effect of its training data) and sometimes doesn't. If full accessibility-grade captioning is required, post-process with an audio event tagger (e.g., PANNs, YAMNet) and merge tags into the SRT timeline; don't rely on Whisper alone.

### Livestream / real-time captioning

This skill targets batch transcription of files. For low-latency streaming, the workflow is different (whisper-streaming, faster-whisper-server, or a cloud streaming API), and the model/chunk trade-offs invert. Out of scope here.

### DRM / encrypted source files

`ffprobe` will show encrypted streams or fail. Whisper can't transcribe DRM-protected audio directly; source unrestricted audio.

### RTL and non-Latin scripts

For RTL languages (Arabic, Hebrew), set the ASS style's `Encoding` field appropriately and verify in Aegisub — some renderers mishandle RTL inside `\k` blocks. Word order in the source is logical (first-spoken first), not visual — let the renderer reorder. For all non-Latin scripts, swap `max_chars=42` for a script-appropriate limit in `reflow()`.

### Cleanup

Intermediate files (Demucs output, resampled WAVs, chunked segments) can run to hundreds of MB. Default: leave them in place and report the paths — users often want a second pass with different settings, and re-running Demucs in particular is slow enough that the disk cost is usually worth it.

"Obviously ephemeral" means a temp directory the same session created and the user didn't name — e.g., `$env:TEMP\transcribe-<timestamp>` on Windows, `/tmp/transcribe-<timestamp>` on Linux/macOS. Anything inside the user's project tree, Downloads folder, or a named output directory is *not* ephemeral; confirm before removing.

## Verification

Quick checks before declaring the result done:

### Audible playback with subs

```powershell
mpv "audio.mp3" --sub-file=out.srt
```

Drift is obvious by ear, much faster than reading timestamps.

### Aegisub scrub for ASS

Scrubbing the timeline reveals karaoke fill problems visually — the fill moves too slow or too fast against the audio.

### Programmatic sanity checks

```python
# Tune these per content type:
#   max_word_dur: speech ~2–3 s is suspicious; sung held notes can hit 8–15 s.
#   overlap_tol_s: 10 ms accommodates floating-point round-trips in JSON output.
#     Genuine overlap above that usually means alignment confusion or a bug
#     in chunked stitching; small coarticulated overlap in fast speech is normal.
MAX_WORD_DUR_S = 8.0      # raise to 15 for sustained vocals/operatic content
OVERLAP_TOL_S = 0.01

for seg in result["segments"]:
    ws = seg["words"]
    for a, b in zip(ws, ws[1:]):
        assert a["end"] <= b["start"] + OVERLAP_TOL_S, "word overlap"
    for w in ws:
        assert w["end"] - w["start"] < MAX_WORD_DUR_S, "implausible word duration"
```

### Confidence triage

Flag words with `prob < 0.5` for manual review. These are the ones most likely wrong, and reviewing only those is much cheaper than re-listening to the whole track.

### Coverage

Total span of word timings should roughly match audio duration; a large gap suggests a dropped section worth re-running.

### Constant offset check

If timestamps are off by a constant offset across the whole file, that's almost always a sample-rate or encoder-delay quirk in the input. Re-encode to 16 kHz mono WAV and re-run instead of shifting the output — shifting hides the root cause and re-bites on the next file from the same source.
