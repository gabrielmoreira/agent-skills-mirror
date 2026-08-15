---
name: automatic-speech-recognition
description: "Transcribes speech with Whisper or faster-whisper and overlaps segments onto diarization turns for speaker-labeled text and SRT. Use when the user needs transcripts, captions, or post-diarization word alignment. Do not use for speaker diarization itself or for cloud STT APIs that ship audio off-box."
version: 1.1.1
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-16
---

## When to Use

ASR converts spoken audio into text. It is the step that turns a stream of
samples into something searchable, editable, and human-readable. Reach for it
when:

- **Diarization has already run.** Diarization tells you *who* spoke and *when*,
  but not *what* they said. ASR fills in the words so the two can be merged into
  a speaker-labeled transcript. Running ASR after diarization (rather than the
  reverse) means you can attribute each transcribed phrase to the correct
  speaker instead of producing one undifferentiated wall of text.
- **You need speaker-labeled transcripts.** Meeting notes, interview records,
  and call-center analytics all depend on knowing both the words and the
  speaker. ASR supplies the words half of that pairing.
- **You are generating subtitles or captions.** Subtitles require text *and*
  precise timestamps so each caption appears in sync with the audio. Whisper
  emits both, which is why it is the workhorse here.
- **You are feeding text into a downstream NLP stage.** Summarization,
  sentiment analysis, translation, and search indexing all operate on text, not
  waveforms. ASR is the bridge between the two.

## Prerequisites

- **Python 3.10+** with `openai-whisper` installed (`pip install openai-whisper`).
- **ffmpeg** on the system PATH (Whisper delegates audio decoding to ffmpeg).
- **PyTorch** (`torch`) installed — Whisper depends on it for model inference.
- **Optional: `faster-whisper`** (`pip install faster-whisper`) for the
  CTranslate2-based optimized path. Prefer this for batch jobs or CPU-only hosts.
- **Optional: CUDA GPU** for faster inference. Without one, Whisper falls back
  to CPU automatically when `device="auto"`.
- **Speaker diarization output** must already exist as a list of turns with
  start time, duration, and speaker label before alignment can run.

## Procedure

### 1. Choose a Whisper model size

| Model    | Size  | Speed   | Accuracy  | Best for |
|----------|-------|---------|-----------|----------|
| tiny     | 39M   | Fastest | Lowest    | Smoke-testing a pipeline only (not production) |
| base     | 74M   | Fast    | Low       | Throughput-bound jobs that tolerate errors |
| small    | 244M  | Medium  | Good      | **Recommended default** — best balance |
| medium   | 769M  | Slow    | Very good | When `small` misses too many words |
| large-v3 | 1550M | Slowest | **Best**  | **Maximum accuracy**, accuracy-critical work |

Use `small` as the default because it transcribes most clean speech accurately
while fitting comfortably in CPU memory. Step up to `large-v3` only when accuracy
genuinely dominates cost — legal records, medical dictation, or content where a
single wrong word is expensive — because it is roughly 6× larger and
correspondingly slower.

The `tiny` model is listed for completeness but its accuracy is low enough that
it is only useful for smoke-testing a pipeline. Treat it as a development
convenience, not a production choice.

### 2. Load the shared preamble

All code blocks below assume these imports, types, constants, and validators
are in scope. Load this preamble first before running any transcription or
alignment code:

```python
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Final, Literal, Sequence, TypedDict

import torch
import whisper

WhisperModelName = Literal["tiny", "base", "small", "medium", "large-v3"]

RECOMMENDED_MODELS: Final[frozenset[str]] = frozenset({"small", "large-v3"})
VALID_MODEL_NAMES: Final[tuple[WhisperModelName, ...]] = (
    "tiny",
    "base",
    "small",
    "medium",
    "large-v3",
)

MIN_SEGMENT_DURATION_S: Final[float] = 0.3
INAUDIBLE_MARKER: Final[str] = "[INAUDIBLE]"


class ASRError(RuntimeError):
    """Raised when audio cannot be loaded, a model cannot be built, or
    transcription fails. Carries a human-readable cause for logging."""


class WhisperSegment(TypedDict):
    start: float
    end: float
    text: str


class WhisperResult(TypedDict):
    text: str
    language: str
    segments: list[WhisperSegment]


def _resolve_audio_path(audio_path: str | Path) -> Path:
    path = Path(audio_path).expanduser()
    if not path.exists():
        raise FileNotFoundError(f"Audio file does not exist: {path}")
    if not path.is_file():
        raise FileNotFoundError(f"Audio path is not a file: {path}")
    return path


def _validate_model_name(model_name: str) -> WhisperModelName:
    if model_name not in VALID_MODEL_NAMES:
        raise ValueError(
            f"Unknown Whisper model {model_name!r}. "
            f"Expected one of: {', '.join(VALID_MODEL_NAMES)}."
        )
    return model_name  # type: ignore[return-value]


def _select_device(preferred: Literal["auto", "cpu", "cuda"] = "auto") -> Literal["cpu", "cuda"]:
    if preferred == "cpu":
        return "cpu"
    if preferred == "cuda":
        if not torch.cuda.is_available():
            raise ASRError("device='cuda' was requested but no CUDA GPU is available.")
        return "cuda"
    return "cuda" if torch.cuda.is_available() else "cpu"


def _validate_language_code(language: str) -> str:
    code = language.strip().lower()
    if not code:
        raise ValueError("language must be a non-empty code such as 'en'.")
    known = set(whisper.tokenizer.LANGUAGES) | set(whisper.tokenizer.TO_LANGUAGE_CODE)
    if code not in known:
        raise ValueError(
            f"Unknown language {language!r}. "
            f"Expected an ISO 639-1 code such as 'en', 'es', or 'fr'."
        )
    return code


def _coerce_segment(item: object) -> WhisperSegment:
    if not isinstance(item, dict):
        raise ASRError(f"Expected each segment to be a mapping, got {type(item).__name__}.")
    try:
        start = float(item["start"])
        end = float(item["end"])
        text = str(item["text"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ASRError(f"Malformed Whisper segment {item!r}: {exc}") from exc
    if end < start:
        raise ASRError(f"Segment end ({end}) precedes start ({start}).")
    return {"start": start, "end": end, "text": text}


def _coerce_result(raw: object) -> WhisperResult:
    if not isinstance(raw, dict):
        raise ASRError(f"Expected a transcription mapping, got {type(raw).__name__}.")
    raw_segments = raw.get("segments")
    if not isinstance(raw_segments, list):
        raise ASRError("Transcription result is missing a 'segments' list.")
    segments = [_coerce_segment(item) for item in raw_segments]
    return {
        "text": str(raw.get("text", "")),
        "language": str(raw.get("language", "")),
        "segments": segments,
    }


def transcribe_audio(
    audio_path: str | Path,
    *,
    model_name: WhisperModelName = "small",
    language: str | None = None,
    device: Literal["auto", "cpu", "cuda"] = "auto",
) -> WhisperResult:
    """Transcribe a single audio file with Whisper.

    Args:
        audio_path: Path to a readable audio file (wav, mp3, m4a, flac, or any
            other ffmpeg-decodable format).
        model_name: One of VALID_MODEL_NAMES. Defaults to the balanced 'small'.
        language: Optional ISO code (e.g. 'en'). When None, Whisper auto-detects.
        device: 'auto' (prefer GPU), or force 'cpu'/'cuda'.

    Returns:
        A validated WhisperResult with full text, detected language, and segments.

    Raises:
        FileNotFoundError: if the audio path does not point at a file.
        ValueError: if model_name or language is invalid.
        ASRError: if the model cannot be loaded or transcription fails.
    """
    resolved = _resolve_audio_path(audio_path)
    name = _validate_model_name(model_name)
    selected_device = _select_device(device)

    try:
        model = whisper.load_model(name, device=selected_device)
    except Exception as exc:
        raise ASRError(f"Failed to load Whisper model {name!r}: {exc}") from exc

    transcribe_kwargs: dict[str, str] = {}
    if language is not None:
        transcribe_kwargs["language"] = _validate_language_code(language)

    try:
        raw_result = model.transcribe(str(resolved), **transcribe_kwargs)
    except Exception as exc:
        raise ASRError(f"Transcription failed for {resolved}: {exc}") from exc

    return _coerce_result(raw_result)
```

### 3. Transcribe the audio

With the preamble in place, transcribing for maximum accuracy or for a balanced
default is a one-liner:

```python
# Maximum accuracy: slower, larger memory footprint, fewest word errors.
best = transcribe_audio("interview.wav", model_name="large-v3")

# Balanced default: good accuracy at a fraction of the cost.
balanced = transcribe_audio("interview.wav", model_name="small")

print(f"Detected language: {balanced['language']}")
print(f"Segment count: {len(balanced['segments'])}")
```

### 4. (Optional) Use faster-whisper for optimized performance

`faster-whisper` reimplements Whisper on top of CTranslate2. It produces
near-identical accuracy but runs several times faster and, with `int8`
quantization, uses far less memory. Prefer it for batch jobs or CPU-only hosts
where the reference implementation is too slow.

```python
from __future__ import annotations

from pathlib import Path
from typing import Literal, Protocol

from faster_whisper import WhisperModel

# Reuse the preamble's helpers and types: _resolve_audio_path, _validate_model_name,
# WhisperSegment, WhisperModelName, ASRError.


class _FWSegment(Protocol):
    start: float
    end: float
    text: str


def transcribe_with_faster_whisper(
    audio_path: str | Path,
    *,
    model_name: WhisperModelName = "small",
    device: Literal["cpu", "cuda"] = "cpu",
    compute_type: str = "int8",
    beam_size: int = 5,
) -> list[WhisperSegment]:
    """Transcribe with faster-whisper and return typed segments.

    int8 on CPU is the cheapest configuration; switch to device='cuda' with
    compute_type='float16' when a GPU is available for another large speedup.

    Raises:
        FileNotFoundError: if the audio path is not a file.
        ValueError: if model_name is unknown or beam_size < 1.
        ASRError: if the model cannot be built or transcription fails.
    """
    resolved = _resolve_audio_path(audio_path)
    _validate_model_name(model_name)
    if beam_size < 1:
        raise ValueError(f"beam_size must be >= 1, got {beam_size}.")

    try:
        model = WhisperModel(model_name, device=device, compute_type=compute_type)
    except Exception as exc:
        raise ASRError(f"Failed to build faster-whisper model {model_name!r}: {exc}") from exc

    try:
        raw_segments, info = model.transcribe(str(resolved), beam_size=beam_size)
        collected: list[WhisperSegment] = []
        segment: _FWSegment
        for segment in raw_segments:
            text = str(segment.text).strip()
            if not text:
                continue
            collected.append(
                {"start": float(segment.start), "end": float(segment.end), "text": text}
            )
    except Exception as exc:
        raise ASRError(f"faster-whisper transcription failed for {resolved}: {exc}") from exc

    print(
        f"Detected language {info.language!r} "
        f"(p={info.language_probability:.2f}) over {info.duration:.1f}s of audio"
    )
    for seg in collected:
        print(f"[{seg['start']:.2f}s -> {seg['end']:.2f}s] {seg['text']}")
    return collected
```

### 5. Align transcriptions with diarization segments

This is the step that makes the transcript *speaker-aware*. Whisper segments its
output by acoustic/linguistic boundaries, which almost never line up with the
turn boundaries diarization produced. Collect **every Whisper segment that
overlaps a turn's time window** and join their text. Overlap (not containment)
is the right test because a single spoken sentence frequently straddles the
boundary between two diarization turns.

```python
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

# Builds on the preamble: WhisperSegment, MIN_SEGMENT_DURATION_S, INAUDIBLE_MARKER.


@dataclass(frozen=True)
class DiarizationTurn:
    """One diarization turn. Frozen so a turn cannot be mutated after the
    validation in __post_init__ has run."""

    start: float
    duration: float
    speaker: str

    def __post_init__(self) -> None:
        if self.start < 0:
            raise ValueError(f"Turn start must be >= 0, got {self.start}.")
        if self.duration <= 0:
            raise ValueError(f"Turn duration must be > 0, got {self.duration}.")
        if not self.speaker.strip():
            raise ValueError("Turn speaker label must be a non-empty string.")

    @property
    def end(self) -> float:
        return self.start + self.duration


@dataclass(frozen=True)
class AlignedTranscript:
    """A turn paired with the transcribed words that fall inside it."""

    speaker: str
    start: float
    end: float
    text: str
    is_inaudible: bool


def align_transcription_with_turns(
    turns: Sequence[DiarizationTurn],
    segments: Sequence[WhisperSegment],
    *,
    min_duration_s: float = MIN_SEGMENT_DURATION_S,
    inaudible_marker: str = INAUDIBLE_MARKER,
) -> list[AlignedTranscript]:
    """Map Whisper segments onto diarization turns by temporal overlap.

    Args:
        turns: Diarization turns, each with a speaker label and time window.
        segments: Whisper segments to distribute across the turns.
        min_duration_s: Turns shorter than this are marked inaudible up front,
            because such fragments rarely transcribe reliably.
        inaudible_marker: Placeholder text used when no usable words overlap.

    Returns:
        One AlignedTranscript per input turn, in the same order.

    Raises:
        ValueError: if min_duration_s is negative.
    """
    if min_duration_s < 0:
        raise ValueError(f"min_duration_s must be non-negative, got {min_duration_s}.")

    aligned: list[AlignedTranscript] = []
    for turn in turns:
        if turn.duration < min_duration_s:
            aligned.append(
                AlignedTranscript(
                    speaker=turn.speaker,
                    start=turn.start,
                    end=turn.end,
                    text=inaudible_marker,
                    is_inaudible=True,
                )
            )
            continue

        overlapping_text = [
            seg["text"].strip()
            for seg in segments
            if seg["start"] < turn.end
            and seg["end"] > turn.start
            and seg["text"].strip()
        ]

        if overlapping_text:
            aligned.append(
                AlignedTranscript(
                    speaker=turn.speaker,
                    start=turn.start,
                    end=turn.end,
                    text=" ".join(overlapping_text),
                    is_inaudible=False,
                )
            )
        else:
            aligned.append(
                AlignedTranscript(
                    speaker=turn.speaker,
                    start=turn.start,
                    end=turn.end,
                    text=inaudible_marker,
                    is_inaudible=True,
                )
            )
    return aligned
```

Example usage with real diarization output:

```python
turns: list[DiarizationTurn] = [
    DiarizationTurn(start=0.80, duration=5.20, speaker="SPEAKER_01"),
    DiarizationTurn(start=6.00, duration=3.50, speaker="SPEAKER_02"),
    DiarizationTurn(start=9.50, duration=0.15, speaker="SPEAKER_01"),  # too short
]

result = transcribe_audio("interview.wav", model_name="small")
aligned = align_transcription_with_turns(turns, result["segments"])

for row in aligned:
    label = "[INAUDIBLE]" if row.is_inaudible else row.text
    print(f"[{row.start:.2f}-{row.end:.2f}] {row.speaker}: {label}")
```

To tune the short-fragment gate:

```python
# Make the gate stricter (treat anything under half a second as inaudible).
aligned = align_transcription_with_turns(turns, result["segments"], min_duration_s=0.5)

# Drop inaudible turns entirely (e.g. for a clean summary).
speech_only: list[AlignedTranscript] = [row for row in aligned if not row.is_inaudible]

inaudible_count = sum(1 for row in aligned if row.is_inaudible)
print(f"{inaudible_count} of {len(aligned)} turns had no usable transcription.")
```

### 6. (Optional) Pin the language

Whisper auto-detects language from the first ~30 seconds of audio, which is
convenient but occasionally wrong on short or code-switched clips. Pinning the
language removes that ambiguity and slightly improves accuracy. Auto-detect
when input is mixed or unknown; specify when you know it in advance.

```python
# Auto-detect — best when you genuinely do not know the language.
auto = transcribe_audio("clip.wav", model_name="small")
print(f"Whisper guessed: {auto['language']}")

# Specify — best when the language is known; validated by _validate_language_code.
english = transcribe_audio("clip.wav", model_name="small", language="en")
```

### 7. Render speaker-labeled subtitles (SRT)

The aligned rows already carry everything a subtitle needs: a speaker, a start
and end time, and text. Formatting them as SRT is the final step for
"accurate speaker-labeled subtitles".

```python
from __future__ import annotations

from typing import Sequence

# Builds on AlignedTranscript and INAUDIBLE_MARKER from earlier blocks.


def _format_srt_timestamp(seconds: float) -> str:
    """Format a time offset as SRT's HH:MM:SS,mmm."""
    if seconds < 0:
        raise ValueError(f"Timestamp must be non-negative, got {seconds}.")
    total_milliseconds = round(seconds * 1000)
    hours, remainder = divmod(total_milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    secs, milliseconds = divmod(remainder, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"


def render_srt(
    aligned: Sequence[AlignedTranscript],
    *,
    include_inaudible: bool = False,
) -> str:
    """Render aligned turns as an SRT subtitle document.

    Args:
        aligned: The output of align_transcription_with_turns.
        include_inaudible: When False (default), turns marked inaudible are
            skipped so captions do not flash '[INAUDIBLE]' at the viewer.

    Returns:
        A complete SRT string, or an empty string if nothing was renderable.
    """
    blocks: list[str] = []
    index = 1
    for row in aligned:
        if row.is_inaudible and not include_inaudible:
            continue
        start = _format_srt_timestamp(row.start)
        end = _format_srt_timestamp(row.end)
        blocks.append(f"{index}\n{start} --> {end}\n{row.speaker}: {row.text}\n")
        index += 1
    return "\n".join(blocks)


subtitles = render_srt(aligned)
print(subtitles)
```

## Pitfalls

- **Very poor audio quality.** Whisper was trained on largely intelligible
  speech. Heavy background noise, clipping, or low bitrate push the model toward
  hallucinated words because it always tries to produce *some* output. If your
  source is noisy, denoise first or gate low-confidence output using
  `no_speech_prob` in the segment metadata.
- **Very short segments.** A 200 ms fragment rarely contains enough acoustic
  context for the model to commit to a transcription, so it tends to emit empty
  or nonsensical text. The alignment code treats anything under
  `MIN_SEGMENT_DURATION_S` (0.3 s) as `[INAUDIBLE]` rather than trusting a
  likely-hallucinated result.
- **The `tiny` model.** Its accuracy is low enough that it is only useful for
  smoke-testing a pipeline. Treat it as a development convenience, not a
  production choice — `small` costs little more and is dramatically more
  reliable.
- **Data privacy in production.** Audio of real people is often sensitive
  (PII, health information, legal discussions). Running Whisper *locally* keeps
  that audio on your own infrastructure; calling a hosted transcription API
  sends it to a third party. Choose deliberately, and avoid logging raw
  transcripts to shared sinks.
- **Uncommon languages and accents.** Whisper's quality is uneven across the
  long tail of languages and regional accents because its training data is.
  Before trusting it on a new language, transcribe a labeled sample and measure
  word error rate rather than assuming parity with English.
- **Language auto-detect on short clips.** Whisper auto-detects from the first
  ~30 seconds of audio. On short or code-switched clips this can be wrong. Pin
  the language with the `language` parameter when you know it in advance.
- **Overlap vs containment in alignment.** A single spoken sentence frequently
  straddles the boundary between two diarization turns. The alignment logic uses
  temporal overlap (not containment) to distribute Whisper segments across turns.
  Do not change this to a containment test or you will silently drop text from
  boundary-spanning sentences.
- **Blank segments from faster-whisper.** The `transcribe_with_faster_whisper`
  function skips blank segments rather than emitting empty captions. If you
  modify this to keep blanks, downstream SRT rendering will produce empty
  subtitle blocks.

## Verification

Each check below targets a specific failure mode:

- [ ] **Run the unit test for alignment.** Alignment is pure logic with no model
  dependency, so it can be tested deterministically with synthetic segments —
  this catches off-by-one overlap bugs without waiting on inference.
- [ ] **Confirm timestamps stay aligned with diarization.** Every aligned row's
  window must match its source turn; drift here desynchronizes subtitles.
- [ ] **Spot-check across model sizes.** Compare `small` vs `large-v3` on a
  representative clip to confirm the accuracy/speed trade-off is acceptable.
- [ ] **Measure on your actual language/accent.** Whisper's quality varies, so
  validate on a labeled sample rather than assuming English-level accuracy.
- [ ] **Review data-handling for privacy.** Ensure audio and transcripts are not
  written to shared or third-party sinks if they contain sensitive content.

Run this test suite — it has no placeholders and exercises the real alignment
logic with synthetic data (no audio or GPU required):

```python
from __future__ import annotations

from pathlib import Path

# Builds on the preamble plus the alignment block: transcribe_audio,
# align_transcription_with_turns, DiarizationTurn, WhisperSegment,
# INAUDIBLE_MARKER, ASRError.


def test_alignment_is_complete_ordered_and_synced() -> None:
    """Pure, deterministic test of the alignment contract — no model required."""
    turns: list[DiarizationTurn] = [
        DiarizationTurn(start=0.0, duration=2.0, speaker="SPEAKER_01"),
        DiarizationTurn(start=2.0, duration=2.0, speaker="SPEAKER_02"),
        DiarizationTurn(start=4.0, duration=0.1, speaker="SPEAKER_01"),  # too short
    ]
    segments: list[WhisperSegment] = [
        {"start": 0.1, "end": 1.9, "text": "Hello there."},
        {"start": 1.8, "end": 3.5, "text": "General Kenobi."},  # straddles turns 1-2
    ]

    aligned = align_transcription_with_turns(turns, segments)

    # 1. Completeness: exactly one output row per input turn.
    assert len(aligned) == len(turns), "alignment must not drop or duplicate turns"

    # 2. Ordering and time sync: each row's window equals its source turn's window.
    for row, turn in zip(aligned, turns):
        assert row.speaker == turn.speaker
        assert row.start == turn.start
        assert row.end == turn.end

    # 3. Overlap semantics: the straddling segment reaches both turns 1 and 2.
    assert "Hello there." in aligned[0].text
    assert "General Kenobi." in aligned[0].text
    assert "General Kenobi." in aligned[1].text

    # 4. Short-fragment gating: the 0.1s turn is marked inaudible, not transcribed.
    assert aligned[2].is_inaudible is True
    assert aligned[2].text == INAUDIBLE_MARKER

    print("Alignment unit test passed.")


def run_integration_check(audio_path: str | Path) -> None:
    """End-to-end check against a real audio file. Skips gracefully when the
    fixture is absent so the suite still runs in environments without sample
    audio or model weights."""
    path = Path(audio_path)
    if not path.is_file():
        print(f"Integration check skipped: no audio fixture at {path}.")
        return

    try:
        result = transcribe_audio(path, model_name="small")
    except ASRError as exc:
        raise AssertionError(f"Integration transcription failed: {exc}") from exc

    assert result["segments"], "expected at least one transcribed segment"
    for seg in result["segments"]:
        assert seg["end"] >= seg["start"], "segment end must not precede its start"
        assert isinstance(seg["text"], str)
    print(
        f"Integration check passed: {len(result['segments'])} segments, "
        f"language={result['language']!r}."
    )


if __name__ == "__main__":
    test_alignment_is_complete_ordered_and_synced()
    run_integration_check("path/to/audio/file.wav")
    print("ASR verification complete.")
```

## Related skills

- **Speaker Diarization** — runs *before* ASR and produces the `DiarizationTurn`
  list this skill aligns against.
- **Natural Language Processing (NLP)** — consumes the transcript for
  summarization, search, or sentiment analysis.
- **Speech Synthesis** — the inverse operation (text → audio).
