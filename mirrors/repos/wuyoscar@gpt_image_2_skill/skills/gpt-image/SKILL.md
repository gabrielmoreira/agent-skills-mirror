---
name: gpt-image
description: General-purpose image generation and reference-image editing via OpenAI GPT Image 2 (`gpt-image-2`). Wraps the two official endpoints from the OpenAI cookbook — `/v1/images/generations` for text-to-image and `/v1/images/edits` for reference-image edits (including alpha-channel masks). Use whenever an agent or user needs to (a) generate an image from a text prompt, (b) restyle or transform an image using a reference image, (c) combine multiple reference images, (d) inpaint a region using a PNG mask, or (e) render dense typography / Chinese text. Reads `OPENAI_API_KEY` from env; writes PNG/JPEG/WebP to disk. Optional Scale references under `references/` for the full prompt-gallery atlas, cross-cutting prompt craft, and official OpenAI parameter guidance.
---

# gpt-image

General image generation/editing CLI for OpenAI's `gpt-image-2`. Designed for skill-capable agents: all API parameters are first-class flags, defaults are sane, output is a file on disk. Use it whenever a runtime or user asks for image generation, reference-image editing, inpainting, dense typography, or gallery-informed prompt drafting.

## One-line usage

```bash
# As an agentic skill plugin (installed through your runtime/plugin manager):
uv run "$CLAUDE_PLUGIN_ROOT/skills/gpt-image/scripts/generate.py" -p "PROMPT" [-f OUT] [-i REF...] [-m MASK] [options]

# As a direct CLI (installed via uvx or uv tool install):
uvx --from git+https://github.com/wuyoscar/gpt_image_2_skill gpt-image -p "PROMPT" [-f OUT] [-i REF...] [-m MASK] [options]

# Or once installed globally:
gpt-image -p "PROMPT" [-f OUT] [-i REF...] [-m MASK] [options]
```

Reads `OPENAI_API_KEY` from env. Writes to `OUT` (or auto-named `YYYY-MM-DD-HH-MM-SS-<slug>.png` in `./fig/` or cwd). Prints output path(s) on stdout. Exit 0 on success, 1 on API error, 2 on bad args / missing key.

## CLI flags (complete reference)

| Flag | Type / Values | Default | Applies to | Description |
|------|---------------|---------|------------|-------------|
| `-p, --prompt` | str | — required | both | Text prompt for generation, or edit instruction. |
| `-f, --file` | path | auto | both | Output path. Auto-gen if omitted. Extension follows `--format`. |
| `-i, --image` | path (repeatable) | — | edits | Reference image(s). Presence routes through `/v1/images/edits` (the official endpoint per the OpenAI cookbook). |
| `-m, --mask` | path | — | edits | Alpha-channel PNG mask. Opaque pixels are preserved, transparent pixels are regenerated. Edits endpoint only — requires `-i`. |
| `--input-fidelity` | `low` \| `high` | — | edits | Controls how closely the output tracks the reference. Supported on `gpt-image-1` and `gpt-image-1.5`. `gpt-image-2` rejects this parameter, so the CLI strips it locally before calling the API. |
| `--model` | str | `gpt-image-2` | both | Model ID. Fallbacks: `gpt-image-1.5`, `gpt-image-1`, `gpt-image-1-mini`. |
| `--size` | literal / shortcut | `1024x1024` | both | Literals: `1024x1024`, `1536x1024`, `1024x1536`, `2048x2048`, `2048x1152`, `3840x2160`, `2160x3840`, or any 16-px multiple up to 3840 max edge (3:1 ratio cap, 655k–8.3M total pixels). Shortcuts: `1k` `2k` `4k` `portrait` `landscape` `square` `wide` `tall`. |
| `--quality` | `auto` \| `low` \| `medium` \| `high` | `high` | both | Cost roughly 10× per step. `low` ≈ $0.005/img, `medium` ≈ $0.04, `high` ≈ $0.17. CLI default stays `high`, but agents should choose deliberately: `low` for cheap drafts / large sweeps, `medium` for normal exploration, `high` for final assets, typography, Chinese text, diagrams, or anything shipping-facing. |
| `-n, --n` | int | `1` | both | Number of images to return. `>1` suffixes filenames `_0`, `_1`, … |
| `--background` | `auto` \| `opaque` | API default | generations only | `opaque` disables transparent background. |
| `--moderation` | `auto` \| `low` | `low` | generations only | Defaults to `low` here for broader prompt exploration. Switch to `auto` if you want the stricter API-side default. |
| `--format` | `png` \| `jpeg` \| `webp` | `png` | both | Response encoding. |
| `--compression` | int 0–100 | — | both | JPEG/WebP compression. Ignored for PNG. |
| `--user` | str | — | both | Optional end-user identifier for OpenAI abuse tracking. |

## Budget / quality policy for agents

Use `--quality` as the budget dial. There is no separate `--budget` flag in this CLI.

- `low` — cheap draft mode. Use for broad prompt exploration, collecting many variants, gallery mining, rough composition checks, or when the user explicitly wants low cost / fast iteration.
- `medium` — balanced mode. Use for normal one-off exploration, style probing, or cases where readability matters but the output is not yet final.
- `high` — shipping / report mode. Use for Chinese text, posters, infographics, paper figures, dense labels, multi-panel layouts, banners, or any asset likely to be kept.

Rule of thumb for autonomous agents:
- If the user asks for **many variants**, **cheap**, **draft**, **explore**, or **collect**, start with `low`.
- If the user asks for **polished but still exploratory**, use `medium`.
- If the user asks for **final**, **fancy**, **hero**, **paper figure**, **poster**, **diagram**, or **exact text**, use `high`.
- If unsure, keep the CLI default `high` for text-heavy / delivery-facing outputs; otherwise prefer `medium` during exploration.

## Endpoint selection (official OpenAI cookbook pattern)

| Mode | Trigger | Endpoint |
|------|---------|----------|
| Generate from prompt | no `-i` | `POST /v1/images/generations` (JSON body) |
| Edit / reference-based | `-i` one or more times | `POST /v1/images/edits` (multipart form) |
| Inpaint with mask | `-i` + `-m` | `POST /v1/images/edits` with a `mask` file |

Both endpoints accept `gpt-image-2` as of April 2026 — verified against OpenAI's [official cookbook prompting guide](https://github.com/openai/openai-cookbook/blob/main/examples/multimodal/image-gen-models-prompting-guide.ipynb). The skill uses the official `openai` Python SDK under the hood (`from openai import OpenAI; client.images.generate(...)` / `client.images.edit(...)`) — the CLI is a thin wrapper that exposes every SDK parameter as a flag.

**Content policy:** gpt-image-2 enforces its own content rules on the edits endpoint. Real-person-likeness edits usually refuse (400 error with a moderation message). The skill surfaces the response body verbatim on stderr and exits 1.

## Canonical examples

```bash
# 1. Vanilla generate, 1K square, auto quality
gpt-image -p "a photorealistic convenience store at 10pm"

# 2. 2K portrait poster with exact Chinese text, high quality
gpt-image \
  -p 'Design a 3:4 tea poster. Exact copy: "山川茶事" / "冷泡系列" / "中杯 16 元"' \
  --size portrait --quality high -f poster.png

# 3. 4-image grid, transparent background disabled, webp
gpt-image -p "isometric furniture, minimalist" \
  -n 4 --background opaque --format webp --compression 85

# 4. Edit / colorize existing image
gpt-image -p "colorize this manga page and translate to Chinese" \
  -i page.jpg -f colored.png

# 5. Multi-reference brand collab
gpt-image -p "77 (the cat) × KFC employee poster" \
  -i cat.png -i kfc_logo.png -f collab.png --size portrait

# 6. Masked inpaint — replace sky only
gpt-image -p "replace sky with aurora, keep foreground intact" \
  -i photo.jpg -m sky_mask.png -f aurora.png --quality high

# 7. 4K widescreen render
gpt-image -p "cinematic Shanghai skyline at dusk" \
  --size 4k --quality high -f skyline.png
```

## Response handling

- API returns `data: [{ b64_json: "…" }]` by default; the script decodes base64 and writes bytes.
- If the API returns `url` instead, the script GETs the URL and writes the downloaded bytes.
- With `-n > 1`, files are suffixed: `out.png` → `out_0.png`, `out_1.png`, …

## Error surface

| Condition | Exit | stderr |
|-----------|------|--------|
| `OPENAI_API_KEY` unset | 2 | `error: OPENAI_API_KEY not set. ...` |
| `--mask` without `-i` | 2 | `error: --mask requires --image (edits endpoint only)` |
| `-i` or `-m` path missing | 2 | `error: --image not found: PATH` |
| OpenAI returns non-2xx | 1 | `error: <status> from OpenAI: <body>` (first 2000 chars of response) |
| Response has no image data | 1 | `error: no image data in response: <json>` |

When an agent hits exit 1, it should surface the response body verbatim — it usually names the problem (rate limit, moderation block, invalid size).

## Size picking guide

| Intent | Size |
|--------|------|
| Default / social square | `1024x1024` (1k) |
| Mobile screenshot, portrait poster, beauty/skincare | `1024x1536` (portrait) |
| Landscape photo, gameplay screenshot | `1536x1024` (landscape) |
| Hi-res print, paper figure | `2048x2048` (2k) |
| Widescreen cinematic, dashboard hero | `3840x2160` (4k) |
| Tall story banner, vertical video thumbnail | `2160x3840` (tall) |

## Scale references (load for prompt leverage, not just CLI calls)

The CLI is only the execution layer. The main value of this skill is the prompt Scale: agents should use the reference files to read concrete gallery patterns before drafting or generating images.

- `references/gallery.md` — routing index for the split 162-prompt Reference Gallery Atlas. The Reference Gallery is canonical; README is only a selected visual showcase. It maps each category to `references/gallery-<category>.md`; load the index first, then only the relevant category file(s) to avoid context bloat. Use this when the user asks for a style/category we already cover, wants diverse ideas, asks to extend the gallery, or needs a prompt that should inherit the repo's collected taste.
- `references/craft.md` — expanded 19-section prompt-writing checklist distilled from the gallery: Scale-first usage, exact text, JSON/config-style prompts, fixed-region infographics, data visualization mini-schemas, research/diagram grammar, UI specs, multi-panel consistency, reference-based unlocks, three-glances test, edit invariants, dense text, and category mini-schemas. Load this when improving or debugging a prompt.
- `references/openai-cookbook.md` — verbatim Markdown capture of OpenAI's [official GPT Image prompting guide](https://github.com/openai/openai-cookbook/blob/main/examples/multimodal/image-gen-models-prompting-guide.ipynb). Load this when the user asks about official parameter semantics, endpoint behavior, migration, or model capabilities.

Reference loading policy:
- For generation/editing requests, first read `references/gallery.md` only as the category index, then load the relevant `references/gallery-<category>.md` file(s); do not load every category and do not rely on generic one-line prompting if the atlas contains a matching pattern.
- Use `craft.md` to refine structure after selecting a gallery pattern.
- Use `openai-cookbook.md` for authoritative API/model questions or when the gallery does not cover the requested workflow.
- Preserve `Curated` versus `Author + Source` metadata when adapting examples. Add new collected prompts to the Reference Gallery first; promote only representative examples to README.

## Attribution

License: CC BY 4.0 for prompt patterns and gallery documentation unless a referenced upstream source states otherwise. Prompt patterns are curated from the original repo gallery, OpenAI Cookbook, and community prompt collections credited in the README. Individual source metadata is preserved per entry in the split `references/gallery-*.md` category files where applicable.
