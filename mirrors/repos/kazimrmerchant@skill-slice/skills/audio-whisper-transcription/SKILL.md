---
name: audio-whisper-transcription
version: 1.2.2
description: "Transcribes audio or video to text with word-level timestamps via faster-whisper (default large-v3-turbo) or local openai-whisper (word_timestamps=True). Use when the user needs captions, filler-word cut lists, or searchable transcripts with start/end times. Not for speaker diarization (pyannote/WhisperX), denoising, or hosts that ban ffmpeg. Never invent package versions such as Whisper 2024.5."
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-14
last_updated: 2026-07-14
---

# Whisper Transcription

Local speech-to-text with word-level timestamps for captions, filler-word detection, and edit lists.

**Reviewed 2026-07-14:** fixed incorrect `word_level_timestamps` flag (local `openai-whisper` uses `word_timestamps=True`), added `large-v3` / `turbo`, and documented **faster-whisper** as the production default.

## When to Use

- Subtitles / captions with word-accurate sync
- Filler-word or keyword hit lists with timestamps
- Searchable transcripts of meetings, interviews, podcasts
- Downstream cut lists for `video-processing-pipeline` / `ffmpeg-video-editing`

## Do Not Use

- Plain transcript with no timing → simpler ASR is enough
- Speaker diarization alone → pair with **pyannote.audio** / WhisperX (this skill is transcription only)
- Extremely noisy audio → denoise / loudnorm first (ffmpeg filters, or **not installed:** `ffmpeg-audio-processing`)
- Environments that ban `ffmpeg` → Whisper needs demux for video containers
- Cloud-only OpenAI STT without local models → use the API path below, not the local snippets

## Prerequisites

### Install

```bash
# Production default (recommended)
pip install -U faster-whisper

# Official OpenAI local package (optional)
pip install -U openai-whisper

# System: ffmpeg 7.1+ or 8.x on PATH
ffmpeg -version
ffprobe -version
```

### Runtime defaults (2026)

| Path | When | Notes |
|------|------|-------|
| **faster-whisper** + `large-v3-turbo` | Default production (English / major EU langs) | CTranslate2; ~4–8× faster than stock `openai-whisper`; INT8/FP16 |
| **faster-whisper** + `large-v3` | Max accuracy / low-resource languages | Slightly slower than turbo |
| **openai-whisper** package | Simple scripts, debugging | Official package; flag is `word_timestamps=True` |
| **OpenAI API** `whisper-1` | Cloud only | Uses `timestamp_granularities=["word"]` + `response_format="verbose_json"` — different API |

Do **not** invent package versions like "Whisper 2024.5". Pin what `pip show openai-whisper` / `faster-whisper` report.

### Model selection

| Model | Params (approx) | Use |
|-------|-----------------|-----|
| `tiny` / `base` | small | Smoke tests only |
| `small` / `medium` | mid | CPU or low VRAM |
| **`large-v3-turbo`** (`turbo`) | ~809M | **Default English production** |
| `large-v3` | ~1.5B | Max accuracy / hard languages |
| `large-v2` | ~1.5B | Legacy only — prefer v3/turbo |

## Procedure

### Step 1 — (Optional) Extract clean audio from video container

Pre-extracting to 16 kHz mono WAV improves consistency and avoids repeated demux during long jobs.

```bash
ffmpeg -y -i input.mp4 -vn -acodec pcm_s16le -ar 16000 -ac 1 audio.wav
```

Validate paths; never pass unsanitized user strings into shell. Use absolute Windows paths (e.g. `~\...`), not hardcoded `/root/...`.

### Step 2 — Transcribe with faster-whisper (recommended production path)

```python
from __future__ import annotations

import json
from pathlib import Path

from faster_whisper import WhisperModel


def transcribe_with_timestamps(
    audio_path: str | Path,
    output_path: str | Path,
    model_size: str = "large-v3-turbo",
    device: str = "cuda",  # or "cpu"
    compute_type: str = "float16",  # "int8" for low VRAM / CPU
    language: str | None = "en",
) -> list[dict]:
    """Word-level timestamps via faster-whisper (CTranslate2)."""
    model = WhisperModel(model_size, device=device, compute_type=compute_type)
    segments, info = model.transcribe(
        str(audio_path),
        language=language,
        word_timestamps=True,
        vad_filter=True,
        beam_size=5,
    )

    words: list[dict] = []
    for seg in segments:
        if not seg.words:
            continue
        for w in seg.words:
            token = (w.word or "").strip()
            if not token:
                continue
            words.append(
                {
                    "word": token,
                    "start": float(w.start),
                    "end": float(w.end),
                }
            )

    Path(output_path).write_text(
        json.dumps(
            {
                "language": info.language,
                "duration": info.duration,
                "words": words,
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    return words
```

### Step 3 — Alternative: openai-whisper (local package)

Use for simple scripts or debugging. The correct flag is `word_timestamps=True` — **not** `word_level_timestamps`.

```python
from __future__ import annotations

import json
from pathlib import Path

import whisper


def transcribe_openai_whisper(
    audio_path: str | Path,
    output_path: str | Path,
    model_name: str = "turbo",  # large-v3-turbo alias in recent packages
    language: str = "en",
) -> list[dict]:
    """Local openai-whisper — flag is word_timestamps=True (not word_level_timestamps)."""
    model = whisper.load_model(model_name)
    result = model.transcribe(
        str(audio_path),
        word_timestamps=True,  # CORRECT local flag
        language=language,
        fp16=False,  # safer default on CPU; set True on CUDA if desired
    )

    words = [
        {
            "word": w["word"].strip(),
            "start": float(w["start"]),
            "end": float(w["end"]),
        }
        for seg in result.get("segments", [])
        for w in seg.get("words", [])
    ]
    Path(output_path).write_text(
        json.dumps(words, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return words
```

### Step 4 — Alternative: OpenAI cloud API (different surface)

The cloud API uses `timestamp_granularities=["word"]` + `response_format="verbose_json"`. Words live on `tr.words` — this is **not** the local `word_timestamps` flag.

```python
from openai import OpenAI

client = OpenAI()
with open("audio.mp3", "rb") as f:
    tr = client.audio.transcriptions.create(
        model="whisper-1",
        file=f,
        response_format="verbose_json",
        timestamp_granularities=["word"],
    )
# words live on tr.words — not the local word_timestamps flag
```

### Step 5 — Filler-word detection (downstream of transcription)

```python
# Always-safe auto-cut candidates (pure vocalized fillers)
FILLER_ALWAYS = {"um", "uh", "hum", "hmm", "mhm"}
# Context-dependent — review list only; do not auto-cut without human OK
FILLER_REVIEW = {
    "like", "so", "well", "yeah", "okay",
    "basically", "actually", "literally",
}


def detect_fillers(words: list[dict]) -> list[dict]:
    hits = []
    for item in words:
        clean = "".join(ch for ch in item["word"].lower() if ch.isalnum())
        if clean in FILLER_ALWAYS:
            hits.append({
                "word": clean,
                "timestamp": round(item["start"], 2),
                "tier": "always",
            })
        elif clean in FILLER_REVIEW:
            hits.append({
                "word": clean,
                "timestamp": round(item["start"], 2),
                "tier": "review",
            })
    return hits
```

## Pitfalls

- **Wrong flag name:** local `openai-whisper` uses `word_timestamps=True`, **not** `word_level_timestamps`. The cloud API uses `timestamp_granularities=["word"]` — a completely different surface.
- **Bogus version pinning:** do not invent versions like "Whisper 2024.5". Run `pip show openai-whisper` / `pip show faster-whisper` and pin what they report.
- **`large-v2` is legacy:** prefer `large-v3` or `large-v3-turbo` for all new work.
- **No `ffmpeg-audio-processing` skill installed:** use raw ffmpeg CLI for extract / normalize / mix.
- **No diarization:** this skill is transcription only. Pair with **pyannote.audio** / WhisperX for speaker labels.
- **Noisy audio:** denoise / loudnorm first (ffmpeg filters) before transcription.
- **Path safety:** never pass unsanitized user strings into shell. Use absolute Windows paths (`~`), not hardcoded `/root/...`.
- **CPU `fp16`:** set `fp16=False` on CPU to avoid errors; set `True` on CUDA for speed.
- **`ffmpeg` required:** Whisper needs demux for video containers; environments banning ffmpeg cannot use local Whisper.

## Verification

1. **Import check:**
   ```bash
   python -c "from faster_whisper import WhisperModel; print('ok')"
   ```
2. **Model download:** run `transcribe_with_timestamps` on a known 10–30s clip with `model_size="large-v3-turbo"` — download should succeed.
3. **Word list integrity:** confirm output JSON has non-empty `word` / `start` / `end` for every entry.
4. **Flag correctness:** verify `word_timestamps=True` is used; do **not** use `word_level_timestamps`.
5. **Extracted WAV probe:**
   ```bash
   ffprobe -v error -show_entries stream=sample_rate,channels -of default=noprint_wrappers=1 audio.wav
   ```
   Should report `sample_rate=16000` and `channels=1`.
6. **Path check:** confirm all media paths are absolute Windows paths (no hardcoded `/root/...`).

## Related Skills

- `ffmpeg-media-info` — probe duration/codec before long jobs
- `ffmpeg-audio-processing` — **not installed** here; use raw ffmpeg for extract / normalize / mix
- `video-processing-pipeline` — cut ranges produced from filler timestamps
- `ffmpeg-video-editing` — manual cut/concat
- `story-to-video` — captions stage in full productions

## Changelog

### 1.2.2 (2026-07-14)

- Restructured into production-grade agent-skill format with numbered steps and verification commands

### 1.2.1 (2026-07-14)

- Split filler lists: always-safe vs review-only; mark `ffmpeg-audio-processing` not installed

### 1.2.0 (2026-07-14)

- Fixed incorrect `word_level_timestamps` claim → local API is `word_timestamps=True`
- Default production path: **faster-whisper** + `large-v3-turbo`
- Added `large-v3` / turbo; demoted `large-v2` to legacy
- Removed bogus "Whisper 2024.5" package versioning
- Documented OpenAI cloud `timestamp_granularities` separately
- Windows-friendly paths; security notes retained
