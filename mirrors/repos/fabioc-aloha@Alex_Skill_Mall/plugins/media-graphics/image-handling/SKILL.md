---
type: skill
lifecycle: stable
inheritance: inheritable
name: "image-handling"
description: Right format, right size, right quality — plus AI image generation via Replicate
tier: extended
applyTo: '**/*image*,**/*handling*'
currency: 2026-04-22
lastReviewed: 2026-04-30
---

# Image Handling Skill


> Right format, right size, right quality.
> **Staleness Watch**: See [EXTERNAL-API-REGISTRY.md](../../EXTERNAL-API-REGISTRY.md) for source URLs and recheck cadence

## Format Selection

| Format | Best For                  | Supports                    |
| ------ | ------------------------- | --------------------------- |
| SVG    | Icons, logos, diagrams    | Infinite scale, animation   |
| PNG    | Screenshots, transparency | Lossless, alpha channel     |
| JPEG   | Photos, gradients         | Small size, no transparency |
| WebP   | Web images                | Best compression, both      |
| ICO    | Favicons                  | Multi-resolution            |

## Conversion Commands

```powershell
# SVG to PNG using sharp-cli (recommended)
# --density sets DPI for vector rendering (150 = crisp text)
npx sharp-cli -i input.svg -o output-folder/ --density 150 -f png

# Note: output must be a directory, filename preserved from input
npx sharp-cli -i banner.svg -o assets/ --density 150 -f png
# Creates: assets/banner.png

# ImageMagick (if installed)
magick input.svg -resize 512x512 output.png
magick input.png -quality 85 output.jpg

# Multiple sizes
foreach ($size in 16,32,64,128,256,512) {
  magick input.svg -resize ${size}x${size} "icon-$size.png"
}
```

## SVG to PNG Tips

- **Emojis don't convert well** - Use text-only or SVG icons
- **Use `--density 150+`** for crisp text rendering
- **Check file size** - README banners should be < 500KB

## GitHub README Images

```markdown
<!-- Absolute URL (always works) -->

![Banner](https://raw.githubusercontent.com/user/repo/main/assets/banner.svg)

<!-- Relative (works in repo) -->

![Banner](./assets/banner.png)

<!-- With dark/light variants -->
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="banner-dark.svg">
  <img src="banner-light.svg" alt="Banner">
</picture>
```

## Size Guidelines

| Use Case      | Max Size | Recommended |
| ------------- | -------- | ----------- |
| README banner | 500KB    | < 100KB     |
| Documentation | 200KB    | < 50KB      |
| Icons         | 50KB     | < 10KB      |
| Favicon       | 10KB     | < 5KB       |

## Optimization

```powershell
# PNG optimization
pngquant --quality=65-80 input.png -o output.png

# JPEG optimization
jpegoptim --max=85 input.jpg

# SVG optimization
npx svgo input.svg -o output.svg
```

## Visual Verification (VS Code 1.112+)

After generating or converting images, use `view_image` to verify output quality:

| Check                     | What to Look For                                    |
| ------------------------- | --------------------------------------------------- |
| SVG → PNG conversion      | Crisp text, no missing elements                     |
| AI-generated images       | Artifacts, spelling errors in text, character drift |
| Optimized images          | No visible quality loss from compression            |
| Face-reference generation | Likeness matches reference photos                   |

For batch operations, use VS Code's image carousel to compare multiple outputs side-by-side.

---

## Batch Processing

```bash
# Convert all PNGs in a folder (cross-platform)
for f in *.png; do magick "$f" -resize 256x256 "resized-$f"; done

# macOS -- sips (zero-install, ships with macOS)
sips -Z 256 *.png                          # Resize to max 256px
sips -s format jpeg input.png --out out.jpg # Convert PNG to JPEG
sips -g pixelHeight -g pixelWidth image.png # Read dimensions
```

### macOS `sips` (Scriptable Image Processing System)

macOS ships `sips` -- zero install, always available. Use for quick resize, format conversion, and metadata reads.

| Operation              | Command                                         | Notes                     |
| ---------------------- | ----------------------------------------------- | ------------------------- |
| Resize (max dimension) | `sips -Z 512 image.png`                         | Preserves aspect ratio    |
| Resize (exact)         | `sips -z 100 100 image.png`                     | Stretches to fit          |
| Convert format         | `sips -s format jpeg img.png --out img.jpg`     | png, jpeg, tiff, gif, bmp |
| Read dimensions        | `sips -g pixelHeight -g pixelWidth img.png`     | Useful in scripts         |
| Rotate                 | `sips -r 90 image.png`                          | Degrees clockwise         |
| Set DPI                | `sips -s dpiHeight 150 -s dpiWidth 150 img.png` | For print                 |

**Limitations**: No SVG rendering, no compositing, no layering, no text overlay. For those, use ImageMagick or Inkscape.

## Replicate Model Selection

Match user intent to the right model. When a user names a specific model or describes a need, use this table.

| Model                    | Replicate ID                         | Cost      | Best For                                                            | Trigger Words                                                    |
| ------------------------ | ------------------------------------ | --------- | ------------------------------------------------------------------- | ---------------------------------------------------------------- |
| **Flux Schnell**         | `black-forest-labs/flux-schnell`     | $0.003    | Fast iteration, prototyping                                         | "flux schnell", "quick image", "fast generation"                 |
| **Flux Dev**             | `black-forest-labs/flux-dev`         | $0.025    | High quality no-text images                                         | "flux dev", "high quality image"                                 |
| **Flux 1.1 Pro**         | `black-forest-labs/flux-1.1-pro`     | $0.04     | Production, photorealistic                                          | "flux pro", "flux 1.1", "production image"                       |
| **Flux 2 Pro**           | `black-forest-labs/flux-2-pro`       | ~$0.05+   | High quality with reference images (up to 8 refs), text rendering   | "flux 2", "flux-2-pro", "high quality refs"                      |
| **Flux 2 Max**           | `black-forest-labs/flux-2-max`       | higher    | Highest fidelity BFL output                                         | "flux 2 max", "highest quality"                                  |
| **Flux Kontext Pro**     | `black-forest-labs/flux-kontext-pro` | $0.04     | Text-based image editing, style transfer, outfit changes            | "edit image", "kontext", "change background", "outfit"           |
| **Flux Kontext Max**     | `black-forest-labs/flux-kontext-max` | $0.08     | Premium editing + improved typography in edited images              | "kontext max", "premium edit"                                    |
| **Ideogram v2**          | `ideogram-ai/ideogram-v2`            | $0.08     | Banner typography (proven, stable API)                              | "ideogram v2", "banner with text"                                |
| **Ideogram v3 Turbo**    | `ideogram-ai/ideogram-v3-turbo`      | $0.03     | Fast typography generation                                          | "ideogram turbo", "fast text image", "ideogram v3"               |
| **Ideogram v3 Balanced** | `ideogram-ai/ideogram-v3-balanced`   | $0.06     | Balanced quality/speed typography                                   | "ideogram balanced"                                              |
| **Ideogram v3 Quality**  | `ideogram-ai/ideogram-v3-quality`    | $0.09     | Highest quality typography                                          | "ideogram quality", "best ideogram"                              |
| **Nano-Banana Pro**      | `google/nano-banana-pro`             | $0.025    | Face-consistent portraits with reference photos (up to 14 refs), 4K | "nano-banana", "face consistency", "portrait", "reference photo" |
| **Nano-Banana 2**        | `google/nano-banana-2`               | $0.067/1K | Faster alternative to nano-banana-pro, same 14-ref API              | "nano-banana-2", "fast portrait", "gemini flash image"           |
| **SDXL**                 | `stability-ai/sdxl`                  | $0.009    | Classic diffusion, LoRA styles                                      | "sdxl", "stable diffusion", "stable diffusion xl"                |
| **Seedream 5 Lite**      | `bytedance/seedream-5-lite`          | varies    | 2K/3K with built-in reasoning, example-based editing                | "seedream", "bytedance", "high resolution"                       |
| **Nano-Banana**          | `google/nano-banana`                 | varies    | Gemini 2.5 latest image editing (98M+ runs)                         | "nano-banana", "gemini image edit"                               |
| **Imagen 4**             | `google/imagen-4`                    | varies    | Google flagship text-to-image (7.9M runs)                           | "imagen", "imagen 4", "google image"                             |
| **Imagen 4 Fast**        | `google/imagen-4-fast`               | lower     | Faster/cheaper Imagen 4 variant                                     | "imagen fast", "cheap imagen"                                    |
| **Imagen 4 Ultra**       | `google/imagen-4-ultra`              | higher    | Highest quality Imagen 4                                            | "imagen ultra", "best imagen"                                    |
| **Flux 2 Flex**          | `black-forest-labs/flux-2-flex`      | ~$0.05+   | Max-quality editing + **10** reference images                       | "flux flex", "flux 2 flex", "10 refs"                            |
| **Flux 2 Klein 4B**      | `black-forest-labs/flux-2-klein-4b`  | low       | Sub-second inference, distilled FLUX.2 (10M+ runs)                  | "flux klein", "fast flux", "real-time"                           |
| **Ideogram v2a**         | `ideogram-ai/ideogram-v2a`           | lower     | Faster+cheaper Ideogram v2 successor                                | "ideogram v2a"                                                   |
| **Ideogram Character**   | `ideogram-ai/ideogram-character`     | varies    | Character consistency from single reference image                   | "ideogram character", "character ref"                            |
| **Qwen Image 2 Pro**     | `qwen/qwen-image-2-pro`              | varies    | Next-gen image gen + editing, strong text rendering                 | "qwen image", "qwen image pro"                                   |
| **Recraft v4**           | `recraft-ai/recraft-v4`              | varies    | Design taste, strong composition, text rendering                    | "recraft", "design image", "art directed"                        |
| **Recraft v4 Pro**       | `recraft-ai/recraft-v4-pro`          | higher    | ~2048px resolution, print-ready                                     | "recraft pro", "print quality"                                   |
| **Recraft v4 SVG**       | `recraft-ai/recraft-v4-svg`          | varies    | Production-ready SVG vector images                                  | "recraft svg", "vector", "generate svg"                          |
| **Recraft v4 Pro SVG**   | `recraft-ai/recraft-v4-pro-svg`      | $0.30     | High quality SVG with detailed paths                                | "recraft pro svg", "detailed svg"                                |

### Model Selection Guide

- **"quick" / "test" / "prototype"** → Flux Schnell ($0.003, 4 steps)
- **"high quality" / "production"** → Flux 1.1 Pro ($0.04) or Flux 2 Pro for multi-ref
- **Text must appear in the image** → Ideogram v3 Turbo ($0.03) or v3 Quality ($0.09); v2 still works
- **Simple/fast text in image** → Ideogram v3 Turbo ($0.03, fastest + cheapest)
- **Edit an existing image** → Flux Kontext Pro ($0.04, text-prompted editing)
- **Premium image editing** → Flux Kontext Max ($0.08, better typography in edits)
- **Painting style / custom LoRA** → SDXL or Flux Dev with LoRA weights
- **Largest / highest resolution output** → Seedream 5 Lite (up to 3K) or Nano-Banana Pro (up to 4K)
- **README banner (default, SVG)** → Recraft v4 SVG (`recraft-ai/recraft-v4-svg`, native SVG output, scalable); see `ai-generated-readme-banners` skill
- **README banner (premium SVG)** → Recraft v4 Pro SVG ($0.30, detailed vector paths)
- **README banner (raster, with text)** → Ideogram v3 Turbo `3:1` ratio ($0.03)
- **README banner (raster, no text)** → Flux 1.1 Pro with `21:9` ratio
- **Face-consistent portraits (fast)** → Nano-Banana 2 ($0.067/1K, `image_input` array, same API as Pro)
- **Face-consistent portraits (quality)** → Nano-Banana Pro ($0.025, `image_input` up to 14 refs)
- **Multi-reference high quality** → Flux 2 Pro (~$0.05+, `input_images` up to 8 refs) or Flux 2 Flex (up to 10 refs)
- **Highest fidelity** → Flux 2 Max
- **Character consistency (single ref)** → Ideogram Character
- **Google flagship** → Imagen 4 (standard), Imagen 4 Ultra (highest quality), Imagen 4 Fast (budget)
- **Sub-second real-time** → Flux 2 Klein 4B (distilled, 10M+ runs)
- **Vector/SVG logo or graphic** → Recraft v4 SVG (native SVG output) or Recraft v4 Pro SVG ($0.30)
- **Art-directed design** → Recraft v4 (strong composition, design taste)
- **Short video clip (≤8s)** → Veo-3.1-fast (faster/cheaper successor to Veo-3, auto audio)
- **Longer video (≤15s)** → Grok Video (`xai/grok-imagine-video`, $0.05/sec, auto audio + lip-sync)
- **Cinematic video** → Kling v3 (`kwaivgi/kling-v3-video`, 1080p, multi-shot, ≤15s)
- **Realistic home-video quality** → Sora-2 (`openai/sora-2`, synced audio)

### LoRA Support (Flux Dev / SDXL)

Both Flux Dev and SDXL accept LoRA weights:

```javascript
// Replicate format
extra_lora: "fofr/flux-pixar-cars";
// HuggingFace format
extra_lora: "huggingface.co/owner/model-name";
// CivitAI format
extra_lora: "civitai.com/models/<id>";
// Direct URL
extra_lora: "https://example.com/weights.safetensors";
```

### Aspect Ratio Reference

| Ratio  | Models     | Use Case                    |
| ------ | ---------- | --------------------------- |
| `21:9` | Flux (all) | Ultra-wide README banner    |
| `3:1`  | Ideogram   | Wide banner with typography |
| `16:9` | All        | Standard widescreen         |
| `1:1`  | All        | Square, avatar, icon        |
| `9:16` | All        | Mobile, portrait            |

## Face Reference Models

For character/portrait consistency across multiple generations, use models that accept reference images:

### Nano-Banana Pro (Recommended for Portraits)

```javascript
const output = await replicate.run("google/nano-banana-pro", {
  input: {
    prompt: "Description of desired scene",
    image_input: referenceImageURIs, // Array of data URIs (up to 14)
    aspect_ratio: "3:4",
    output_format: "png",
  },
});
```

**Key**: `image_input` accepts an **array** of data URIs. More references = better face consistency.

### Flux 2 Pro (Higher Quality Alternative)

```javascript
const output = await replicate.run("black-forest-labs/flux-2-pro", {
  input: {
    prompt: "Description of desired scene",
    input_images: referenceImageURIs, // Array of data URIs (up to 8)
    aspect_ratio: "3:4",
    output_format: "png",
  },
});
```

**Key**: `input_images` (not `image_input`) — different parameter name from nano-banana.

### Preparing Reference Photos

```powershell
# Resize to 512px @ 85% quality for optimal API performance
magick input.jpg -resize 512x512 -quality 85 output.jpg

# Convert to base64 data URI (for embedding in visual memory)
[Convert]::ToBase64String([IO.File]::ReadAllBytes("photo.jpg")) | Set-Clipboard
```

Optimal reference specs: 512px longest edge, 85% JPEG quality, ~40-80KB per photo.

---

## Video Generation Models

Generate video from a still image or text prompt via Replicate. All video models support image-to-video workflows.

| Model             | Replicate ID                  | Cost        | Duration         | Audio                          | Best For                               |
| ----------------- | ----------------------------- | ----------- | ---------------- | ------------------------------ | -------------------------------------- |
| **Veo-3**         | `google/veo-3`                | $0.50/video | 4, 6, or 8s only | ✅ Auto                        | Short clips with synced audio          |
| **Veo-3.1-fast**  | `google/veo-3.1-fast`         | lower       | 4-8s             | ✅ Context-aware audio         | Newer/faster Veo 3, last-frame support |
| **Veo-3.1**       | `google/veo-3.1`              | higher      | 4-8s             | ✅ Context-aware audio         | Highest fidelity successor to Veo 3    |
| **Grok Video**    | `xai/grok-imagine-video`      | $0.05/sec   | 1-15s            | ✅ Auto (music, SFX, lip-sync) | Longer videos, best audio              |
| **Kling v3**      | `kwaivgi/kling-v3-video`      | $0.22/sec   | 3-15s            | ✅ Native                      | Cinematic quality, 1080p, multi-shot   |
| **Kling v3 Omni** | `kwaivgi/kling-v3-omni-video` | varies      | 3-15s            | ✅ Native                      | Multi-modal: text, ref image, editing  |
| **Sora-2**        | `openai/sora-2`               | varies      | flexible         | ✅ Synced                      | Home-video realism, flexible prompting |
| **WAN 2.5 fast**  | `wan-video/wan-2.5-t2v-fast`  | low         | 5-10s            | ❌                             | Open-source, fast, cost-effective      |

### Duration Constraints

| Model      | Min | Max | Notes                                               |
| ---------- | --- | --- | --------------------------------------------------- |
| Veo-3      | 4s  | 8s  | **Only accepts 4, 6, or 8** — other values rejected |
| Grok Video | 1s  | 15s | Flexible, any integer                               |
| Kling v3   | 3s  | 15s | Modes: `standard` (720p), `pro` (1080p)             |

### Video Generation Pattern

Typical workflow: generate a still image first, then animate it:

```javascript
// Step 1: Generate still image
const image = await replicate.run("google/nano-banana-pro", {
  input: { prompt: "Person smiling at camera", image_input: refs },
});

// Step 2: Animate to video
const video = await replicate.run("google/veo-3", {
  input: {
    prompt: "Head turns slowly, smile widens, warm natural lighting",
    image: imageUrl,
    duration: 6,
  },
});
```

---

## Cloud TTS Models (Replicate)

For content creation (audiobooks, narration, voice cloning), Replicate offers paid cloud TTS models.

| Model                | Replicate ID                   | Cost            | Voice Cloning  | Languages | Best For                         |
| -------------------- | ------------------------------ | --------------- | -------------- | --------- | -------------------------------- |
| **Speech 2.8 Turbo** | `minimax/speech-2.8-turbo`     | $0.06/1k tokens | ❌             | 40+       | Fast, expressive, many voices    |
| **Speech 2.8 HD**    | `minimax/speech-2.8-hd`        | higher          | ❌             | 40+       | Studio-grade high-fidelity audio |
| **Chatterbox Turbo** | `resemble-ai/chatterbox-turbo` | $0.025/1k chars | ✅ (5s sample) | English   | Voice cloning, natural pauses    |
| **Qwen TTS**         | `qwen/qwen3-tts`               | $0.02/1k chars  | ✅             | 10        | Voice design from description    |

### Voice Presets

**Speech Turbo**: `Wise_Woman`, `Deep_Voice_Man`, `Casual_Guy`, `Lively_Girl`, `Young_Knight`, `Abbess`, + 6 more
**Chatterbox**: `Andy`, `Luna`, `Ember`, `Aurora`, `Cliff`, `Josh`, `William`, `Orion`, `Ken`
**Qwen TTS**: `Aiden`, `Dylan`, `Eric`, `Serena`, `Vivian`, + 4 more

### Emotion Control (Speech Turbo)

Supported emotions: `auto`, `happy`, `sad`, `angry`, `fearful`, `disgusted`, `surprised`

### Voice Cloning (Chatterbox / Qwen)

Provide a 5+ second audio sample to clone a voice:

```javascript
const output = await replicate.run("resemble-ai/chatterbox-turbo", {
  input: {
    text: "Content to speak in the cloned voice",
    audio_prompt: referenceAudioDataURI, // 5+ seconds WAV/MP3
  },
});
```

### Voice Design (Qwen TTS)

Create a voice from a natural language description:

```javascript
const output = await replicate.run("qwen/qwen3-tts", {
  input: {
    text: "Content to speak",
    tts_mode: "voice_design",
    voice_description:
      "A warm, friendly female voice with a slight British accent",
  },
});
```

### When to Use Each TTS Model

| Scenario                        | Recommended      | Why                               |
| ------------------------------- | ---------------- | --------------------------------- |
| Create audiobook narration      | Speech 2.8 HD    | Studio-grade quality              |
| Fast narration, many languages  | Speech 2.8 Turbo | 40+ languages, emotion control    |
| Clone a specific voice          | Chatterbox Turbo | 5s sample, English                |
| Design a voice from description | Qwen TTS         | Natural language voice spec       |
| Generate voice for video        | Speech 2.8 Turbo | Emotion control, syncs with video |

---
