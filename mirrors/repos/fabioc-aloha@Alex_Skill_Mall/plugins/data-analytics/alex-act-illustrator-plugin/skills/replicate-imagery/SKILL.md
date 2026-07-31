---
name: "replicate-imagery"
description: "Route AI image generation and editing requests to Replicate (FLUX, Ideogram, Recraft, SDXL, imagen) via the bundled `replicate` MCP server. Use when a document, book, or report needs an illustration, hero image, character/concept art, photorealistic scene, or style-transferred image that neither Flint (data charts), Mermaid (technical diagrams), nor svg-banner (brand banners) can produce. Composes with Replicate's upstream agent skills (prompt-images, find-models, run-models, compare-models, prompt-videos) installable via `npx skills add replicate/skills`. Requires `REPLICATE_API_TOKEN`."
lastReviewed: 2026-07-30
---

# Replicate Imagery

Thin routing + brand-alignment skill for AI image generation and editing on Replicate. Delegates substantive prompting guidance to Replicate's upstream `prompt-images` skill and model discovery to the `replicate` MCP server. This skill is the plugin's entry point that says WHEN to reach for Replicate and HOW it composes with the plugin's other visual capabilities.

## When to use this skill

You want to add a visual artifact to a doc / book / report and none of these fit:

| Artifact                                            | Not this skill — use instead                                        |
| --------------------------------------------------- | ------------------------------------------------------------------- |
| Data chart (bar, line, scatter, distribution, KPI)  | [`flint-chart`](../flint-chart/SKILL.md)                            |
| Technical / architectural / flow diagram            | `markdown-mermaid` (Alex_ACT_Steward baseline)                      |
| Brand banner (hero header for a doc)                | `svg-banner` (Alex_ACT_Steward baseline)                            |
| Deterministic hand-authored figure (dataset-backed) | [`figure-generator`](../figure-generator/SKILL.md)                  |
| Print-quality book figure with typography grammar   | [`print-svg-style-guide`](../print-svg-style-guide/SKILL.md)        |

Fires when the goal is one of:

- **Illustrations** — decorative or narrative images for chapters, sections, blog posts
- **Hero images** — top-of-page visuals for docs shared externally
- **Character / concept art** — figures for creative writing, book covers, brand mascots
- **Photorealistic scenes** — mockups, product-in-context imagery, scene composition
- **Style-transferred images** — restyling existing images to match a brand aesthetic
- **Image editing** — inpaint, background removal, upscaling, prompt-driven edits

## Prerequisites

1. **`REPLICATE_API_TOKEN` environment variable** — get one at [replicate.com/account/api-tokens](https://replicate.com/account/api-tokens). Set in your shell env so the MCP server picks it up:

   ```pwsh
   # PowerShell (per-session)
   $env:REPLICATE_API_TOKEN = 'r8_...'

   # PowerShell (persistent, user scope)
   [System.Environment]::SetEnvironmentVariable('REPLICATE_API_TOKEN', 'r8_...', 'User')
   ```

   ```bash
   # bash / zsh
   export REPLICATE_API_TOKEN=r8_...
   ```

   Do NOT commit the token to any config file. The plugin's shipped `.vscode/mcp.json` references it via `${env:REPLICATE_API_TOKEN}` so it stays out of source control.

2. **The `replicate` MCP server** — ships in this plugin's `.vscode/mcp.json`. Starts automatically on first `replicate` tool invocation. Package: [`replicate-mcp`](https://www.npmjs.com/package/replicate-mcp).

3. **Upstream Replicate skills (recommended, one-shot)** — install once per project:

   ```pwsh
   npx skills add replicate/skills
   ```

   Pulls in five agent skills authored by Replicate covering the substantive prompting knowledge this thin skill delegates to:

   | Upstream skill | What it covers |
   | --- | --- |
   | `find-models` | Searching models, browsing collections, reading schemas, picking the right model |
   | `compare-models` | Evaluating by cost, speed, quality, capabilities |
   | `run-models` | Creating predictions, polling, webhooks, streaming, file handling, multi-model workflows |
   | `prompt-images` | Prompting techniques: photographic language, text rendering, style transfer, character consistency, inpainting |
   | `prompt-videos` | Prompting techniques for video: scene, camera motion, audio/dialogue, time-coded multi-shot, style control |

   Update with `npx skills update`. Remove with `npx skills remove replicate`.

## Model selection

Replicate hosts thousands of models. Working set for illustration as of 2026-07:

| Need | Recommended model | Notes |
| --- | --- | --- |
| Fast, cheap illustrations | [`black-forest-labs/flux-schnell`](https://replicate.com/black-forest-labs/flux-schnell) | Very fast, low cost; iterate freely |
| Higher quality, still fast | [`black-forest-labs/flux-dev`](https://replicate.com/black-forest-labs/flux-dev) | Balance of quality and speed |
| Premium quality, hero images | [`black-forest-labs/flux-1.1-pro`](https://replicate.com/black-forest-labs/flux-1.1-pro) or `flux-1.1-pro-ultra` | Premium; `ultra` variant supports very high resolution |
| Great text-in-image rendering | [`ideogram-ai/ideogram-v3`](https://replicate.com/ideogram-ai/ideogram-v3) | Best for images with readable typography (signage, quotes, labels) |
| Vector-style, brand-consistent | [`recraft-ai/recraft-v3`](https://replicate.com/recraft-ai/recraft-v3) | Cleaner, designed feel; respects color guidance well |
| Photorealistic scenes | [`google/imagen-4`](https://replicate.com/google/imagen-4) | Google's photorealism model |
| Image editing via prompt | [`black-forest-labs/flux-kontext-pro`](https://replicate.com/black-forest-labs/flux-kontext-pro) | Edit existing images with natural-language instructions |
| Inpainting (fill masked region) | [`black-forest-labs/flux-fill-pro`](https://replicate.com/black-forest-labs/flux-fill-pro) | Mask + prompt → composited output |
| Upscaling | [`philz1337x/clarity-upscaler`](https://replicate.com/philz1337x/clarity-upscaler) or [`lucataco/real-esrgan`](https://replicate.com/lucataco/real-esrgan) | Real-ESRGAN is the classic cheap option; Clarity has finer detail preservation |
| Background removal | [`851-labs/background-remover`](https://replicate.com/851-labs/background-remover) | Alpha channel output |

**Discover current models** via the MCP tool: ask the agent "search Replicate for `<capability>` models" — the `replicate` MCP calls `models.search` under the hood and returns current results with cost, hardware, and capability metadata. Per-model page at `replicate.com/<owner>/<model>` shows pricing and interactive playground.

Model list evolves fast. If a recommendation here is stale, the upstream `find-models` skill has current model-discovery guidance and the MCP does live discovery.

## Brand alignment

For illustrations that should feel on-brand with the Alex ACT constellation, weave color hex codes from the constellation's [`brand-palette.json`](https://github.com/fabioc-aloha/Alex_ACT_Steward/blob/main/.github/config/brand-palette.json) into the prompt. Example:

> "A minimalist illustration of a person coding at a desk, dominant color emerald `#10b981` with deep slate `#0f172a` accents, cyan `#06b6d4` highlight on the monitor, clean vector style, no text."

Per-project brands: use that project's own `brand-palette.json` (heirs override — see this plugin's README `Brand palette` section for the swatch and configuration key mapping).

Best model choices for brand-consistent output:

- `recraft-ai/recraft-v3` — strongest color-guidance adherence, vector-friendly
- `ideogram-ai/ideogram-v3` — respects color hints, best if the image includes readable text
- `black-forest-labs/flux-*` — interprets colors well but with less strict adherence

## Output handling

- Default output location: `assets/generated/<slug>-<timestamp>.png`
- Consider adding `assets/generated/` to `.gitignore` — ML-generated images are large and often iterative
- Keep curated finals in `assets/` (not `assets/generated/`)
- For book / report embedding, downscale to target print DPI before committing to keep the git tree light

## Cost awareness

Replicate charges per prediction. Approximate costs for image generation as of 2026-07 (verify current at `replicate.com/<model>`):

| Model                              | Approx. cost per image  |
| ---------------------------------- | ----------------------- |
| `black-forest-labs/flux-schnell`   | ~$0.003                 |
| `black-forest-labs/flux-dev`       | ~$0.025                 |
| `black-forest-labs/flux-1.1-pro`   | ~$0.04                  |
| `ideogram-ai/ideogram-v3`          | ~$0.09                  |
| `recraft-ai/recraft-v3`            | ~$0.04                  |
| Video models                       | ~$0.10-$5.00 per second |

Fabio's Karpathy_Loop testing (2026-07-27 user memory) spent ~$1.83 across an iteration session with multiple stock media generations. Individual illustrations are cheap; volume adds up.

Set a spending cap at [replicate.com/account/billing](https://replicate.com/account/billing) if runaway costs are a concern.

## Composition with plugin skills

- **Big Idea gate first**: run [`chart-big-idea`](../chart-big-idea/SKILL.md) Step 0.5 (earn-a-figure gate) before generating. Skips wasted API calls for figures that shouldn't exist.
- **Verify after**: run [`render-verify`](../render-verify/SKILL.md) to check the generated image actually communicates what you asked for. AI-generated images fail Prose-coupling surprisingly often (prose says X, image shows Y).
- **Iterate cheap, publish expensive**: FLUX-schnell for iteration, FLUX-1.1-pro or Ideogram for the final.
- **Style-lock for a series**: for a book or multi-chapter report, lock model + seed + palette hints across figures so the visual family reads as one voice. Ideogram and Recraft handle this best.

## Boundaries

- Does not itself run predictions — dispatches to the `replicate` MCP server which invokes the Replicate HTTP API. Requires the MCP server to be running (starts on demand once configured; verify with the plugin install verifier).
- Does not manage the API token — user brings their own via `REPLICATE_API_TOKEN` env var. If the var is unset, the MCP server fails on first invocation, not at config load.
- Does not cache or dedupe predictions — same prompt run twice = two paid predictions. Save outputs you want to keep.
- Does not select the model automatically — the agent chooses based on the prompt + this skill's recommendations. Model choice matters for both cost and quality.
- Does not do TTS, music, code generation, or LLM inference on Replicate — those are separate categories the plugin does not currently route to.

## Falsifiability

Revisit by **2026-10-30** (90 days) or sooner if:

- The recommended model list is stale (≥3 models retired or superseded by newer versions)
- The upstream `replicate/skills` bundle changes structure such that the composition callouts here point at moved content
- Heirs consistently reach for this skill for artifact types the routing table above says NOT to use (indicates the boundary is unclear)
- Cost estimates in the table are off by >2x versus real Replicate pricing at 2026-10 recheck
- The `replicate-mcp` npm package moves, renames, or changes invocation shape
- Zero heir uses the skill in the observation window (parking-lot candidate — the plugin scope was wrong to activate)
