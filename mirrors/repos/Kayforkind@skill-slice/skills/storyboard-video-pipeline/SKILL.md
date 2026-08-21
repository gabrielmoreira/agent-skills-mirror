---
name: storyboard-video-pipeline
description: "Assembles a final cut from a storyboard manifest plus per-shot clips and audio: timed concat, audio mux, SRT burn, and verification frames via ffmpeg. Use when the request names manifest, clips, and audio together and asks to stitch, mux, or burn. Not for bare concat or mux without a manifest, generative T2V prompting, or NLE timeline editing; never treat cmd /c as safe for filter_complex on Windows."
version: 1.0.1
---

## When to Use

Trigger this skill when the user's request names **all three** inputs together — a storyboard manifest (`storyboard.json` or equivalent), per-shot clip files, and one or more audio tracks — and asks for assembly, stitching, muxing, burning subtitles, or producing a final video from a storyboard.

**Do not trigger** on bare "concat these clips" or "mux this audio" requests that lack a manifest. Those are simpler ffmpeg tasks that don't need the five-stage pipeline described here.

Typical trigger phrases: "assemble the storyboard," "stitch the shots with the narration," "burn the captions into the storyboard video," "mux the music bed onto the storyboard cut."

## Prerequisites

- **ffmpeg** and **ffprobe** installed and on `PATH`. Verify with `ffmpeg -version` and `ffprobe -version`.
- **Python 3.8+** (recommended) or PowerShell 5.1+ for orchestration glue — manifest parsing, SRT generation, and the verification report require JSON support and timestamp arithmetic. Bash/batch loops are acceptable only for building `list.txt` from a directory listing; the moment you parse JSON or compute timestamps, switch to Python or PowerShell.
- **Windows host is primary.** All commands below are PowerShell-compatible. Simple ffmpeg invocations through `cmd /c` are fine, but any command containing `-filter_complex` or a `-vf` with commas must be invoked with an argv array (Python `subprocess.run([...])`, PowerShell splatting) — `cmd /c` mangles filter-graph escaping (commas, colons, quotes).
- **Disk space.** Long renders can produce tens of GB in the working directory. Confirm adequate free space before starting.
- **zscale filter** (only if HDR tonemapping is needed): run `ffmpeg -filters | findstr zscale` first. If missing, point the user at a full ffmpeg build (e.g., a gyan.dev full release, not essentials) before continuing.

## Procedure

### The core decision: what is authoritative

By default the **manifest is the source of truth for timing**, and clips and subtitles are conformed to it. This prevents three failure modes that naive `ffmpeg -f concat` pipelines produce: codec/fps drift across clips, encoded-vs-manifest duration mismatch, and subtitle drift between manifest-authored cues and cut-authored clips.

**Invert this default when:**

- The user explicitly says clip durations are authoritative (e.g., already cut in an NLE).
- The manifest predates the latest clip renders and the user has been editing in a timeline since.
- **Detection heuristic:** if encoded durations are all close to integer multiples of `1/fps` and the manifest durations are round seconds (`3.0`, `4.5`, `1.0`), the manifest is probably the outline and the clips are the cut — confirm with the user before inverting.

When inverted: build the SRT from encoded durations, skip the Stage 1 trim/pad step, but still normalize codec/pix_fmt/fps so Stage 2 can stream-copy.

### Working directory and resumability

Write all intermediate artifacts to `./_pipeline_work/` (override if the user specifies). Layout:

```
_pipeline_work/
  manifest.snapshot.json  # frozen copy of the manifest used for this run
  probe/                  # per-clip ffprobe JSON
  normalized/             # Stage 1 outputs, named shot_{NN}.mp4
  concat.mp4              # Stage 2 output
  muxed.mp4               # Stage 3 output
  subtitles.srt           # Stage 4 output
  verification/           # Stage 5 frames
  verification_report.md
```

To resume after a failure, check which outputs already exist and skip stages whose outputs are newer than their inputs. **Critical caveat:** the manifest is an input to every stage. Compare `manifest.snapshot.json` to the current manifest before resuming — if they differ, invalidate everything downstream of normalize (re-run Stages 1–5). If the manifest is unchanged, the standard newer-than-input check is enough — don't re-normalize clips just to regenerate subtitles.

Ask once at the end whether to keep or delete `_pipeline_work/`.

### Preflight (before any encoding)

Validate everything below in one pass and batch every ambiguity into a single round of questions rather than asking shot-by-shot.

**1. Manifest parses and durations resolve.**

Pick the duration key by priority: `duration_s` → `duration` → `length` → `seconds`. If multiple are present on one entry and disagree, ask.

Duration type normalization — accept and normalize all of:

- Numeric seconds: `3.5` → `3.5`
- String with unit: `"3.5s"`, `"500ms"` → parse and convert
- Timecode: `"00:00:03.500"`, `"00:00:03;15"` (semicolon = drop-frame) → seconds
- ISO 8601 duration: `"PT3.5S"`, `"PT1M30S"` → seconds
- Rational frame counts: `"105/30"` or `{"num": 105, "den": 30}` → seconds

Sanity-check units on raw numerics: if any value > 600, the field is probably milliseconds (confirm, then divide by 1000); if values are small integers ≤ 120 and the manifest carries an `fps` field, they may be frame counts (convert via `frames / fps`).

**Sub-frame and zero durations.** A shot with `duration < 1/fps` is almost always a manifest bug — flag it. Cues under 500ms are unreadable as subtitles and Stage 5's `start + duration − 0.100s` boundary frame goes negative; clamp the boundary extract to `start + duration/2` for sub-200ms shots, and in Stage 4 merge the cue with its neighbor when `duration < 0.5s`.

**2. Every shot maps to a clip file or a synthesis directive.**

Common mappings: `shot.clip`, `shot.file`, `shot.path`, or `shot.id` → `clips/{id}.{ext}`. Shots with no clip but with a `text` / `color` / `placeholder: true` field are synthesized in Stage 1. Shots with neither are a fatal manifest bug — stop and report.

**3. Total manifest duration vs. total audio length.**

Compute `Δ = audio_seconds − Σ shot_durations`:

- `|Δ| ≤ 0.5s`: proceed silently.
- `0.5s < |Δ| ≤ 2.0s`: proceed; note in the final summary. Stage 3's length branch handles it.
- `|Δ| > 2.0s`: fatal. Almost always a unit error or a missing shot. Report and stop.

**4. Resolve the output frame size.**

Aspect alone is not enough. Resolve in this order:

1. Manifest `resolution` field (`"1920x1080"`, `"1080x1920"`) — use as-is.
2. Manifest `aspect` + an explicit target (`target: "1080p"`, `target: "4K"`) — combine them.
3. **Implicit rule when only aspect is given:** default to 1080p — `1920×1080` for landscape (16:9), `1080×1920` for vertical (9:16), `1080×1080` for square — unless every probed clip is smaller, in which case match the smallest probed clip's nominal resolution. This avoids both upscaling proxies and shipping unnecessarily large renders.
4. Mixed-aspect clips: take the manifest aspect as authoritative; Stage 1's pad filter letterboxes the rest.
5. No signal anywhere: ask. Do not silently default to 1920×1080.

**5. Output path won't clobber a render the user still needs.**

Check existence. If the path exists and was modified in the last 24 hours, ask before overwriting. If it exists and is older, mention it in your summary and overwrite. If it doesn't exist, proceed.

**What is a "broken manifest" worth stopping on:**

Missing `duration` on any shot, missing clip mapping with no synthesis directive, unit error, audio/video mismatch > 2.0s, or duration values that fail every parser in the type-normalization list. Missing optional fields (`text`, transitions, styling hints) are recoverable — emit empty cues or default behavior and note it once.

### Stage 1 — Probe and normalize clips

1. Run `ffprobe -v error -print_format json -show_streams -show_format {file}` per clip and save the JSON to `_pipeline_work/probe/`. Parse from JSON; stderr text isn't a stable interface across ffmpeg versions and OSes.
2. For large manifests (50+ shots), run ffprobe in parallel (bounded to ~8 workers). Don't parallelize the normalize step — libx264 already uses all cores.
3. From each probe, flag:
   - **Variable frame rate** (`avg_frame_rate ≠ r_frame_rate`, or `nb_frames` inconsistent with `duration × fps`). Forces `-vsync cfr` during normalization.
   - **HDR / wide gamut** (`color_transfer` in `smpte2084`, `arib-std-b67`). The default `yuv420p` will crush HDR to washed-out SDR — warn the user and offer a tonemap only if they ask. Tonemap options: `hable` (broadcast-safe default), `mobius` (preserves highlights better), `reinhard` (softest rolloff). Full chain: `zscale=t=linear:npl=100,tonemap=hable,zscale=p=bt709:t=bt709:m=bt709,format=yuv420p`. **Build caveat:** `zscale` requires libzimg, which isn't in every ffmpeg build. Run `ffmpeg -filters | findstr zscale` first; if missing, point the user at a full build before continuing.
   - **Encoded duration vs. manifest duration.** Record `Δ = encoded − manifest` per shot for the verification report.
4. Normalize every clip to a common profile so Stage 2 can stream-copy. The concat demuxer requires matching `codec`, `pix_fmt`, `resolution`, `sar`, and `timebase`:

   ```
   -c:v libx264 -pix_fmt yuv420p -r 30 -vsync cfr \
     -vf "scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,setsar=1" \
     -video_track_timescale 30000 \
     -c:a aac -ar 48000 -ac 2
   ```

   The `pad` filter letterboxes mixed-aspect inputs — almost always what a storyboard cut wants. Override fps or codec only if the user has stated a target.

5. Conform each clip's *duration* to the manifest:
   - **Encoded longer than manifest**: trim with `-t {manifest_duration}`.
   - **Encoded shorter than manifest by `Δ`, where `Δ ≤ min(1.0s, 0.25 × manifest_duration)`**: freeze the last frame with `tpad=stop_mode=clone:stop_duration={Δ}`. Don't loop — loops create visible jumps.
   - **Shorter by more than that**: stop and report. Freeze-padding 6 seconds onto a 1s clip looks broken; the user needs the chance to fix the clip or the manifest.

6. **Clip audio.** Encode normalized clips muted (`-an`) by default, unless the user has asked for diegetic clip audio or the manifest carries a `keep_audio: true` per-shot flag. Reason: when Stage 3 muxes an external narration/music track over kept clip audio, the two often phase-cancel on shared frequencies or create unintended ducking. If retention is requested, encode at the same `-ar 48000 -ac 2` profile so the Stage 3 `amix` has uniform inputs.

7. **Synthesizing missing clips** (placeholder / color / text shots). Use `lavfi` sources, then run through the same normalization profile:
   - Color or black card: `-f lavfi -i color=c={color or black}:s={W}x{H}:r=30 -t {duration}`
   - Text card: append `-vf "drawtext=text='{escaped text}':fontsize=72:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2"`
   - Synthesized clips need a silent audio track if any sibling clip retained audio: `-f lavfi -i anullsrc=channel_layout=stereo:sample_rate=48000`

8. **"Not normalizable" — when Stage 2 falls back to the concat filter.** A clip libx264 can't decode in this build (rare today), or a profile where re-encoding to baseline H.264 visibly degrades it and the user has flagged preservation — ProRes 4444, DNxHR HQX, 10-bit HEVC HDR with the tonemap declined. In practice the only frequent case is the HDR-declined path. Treat everything else as normalizable.

### Stage 2 — Concatenate

1. If Stage 1 fully normalized every clip — meaning all five fields (`codec`, `pix_fmt`, `resolution`, `sar`, `timebase`) match across the set — use the concat **demuxer** for a fast, lossless join:

   ```
   ffmpeg -f concat -safe 0 -i list.txt -c copy concat.mp4
   ```

2. If some inputs couldn't be normalized, fall back to the concat **filter** for the holdouts and demuxer-concat the rest in groups, producing one or more intermediate `group_NN.mp4` files that are then demuxer-concatenated at the top level. **Don't mix the two approaches inside a single ffmpeg invocation:** stream-mapping demuxer-copied streams alongside filter outputs requires manually tracking input stream indices through `-map` flags, and the timestamps from the two paths use different reference points, so the join glitches by a frame or two at every transition. Two-pass grouping sidesteps both problems.

3. For very long manifests (200+ shots), check `list.txt` doesn't exceed the ffmpeg input line limit and that paths are quoted with `file '...'` syntax. If a fallback path ends up passing every clip as a separate `-i`, Windows `CreateProcess` caps the command line at ~32 KB.

### Stage 3 — Mux audio

**Single external track:**

```
ffmpeg -i concat.mp4 -i {audio} -c:v copy -c:a aac -shortest muxed.mp4
```

- **Audio longer than video**: `-shortest` is correct; trim the tail.
- **Audio shorter than video**: do **not** use `-shortest` — it would clip the last shot. Pad audio instead: `-af "apad" -t {video_duration}`.
- **Within 0.1s (3 frames at 30fps)**: both paths work, but `-shortest` will drop up to 3 frames off a held title card or freeze frame on the last shot. If the last shot is a freeze (`tpad` in Stage 1) or low-motion hold longer than 2s, prefer the `apad` path; otherwise `-shortest` is fine.

**Multiple tracks** (narration + music bed + SFX, etc.). Only include `amix` inputs for tracks the user actually supplied — adding a silent placeholder input isn't a level problem, but `duration=longest` will extend the mix to match the placeholder and `dropout_transition` will ramp the live channels when an input ends, both audible. Example for narration + bed + sfx:

```
-filter_complex "[1:a]volume=0.3[bed];[2:a]volume=0.8[sfx];[0:a][bed][sfx]amix=inputs=3:duration=longest:dropout_transition=2[outa]"
```

Default mix weights: narration 1.0, music bed 0.3, SFX 0.8 — tune per user input, and let manifest-level `volume` fields override these. If clip audio was retained in Stage 1, add the concat video's audio as an additional `amix` input.

**Channel layout and sample rate.** Resample/remix mismatched inputs to a common `48000 Hz / stereo` profile via `aresample=48000` and `pan=stereo|c0=c0|c1=c1` (or `c0=c0|c1=c0` for mono → stereo). 5.1/7.1 narration is unusual; if the user supplies one, downmix to stereo with `pan=stereo|FL<FL+0.5*FC+0.7*BL|FR<FR+0.5*FC+0.7*BR` unless they ask to preserve surround.

**Loudness normalization.** Not applied by default — many users tune the mix by ear and `loudnorm` will undo it. Offer `loudnorm=I=-14:TP=-1.5:LRA=11` (common streaming target, ~-14 LUFS integrated) only if the user mentions a delivery target or asks for normalization. Single-pass `loudnorm` is approximate; mention two-pass if they need precision.

Record in the verification report which length branch ran (audio-padded vs `-shortest`-trimmed), which inputs were mixed, and the final muxed duration.

### Stage 4 — Subtitles

1. Generate the SRT by accumulating manifest durations to compute `start` and `end` per entry. Authoring against the same clock the video was conformed to is what eliminates drift by construction.
2. Caption field priority: `text` → `caption` → `narration` → `subtitle`. For entries with no caption text, emit a single-space cue (`" "`) at the correct timing rather than collapsing the entry — collapsing shifts every following cue out of sync with the video. The ffmpeg `subtitles` filter occasionally drops truly empty cues and renumbers, which is the silent-shift failure mode to avoid.
3. **Minimum cue duration.** Cues under 500ms are unreadable. Where the manifest produces a sub-500ms cue, merge it with the neighbor (prepend or append the text to whichever side has slack and the same speaker/context) and note the merge in the verification report.
4. **Escaping.** SRT is *not* HTML, and renderer support for HTML-ish tags is inconsistent. Default to **no escaping** for plain text. Only escape `<` → `&lt;` and `&` → `&amp;` if you are emitting styling tags and the literal characters would be mis-parsed.
5. Normalize whitespace, strip control characters (U+0000–U+001F except `\n`), and convert tabs to spaces.
6. **Line wrapping.** Default to 2 lines max, ~42 chars per line — social-media/broadcast safe range. If the user has a specific delivery spec, use it: Netflix is 42, YouTube ingest tolerates up to 84, EBU broadcast is 32–37. If a cue exceeds the limit and its duration allows (~1.5s minimum per split), split into consecutive cues; otherwise wrap and accept that some platforms will overflow.
7. **Detect stale user-supplied SRT.** If the user supplies their own SRT/ASS, parse it and accumulate cue end-times. If the final cue ends more than 1.0s from `Σ shot_durations`, the SRT is almost certainly cut against a different timeline — flag and ask before muxing. Otherwise, skip generation and use theirs.
8. **Delivery modes:**
   - **Sidecar SRT** (default): write `_pipeline_work/subtitles.srt` and copy it beside the final video. Non-destructive and editable.
   - **Burned-in**: `-vf "subtitles=subtitles.srt:force_style='FontName=...,FontSize=...,Outline=2'"`. Re-encodes the video stream at default CRF — visually near-identical but not bit-exact — and is slower. Default to sidecar; burn when the user asks or the target (e.g., social feeds without sidecar support) requires it.

### Stage 5 — Verification frames

1. For each shot, extract three JPEGs into `_pipeline_work/verification/`:
   - `shot_{NN}_mid.jpg` at `start + duration/2` — confirms the right clip landed in the right slot.
   - `shot_{NN}_end.jpg` at `start + duration − 0.100s` (clamped to `start + duration/2` for sub-200ms shots) — last visible frame of the shot.
   - `shot_{NN+1}_start.jpg` at `start_of_next` — first visible frame after the cut.

   Midpoints catch wrong-clip-in-slot errors; boundaries catch right-clip-but-wrong-trim errors. Both kinds happen, and they look identical during casual playback scrubbing.

2. Extract command:

   ```
   ffmpeg -ss {timestamp} -i muxed.mp4 -frames:v 1 -q:v 2 {out}.jpg
   ```

   Pre-input seek (`-ss` before `-i`) is fast and frame-accurate on `muxed.mp4`, because Stage 3 produces an unfragmented MP4 with the `moov` box upfront. Fall back to post-input seek (`-ss` after `-i`) only if a verification frame visibly differs from the expected content during a spot-check.

3. `-q:v 2` is high quality (~95% JPEG). A 100-shot manifest produces 300 JPEGs (~30–80 MB total at 1080p); use `-q:v 5` (~70% quality, ~10–25 MB) when the verification directory size matters or for preview-mode renders.

4. Write `verification_report.md` with one row per shot: index, clip filename, manifest duration, encoded duration, drift `Δ`, subtitle cue text, and links to the three frames. Header section: target resolution/fps, total duration, audio branch taken (Stage 3), subtitle mode (sidecar vs burned), any deviation from defaults, and a flagged list of every shot with `|Δ| > 0.1s`. Drift is mentioned in one place — this report — and the end-of-run summary just points at it.

### When to deviate

Most deviations are covered inline above. The cross-cutting ones:

- **Clip durations authoritative.** Triggered by explicit user statement or the detection heuristic in "The core decision." Build the SRT from encoded durations and skip the Stage 1 trim/pad step (but still normalize codec/pix_fmt/fps).
- **Quick draft or preview render.** Skip Stage 1's per-clip normalization (use the concat filter directly in Stage 2), drop the encode to `-crf 28 -preset veryfast -vf scale=-2:720`, and reduce Stage 5 to one midpoint frame per shot (not three) — the safety net still catches the highest-cost error class (wrong clip in slot) even for drafts. Label the output filename clearly (e.g., `_preview.mp4`) so the user doesn't ship a proxy.
- **Transitions.** This pipeline assumes hard cuts. If the manifest specifies `transition: {type, duration}` per shot, use `xfade` in Stage 2 (concat-filter path). Crossfades need overlap material, so in Stage 1 *do not* trim the outgoing clip to its manifest duration — leave the last `transition_duration` seconds intact and feed `xfade` an `offset = manifest_duration − transition_duration`. The post-transition timeline shrinks by `Σ transition_durations`; re-derive subtitle timings against that shorter timeline.

State any deviation in the final summary so the user can push back if your judgment was wrong.

### What to report when done

Keep it terse — the verification report has the detail:

- Output video path and duration.
- Subtitle path and whether burned in.
- Verification report path.
- Count of shots flagged with `|Δ| > 0.1s` (one line; the report lists them).
- Any deviation taken (proxy mode, aspect/resolution override, audio branch, transitions, retained clip audio, clip-durations-authoritative, etc.).

## Pitfalls

- **Don't parse ffprobe stderr.** Use `-print_format json` and parse the JSON. Stderr text isn't a stable interface across ffmpeg versions and OSes, and you'll waste an hour debugging a regex that worked yesterday.
- **Don't mix concat demuxer and concat filter in a single ffmpeg invocation.** Stream-mapping demuxer-copied streams alongside filter outputs requires manually tracking input stream indices through `-map` flags, and timestamps from the two paths use different reference points — the join glitches by a frame or two at every transition. Use two-pass grouping instead.
- **Don't loop short clips to pad duration.** Loops create visible jumps. Use `tpad=stop_mode=clone:stop_duration={Δ}` to freeze the last frame instead.
- **Don't freeze-pad more than `min(1.0s, 0.25 × manifest_duration)`.** Freeze-padding 6 seconds onto a 1s clip looks broken. Stop and report instead.
- **Don't collapse empty subtitle cues.** Emit a single-space cue (`" "`) at the correct timing. Collapsing shifts every following cue out of sync with the video. The ffmpeg `subtitles` filter occasionally drops truly empty cues and renumbers.
- **Don't add silent placeholder inputs to `amix`.** `duration=longest` will extend the mix to match the placeholder and `dropout_transition` will ramp the live channels when an input ends — both audible artifacts.
- **Don't use `-shortest` when audio is shorter than video.** It clips the last shot. Use `-af "apad" -t {video_duration}` instead.
- **Don't use `cmd /c` for commands with `-filter_complex` or `-vf` containing commas.** `cmd /c` mangles filter-graph escaping. Use Python `subprocess.run([...])` or PowerShell splatting with an argv array.
- **Don't apply `loudnorm` by default.** Many users tune the mix by ear and `loudnorm` will undo it. Only offer it if the user mentions a delivery target.
- **Don't silently default to 1920×1080.** If there's no resolution signal anywhere in the manifest or clips, ask the user.
- **Don't re-normalize clips on resume just to regenerate subtitles.** If the manifest is unchanged, the standard newer-than-input check is enough. Only invalidate downstream stages if `manifest.snapshot.json` differs from the current manifest.
- **HDR will be crushed by default `yuv420p`.** Warn the user before normalizing HDR/wide-gamut content. Offer tonemapping only if they ask, and verify `zscale` is available first.
- **Windows `CreateProcess` command line cap (~32 KB).** If a fallback path passes every clip as a separate `-i`, very long manifests can exceed this limit.

## Verification

After the pipeline completes, verify the outputs:

1. **Check final video exists and has expected duration:**

   ```
   ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 _pipeline_work/muxed.mp4
   ```

   Compare to `Σ shot_durations` (adjusted for any transitions). Mismatch > 0.1s indicates a Stage 2 or Stage 3 issue.

2. **Check subtitle file has correct cue count:**

   ```powershell
   (Get-Content _pipeline_work/subtitles.srt | Select-String "^\d+$").Count
   ```

   Should equal the number of shots with caption text (or all shots if using single-space cues for empty entries).

3. **Check verification frames exist:**

   ```powershell
   (Get-ChildItem _pipeline_work\verification\*.jpg).Count
   ```

   Should be `3 × shot_count` (or `1 × shot_count` in preview mode).

4. **Spot-check boundary frames.** Open `shot_{NN}_end.jpg` and `shot_{NN+1}_start.jpg` for a few shots — they should show the last frame of shot NN and the first frame of shot NN+1 respectively. If they show the wrong content, the clip ordering or trim is wrong.

5. **Review the verification report.** Open `_pipeline_work/verification_report.md` and check:
   - Every shot with `|Δ| > 0.1s` is flagged.
   - The audio branch taken (padded vs `-shortest`) is recorded.
   - Subtitle mode (sidecar vs burned) is recorded.
   - Any deviations from defaults are listed.

6. **If burned-in subtitles, verify they render.** Open `muxed.mp4` and confirm captions are visible at the expected timestamps. If sidecar, open the video in a player that supports external SRT (mpv, VLC) and confirm cue timing.

## Examples

### Worked example — mixed inputs

A manifest combining a clean clip, a clip needing freeze-pad, a synthesized text card, mixed duration types, and a multi-track mix:

```json
{
  "fps": 30,
  "aspect": "9:16",
  "shots": [
    {"id": "01", "clip": "clips/01.mp4", "duration_s": 3.0, "text": "Hook line."},
    {"id": "02", "clip": "clips/02.mp4", "duration_s": "PT4.5S", "text": "Beat two."},
    {"id": "03", "placeholder": true, "text": "Coming soon", "duration_s": 2.0}
  ],
  "audio": [
    {"path": "narration.wav", "role": "narration"},
    {"path": "bed.mp3", "role": "music", "volume": 0.25}
  ]
}
```

With these inputs the pipeline:

1. Probes clips 01 and 02. Clip 02 is encoded at 4.2s — within the freeze-pad window (`Δ = 0.3s ≤ min(1.0s, 1.125s)`), so Stage 1 freezes its last frame for 0.3s. The `"PT4.5S"` ISO 8601 string is normalized to `4.5` during preflight.
2. Synthesizes shot 03 as a 2.0s black card with the centered text "Coming soon" via `lavfi color` + `drawtext`, plus a `lavfi anullsrc` silent stereo track to keep `amix` symmetric.
3. Normalizes all three to 1080×1920 (vertical 9:16, default 1080p sizing), 30 fps, yuv420p, 48 kHz stereo.
4. Demuxer-concatenates into `concat.mp4` (9.5s).
5. Muxes narration + music bed via `amix` with weights `1.0` and `0.25` (the manifest specified the music level, overriding the 0.3 default). Stage 3 picks the audio length branch based on the longer of the two inputs and records the choice.
6. Generates `subtitles.srt`:

   ```
   1
   00:00:00,000 --> 00:00:03,000
   Hook line.

   2
   00:00:03,000 --> 00:00:07,500
   Beat two.

   3
   00:00:07,500 --> 00:00:09,500
   Coming soon
   ```

7. Extracts 9 verification JPEGs and writes the report, flagging shot 02's 0.3s freeze in the drift column.
