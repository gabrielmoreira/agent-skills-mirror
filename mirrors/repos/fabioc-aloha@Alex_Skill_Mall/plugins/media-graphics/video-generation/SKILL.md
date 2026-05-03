---
type: skill
lifecycle: stable
inheritance: inheritable
name: "video-generation"
description: AI video generation via Replicate — 17 models, editing, and production workflows
tier: extended
applyTo: '**/*video*,**/*generation*'
currency: 2026-04-22
lastReviewed: 2026-04-30
---

# Video Generation Skill


> **Domain**: AI Video Generation  
> **Version**: 2.0.0  
> **Last Updated**: 2026-04-15  
> **Author**: the AI assistant (your AI assistant)  
> **Source**: Patterns from AlexVideos CLI toolkit  
> **Related**: [image-handling](../image-handling/SKILL.md) (images), [text-to-speech](../text-to-speech/SKILL.md) (audio)

## Overview

Generate AI videos using 17 cloud models on Replicate. Supports text-to-video, image-to-video, video editing, and talking-head workflows.

---

## Model Catalog (17 Models)

| Key | Model | Replicate ID | Duration | Audio | Cost |
|-----|-------|--------------|----------|-------|------|
| `veo3fast` | **Veo 3.1 Fast** | `google/veo-3.1-fast` | 4/6/8s | ✅ Auto | $0.10–0.15/sec |
| `veo3` | **Veo 3.1** | `google/veo-3.1` | 4/6/8s | ✅ Auto | $0.20–0.40/sec |
| `grok` | **Grok Video** | `xai/grok-imagine-video` | 1–15s | ✅ Lip-sync | $0.05/sec |
| `gen45` | **Gen-4.5 Runway** | `runwayml/gen-4.5` | 5–10s | ❌ | $0.12/sec |
| `kling` | **Kling v3** | `kwaivgi/kling-v3-video` | 3–15s | Optional | $0.17–0.22/sec |
| `kling26` | **Kling v2.6** | `kwaivgi/kling-v2.6` | 5–10s | ✅ Auto | variable |
| `kling3omni` | **Kling v3 Omni** | `kwaivgi/kling-v3-omni-video` | 3–15s | ❌ | variable |
| `sora` | **Sora-2** | `openai/sora-2` | 4–12s | ✅ Auto | $0.10/sec |
| `sora2pro` | **Sora-2 Pro** | `openai/sora-2-pro` | 4/8/12s | ✅ Auto | $0.30–0.50/sec |
| `seedance` | **Seedance Lite** | `bytedance/seedance-1-lite` | 2–12s | ❌ | $0.036/sec |
| `seedpro` | **Seedance Pro** | `bytedance/seedance-1-pro` | 2–12s | ❌ | $0.15/sec |
| `pixverse` | **PixVerse v5.6** | `pixverse/pixverse-v5.6` | 5/10s | ✅ Auto | variable |
| `hailuo` | **Hailuo-02** | `minimax/hailuo-02` | 6/10s | ❌ | variable |
| `hailuo23` | **Hailuo-2.3** | `minimax/hailuo-2.3` | 6/10s | ❌ | variable |
| `ray2` | **Ray 2 Luma** | `luma/ray-2-720p` | 5/9s | ❌ | $0.18/sec |
| `rayflash` | **Ray Flash 2** | `luma/ray-flash-2-720p` | 5/9s | ❌ | $0.06/sec |
| `wan` | **WAN 2.5 Fast** | `wan-video/wan-2.5-t2v-fast` | 5–10s | ✅ Auto | $0.068/sec |

---

## Parameter Support Matrix

| Model | prompt | duration | image | aspect | resolution | negative | audio |
|-------|:------:|:--------:|:-----:|:------:|:----------:|:--------:|:-----:|
| `veo3fast` | ✅ | 4/6/8 | ✅ | ✅ | ✅ | ✅ | ✅ auto |
| `veo3` | ✅ | 4/6/8 | ✅ | ✅ | ✅ | ✅ | ✅ auto |
| `grok` | ✅ | 1–15 | ✅ | ✅ | ✅ | — | ✅ auto |
| `gen45` | ✅ | 5–10 | ✅ | ✅ | — | — | — |
| `kling` | ✅ | 3–15 | ✅ | ✅ | ✅ (mode) | ✅ | optional |
| `kling26` | ✅ | 5–10 | ✅ | ✅ | — | ✅ | ✅ auto |
| `kling3omni` | ✅ | 3–15 | ✅ | ✅ | ✅ (mode) | — | — |
| `sora` | ✅ | 4–12 | ✅ | ✅ | — | — | ✅ auto |
| `sora2pro` | ✅ | 4/8/12 | ✅ | ✅ | ✅ | — | ✅ auto |
| `seedance` | ✅ | 2–12 | ✅ | ✅ | ✅ | — | — |
| `seedpro` | ✅ | 2–12 | ✅ | ✅ | ✅ | — | — |
| `pixverse` | ✅ | 5/10 | ✅ | ✅ | ✅ (quality) | ✅ | ✅ auto |
| `hailuo` | ✅ | 6/10 | ✅ | — | ✅ | — | — |
| `hailuo23` | ✅ | 6/10 | ✅ | — | ✅ | — | — |
| `ray2` | ✅ | 5/9 | ✅ | ✅ | — | — | — |
| `rayflash` | ✅ | 5/9 | ✅ | ✅ | — | — | — |
| `wan` | ✅ | 5–10 | — | ✅ | — | ✅ | ✅ auto |

**Notes:**

- **Fixed values** (e.g., 5/9) mean only those exact values accepted
- **Ranges** (e.g., 3–15) accept any integer in range
- **Sora models** use "portrait"/"landscape" internally (mapped from 9:16/16:9)

---

## Model Selection Guide

| Need                           | Model              | Why                            |
| ------------------------------ | ------------------ | ------------------------------ |
| **Default / Quick preview**    | veo3fast           | Best balance: speed, quality, cost |
| **Talking head / lip-sync**    | grok, kling26      | Grok: best lip-sync; Kling26: best motion |
| **High quality cinematic**     | sora2pro, veo3     | Premium quality, synced audio  |
| **Image animation**            | kling, gen45       | Strong image-to-video          |
| **Budget production**          | rayflash, seedance | Cheapest per-second            |
| **Longest duration (15s)**     | grok, kling        | Only models supporting 15s     |
| **Real-world physics**         | hailuo, hailuo23   | Physics simulation, VFX        |

---

## Talking-Head Video Workflow

Proven pipeline for generating a person speaking to camera with synchronized speech:

```bash
# Step 1 — Age-progress reference photo (if needed)
node scripts/generate-image.js "A 26-year-old professional in studio" --model nanapro --image ref.png

# Step 2 — Generate video with Kling v2.6 (best talking-head i2v)
node scripts/generate-video.js "Person looking directly into camera, speaking confidently" --model kling26 --image aged.jpg --duration 10

# Step 3 — Generate speech
node scripts/generate-voice.js "[script]" --model mm28turbo

# Step 4 — Merge video + speech
node scripts/generate-edit-video.js --model avmerge --video clip.mp4 --audio speech.mp3
```

**Model notes:**

- `kling26` — Best overall motion quality for talking-head i2v
- `grok` — Best lip sync, but no native audio (requires `avmerge`)
- `veo3fast` / `sora` — May flag real-person reference photos

**Prompt pattern:**
> "A sharp [age]-year-old [description] looking directly into camera, speaking to the audience about [topic]. Calm, confident, broadcast-quality delivery. Professional studio lighting."

---

## Video Editing (10 Models)

| Key | Model | Purpose | Cost |
|-----|-------|---------|------|
| `modify` | Luma Modify | AI video style transfer | variable |
| `reframe` | Luma Reframe | AI crop to new aspect ratio | $0.06/sec |
| `trim` | Trim Video | Extract segment by time | <$0.001 |
| `merge` | Video Merge | Concatenate videos | variable |
| `avmerge` | ffmpeg-static | Combine audio + video | **free** (local) |
| `extract` | Extract Audio | Strip audio from video | variable |
| `frames` | Frame Extractor | Export frames as images | <$0.001 |
| `upscale` | Real-ESRGAN | AI upscale to 4K | ~$0.46 |
| `caption` | AutoCaption | Auto subtitles | ~$0.07 |
| `utils` | Video Utils | Convert, misc ops | <$0.002 |

---

## Generation Workflows

### Text-to-Video

```javascript
import Replicate from "replicate";

const replicate = new Replicate();

const output = await replicate.run("google/veo-3.1-fast", {
  input: {
    prompt: "A person walking through a futuristic city at sunset, cinematic lighting",
    duration: 5, // seconds
  },
});

console.log("Video URL:", output);
```

### Image-to-Video (Animation)

```javascript
import { readFileSync } from "fs";

const output = await replicate.run("kwaivgi/kling-v3-video", {
  input: {
    prompt: "Gentle wind blowing through hair, subtle movement",
    image: readFileSync("source-image.png"), // or URL
    duration: 5,
  },
});
```

### Talking Head with Lip-Sync

```javascript
const output = await replicate.run("xai/grok-imagine-video", {
  input: {
    prompt: "Person speaking to camera with natural expressions",
    audio: readFileSync("narration.mp3"), // Voice audio
    duration: 10,
  },
});
```

---

## Quality Guidelines

### Prompt Engineering

| Element         | Good Example                                       | Avoid                     |
| --------------- | -------------------------------------------------- | ------------------------- |
| Camera motion   | "slow dolly forward", "tracking shot"              | "camera moves"            |
| Lighting        | "golden hour", "dramatic side lighting"            | "good lighting"           |
| Style           | "cinematic 4K", "documentary style"                | "nice video"              |
| Subject         | "a person with short brown hair"                   | "someone"                 |
| Action          | "walking slowly through", "gesturing while talking"| "doing something"         |

### Duration Selection

| Duration | Use Case                         | Model Recommendation    |
| -------- | -------------------------------- | ----------------------- |
| 2-4s     | Loop, GIF replacement            | veo-3.1-fast            |
| 5-8s     | Short clip, social media         | veo-3.1-fast, kling-v3  |
| 10-15s   | Story segment, talking head      | grok-video, sora-2      |

### Resolution

- Most models default to 720p or 1080p
- Kling v3 supports explicit 1080p
- Higher resolution = longer generation time

---

## Audio Handling

### Models with Built-in Audio

| Model          | Audio Type       | Notes                        |
| -------------- | ---------------- | ---------------------------- |
| veo-3.1-fast   | Auto-generated   | Ambient sounds from scene    |
| grok-video     | Lip-sync         | Syncs mouth to provided audio|
| sora-2         | Synced           | High-quality scene audio     |

### Adding Audio Post-Generation

For models without audio, combine with TTS:

```javascript
// 1. Generate video (no audio)
const video = await replicate.run("kwaivgi/kling-v3-video", {
  input: { prompt: "...", duration: 5 },
});

// 2. Generate narration via TTS
const audio = await replicate.run("minimax/speech-2.8-turbo", {
  input: { text: "Narration text", voice: "Wise_Woman" },
});

// 3. Combine with ffmpeg
// ffmpeg -i video.mp4 -i audio.mp3 -c:v copy -c:a aac output.mp4
```

---

## Cost Estimation

| Model          | 5s clip    | 10s clip   | 15s clip   |
| -------------- | ---------- | ---------- | ---------- |
| veo-3.1-fast   | ~$0.15     | ~$0.30     | N/A (8s max)|
| grok-video     | ~$0.25     | ~$0.50     | ~$0.75     |
| minimax-video  | ~$0.25     | ~$0.50     | N/A (6s max)|
| kling-v3       | varies     | varies     | varies     |
| sora-2         | premium    | premium    | premium    |

---

## Output Handling

### Download Video

```javascript
import { writeFileSync } from "fs";

const response = await fetch(output);
const buffer = await response.arrayBuffer();
writeFileSync("output.mp4", Buffer.from(buffer));
```

### Verify Quality

```bash
# Check video properties with ffprobe
ffprobe -v quiet -print_format json -show_format -show_streams output.mp4
```

---

## Error Handling

| Error                    | Cause                        | Solution                     |
| ------------------------ | ---------------------------- | ---------------------------- |
| Generation timeout       | Complex prompt               | Simplify, reduce duration    |
| NSFW rejection           | Content policy               | Adjust prompt                |
| Low quality output       | Vague prompt                 | Add specific details         |
| Audio desync             | Wrong model                  | Use lip-sync model           |

---

## Integration with Studio Agents

- **Image Studio**: Generates source images for image-to-video
- **Audio Studio**: Creates narration for post-hoc audio
- **Visual Memory**: Stores reference images/videos
