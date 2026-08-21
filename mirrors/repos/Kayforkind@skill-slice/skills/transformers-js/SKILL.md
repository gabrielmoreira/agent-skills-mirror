---
name: transformers-js
description: "Runs Hugging Face models in JavaScript/TypeScript via @huggingface/transformers and ONNX (browser WASM/WebGPU or Node): NLP, vision, audio, embeddings, pipelines. Use when inference must stay in JS without a Python backend. Not for Python Diffusers (stable-diffusion), SVG-vault CLIP indexing (svg-vault-embeddings), or model training."
version: 1.0.1
risk: unknown
source: https://github.com/huggingface/skills/tree/main/skills/transformers-js
source_repo: huggingface/skills
source_type: official
date_added: 2026-07-01
license: Apache-2.0
license_source: https://github.com/huggingface/skills/blob/main/LICENSE
---

# Transformers.js — Machine Learning for JavaScript

Transformers.js enables running state-of-the-art ML models directly in JavaScript across browsers and server-side runtimes (Node.js, Bun, Deno), with no Python server required. Models are executed via ONNX Runtime (WASM or WebGPU backend).

## When to Use

Use this skill when the user needs to:

- Run ML models for **text analysis, generation, or translation** in JavaScript
- Perform **image classification, object detection, or segmentation** in JS
- Implement **speech recognition or audio processing** without a backend
- Build **multimodal AI applications** (image-to-text, document QA, zero-shot detection)
- Generate **embeddings / feature extraction** for RAG or similarity search
- Run models **client-side in the browser** with no server round-trip
- Integrate Hugging Face Hub models into a Node.js / Bun / Deno service

**Trigger keywords:** transformers.js, huggingface js, pipeline sentiment, onnx browser, webgpu inference, text-generation node, embeddings javascript, object detection browser, speech recognition js, translation nllb, quantized model js

## Prerequisites

1. **Node.js 18+** (or Bun 1.1+, Deno 1.38+) installed on the Windows host.
   ```powershell
   node --version   # expect v18.x or higher
   npm --version
   ```
2. **npm** (ships with Node) or an alternative package manager (`pnpm`, `yarn`, `bun`).
3. Internet access to `huggingface.co` for initial model download (unless using pre-cached local models).
4. For WebGPU in browser: Chrome 113+ or Edge 113+. For Node.js WebGPU, verify runtime support before relying on it.
5. Optional: `HF_TOKEN` environment variable if accessing gated or private models. Use `YOUR_HF_TOKEN` as a placeholder — never commit real tokens.

## Procedure

### 1. Install the Package

```powershell
# In your project directory on Windows
npm install @huggingface/transformers
```

For browser-only usage via CDN (no install needed):

```html
<script type="module">
  import { pipeline } from 'https://cdn.jsdelivr.net/npm/@huggingface/transformers';
</script>
```

### 2. Create a Pipeline and Run Inference

The `pipeline()` API is the simplest entry point — it handles preprocessing, model loading, and postprocessing.

```javascript
import { pipeline } from '@huggingface/transformers';

// Create a pipeline for a specific task (uses default model)
const pipe = await pipeline('sentiment-analysis');

// Run inference
const result = await pipe('I love transformers!');
// Output: [{ label: 'POSITIVE', score: 0.999817686 }]

// CRITICAL: Always dispose when done to free memory
await pipe.dispose();
```

### 3. Specify a Custom Model

Pass a Hugging Face Hub model ID as the second argument:

```javascript
const pipe = await pipeline(
  'sentiment-analysis',
  'Xenova/bert-base-multilingual-uncased-sentiment'
);
```

**Finding compatible models:**

Browse the Hub filtered by `library=transformers.js`:

- All models: `https://huggingface.co/models?library=transformers.js&sort=trending`
- Filter by task: add `&pipeline_tag=<task_id>` (e.g., `text-generation`, `image-classification`, `automatic-speech-recognition`)
- Sort options: `&sort=trending`, `&sort=downloads`, `&sort=likes`, `&sort=modified`

**Model size guidance:**

| Size | Typical use |
|------|-------------|
| Small (< 100 MB) | Fast, browser-suitable, limited accuracy |
| Medium (100–500 MB) | Balanced, good for most use cases |
| Large (> 500 MB) | High accuracy, slower, better for Node.js or powerful devices |

### 4. Configure Device and Quantization

```javascript
// CPU / WASM (default)
const pipe = await pipeline('sentiment-analysis', 'model-id');

// GPU via WebGPU
const pipe = await pipeline('sentiment-analysis', 'model-id', {
  device: 'webgpu',
});

// Quantization — control precision vs. performance
const pipe = await pipeline('sentiment-analysis', 'model-id', {
  dtype: 'q4',  // Options: 'fp32', 'fp16', 'q8', 'q4'
});
```

**Quantization levels:**

| dtype | Size | Accuracy |
|-------|------|----------|
| `fp32` | Largest | Full precision |
| `fp16` | Smaller | Half precision, still accurate |
| `q8` | Much smaller | Slight accuracy loss |
| `q4` | Smallest | Noticeable accuracy loss |

### 5. Track Download Progress

Models can be large (MB to GB). Pass a `progress_callback` to `pipeline()`:

```javascript
import { pipeline } from '@huggingface/transformers';

function onProgress(info) {
  if (info.status === 'progress_total') {
    console.log(`Total: ${info.progress.toFixed(1)}%`);
    return;
  }
  if (info.status === 'progress') {
    console.log(`${info.file}: ${info.progress.toFixed(1)}%`);
  }
  if (info.status === 'done') {
    console.log(`✓ ${info.file} complete`);
  }
}

const classifier = await pipeline('sentiment-analysis', null, {
  progress_callback: onProgress,
});
```

**Progress info statuses:** `initiate`, `download`, `progress`, `progress_total`, `done`, `ready`.

> **Load `./references/PIPELINE_OPTIONS.md`** when you need the full `pipeline()` options surface (device, dtype, progress_callback, revision, subfolder, etc.) or browser/React/CLI progress UI examples.

### 6. Configure the Global Environment

```javascript
import { env, LogLevel } from '@huggingface/transformers';

// Common settings
env.allowRemoteModels = true;       // Load from Hugging Face Hub
env.allowLocalModels = false;       // Load from file system
env.localModelPath = '/models/';    // Local model directory
env.useFSCache = true;              // Cache models on disk (Node.js)
env.useBrowserCache = true;         // Cache models in browser
env.cacheDir = './.cache';          // Cache directory location
env.logLevel = LogLevel.INFO;       // Optional: override default WARNING

// Optional: custom fetch for auth headers, retries, abort signals
env.fetch = (url, options) =>
  fetch(url, {
    ...options,
    headers: {
      ...options?.headers,
      Authorization: `Bearer ${YOUR_HF_TOKEN}`,
    },
  });
```

**Configuration patterns:**

```javascript
// Development: fast iteration with remote models
env.allowRemoteModels = true;
env.useFSCache = true;

// Production: local models only
env.allowRemoteModels = false;
env.allowLocalModels = true;
env.localModelPath = '/app/models/';

// Custom CDN
env.remoteHost = 'https://cdn.example.com/models';

// Disable caching (testing)
env.useFSCache = false;
env.useBrowserCache = false;
```

> **Load `./references/CONFIGURATION.md`** when you need complete documentation on all `env` options, caching strategies, pre-downloading models, or custom CDN setup.

### 7. Use ModelRegistry for Pre-Load Inspection (v4)

`ModelRegistry` lets you inspect required files, cache status, and available dtypes before loading a pipeline.

```javascript
import { ModelRegistry } from '@huggingface/transformers';

const task = 'feature-extraction';
const modelId = 'onnx-community/all-MiniLM-L6-v2-ONNX';
const modelOptions = { dtype: 'fp32' };

const files = await ModelRegistry.get_pipeline_files(task, modelId, modelOptions);
const cached = await ModelRegistry.is_pipeline_cached(task, modelId, modelOptions);
const dtypes = await ModelRegistry.get_available_dtypes(modelId);

console.log({ files: files.length, cached, dtypes });
```

> **Load `./references/MODEL_REGISTRY.md`** when you need production patterns for cache inspection, artifact clearing, or dtype negotiation before pipeline creation.

### 8. Common Task Examples

#### NLP

```javascript
// Text classification / sentiment
const classifier = await pipeline('text-classification');
const result = await classifier('This movie was amazing!');

// Named Entity Recognition
const ner = await pipeline('token-classification');
const entities = await ner('My name is John and I live in New York.');

// Question Answering
const qa = await pipeline('question-answering');
const answer = await qa({
  question: 'What is the capital of France?',
  context: 'Paris is the capital and largest city of France.'
});

// Text Generation
const generator = await pipeline('text-generation', 'onnx-community/gemma-3-270m-it-ONNX');
const text = await generator('Once upon a time', {
  max_new_tokens: 100,
  temperature: 0.7
});

// Translation
const translator = await pipeline('translation', 'Xenova/nllb-200-distilled-600M');
const output = await translator('Hello, how are you?', {
  src_lang: 'eng_Latn',
  tgt_lang: 'fra_Latn'
});

// Summarization
const summarizer = await pipeline('summarization');
const summary = await summarizer(longText, { max_length: 100, min_length: 30 });

// Zero-Shot Classification
const zsc = await pipeline('zero-shot-classification');
const result = await zsc('This is a story about sports.', ['politics', 'sports', 'technology']);
```

> **Load `./references/TEXT_GENERATION.md`** when you need streaming token-by-token output (`TextStreamer`), chat/conversation format with system/user/assistant roles, generation parameters (temperature, top_k, top_p), or React/API integration examples.

#### Computer Vision

```javascript
// Image Classification
const classifier = await pipeline('image-classification');
const result = await classifier('https://example.com/image.jpg');

// Object Detection
const detector = await pipeline('object-detection');
const objects = await detector('https://example.com/image.jpg');
// Returns: [{ label: 'person', score: 0.95, box: { xmin, ymin, xmax, ymax } }, ...]

// Image Segmentation
const segmenter = await pipeline('image-segmentation');
const segments = await segmenter('https://example.com/image.jpg');

// Depth Estimation
const depthEstimator = await pipeline('depth-estimation');
const depth = await depthEstimator('https://example.com/image.jpg');

// Zero-Shot Image Classification
const zic = await pipeline('zero-shot-image-classification');
const result = await zic('image.jpg', ['cat', 'dog', 'bird']);
```

#### Audio

```javascript
// Automatic Speech Recognition
const transcriber = await pipeline('automatic-speech-recognition');
const result = await transcriber('audio.wav');
// Returns: { text: 'transcribed text here' }

// Audio Classification
const classifier = await pipeline('audio-classification');
const result = await classifier('audio.wav');

// Text-to-Speech
const synthesizer = await pipeline('text-to-speech', 'Xenova/speecht5_tts');
const audio = await synthesizer('Hello, this is a test.', {
  speaker_embeddings: speakerEmbeddings
});
```

#### Multimodal

```javascript
// Image-to-Text (Captioning)
const captioner = await pipeline('image-to-text');
const caption = await captioner('image.jpg');

// Document Question Answering
const docQA = await pipeline('document-question-answering');
const answer = await docQA('document-image.jpg', 'What is the total amount?');

// Zero-Shot Object Detection
const detector = await pipeline('zero-shot-object-detection');
const objects = await detector('image.jpg', ['person', 'car', 'tree']);
```

#### Feature Extraction (Embeddings)

```javascript
// Raw embeddings
const extractor = await pipeline('feature-extraction');
const embeddings = await extractor('This is a sentence to embed.');
// Returns: tensor of shape [1, sequence_length, hidden_size]

// Sentence embeddings with mean pooling + normalization
const extractor = await pipeline('feature-extraction', 'onnx-community/all-MiniLM-L6-v2-ONNX');
const embeddings = await extractor('Text to embed', { pooling: 'mean', normalize: true });
```

#### Batch Processing

```javascript
const classifier = await pipeline('sentiment-analysis');
const results = await classifier([
  'I love this!',
  'This is terrible.',
  'It was okay.'
]);
```

### 9. Standalone Tokenization (Optional)

For tokenization-only workflows without full model inference:

```powershell
npm install @huggingface/tokenizers
```

```javascript
import { Tokenizer } from '@huggingface/tokenizers';
```

### 10. Working with Tensors Directly

```javascript
import { AutoTokenizer, AutoModel } from '@huggingface/transformers';

const tokenizer = await AutoTokenizer.from_pretrained('bert-base-uncased');
const model = await AutoModel.from_pretrained('bert-base-uncased');

const inputs = await tokenizer('Hello world!');
const outputs = await model(inputs);
```

### 11. Error Handling

```javascript
try {
  const pipe = await pipeline('sentiment-analysis', 'model-id');
  const result = await pipe('text to analyze');
} catch (error) {
  if (error.message.includes('fetch')) {
    console.error('Model download failed. Check internet connection.');
  } else if (error.message.includes('ONNX')) {
    console.error('Model execution failed. Check model compatibility.');
  } else {
    console.error('Unknown error:', error);
  }
}
```

### 12. Memory Management — CRITICAL

**HARD RULE:** Always call `pipe.dispose()` when finished. Models consume 100 MB to several GB of memory and hold GPU/CPU resources.

```javascript
const pipe = await pipeline('sentiment-analysis');
const result = await pipe('Great product!');
await pipe.dispose();  // Free memory
```

**When to dispose:**
- Application shutdown or component unmount
- Before loading a different model
- After batch processing in long-running apps
- On `SIGTERM`/`SIGINT` in servers

> **Load `./references/EXAMPLES.md`** when you need real-world cleanup patterns for React components, Express servers, browser SPAs, or long-running Node.js services.

## Pitfalls

1. **Never skip `pipe.dispose()`** — causes memory leaks that crash browsers and destabilize servers. This is the #1 production issue.
2. **Model not found** — verify the model exists on Hugging Face Hub, check spelling, and ensure the repo has an `onnx/` folder with ONNX weights. Not all Hub models are Transformers.js-compatible.
3. **WebGPU availability** — requires Chrome 113+ / Edge 113+ in browser. In Node.js, verify runtime WebGPU support. If `fp32` fails on WebGPU, try `fp16`. Always fall back to WASM if WebGPU is unavailable.
4. **Large model downloads in browser** — models can be hundreds of MB. Always show progress indicators and consider pre-downloading or using a CDN. Use `dtype: 'q4'` or `'q8'` to reduce size.
5. **Gated models** — if a model requires authentication, set `env.fetch` with an `Authorization: Bearer YOUR_HF_TOKEN` header. Never hardcode tokens; use environment variables.
6. **Version drift** — model repos can change. Pin specific revisions in production: `{ revision: 'abc123' }`.
7. **Sequence length limits** — for text generation, set `max_new_tokens` to avoid memory exhaustion on long outputs.
8. **Batch size vs. memory** — large batches on WASM can exhaust memory. Reduce batch size or process sequentially.
9. **Cache corruption** — if inference fails after a partial download, clear the cache directory (`./.cache` by default on Node.js) or use `ModelRegistry` to inspect and clear cached artifacts.
10. **Windows path handling** — when setting `env.localModelPath` on Windows, use forward slashes (`/models/`) or escaped backslashes (`C:\\models\\`). Node.js handles both, but mixing raw backslashes in JS strings causes escape issues.

## Verification

### Verify Installation

```powershell
# Check package is installed
npm list @huggingface/transformers

# Verify Node.js version
node --version
```

### Verify a Pipeline Runs (Smoke Test)

Create `test-smoke.mjs`:

```javascript
import { pipeline } from '@huggingface/transformers';

const pipe = await pipeline('sentiment-analysis');
const result = await pipe('I love transformers!');
console.log(result);
// Expected: [{ label: 'POSITIVE', score: 0.999... }]

await pipe.dispose();
console.log('✓ Smoke test passed');
```

Run it:

```powershell
node test-smoke.mjs
```

**Expected output:**
```
[ { label: 'POSITIVE', score: 0.9998... } ]
✓ Smoke test passed
```

### Verify WebGPU Availability (Browser)

```javascript
if ('gpu' in navigator) {
  console.log('WebGPU available');
} else {
  console.log('WebGPU NOT available — falling back to WASM');
}
```

### Verify ModelRegistry Cache Status

```javascript
import { ModelRegistry } from '@huggingface/transformers';

const cached = await ModelRegistry.is_pipeline_cached(
  'feature-extraction',
  'onnx-community/all-MiniLM-L6-v2-ONNX',
  { dtype: 'fp32' }
);
console.log(`Cached: ${cached}`);
```

### Verify Disposal

After `pipe.dispose()`, subsequent calls on the same pipeline instance should throw or return undefined — confirming resources were released.

## Quick Reference: Task IDs

| Task | Task ID |
|------|---------|
| Text classification | `text-classification` or `sentiment-analysis` |
| Token classification | `token-classification` or `ner` |
| Question answering | `question-answering` |
| Fill mask | `fill-mask` |
| Summarization | `summarization` |
| Translation | `translation` |
| Text generation | `text-generation` |
| Text-to-text generation | `text2text-generation` |
| Zero-shot classification | `zero-shot-classification` |
| Image classification | `image-classification` |
| Image segmentation | `image-segmentation` |
| Object detection | `object-detection` |
| Depth estimation | `depth-estimation` |
| Image-to-image | `image-to-image` |
| Zero-shot image classification | `zero-shot-image-classification` |
| Zero-shot object detection | `zero-shot-object-detection` |
| Automatic speech recognition | `automatic-speech-recognition` |
| Audio classification | `audio-classification` |
| Text-to-speech | `text-to-speech` or `text-to-audio` |
| Image-to-text | `image-to-text` |
| Document question answering | `document-question-answering` |
| Feature extraction | `feature-extraction` |
| Sentence similarity | `sentence-similarity` |

## Reference Files in This Skill

Load these on-demand when the user's task requires deeper detail:

| Reference | When to Load |
|-----------|-------------|
| `./references/PIPELINE_OPTIONS.md` | Full `pipeline()` options surface, progress UI examples (browser, React, CLI) |
| `./references/CONFIGURATION.md` | Complete `env` configuration, caching strategies, pre-download, custom CDN |
| `./references/MODEL_REGISTRY.md` | Production cache inspection, artifact clearing, dtype negotiation |
| `./references/CACHE.md` | Browser Cache API, Node.js filesystem cache, custom cache implementations |
| `./references/TEXT_GENERATION.md` | Streaming (`TextStreamer`), chat format, generation parameters, React/API examples |
| `./references/MODEL_ARCHITECTURES.md` | Supported model architectures and selection tips |
| `./references/EXAMPLES.md` | Real-world implementations: React cleanup, Express servers, browser SPAs |

## Official Resources

- Docs: https://huggingface.co/docs/transformers.js
- API reference: https://huggingface.co/docs/transformers.js/api/pipelines
- Model hub (filtered): https://huggingface.co/models?library=transformers.js
- GitHub: https://github.com/huggingface/transformers.js
- Examples repo: https://github.com/huggingface/transformers.js-examples

## Best Practices Summary

1. **Always dispose pipelines** — `pipe.dispose()` is mandatory.
2. **Start with the pipeline API** — use `AutoModel`/`AutoTokenizer` only when you need fine-grained control.
3. **Start small** — test with a smaller/quantized model first, then upgrade.
4. **Batch when possible** — process multiple inputs together for throughput.
5. **Pin model versions** — use `{ revision: 'abc123' }` in production.
6. **Handle loading states** — show progress indicators for UX.
7. **Wrap in try-catch** — always handle fetch/ONNX errors gracefully.
8. **Provide fallbacks** — WASM fallback when WebGPU is unavailable.
9. **Reuse pipelines** — load once, use many times; do not recreate per request.
10. **Graceful shutdown** — dispose on `SIGTERM`/`SIGINT` in servers.

## Limitations

- Use this skill only when the task clearly matches Transformers.js scope (JS/TS inference via ONNX Runtime).
- Verify commands, API behavior, pricing, quotas, credentials, and deployment effects against current official documentation before making changes.
- Do not treat generated examples as a substitute for environment-specific tests, security review, or user approval for destructive or costly actions.
