---
name: multimedia-production-mastery
version: 1.2.1
description: "Automates music- and curve-driven video edits: librosa beat-sync, MoviePy 2.x time_transform ramps, FFmpeg zoompan easing, camera shake, and word-highlight .ass. Use when beats, easing math, or time-remap drive the cut. Not for plain trim/concat (ffmpeg-video-editing), format conversion (ffmpeg-format-conversion), or audio loudness (ffmpeg-audio-processing)."
category: media-automation
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-20
last_updated: 2026-07-01
trigger: "User asks to cut or transition video on music beats or onsets, build a speed ramp (fast -> slow-mo -> fast), animate smooth zoom/pan with easing curves, add bass-impact camera shake, or generate karaoke-style word-highlight subtitles."
action: "Run the matching bundled script (beat_sync.py, speed_ramp.py, subtitles_styled.py) or compose the documented MoviePy 2.x / FFmpeg recipe; apply the easing and time-remap formulas; enforce even output dimensions and close every clip handle."
exception: "Outputting odd-dimension video; leaving MoviePy clip handles open on Windows; applying atempo outside 0.5-2.0 without chaining; calling time_transform without restoring the clip duration."
not-triggered: "Format conversion, simple trims or concatenation, static image editing or graphic design, generative AI video creation, CapCut or other NLE project-file manipulation."
---

# Multimedia Production Mastery

Automation recipes, mathematical formulations, and Python/FFmpeg templates for edits that are *driven by a signal or a curve*: audio beats, easing functions, and time-remap profiles. The unit of work here is a computed timeline, not a manual cut.

## When to Use

Use this skill when one or more of the following are true:

- **Beat synchronization** — cutting or transitioning clips to align with the tempo, beats, or onsets of an audio track (librosa analysis feeding MoviePy/FFmpeg cuts).
- **Speed ramping** — smooth, non-linear acceleration/deceleration profiles (fast → slow-mo → fast) via time remapping.
- **Zoom & pan curves** — Ken Burns motion using sinusoidal or exponential ease-in/ease-out instead of robotic linear interpolation.
- **Camera shake** — procedural handheld or bass-impact shake generated from noise or onset strength.
- **Styled dynamic subtitles** — `.ass` files with word-by-word highlight colors, custom fonts, borders, and margins.
- **Pipeline orchestration** — wiring librosa + MoviePy 2.x + FFmpeg around pre-rendered clips (including AI-generated ones).

### When NOT to use — routing table

| Request | Route to |
|---|---|
| Cut, trim, join, or re-encode segments with no timing math | `ffmpeg-video-editing` |
| Constant-rate scale, crop, watermark, blur, or uniform speed change | `ffmpeg-video-filters` |
| Assemble finished clips, audio, and titles into a final deliverable | `video-assembly-pipeline` |
| Extract, normalise, or mix audio tracks | `ffmpeg-audio-processing` |
| Programmatic timeline edits inside CapCut Desktop drafts | `capcut-video-automation` |
| Container/format conversion with no timeline changes | `ffmpeg-format-conversion` |

## Prerequisites

### Python environment

All bundled scripts require the following packages in the active Python environment:

| Package | Version constraint | Purpose |
|---|---|---|
| `librosa` | ≥ 0.11 (tempo returns NumPy array) | Beat/onset detection |
| `moviepy` | **2.x only** — 1.x API is incompatible | Video composition, time remapping |
| `numpy` | any recent | Numerical integration, interpolation |
| `scipy` | any recent | `cumulative_trapezoid` for speed profiles |

Verify before running any script:

```powershell
python -c "import librosa, moviepy, numpy, scipy; print(librosa.__version__, moviepy.__version__)"
```

Expected output should show `moviepy` version starting with `2.`.

### FFmpeg

FFmpeg must be on `PATH`. Verify:

```powershell
ffmpeg -version
```

### Bundled scripts location

All scripts live in `scripts/` relative to this skill directory:

| Script | Purpose | Key flags |
|---|---|---|
| `beat_sync.py` | Detect beats/onsets in a track and cut a video (or stitch a clip folder) on them | `--audio` (req), `--video` \| `--dir`, `--output` (req), `--onset`, `--export-beats beats.json` |
| `speed_ramp.py` | Three-phase non-linear speed ramp | `--video` (req), `--output` (req), `--start-speed 2.0`, `--mid-speed 0.2`, `--end-speed 2.0`, `--ramp-start 0.2`, `--ramp-end 0.8` |
| `subtitles_styled.py` | Timed-words JSON → styled `.ass` with per-word highlights | `--input` (req), `--output` (req), `--font`, `--size`, `--color #RRGGBB`, `--highlight-color`, `--outline-color`, `--outline`, `--shadow`, `--alignment`, `--margin-v` |

### Bundled references

Load `references/effects-landscape.md` when the user asks about available AI-enhanced or classical video effects, their parameters, tooling, or underlying math — it is a catalog you can search for effect names and implementation details.

## Procedure

### Step 1 — Identify the driving signal

Determine what drives the edit:

| Signal | Tool | Script |
|---|---|---|
| Musical beats or tempo | `librosa.beat.beat_track` | `beat_sync.py` |
| Onsets (percussive/transient) | `librosa.onset.onset_detect` | `beat_sync.py --onset` |
| Custom speed curve | `scipy.integrate.cumulative_trapezoid` | `speed_ramp.py` |
| Easing curve for zoom/pan | FFmpeg `zoompan` with cosine easing | Recipe 1 below |
| Word timings for subtitles | External JSON (whisper or manual) | `subtitles_styled.py` |

### Step 2 — Run or compose the matching recipe

#### Recipe A: Beat-synced cut from a folder of clips

```powershell
python scripts/beat_sync.py --audio music.mp3 --dir .\raw_clips --output synced.mp4
```

Export detected beats for inspection or reuse:

```powershell
python scripts/beat_sync.py --audio music.mp3 --dir .\raw_clips --output synced.mp4 --export-beats beats.json
```

For sparse or syncopated tracks where beat tracking misses, use onset detection:

```powershell
python scripts/beat_sync.py --audio ambient.mp3 --dir .\raw_clips --output synced.mp4 --onset
```

#### Recipe B: Three-phase speed ramp (fast → slow-mo → fast)

```powershell
python scripts/speed_ramp.py --video in.mp4 --output ramped.mp4 --mid-speed 0.15
```

Full parameter control:

```powershell
python scripts/speed_ramp.py `
  --video in.mp4 `
  --output ramped.mp4 `
  --start-speed 2.0 `
  --mid-speed 0.2 `
  --end-speed 2.0 `
  --ramp-start 0.2 `
  --ramp-end 0.8
```

#### Recipe C: Word-highlight styled subtitles

Input JSON format (word-level timings, `highlight` flags the accent color):

```json
[
  { "start": 0.5, "end": 1.2, "text": "Welcome", "highlight": false },
  { "start": 1.8, "end": 3.0, "text": "Future!", "highlight": true }
]
```

Generate the `.ass` file:

```powershell
python scripts/subtitles_styled.py `
  --input words.json `
  --output subs.ass `
  --highlight-color "#00FFFF"
```

### Step 3 — Core formulas (reference when composing custom code)

#### Non-linear motion curves

**HARD RULE:** Never linearly interpolate zoom or pan — it reads as robotic. Use sinusoidal ease-in-out:

```
z(t) = z_start + (z_end - z_start) * (1 - cos(pi * t / d)) / 2
```

where `t` is current time, `d` the ease duration. To keep pixel `(x_f, y_f)` centered on a `W x H` frame while zooming by `z(t)`:

```
x(t) = x_f - W / (2 * z(t))
y(t) = y_f - H / (2 * z(t))
```

#### Time remapping (speed ramps)

Define `S(t)` = source time at output time `t`; the derivative `S'(t)` is the instantaneous speed multiplier. Build `S(t)` by integrating a speed profile.

- **MoviePy 2.x:** `clip.time_transform(time_func)` — the 1.x `fl_time` is gone. **HARD RULE:** `time_transform()` leaves the clip's duration undefined. Call `.with_duration(target)` immediately after, or output is truncated.
- **FFmpeg:** dynamic speed requires splitting into segments and applying `setpts` (video) + `atempo` (audio) per segment. **HARD RULE:** `atempo` only accepts `[0.5, 2.0]`; chain filters for anything outside (e.g. `atempo=2.0,atempo=2.0` for 4x, `atempo=2.0,atempo=1.5` for 3x).

#### ASS color formats

Two different hex conventions inside one file:

| Context | Format | Example |
|---|---|---|
| Style definitions (`[V4+ Styles]`) | `&HAABBGGRR` — 8 digits, no trailing `&` | `&H0000FFFF` = opaque yellow |
| Inline override tags | `\c&HBBGGRR&` — 6 digits, trailing `&`, no alpha | `{\c&H00FFFF&}` = yellow from here on |

**HARD RULE:** Alpha is **inverted** relative to RGBA: `00` = fully opaque, `FF` = fully transparent. Invisible text usually means `FF` (transparent) where `00` (opaque) was intended.

### Step 4 — FFmpeg recipes

#### Recipe 1: Jitter-free FFmpeg zoompan (Ken Burns)

`zoompan` evaluates positions in integer pixels, causing visible jitter at low zoom speeds. Pre-upscale to 4K first so the truncation error becomes sub-pixel:

```powershell
ffmpeg -i in.jpg -vf "scale=3840:-2,zoompan=z='1+0.5*(1-cos(PI*on/149))/2':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=150:fps=30:s=1920x1080" -c:v libx264 -pix_fmt yuv420p out.mp4
```

#### Recipe 2: The even-dimensions rule

**HARD RULE:** Most encoders (yuv420p especially) fail on odd width/height. After any crop or scale, force even dimensions:

```powershell
ffmpeg -i input.mp4 -vf "scale='trunc(iw/2)*2:trunc(ih/2)*2'" output.mp4
```

#### Recipe 3: MoviePy 2.x non-linear speed ramp (custom code)

Integrate a speed profile to get the time-remap function, then apply it:

```python
import numpy as np
from scipy.integrate import cumulative_trapezoid
from moviepy import VideoFileClip

src = VideoFileClip("in.mp4")
fps = src.fps
out_dur = 6.0
t_out = np.linspace(0, out_dur, int(out_dur * fps) + 1)

# Speed profile: fast -> slow -> fast
speed = 1.0 + 0.5 * (np.cos(2 * np.pi * t_out / out_dur) * 0.5 + 0.5)

# Integrate speed to get source timestamps for each output frame
s_src = np.clip(cumulative_trapezoid(speed, t_out, initial=0.0), 0, src.duration - 1e-3)
time_func = lambda t: float(np.interp(t, t_out, s_src))

ramped = src.time_transform(time_func).with_duration(out_dur)
ramped.write_videofile("out.mp4", fps=fps, audio=False)

src.close()
ramped.close()
```

#### Recipe 4: Proxy workflow for heavy footage

Validate cuts and beat alignment on a cheap proxy, render once on the original:

1. Generate proxy:
   ```powershell
   ffmpeg -i input.mp4 -vf scale=-2:720 -c:v libx264 -crf 20 -c:a copy proxy.mp4
   ```
2. Iterate timing/beat scripts against `proxy.mp4`.
3. Swap the source path back to the 4K original for the final render only.

### Step 5 — Onset fallback for difficult tracks

Standard beat tracking misses beats in sparse or heavily syncopated material. Fall back to onsets in custom code:

```python
onset_frames = librosa.onset.onset_detect(y=y, sr=sr, backtrack=True)
times = librosa.frames_to_time(onset_frames, sr=sr)
```

(`beat_sync.py --onset` does this automatically.)

## Pitfalls

1. **MoviePy duration reset** — `time_transform()` leaves the clip's duration undefined. Call `.with_duration(target)` immediately after, or output is truncated.
2. **ASS inverted alpha** — invisible text usually means `FF` (transparent) where `00` (opaque) was intended. Alpha is inverted relative to RGBA.
3. **atempo range** — multipliers outside `[0.5, 2.0]` silently fail unless chained (`atempo=2.0,atempo=1.5` for 3x, `atempo=2.0,atempo=2.0` for 4x).
4. **librosa tempo type** — `beat_track()` returns a NumPy array for tempo in librosa 0.11+; cast with `float()` before formatting.
5. **Beat tracking on ambient/vocal tracks** — standard beat tracking misses beats in sparse or heavily syncopated material. Use `--onset` flag or `librosa.onset.onset_detect` with `backtrack=True`.
6. **Windows file locks** — unclosed `VideoFileClip`/`AudioFileClip` handles keep files locked and crash subsequent runs. **HARD RULE:** Always `.close()` every clip before the script exits, including in error paths.
7. **Odd output dimensions** — yuv420p and most encoders fail on odd width/height. Always force even dimensions after any crop or scale operation.
8. **MoviePy 1.x vs 2.x API** — only use 2.x methods: `time_transform` / `with_duration` / `subclipped` / `with_audio`. The 1.x `fl_time` / `set_duration` / `subclip` methods do not exist in 2.x and will raise `AttributeError`.
9. **zoompan integer jitter** — `zoompan` evaluates positions in integer pixels. Without pre-upscaling to 4K, low zoom speeds produce visible jitter. Always pre-scale to a high resolution before `zoompan`.

## Verification

Run through this checklist before considering the task complete:

- [ ] **Environment check:** `librosa`, `moviepy` (2.x), `numpy`, and `scipy` import successfully:
  ```powershell
  python -c "import librosa, moviepy, numpy, scipy; print(librosa.__version__, moviepy.__version__)"
  ```
  Output must show `moviepy` version starting with `2.`.

- [ ] **MoviePy 2.x API only:** Only these methods are used: `time_transform` / `with_duration` / `subclipped` / `with_audio`. No 1.x `fl_time` / `set_duration` / `subclip` appears anywhere in the code.

- [ ] **Even dimensions:** Every scale/crop expression forces even output dimensions. Verify with:
  ```powershell
  ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=p=0 output.mp4
  ```
  Both width and height must be even numbers.

- [ ] **ASS color formats:** Inline ASS tags use 6-digit hex with trailing `&` (`\c&HBBGGRR&`); style lines use 8-digit `&HAABBGGRR`; alpha semantics are inverted (`00` = opaque, `FF` = transparent).

- [ ] **Clip handles closed:** All `VideoFileClip`/`AudioFileClip` handles are `.close()`d before the script exits. On Windows, verify no file locks remain by attempting to delete or rename the input file after the script finishes.

- [ ] **atempo within range:** Any `atempo` filter values are within `[0.5, 2.0]` or properly chained. Verify by inspecting the FFmpeg filtergraph string.

- [ ] **Output plays:** Quick sanity check:
  ```powershell
  ffprobe -v error -show_entries format=duration -of csv=p=0 output.mp4
  ```
  Duration should match the expected target duration (not the source duration for ramped clips).

## Related skills

- `ffmpeg-video-editing` — plain cut/trim/concat with no timing math
- `ffmpeg-video-filters` — constant-rate scale, crop, watermark, blur, uniform speed
- `video-assembly-pipeline` — stitching finished clips into a deliverable
- `ffmpeg-audio-processing` — audio extraction, normalisation, mixing
- `capcut-video-automation` — CapCut Desktop draft manipulation
- `ffmpeg-format-conversion` — container/format conversion with no timeline changes
