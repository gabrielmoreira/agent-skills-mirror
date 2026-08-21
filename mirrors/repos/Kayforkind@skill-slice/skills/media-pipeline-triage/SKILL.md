---
name: media-pipeline-triage
description: "Localizes audio/video pipeline failures—VFR drift, silent FFmpeg merges, lip-sync no-ops, subtitle lag, Veo speech-vs-song—by checking frames and streams per stage. Use when compiled shorts look out of sync or a lip-sync log claims success with closed mouths. Not for Remotion composition authoring or generic application crash hunts."
version: 1.0.1
risk: safe
source: custom
date_added: "2026-06-03"
domain: troubleshooting
kind: leaf
tags: [media, audio-video-sync, lip-sync, subtitles, ffmpeg, veo3]
---

# Media Pipeline Triage

Media pipeline failures hide behind vague symptoms like "it's out of sync" or "the lip-sync is off." Triage localizes *which stage* introduced the drift — audio extraction, clip generation, lip-sync retargeting, subtitle timing, or final compilation — because each points to a completely different fix.

## When to Use

Use when compiled music videos or shorts have audio-video misalignment, when lip-sync looks wrong, when subtitles appear at the wrong time, when FFmpeg produces silent output, or when AI-generated clip speech conflicts with the target song audio. This is the media-specific complement to `network-and-api-failure-triage` and extends the investigation methods of `hypothesis-driven-investigation` into the AV domain.

**Trigger keywords:** out of sync, lip-sync, mouth not moving, silent audio, subtitle drift, VFR, ffmpeg merge, veo3 speech, pipeline no change, no visible change, audio drift, face not detected.

## Prerequisites

- **FFmpeg and FFprobe** installed and on PATH (Windows PowerShell: `ffmpeg -version` must succeed).
- **Python 3.8+** with `numpy`, `scipy`, `opencv-python` if using automated offset detection or coordinate diagnostics.
- **SyncNet** (`pip install syncnet-python`) for quantitative lip-sync scoring.
- **InsightFace** with `buffalo_l` model and `det_10g.onnx` detector for face detection on stylized content.
- **Whisper** (or equivalent transcription tool) for subtitle timing validation.
- Access to all intermediate pipeline artifacts (raw clips, Wav2Lip outputs, LivePortrait outputs, audio slices). If intermediates are missing, the pipeline must be re-run with intermediate output enabled.

## Procedure

### Core Principle

**Never trust intermediate claims — visually verify every stage's output.** A log line that says "lip-sync complete, 133/133 frames processed" is not verification. An extracted frame showing open mouths during speech is verification.

### Phase 1: Identify the Failure Mode

Match the symptom to one of the seven canonical failure modes below before diving into debugging.

---

#### Failure Mode 1: Veo 3 Speech-vs-Song Conflict (Visual Mouth ≠ Audio Words)

**Symptom:** Character's mouth visibly says one thing while the audio track plays different words.

**Root Cause:** Veo 3 generates its own speech in clips. When the original song is overlaid, the visual speech doesn't match.

**Diagnosis:**
1. Extract audio from the raw clip (before song overlay):
   ```powershell
   ffmpeg -y -i shot_01.mp4 -vn -acodec pcm_s16le raw_clip_audio.wav
   ```
2. Transcribe the extracted audio with Whisper.
3. Compare the transcription against the target song lyrics at 3+ timestamps.

**Fix:** Regenerate clips using speech-suppressed prompts, or run the lip-sync re-sync pipeline to overwrite the visual mouth shapes with shapes driven by the target song audio.

---

#### Failure Mode 2: Silent Audio After FFmpeg Merge

**Symptom:** Final video plays but has no sound, or plays the wrong (silent AI-generated) audio track.

**Root Cause:** FFmpeg defaults to the first audio stream (often the silent AI-generated track from input 0) instead of the provided music file.

**Diagnosis:**
```powershell
ffprobe -v error -select_streams a -show_entries stream=codec_name,channels,bit_rate -of default=noprint_wrappers=1 output.mp4
```
If `bit_rate=N/A` or `channels=0`, the audio stream is empty.

**Fix:** Add explicit stream mapping to force video from input 0 and audio from the music file input:
```powershell
ffmpeg -y -i video_input.mp4 -i music.wav -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -shortest output.mp4
```

---

#### Failure Mode 3: Progressive Audio Drift (VFR Clips)

**Symptom:** Audio and video start aligned but gradually drift apart over the duration.

**Root Cause:** AI-generated clips often have variable frame rate (VFR). Concatenating VFR clips causes cumulative timing errors.

**Diagnosis — use the `vfrdet` filter (ffprobe metadata is unreliable; it reports nominal rate, not actual):**
```powershell
ffmpeg -i input.mp4 -vf vfrdet -an -f null -
```
Parse stderr for `VFR:X.XXX` — any value > 0 indicates variable frame rate.

Alternatively check frame rates:
```powershell
ffprobe -v error -select_streams v -show_entries stream=r_frame_rate,avg_frame_rate -of default=noprint_wrappers=1 clip.mp4
```
If `r_frame_rate` ≠ `avg_frame_rate`, it's VFR.

**Fix:** Convert all clips to CFR before concatenation:
```powershell
ffmpeg -y -i input_vfr.mp4 -vsync cfr -r 30 output_cfr.mp4
```

---

#### Failure Mode 4: Lip-Sync Face Detection Failure on Cartoons

**Symptom:** Lip-sync pipeline produces unchanged output or crashes with "no face detected."

**Root Cause:** Face detection models (trained on photorealistic faces) fail on heavily stylized Pixar/anime characters.

**Diagnosis:** Run the face detector in isolation and check if bounding boxes are returned. Print all detected faces and their bounding boxes:
```python
import cv2
# Load frame from the intermediate video at the resolution it's processed at
frame = cv2.imread("frame.png")
# ... run face detector ...
for face in detected_faces:
    x1, y1, x2, y2 = face['bbox']
    x_center = (x1 + x2) / 2.0
    y_center = (y1 + y2) / 2.0
    width = x2 - x1
    height = y2 - y1
    print(f"Face at center=({x_center:.0f}, {y_center:.0f}), size=({width:.0f}x{height:.0f})")
    cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
cv2.imwrite("debug_faces.png", frame)
```

**Fix:** Use InsightFace with the `buffalo_l` model and `det_10g.onnx` detector. For extreme stylization, use the LivePortrait two-stage pipeline which has better cartoon face handling.

---

#### Failure Mode 5: Lip-Sync Pipeline Produces No Visible Change (Silent Failure)

**Symptom:** Lip-sync pipeline runs to completion without errors, but the output video shows identical closed-mouth frames as the input. No crash, no warning — just zero lip movement.

**Root Cause:** One or more stages in a multi-stage pipeline silently fail, producing pass-through output. Common culprits:
- A function signature mismatch (method doesn't accept `**kwargs` but caller passes keyword args → `TypeError` or `NameError` silently swallowed).
- Face detection bounding box coordinates are valid at one resolution but wrong after crop/scale transforms between pipeline stages.
- The ML model (e.g., Wav2Lip) cannot generate meaningful output for the input domain (cartoon/3D vs photorealistic faces) but doesn't raise an error — it just outputs the original face unchanged.

**Diagnosis:** Follow the **Multi-Stage Pipeline Debugging Protocol** below.

**Fix:** Depends on which stage fails. If the ML model can't handle the input domain, switch to an alternative architecture (e.g., direct LivePortrait retargeting with a human driving video instead of Wav2Lip → LivePortrait chain).

---

#### Failure Mode 6: Subtitle Timing Drift

**Symptom:** Subtitles appear too early or too late relative to the vocals.

**Root Cause:** Subtitle timestamps were guessed or derived from storyboard estimates instead of actual audio transcription.

**Diagnosis:** Compare SRT timestamps against Whisper transcription timestamps of the audio file.

**Fix:** Re-generate subtitles from the actual audio using the `auto_subtitle_generator.py` script.

---

#### Failure Mode 7: Subtitle Oversized / Covering Character

**Symptom:** Text dominates the frame, covering the character's face or occupying >15% of screen height.

**Root Cause:** FontSize set too high (above 26 for libass, above 36 for MoviePy TextClip).

**Diagnosis:**
```powershell
ffmpeg -y -i video.mp4 -ss 00:00:15 -vframes 1 check.png
```
Visually inspect the extracted frame.

**Fix:** Reduce FontSize to 20–24 (libass) or 28–36 (MoviePy). Limit subtitle lines to 3–5 words per line.

---

### Phase 2: Multi-Stage Pipeline Debugging Protocol

Use this systematic method when the failure mode is "no visible change" or when you need to localize which stage in a multi-stage pipeline (e.g., audio extraction → Wav2Lip → LivePortrait → FFmpeg compile) introduced the defect.

#### Step 1: Verify the Final Output First (Reverse Trace)

Start from the end product — the compiled video — and confirm the symptom visually:

```powershell
ffmpeg -y -i final_output.mp4 -ss 00:00:02 -vframes 1 -update 1 verify_2s.png
ffmpeg -y -i final_output.mp4 -ss 00:00:12 -vframes 1 -update 1 verify_12s.png
```

**View the extracted frames.** Do NOT skip this step. Do NOT rely on logs or metadata claiming "lip-sync successful." The frame is the ground truth.

> If the frame shows closed mouths during speech, the lip-sync failed. If mouths are open but wrong words, it's Failure Mode 1 (Veo 3 Speech Conflict). If the frame looks correct, the compilation step is the likely culprit.

#### Step 2: Trace Backwards Through Every Intermediate Artifact

For each pipeline stage, locate and visually inspect its output:

```
Stage N (final compile)  →  final_output.mp4      → extract frame, view it
Stage N-1 (lip-sync)     →  synced_01.mp4          → extract frame, view it
Stage N-2 (driving gen)  →  wav2lip_output.mp4     → extract frame, view it
Stage N-3 (audio slice)  →  vocals_01.wav          → check duration, loudness
Stage 0 (raw clip)       →  shot_01.mp4            → extract frame, view it (baseline)
```

**The stage where the defect first appears is the culprit.** If the raw clip has closed mouths (expected) and the Wav2Lip output ALSO has closed mouths, Wav2Lip is the broken stage. If Wav2Lip output has open mouths but the LivePortrait output has closed mouths, LivePortrait is the broken stage.

**For each intermediate file:**
```powershell
# Extract a frame
ffmpeg -y -i intermediate.mp4 -ss 00:00:02 -vframes 1 -update 1 stage_check.png
# Check duration matches expectations
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 intermediate.mp4
# Check resolution
ffprobe -v error -select_streams v -show_entries stream=width,height -of csv=p=0 intermediate.mp4
```

#### Step 3: Read Code Signatures and Trace the Call Graph

Once you've localized the failing stage, read the actual source code — do not guess about how functions are called:

1. **Read the entry point** (the script that invokes the pipeline).
2. **Read every function signature** that handles the failing stage — check whether the method accepts `**kwargs`, what parameters it actually uses, and how they are passed.
3. **Trace keyword arguments end-to-end**: if the caller passes `source_path=args.source`, verify that every function in the chain actually receives and uses this parameter.
4. **Look for `kwargs` in non-kwargs methods** — a function that references `kwargs.get(...)` but has no `**kwargs` in its signature will raise a `NameError` at runtime.

**Common code-level failures in media pipelines:**
- Method signature doesn't accept `**kwargs` but caller passes keyword args.
- Scene-specific coordinate ranges hardcoded for one resolution but applied at a different resolution after crop/scale.
- Face detection bounding box filter ranges (x_min, x_max, y_max_thresh) tuned for widescreen but applied to vertical video.
- Exception swallowed in a `try/except` block, causing the pipeline to silently fall back to the unmodified input.

#### Step 4: Isolate Each Stage Independently

Run each pipeline stage in isolation to confirm it works or fails on its own:

```powershell
# 1. Extract the audio segment
ffmpeg -y -i vocals.wav -ss 0.07 -t 5.57 vocals_scene1.wav

# 2. Run Wav2Lip directly (NOT through the wrapper pipeline)
python Wav2Lip\inference.py --checkpoint_path Wav2Lip\checkpoints\wav2lip_gan.pth --face shot_01.mp4 --audio vocals_scene1.wav --outfile test_wav2lip_scene1.mp4

# 3. Extract frames and visually compare
ffmpeg -y -i test_wav2lip_scene1.mp4 -ss 00:00:02 -vframes 1 -update 1 wav2lip_check.png
ffmpeg -y -i shot_01.mp4 -ss 00:00:02 -vframes 1 -update 1 raw_check.png
```

**View both frames side-by-side.** If the Wav2Lip frame looks identical to the raw frame, Wav2Lip is not generating lip shapes for this face type.

#### Step 5: Check Coordinate Systems Across Resolution Transforms

Multi-stage pipelines often transform video resolution between stages. Face detection coordinates that work at one resolution may be completely wrong at another. Use the diagnostic Python snippet from Failure Mode 4 to print all detected faces and draw bounding boxes.

**Common coordinate failures:**
- Widescreen (1920×1080) coordinates applied to vertical (720×1280) after crop.
- Face center ranges `[300, 480]` tuned for a specific character position but the character is at `x=643` after re-composition.
- Multiple faces detected; the filter selects the wrong one (e.g., steering wheel scored higher than the actual face because the size threshold was too permissive).

#### Step 6: Verify Audio Input Quality

A lip-sync pipeline that receives silence or near-silence will correctly produce no lip movement:

```powershell
# Check duration
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 vocals_scene1.wav
# Check loudness
ffmpeg -i vocals_scene1.wav -af "volumedetect" -f null - 2>&1 | Select-String "mean_volume"
```
If `mean_volume` < -40 dB, the segment is effectively silent.

#### Step 7: Differential Test — Swap One Component

If still stuck after Steps 1–6, perform a differential test:
- Replace the cartoon face with a **photorealistic human face** and run the same pipeline → if lips move, the model can't handle cartoon faces.
- Replace the audio with a **known-good speech clip** → if lips move, the audio input was the problem.
- Replace the driving video with a **pre-made driving video with visible lip motion** → if the source video still shows closed mouths, the motion transfer stage is broken.

**Only change one variable at a time.** Each test should confirm or eliminate exactly one hypothesis.

---

### Phase 3: Automated Quality Verification

Apply these quantitative checks after applying a fix to confirm the defect is resolved.

#### SyncNet Lip-Sync Scoring
Quantify lip-sync quality without ground-truth video:
- **LSE-D** (Lip Sync Error - Distance): Lower = better. Pass threshold: < 7.0
- **LSE-C** (Lip Sync Error - Confidence): Higher = better. Pass threshold: > 5.0
- Install: `pip install syncnet-python`
- Run on 10–100 frame sliding windows for stability.

#### VMAF Video Quality
Measure visual quality regression after re-encoding:
```powershell
ffmpeg -i distorted.mp4 -i reference.mp4 -lavfi libvmaf -f null -
```
Flag segments where VMAF drops below 80. Use VMAF-CUDA for GPU-accelerated monitoring.

#### VFR Detection
The most reliable VFR detection method:
```powershell
ffmpeg -i input.mp4 -vf vfrdet -an -f null -
```
Parse stderr for `VFR:X.XXX` — any value > 0 indicates variable frame rate. ffprobe metadata is unreliable (reports nominal rate, not actual).

#### Cross-Correlation Offset Detection
Programmatically detect audio-video offset:
```python
import numpy as np
from scipy.signal import correlate

# Extract audio from both tracks, compute cross-correlation
correlation = correlate(audio_track_1, audio_track_2, mode='full')
lag = np.argmax(correlation) - len(audio_track_1) + 1
offset_ms = lag / sample_rate * 1000
print(f"Detected offset: {offset_ms:.1f}ms")
# ITU-R BT.1359: ±45ms acceptable, ±80ms annoying
```

#### Subtitle Timing Validation
- Auto-align with `ffsubsync` or `alass`.
- Validate: CPS (characters per second) ≤ 25, duration ≥ 0.7s, no overlapping cues.
- Match against platform specs (Netflix, YouTube).

## Pitfalls

- **"Verified" without transcription** — claiming the video is correct without transcribing and comparing spoken words against the audio track.
- **Retrying the same pipeline** — re-running an identical command expecting different results instead of diagnosing the root cause.
- **Trusting AI-claimed sync** — accepting lip-sync or subtitle alignment based on metadata alone without visual and auditory human verification.
- **Ignoring VFR** — concatenating variable-frame-rate clips and wondering why audio drifts. Always use `vfrdet` filter, not ffprobe nominal rate.
- **Oversized text defense** — "the text looks fine to me" without extracting a frame and measuring screen percentage.
- **Trusting logs over frames** — reading a log line that says "lip-sync complete, 133/133 frames processed" and claiming success without extracting a single frame from the output and visually confirming mouths are open.
- **Skipping intermediate outputs** — jumping from "the pipeline ran" to "the final video is wrong" without checking which stage's output first shows the defect.
- **Assuming code matches docs** — the walkthrough says the face coordinates were fixed, but the actual code may have a different bug (e.g., `kwargs` referenced in a non-kwargs method) that prevents the fix from ever executing.
- **Resolution-blind coordinate hardcoding** — using face detection coordinates tuned at one resolution across pipeline stages that operate at different resolutions.
- **Silent fallback acceptance** — not noticing that a pipeline stage caught an exception and silently returned the unmodified input instead of the processed result.
- **FFmpeg default stream selection** — relying on FFmpeg's automatic stream selection instead of explicit `-map` flags when inputs have multiple audio streams.
- **ffprobe VFR false negatives** — ffprobe reports the nominal frame rate, not the actual frame rate. Use the `vfrdet` filter for reliable VFR detection.

## Verification

### Diagnostic Checklist

Confirm each item before declaring the pipeline fixed:

- [ ] Failure stage localized (clip generation / lip-sync / subtitle timing / FFmpeg compilation).
- [ ] Raw clips inspected individually (before assembly) to isolate the faulty clip.
- [ ] Audio stream verified via FFprobe (codec, channels, bitrate all non-zero).
- [ ] Stream mapping confirmed in FFmpeg command (`-map 0:v:0 -map 1:a:0`).
- [ ] VFR checked using `vfrdet` filter and converted to CFR if detected.
- [ ] Spoken words transcribed and compared against target lyrics at 3+ timestamps.
- [ ] Subtitle timestamps compared against Whisper transcription of actual audio.
- [ ] Frame extracted and visually inspected for subtitle sizing and lip movement.
- [ ] **Multi-stage pipeline**: frames extracted and visually inspected at EVERY intermediate stage, not just the final output.
- [ ] **Multi-stage pipeline**: function signatures read and kwargs traced end-to-end through the call chain.
- [ ] **Multi-stage pipeline**: each stage tested in isolation to confirm it can produce the expected output independently.
- [ ] **Multi-stage pipeline**: coordinate systems verified across resolution transforms (widescreen ↔ vertical, crop offsets, scale factors).
- [ ] **Multi-stage pipeline**: audio segment loudness checked (mean_volume > -40 dB) to confirm non-silent input.

### Automated Quality Checklist

- [ ] VFR detected and converted to CFR using `vfrdet` filter.
- [ ] Audio loudness normalized to -16 LUFS (streaming) or -23 LUFS (broadcast).
- [ ] SyncNet LSE-D < 7.0 and LSE-C > 5.0 on lip-synced content.
- [ ] VMAF > 80 after any re-encode step.
- [ ] Audio offset < ±45ms (ITU-R BT.1359 guideline).
- [ ] Subtitle CPS ≤ 25 with no overlapping cues.
- [ ] Stream mapping confirmed (`-map 0:v:0 -map 1:a:0`).
- [ ] Frame extracted and visually inspected for layout.

### Quick Verification Commands

```powershell
# Verify audio stream is non-empty in final output
ffprobe -v error -select_streams a -show_entries stream=codec_name,channels,bit_rate -of default=noprint_wrappers=1 output.mp4

# Verify no VFR in final output
ffmpeg -i output.mp4 -vf vfrdet -an -f null - 2>&1 | Select-String "VFR"

# Extract verification frames
ffmpeg -y -i output.mp4 -ss 00:00:02 -vframes 1 -update 1 final_check_2s.png
ffmpeg -y -i output.mp4 -ss 00:00:12 -vframes 1 -update 1 final_check_12s.png

# Check audio loudness
ffmpeg -i output.mp4 -af "volumedetect" -f null - 2>&1 | Select-String "mean_volume"
```

## Related Skills

- **`hypothesis-driven-investigation`** — Localize the clip source using structured hypothesis testing.
- **`network-and-api-failure-triage`** — Check the API calls (Veo 3, model inference endpoints) when pipeline stages fail to fetch or generate.
- **`video-maker`** — Verify the fix with the Mandatory Media Verification Protocol (Section 10).
- **`audio-reactive-music-video`** — Reference for `auto_subtitle_generator.py` and subtitle generation workflow (Section 7B).
- **`lip-sync-agent`** — Reference for lip-sync re-sync pipeline (Section 4).
- **`google-flow-agent`** — Reference for Veo 3 speech-suppressed prompts (Section 5).
