---
name: video-assembly
version: 1.1.1
description: "Assembles a final video from existing clips, audio, and subs with FFmpeg concat/amix/xfade/subtitles/loudnorm (Remotion only for complex motion). Use when combining production outputs, concatenating clips, or mixing/burning audio and captions. Not for generating the clips (ComfyUI/Flow), Remotion composition authoring (remotion-video), or Whisper transcription. Never concat mismatched codecs with -c copy."
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-14
---

## When to Use
- Combine multiple production outputs (video clips, audio files, subtitles) into a final deliverable.
- Final stage of the video production pipeline: concatenation, audio mixing, transitions, and format conversion.
- Trigger keywords: assemble video, combine clips, add audio, mix audio, burn subtitles, video transitions, format conversion, normalize audio.

## Prerequisites
- FFmpeg installed and available in system PATH.
- For complex compositions: Remotion and Node.js installed (delegate to `remotion-best-practices`).
- Windows host primary (PowerShell). Commands below use PowerShell syntax.

## Procedure

### Mode 1: FFmpeg (Simple, Fast)
Best for: Concatenation, audio mixing, basic transitions, format conversion.

#### 1. Concatenate Video Clips
```powershell
# Create file list (PowerShell)
"file 'clip1.mp4'" | Out-File -FilePath filelist.txt -Encoding ascii
"file 'clip2.mp4'" | Out-File -FilePath filelist.txt -Encoding ascii -Append
"file 'clip3.mp4'" | Out-File -FilePath filelist.txt -Encoding ascii -Append

# Concatenate (same codec/resolution)
ffmpeg -f concat -safe 0 -i filelist.txt -c copy output.mp4

# Concatenate (different codecs/resolutions - re-encode)
ffmpeg -f concat -safe 0 -i filelist.txt -vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2" -c:v libx265 -crf 23 -preset medium -c:a aac -b:a 192k output.mp4
```

#### 2. Add Audio to Video
```powershell
# Replace audio
ffmpeg -i video.mp4 -i audio.wav -c:v copy -c:a aac -map 0:v:0 -map 1:a:0 output.mp4

# Mix audio (keep original + add music)
ffmpeg -i video.mp4 -i music.mp3 -filter_complex "[0:a][1:a]amix=inputs=2:duration=first:dropout_transition=3" -c:v copy output.mp4

# Add audio with volume control
ffmpeg -i video.mp4 -i bgm.mp3 -filter_complex "[1:a]volume=0.3[bg];[0:a][bg]amix=inputs=2:duration=first" -c:v copy output.mp4
```

#### 3. Add Subtitles
```powershell
# Burn subtitles (SRT file)
ffmpeg -i video.mp4 -vf "subtitles=subs.srt:force_style='FontName=Arial,FontSize=24,PrimaryColour=&HFFFFFF,OutlineColour=&H000000,Outline=2'" -c:a copy output.mp4

# Burn subtitles (ASS file for styled)
ffmpeg -i video.mp4 -vf "ass=subs.ass" -c:a copy output.mp4
```

#### 4. Transitions Between Clips
```powershell
# Crossfade (2 second transition) - PowerShell line continuation
ffmpeg -i clip1.mp4 -i clip2.mp4 -filter_complex `
  "[0:v]trim=0:5,setpts=PTS-STARTPTS[v0]; `
   [1:v]trim=0:5,setpts=PTS-STARTPTS[v1]; `
   [v0][v1]xfade=transition=fade:duration=2:offset=3[outv]" `
  -map "[outv]" output.mp4
```

#### 5. Extract/Manipulate Frames
```powershell
# Extract frames
ffmpeg -i video.mp4 -vf "fps=1" frames/frame_%04d.png

# Create video from frames
ffmpeg -framerate 24 -i frames/frame_%04d.png -c:v libx265 -crf 23 -preset medium -pix_fmt yuv420p output.mp4

# Speed up/slow down
ffmpeg -i video.mp4 -filter:v "setpts=0.5*PTS" -filter:a "atempo=2.0" fast.mp4   # 2x speed
ffmpeg -i video.mp4 -filter:v "setpts=2.0*PTS" -filter:a "atempo=0.5" slow.mp4   # 0.5x speed
```

#### 6. Format Conversion
```powershell
# MP4 (H.265) - universal compatibility
ffmpeg -i input.mov -c:v libx265 -crf 23 -preset medium -c:a aac -b:a 192k output.mp4

# WebM (VP9) - web delivery
ffmpeg -i input.mp4 -c:v libvpx-vp9 -crf 30 -b:v 0 -c:a libopus output.webm

# GIF (short clips)
ffmpeg -i input.mp4 -vf "fps=15,scale=480:-1:flags=lanczos" -loop 0 output.gif
```

#### 7. Audio Normalization
```powershell
# Normalize to -16 LUFS (YouTube standard)
ffmpeg -i input.mp4 -af "loudnorm=I=-16:TP=-1.5:LRA=11" -c:v copy output.mp4

# Two-pass normalization (more accurate)
ffmpeg -i input.mp4 -af loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json -f null -
# Read measured values from JSON output, then apply:
ffmpeg -i input.mp4 -af "loudnorm=I=-16:TP=-1.5:LRA=11:measured_I=-20:measured_TP=-2:measured_LRA=8:measured_thresh=-30" -c:v copy output.mp4
```

### Mode 2: Remotion (Complex Compositions)
Best for: Animated captions, data visualizations, complex motion graphics, React-based templates.
Delegate to `remotion-best-practices` skill for guidance.

**Use Remotion when:**
- Animated text/captions needed
- Data visualizations in video
- Complex motion graphics
- Programmatic/template-based video generation
- React-based UI elements as video overlays

**Pass to Remotion:**
- Clip paths and timings
- Text content and styles
- Animation specifications
- Output format requirements

### Quality Presets

| Use Case | CRF | Resolution | Notes |
|----------|-----|------------|-------|
| Master/Archive | 15-17 | Original | Large files, best quality |
| YouTube Upload | 18-20 | 1920x1080 | Good balance |
| Social Media | 20-23 | 1080x1920 (vertical) | Smaller files |
| Preview/Draft | 25-28 | 1280x720 | Quick review |

### Assembly Pipelines

#### Standard Video
1. Gather clips from `comfyui-video-pipeline` outputs.
2. Gather audio from `comfyui-voice-pipeline` outputs.
3. Normalize audio levels (-16 LUFS for YouTube).
4. Trim/arrange clips to match script timing.
5. Add transitions between clips (if multiple).
6. Add background music (optional, lower volume).
7. Add subtitles (if applicable).
8. Export in target format.

#### Talking Head Video
1. Lip-synced video from `comfyui-voice-pipeline`.
2. Add intro/outro (if applicable).
3. Add lower thirds or name cards.
4. Add background music at -20dB below speech.
5. Normalize speech to -16 LUFS.
6. Export.

#### Tutorial/Walkthrough
1. Screen recordings + talking head overlay.
2. Use Remotion for animated annotations.
3. Add chapter markers.
4. Add subtitles (auto-generate from audio).
5. Export with chapters embedded.

## Pitfalls
- **Do not use for initial video generation or AI clip creation** (use `comfyui-video-pipeline`).
- **Do not use for voice synthesis** (use `comfyui-voice-pipeline`).
- **Do not use for complex 3D rendering or high-end VFX** that requires a dedicated NLE (Non-Linear Editor) like DaVinci Resolve or Premiere Pro, unless the requirements can be met via Remotion.
- **Avoid using deprecated FFmpeg filters and codecs.** Always check the latest FFmpeg documentation for updates and best practices.
- **Be cautious with FFmpeg's `concat` demuxer**, as it can be unstable with certain file formats. Prefer using the `concat` filter for more robust concatenation.
- **Ensure that all input files are properly encoded and compatible** with the chosen FFmpeg or Remotion workflow to avoid unexpected errors or quality issues.
- **PowerShell line continuations**: Use backtick (`` ` ``) instead of backslash (`\`) for multi-line FFmpeg commands in PowerShell.

## Verification
- [ ] Run `ffmpeg -i output.mp4` to verify stream integrity and resolution.
- [ ] Check audio levels to ensure normalization to -16 LUFS.
- [ ] Verify that no black frames exist at cut points.
- [ ] Confirm subtitles are correctly timed and burned in.
- [ ] Validate that the final file size is within the target platform's limits.
- [ ] Ensure all input files are compatible and properly encoded.
- [ ] Test the final video on the target platform to ensure compatibility and performance.

## Related skills
- `comfyui-video-pipeline`
- `comfyui-voice-pipeline`
- `remotion-best-practices`
