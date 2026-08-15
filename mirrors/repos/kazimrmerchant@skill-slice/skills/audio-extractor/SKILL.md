---
name: audio-extractor
version: 1.1.1
description: "Pulls a video soundtrack into mono 16 kHz 16-bit PCM WAV through the bundled FFmpeg wrapper. Trigger on extract-audio, ASR/VAD prep, or normalizing mixed containers to analysis WAV. Not for stereo music mastering, archival hi-fi, or keeping the picture track."
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-16
---

## Overview

Extracts the audio track from a video file and writes it as a **mono, 16 kHz, 16-bit PCM WAV** (`pcm_s16le`). This format is the lingua franca of speech and energy-analysis pipelines (ASR, VAD, RMS/energy features), which expect a single channel, a known sample rate, and uncompressed samples. Producing that format up front means downstream tools consume the output without re-decoding or re-sampling.

**Why these defaults:**

- **Mono (1 channel)** — Speech and energy analysis treat audio as a single signal. Stereo doubles data with no ASR/VAD benefit and forces every consumer to decide how to combine channels.
- **16 kHz sample rate** — Human speech energy lives almost entirely below 8 kHz. By Nyquist, 16 kHz captures everything up to 8 kHz, which is the band ASR/VAD models are trained on. Higher rates waste storage and compute on frequencies those models ignore.
- **PCM s16le** — Uncompressed and lossless; introduces no codec artifacts that would corrupt energy or spectral features. De-facto WAV standard readable by `librosa`, `soundfile`, `scipy.io.wavfile`, and similar libraries.

## When to Use

- **Speech analysis (ASR, VAD).** Models like Whisper and wav2vec2 are trained on 16 kHz mono. Feeding them that exact format avoids internal resample steps and the subtle artifacts they introduce.
- **Energy calculation and signal processing.** RMS energy, spectral flux, and similar features are simplest and most reproducible on a single channel at a fixed sample rate.
- **Standardizing heterogeneous inputs.** Videos arrive in many containers/codecs (AAC, Opus, MP3, AC-3). Converting them all to one PCM WAV format removes codec-specific quirks before later processing stages.

**When NOT to use:**

- **You need the picture, not the sound.** This skill discards the video stream entirely. Use a frame-extraction tool instead.
- **You need to preserve fidelity (music, mastering, archival).** The conversion downmixes to mono and caps bandwidth at 8 kHz (Nyquist for 16 kHz). That is ideal for speech but destructive for stereo imaging and high-frequency musical content. Keep the original stereo at its native sample rate for hi-fi work.
- **The source is untrusted and unsandboxed.** FFmpeg's demuxers/decoders have a history of memory-safety bugs exploitable by deliberately malformed media files (heap overflows, OOB reads). Treat unknown-origin video as hostile input: run in a sandbox/container, apply resource limits, keep FFmpeg patched. Validate provenance before processing.
- **You are on a legacy FFmpeg.** Versions before FFmpeg 6.0 lack security fixes for the vulnerability class above. FFmpeg 6.0+ is what makes the "safe" risk rating defensible.

## Prerequisites

- **FFmpeg 6.0+** — The engine that demuxes the video and encodes the WAV. The 6.0 floor is a **security floor**, not just a feature one.
- **Python 3.10+** — Required because the implementation uses PEP 604 union syntax (`int | None`) and modern `from __future__ import annotations` behavior.

**Windows (PowerShell) — verify prerequisites:**

```powershell
ffmpeg -version    # Must report 6.0 or higher
python --version   # Must report 3.10 or higher
```

If FFmpeg is missing, install it via `winget install Gyan.FFmpeg` or download from https://ffmpeg.org and add to `PATH`.

## Procedure

### 1. Locate the extraction script

The script lives at:

- **Windows:** `~\.cursor\skills\audio-extractor\scripts\extract_audio.py`
- **Linux/macOS:** `~/.cursor/skills/audio-extractor/scripts/extract_audio.py`

### 2. Run the extraction

**Windows (PowerShell):**

```powershell
python ~\.cursor\skills\audio-extractor\scripts\extract_audio.py `
    --video C:\path\to\video.mp4 `
    --output C:\path\to\audio.wav
```

**Linux/macOS:**

```bash
python3 ~/.cursor/skills/audio-extractor/scripts/extract_audio.py \
    --video /path/to/video.mp4 \
    --output /path/to/audio.wav
```

### 3. Parameters

| Parameter | Required | Default | Validation |
| --- | --- | --- | --- |
| `--video` | Yes | — | Path to input video. Accepts any container FFmpeg can demux (`.mp4`, `.mkv`, `.mov`, `.avi`, `.webm`, `.flv`, `.m4v`, `.mpeg`, `.ts`, `.wmv`, etc.). Must exist and be a regular file — checked before FFmpeg runs. |
| `--output` | Yes | — | Destination WAV path. Must end in `.wav`. Parent directory must already exist. |
| `--sample-rate` | No | `16000` | Output sample rate in Hz. Must be between 8000 and 192000 (inclusive). Rejects typos like `1600` early. |
| `--duration` | No | full track | Optional cap in seconds on how much audio to extract. Must be positive when supplied. |

### 4. Output format

- **Container/encoding:** WAV, PCM 16-bit signed little-endian (`pcm_s16le`)
- **Channels:** Mono (1)
- **Sample rate:** 16000 Hz by default (overridable via `--sample-rate`)
- **Intended consumers:** Speech-to-text and energy-analysis pipelines expecting single-channel, fixed-rate, uncompressed input

### 5. Load reference files (when needed)

- **`scripts/extract_audio.py`** — The main extraction script. Always use this; do not call `ffmpeg` directly. The script validates inputs, wraps FFmpeg errors into actionable messages, and verifies output was produced.
- **`references/`** — If the skill directory contains a `references/` folder, load any files there for extended documentation on supported codecs, troubleshooting matrices, or downstream pipeline integration notes. Check for this directory when you encounter unusual container formats or need integration guidance.

## Examples

```powershell
# Extract the full audio track at default 16 kHz mono PCM format.
python ~\.cursor\skills\audio-extractor\scripts\extract_audio.py `
    --video C:\videos\meeting.mp4 `
    --output C:\audio\meeting.wav

# Extract only the first 10 minutes (600 seconds) of a long lecture.
python ~\.cursor\skills\audio-extractor\scripts\extract_audio.py `
    --video C:\videos\lecture.mp4 `
    --duration 600 `
    --output C:\audio\lecture_first10min.wav

# Extract at a higher sample rate (44.1 kHz) when a downstream tool requires it.
# Note: this still produces mono PCM, so it is wider-band speech, not hi-fi stereo.
python ~\.cursor\skills\audio-extractor\scripts\extract_audio.py `
    --video C:\videos\interview.mkv `
    --sample-rate 44100 `
    --output C:\audio\interview_44k.wav
```

## Pitfalls

- **`FFmpeg was not found on PATH`** — FFmpeg is not installed or not on `PATH`. Install FFmpeg 6.0+ and confirm with `ffmpeg -version`.
- **`Input video does not exist` / `is not a regular file`** — The `--video` path is wrong or points at a directory. Re-check the path; this is caught before FFmpeg runs.
- **`Output path must end in .wav`** — The `--output` value has the wrong (or no) extension. The skill only emits WAV and enforces the extension.
- **`Output directory does not exist`** — Create the parent directory first (`mkdir` / `New-Item -ItemType Directory`), then re-run.
- **`sample_rate must be between 8000 and 192000 Hz`** — Usually a typo (e.g. `1600` instead of `16000`). Supply a value in range.
- **`FFmpeg failed (exit code N)`** — The printed stderr tail tells you why. Common causes: a video with no audio stream, or a corrupt/truncated file. If the source is untrusted, treat a crash here as a reason to sandbox the input rather than retry.
- **`FFmpeg reported success but produced no usable output`** — FFmpeg exited 0 but the output file is missing or zero bytes. This can happen with certain edge-case containers; inspect the stderr output for warnings.
- **Security: untrusted media files** — FFmpeg demuxers/decoders have a history of memory-safety bugs exploitable by malformed media. Always sandbox untrusted input. Keep FFmpeg patched at 6.0+. Do not disable validation checks to "force" extraction.
- **Do not call `ffmpeg` directly** — The script wraps FFmpeg with input validation, error handling, and output verification. Bypassing it loses these safeguards.

## Verification

After extraction, verify the output:

```powershell
# 1. Confirm the file exists and is non-empty.
Get-Item C:\path\to\audio.wav | Select-Object Name, Length

# 2. Confirm container/encoding is WAV PCM s16le.
ffprobe -i C:\path\to\audio.wav

# 3. Confirm mono (1 channel) and 16000 Hz (or your overridden rate).
ffprobe -show_entries stream=channels,sample_rate,codec_name -of default=noprint_wrappers=1 C:\path\to\audio.wav

# 4. If --duration N was used, confirm the clip is approximately N seconds.
ffprobe -show_entries format=duration -of default=noprint_wrappers=1 C:\path\to\audio.wav
```

**Expected output for step 3 (default settings):**

```
codec_name=pcm_s16le
channels=1
sample_rate=16000
```

**Checklist:**

- [ ] Output file exists, is non-empty, and is playable.
- [ ] Container/encoding is WAV PCM `pcm_s16le` (via `ffprobe`).
- [ ] Audio is mono (1 channel) at 16000 Hz, unless `--sample-rate` was overridden.
- [ ] Extracted audio content matches the source video's audio (spot-listen).
- [ ] Extraction succeeds across several FFmpeg-supported containers (`.mp4`, `.mkv`, `.webm`).
- [ ] Invalid inputs fail loudly and early: missing `--video`, non-`.wav` `--output`, out-of-range `--sample-rate` each produce a clear error and non-zero exit code.
- [ ] `--duration N` produces a clip of approximately `N` seconds.

## Related Skills

- **`audio-analyzer`** — Computes energy and spectral features from the WAV this skill produces. The mono/16 kHz/PCM output is exactly the input it expects.
- **`speech-to-text`** — Transcribes the extracted audio. It assumes 16 kHz mono, so running this skill first removes a resample step on its side.
