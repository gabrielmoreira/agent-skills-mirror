# Audio Asset Reference: `sprite-gen sound`

## Overview and CLI Usage

```bash
sprite-gen sound --kind sfx|bgm --prompt TEXT (or --prompt-file PATH) --duration SECONDS --event NAME --out-dir DIR [--cache-dir DIR] [--loop|--no-loop] [--target-lufs FLOAT] [--crossfade SECONDS]
```

### Options and System Requirements
- `--kind`: `sfx` (default `--no-loop`, -18 LUFS) or `bgm` (default `--loop`, -20 LUFS, instrumental).
- `--prompt` / `--prompt-file`: Prompt text or file. The provider may reject prompts containing artist names, franchises, or lyrics; the CLI omits a dialogue verb.
- `--duration`: Requested duration in seconds.
- `--event`: Safe identifier (1..128 characters); first character must be alphanumeric, remaining characters can be alphanumeric, dot, underscore, dash, or colon.
- `--out-dir`: Destination; must be new or match existing recipe and output file digests.
- `--cache-dir`: Defaults to `$XDG_CACHE_HOME/sprite-gen/audio` or `~/.cache/sprite-gen/audio` (never inside `--out-dir`; local by default but can be copied; no cross-cache-directory or cross-machine duplicate-request guarantee).
- `--target-lufs`: Target integrated loudness within `-36..-9` LUFS.
- `--crossfade`: Overlap duration in seconds.
- **Environment & PATH**: `ELEVENLABS_API_KEY` is required only for new paid requests (offline work needs none). `ffmpeg` (with `libopus` and `aac` encoders) and `ffprobe` are required on `PATH` and checked before paid calls.

## Provider APIs and Cost Accounting

Requests use ElevenLabs (`output_format=mp3_44100_128`):
- **SFX**: `POST /v1/sound-generation` (`text`, `duration_seconds` 0.5..30 [API reference takes precedence over 0.1s overview bound], `loop`, `model_id="eleven_text_to_sound_v2"`, `prompt_influence=0.3`).
- **BGM**: `POST /v1/music` (`prompt` max 4100 characters, `music_length_ms` 3000..600000, `model_id="music_v1"`, `force_instrumental=true`).

### Billing and Usage Accounting
Checked 2026-10-13: [ElevenLabs Pricing](https://elevenlabs.io/pricing/api) quotes SFX at $0.12/min and music at $0.15/min (USD), FAQ notes generation metering, and legacy [Capabilities](https://elevenlabs.io/docs/overview/capabilities/sound-effects) states 40 credits/sec for fixed-duration SFX. Because plans vary, no currency conversion is hardcoded; the runtime records provider `character_cost` directly from responses when present (never guessed currency). Check quotas via [User Subscription](https://elevenlabs.io/docs/api-reference/user/subscription/get) (`character_count`/`character_limit`).

## Cache Idempotency and Retries

Raw paid audio is stored in SQLite keyed by provider parameter digest. Tuning `--event`, loudness, or exports reuses raw cache without new purchases:
- **Locking & Recovery**: Atomic claims precede requests; raw blobs and receipts commit on success. Duplicates, crashes, or uncertain results refuse resubmission. Do not delete unresolved cache entries blindly; inspect provider billing/history first. All errors remain unresolved.
- **Offline Processing**: Downstream processing runs offline. Identical runs require no network.
- **Retries**: Uses `sprite_gen.gen.retry` exclusively. ElevenLabs 429 retries only when `detail.status` is `system_busy` or `too_many_concurrent_requests` (max 2 retries via `Retry-After` or engine backoff; see [ElevenLabs 429 Errors](https://elevenlabs.io/docs/help-center/technical/api-error-code-429)). No other 429, 5xx, transport retries, or provider fallbacks occur. Emits only bounded status, code, and request IDs without error prose.

## Audio DSP, Looping, and Quality Gates

1. **Export and Normalization**: Provider audio decodes to 48kHz stereo PCM. Normalization uses two-pass [FFmpeg Loudnorm](https://ffmpeg.org/ffmpeg-filters.html#loudnorm) targeting -2 dBTP with repeating loop context. Up to three per-format offline encode/measure passes correct codec reconstruction overshoot using measured gain and tighter oversampled [FFmpeg Alimiter](https://ffmpeg.org/ffmpeg-filters.html#alimiter) (192kHz, auto-gain off, latency compensated) without triggering provider retries.
2. **Export Formats**: Outputs complete normalized audio in 48kHz stereo Opus in OGG (`sound.ogg`, `libopus`, 160 kbps) and AAC in M4A (`sound.m4a`, `aac`, 192 kbps). The exporter exports M4A with `-movie_timescale 48000`, equal to the normalized source sample rate (setting the movie header box time scale; see [FFmpeg Formats](https://ffmpeg.org/ffmpeg-formats.html#mov_002c-mp4_002c-ismv)), preserving fractional-millisecond source lengths without introducing declared tail padding. Export files remove all pre-encode crossfades, loop splices, and 5ms boundary zero-tapers; the complete normalized source is preserved intact in encoded audio.
3. **Quality Gates**: Output formats must decode to the integrated loudness target within +/-1 LU and true peak <= -1 dBTP. After every AAC encode, the exporter invokes `ffprobe` and requires first audio stream `time_base=1/48000` and `duration_ts=end_frame-start_frame`; mismatch or unreadable duration fails clearly before publishing. Silence or unmeasurable audio fails. Numeric checks do not judge musical beat alignment.
4. **Looping and Playback Quality**: Crossfading is deferred to runtime preparation. Because playback overlap blending can alter loudness, applications must validate prepared and rendered audio output. No claim is made that all signals are perceptually seamless or beat aligned.
5. **Boundary Continuity Verification**: Computes loop boundary continuity by measuring the wrap delta and subtracting the difference between adjacent samples in the same decoded/resampled buffer at the decoded sample rate, evaluated separately for prepared buffers and rendered output. Artificial control discontinuities must fail; there is no absolute near-zero endpoint sample criterion. Tests verify numeric waveforms rather than subjective listening.

## Manifest Schema and Coordinates

Outputs `sound.json` (version 2, `kind="sprite-gen-sound"`, `recipe.processing_version=3`, independent of `playback` version 2). Existing output directories generated with recipe versions 1 or 2 are rejected; specify a new `--out-dir`. Original provider request cache keys and blobs remain unchanged; reprocessing cached audio needs no key or new paid request. Provider APIs, caching, and retry behaviors remain unchanged.

### Manifest Properties

- `event`: Safe string identifier (1..128 characters).
- `audio_kind`: `"sfx"` or `"bgm"`.
- `loop`: Boolean looping flag.
- `duration_seconds`: Final playback duration in seconds, derived as `(end_frame - start_frame - overlap_frames) / sample_rate` (for example, `(144000 - 12000) / 48000 = 2.75` s).
- `target_lufs`: Target integrated loudness in LUFS (`-36..-9`).
- `playback`: Integer coordinate object governing client-side preparation:
  ```json
  {
    "version": 2,
    "sample_rate": 48000,
    "start_frame": 0,
    "end_frame": 144000,
    "overlap_frames": 12000
  }
  ```
  - Coordinates refer to the complete exported pre-overlap PCM source at `sample_rate` (48000 Hz, independent of provider container sample rate) over the half-open interval `[start_frame, end_frame)`.
  - Let `N = end_frame - start_frame` and `M = overlap_frames`.
  - For non-looping audio (`loop: false`), `M = 0`.
  - For looping audio (`loop: true`), `2 <= M < N / 2` (see [helper mapping](#export-signatures) for the export minimum).
  - Manifest `duration_seconds` is `(N - M) / sample_rate`.
  - The CLI `--crossfade` parameter (seconds) is converted to integer frame count `M`, defaulting to `min(0.25, requested_duration / 8)`.
- `files`: Format dictionary for `ogg` and `m4a` containing `path`, decoded `duration_seconds` (full decoded file duration, which may include codec priming/tail padding), `lufs`, `true_peak_dbfs`, `sha256`, `encode_passes`, and `pcm_peak_limit_dbtp`.
- **Removed Fields**: `codec_taper_seconds`, `loop_start_seconds`, `loop_end_seconds`, and `crossfade_seconds` are removed from output manifest metadata (the recipe still accepts `--crossfade` in seconds).

## Client Playback Helper: sprite-gen-audio-v2.mjs

Loop blending and buffer trimming are executed in the browser via the standalone ES module `sprite-gen-audio-v2.mjs` (owned by the engine under `sprite_gen/audio`, bundled in wheels and emitted into game packs). The helper has no external imports or dependencies. The canonical algorithm resides solely in this module and must not be duplicated into consumer application code.

### Export Signatures

- `prepareAudioBuffer(decoded, playback) => AudioBuffer`:
  - Coordinates:
    - Input `playback` v2 provides integer fields `sample_rate=sr`, `start_frame=start`, `end_frame=end`, and `overlap_frames=M`.
    - Coordinate dimensions are `N=end-start` and destination sample rate `r=decoded.sampleRate`. Rescaling is `rescale(f)=f*r/sr`, evaluating multiplication before division.
    - Frame boundaries map to `first=floor(start*r/sr)` and `mappedEnd=floor(end*r/sr)`.
    - Buffer length requires `decoded.length >= mappedEnd-1`, providing exactly one frame of tolerance universally, not per decoder; two or more missing frames cause a `RangeError`.
    - Destination bounds evaluate to `last=min(mappedEnd,decoded.length)` and `N'=last-first`. All excess decoded padding is ignored.
  - One-shots (`M=0`): `L'=N'` and `M'=0`, copying `source[first:last]` unchanged; a one-frame shortfall reduces one-shot length by making the output one frame shorter, with no synthesis or padding.
  - Loops (`M>0`): `L'=Math.round((N-M)*r/sr)` is computed exactly once, rounding positive ties toward `+Infinity`, with `M'=N'-L'`. Thus, one missing decoded frame decreases `M'` by one without changing declared loop length `L'` (a one-frame shortfall reduces loop overlap, never declared loop length). The contract requires `2<=M'<N'/2` and `L'>0`; an overlap count `count<2` on a one-frame shortfall throws a `RangeError` containing the exact text `overlap too short after decoder one-frame shortfall`. Do not round overlap independently. The output copies `source[first+M':last-M']`, then blends the tail `M'` frames with the head `M'` frames using complementary cosine weights `0.5 - 0.5 * Math.cos(Math.PI * i / (M' - 1))`.
  - Supported minimum decoded rate is `r_min=8000 Hz`; the shared frame-contract validator rejects exports (before normalization and encoding) and manifest imports unless `M*r_min/sr>=3.5` for loops, with the exact integer check `2*M*8000>=7*sr`. This guarantees at least two destination blend frames after interval quantization (`<1` frame), final length rounding (`<=0.5` frame), and the single decoder shortfall (`1` frame). The runtime minimum remains `M'>=2`; when `M'` is 0 or 1 after shortfall, it throws the explicit `RangeError` above. For a 48kHz export, `M=20` is rejected and `M=21` is the minimum allowed. This conservative bound protects arbitrary interval origin and duration for supported rates.
  - Decoded-length rationale: Web Audio mandates resampling when context rates differ, but specifies no uniform length rounding. Chromium's official source uses `source_length/(source_rate/destination_rate)` truncated to an integer. Floating-point double arithmetic `48000/(48000/44100)` evaluates just below `44100` and truncates to `44099`. In a fractional example, `144003/(48000/44100)=132302.75625` truncates to `132302`. See [Blink AudioBus sample-rate conversion](https://chromium.googlesource.com/chromium/src/+/6718b706ff100957d755554cec783840a8f1f05b/third_party/blink/renderer/platform/audio/audio_bus.cc). This tolerance is an explicit contract allowance, not a universal specification guarantee.
  - **Cache & Immutability**:
    - The input `AudioBuffer` is not modified.
    - Employs an internal `WeakMap` cache per module instance. Calling with the same input buffer and playback metadata returns the previously prepared buffer. Passing an already prepared buffer with identical metadata returns itself; passing altered metadata on an already prepared buffer throws. Applications should import the same module URL once, retain prepared buffers, and avoid copying prepared PCM back into raw inputs.
- `createAudioSource(context, decoded, audio) => AudioBufferSourceNode`: Creates and configures an audio source node. For looping playback, it internally creates and caches an L+1 frame buffer with the final sample set to the first prepared sample for cyclic boundary interpolation, setting `loopStart = 0` and `loopEnd = prepared.duration` (L / sampleRate) to exclude the guard frame. One-shots use the immutable L-frame prepared buffer without a guard frame. Consumers must use this function to configure loop playback and must not overwrite `loopEnd` with `source.buffer.duration`; context and audio sample rates should match.

## Examples

```bash
sprite-gen sound --kind sfx --prompt "laser shot" --duration 0.8 --event laser:shot --out-dir ./dist/laser
sprite-gen sound --kind bgm --prompt "synth cave" --duration 20.0 --event cave:bgm --crossfade 0.25 --out-dir ./dist/cave
```

### Manifest Audio Fragment (`sound.json`, Partial)

```json
{
  "kind": "sprite-gen-sound",
  "version": 2,
  "event": "cave:bgm",
  "audio_kind": "bgm",
  "loop": true,
  "duration_seconds": 19.75,
  "target_lufs": -20.0,
  "playback": {
    "version": 2,
    "sample_rate": 48000,
    "start_frame": 0,
    "end_frame": 960000,
    "overlap_frames": 12000
  },
  "files": {
    "ogg": { "path": "sound.ogg" },
    "m4a": { "path": "sound.m4a" }
  }
}
```

## References
- [ElevenLabs SFX](https://elevenlabs.io/docs/api-reference/text-to-sound-effects/convert)
- [ElevenLabs Music](https://elevenlabs.io/docs/api-reference/music/compose)
- [ElevenLabs 429 Errors](https://elevenlabs.io/docs/help-center/technical/api-error-code-429)
- [ElevenLabs Capabilities](https://elevenlabs.io/docs/overview/capabilities/sound-effects)
- [ElevenLabs Pricing](https://elevenlabs.io/pricing/api)
- [ElevenLabs Subscription](https://elevenlabs.io/docs/api-reference/user/subscription/get)
- [FFmpeg Loudnorm](https://ffmpeg.org/ffmpeg-filters.html#loudnorm)
- [FFmpeg Alimiter](https://ffmpeg.org/ffmpeg-filters.html#alimiter)
- [W3C Web Audio decodeAudioData](https://www.w3.org/TR/webaudio-1.0/#dom-baseaudiocontext-decodeaudiodata)
- [W3C Web Audio looping](https://www.w3.org/TR/webaudio-1.0/#looping)
