---
type: skill
lifecycle: stable
inheritance: inheritable
name: image-storage-embedding-split
description: Storing images at embed size loses the original:
tier: standard
applyTo: '**/*image*,**/*storage*,**/*embedding*'
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# Image Storage vs Embedding Split

## The Problem

Storing images at embed size loses the original:

- Can't upscale later
- Can't use for different contexts
- Quality degradation is permanent

## The Solution

Keep originals at full resolution. Embed at reduced size.

```javascript
const sharp = require('sharp');

async function processImage(inputPath, outputDir) {
  const filename = path.basename(inputPath, path.extname(inputPath));
  
  // Store original at full resolution
  const original = await sharp(inputPath)
    .resize(512, 512, { fit: 'inside' })
    .toFile(path.join(outputDir, `${filename}-512.png`));
  
  // Create embed version at reduced size
  const embed = await sharp(inputPath)
    .resize(256, 256, { fit: 'inside' })
    .toBuffer();
  
  // Return both
  return {
    originalPath: path.join(outputDir, `${filename}-512.png`),
    embedDataUri: `data:image/png;base64,${embed.toString('base64')}`,
    embedSize: 256
  };
}
```

## Storage Schema

```json
{
  "images": [
    {
      "id": "avatar-001",
      "originalPath": "assets/avatar-001-512.png",
      "embedDataUri": "data:image/png;base64,iVBOR...",
      "embedSize": 256,
      "originalSize": 512
    }
  ]
}
```

## Token Savings

| Size | Base64 Size | Token Estimate |
|------|-------------|----------------|
| 512px | ~42KB | ~10,500 tokens |
| 256px | ~13KB | ~3,250 tokens |
| Savings | ~70% | ~7,250 tokens |

## Verification

1. Original file exists at full resolution
2. Embedded version is at reduced size
3. Schema documents both dimensions
4. Can regenerate embed from original

## When to Apply

- AI context windows with images
- Visual memory systems
- Any system with storage/display size trade-offs

## Tags

`images` `ai` `tokens` `storage`
