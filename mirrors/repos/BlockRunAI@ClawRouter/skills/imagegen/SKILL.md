---
name: imagegen
description: Generate or edit images via BlockRun's image API. Trigger when the user asks to generate, create, draw, make an image — or to edit, modify, change, or retouch an existing image.
metadata: { "openclaw": { "emoji": "🖼️", "requires": { "config": ["models.providers.blockrun"] } } }
---

# Image Generation & Editing

Generate or edit images through ClawRouter. Payment is automatic via x402.

---

## Generate an Image

POST to `http://localhost:8402/v1/images/generations`:

```json
{
  "model": "google/nano-banana",
  "prompt": "a golden retriever surfing on a wave",
  "size": "1024x1024",
  "n": 1
}
```

Response:

```json
{
  "created": 1741460000,
  "data": [{ "url": "http://localhost:8402/images/abc123.png" }]
}
```

Display inline: `![generated image](http://localhost:8402/images/abc123.png)`

### Model Selection

| Model         | Full ID                     | Price | Sizes                           | Best for                            |
| ------------- | --------------------------- | ----- | ------------------------------- | ----------------------------------- |
| `nano-banana` | `google/nano-banana`        | $0.05 | 1024×1024, 1216×832, 1024×1792  | Default — fast, cheap, good quality |
| `banana-pro`  | `google/nano-banana-pro`    | $0.10 | up to 4096×4096                 | High-res, large format              |
| `dall-e-3`    | `openai/dall-e-3`           | $0.04 | 1024×1024, 1792×1024, 1024×1792 | Photorealistic, complex scenes      |
| `gpt-image`   | `openai/gpt-image-1`        | $0.02 | 1024×1024, 1536×1024, 1024×1536 | Budget option                       |
| `flux`        | `black-forest/flux-1.1-pro` | $0.04 | 1024×1024, 1216×832, 832×1216   | Artistic styles, fewer restrictions |

**Choosing a model:**

- Default → `nano-banana`
- "high res" / "large" → `banana-pro`
- "photorealistic" / "dall-e" → `dall-e-3`
- "artistic" / flexible content → `flux`

**Choosing a size:**

- Default: `1024x1024`
- Portrait: `1024x1792`
- Landscape: `1792x1024` (dall-e-3) or `1216x832` (nano-banana / flux)
- High-res: `2048x2048` or `4096x4096` with `banana-pro` only

---

## Edit an Existing Image

POST to `http://localhost:8402/v1/images/image2image`:

```json
{
  "model": "openai/gpt-image-1",
  "prompt": "make the background a snowy mountain landscape",
  "image": "https://example.com/photo.jpg",
  "size": "1024x1024",
  "n": 1
}
```

ClawRouter automatically downloads URLs and reads local file paths — pass them directly, no manual base64 conversion needed.

Optional `mask` field: a second image (URL or path) that marks which areas to edit (white = edit, black = keep).

Response is identical to generation:

```json
{
  "created": 1741460000,
  "data": [{ "url": "http://localhost:8402/images/xyz456.png", "revised_prompt": "..." }]
}
```

**Supported models for editing:** `openai/gpt-image-1` only ($0.02)

---

## Example Interactions

**User:** Draw me a cyberpunk city at night
→ POST to `/v1/images/generations`, model `nano-banana`, prompt as given.

**User:** Generate a high-res portrait of a samurai
→ POST to `/v1/images/generations`, model `banana-pro`, size `1024x1792`.

**User:** Edit this photo to add a sunset background: https://example.com/portrait.jpg
→ POST to `/v1/images/image2image`, model `gpt-image`, image = the URL, prompt = "add a warm sunset background".

**User:** Change the background in my image to a beach (attaches local file)
→ POST to `/v1/images/image2image`, image = the local file path, prompt describes the change.

---

## Notes

- Payment is automatic via x402 — deducted from the user's BlockRun wallet
- If the call fails with a payment error, tell the user to fund their wallet at [blockrun.ai](https://blockrun.ai)
- Google models may return base64 internally — ClawRouter uploads automatically and returns a hosted URL
- DALL-E 3 enforces OpenAI content policy; use `flux` or `nano-banana` for more flexibility
- Image editing is only available with `gpt-image-1`; generation supports all 5 models
