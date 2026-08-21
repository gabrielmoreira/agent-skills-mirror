---
name: text-to-speech
version: 1.1.1
description: "Masters synthesized voiceover with FFmpeg: artifact cleanup, -23 LUFS loudnorm, atempo or silence pad, boundary fades, and segment stitch for video. Use for TTS, LUFS, or voiceover export. Do not use for Whisper transcripts (automatic-speech-recognition) and not a live-mic capture chair."
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-14
---

# SKILL: TTS Audio Mastering

Produce clean, consistent, delivery-ready TTS audio for video integration. Covers speech cleanup, loudness normalization, segment boundary handling, and export specifications.

## When to Use

Use this skill when you need to:
- Generate and master Text-to-Speech (TTS) audio for video project integration
- Apply loudness normalization to synthesized speech to meet delivery specs
- Clean up TTS artifacts (rumble, digital fizz, boundary clicks)
- Align TTS segment durations to target timing windows
- Stitch multiple TTS segments into a continuous track

**Trigger keywords:** TTS, text-to-speech, voiceover synthesis, audio mastering, loudness normalization, LUFS, speech cleanup, TTS for video, segment stitching

## Prerequisites

- **FFmpeg** (latest stable release) — older versions may have security vulnerabilities; always update before use
- **A TTS engine** chosen by deployment constraints:
  - **Neural offline** (e.g., Kokoro): stable, high quality, no network dependency
  - **Cloud TTS** (e.g., Edge-TTS / OpenAI TTS): convenient, higher naturalness but network-dependent
  - **Formant TTS** (e.g., Flite): prototyping only; less natural
- **Windows host (PowerShell)** is the primary environment. All commands below are FFmpeg CLI and work in PowerShell.
- If using cloud TTS, ensure API credentials are securely managed (use `YOUR_KEY` placeholders in scripts; never hardcode live secrets).

### Hard Rules

- **Never use `espeak-ng` for production TTS** — deprecated due to unnatural sound quality. Use only for quick prototyping if explicitly requested.
- **Always confirm the native sample rate** of generated audio before resampling for video delivery. Common rates as of 2026: 44.1 kHz, 48 kHz, 96 kHz.
- **Always apply loudness normalization as the final step** after cleanup and timing edits. If you adjust tempo/duration after normalization, re-normalize again.
- **Always apply boundary fades after padding or trimming** to avoid clicks.
- **Keep end-to-end drift ≤ 0.2s** unless the task explicitly states otherwise.

## Procedure

### Step 1 — Generate TTS Audio

1. Choose a TTS engine based on quality needs and deployment constraints (see Prerequisites).
2. Generate the raw TTS audio segment(s) to a WAV file.
3. Confirm the native sample rate of the output:
   ```powershell
   ffprobe -v error -select_streams a:0 -show_entries stream=sample_rate -of csv=p=0 input.wav
   ```
4. Note the sample rate — you will need it for any resampling or silence generation steps.

### Step 2 — Speech Cleanup (Per Segment)

Apply lightweight processing to remove common artifacts. Keep filter chains **consistent across all segments**.

**Filter chain:**
- **High-pass filter at 20 Hz** — removes rumble and DC offset
- **Low-pass filter at 16 kHz** (optional) — removes digital fizz/harshness
- **Fade-in 50 ms** and **fade-out 50 ms** — prevents clicks at boundaries

```powershell
# Replace DURATION with the actual segment duration in seconds (e.g., 5.0)
ffmpeg -i input.wav -af "highpass=f=20,lowpass=f=16000,afade=t=in:ss=0:d=0.05,afade=t=out:ss=DURATION-0.05:d=0.05" cleaned.wav
```

> **Note:** You must substitute `DURATION` with the real audio length. Obtain it via:
> ```powershell
> ffprobe -v error -show_entries format=duration -of csv=p=0 input.wav
> ```

### Step 3 — Measure Loudness

Measure integrated loudness and true peak using FFmpeg's `ebur128` filter:

```powershell
ffmpeg -i cleaned.wav -filter_complex ebur128 -f null -
```

Review the output for:
- **Integrated loudness** (I) — target: **-23 LUFS**
- **True peak** (TP) — target: **-1.5 dBTP**
- **Loudness range** (LRA) — target: around **11** (optional guideline)

### Step 4 — Loudness Normalization

Apply `loudnorm` as the **final step** after cleanup and timing edits:

```powershell
# Single-pass normalization (simpler, slightly less precise)
ffmpeg -i cleaned.wav -af "loudnorm=I=-23:LRA=11:TP=-1.5" output_mastered.wav
```

For best results, use a **two-pass** loudnorm workflow:
1. First pass — extract measured values:
   ```powershell
   ffmpeg -i cleaned.wav -af "loudnorm=I=-23:LRA=11:TP=-1.5:print_format=json" -f null - 2> loudnorm_log.txt
   ```
2. Parse the JSON output for `measured_I`, `measured_TP`, `measured_LRA`, `measured_thresh`, `offset`, `target_offset`.
3. Second pass — apply with measured values:
   ```powershell
   ffmpeg -i cleaned.wav -af "loudnorm=I=-23:LRA=11:TP=-1.5:measured_I=<MEASURED_I>:measured_TP=<MEASURED_TP>:measured_LRA=<MEASURED_LRA>:measured_thresh=<MEASURED_THRESH>:offset=<OFFSET>:linear=true" output_mastered.wav
   ```

**Critical:** If you adjust tempo or duration after this step, you **must re-normalize**.

### Step 5 — Timing & Segment Boundary Handling

When stitching segment-level TTS into a full track:

#### 5a — Padding a short segment with silence

If a segment is shorter than its target window, pad with silence:

```powershell
# Example: segment is 3s, target window is 5s → create 2s of silence
# Use the SAME sample rate and channel layout as the segment
ffmpeg -f lavfi -i "anullsrc=r=44100:cl=stereo" -t 2 silence.wav

# Concatenate segment + silence
ffmpeg -i tts_segment.wav -i silence.wav -filter_complex "[0:a][1:a]concat=n=2:v=0:a=1[a]" -map "[a]" padded_segment.wav
```

#### 5b — Gentle speed adjustment for a slightly long segment

If a segment is slightly longer than its window, use `atempo` for a small speed change:

```powershell
# Example: segment is 5.2s, target is 5s
# Speed factor = target / actual = 5 / 5.2 = 0.9615
ffmpeg -i tts_segment.wav -filter:a "atempo=0.9615" speed_adjusted_segment.wav
```

> **Caution:** Keep `atempo` adjustments small (ideally within ±5%). Larger changes introduce audible artifacts. If a segment is significantly too long, consider regenerating with adjusted pacing from the TTS engine.

#### 5c — Apply boundary fades after any padding/trimming

Always re-apply 50 ms fades after padding or trimming to prevent clicks:

```powershell
ffmpeg -i padded_segment.wav -af "afade=t=in:ss=0:d=0.05,afade=t=out:ss=DURATION-0.05:d=0.05" final_segment.wav
```

### Step 6 — Stitch Segments into Full Track

Concatenate all mastered segments:

```powershell
# Create a concat list file
# file 'segment_01.wav'
# file 'segment_02.wav'
# file 'segment_03.wav'
ffmpeg -f concat -safe 0 -i concat_list.txt -c copy full_track.wav
```

Verify end-to-end drift is **≤ 0.2s** against the target timeline.

## Examples

### Example 1: Full Cleanup + Normalization Pipeline

```powershell
# 1. Get duration
$duration = (ffprobe -v error -show_entries format=duration -of csv=p=0 input.wav)

# 2. Cleanup
ffmpeg -i input.wav -af "highpass=f=20,lowpass=f=16000,afade=t=in:ss=0:d=0.05,afade=t=out:ss=$($duration - 0.05):d=0.05" cleaned.wav

# 3. Measure
ffmpeg -i cleaned.wav -filter_complex ebur128 -f null -

# 4. Normalize
ffmpeg -i cleaned.wav -af "loudnorm=I=-23:LRA=11:TP=-1.5" output_mastered.wav
```

### Example 2: Padding + Speed Adjustment Combined

```powershell
# Segment is 4.8s, target window is 5.0s
# Pad with 0.2s silence at the end
ffmpeg -f lavfi -i "anullsrc=r=44100:cl=stereo" -t 0.2 silence_tail.wav
ffmpeg -i tts_segment.wav -i silence_tail.wav -filter_complex "[0:a][1:a]concat=n=2:v=0:a=1[a]" -map "[a]" padded.wav

# Apply boundary fades
$dur = (ffprobe -v error -show_entries format=duration -of csv=p=0 padded.wav)
ffmpeg -i padded.wav -af "afade=t=in:ss=0:d=0.05,afade=t=out:ss=$($dur - 0.05):d=0.05" final.wav
```

## Pitfalls

- **Using `espeak-ng` for production** — deprecated; sound quality is unnatural. Use neural or cloud TTS engines instead.
- **Resampling without checking native sample rate** — always confirm the TTS engine's output rate before resampling to avoid unnecessary quality loss.
- **Applying loudnorm before timing edits** — normalization must be the **last** step. Any tempo/duration change after normalization requires re-normalizing.
- **Missing boundary fades after padding/trimming** — causes audible clicks at segment boundaries. Always re-apply 50 ms fades.
- **Large `atempo` adjustments** — changes beyond ±5% introduce warbling artifacts. Prefer regenerating the TTS segment with adjusted pacing.
- **Inconsistent filter chains across segments** — use the same cleanup filter chain for every segment to maintain tonal consistency.
- **Outdated FFmpeg** — older versions may have security vulnerabilities. Always use the latest stable release.
- **Hardcoded API credentials** — when using cloud TTS, never hardcode live API keys in scripts. Use environment variables or secure credential stores with `YOUR_KEY` placeholders.
- **Exceeding drift tolerance** — end-to-end drift > 0.2s causes visible desync in video. Verify total track duration against the target timeline.

## Verification

Run these checks on the final mastered audio:

```powershell
# 1. Verify integrated loudness meets -23 LUFS target
ffmpeg -i output_mastered.wav -filter_complex ebur128 -f null -
# Check: Integrated loudness should read approximately -23.0 LUFS

# 2. Verify true peak is within -1.5 dBTP
# The ebur128 output includes true peak measurements
# Check: True peak should not exceed -1.5 dBTP

# 3. Verify sample rate matches delivery spec
ffprobe -v error -select_streams a:0 -show_entries stream=sample_rate -of csv=p=0 output_mastered.wav

# 4. Verify total duration
ffprobe -v error -show_entries format=duration -of csv=p=0 output_mastered.wav
# Compare against target timeline; drift must be <= 0.2s

# 5. Listen test — play the final audio and check for:
#    - No clicks at segment boundaries
#    - No rumble or DC offset
#    - No digital fizz/harshness
#    - Consistent loudness across all segments
```

**Checklist:**
- [ ] TTS segment generated with a chosen engine (not `espeak-ng` for production)
- [ ] Native sample rate confirmed before any resampling
- [ ] Speech cleanup filters applied (highpass=20Hz, lowpass=16kHz, 50ms fades)
- [ ] Loudness measured with `ebur128`
- [ ] Loudness normalized to -23 LUFS, -1.5 dBTP, LRA ~11
- [ ] Normalization applied as the final step (or re-normalized after any timing change)
- [ ] Short segments padded with silence; long segments gently speed-adjusted (≤5%)
- [ ] Boundary fades re-applied after all padding/trimming
- [ ] End-to-end drift ≤ 0.2s
- [ ] Final audio listened to for artifacts and consistency

## Related Skills

- `audio-transcription` — generates text from speech, which can serve as input for TTS
- `video-editing` — integrates mastered TTS audio into video timelines
- `audio-analysis` — advanced audio property analysis beyond basic loudness measurement
