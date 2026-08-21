---
name: voice-activity-detection
description: "Returns (start_sec, end_sec) speech spans with Silero, SpeechBrain, or WebRTC VAD, then merge-and-pad postprocess. Use when gating diarization, ASR chunking, or push-to-talk so silence never reaches the next model. Do not use as a leading-silence energy trimmer (silence-detector) or as speaker-ID clustering (speaker-clustering)."
version: 1.2.1
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-16
---

# Voice Activity Detection (VAD)

## Overview

Voice Activity Detection (VAD) identifies which parts of an audio signal contain speech versus silence or background noise. It is almost always the *first* stage in a speech pipeline. Every downstream model — speaker diarization, ASR, audio compression — is expensive to run and easy to confuse. Feeding raw audio wastes compute on silence and causes models to "explain" noise (slammed doors, HVAC hum) as content. Gating on speech first cuts input volume, raises signal-to-noise ratio, and eliminates a class of failure modes (e.g. a clusterer inventing a phantom "speaker" from background hum).

The output of any VAD is the same shape regardless of backend: a `list[tuple[float, float]]` of `(start_sec, end_sec)` speech segments. Every example in this skill standardizes on that contract so backends can be swapped without rewriting downstream pipeline code.

## When to Use

- **Before speaker diarization** — so the embedding model only sees speech. Encoding silence produces a vector the clusterer mistakes for a real speaker; this is the single most common diarization accuracy bug.
- **To cut compute on long recordings** — silence and noise are dead weight for ASR and enhancement models; removing them is a direct latency and cost win.
- **To chunk long audio for ASR** — most ASR models degrade or hit memory limits on very long inputs; speech-bounded chunks keep each request tractable.
- **For push-to-talk / wake-word triggers** — a lightweight VAD decides when to open the mic stream, avoiding a constant, expensive ASR connection.

### Do Not Use

- **When the whole signal is known to be speech** (e.g. a clean studio narration track) — VAD adds latency and risks clipping soft onsets for no benefit.
- **When you need precise timing of non-speech events** (music onsets, sirens, environmental sounds) — VAD is tuned to suppress exactly those; use a general audio event detector instead.
- **In extreme low-SNR conditions** — when noise rivals speech energy, VAD floods false positives or drops speech entirely. Run a dedicated noise-suppression / speech-enhancement model *first*, then VAD on the cleaned signal.

## Prerequisites

### Python Environment

```powershell
# Core packages (install in your venv/conda env)
pip install torch torchaudio
pip install speechbrain
pip install webrtcvad
pip install numpy scikit-learn

# Optional: ONNX runtime for Silero offline/production use
pip install onnxruntime
```

### Windows (PowerShell) Notes

- `torch.hub` caches models under `%USERPROFILE%\.cache\torch\hub\`. If the first `torch.hub.load` call fails due to network issues, pre-download the model and place it there, or use `use_onnx=True` with a local ONNX file.
- SpeechBrain caches under `savedir` (default `/tmp/speechbrain_vad` on Linux). On Windows, override this to a local path, e.g. `~\.cache\speechbrain_vad`.
- `webrtcvad` requires a C compiler on install. On Windows, install [Visual C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) first if `pip install webrtcvad` fails.

### Audio Format Requirements

| Backend | Accepted Format | Sample Rates |
|---------|----------------|--------------|
| Silero VAD | WAV (any), resampled internally | 8000, 16000 Hz ONLY |
| SpeechBrain VAD | WAV (any), resampled internally | 16000 Hz (internal) |
| WebRTC VAD | Mono 16-bit PCM WAV | 8000, 16000, 32000, 48000 Hz |

## Procedure

### Step 1: Choose the Right VAD Backend

| Tool | Best For | Pros | Cons |
|------|----------|------|------|
| **Silero VAD** | High precision / real-time / short bursts | Best accuracy, very low false alarms | Needs PyTorch or ONNX runtime; 8 k/16 k only |
| **SpeechBrain** | General purpose / long-form / research | Robust on varied acoustics, composes with toolkit | Heavier memory and load time |
| **WebRTC VAD** | Embedded / edge / lowest latency | Tiny footprint, no DL deps, microsecond frames | Lower accuracy, rigid PCM/frame contract |

**Decision rule:** Can you afford a PyTorch dependency? If yes and you want best accuracy, use Silero (or SpeechBrain for long-form). If no — embedded device, hard real-time, or strict dependency budget — use WebRTC and lean on `postprocess_boundaries` to clean up its noisier output.

### Step 2: Run VAD Detection

#### Option A: Silero VAD (Recommended for High Accuracy & Short Segments)

Silero is the de-facto standard for lightweight, high-performance VAD. It is trained *only* on 8 kHz and 16 kHz audio — any other rate silently destroys accuracy, so the wrapper rejects it up front.

```python
from __future__ import annotations
from pathlib import Path
import torch

SAMPLING_RATE: int = 16000  # Silero was trained on 8 kHz / 16 kHz only.
Segment = tuple[float, float]


def detect_speech_silero(
    audio_path: str | Path,
    *,
    threshold: float = 0.5,
    min_speech_duration_ms: int = 250,
    min_silence_duration_ms: int = 100,
    sampling_rate: int = SAMPLING_RATE,
    use_onnx: bool = False,
) -> list[Segment]:
    """Return speech segments as (start_sec, end_sec) tuples."""
    # --- validate at the boundary so failures are loud and specific ---
    if not 0.0 <= threshold <= 1.0:
        raise ValueError(f"threshold must be in [0.0, 1.0], got {threshold!r}")
    if sampling_rate not in (8000, 16000):
        raise ValueError(
            f"Silero VAD supports only 8000 or 16000 Hz, got {sampling_rate!r}"
        )
    if min_speech_duration_ms < 0 or min_silence_duration_ms < 0:
        raise ValueError("duration thresholds must be non-negative")

    audio_path = Path(audio_path)
    if not audio_path.is_file():
        raise FileNotFoundError(f"audio file not found: {audio_path}")

    # --- load model (torch.hub caches it after the first call) ---
    try:
        model, utils = torch.hub.load(
            repo_or_dir="snakers4/silero-vad",
            model="silero_vad",
            force_reload=False,
            onnx=use_onnx,
        )
    except Exception as exc:
        raise RuntimeError(
            "failed to load Silero VAD from torch.hub; pre-download the model or "
            "point use_onnx at a local ONNX runtime for offline/production use"
        ) from exc

    get_speech_timestamps, save_audio, read_audio, VADIterator, collect_chunks = utils

    waveform: torch.Tensor = read_audio(str(audio_path), sampling_rate=sampling_rate)

    raw_timestamps = get_speech_timestamps(
        waveform,
        model,
        threshold=threshold,
        min_speech_duration_ms=min_speech_duration_ms,
        min_silence_duration_ms=min_silence_duration_ms,
        sampling_rate=sampling_rate,
    )

    return [
        (ts["start"] / sampling_rate, ts["end"] / sampling_rate)
        for ts in raw_timestamps
    ]
```

#### Option B: SpeechBrain VAD (General Purpose / Long-Form)

The CRDNN model carries more acoustic context, so it over-fragments less on long-form audio where Silero's short window can chop a single utterance into many pieces.

```python
from __future__ import annotations
from pathlib import Path
import torch
from speechbrain.inference.VAD import VAD

Segment = tuple[float, float]


def detect_speech_speechbrain(
    audio_path: str | Path,
    *,
    savedir: str | Path = "C:\\Users\\YourUser\\.cache\\speechbrain_vad",
) -> list[Segment]:
    """Return speech segments using SpeechBrain's pre-trained CRDNN VAD."""
    audio_path = Path(audio_path)
    if not audio_path.is_file():
        raise FileNotFoundError(f"audio file not found: {audio_path}")

    try:
        vad_model = VAD.from_hparams(
            source="speechbrain/vad-crdnn-libriparty",
            savedir=str(savedir),
        )
    except Exception as exc:
        raise RuntimeError(
            "failed to load SpeechBrain VAD; verify network access and that the "
            "'speechbrain' package is installed"
        ) from exc

    boundaries_tensor: torch.Tensor = vad_model.get_speech_segments(str(audio_path))

    return [(float(start), float(end)) for start, end in boundaries_tensor.tolist()]
```

#### Option C: WebRTC VAD (Ultra-Lightweight / Embedded)

WebRTC operates on raw 16-bit PCM mono at fixed frame sizes only. Hand it stereo, float, or an odd frame length and it does not error — it returns garbage decisions. The wrapper fails loudly on any contract violation.

```python
from __future__ import annotations
import contextlib
import wave
import webrtcvad

Segment = tuple[float, float]

_SUPPORTED_RATES: frozenset[int] = frozenset({8000, 16000, 32000, 48000})
_SUPPORTED_FRAME_MS: frozenset[int] = frozenset({10, 20, 30})


def _read_wave_mono_pcm16(path: str) -> tuple[bytes, int]:
    """Read a mono 16-bit PCM WAV and return (raw_pcm_bytes, sample_rate)."""
    with contextlib.closing(wave.open(path, "rb")) as wav:
        num_channels = wav.getnchannels()
        sample_width = wav.getsampwidth()
        sample_rate = wav.getframerate()

        if num_channels != 1:
            raise ValueError(f"expected mono audio, got {num_channels} channels")
        if sample_width != 2:
            raise ValueError(
                f"expected 16-bit PCM (2-byte samples), got {sample_width}-byte samples"
            )
        if sample_rate not in _SUPPORTED_RATES:
            raise ValueError(
                f"sample_rate {sample_rate} unsupported; "
                f"use one of {sorted(_SUPPORTED_RATES)}"
            )

        pcm_data = wav.readframes(wav.getnframes())
        return pcm_data, sample_rate


def detect_speech_webrtc(
    audio_path: str,
    *,
    aggressiveness: int = 3,
    frame_ms: int = 30,
) -> list[Segment]:
    """Return speech segments using the lightweight WebRTC VAD."""
    if aggressiveness not in (0, 1, 2, 3):
        raise ValueError(
            f"aggressiveness must be 0..3 (0=lenient, 3=strict), got {aggressiveness}"
        )
    if frame_ms not in _SUPPORTED_FRAME_MS:
        raise ValueError(
            f"frame_ms must be one of {sorted(_SUPPORTED_FRAME_MS)}, got {frame_ms}"
        )

    pcm_data, sample_rate = _read_wave_mono_pcm16(audio_path)
    vad = webrtcvad.Vad(aggressiveness)

    samples_per_frame = int(sample_rate * frame_ms / 1000)
    bytes_per_frame = samples_per_frame * 2
    frame_duration_s = frame_ms / 1000.0

    segments: list[Segment] = []
    segment_start: float | None = None

    num_frames = len(pcm_data) // bytes_per_frame
    for i in range(num_frames):
        offset = i * bytes_per_frame
        frame = pcm_data[offset : offset + bytes_per_frame]
        timestamp = i * frame_duration_s

        is_speech = vad.is_speech(frame, sample_rate)

        if is_speech and segment_start is None:
            segment_start = timestamp
        elif not is_speech and segment_start is not None:
            segments.append((segment_start, timestamp))
            segment_start = None

    if segment_start is not None:
        segments.append((segment_start, num_frames * frame_duration_s))

    return segments
```

### Step 3: Postprocess VAD Boundaries (Effectively Mandatory)

Raw VAD output is never clean enough to use directly. Every VAD fragments speech: a single sentence comes back as several segments split on micro-pauses, interleaved with stray sub-100 ms blips from transient noise. Passing that into diarization inflates speaker count; into ASR, clips word boundaries.

```python
from __future__ import annotations

Segment = tuple[float, float]


def postprocess_boundaries(
    boundaries: list[Segment],
    *,
    min_duration_s: float = 0.30,
    merge_gap_s: float = 0.50,
    pad_s: float = 0.0,
    total_duration_s: float | None = None,
) -> list[Segment]:
    """Clean raw VAD output into cohesive speech segments.

    Args:
        boundaries: raw (start_sec, end_sec) segments from any VAD backend.
        min_duration_s: drop segments shorter than this (noise spikes).
        merge_gap_s: merge two segments separated by a gap no larger than this.
        pad_s: symmetric padding added to each side to recover trimmed onsets.
        total_duration_s: if given, padded ends are clamped to clip length.
    """
    if min_duration_s < 0 or merge_gap_s < 0 or pad_s < 0:
        raise ValueError("min_duration_s, merge_gap_s and pad_s must be non-negative")
    if total_duration_s is not None and total_duration_s < 0:
        raise ValueError("total_duration_s must be non-negative when provided")
    if not boundaries:
        return []

    cleaned: list[Segment] = []
    for segment in boundaries:
        start, end = segment
        if end < start:
            raise ValueError(f"segment end precedes start: {segment!r}")
        cleaned.append((float(start), float(end)))
    cleaned.sort(key=lambda s: s[0])

    # 1. Remove segments shorter than min_duration_s (noise spikes).
    cleaned = [s for s in cleaned if (s[1] - s[0]) >= min_duration_s]
    if not cleaned:
        return []

    # 2. Merge segments separated by <= merge_gap_s (bridge natural pauses).
    merged: list[list[float]] = [list(cleaned[0])]
    for start, end in cleaned[1:]:
        prev_start, prev_end = merged[-1]
        if start - prev_end <= merge_gap_s:
            merged[-1][1] = max(prev_end, end)
        else:
            merged.append([start, end])

    # 3. Optional symmetric padding, clamped to [0, total_duration_s].
    result: list[Segment] = []
    for start, end in merged:
        padded_start = max(0.0, start - pad_s)
        padded_end = end + pad_s
        if total_duration_s is not None:
            padded_end = min(total_duration_s, padded_end)
        result.append((padded_start, padded_end))

    return result
```

### Step 4: Integrate with Downstream Pipeline (Speaker Diarization Example)

This is the canonical reason VAD exists in a diarization pipeline. Gate the audio on speech, embed each segment, then cluster the embeddings.

```python
from __future__ import annotations
import torch

Segment = tuple[float, float]


def embed_speech_segments(
    waveform: torch.Tensor,
    sample_rate: int,
    boundaries: list[Segment],
    speaker_model: torch.nn.Module,
    *,
    min_samples: int = 400,  # ~25 ms at 16 kHz; embedders unreliable below this
) -> list[torch.Tensor]:
    """Extract one speaker embedding per speech segment."""
    if waveform.dim() != 2:
        raise ValueError(
            f"expected waveform shape [channels, samples], got {tuple(waveform.shape)}"
        )
    if sample_rate <= 0:
        raise ValueError(f"sample_rate must be positive, got {sample_rate}")
    if min_samples <= 0:
        raise ValueError(f"min_samples must be positive, got {min_samples}")

    total_samples = waveform.shape[1]
    embeddings: list[torch.Tensor] = []

    for start_s, end_s in boundaries:
        start_sample = max(0, int(start_s * sample_rate))
        end_sample = min(total_samples, int(end_s * sample_rate))

        if end_sample - start_sample < min_samples:
            continue  # too short to embed reliably; skip

        segment_audio = waveform[:, start_sample:end_sample]

        with torch.no_grad():
            embedding = speaker_model.encode_batch(segment_audio)

        embeddings.append(embedding)

    return embeddings


def cluster_speaker_embeddings(
    embeddings: list[torch.Tensor],
    *,
    distance_threshold: float = 0.7,
) -> list[int]:
    """Assign a speaker label to each embedding via agglomerative clustering."""
    if distance_threshold <= 0:
        raise ValueError(
            f"distance_threshold must be positive, got {distance_threshold}"
        )
    if not embeddings:
        return []
    if len(embeddings) == 1:
        return [0]

    import numpy as np
    from sklearn.cluster import AgglomerativeClustering

    matrix: np.ndarray = (
        torch.cat(embeddings).reshape(len(embeddings), -1).cpu().numpy()
    )

    clusterer = AgglomerativeClustering(
        n_clusters=None,
        distance_threshold=distance_threshold,
        metric="cosine",
        linkage="average",
    )
    labels = clusterer.fit_predict(matrix)
    return [int(label) for label in labels]


# End-to-end usage:
#
#   segments = postprocess_boundaries(
#       detect_speech_silero("meeting.wav"),
#       min_duration_s=0.30,
#       merge_gap_s=0.50,
#       pad_s=0.10,
#   )
#   embeddings = embed_speech_segments(waveform, 16000, segments, speaker_model)
#   speaker_labels = cluster_speaker_embeddings(embeddings, distance_threshold=0.7)
#   # speaker_labels[i] is the speaker for segments[i].
```

## Pitfalls

1. **Feeding non-16 kHz / 8 kHz audio to Silero.** Silero was trained *only* on 8 kHz and 16 kHz. Any other sample rate silently destroys accuracy without raising. The wrapper rejects this up front — never bypass the validation.

2. **Passing stereo or float audio to WebRTC VAD.** `webrtcvad` reads raw little-endian 16-bit PCM mono. Passing stereo or float audio produces silently-wrong speech decisions rather than an exception. The wrapper validates the WAV header and rejects anything else — never bypass `_read_wave_mono_pcm16`.

3. **Skipping postprocessing.** Raw VAD output fragments speech: a single sentence returns as multiple segments split on micro-pauses, interleaved with sub-100 ms noise blips. Passing raw output into diarization inflates speaker count; into ASR, clips word boundaries. `postprocess_boundaries` is effectively mandatory.

4. **Too many false alarms (noise detected as speech).** Raise `threshold` (Silero) or `aggressiveness` (WebRTC). Both raise the bar a frame must clear. Cost: genuine quiet speech may be missed — move in small steps.

5. **Missing short segments (speech clipped).** Lower `threshold` or `min_speech_duration_ms`. The threshold change lets lower-confidence (quieter) frames pass; the duration change stops the VAD from discarding brief but real utterances like "yes" or "mm-hm."

6. **Over-segmentation (one sentence split into many).** Increase `merge_gap_s` in `postprocess_boundaries`. A larger tolerated gap bridges natural mid-sentence pauses.

7. **Clipping at start or end of words.** Set `pad_s` (e.g. `0.1`) in `postprocess_boundaries`. VAD reacts to energy, and soft onsets sit below the trigger. Use `total_duration_s` to keep padded ends from overrunning the clip.

8. **Using VAD in extreme low-SNR conditions.** When noise rivals speech energy, VAD floods false positives or drops speech entirely. Run a dedicated noise-suppression / speech-enhancement model *first*, then VAD on the cleaned signal.

9. **torch.hub failures in CI / offline environments.** Network failures are common. Pre-download the Silero model to `%USERPROFILE%\.cache\torch\hub\` or use `use_onnx=True` with a local ONNX runtime for production.

10. **Embedding silence as a phantom speaker.** A speaker-embedding model will happily encode silence or background noise into a vector, and the clusterer treats that vector as a phantom speaker. Always gate embeddings on VAD speech regions only.

## Verification

1. **Functional test (Silero).** Call `detect_speech_silero` on a known speech file and confirm it returns a non-empty `list[tuple[float, float]]` where every `end > start`:

```python
segments = detect_speech_silero("test_speech.wav", sampling_rate=16000)
assert len(segments) > 0, "expected at least one speech segment"
assert all(end > start for start, end in segments), "end must exceed start"
print(f"OK: {len(segments)} segments detected")
```

2. **Validation test.** Pass an out-of-range `threshold` and a non-existent path; confirm you get `ValueError` and `FileNotFoundError`:

```python
try:
    detect_speech_silero("test.wav", threshold=1.5)
    assert False, "should have raised ValueError"
except ValueError:
    print("OK: threshold validation works")

try:
    detect_speech_silero("nonexistent.wav")
    assert False, "should have raised FileNotFoundError"
except FileNotFoundError:
    print("OK: file-not-found validation works")
```

3. **Logic test (postprocessing).** Feed `postprocess_boundaries` a sub-`min_duration_s` blip and two segments separated by less than `merge_gap_s`; confirm the blip is dropped and the two are merged:

```python
raw = [(1.0, 1.1), (2.0, 3.0), (3.3, 4.0)]  # blip + two close segments
result = postprocess_boundaries(raw, min_duration_s=0.30, merge_gap_s=0.50)
assert len(result) == 1, f"expected 1 merged segment, got {len(result)}"
assert result[0] == (2.0, 4.0), f"expected (2.0, 4.0), got {result[0]}"
print(f"OK: postprocessing merged correctly -> {result}")
```

4. **Contract test (WebRTC).** Confirm `detect_speech_webrtc` raises on a stereo or non-16-bit WAV and on an unsupported `frame_ms`:

```python
try:
    detect_speech_webrtc("stereo.wav")
    assert False, "should have raised on stereo"
except ValueError as e:
    print(f"OK: stereo rejected -> {e}")

try:
    detect_speech_webrtc("mono_16bit.wav", frame_ms=15)
    assert False, "should have raised on bad frame_ms"
except ValueError as e:
    print(f"OK: bad frame_ms rejected -> {e}")
```

5. **Accuracy check.** Compare VAD output against a manually labeled file and tune `threshold` / `aggressiveness` to the actual noise floor of your environment — the defaults are a starting point, not a universal setting.

## Related Skills

- Speaker Diarization
- Audio Segmentation
- Noise Reduction / Speech Enhancement
- Automatic Speech Recognition (ASR)
