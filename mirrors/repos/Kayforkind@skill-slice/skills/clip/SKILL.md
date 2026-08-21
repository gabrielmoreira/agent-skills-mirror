---
name: clip
description: "Runs OpenAI CLIP for zero-shot image classification, image-text cosine matching, semantic search, and cross-modal retrieval in a shared embedding space. Use when labeling images without training, ranking images by a text query, or scoring vision-language similarity. Not for captioning (BLIP-2), conversational VLM chat (LLaVA), or pixel-level segmentation (SAM); never skip L2-normalizing embeddings before cosine scores."
version: 1.0.1
author: Orchestra Research
license: MIT
dependencies: [transformers, torch, pillow, ftfy, regex, tqdm]
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [Multimodal, CLIP, Vision-Language, Zero-Shot, Image Classification, OpenAI, Image Search, Cross-Modal Retrieval, Content Moderation]

---

# CLIP — Contrastive Language-Image Pre-Training

OpenAI's CLIP connects vision and language in a shared embedding space, enabling zero-shot image classification, image-text similarity, semantic image search, and cross-modal retrieval without fine-tuning. Trained on 400M image-text pairs; matches ResNet-50 zero-shot on ImageNet.

## When to Use

**Use CLIP when you need:**
- Zero-shot image classification (no training data required)
- Image-text similarity or matching scores
- Semantic image search (text query → ranked images)
- Content moderation (detect NSFW, violence, graphic content)
- Cross-modal retrieval (image→text, text→image)
- Visual question answering (broad category level)

**Use alternatives instead:**
- **BLIP-2** — better image captioning
- **LLaVA** — vision-language conversational chat
- **Segment Anything (SAM)** — pixel-level image segmentation

## Prerequisites

1. Python 3.8+ installed on the host.
2. PyTorch with CUDA support if a GPU is available (10–50× faster). CPU works but is slower.
3. On Windows (PowerShell), ensure `python` and `pip` are on `PATH`:
   ```powershell
   python --version
   pip --version
   ```
4. Install the OpenAI CLIP package and dependencies:
   ```powershell
   pip install git+https://github.com/openai/CLIP.git
   pip install torch torchvision ftfy regex tqdm
   ```
5. Verify import:
   ```powershell
   python -c "import clip; print('CLIP OK')"
   ```

## Procedure

### 1. Load a model and preprocess function

```python
import torch
import clip
from PIL import Image

device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/32", device=device)
```

**Available models (sorted by size):**

| Model    | Parameters | Speed | Quality |
|----------|------------|-------|---------|
| RN50     | 102M       | Fast  | Good    |
| RN101    | —          | Medium| Good    |
| ViT-B/32 | 151M       | Medium| Better (recommended) |
| ViT-B/16 | —          | Slower| Better  |
| ViT-L/14 | 428M       | Slow  | Best    |

```python
# List all available models
print(clip.available_models())
```

### 2. Zero-shot image classification

```python
import torch
import clip
from PIL import Image

device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/32", device=device)

# Load and preprocess image
image = preprocess(Image.open("photo.jpg")).unsqueeze(0).to(device)

# Define candidate labels (descriptive phrases work best)
labels = ["a dog", "a cat", "a bird", "a car"]
text = clip.tokenize(labels).to(device)

# Compute similarity and probabilities
with torch.no_grad():
    logits_per_image, _ = model(image, text)
    probs = logits_per_image.softmax(dim=-1).cpu().numpy()

for label, prob in zip(labels, probs[0]):
    print(f"{label}: {prob:.2%}")
```

### 3. Image-text similarity (cosine)

```python
# Encode and normalize
with torch.no_grad():
    image_features = model.encode_image(image)
    text_features = model.encode_text(text)

image_features /= image_features.norm(dim=-1, keepdim=True)
text_features /= text_features.norm(dim=-1, keepdim=True)

similarity = (image_features @ text_features.T).item()
print(f"Similarity: {similarity:.4f}")
```

> **HARD RULE:** Always normalize embeddings before computing cosine similarity. Unnormalized dot products are not bounded to [-1, 1] and will produce misleading scores.

### 4. Semantic image search (text → images)

```python
image_paths = ["img1.jpg", "img2.jpg", "img3.jpg"]
image_embeddings = []

for img_path in image_paths:
    image = preprocess(Image.open(img_path)).unsqueeze(0).to(device)
    with torch.no_grad():
        embedding = model.encode_image(image)
        embedding /= embedding.norm(dim=-1, keepdim=True)
    image_embeddings.append(embedding)

image_embeddings = torch.cat(image_embeddings)

# Encode text query
query = "a sunset over the ocean"
text_input = clip.tokenize([query]).to(device)
with torch.no_grad():
    text_embedding = model.encode_text(text_input)
    text_embedding /= text_embedding.norm(dim=-1, keepdim=True)

# Rank images
similarities = (text_embedding @ image_embeddings.T).squeeze(0)
top_k = similarities.topk(3)

for idx, score in zip(top_k.indices, top_k.values):
    print(f"{image_paths[idx]}: {score:.3f}")
```

### 5. Content moderation

```python
categories = [
    "safe for work",
    "not safe for work",
    "violent content",
    "graphic content"
]

text = clip.tokenize(categories).to(device)

with torch.no_grad():
    logits_per_image, _ = model(image, text)
    probs = logits_per_image.softmax(dim=-1)

max_idx = probs.argmax().item()
max_prob = probs[0, max_idx].item()
print(f"Category: {categories[max_idx]} ({max_prob:.2%})")
```

### 6. Batch processing

```python
# Batch of images
images = [preprocess(Image.open(f"img{i}.jpg")) for i in range(10)]
images = torch.stack(images).to(device)

with torch.no_grad():
    image_features = model.encode_image(images)
    image_features /= image_features.norm(dim=-1, keepdim=True)

# Batch of texts
texts = ["a dog", "a cat", "a bird"]
text_tokens = clip.tokenize(texts).to(device)

with torch.no_grad():
    text_features = model.encode_text(text_tokens)
    text_features /= text_features.norm(dim=-1, keepdim=True)

# Similarity matrix: (10 images × 3 texts)
similarities = image_features @ text_features.T
print(similarities.shape)  # torch.Size([10, 3])
```

### 7. Integration with a vector database (Chroma)

```python
import chromadb

client = chromadb.Client()
collection = client.create_collection("image_embeddings")

# Add image embeddings
for img_path, embedding in zip(image_paths, image_embeddings):
    collection.add(
        embeddings=[embedding.cpu().numpy().tolist()],
        metadatas=[{"path": img_path}],
        ids=[img_path]
    )

# Query with text
query = "a sunset"
text_embedding = model.encode_text(clip.tokenize([query]).to(device))
text_embedding /= text_embedding.norm(dim=-1, keepdim=True)

results = collection.query(
    query_embeddings=[text_embedding.cpu().numpy().tolist()],
    n_results=5
)
print(results)
```

### Best practices

1. **Use ViT-B/32 for most cases** — best speed/quality balance.
2. **Always normalize embeddings** — required for cosine similarity.
3. **Batch processing** — encode multiple images/texts in one forward pass for efficiency.
4. **Cache embeddings** — re-encoding is expensive; store normalized vectors.
5. **Use descriptive labels** — "a photo of a golden retriever" beats "dog".
6. **GPU recommended** — 10–50× faster than CPU.
7. **Always use the provided `preprocess` function** — handles resize, center crop, normalization. Do not feed raw PIL images.

## Pitfalls

1. **Not for fine-grained tasks** — CLIP excels at broad categories; it struggles with sub-class distinctions (e.g., 200 bird species).
2. **Vague labels perform poorly** — "animal" is weak; "a photo of a sleeping cat on a couch" is strong.
3. **Dataset biases** — trained on web image-text pairs; may reflect societal and dataset biases. Do not use as sole arbiter for sensitive moderation decisions.
4. **No bounding boxes** — CLIP operates on whole images only. Use a detection model (YOLO, DETR) for localization.
5. **Limited spatial understanding** — weak at counting, positional reasoning, and reading text in images.
6. **Forgetting to normalize** — the most common bug. Without L2 normalization, dot products are not cosine similarities.
7. **Token length limit** — `clip.tokenize` truncates to 77 context tokens. Long prompts are silently cut; keep labels concise.
8. **CPU-only latency** — image encoding ~200 ms on CPU vs ~20 ms on GPU. For production search, use GPU or pre-compute and cache.

## Verification

1. **Verify installation:**
   ```powershell
   python -c "import clip; print(clip.available_models())"
   ```
   Expected output includes: `['RN50', 'RN101', 'RN50x4', 'RN50x16', 'RN50x64', 'ViT-B/32', 'ViT-B/16', 'ViT-L/14', 'ViT-L/14@336px']`

2. **Verify model loads and produces embeddings:**
   ```python
   import torch, clip
   device = "cuda" if torch.cuda.is_available() else "cpu"
   model, preprocess = clip.load("ViT-B/32", device=device)
   text = clip.tokenize(["a test label"]).to(device)
   with torch.no_grad():
       feats = model.encode_text(text)
   print(feats.shape)  # torch.Size([1, 512])
   ```

3. **Verify zero-shot classification output format:**
   ```python
   probs = logits_per_image.softmax(dim=-1).cpu().numpy()
   assert probs.shape == (1, len(labels))
   assert abs(probs.sum() - 1.0) < 1e-5  # probabilities sum to 1
   ```

4. **Verify cosine similarity is bounded:**
   ```python
   image_features /= image_features.norm(dim=-1, keepdim=True)
   text_features /= text_features.norm(dim=-1, keepdim=True)
   sim = (image_features @ text_features.T).item()
   assert -1.0 <= sim <= 1.0
   ```

## Performance Reference

| Operation           | CPU      | GPU (V100) |
|---------------------|----------|------------|
| Image encoding      | ~200 ms  | ~20 ms     |
| Text encoding       | ~50 ms   | ~5 ms      |
| Similarity compute  | <1 ms    | <1 ms      |

## Resources

- **GitHub:** https://github.com/openai/CLIP (25,300+ stars)
- **Paper:** https://arxiv.org/abs/2103.00020
- **Colab:** https://colab.research.google.com/github/openai/clip/
- **License:** MIT
