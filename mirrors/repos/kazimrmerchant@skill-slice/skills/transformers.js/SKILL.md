---
name: transformers-js
description: "Runs Hugging Face ONNX models in JavaScript or TypeScript via @huggingface/transformers pipeline() on WebGPU, WASM, or Node.js. Use for in-browser or Node inference: sentiment, generation, classification, detection, ASR, or embeddings. Never a Python transformers or PyTorch serving chair; not for Hub models that lack an onnx/ weight folder."
version: 3.8.2
metadata:
  author: huggingface
  category: machine-learning
  repository: https://github.com/huggingface/transformers.js
---

# Transformers.js — Machine Learning for JavaScript

Transformers.js runs state-of-the-art ONNX-based ML models directly in JavaScript — both in browsers (WebGPU/WASM) and Node.js — with no Python server required. Models are fetched from the Hugging Face Hub and cached locally.

## When to Use

Use this skill when you need to:

- Run ML inference (text classification, NER, QA, summarization, translation, text generation) in JavaScript or TypeScript
- Perform image classification, object detection, segmentation, or depth estimation
- Implement speech recognition (ASR), audio classification, or text-to-speech
- Build multimodal applications (image captioning, document QA, zero-shot detection)
- Generate embeddings / feature extraction for RAG or similarity search
- Run models client-side in the browser without a backend
- Use WebGPU acceleration for large models in supported browsers

**Trigger keywords:** transformers.js, huggingface, pipeline, ONNX, sentiment-analysis, text-generation, image-classification, object-detection, speech-recognition, embeddings, feature-extraction, WebGPU, WASM, quantization, q4, q8

## Prerequisites

- **Node.js** ≥ 18 (for server-side usage) or a modern browser (Chrome 113+ / Edge 113+ for WebGPU; any WASM-capable browser for CPU)
- **npm** or **pnpm** or **yarn** for installation
- Internet access to download models from Hugging Face Hub (or pre-downloaded local models)
- On Windows (PowerShell): ensure `node` and `npm` are on `PATH`

```powershell
# Verify Node.js and npm are available
node --version   # expect v18.x or higher
npm --version
```

## Procedure

### 1. Install the Package

```powershell
# Node.js / bundler projects
npm install @huggingface/transformers
```

For browser-only usage via CDN (no build step):

```html
<script type="module">
  import { pipeline } from 'https://cdn.jsdelivr.net/npm/@huggingface/transformers';
</script>
```

### 2. Create a Pipeline and Run Inference

The `pipeline()` API bundles preprocessing, model inference, and postprocessing into a single callable.

```javascript
import { pipeline } from '@huggingface/transformers';

// Create a pipeline (downloads model on first call, caches thereafter)
const classifier = await pipeline('sentiment-analysis');

// Run inference
const result = await classifier('I love transformers!');
// => [{ label: 'POSITIVE', score: 0.999817686 }]

// CRITICAL: Always dispose when done to free memory
await classifier.dispose();
```

### 3. Specify a Custom Model

Pass a Hugging Face model ID as the second argument. Only models with ONNX weights (look for an `onnx/` folder in the repo) are compatible.

```javascript
const pipe = await pipeline(
  'sentiment-analysis',
  'Xenova/bert-base-multilingual-uncased-sentiment'
);
```

**Finding compatible models:**

Browse the Hub filtered by the `transformers.js` library tag:

```
https://huggingface.co/models?library=transformers.js&sort=trending
```

Filter by task using `pipeline_tag`:

| Task | URL |
|------|-----|
| Text generation | `https://huggingface.co/models?pipeline_tag=text-generation&library=transformers.js&sort=trending` |
| Text classification | `https://huggingface.co/models?pipeline_tag=text-classification&library=transformers.js&sort=trending` |
| Translation | `https://huggingface.co/models?pipeline_tag=translation&library=transformers.js&sort=trending` |
| Summarization | `https://huggingface.co/models?pipeline_tag=summarization&library=transformers.js&sort=trending` |
| Question answering | `https://huggingface.co/models?pipeline_tag=question-answering&library=transformers.js&sort=trending` |
| Image classification | `https://huggingface.co/models?pipeline_tag=image-classification&library=transformers.js&sort=trending` |
| Object detection | `https://huggingface.co/models?pipeline_tag=object-detection&library=transformers.js&sort=trending` |
| Image segmentation | `https://huggingface.co/models?pipeline_tag=image-segmentation&library=transformers.js&sort=trending` |
| Speech recognition | `https://huggingface.co/models?pipeline_tag=automatic-speech-recognition&library=transformers.js&sort=trending` |
| Audio classification | `https://huggingface.co/models?pipeline_tag=audio-classification&library=transformers.js&sort=trending` |
| Image-to-text | `https://huggingface.co/models?pipeline_tag=image-to-text&library=transformers.js&sort=trending` |
| Feature extraction | `https://huggingface.co/models?pipeline_tag=feature-extraction&library=transformers.js&sort=trending` |
| Zero-shot classification | `https://huggingface.co/models?pipeline_tag=zero-shot-classification&library=transformers.js&sort=trending` |

**Sort options:** `&sort=trending` (recent popularity), `&sort=downloads` (all-time), `&sort=likes` (community), `&sort=modified` (recently updated).

**Model selection tips:**
- Prefer models by `Xenova` (Transformers.js maintainer) or `onnx-community` — these are tested for JS compatibility
- Check the model card for ONNX file availability, size, quantization options, and license
- Start small (< 100 MB for browser), scale up if accuracy is insufficient
- Pin a specific revision in production: `{ revision: 'abc123' }`

### 4. Configure Device and Quantization

```javascript
// CPU via WASM (default)
const pipe = await pipeline('sentiment-analysis', 'model-id');

// WebGPU (experimental, browser only)
const pipe = await pipeline('sentiment-analysis', 'model-id', {
  device: 'webgpu',
});

// Quantization — controls precision vs. size/speed
const pipe = await pipeline('sentiment-analysis', 'model-id', {
  dtype: 'q4',  // Options: 'fp32', 'fp16', 'q8', 'q4'
});
```

| dtype | Precision | Size | Use case |
|-------|-----------|------|----------|
| `fp32` | Full | Largest | Maximum accuracy, WebGPU |
| `fp16` | Half | Smaller | Good accuracy, WebGPU |
| `q8` | 8-bit | Much smaller | General-purpose, slight accuracy loss |
| `q4` | 4-bit | Smallest | Fastest download, noticeable accuracy loss |

### 5. Track Download Progress

Models range from a few MB to several GB. Pass a `progress_callback` to track downloads:

```javascript
const fileProgress = {};

function onProgress(info) {
  if (info.status === 'progress') {
    fileProgress[info.file] = info.progress;
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

**Progress info statuses:** `initiate` → `download` → `progress` (repeated) → `done` → `ready`.

> **Load `./references/PIPELINE_OPTIONS.md`** when you need the full list of pipeline constructor options (device, dtype, progress_callback, revision, subfolder, etc.) or browser/React progress UI patterns.

### 6. Configure the Global Environment

```javascript
import { env } from '@huggingface/transformers';

// Common settings
env.allowRemoteModels = true;       // Load from Hugging Face Hub
env.allowLocalModels = false;       // Load from file system
env.localModelPath = '/models/';    // Local model directory
env.useFSCache = true;              // Cache on disk (Node.js)
env.useBrowserCache = true;         // Cache in browser
env.cacheDir = './.cache';          // Cache directory location
```

**Typical patterns:**

```javascript
// Development: remote models + disk cache
env.allowRemoteModels = true;
env.useFSCache = true;

// Production: local models only (no network dependency)
env.allowRemoteModels = false;
env.allowLocalModels = true;
env.localModelPath = '/app/models/';

// Custom CDN / mirror
env.remoteHost = 'https://cdn.example.com/models';
```

> **Load `./references/CONFIGURATION.md`** when you need the complete `env` API (all flags, cache directory management, custom backends, pre-downloading models, or disabling caching for tests).

> **Load `./references/CACHE.md`** when you need details on browser Cache API storage, Node.js filesystem cache layout, cache eviction, or custom cache implementations.

### 7. Dispose Pipelines to Free Memory

**HARD RULE:** Always call `pipe.dispose()` when finished. Models hold 100 MB – several GB of memory and retain GPU/CPU resources.

```javascript
const pipe = await pipeline('sentiment-analysis');
const result = await pipe('Great product!');
await pipe.dispose();  // Free memory
```

**When to dispose:**
- Application shutdown or component unmount (React `useEffect` cleanup)
- Before loading a different model for the same task
- After batch processing in long-running server processes
- On `SIGTERM` / `SIGINT` in Node.js servers

> **Load `./references/EXAMPLES.md`** when you need real-world cleanup patterns for React components, Express servers, CLI tools, or browser SPAs.

### 8. Task-Specific Usage

#### NLP Tasks

```javascript
// Text classification / sentiment
const classifier = await pipeline('text-classification');
const result = await classifier('This movie was amazing!');

// Named entity recognition
const ner = await pipeline('token-classification');
const entities = await ner('My name is John and I live in New York.');

// Question answering
const qa = await pipeline('question-answering');
const answer = await qa({
  question: 'What is the capital of France?',
  context: 'Paris is the capital and largest city of France.'
});

// Text generation
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

// Zero-shot classification
const zsClassifier = await pipeline('zero-shot-classification');
const result = await zsClassifier('This is a story about sports.', ['politics', 'sports', 'technology']);
```

> **Load `./references/TEXT_GENERATION.md`** when you need streaming token-by-token output (`TextStreamer`), chat/conversation format with system/user/assistant roles, generation parameters (temperature, top_k, top_p, repetition_penalty), or React/API endpoint examples.

#### Computer Vision Tasks

```javascript
// Image classification
const classifier = await pipeline('image-classification');
const result = await classifier('https://example.com/image.jpg');

// Object detection
const detector = await pipeline('object-detection');
const objects = await detector('https://example.com/image.jpg');
// => [{ label: 'person', score: 0.95, box: { xmin, ymin, xmax, ymax } }, ...]

// Image segmentation
const segmenter = await pipeline('image-segmentation');
const segments = await segmenter('https://example.com/image.jpg');

// Depth estimation
const depthEstimator = await pipeline('depth-estimation');
const depth = await depthEstimator('https://example.com/image.jpg');

// Zero-shot image classification
const zsImgClassifier = await pipeline('zero-shot-image-classification');
const result = await zsImgClassifier('image.jpg', ['cat', 'dog', 'bird']);
```

#### Audio Tasks

```javascript
// Automatic speech recognition
const transcriber = await pipeline('automatic-speech-recognition');
const result = await transcriber('audio.wav');
// => { text: 'transcribed text here' }

// Audio classification
const audioClassifier = await pipeline('audio-classification');
const result = await audioClassifier('audio.wav');

// Text-to-speech
const synthesizer = await pipeline('text-to-speech', 'Xenova/speecht5_tts');
const audio = await synthesizer('Hello, this is a test.', {
  speaker_embeddings: speakerEmbeddings
});
```

#### Multimodal Tasks

```javascript
// Image-to-text (captioning)
const captioner = await pipeline('image-to-text');
const caption = await captioner('image.jpg');

// Document question answering
const docQA = await pipeline('document-question-answering');
const answer = await docQA('document-image.jpg', 'What is the total amount?');

// Zero-shot object detection
const detector = await pipeline('zero-shot-object-detection');
const objects = await detector('image.jpg', ['person', 'car', 'tree']);
```

#### Feature Extraction (Embeddings)

```javascript
// Raw embeddings (token-level)
const extractor = await pipeline('feature-extraction');
const embeddings = await extractor('This is a sentence to embed.');
// => tensor of shape [1, sequence_length, hidden_size]

// Sentence embeddings (mean pooling + normalization)
const extractor = await pipeline('feature-extraction', 'onnx-community/all-MiniLM-L6-v2-ONNX');
const embeddings = await extractor('Text to embed', { pooling: 'mean', normalize: true });
```

### 9. Batch Processing

```javascript
const classifier = await pipeline('sentiment-analysis');
const results = await classifier([
  'I love this!',
  'This is terrible.',
  'It was okay.'
]);
```

### 10. Low-Level Access (Tokenizer + Model)

For fine-grained control, load tokenizer and model separately:

```javascript
import { AutoTokenizer, AutoModel } from '@huggingface/transformers';

const tokenizer = await AutoTokenizer.from_pretrained('bert-base-uncased');
const model = await AutoModel.from_pretrained('bert-base-uncased');

const inputs = await tokenizer('Hello world!');
const outputs = await model(inputs);
```

> **Load `./references/MODEL_ARCHITECTURES.md`** when you need the full list of supported model architectures, AutoModel/AutoTokenizer class hierarchy, or model-specific loading tips.

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

## Quick Reference: Task IDs

| Task | Task ID |
|------|---------|
| Text classification | `text-classification` or `sentiment-analysis` |
| Token classification (NER) | `token-classification` or `ner` |
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

## Pitfalls

1. **Never skip `pipe.dispose()`** — Models hold 100 MB to several GB. Failing to dispose causes memory leaks, browser tab crashes, and server OOM kills. This is the #1 source of production failures.

2. **Not all Hugging Face models work with Transformers.js** — Only models with ONNX weights (an `onnx/` folder in the repo) are compatible. Always verify ONNX availability before selecting a model.

3. **WebGPU is experimental** — Requires Chrome 113+ or Edge 113+. If `fp32` fails on WebGPU, try `fp16`. Always provide a WASM fallback for unsupported browsers.

4. **First inference is slow** — The first call to `pipeline()` downloads the model (can be hundreds of MB). Use `progress_callback` to show loading state. Subsequent calls use cache.

5. **Quantization trade-offs are real** — `q4` models are much smaller but can show noticeable accuracy degradation. Test with your actual data before committing to a quantization level.

6. **Browser memory limits** — Large models (> 500 MB) can crash browser tabs. Use `q8` or `q4` quantization and prefer smaller models for browser deployment.

7. **Recreating pipelines is expensive** — Don't create a new `pipeline()` for each inference call. Create once, reuse for all inferences, dispose at shutdown.

8. **Model name typos** — Hugging Face model IDs are case-sensitive and include the namespace (e.g., `Xenova/bert-base-multilingual-uncased-sentiment`, not `bert-base-multilingual-uncased-sentiment`).

9. **Caching can go stale** — If a model is updated on the Hub, your local cache may hold an older version. Pin a `revision` hash in production, or clear cache when upgrading.

10. **`max_new_tokens` unbounded** — For text generation, always set `max_new_tokens` to a reasonable limit. Unbounded generation can exhaust memory and produce runaway output.

11. **Windows path handling** — When setting `env.localModelPath` on Windows (PowerShell), use forward slashes or raw strings to avoid backslash escaping issues:
    ```javascript
    env.localModelPath = 'C:/Users/yourname/models/';  // forward slashes work
    ```

## Verification

### Verify Installation

```powershell
# Check package is installed
npm list @huggingface/transformers
```

### Verify a Pipeline Works (Node.js)

Create `test-pipeline.mjs`:

```javascript
import { pipeline } from '@huggingface/transformers';

const classifier = await pipeline('sentiment-analysis');
const result = await classifier('I love transformers!');
console.log(result);
// Expected: [{ label: 'POSITIVE', score: 0.9998... }]

await classifier.dispose();
console.log('Pipeline disposed successfully.');
```

Run it:

```powershell
node test-pipeline.mjs
```

**Expected output:**
```
[ { label: 'POSITIVE', score: 0.999817686 } ]
Pipeline disposed successfully.
```

### Verify Environment Configuration

```javascript
import { env } from '@huggingface/transformers';

console.log('Version:', env.version);           // e.g., '3.8.1'
console.log('Remote models:', env.allowRemoteModels);  // true
console.log('FS cache:', env.useFSCache);             // true
console.log('Cache dir:', env.cacheDir);              // default path
```

### Verify Model Compatibility

Before committing to a model, check the Hugging Face Hub repo:

1. Navigate to `https://huggingface.co/<model-id>`
2. Confirm an `onnx/` folder exists with `.onnx` weight files
3. Check the model card for `transformers.js` usage examples
4. Verify the model supports your desired task (`pipeline_tag`)

## Related Skills

- **onnx-runtime** — Lower-level ONNX Runtime Web/Node usage without the pipeline abstraction
- **huggingface-hub** — Downloading, uploading, and managing models on the Hub
- **rag-embeddings** — Building retrieval-augmented generation pipelines with feature-extraction models

## Reference Files in This Skill

Load these on demand when you need deeper detail:

| Reference | When to Load |
|-----------|-------------|
| `./references/PIPELINE_OPTIONS.md` | Full pipeline constructor options, progress callback patterns, device/dtype matrices |
| `./references/CONFIGURATION.md` | Complete `env` API, all flags, custom backends, pre-downloading |
| `./references/CACHE.md` | Browser Cache API, Node.js FS cache layout, eviction, custom cache |
| `./references/TEXT_GENERATION.md` | Streaming, chat format, generation parameters, React/API examples |
| `./references/MODEL_ARCHITECTURES.md` | Supported architectures, AutoModel hierarchy, model-specific tips |
| `./references/EXAMPLES.md` | Real-world implementations: React cleanup, Express servers, CLI tools |

## Official Resources

- Docs: https://huggingface.co/docs/transformers.js
- API reference: https://huggingface.co/docs/transformers.js/api/pipelines
- Model hub: https://huggingface.co/models?library=transformers.js
- GitHub: https://github.com/huggingface/transformers.js
- Examples: https://github.com/huggingface/transformers.js/tree/main/examples
