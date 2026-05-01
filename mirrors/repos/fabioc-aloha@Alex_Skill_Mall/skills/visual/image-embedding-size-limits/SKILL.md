---
type: skill
lifecycle: stable
inheritance: inheritable
name: image-embedding-size-limits
description: Image embedding size limits in markdown — base64 bloats 33%, use file references for images over 50KB
tier: standard
applyTo: '**/*image*,**/*embedding*,**/*size*'
currency: 2026-04-30
lastReviewed: 2026-04-30
---

# Image Embedding Size Limits

**Category**: Visual
**Time Saved**: 30 minutes + token cost savings
**Battle-tested**: Yes — AI context window management

---

## The Problem

You're building an AI application that processes images — visual memory, document analysis, or character references. You embed images as base64 data URIs. Your context window fills up fast, API costs spike, or requests start failing.

## Why It Happens

Base64 encoding increases image size by ~33%. A 512×512 image easily becomes 40-60KB of text. Put 10 images in context and you've used 500KB+ of your token budget.

## The Rule

**256px maximum for embedded images. Store originals at full resolution separately.**

| Dimension | Use Case | Typical Size |
|-----------|----------|--------------|
| 256px | AI context embedding | 10-15KB |
| 512px | Storage/archive | 40-60KB |
| 1024px+ | Print/high-res | 100KB+ |

## The 70% Savings

```
512px image: ~42KB base64
256px image: ~13KB base64
Savings: 70% per image
```

For 10 images: 420KB → 130KB — that's 290KB of context saved.

## Implementation Pattern

### Storage vs Embedding Split

```javascript
// visual-memory.json
{
  "images": [
    {
      "id": "portrait-001",
      "name": "Character Reference",
      "storageSize": 512,      // Full resolution on disk
      "embedSize": 256,        // Smaller version in dataUri
      "storagePath": "assets/portraits/full/portrait-001.png",
      "dataUri": "data:image/png;base64,..."  // 256px version
    }
  ]
}
```

### Resize on Embed

```javascript
const sharp = require('sharp');

async function createEmbedding(imagePath, maxDim = 256) {
  const buffer = await sharp(imagePath)
    .resize(maxDim, maxDim, { fit: 'inside' })
    .png()
    .toBuffer();
  
  return `data:image/png;base64,${buffer.toString('base64')}`;
}

async function addToVisualMemory(imagePath, metadata) {
  // Store original at full resolution
  const storagePath = await copyToStorage(imagePath);
  
  // Create smaller embedding
  const dataUri = await createEmbedding(imagePath, 256);
  
  return {
    ...metadata,
    storageSize: 512,
    embedSize: 256,
    storagePath,
    dataUri,
  };
}
```

### Lazy Loading Pattern

```javascript
class VisualMemory {
  constructor() {
    this.index = [];  // Metadata only, no images
  }
  
  // Load thumbnails for context (256px)
  async getEmbeddings(ids) {
    return ids.map(id => this.index[id].dataUri);
  }
  
  // Load full resolution when needed
  async getFullResolution(id) {
    const entry = this.index[id];
    return fs.readFileSync(entry.storagePath);
  }
}
```

## Size Reference Table

| Original Size | 256px Base64 | 512px Base64 | Savings |
|--------------|--------------|--------------|---------|
| 1024×1024 | ~15KB | ~55KB | 73% |
| 512×512 | ~13KB | ~42KB | 69% |
| 256×256 | ~13KB | N/A | — |

## When to Use Each Size

| Use Case | Size | Rationale |
|----------|------|-----------|
| AI context/prompts | 256px | Token efficiency |
| Face recognition models | 256px | Most work at this size |
| Visual comparison | 256px | Sufficient detail |
| Archival storage | 512px | Quality preservation |
| Print/export | Original | Full quality needed |

## Format Considerations

```javascript
// PNG: Lossless, larger, good for diagrams
await sharp(input).png().toBuffer();

// JPEG: Lossy, smaller, good for photos
await sharp(input).jpeg({ quality: 80 }).toBuffer();

// WebP: Best compression, broad support
await sharp(input).webp({ quality: 80 }).toBuffer();
```

## Verification Checklist

- [ ] Embedded images max 256px
- [ ] Original files stored separately at full resolution
- [ ] `embedSize` field documents the embedded dimension
- [ ] Base64 size under 20KB per image
- [ ] Total embedded image budget tracked

## Common Symptoms

- Context window exceeded with few images
- API costs higher than expected
- Slow response times from large payloads
- "Request too large" errors

## Related Skills

- `docs-decay-velocity` — Managing evolving content
