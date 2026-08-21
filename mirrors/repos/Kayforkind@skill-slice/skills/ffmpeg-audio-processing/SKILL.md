---
name: ffmpeg-audio-processing
version: 1.3.1
description: "Extracts, loudness-normalizes (loudnorm/LUFS), mixes, resamples, and analyzes audio with FFmpeg filter graphs. Use when pulling soundtracks from video, mixing narration over music, rearranging channels, or measuring levels. Not for container remux (ffmpeg-format-conversion), DAW timeline edits, or real-time low-latency streaming."
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-16
---

# FFmpeg Audio Processing Skill

Extract, normalize, mix, and process audio tracks from video and audio files using FFmpeg — the non-interactive, scriptable tool that covers the full pipeline (demux → decode → filter → encode → mux) in a single invocation. Ideal for batch jobs and reproducible automation where a GUI editor would force manual, unrepeatable steps.

FFmpeg expresses everything as command-line flags and filter graphs, so the value of this skill is knowing *which* flags express your intent and *why* they behave the way they do.

## When to Use

Reach for this skill when the operation is a deterministic, file-to-file transform that you want to script or repeat:

- **Extract audio from video** — you need the soundtrack as a standalone file (e.g. transcription, podcast production) and want to control codec/quality.
- **Normalize audio levels** — different sources were recorded at different loudness and you need a consistent target (streaming, broadcast, podcast).
- **Mix multiple audio tracks** — combine narration with a music bed, or fold several stems into one track with per-source gain control.
- **Convert audio formats** — move between containers/codecs (WAV ↔ MP3 ↔ AAC ↔ FLAC ↔ Opus) for size, compatibility, or quality reasons.
- **Extract or rearrange channels** — pull a single channel out of a stereo file, or collapse/expand the channel count.
- **Adjust audio volume** — apply a fixed gain in dB or as a linear multiplier.
- **Resample audio** — change sample rate to match delivery target (48 kHz for video, 44.1 kHz for music).
- **Analyze audio levels** — measure peak, mean, loudness, or stream metadata before processing.

### When NOT to Use

- **Complex, timeline-based multi-track editing** — FFmpeg has no visual timeline. Arranging clips by ear, drawing volume automation, or doing spectral repair is far easier in a DAW (Audacity, Reaper, Adobe Audition). Use FFmpeg for deterministic batch steps and a DAW for creative, by-hand work.
- **Low-latency real-time streaming** — FFmpeg *can* stream, but the recipes here assume file-to-file batch processing. Real-time, low-latency pipelines need specific tuning (`-fflags nobuffer`, `-flags low_delay`, buffer sizing) that is out of scope and easy to get wrong.
- **Bit-exact archival masters from a lossy source** — every lossy re-encode (MP3/AAC/Opus) permanently discards information. If you need an archival master, keep it in a lossless format (WAV or FLAC) and only derive lossy copies. Never transcode lossy → lossy when quality must be preserved.
- **FFmpeg older than 5.1** — prefer FFmpeg 6.x/7.x, or at minimum 5.1. Older builds miss filter improvements this skill relies on (e.g. `loudnorm` linear mode, the high-quality `soxr` resampler) and accumulate unpatched CVEs. `aac` (FFmpeg's native encoder) and `libmp3lame` are the current recommended encoders — neither is deprecated; the genuinely deprecated piece is the old `-map_channel` option, which the channel examples below replace with the `pan` filter.

## Prerequisites

### Confirm FFmpeg is installed

Before running any command, verify the binaries exist:

```powershell
ffmpeg -version
ffprobe -version
```

Both should print version information. A clear "not installed" error beats a confusing failure deep in a pipeline. Prefer FFmpeg 6.x/7.x, or at minimum 5.1.

### Safe invocation habits

A few habits prevent the most common failures and security pitfalls:

1. **Never build commands by string-concatenating untrusted filenames.** A filename containing `;`, `$( )`, quotes, or spaces can break a shell command or inject arbitrary commands. In scripts, pass arguments as an array — `execFile` with an argv array in Node, `subprocess.run([...])` (never `shell=True`) in Python. In the shell, always quote paths: `"$input"`.
2. **Decide overwrite behavior explicitly.** `-y` overwrites the output without asking; `-n` refuses to overwrite. Pick one so an interactive prompt never stalls an automated run.
3. **Add `-hide_banner`** to keep logs focused on warnings/errors rather than build configuration noise.
4. **Fail fast in shell scripts** with `set -euo pipefail` (bash) or `$ErrorActionPreference = "Stop"` (PowerShell) so a failed extract does not silently feed an empty file into the next step.

### Defensive wrapper pattern (bash)

```bash
#!/usr/bin/env bash
set -euo pipefail

require() { command -v "$1" >/dev/null 2>&1 || { echo "Missing dependency: $1" >&2; exit 1; }; }
require ffmpeg
require ffprobe

input="${1:?usage: process.sh <input> <output>}"
output="${2:?usage: process.sh <input> <output>}"
[[ -f "$input" ]] || { echo "Input not found: $input" >&2; exit 1; }
```

### Defensive wrapper pattern (PowerShell)

```powershell
$ErrorActionPreference = "Stop"
if (-not (Get-Command ffmpeg -ErrorAction SilentlyContinue)) { throw "ffmpeg not found" }
if (-not (Get-Command ffprobe -ErrorAction SilentlyContinue)) { throw "ffprobe not found" }
if (-not (Test-Path $args[0])) { throw "Input not found: $($args[0])" }
```

## Procedure

Each command below notes *why* the flags are chosen so you can adapt them safely. All commands use `-hide_banner` and `-y` for clean, non-interactive automation.

### 1. Extract Audio from Video

#### Re-encode to MP3 (VBR, transparent quality)

`-vn` drops the video stream so we only process audio. `-q:a 2` selects VBR quality ~190 kbps: transparent for speech/music, smaller than a fixed high bitrate. `libmp3lame` is the recommended MP3 encoder.

```powershell
ffmpeg -hide_banner -y -i "video.mp4" -vn -c:a libmp3lame -q:a 2 "audio.mp3"
```

#### Stream-copy AAC out of an MP4 (no re-encode)

Near-instant and lossless because the bytes are copied verbatim — only valid when the source codec already matches the target container.

```powershell
ffmpeg -hide_banner -y -i "video.mp4" -vn -c:a copy "audio.aac"
```

#### Extract to uncompressed 16-bit PCM WAV

Use this as a working master when later steps must avoid stacking lossy generation loss.

```powershell
ffmpeg -hide_banner -y -i "video.mp4" -vn -c:a pcm_s16le "audio.wav"
```

#### Pick a specific audio stream (0-based)

When a file carries several tracks, e.g. a second-language dub at index 1.

```powershell
ffmpeg -hide_banner -y -i "video.mp4" -map 0:a:1 -c:a copy "audio2.aac"
```

### 2. Normalize Audio Levels (Loudness Normalization)

Loudness normalization targets a perceived-loudness value (LUFS), not a peak, so quiet and loud sources end up sounding equally loud. The targets differ by platform: streaming services aim near -14 LUFS, EBU R128 broadcast at -23 LUFS, and spoken-word podcasts around -16 LUFS.

**Gotcha:** `loudnorm` runs internally at 192 kHz, so the output inherits that rate unless you pin it back with `-ar` (or an `aresample` after the filter).

#### Single pass (fast, casual use)

`I` = integrated loudness target, `TP` = max true peak (dBTP, -1.5 leaves headroom against inter-sample clipping), `LRA` = allowed loudness range. `-ar 48000` pins the rate back to the source's.

```powershell
ffmpeg -hide_banner -y -i "input.wav" `
  -af "loudnorm=I=-16:TP=-1.5:LRA=11" -ar 48000 "output.wav"
```

#### Two pass (accurate, repeatable)

Pass 1 measures and writes nothing (`-f null -` discards output portably on Windows and POSIX):

```powershell
ffmpeg -hide_banner -i "input.wav" `
  -af "loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json" -f null -
```

Pass 2 feeds the measured_* values from that JSON back in. `linear=true` makes `loudnorm` apply one static gain offset instead of dynamic compression, which preserves the source dynamics — the whole point of measuring first. (Numbers below are examples; substitute the ones pass 1 printed.)

```powershell
ffmpeg -hide_banner -y -i "input.wav" `
  -af "loudnorm=I=-16:TP=-1.5:LRA=11:measured_I=-23.1:measured_TP=-4.2:measured_LRA=6.4:measured_thresh=-33.5:offset=0.3:linear=true" `
  -ar 48000 "normalized.wav"
```

### 3. Adjust Volume

`volume` accepts either decibels (perceptual, what you usually want) or a linear multiplier. +6 dB ≈ double the amplitude; a 0.5 linear factor halves it.

```powershell
# Raise level by 6 dB (about 2x amplitude)
ffmpeg -hide_banner -y -i "input.wav" -af "volume=6dB" "louder.wav"

# Lower level by 3 dB
ffmpeg -hide_banner -y -i "input.wav" -af "volume=-3dB" "quieter.wav"

# Linear multiplier: 0.5 = half amplitude (~-6 dB)
ffmpeg -hide_banner -y -i "input.wav" -af "volume=0.5" "half.wav"
```

### 4. Channel Operations

`-map_channel` is deprecated; the `pan` filter is the modern, explicit replacement and reads as "build a mono output whose channel 0 is source channel c0 (left) or c1 (right)".

```powershell
# Extract the left channel to a mono file
ffmpeg -hide_banner -y -i "stereo.wav" -af "pan=mono|c0=c0" "left.wav"

# Extract the right channel to a mono file
ffmpeg -hide_banner -y -i "stereo.wav" -af "pan=mono|c0=c1" "right.wav"

# Downmix to mono. -ac 1 lets FFmpeg apply the correct downmix coefficients.
ffmpeg -hide_banner -y -i "stereo.wav" -ac 1 "mono.wav"

# Upmix mono to dual-mono stereo
ffmpeg -hide_banner -y -i "mono.wav" -ac 2 "stereo.wav"
```

### 5. Mix Audio Tracks

When mixing, `amix` by default divides the output by the number of inputs, which unexpectedly *attenuates* everything. `normalize=0` disables that so your per-source `volume` settings are honored exactly. `duration=first` stops the output at the end of the first input instead of stretching to the longest.

#### Replace a video's audio entirely with an external track

```powershell
ffmpeg -hide_banner -y -i "video.mp4" -i "audio.mp3" `
  -map 0:v:0 -map 1:a:0 -c:v copy -shortest "output.mp4"
```

#### Mix two tracks, preserving set levels (normalize=0)

```powershell
ffmpeg -hide_banner -y -i "video.mp4" -i "audio2.mp3" `
  -filter_complex "[0:a][1:a]amix=inputs=2:duration=first:normalize=0[mix]" `
  -map 0:v:0 -map "[mix]" -c:v copy "output.mp4"
```

#### Narration at full level with a quiet music bed underneath

```powershell
ffmpeg -hide_banner -y -i "video.mp4" -i "bgm.mp3" `
  -filter_complex "[0:a]volume=1.0[voice];[1:a]volume=0.25[music];[voice][music]amix=inputs=2:duration=first:dropout_transition=2:normalize=0[mix]" `
  -map 0:v:0 -map "[mix]" -c:v copy "output.mp4"
```

### 6. Audio Delay

```powershell
# Shift only the audio later by 0.5 s using a second, time-offset input of the
# same file. Useful for nudging lip-sync.
ffmpeg -hide_banner -y -i "video.mp4" -itsoffset 0.5 -i "video.mp4" `
  -map 0:v -map 1:a -c copy "output.mp4"

# Pure-filter delay in milliseconds. all=1 applies the same delay to every
# channel without having to list one value per channel.
ffmpeg -hide_banner -y -i "input.wav" -af "adelay=delays=500:all=1" "delayed.wav"
```

### 7. Sample Rate Conversion

Match the sample rate to the delivery target (48 kHz for video, 44.1 kHz for music CDs). The `soxr` resampler gives the highest quality when FFmpeg is built with libsoxr; drop `:resampler=soxr` if your build lacks it.

```powershell
# Resample in place within a container
ffmpeg -hide_banner -y -i "input.wav" -af "aresample=48000:resampler=soxr" -ar 48000 "out48k.wav"

# Extract audio and resample in one step
ffmpeg -hide_banner -y -i "input.mp4" -vn -af "aresample=48000:resampler=soxr" -ar 48000 "audio48k.wav"
```

### 8. Audio Filters

```powershell
# High-pass: remove rumble/handling noise below 200 Hz
ffmpeg -hide_banner -y -i "input.wav" -af "highpass=f=200" "hp.wav"

# Low-pass: tame harsh content above 3 kHz
ffmpeg -hide_banner -y -i "input.wav" -af "lowpass=f=3000" "lp.wav"

# Band-pass centered at 1 kHz with a 500 Hz width (h = Hz width type)
ffmpeg -hide_banner -y -i "input.wav" -af "bandpass=f=1000:width_type=h:w=500" "bp.wav"

# 2 s fade-in from the start, 2 s fade-out beginning at 8 s. Comma chains filters.
ffmpeg -hide_banner -y -i "input.wav" -af "afade=t=in:st=0:d=2,afade=t=out:st=8:d=2" "faded.wav"
```

### 9. Audio Analysis

```powershell
# Quick peak/mean dump. -f null - discards output and just prints the stats.
ffmpeg -hide_banner -i "input.wav" -af "volumedetect" -f null -

# EBU R128 integrated loudness, true peak, and range — measure before normalizing.
ffmpeg -hide_banner -i "input.wav" -af "ebur128=peak=true" -f null -

# Machine-readable stream metadata via ffprobe (sample rate, channels, bitrate).
ffprobe -v error -select_streams a:0 `
  -show_entries stream=codec_name,sample_rate,channels,bit_rate `
  -of json "input.wav"
```

### 10. Combine Multiple Audio Files

Prefer the `concat` *filter* for arbitrary files: it decodes each input first, so inputs may differ in codec, sample rate, or channel layout. The older `concat:` protocol and the concat demuxer require identical codecs and only suit specific formats.

#### Robust concatenation (inputs may differ in format)

```powershell
ffmpeg -hide_banner -y -i "a.mp3" -i "b.mp3" -i "c.mp3" `
  -filter_complex "[0:a][1:a][2:a]concat=n=3:v=0:a=1[out]" `
  -map "[out]" "joined.mp3"
```

#### Fast path (same codec/params, no re-encode)

`list.txt` contains lines like: `file 'a.mp3'`. `-safe 0` permits absolute paths in `list.txt`; omit it if the list only holds relative paths you control.

```powershell
ffmpeg -hide_banner -y -f concat -safe 0 -i "list.txt" -c copy "joined.mp3"
```

## Pitfalls

1. **`loudnorm` outputs at 192 kHz by default.** The filter runs internally at 192 kHz, so the output inherits that rate unless you pin it back with `-ar` (or an `aresample` after the filter). Always add `-ar 48000` (or your target rate) after `loudnorm`.

2. **`amix` attenuates by default.** `amix` divides the output by the number of inputs, which unexpectedly *attenuates* everything. Always set `normalize=0` when you want your per-source `volume` settings honored exactly.

3. **Lossy → lossy transcoding destroys quality.** Every lossy re-encode (MP3/AAC/Opus) permanently discards information. If you need an archival master, keep it in a lossless format (WAV or FLAC) and only derive lossy copies.

4. **`-map_channel` is deprecated.** Use the `pan` filter instead for channel extraction and rearrangement. The old `-map_channel` option is removed in newer FFmpeg builds.

5. **String-concatenating untrusted filenames is a security risk.** A filename containing `;`, `$( )`, quotes, or spaces can break a shell command or inject arbitrary commands. Always pass arguments as an array in scripts and quote paths in the shell.

6. **Missing `-y` or `-n` can stall automation.** Without explicit overwrite behavior, FFmpeg may prompt interactively, hanging automated runs. Always pick `-y` (overwrite) or `-n` (refuse).

7. **`-f null -` is portable.** It works on both Windows and POSIX for discarding output during measurement passes. Do not use platform-specific null devices.

8. **Concat demuxer requires identical codecs.** The `concat:` protocol and concat demuxer only work when all inputs share the exact same codec and parameters. Use the `concat` *filter* when inputs may differ.

9. **`soxr` resampler may not be available.** If your FFmpeg build lacks libsoxr, drop `:resampler=soxr` from the `aresample` filter. The default resampler still works, just at lower quality.

10. **FFmpeg older than 5.1 misses critical features.** Prefer FFmpeg 6.x/7.x. Older builds lack `loudnorm` linear mode, the high-quality `soxr` resampler, and accumulate unpatched CVEs.

## Verification

After running any command, verify the output:

### Verify output file exists and has content

```powershell
# Check file exists and is non-empty
Test-Path "output.wav"
(Get-Item "output.wav").Length  # Should be > 0
```

### Verify audio stream properties

```powershell
ffprobe -v error -select_streams a:0 `
  -show_entries stream=codec_name,sample_rate,channels,bit_rate,duration `
  -of json "output.wav"
```

Expected: JSON output showing the correct codec, sample rate, channel count, and non-zero duration.

### Verify loudness after normalization

```powershell
ffmpeg -hide_banner -i "normalized.wav" -af "ebur128=peak=true" -f null -
```

Check the `I` (integrated) value in the output — it should be close to your target (e.g. -16 LUFS).

### Verify volume levels

```powershell
ffmpeg -hide_banner -i "output.wav" -af "volumedetect" -f null -
```

Check `mean_volume` and `max_volume` in the output to confirm the levels are as expected.

### Verify channel layout

```powershell
ffprobe -v error -select_streams a:0 `
  -show_entries stream=channels,channel_layout `
  -of json "output.wav"
```

Expected: `"channels": 1` and `"channel_layout": "mono"` for mono output, or `"channels": 2` and `"channel_layout": "stereo"` for stereo.

### Verify concatenation succeeded

```powershell
# Output duration should approximately equal the sum of input durations
ffprobe -v error -show_entries format=duration -of csv=p=0 "joined.mp3"
```

## Related Skills

- **video-processing** — for video-specific operations (trimming, scaling, codec conversion) that complement audio extraction.
- **media-transcoding** — for broader format conversion across both audio and video containers.
