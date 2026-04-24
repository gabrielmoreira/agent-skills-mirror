---
name: gpt-image-2
description: Generate or edit images with OpenAI's GPT Image 2 (ChatGPT Images 2.0) via Fal AI. Two endpoints — text-to-image AND image edit (reference images + optional mask). Best-in-class for fine typography — chalkboards, signs, menus, posters, packaging, UI mockups, anything with legible text. Sync API, 1-4 images per call, custom dimensions up to 8.3MP. Includes pointer to a 700+ community prompt library (CC BY 4.0) for style/category inspiration. Triggers on gpt image 2, gpt-image-2, chatgpt image, openai image, typography image, sign mockup, poster mockup, menu image, packaging mockup, edit image, image edit, modify image, gpt image 2 prompt, awesome gpt-image-2.
---

# GPT Image 2 (ChatGPT Images 2.0)

OpenAI's latest image model — the strongest model available for **legible text inside images**. Use this when the picture *is* the typography: chalkboards, store signs, hand-lettered posters, menu boards, magazine covers, packaging mockups, UI screenshots, book covers.

**Two endpoints:**
- **Text-to-image** (`openai/gpt-image-2`) — generate from a prompt
- **Image edit** (`openai/gpt-image-2/edit`) — modify a reference image (with optional mask for region-specific edits)

| Field | Value |
|-------|-------|
| Model ID | `openai/gpt-image-2` (text-to-image) · `openai/gpt-image-2/edit` (edit) |
| Provider | Fal AI |
| Method | Sync (POST → response with image URLs, no polling) |
| Type | Image generation + editing |
| API Key | `.env` → `FAL_KEY` |
| Docs | https://fal.ai/models/openai/gpt-image-2 · https://fal.ai/models/openai/gpt-image-2/edit |

---

## Setup

1. Get a Fal API key from https://fal.ai/dashboard/keys
2. Add to your `.env` file (or wherever your project keeps secrets):
   ```
   FAL_KEY=your_key_here
   ```
3. That's it. Sync API — no SDK install required, just `curl` or `fetch`.

---

## How to call it

Auth header is `Authorization: Key {key}` — **not** `Bearer`. This applies to both endpoints.

### Text-to-image — minimum request

```bash
curl -s -X POST "https://fal.run/openai/gpt-image-2" \
  -H "Authorization: Key $FAL_KEY" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "A vintage diner chalkboard reading TODAY SPECIAL — Lobster Roll $24"}'
```

### Text-to-image — full request

```json
{
  "prompt": "...",
  "image_size": "landscape_4_3",
  "quality": "medium",
  "num_images": 1,
  "output_format": "png"
}
```

### Image edit — minimum request

Pass one or more public image URLs as references. Prompt describes the edit.

```bash
curl -s -X POST "https://fal.run/openai/gpt-image-2/edit" \
  -H "Authorization: Key $FAL_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Same workers, same beam — but they are all on phones now. One taking a selfie, one annoyed on a call. Hard hats with AirPods.",
    "image_urls": ["https://v3b.fal.media/files/b/.../reference.png"]
  }'
```

### Image edit — full request

```json
{
  "prompt": "...",
  "image_urls": ["https://...", "https://..."],
  "image_size": "auto",
  "quality": "medium",
  "num_images": 1,
  "output_format": "png",
  "mask_url": "https://.../mask.png"
}
```

- `image_size: "auto"` infers dimensions from the reference image — usually what you want.
- `mask_url` (optional) is a black/white image marking the region to edit. White = edit, black = keep. Use for surgical edits ("only change the sky").

### Response (both endpoints)

```json
{
  "images": [
    {
      "url": "https://v3b.fal.media/files/b/.../result.png",
      "content_type": "image/png",
      "file_name": "result.png"
    }
  ]
}
```

Download `images[i].url` immediately — Fal URLs may expire.

### Where do `image_urls` come from?

The reference image needs to be at a publicly accessible URL. Options:

1. **Fal's own storage** — use the JS/Python client's upload helper (`fal.storage.upload(file)` in JS, `fal_client.upload_file(path)` in Python).
2. **Reuse a previous Fal output URL** — outputs from any Fal model can be passed straight back as `image_urls` to chain edits.
3. **Any public host** — S3, GitHub raw, your own server, etc. Must be a direct image URL (not an HTML page).

If your project uses [Kie AI](https://kie.ai), their file upload endpoint at `https://kieai.redpandaai.co/api/file-stream-upload` works fine and returns a URL you can pass to Fal — see the bash recipe below for an example.

---

## Parameters

### Text-to-image (`openai/gpt-image-2`)

| Param | Required | Options | Default |
|-------|----------|---------|---------|
| `prompt` | Yes | string | — |
| `image_size` | No | preset name OR `{width, height}` | `"landscape_4_3"` |
| `quality` | No | `"low"`, `"medium"`, `"high"` | `"medium"` (Jay's default — high is overkill for most cases, ~3.5x more expensive) |
| `num_images` | No | 1 – 4 | `1` |
| `output_format` | No | `"jpeg"`, `"png"`, `"webp"` | `"png"` |
| `sync_mode` | No | bool — return base64 data URI inline | `false` |

### Image edit (`openai/gpt-image-2/edit`)

| Param | Required | Options | Default |
|-------|----------|---------|---------|
| `prompt` | Yes | string — describe the edit | — |
| `image_urls` | Yes | array of public image URLs | — |
| `image_size` | No | preset, `{width, height}`, or `"auto"` | `"auto"` (infer from input) |
| `quality` | No | `"low"`, `"medium"`, `"high"` | `"medium"` |
| `num_images` | No | 1 – 4 | `1` |
| `output_format` | No | `"jpeg"`, `"png"`, `"webp"` | `"png"` |
| `sync_mode` | No | bool — return base64 data URI inline | `false` |
| `mask_url` | No | URL of B/W mask (white = edit, black = keep) | — |

### Image sizes

**Preset names:** `square_hd`, `square`, `portrait_4_3`, `portrait_16_9`, `landscape_4_3`, `landscape_16_9`.

**Custom dimensions** — pass an object:
```json
"image_size": { "width": 1536, "height": 1024 }
```

Constraints on custom sizes:
- Both dimensions must be multiples of **16**
- Max edge: **3840px**
- Aspect ratio: **≤ 3:1**
- Total pixels between **655,360 and 8,294,400** (~640×1024 min, ~3840×2160 max)

---

## Pricing

Token-based, billed via Fal:

| Token type | Input | Cached | Output |
|------------|-------|--------|--------|
| Text | $5 / 1M | $1.25 / 1M | $10 / 1M |
| Image | $8 / 1M | $2 / 1M | $30 / 1M |

**Per-image rough cost** (landscape_4_3 = 1536×1024):
- `low` ≈ $0.02 per image
- `medium` ≈ $0.05 per image  ← **default**
- `high` ≈ $0.18 per image

`quality` is the biggest cost lever. Default to `medium` — that's the sweet spot for most work. Bump to `high` only when typography/detail really matters and the image is a final. `low` for cheap drafts. Check actual usage in the Fal dashboard.

---

## When to use vs other models

| Scenario | Endpoint | Notes |
|----------|----------|-------|
| Sign / chalkboard / poster with text | text-to-image | Best in class for typography |
| Magazine cover / book cover | text-to-image | |
| Menu board / packaging mockup | text-to-image | |
| UI screenshot mockup | text-to-image | |
| Modify an existing image ("change the sky", "swap the logo", "add text") | edit | Pass image as `image_urls`, describe the change |
| Surgical region edit ("only change this corner") | edit + `mask_url` | Mask defines the editable region |
| Iterative refinement | edit | Feed previous output URL back in |
| Photoreal portrait | other | Use Nano Banana / Flux |
| Style transfer with strong style preservation | other | GPT Image 2 edit reinterprets more than it preserves |
| Need < $0.02 per render | other | Switch model — even `low` quality here is comparable to other models' default |

---

## Recipe — Node.js

One helper, both endpoints. Drop in a `.js` file and run with `node`. Forward slashes in paths work fine on Windows.

```javascript
import fs from 'node:fs';
import path from 'node:path';

const FAL_KEY = process.env.FAL_KEY ||
  fs.readFileSync('.env', 'utf8').match(/FAL_KEY=(.+)/)[1].trim();

// Pass image_urls to use the edit endpoint; omit for text-to-image.
async function gptImage2({
  prompt,
  image_urls,
  mask_url,
  image_size,
  quality = 'medium',
  num_images = 1,
  output_format = 'png',
  outDir = './output',
  label = 'gpt2',
}) {
  fs.mkdirSync(outDir, { recursive: true });

  const isEdit = Array.isArray(image_urls) && image_urls.length > 0;
  const url = isEdit
    ? 'https://fal.run/openai/gpt-image-2/edit'
    : 'https://fal.run/openai/gpt-image-2';

  const body = { prompt, quality, num_images, output_format };
  if (isEdit) {
    body.image_urls = image_urls;
    body.image_size = image_size ?? 'auto';
    if (mask_url) body.mask_url = mask_url;
  } else {
    body.image_size = image_size ?? 'landscape_4_3';
  }

  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Authorization': `Key ${FAL_KEY}`, 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });

  const json = await res.json();
  if (!json.images?.length) throw new Error(`No images returned: ${JSON.stringify(json)}`);

  const ts = Date.now();
  const saved = [];
  for (let i = 0; i < json.images.length; i++) {
    const suffix = json.images.length > 1 ? `_${i + 1}` : '';
    const fname = `${label}_${ts}${suffix}.${output_format}`;
    const fp = path.join(outDir, fname);
    const buf = Buffer.from(await (await fetch(json.images[i].url)).arrayBuffer());
    fs.writeFileSync(fp, buf);
    saved.push(fp);
    console.log(`Saved: ${fp}`);
  }
  return saved;
}

// Text-to-image
await gptImage2({
  prompt: 'A chalkboard sign on a brick wall, hand-lettered: "OPEN AT 7"',
  label: 'chalkboard',
});

// Edit an existing image
await gptImage2({
  prompt: 'Same scene but everyone is on their phone now. One taking a selfie, one on a call.',
  image_urls: ['https://v3b.fal.media/files/b/.../original.png'],
  label: 'phones_edit',
});
```

## Recipe — Python

One helper, both endpoints. Pass `image_urls` for the edit variant; omit for text-to-image.

```python
import os, time, requests, pathlib

FAL_KEY = os.environ['FAL_KEY']

def gpt_image_2(prompt, image_urls=None, mask_url=None, image_size=None,
                quality='medium', num_images=1, output_format='png',
                out_dir='./output', label='gpt2'):
    pathlib.Path(out_dir).mkdir(parents=True, exist_ok=True)
    is_edit = bool(image_urls)
    url = 'https://fal.run/openai/gpt-image-2/edit' if is_edit else 'https://fal.run/openai/gpt-image-2'

    body = {'prompt': prompt, 'quality': quality,
            'num_images': num_images, 'output_format': output_format}
    if is_edit:
        body['image_urls'] = image_urls
        body['image_size'] = image_size or 'auto'
        if mask_url:
            body['mask_url'] = mask_url
    else:
        body['image_size'] = image_size or 'landscape_4_3'

    res = requests.post(url,
        headers={'Authorization': f'Key {FAL_KEY}', 'Content-Type': 'application/json'},
        json=body)
    data = res.json()
    if not data.get('images'):
        raise RuntimeError(f'No images: {data}')

    ts = int(time.time() * 1000)
    saved = []
    for i, img in enumerate(data['images']):
        suffix = f'_{i+1}' if len(data['images']) > 1 else ''
        fp = f'{out_dir}/{label}_{ts}{suffix}.{output_format}'
        with open(fp, 'wb') as f:
            f.write(requests.get(img['url']).content)
        saved.append(fp)
        print(f'Saved: {fp}')
    return saved

# Text-to-image
gpt_image_2(prompt='A chalkboard reading "OPEN AT 7"', label='chalkboard')

# Edit
gpt_image_2(
    prompt='Same scene but everyone is on their phone now',
    image_urls=['https://v3b.fal.media/files/b/.../original.png'],
    label='phones_edit',
)
```

## Recipe — bash (one-shot)

Use a temp JSON file to avoid shell-escape pain with multi-line prompts.

### Text-to-image

```bash
cat > /tmp/gpt2_body.json << 'ENDJSON'
{
  "prompt": "A vintage diner chalkboard, hand-lettered: TODAY SPECIAL — Lobster Roll $24",
  "image_size": "landscape_4_3",
  "quality": "medium",
  "num_images": 1,
  "output_format": "png"
}
ENDJSON

curl -s -X POST "https://fal.run/openai/gpt-image-2" \
  -H "Authorization: Key $FAL_KEY" \
  -H "Content-Type: application/json" \
  -d @/tmp/gpt2_body.json
```

### Image edit

```bash
cat > /tmp/gpt2_edit_body.json << 'ENDJSON'
{
  "prompt": "Same workers on the beam — but they're all on phones now. One taking a selfie.",
  "image_urls": ["https://v3b.fal.media/files/b/.../original.png"],
  "image_size": "auto",
  "quality": "medium",
  "num_images": 1,
  "output_format": "png"
}
ENDJSON

curl -s -X POST "https://fal.run/openai/gpt-image-2/edit" \
  -H "Authorization: Key $FAL_KEY" \
  -H "Content-Type: application/json" \
  -d @/tmp/gpt2_edit_body.json
```

---

## Prompting tips

GPT Image 2 is unusually good at typography, but you have to tell it clearly:

- **Structure complex prompts as JSON.** For multi-element scenes (posters, infographics, multi-panel comics, app mockups), the model responds notably better to a JSON object than to flowing prose. Keys like `type`, `subject`, `style`, `background`, `header`, `layout`, `footer` give the model an explicit slot for each element. Loose prose forces it to guess what's foreground vs background. The community-curated prompt library (see "Prompt examples library" below) is almost entirely structured JSON for this reason.
- **Parameterize with placeholders for reuse.** Use `{argument name="quote" default="Stay hungry, stay foolish"}` syntax to mark variables in your prompt. Originally a [Raycast Snippets](https://raycast.com/help/snippets) convention, widely adopted across the GPT Image 2 community. Lets one prompt template handle many variants without rewriting.
- **Quote the text:** `hand-lettered text reads "OPEN AT 7"` — quoting helps the model lock in the literal characters.
- **Specify the lettering style:** `chalk lettering`, `serif sign painter`, `bold sans-serif neon`, `embossed metal type`, `cursive script`.
- **Anchor the surface:** chalkboard, brick wall, neon storefront, paper menu, vinyl record sleeve. The model uses the surface to inform the lettering style.
- **Mention lighting:** `warm tungsten`, `golden hour`, `cool fluorescent` — affects mood + readability.
- **Layout hints work:** `the title stacked over three lines`, `with a small drawing below`, `centered`.
- **For multi-line text:** spell out line breaks. `Line 1: "ESPRESSO". Line 2: "$4.50".` Don't trust newlines in the prompt to translate.

### For the edit endpoint

- **Describe the change, not the whole scene.** "Same workers, same beam, same lunch boxes — but everyone is on their phone now" works better than re-describing the original from scratch.
- **Anchor to what stays the same.** The model preserves more when you explicitly call out what shouldn't change.
- **Use `mask_url` for surgical edits.** Without a mask, the model may reinterpret the whole image. With a mask, it constrains the change to the white region.
- **Chain edits.** Pass the previous output URL back into a new edit call. Good for iterative refinement.

What it's bad at:
- Long paragraphs of text — keep it to a few words/lines.
- Faces with expressions tied to specific real people — generic figures fine, named likenesses iffy.
- Strict style preservation in edits — it tends to reinterpret. For tight style transfer use a different model.

---

## Transparent backgrounds — not supported

Fal's GPT Image 2 endpoints do **not** support true transparency. Tested 2026-04-22:

- No `background` parameter (OpenAI's direct API has `background: "transparent"` for `gpt-image-1` — Fal's wrapper for GPT Image 2 does not expose it).
- Passing `background: "transparent"` anyway → silently ignored, output is RGB PNG with no alpha channel.
- Prompting for "transparent background" → model paints a *fake* checkerboard pattern in the pixels. Looks transparent; isn't. The PNG is still RGB.

**If you need a transparent PNG, chain a background remover:**
- `fal-ai/imageutils/rembg` — fast, cheap, works on most subjects.
- `fal-ai/birefnet` — higher quality, slower.
- Pass the GPT Image 2 output URL straight in as `image_url`.

Or use Nano Banana Pro / other models for the generation step if clean alpha matters.

---

## Prompt examples library

For style/category inspiration, the **`awesome-gpt-image-2`** community library has 700+ curated prompts (CC BY 4.0, attribution required). Use it whenever a user asks "how would I prompt this?" for a recognizable style or use-case.

**Two ways in:**

1. **Browse the gallery (humans):** [youmind.com/gpt-image-2-prompts](https://youmind.com/gpt-image-2-prompts) — masonry grid, full-text search, deep-linkable categories.
2. **Grep the README (agents):** [raw.githubusercontent.com/YouMind-OpenLab/awesome-gpt-image-2/main/README.md](https://raw.githubusercontent.com/YouMind-OpenLab/awesome-gpt-image-2/main/README.md) — single markdown file, ~350KB, all prompts in one place. Predictable structure: each prompt is `### No. N: Category - Title` → badges → `#### 📖 Description` → `#### 📝 Prompt` (a fenced code block, usually JSON) → `#### 📌 Details` (author/source/date).

**Category slugs** (use as `?categories={slug}` on youmind.com, or as a grep target in the README):

- **Use cases:** `profile-avatar`, `social-media-post`, `infographic-edu-visual`, `youtube-thumbnail`, `comic-storyboard`, `product-marketing`, `ecommerce-main-image`, `game-asset`, `poster-flyer`, `app-web-design`
- **Styles:** `photography`, `cinematic-film-still`, `anime-manga`, `illustration`, `sketch-line-art`, `comic-graphic-novel`, `3d-render`, `chibi-q-style`, `isometric`, `pixel-art`, `oil-painting`, `watercolor`, `ink-chinese-style`, `retro-vintage`, `cyberpunk-sci-fi`, `minimalism`
- **Subjects:** `portrait-selfie`, `influencer-model`, `character`, `group-couple`, `product`, `food-drink`, `fashion-item`, `animal-creature`, `vehicle`, `architecture-interior`, `landscape-nature`, `cityscape-street`, `diagram-chart`, `text-typography`, `abstract-background`

**Recipe — fetch + grep examples for a category:**

```bash
# Pull the README once, save locally
curl -s https://raw.githubusercontent.com/YouMind-OpenLab/awesome-gpt-image-2/main/README.md -o /tmp/gpt2_prompts.md

# Find all entries matching a category (case-insensitive)
grep -n "^### No\." /tmp/gpt2_prompts.md | grep -i "youtube thumbnail"

# Read a specific prompt block by its line range (use line numbers from the grep above)
sed -n '2722,2830p' /tmp/gpt2_prompts.md
```

**Or, in one shot via WebFetch** (for agents): fetch the raw README and ask for the N best examples in category X — the file's predictable headings make extraction reliable.

**Attribution.** When reusing a prompt verbatim or near-verbatim in published work, credit YouMind OpenLab + the original author (the `📌 Details` section names the author and source). Repo: [github.com/YouMind-OpenLab/awesome-gpt-image-2](https://github.com/YouMind-OpenLab/awesome-gpt-image-2).

---

## Notes / gotchas

- **Sync API** — single POST call returns the image URL. No polling, no taskId.
- **Auth header is `Key`, not `Bearer`** — Fal-specific.
- **Up to 4 images per call** via `num_images` — useful for picking from variants. Cost scales linearly.
- **Custom dimensions:** multiples of 16, total pixels in [655K, 8.3M], aspect ratio ≤ 3:1, max edge 3840px.
- **Two endpoints:** `/openai/gpt-image-2` (text-to-image) vs `/openai/gpt-image-2/edit` (with `image_urls` and optional `mask_url`). Pick by what you have as input.
- **Edit endpoint defaults `image_size` to `auto`** — uses the input image's dimensions. Override only if you need a different output shape.
- **Reference images must be public URLs** — upload to Fal storage, reuse a previous Fal output URL, or host elsewhere (S3, GitHub raw).
- **Fal URLs expire** — download immediately.
- `sync_mode: true` returns a base64 data URI inline (skips request history). Useful for piping into another tool without disk I/O. Default is `false`.

---

## Links

- Text-to-image: https://fal.ai/models/openai/gpt-image-2
- Image edit: https://fal.ai/models/openai/gpt-image-2/edit
- Fal API docs (T2I): https://fal.ai/models/openai/gpt-image-2/api
- Fal API docs (Edit): https://fal.ai/models/openai/gpt-image-2/edit/api
- Fal pricing: https://fal.ai/pricing
- Fal dashboard (usage / keys): https://fal.ai/dashboard
- Prompt library (gallery): https://youmind.com/gpt-image-2-prompts
- Prompt library (repo, CC BY 4.0): https://github.com/YouMind-OpenLab/awesome-gpt-image-2
