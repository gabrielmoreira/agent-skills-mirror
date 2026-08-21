---
name: local-lipsync-pipeline
description: "Chains local-GPU lip-sync for stylized or non-photoreal faces (anime, cartoons, CG avatars, puppets, VTubers): Wav2Lip, MuseTalk, LivePortrait, SadTalker, GFPGAN/CodeFormer paste-back, detector fallbacks, feathered mouth composite, CFR conform, and FFmpeg remux. Use when a real-face detector rejects stylized input, jaw clips, mouth seams, audio drift, or VRAM OOMs while chaining models. Not for photoreal talking-head SaaS or generic ffmpeg without sync; never load Wav2Lip, MuseTalk, and LivePortrait in one process on under 12 GB VRAM."
version: 1.0.1
---

# Local Lip-Sync Pipeline for Stylized Characters

## Overview

Off-the-shelf lip-sync models were trained on real human faces and degrade in specific, fixable ways on stylized input. The fixes live in the order you run things, the swap points between stages, and a handful of compositing details. This skill captures that pipeline end-to-end.

**Key terms used throughout:**

- **Stylized character** — any non-photoreal speaking face. Sub-styles: cel-shaded 2D (anime, classic Western cartoons — flat fills, hard line art), 3D rendered (Pixar/Disney/Arcane-style CG with soft shading), semi-realistic CG (stylized human faces with photoreal-leaning shading), illustrated/painted (textured 2D, brushwork visible), puppet/mascot (physical foam or rigid-shell heads, often hinged or fixed mouths).
- **Real-face detector** — trained on photographs of human faces (RetinaFace, S3FD, MTCNN, OpenCV Haar "face" cascades). Opposite: anime/illustration detectors trained on drawn faces.
- **Locked-off shot** — static camera with no pan, tilt, zoom, or roll. Face stays in roughly the same image-space region; manual bbox is trivially viable.
- **Double-hop** — audio→cartoon technique: generate a driver video from audio using SadTalker, then feed that driver into LivePortrait. Two model passes.
- **CFR / VFR** — constant-frame-rate vs. variable-frame-rate source. All sync models here assume CFR; VFR sources must be conformed first.

Decision-tree, compositing, licensing, and orchestrator details are **in this SKILL.md** (Step 0, Steps 4–6, Orchestration, Licensing). This pack does not ship separate companion files.

## When to Use

Use this skill when:

- Lip-syncing a stylized or non-photoreal character to a voice track on local GPU hardware.
- A real-face detector is rejecting a stylized face (cel-shaded, anime, puppet, mascot).
- You see jaw or chin clipping after Wav2Lip paste-back.
- You see blurry hallucinated mouth texture or visible mask seams.
- Audio drifts, or lips fire before/after sound.
- Ghosting appears on already-animated source frames.
- "Real-time" claims fall below realtime on the user's hardware.
- VRAM exhaustion occurs when chaining models in one process.
- torch/onnxruntime pin conflicts break a shared environment.
- MPS/Apple Silicon limitations surface (MuseTalk ONNX paths fall back to CPU).
- Multi-character dialogue needs per-speaker sync passes.
- Occluded mouths (hand over mouth, head turn) produce ghost mouth shapes.
- HDR or alpha-channel source needs pre-processing before sync.
- License questions arise around Wav2Lip/GFPGAN/CodeFormer weights for commercial delivery.

**Skip** when the question is a generic ffmpeg/audio question that happens to mention a stylized character but doesn't involve sync — answer those directly.

## Prerequisites

### GPU / Platform

- **CUDA on Linux/Windows** is the smooth path.
- **MPS (Apple Silicon)**: works partially for LivePortrait; MuseTalk's ONNX-accelerated paths are CUDA-only and fall back to CPU on Mac.
- **ROCm (AMD)** and **Intel Arc**: treat as CUDA-equivalent in API but expect rough edges. Install `torch` ROCm wheels and `onnxruntime-rocm` (AMD) or `onnxruntime-openvino` (Intel). Some custom CUDA kernels in MuseTalk have no ROCm/OneAPI port and fall back to slow paths.
- **CPU-only**: Wav2Lip will run (slowly); MuseTalk and LivePortrait are impractical without a GPU.

### VRAM

- Under ~12 GB free: chain stages as **separate subprocesses** so VRAM is released between them. Loading all three models in one Python process is the most common OOM pattern.
- Over 12 GB: chaining is safe but still optional.
- The orchestrator probes VRAM up front and picks chained vs. serialized from the result.

### Environment Isolation

Wav2Lip's reference code expects torch 1.13 with the old FP16 API; MuseTalk wants torch 2.0+; LivePortrait wants 2.3+. Pinning all three into one env works briefly, then breaks on the next upgrade.

**Default: one Python environment per model, orchestrated by a top-level script that shells out.**

Escape hatches: Docker, `uv` workspaces, or `pip-tools` constraints — don't tear down a working multi-env or container setup just to match a convention. A single env with careful pinning is possible but brittle across upgrades — only attempt if explicitly requested.

Suggested layout (on Windows substitute `Scripts\python.exe` for `bin/python`):

```
lipsync/
├── envs/
│   ├── wav2lip/         # python 3.8, torch 1.13
│   ├── musetalk/        # python 3.10, torch 2.0+
│   ├── liveportrait/    # python 3.10, torch 2.3+
│   └── enhance/         # gfpgan + codeformer + realesrgan
├── models/              # shared checkpoints (symlink into each env)
├── work/                # scratch frames, masks, alignments
└── orchestrator.py      # runs on its own python (3.10+), outside any env above
```

The orchestrator runs on its own Python interpreter (3.10+ — it uses `list[str]` and pathlib idioms that the Wav2Lip env's 3.8 wouldn't accept) **outside** the per-model envs — it never imports torch, it just shells out. Symlinking the shared `models/` directory into each env keeps a single source of truth.

### Checkpoint Sourcing

- Pin checkpoint files by SHA-256 in a small `models/manifest.toml` and verify on download. The orchestrator refuses to run with mismatched hashes — a silently corrupted MuseTalk weight produces plausible-looking sync that's subtly wrong.
- Maintain a fallback mirror list per checkpoint (HF mirror, IPFS pin, internal artifact storage). When the primary 404s, fall through.
- Cache checkpoints in `models/` and **never** inside the per-env site-packages — re-installing an env should not re-download a 2 GB weight.

### Model Selection

| Model | Best for | Avoid when |
|---|---|---|
| Wav2Lip / wav2lip_gan | Fast baseline, semi-realistic 2D/3D | 96×96 mouth crop is the resolution ceiling regardless of enhancement; also weak on very flat or chibi faces |
| MuseTalk | 256×256 mouth output; faster-than-realtime at 512p on a 4090, ~1× on a 3060; lip closure on plosives is visually correct on most cel-shaded and 3D-rendered faces once `bbox_shift` is tuned; weaker on heavily painterly styles | Heavy occlusion or profile angles beyond ~45° |
| LivePortrait | Driving stylized faces from a driver clip — transfers eyes, brows, head pose, and mouth together rather than just lips | Audio-only with no driver, unless using the double-hop (§3c) |

A common winning combination: **MuseTalk for the mouth + LivePortrait for everything else + an enhancer + a feathered composite mask**.

Two newcomer surprises to surface up front: LivePortrait needs a driver video, and Wav2Lip's 96×96 ceiling is a property of the architecture, not a parameter to tune.

## Procedure

### Step 0: Decision Tree (do this first)

Answer these before any rendering — they pick the model and gate later choices, and re-litigating after a 20-minute render wastes time:

1. **Sub-style → enhancer.** Cel-shaded 2D / anime → RealESRGAN (no face prior, so it won't fight the line art). 3D rendered → CodeFormer (handles soft shading well). Semi-realistic CG → GFPGAN (lightweight face prior, identity-preserving, roughly 2× the inference speed of CodeFormer on equivalent hardware in our measurements). Puppet / mascot / illustrated → start with RealESRGAN; GFPGAN and CodeFormer tend to push features toward photoreal proportions on these inputs, which is rarely what you want.
2. **Driver video available?** Yes → LivePortrait is viable. Audio only → Wav2Lip or MuseTalk, or the double-hop (§3c) that generates a driver from audio first.
3. **Camera / head motion.** Locked-off shot → a fixed manual bbox is the fastest and most stable path. Moving shot → tracker or per-frame detector; flickery detection is a major cause of jitter complaints.
4. **Delivery fps** (24, 23.976, 25, 29.97, 30). Wav2Lip, MuseTalk, and LivePortrait checkpoints were all trained at 25 fps. Sync internally at 25 and conform to the delivery fps in the final remux. Running these models on 30 fps source without conforming isn't fatal, but mouth motion drifts at the ratio difference (~17% on 30 → 25).
5. **Aspect ratio.** 16:9 and 9:16 (vertical/reels) both work, but the mask heuristics in §5 (ellipse at 70% of bbox height, etc.) were measured against 16:9 with roughly square face crops. On vertical phone-shot source, faces are usually taller-than-wide — shift the ellipse center upward by ~5–10% of crop height to stay anchored on the mouth. Anamorphic or letterboxed source: crop to the live image area before sync; bbox math doesn't account for black bars.
6. **GPU / platform.** See Prerequisites above.
7. **VRAM.** Under ~12 GB, chain stages as separate subprocesses. The orchestrator probes VRAM up front and picks chained vs. serialized from the result.
8. **Audio composition.** Dialogue-only audio works as-is. Dialogue mixed with music or SFX in the same track degrades Wav2Lip's mel features and MuseTalk's audio encoder — run stem separation first (e.g. Demucs `htdemucs`, vocals stem) and feed only the vocal stem to the sync model. Keep the full mix for the final remux.

### Step 1: Probe and Prep Input

```bash
ffprobe -v error -show_entries stream=codec_type,r_frame_rate,nb_frames,sample_rate,channels,duration -of json INPUT.mp4
```

The most common silent failure is a **VFR source**: a nominal `r_frame_rate` doesn't prove constant frame rate — phone recordings and screen captures routinely advertise "30 fps" while dropping packets. Spot-check with `ffprobe -select_streams v -show_entries packet=pts_time` on a few frames; if the deltas vary, it's VFR. When in doubt, re-encode to CFR:

```bash
ffmpeg -i INPUT.mp4 -vf fps=25 -fps_mode cfr -c:v libx264 -crf 16 \
  -c:a pcm_s16le -ar 16000 -ac 1 INPUT_cfr.mov
```

Key notes about that command:

- `fps=25 -fps_mode cfr` (older ffmpeg: `-vsync cfr`) actually forces CFR by duplicating or dropping frames. `-r 25` alone does *not* on VFR input — it just re-tags the container, which is a foot-gun.
- 16 kHz mono is what Wav2Lip / MuseTalk audio encoders expect for **model input**. Keep the **original** audio file separately — 16 kHz mono is below typical broadcast/streaming spec (usually 48 kHz stereo); remux the original back at Step 6. For low-bar deliverables (social-media mascot loops, internal demos) the 16 kHz can be acceptable; surface the choice to the user rather than assume.
- `.mov` accepts `pcm_s16le`; `.mp4` does not reliably. Use `.mov` or `.mkv` here, or transcode the working audio to AAC if you must stay in `.mp4`.
- For 24 / 23.976 / 29.97 delivery, set `fps=` accordingly and plan a pulldown step at remux.
- **HDR / log inputs**: if `ffprobe` reports `bt2020`, `smpte2084`, or `arib-std-b67`, tone-map before sync — libx264 with default flags crushes HDR colorimetry and you'll deliver an SDR clip with a faint green cast. Example: `-vf zscale=t=linear,...,zscale=t=bt709:m=bt709:r=tv,format=yuv420p`.
- **BT.601 ↔ BT.709 matrix mismatch** is more common than HDR and easier to miss. SD-era content (480p/576p) is BT.601; HD is BT.709. If the source is SD or labeled BT.601 and you don't convert with `-vf zscale=matrix=709:matrixin=601` (or `colormatrix` filter), the sync model writes its output as BT.709 and reds shift greenish on remux. Check `ffprobe`'s `color_space` field and force-convert when it disagrees with the working space.
- **Alpha channels** (mascot/puppet on a comp): extract the alpha matte first, sync the RGB only, then re-mux the original alpha back. Sync models will destroy or ignore alpha if left in.
- **Embedded subtitle / caption streams**: the CFR re-encode preserves subtitle streams only if you pass `-c:s copy`. If you later apply `-itsoffset` at remux (Step 6), embedded subtitle PTS does not shift with `-itsoffset` on the video — captions desync. Either burn captions in after final remux, or re-time them with `ffmpeg -itsoffset` on the subtitle input separately.
- **Long clips**: anything over ~2 minutes should be chunked, especially with MuseTalk (VRAM use grows with batch size; long renders compound). Split at silence boundaries (`ffmpeg -af silencedetect`), sync each chunk independently, then concat. Overlap each chunk by ~0.5 s and crossfade the overlap on concat to avoid audible/visible seams at chunk boundaries — a known MuseTalk failure mode.

### Step 2: Face Detect / Align

Real-face detectors frequently reject stylized faces — their training data shares almost no low-level features with cel-shaded art. Fallback ladder, in order of preference:

1. **Bundled detector** — try it first; sometimes works on semi-realistic CG.
2. **YOLOv8-face** (`ultralytics`) — more forgiving on illustrated faces because YOLO's training data is broader.
3. **`anime-face-detector`** (LFD/SSD-based) for anime specifically. Preferred over `lbpcascade_animeface.xml` (Haar), which has poor recall on modern styles — keep Haar only as a last-resort fallback.
4. **Manual bbox** — ask the user for a bounding box on frame 1 and propagate with a moving-average smoother over ~5–9 frames. On locked-off shots and slow camera moves, this is often *more* stable than a flickery detector.
5. **No face at all** (faceless mascot, abstract character, mouth-only render, plush with a fixed jaw hinge): skip face detection entirely and define the mouth region directly as the ROI. Ask the user to mark the mouth bbox on frame 1; sync models accept a manually-specified mouth crop without a surrounding "face." Wav2Lip's `--box` flag is the relevant entry point; MuseTalk needs a stub bbox in the per-shot YAML treated as a mouth-only region with `bbox_shift=0`.

**Multi-face frames**: detectors return all faces, so pick by who's speaking. Two practical signals: force-aligned phonemes vs. lip motion in the source, or explicit per-shot selection (largest face, leftmost, named track). Two-character dialogue typically wants two passes with two bboxes and two audio tracks, composited at the end.

**Speaker change mid-shot** (off-screen narrator hands off to an on-screen character, or two characters trade lines without a cut): time-slice the audio per speaker, run sync only over the on-screen speaker's segments, and pass off-screen segments through unmodified. A force-aligner like `whisperx` gives word-level timestamps that map cleanly to "sync this range, skip that range."

**Off-screen / occluded frames** (hand over mouth, head turn, prop in the way): skip them, passing the original frame through unchanged. Syncing through an occluder produces ghost mouth shapes drawn over the obstructing object, which looks worse than no sync. Detection methods, in increasing reliability:

- Face-confidence threshold from the detector — fast but unreliable on stylized art, where the detector is already shaky.
- IoU between the current bbox and the moving-average expected bbox; large drops flag occlusion or sudden head turn.
- A separate hand/object segmenter (e.g. SAM 2 with a "hand" prompt) on suspect frames — slow but accurate, suitable for a final pass before delivery.

### Step 3: Run the Sync Model

#### 3a. Wav2Lip

```bash
python inference.py \
  --checkpoint_path checkpoints/wav2lip.pth \
  --face INPUT_cfr.mov \
  --audio AUDIO.wav \
  --pads 0 20 0 0 \
  --resize_factor 1 \
  --nosmooth \
  --outfile work/wav2lip_raw.mp4
```

- `--pads 0 20 0 0` adds bottom padding so the chin is included. The default tight crop clips the chin on stylized faces, producing a visible jaw-step when the crop is pasted back.
- `--nosmooth` disables Wav2Lip's frame-averaging smoother. The smoother helps on live-action but ghosts on already-animated source. Rule of thumb: use `--nosmooth` on animated input, omit on live-action.
- `wav2lip_gan.pth` is sharper but produces photoreal skin texture under stylized line art, which most users describe as off-putting. Use it only when followed by an enhancer pass.

Caveats: Wav2Lip is biased toward **English visemes** (training data skew). Non-English audio works but expect weaker alignment on phonemes absent from English (clicks, trills, tonal contour). **Singing, screaming, whispered audio** is out of distribution for all three models — sync will degrade and no parameter fixes it.

#### 3b. MuseTalk

MuseTalk takes a `bbox_shift` parameter to position the mouth correctly. Units are **pixels in the original frame's coordinate space**. Sign convention: **positive `bbox_shift` moves the inferred mouth region downward** (toward the chin); negative moves it upward. The default is tuned for real-face proportions, so on stylized characters — particularly large heads with small mouths — it needs per-character tuning, typically in the range −20 to +20 px. Symptom-to-direction map:

- Mouth appears too high (closure happens above the actual lips) → increase `bbox_shift` (more positive, pushes the inferred region downward to meet the real mouth).
- Mouth appears too low (closure happens on the chin) → decrease `bbox_shift` (more negative).

Iterate cheaply: render 2 seconds, check, adjust, re-render.

```bash
python -m scripts.inference \
  --inference_config work/per_shot.yaml \
  --result_dir work/musetalk \
  --bbox_shift 5
```

The orchestrator writes `per_shot.yaml` programmatically — example shape:

```yaml
# work/per_shot.yaml — generated by orchestrator.py, do not hand-edit
shot_001:
  video_path: work/shot_001_cfr.mov
  audio_path: work/shot_001_vocals.wav
  bbox_shift: 5
shot_002:
  video_path: work/shot_002_cfr.mov
  audio_path: work/shot_002_vocals.wav
  bbox_shift: -8
```

Editing the bundled `configs/inference/test.yaml` by hand causes merge conflicts on every repo upgrade and breaks reproducibility — generate the per-shot file fresh each run.

MuseTalk's "real-time" claim is hardware- and resolution-dependent: faster-than-realtime at 256–512 px on an RTX 4090; ~1× on a 3060; well below realtime on Apple MPS, where ONNX-accelerated paths fall back to CPU. Set expectations against the user's hardware, not the README headline.

#### 3c. LivePortrait (and the Double-Hop)

LivePortrait needs a **source image** (the stylized character) and a **driver video** (a face performing the motion you want). For audio-only inputs, generate the driver first with an audio-driven talking-head model — **SadTalker** is the usual choice (it's audio-driven, not TTS — feed it your audio plus a generic portrait), then feed that output as LivePortrait's driver. This is the **double-hop**.

```bash
python inference.py \
  -s assets/source_character.png \
  -d work/driver.mp4 \
  --flag_relative_motion \
  --flag_pasteback \
  -o work/liveportrait_out.mp4
```

`--flag_relative_motion` transfers *changes in pose* rather than absolute pose. This matters because cartoon and human head proportions differ — often dramatically — and absolute-pose transfer pulls the cartoon's features toward the human's resting position.

**Identity-leakage caveats** — both technical and legal:

- *Technical*: a SadTalker driver generated from an actor's portrait carries that actor's idiosyncratic mouth shape, asymmetries, and smile-lines into the cartoon. Two ways to dampen: pick a neutral, frontal, symmetric portrait for the driver, or pre-stylize the driver portrait before SadTalker sees it.
- *Legal*: using a recognizable person's likeness as the driver portrait may carry rights-of-publicity or likeness-rights issues, separate from model licensing. Most acute for celebrities and stock photos with restrictive licenses. Use a portrait you have rights to use as a driving signal, even though the final delivery doesn't show that face.

### Step 4: Enhancement Pass

Sync models output a low-resolution mouth crop. Enhancement restores detail. The default approach is: crop to mouth, enhance, paste back. Face priors can introduce small color shifts (warmer skin tones) and minor geometric warping (eye position, jaw width) when applied full-frame; cropping to the mouth contains both.

- For **locked-off shots with no background motion**: full-frame enhancement is fine and simpler.
- For **moving shots or detailed backgrounds**: crop-and-paste avoids drift outside the face region.

Enhancer selection (from the decision tree):

| Sub-style | Enhancer | Reason |
|---|---|---|
| Cel-shaded 2D / anime | RealESRGAN | No face prior, won't fight line art |
| 3D rendered | CodeFormer | Handles soft shading well |
| Semi-realistic CG | GFPGAN | Lightweight face prior, identity-preserving, ~2× faster than CodeFormer |
| Puppet / mascot / illustrated | RealESRGAN (start) | GFPGAN/CodeFormer push toward photoreal proportions |

### Step 5: Composite Mask

The sync model returns a rectangular crop; pasting it raw leaves a visible box. Use the `feathered_mouth_mask` helper below. Feather and shape:

```python
import cv2, numpy as np

def feathered_mouth_mask(crop_h, crop_w, feather=15):
    mask = np.zeros((crop_h, crop_w), dtype=np.float32)
    cv2.ellipse(
        mask,
        (crop_w // 2, int(crop_h * 0.70)),
        (int(crop_w * 0.45), int(crop_h * 0.28)),
        0, 0, 360, 1.0, -1,
    )
    return cv2.GaussianBlur(mask, (0, 0), feather)
```

Composite: `out = orig * (1 - mask) + synced * mask`.

**Ellipse parameters per character**: anchor to the eye-line and chin position. Rule of thumb — center the ellipse at ~70% of bbox height for human-proportioned faces; raise to ~55–60% for chibi or large-forehead designs (their mouths sit higher relative to the bbox); horizontal radius covers the widest "open mouth" pose without crossing the cheek line. On vertical/portrait-aspect source, shift center upward by ~5–10% of crop height. Render a 1-second test on a vowel-heavy phrase ("amazing apples"), eyeball it, adjust, re-render — faster than guessing the math.

**Tracking the mask on moving shots**: anchor to the same bbox produced in Step 2 (detector output or manual + smoother) and re-derive crop coordinates per frame from that bbox. The bbox is the single source of truth for mouth-region location; a second tracker on the mask gives you two truths to reconcile. The legitimate exception is when the detector itself is wrong on a specific stretch (manual review flags it) — hand-paint the bbox for those frames rather than introduce a second tracker.

### Step 6: Audio-Video Remux and Sync Verification

Put the **original** audio (native sample rate / channels, not the 16 kHz mono used for model input) back over the synced video:

```bash
ffmpeg -i work/composited.mp4 -i ORIGINAL_AUDIO.wav \
  -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest \
  OUTPUT.mp4
```

Verify on phoneme-rich segments — `p`, `b`, `m` should be fully closed on every occurrence. If off by a constant offset, the model's audio preprocessing dropped or padded samples. Typical offsets are 1–3 frames (40–120 ms at 25 fps); larger usually means an fps mismatch and is worth revisiting Step 1.

**`-itsoffset` sign convention** (classic foot-gun): `-itsoffset T` applied **before an input** delays that input by T seconds. If the lips fire *before* the sound, the video needs to be delayed relative to the audio — apply `-itsoffset` to the video input. Equivalent: advance the audio. Confirm direction on a 2-second test clip before rendering the whole timeline.

```bash
# Lips leading audio by ~40 ms — delay video relative to audio:
ffmpeg -itsoffset 0.04 -i work/composited.mp4 -i ORIGINAL_AUDIO.wav \
  -map 0:v -map 1:a -c:v copy -c:a aac OUTPUT.mp4
```

**Caption tracks**: if the deliverable has burned or embedded subtitles, `-itsoffset` on the video does not shift embedded subtitle PTS. Either burn captions after this step, or apply the same `-itsoffset` to the subtitle input.

### Orchestration

When setting up the pipeline or debugging stage handoffs, keep the orchestrator dumb: shell out to each env, pass file paths, check return codes. Two non-obvious requirements: **skip-if-exists** (so a mid-pipeline failure doesn't redo a 20-minute MuseTalk pass) and **argument lists** rather than shell strings (paths with spaces work, no shell-injection surface). The orchestrator runs on its own Python (3.10+) outside any per-model env:

```python
# orchestrator.py — runs on its own python (3.10+), never inside a per-model env.
# Uses list[str] and pathlib idioms that the Wav2Lip env (3.8) wouldn't accept.
import subprocess
import sys
from pathlib import Path

IS_WIN = sys.platform.startswith("win")
# Windows envs put python in Scripts\python.exe; POSIX envs use bin/python.
PY_REL = "Scripts/python.exe" if IS_WIN else "bin/python"

ENVS = {
    "wav2lip":      Path.home() / "lipsync/envs/wav2lip"      / PY_REL,
    "musetalk":     Path.home() / "lipsync/envs/musetalk"     / PY_REL,
    "liveportrait": Path.home() / "lipsync/envs/liveportrait" / PY_REL,
    "enhance":      Path.home() / "lipsync/envs/enhance"      / PY_REL,
}

def run(env: str, args: list[str], cwd: Path, out: Path) -> None:
    if out.exists() and out.stat().st_size > 0:
        print(f"[{env}] skip (exists): {out}")
        return
    cmd = [str(ENVS[env]), *args]
    print(f"[{env}] {' '.join(cmd)}")
    subprocess.run(cmd, cwd=cwd, check=True)
```

The orchestrator **must** probe available VRAM up front (`nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits` on CUDA; `rocm-smi` on ROCm; platform-equivalent elsewhere) and pick chained vs. serialized execution from the result. Under 12 GB free → serialize (one model at a time, releasing VRAM between subprocess calls). Over 12 GB → chaining is safe but still optional.

## Pitfalls

1. **VFR source masquerading as CFR.** A nominal `r_frame_rate` from `ffprobe` doesn't prove constant frame rate. Phone recordings and screen captures routinely advertise "30 fps" while dropping packets. Spot-check with `ffprobe -select_streams v -show_entries packet=pts_time`. When in doubt, re-encode to CFR — re-encoding is cheap compared to debugging "why does the mouth drift after 10 seconds."

2. **`-r 25` alone does NOT force CFR on VFR input.** It just re-tags the container. Use `fps=25 -fps_mode cfr` (or `-vsync cfr` on older ffmpeg) to actually force CFR by duplicating or dropping frames.

3. **Chin clipping from tight Wav2Lip crop.** The default tight crop clips the chin on stylized faces, producing a visible jaw-step on paste-back. Fix: `--pads 0 20 0 0`.

4. **Ghosting on animated source from Wav2Lip smoother.** The frame-averaging smoother helps on live-action but ghosts on already-animated source. Fix: `--nosmooth` on animated input.

5. **Wav2Lip 96×96 resolution ceiling.** This is a property of the architecture, not a parameter to tune. Enhancement can sharpen the output but cannot add detail that was never generated.

6. **Loading all three models in one Python process.** The most common OOM pattern. Fix: chain stages as separate subprocesses so VRAM is released between them, especially under ~12 GB VRAM.

7. **Editing bundled `configs/inference/test.yaml` by hand for MuseTalk.** Causes merge conflicts on every repo upgrade and breaks reproducibility. Fix: generate the per-shot YAML fresh each run via the orchestrator.

8. **MuseTalk `bbox_shift` wrong direction.** Positive moves the inferred mouth region **downward** (toward chin); negative moves it **upward**. If the mouth appears too high, increase `bbox_shift`. If too low, decrease it.

9. **Visible rectangular mask seam on paste-back.** The sync model returns a rectangular crop. Fix: apply a feathered elliptical mask (see Step 5).

10. **Audio drift from 16 kHz mono remux.** 16 kHz mono is below broadcast/streaming spec. Always keep the original audio and remux it back at Step 6.

11. **`-itsoffset` sign confusion.** `-itsoffset T` applied **before an input** delays that input by T seconds. If lips fire before sound, delay the video (apply `-itsoffset` to the video input). Confirm on a 2-second test clip before rendering the whole timeline.

12. **Embedded subtitle desync after `-itsoffset`.** `-itsoffset` on the video does not shift embedded subtitle PTS. Either burn captions after the remux step, or apply the same `-itsoffset` to the subtitle input separately.

13. **HDR color crush.** If `ffprobe` reports `bt2020`, `smpte2084`, or `arib-std-b67`, tone-map before sync — libx264 with default flags crushes HDR colorimetry, delivering an SDR clip with a faint green cast.

14. **BT.601 ↔ BT.709 matrix mismatch.** SD-era content (480p/576p) is BT.601; HD is BT.709. If the source is BT.601 and you don't convert, reds shift greenish on remux. Check `ffprobe`'s `color_space` field and force-convert with `-vf zscale=matrix=709:matrixin=601`.

15. **Alpha channel destruction.** Sync models will destroy or ignore alpha if left in. Extract the alpha matte first, sync the RGB only, then re-mux the original alpha back.

16. **MuseTalk VRAM growth on long clips.** VRAM use grows with batch size; long renders compound. Chunk anything over ~2 minutes at silence boundaries, sync each chunk independently, then concat with ~0.5 s overlap crossfaded.

17. **Ghost mouth shapes over occluders.** Syncing through an occluder (hand over mouth, head turn, prop) produces ghost mouth shapes drawn over the obstructing object. Skip occluded frames, passing the original through unchanged.

18. **Identity leakage in double-hop.** A SadTalker driver generated from an actor's portrait carries that actor's mouth shape, asymmetries, and smile-lines into the cartoon. Dampen with a neutral, frontal, symmetric driver portrait, or pre-stylize the driver before SadTalker sees it.

19. **Music/SFX degrading mel features.** Dialogue mixed with music or SFX in the same track degrades Wav2Lip's mel features and MuseTalk's audio encoder. Run stem separation first (e.g. Demucs `htdemucs`, vocals stem) and feed only the vocal stem to the sync model.

20. **Singing/screaming/whispered audio.** Out of distribution for all three models — sync will degrade and no parameter fixes it.

21. **MuseTalk "real-time" expectations.** Faster-than-realtime at 256–512 px on an RTX 4090; ~1× on a 3060; well below realtime on Apple MPS. Set expectations against the user's hardware, not the README headline.

22. **Checkpoint corruption from mirror outages.** A silently corrupted MuseTalk weight produces plausible-looking sync that's subtly wrong. Pin checkpoints by SHA-256 in `models/manifest.toml` and verify on download. The orchestrator refuses to run with mismatched hashes.

23. **Caching checkpoints inside per-env site-packages.** Re-installing an env should not re-download a 2 GB weight. Cache in `models/` and symlink into each env.

24. **torch/onnxruntime pin conflicts in shared env.** Wav2Lip wants torch 1.13; MuseTalk wants 2.0+; LivePortrait wants 2.3+. One env per model is the default. A single env with careful pinning is brittle across upgrades.

## Verification

### Input conformance

```bash
# Confirm CFR after re-encode — deltas should be uniform
ffprobe -select_streams v -show_entries packet=pts_time -of csv INPUT_cfr.mov | head -20
```

All `pts_time` deltas should be identical (0.04s at 25 fps). If they vary, the source is still VFR — re-encode again.

### Audio alignment

```bash
# Check audio stream properties of the final output
ffprobe -v error -show_entries stream=codec_type,sample_rate,channels,duration -of json OUTPUT.mp4
```

Confirm the audio sample rate matches the original (e.g. 48000 Hz, stereo), not the 16 kHz mono used for model input.

### Lip sync spot-check

Verify on phoneme-rich segments — `p`, `b`, `m` should be fully closed on every occurrence. If off by a constant offset, the model's audio preprocessing dropped or padded samples. Typical offsets are 1–3 frames (40–120 ms at 25 fps); larger usually means an fps mismatch — revisit Step 1.

### VRAM probe

```bash
# CUDA
nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits

# ROCm
rocm-smi --showmeminfo vram
```

Confirm free VRAM before launching the orchestrator. Under 12 GB → expect serialized execution.

### Checkpoint integrity

```bash
# Verify SHA-256 against models/manifest.toml
sha256sum models/wav2lip.pth
sha256sum models/musetalk/*.pth
```

The orchestrator refuses to run with mismatched hashes. If a hash fails, re-download from a fallback mirror.

### Mask seam check

Render a 1-second test on a vowel-heavy phrase ("amazing apples") and eyeball the composite boundary. If a rectangular seam is visible, increase the feather radius in `feathered_mouth_mask` or adjust the ellipse parameters.

## Licensing

These checkpoints come with non-trivial license terms. A local pipeline is not automatically a licensed pipeline. Surface this section before any commercial delivery discussion:

- **Wav2Lip**: pretrained weights are research-only in the original release; commercial use of the released checkpoints is not permitted under that license.
- **GFPGAN**, **CodeFormer**: each ship with their own license; review the current terms at the version pulled.
- **MuseTalk**, **LivePortrait**: check the current repo license at the commit hash pulled, not the historical one.

License terms above verified against upstream repos **as of 2026-06**. Re-check at the version actually pulled, since these change. If the deliverable is commercial, surface the licensing question explicitly and let the user decide rather than assume "it ran on my machine" implies "I can ship it."

## Defaults (single canonical table)

Reasoning is consolidated here so the inline pipeline stays terse. Deviate when the reason in the right column doesn't apply.

| Default | Reason | Deviate when |
|---|---|---|
| One env per model | Conflicting torch/onnxruntime pins break shared envs on upgrade. | User has a working multi-env or container setup. |
| CFR re-encode at 25 fps | Wav2Lip/MuseTalk/LivePortrait assume CFR; checkpoints trained at 25. | `ffprobe` packet timestamps confirm source is already CFR. |
| `--nosmooth` on Wav2Lip | Smoother ghosts on already-animated source. | Smooth live-action source where the smoother helps. |
| Crop-then-enhance | Face priors can color-shift (warmer skin) and geometry-shift (eye position, jaw width) adjacent regions full-frame. | Locked-off shot with simple background. |
| `wav2lip.pth` baseline first | `wav2lip_gan.pth` produces photoreal skin texture under stylized line art. | Followed by an enhancer pass that masks the texture. |
| Sync internally at 25 fps | Checkpoints were trained at 25; conform to delivery fps at remux. | All models in use are non-25-trained (uncommon). |
| Keep original audio through pipeline | 16 kHz mono is below broadcast/streaming spec. | Deliverable spec accepts 16 kHz (some social formats do). |
| Stem-separate dialogue from mix | Mel features degrade on music + dialogue. | Source is already isolated dialogue. |
| Pin checkpoints by SHA-256 | Mirror outages and silent corruption produce subtly wrong sync. | Single-shot experiments where reproducibility doesn't matter. |
| Orchestrator probes VRAM up front | OOM mid-pipeline wastes the most expensive stage's runtime. | Single dedicated workstation with known headroom. |
