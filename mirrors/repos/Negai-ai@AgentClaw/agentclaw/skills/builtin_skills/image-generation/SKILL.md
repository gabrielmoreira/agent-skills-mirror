---
name: image-generation
description: Generate, edit, and iterate raster images from text prompts or reference images with GPT Image, Nano Banana, or Seedream. Use for visual asset creation, concept art, product/mockup imagery, style exploration, thumbnails, illustrations, and image transformation workflows across image provider APIs.
---

# Image Generation Skill

Use this skill for image creation and image editing work that should call an image provider API and save usable raster files.

## Provider Selection

Current complete provider:

- OpenAI GPT Image Image API: read `references/openai.md`; use `scripts/openai_generate_image.py` for repeatable command-line generation and editing. This runner also accepts an OpenAI-compatible `base_url` for GPT Image compatible providers.
- Nano Banana image generation: read `references/nano_banana.md`; use `scripts/nano_banana_generate_image.py` for Nano Banana 2, Nano Banana Pro, and Nano Banana generation/editing.
- Seedream image generation on Volcengine Ark: read `references/seedream.md`; use `scripts/seedream_generate_image.py` for Seedream 5 text-to-image, image-to-image, coherent image groups, streaming, and web search.

Reserved provider integration:

- Future providers should add one `references/<provider>.md` file and one `scripts/<provider>_generate_image.py` runner following `references/provider_contract.md`.

## Workflow

1. Capture the visual brief: subject, style, composition, aspect ratio, output count, quality, format, destination folder, and any reference images.
2. Pick the provider. OpenAI is the supported default in this skill.
3. Check the provider API key before calling the script. If the key is missing, tell the user the exact variable to configure; after the user provides or confirms the key, write/update it in the project `.env` and update the current temporary environment before retrying.
4. Read the matching provider reference when API parameters, edits, masks, streaming, or model limits matter.
5. Use the provider script for deterministic file output when possible; otherwise write a small one-off call using the same output contract.
6. Save generated files to the requested path, or to `generated_images` when no path is specified.
7. Return the saved file paths, `output_dir`, provider/model, size/quality/format, revised prompt when available, and any provider response ID. For user-visible Markdown images, use browser-safe URLs only; if the script returns local `output_paths`, call `create_download_url` for each image and use the returned URL instead of embedding local paths.

## API Key Handling

Required keys by provider:

- OpenAI official or compatible GPT Image: `OPENAI_IMAGE_KEY`. Compatible services may also need the optional endpoint override `OPENAI_BASE_URL` or `--base-url`.
- Nano Banana: `GOOGLE_IMAGE_KEY`.
- Seedream on Volcengine Ark: `ARK_API_KEY`.

The bundled runners automatically load `.env` before reading these variables. They check `AGENTCLAW_PROJECT_DIR/.env`, the current working directory `.env`, and the AgentClaw project `.env`, then copy loaded values into the script process environment without overriding already exported variables.

When a selected provider key is not configured, tell the user which key is needed and wait for the user to provide or configure it. After the user provides the value, update the project `.env` and the current temporary environment for this session before rerunning the provider script. Keep secrets out of prompts, logs, references, tests, and generated reports.

All bundled runners default to `generated_images` and include `output_dir` plus `absolute_output_dir` in their JSON result. These are local filesystem directories, not browser URLs.

## OpenAI Quick Start

```bash
python agentclaw/skills/builtin_skills/image-generation/scripts/openai_generate_image.py \
  --prompt "A clean product hero image of a compact desktop AI assistant device" \
  --output-dir generated_images \
  --model gpt-image-2
```

For explicit GPT Image output parameters:

```bash
python agentclaw/skills/builtin_skills/image-generation/scripts/openai_generate_image.py \
  --prompt "A polished app icon for AgentClaw, sharp claw mark plus workflow nodes" \
  --model gpt-image-2 \
  --size 1024x1024 \
  --quality high \
  --format png
```

For an OpenAI-compatible image service:

```bash
python agentclaw/skills/builtin_skills/image-generation/scripts/openai_generate_image.py \
  --prompt "A square face icon in a clean 3D style" \
  --base-url https://api.squarefaceicon.org/v1 \
  --model gpt-image-2 \
  --size 1024x1024
```

For an edit or reference-image composition:

```bash
python agentclaw/skills/builtin_skills/image-generation/scripts/openai_generate_image.py \
  --prompt "Create a cohesive product bundle image using these reference items" \
  --input-image body-lotion.png \
  --input-image soap.png \
  --output-dir generated_images
```

For a masked edit:

```bash
python agentclaw/skills/builtin_skills/image-generation/scripts/openai_generate_image.py \
  --prompt "Replace the selected area with a small indoor pool" \
  --input-image room.png \
  --mask-image mask.png
```

## Nano Banana Quick Start

```bash
python agentclaw/skills/builtin_skills/image-generation/scripts/nano_banana_generate_image.py \
  --prompt "A professional product photo of an AI automation workspace on a clean desk" \
  --banana nano-banana-2 \
  --aspect-ratio 16:9 \
  --image-size 1K \
  --output-dir generated_images
```

For professional assets or stronger text rendering:

```bash
python agentclaw/skills/builtin_skills/image-generation/scripts/nano_banana_generate_image.py \
  --prompt "A premium magazine cover with the title AgentClaw, no other cover text" \
  --banana nano-banana-2 \
  --aspect-ratio 3:4 \
  --image-size 2K
```

## Seedream Quick Start

```bash
python agentclaw/skills/builtin_skills/image-generation/scripts/seedream_generate_image.py \
  --prompt "A cinematic wide-angle image of a vintage train bursting out of a black hole" \
  --seedream seedream-5 \
  --size 2K \
  --output-dir generated_images
```

For a coherent group:

```bash
python agentclaw/skills/builtin_skills/image-generation/scripts/seedream_generate_image.py \
  --prompt "Generate four coherent illustrations of the same courtyard across spring, summer, autumn, and winter" \
  --seedream seedream-5 \
  --sequential-image-generation auto \
  --max-images 4 \
  --stream
```

For image-to-image:

```bash
python agentclaw/skills/builtin_skills/image-generation/scripts/seedream_generate_image.py \
  --prompt "Use this logo as reference and create outdoor sports brand visuals" \
  --input-image logo.png \
  --seedream seedream-5 \
  --size 2K
```

## Notes

- Use one key variable per provider: `OPENAI_IMAGE_KEY`, `GOOGLE_IMAGE_KEY`, or `ARK_API_KEY`.
- For OpenAI-compatible GPT Image services, use `OPENAI_BASE_URL` or pass `--base-url`.
- For edits with reference images or masks, keep all source files local and pass their paths explicitly.
- Prefer PNG for transparent or lossless assets, JPEG for faster photo-style outputs, and WebP for compact web delivery.
- Do not display local paths such as `generated_images/...` or `absolute_output_dir` inside Markdown image links. The dashboard will resolve relative paths under `/dashboard/`, for example `/dashboard/generated_images/...`, which is not a served file URL. Use `create_download_url`, `public_urls`, `image_markdown`, or signed `/api/files/...?token=...` URLs for display.
