---
name: huggingface-tokenizers
description: "Trains and runs Hugging Face tokenizers (Rust core): BPE, WordPiece, Unigram, offset alignment, padding/truncation, and PreTrainedTokenizerFast wrap. Use when the user needs fast tokenization, custom tokenizer training, or token-to-text offsets for NER/QA. Not for SentencePiece (T5/ALBERT native), tiktoken (OpenAI GPT), or only loading a pretrained AutoTokenizer. Never add special tokens after training — IDs shift and break weights."
version: 1.0.1
author: Orchestra Research
license: MIT
dependencies: [tokenizers, transformers, datasets]
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Tokenization, HuggingFace, BPE, WordPiece, Unigram, Fast Tokenization, Rust, Custom Tokenizer, Alignment Tracking, Production]
---

# HuggingFace Tokenizers — Fast Tokenization for NLP

Fast, production-ready tokenizers with a Rust core and Python bindings. Tokenizes ~1 GB of text in <20 seconds on CPU. Supports BPE, WordPiece, and Unigram algorithms, alignment tracking, padding/truncation, and seamless `transformers` integration.

## When to Use

**Use this skill when you need to:**
- Tokenize large corpora at high speed (<20 s per GB on CPU)
- Train a custom tokenizer from scratch (BPE, WordPiece, or Unigram)
- Track token-to-original-text alignment offsets (NER, QA, token classification)
- Build production NLP pipelines with deterministic tokenization
- Wrap a custom tokenizer for `transformers` (`PreTrainedTokenizerFast`)

**Use alternatives instead when:**
- **SentencePiece** — language-independent tokenization used by T5/ALBERT natively
- **tiktoken** — OpenAI GPT model tokenization specifically
- **`transformers.AutoTokenizer`** — only loading pretrained tokenizers (uses this library internally)

## Prerequisites

- Python 3.8+
- `pip install tokenizers` (minimum), or `pip install tokenizers transformers datasets` for full integration
- Windows PowerShell is the primary host. Use `python` (not `python3`) in PowerShell commands.

```powershell
# Windows PowerShell — install
pip install tokenizers transformers datasets
```

```bash
# Linux/macOS — install
pip3 install tokenizers transformers datasets
```

## Procedure

### 1. Load a Pretrained Tokenizer

```python
from tokenizers import Tokenizer

# Load from HuggingFace Hub
tokenizer = Tokenizer.from_pretrained("bert-base-uncased")

# Encode text
output = tokenizer.encode("Hello, how are you?")
print(output.tokens)  # ['hello', ',', 'how', 'are', 'you', '?']
print(output.ids)     # [7592, 1010, 2129, 2024, 2017, 1029]

# Decode back
text = tokenizer.decode(output.ids)
print(text)  # "hello, how are you?"
```

### 2. Train a Custom BPE Tokenizer

```python
from tokenizers import Tokenizer
from tokenizers.models import BPE
from tokenizers.trainers import BpeTrainer
from tokenizers.pre_tokenizers import Whitespace

# Initialize tokenizer with BPE model
tokenizer = Tokenizer(BPE(unk_token="[UNK]"))
tokenizer.pre_tokenizer = Whitespace()

# Configure trainer
trainer = BpeTrainer(
    vocab_size=30000,
    special_tokens=["[UNK]", "[CLS]", "[SEP]", "[PAD]", "[MASK]"],
    min_frequency=2
)

# Train on files
files = ["train.txt", "validation.txt"]
tokenizer.train(files, trainer)

# Save
tokenizer.save("my-tokenizer.json")
```

**Training time**: ~1–2 minutes for 100 MB corpus, ~10–20 minutes for 1 GB.

### 3. Batch Encoding with Padding

```python
# Enable padding
tokenizer.enable_padding(pad_id=3, pad_token="[PAD]")

# Encode batch
texts = ["Hello world", "This is a longer sentence"]
encodings = tokenizer.encode_batch(texts)

for encoding in encodings:
    print(encoding.ids)
# [101, 7592, 2088, 102, 3, 3, 3]
# [101, 2023, 2003, 1037, 2936, 6251, 102]
```

### 4. Choose a Tokenization Algorithm

#### BPE (Byte-Pair Encoding)

Used by GPT-2, GPT-3, RoBERTa, BART, DeBERTa.

```python
from tokenizers import Tokenizer
from tokenizers.models import BPE
from tokenizers.trainers import BpeTrainer
from tokenizers.pre_tokenizers import ByteLevel

tokenizer = Tokenizer(BPE(unk_token="<unk>"))
tokenizer.pre_tokenizer = ByteLevel()

trainer = BpeTrainer(
    vocab_size=50257,
    special_tokens=["<|endoftext|>"],
    min_frequency=2
)

tokenizer.train(files=["data.txt"], trainer=trainer)
```

**Advantages**: Handles OOV words well (breaks into subwords), flexible vocabulary size, good for morphologically rich languages.
**Trade-offs**: Tokenization depends on merge order; may split common words unexpectedly.

#### WordPiece

Used by BERT, DistilBERT, MobileBERT.

```python
from tokenizers import Tokenizer
from tokenizers.models import WordPiece
from tokenizers.trainers import WordPieceTrainer
from tokenizers.pre_tokenizers import Whitespace
from tokenizers.normalizers import BertNormalizer

tokenizer = Tokenizer(WordPiece(unk_token="[UNK]"))
tokenizer.normalizer = BertNormalizer(lowercase=True)
tokenizer.pre_tokenizer = Whitespace()

trainer = WordPieceTrainer(
    vocab_size=30522,
    special_tokens=["[UNK]", "[CLS]", "[SEP]", "[PAD]", "[MASK]"],
    continuing_subword_prefix="##"
)

tokenizer.train(files=["corpus.txt"], trainer=trainer)
```

**Advantages**: Prioritizes meaningful merges (high score = semantically related), proven in BERT.
**Trade-offs**: Unknown words become `[UNK]` if no subword match; saves vocabulary, not merge rules (larger files).

#### Unigram

Used by ALBERT, T5, mBART, XLNet (via SentencePiece).

```python
from tokenizers import Tokenizer
from tokenizers.models import Unigram
from tokenizers.trainers import UnigramTrainer

tokenizer = Tokenizer(Unigram())

trainer = UnigramTrainer(
    vocab_size=8000,
    special_tokens=["<unk>", "<s>", "</s>"],
    unk_token="<unk>"
)

tokenizer.train(files=["data.txt"], trainer=trainer)
```

**Advantages**: Probabilistic (finds most likely tokenization), works well for languages without word boundaries.
**Trade-offs**: Computationally expensive to train, more hyperparameters to tune.

> **When to load deeper reference**: For algorithm internals and selection criteria, load `references/algorithms.md`.

### 5. Configure the Tokenization Pipeline

Pipeline order: **Normalization → Pre-tokenization → Model → Post-processing**

#### Normalization

```python
from tokenizers.normalizers import NFD, StripAccents, Lowercase, Sequence

tokenizer.normalizer = Sequence([
    NFD(),           # Unicode normalization (decompose)
    Lowercase(),     # Convert to lowercase
    StripAccents()   # Remove accents
])

# Input: "Héllo WORLD" → After normalization: "hello world"
```

Common normalizers: `NFD`, `NFC`, `NFKD`, `NFKC`, `Lowercase()`, `StripAccents()`, `Strip()`, `Replace(pattern, content)`.

#### Pre-tokenization

```python
from tokenizers.pre_tokenizers import Whitespace, Punctuation, Sequence, ByteLevel

# Split on whitespace and punctuation
tokenizer.pre_tokenizer = Sequence([
    Whitespace(),
    Punctuation()
])

# Input: "Hello, world!" → ["Hello", ",", "world", "!"]
```

Common pre-tokenizers: `Whitespace()`, `ByteLevel()`, `Punctuation()`, `Digits(individual_digits=True)`, `Metaspace()`.

#### Post-processing

```python
from tokenizers.processors import TemplateProcessing

# BERT-style: [CLS] sentence [SEP]
tokenizer.post_processor = TemplateProcessing(
    single="[CLS] $A [SEP]",
    pair="[CLS] $A [SEP] $B [SEP]",
    special_tokens=[
        ("[CLS]", 1),
        ("[SEP]", 2),
    ],
)
```

Common patterns:

```python
# GPT-2: sentence <|endoftext|>
TemplateProcessing(
    single="$A <|endoftext|>",
    special_tokens=[("<|endoftext|>", 50256)]
)

# RoBERTa: <s> sentence </s>
TemplateProcessing(
    single="<s> $A </s>",
    pair="<s> $A </s> </s> $B </s>",
    special_tokens=[("<s>", 0), ("</s>", 2)]
)
```

> **When to load deeper reference**: For full pipeline component details (normalizers, pre-tokenizers, post-processors, decoders), load `references/pipeline.md`.

### 6. Track Token Alignment

```python
text = "Hello, world!"
output = tokenizer.encode(text)

# Get token offsets
for token, offset in zip(output.tokens, output.offsets):
    start, end = offset
    print(f"{token:10} → [{start:2}, {end:2}): {text[start:end]!r}")

# Output:
# hello      → [ 0,  5): 'Hello'
# ,          → [ 5,  6): ','
# world      → [ 7, 12): 'world'
# !          → [12, 13): '!'
```

**Use cases**: Named entity recognition (map predictions back to text), question answering (extract answer spans), token classification (align labels to original positions).

### 7. Integrate with Transformers

#### Load with AutoTokenizer

```python
from transformers import AutoTokenizer

# AutoTokenizer automatically uses fast tokenizers
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

# Check if using fast tokenizer
print(tokenizer.is_fast)  # True

# Access underlying tokenizers.Tokenizer
fast_tokenizer = tokenizer.backend_tokenizer
print(type(fast_tokenizer))  # <class 'tokenizers.Tokenizer'>
```

#### Convert Custom Tokenizer to Transformers

```python
from tokenizers import Tokenizer
from transformers import PreTrainedTokenizerFast

# Train custom tokenizer
tokenizer = Tokenizer(BPE())
# ... train tokenizer ...
tokenizer.save("my-tokenizer.json")

# Wrap for transformers
transformers_tokenizer = PreTrainedTokenizerFast(
    tokenizer_file="my-tokenizer.json",
    unk_token="[UNK]",
    pad_token="[PAD]",
    cls_token="[CLS]",
    sep_token="[SEP]",
    mask_token="[MASK]"
)

# Use like any transformers tokenizer
outputs = transformers_tokenizer(
    "Hello world",
    padding=True,
    truncation=True,
    max_length=512,
    return_tensors="pt"
)
```

> **When to load deeper reference**: For AutoTokenizer, PreTrainedTokenizerFast, and special token configuration details, load `references/integration.md`.

### 8. Train from Iterator (Large Datasets)

```python
from datasets import load_dataset

# Load dataset
dataset = load_dataset("wikitext", "wikitext-103-raw-v1", split="train")

# Create batch iterator
def batch_iterator(batch_size=1000):
    for i in range(0, len(dataset), batch_size):
        yield dataset[i:i + batch_size]["text"]

# Train tokenizer
tokenizer.train_from_iterator(
    batch_iterator(),
    trainer=trainer,
    length=len(dataset)  # For progress bar
)
```

**Performance**: Processes 1 GB in ~10–20 minutes.

> **When to load deeper reference**: For advanced training configurations and large-dataset handling, load `references/training.md`.

### 9. Enable Truncation and Padding

```python
# Enable truncation
tokenizer.enable_truncation(max_length=512)

# Enable padding
tokenizer.enable_padding(
    pad_id=tokenizer.token_to_id("[PAD]"),
    pad_token="[PAD]",
    length=512  # Fixed length, or None for batch max
)

# Encode with both
output = tokenizer.encode("This is a long sentence that will be truncated...")
print(len(output.ids))  # 512
```

### 10. Multi-processing for Large Corpora

```python
from tokenizers import Tokenizer
from multiprocessing import Pool

# Load tokenizer
tokenizer = Tokenizer.from_file("tokenizer.json")

def encode_batch(texts):
    return tokenizer.encode_batch(texts)

# Process large corpus in parallel
with Pool(8) as pool:
    # Split corpus into chunks
    chunk_size = 1000
    chunks = [corpus[i:i+chunk_size] for i in range(0, len(corpus), chunk_size)]

    # Encode in parallel
    results = pool.map(encode_batch, chunks)
```

**Speedup**: 5–8× with 8 cores.

## Examples

### Performance Benchmarks

#### Training Speed

| Corpus Size | BPE (30k vocab) | WordPiece (30k) | Unigram (8k) |
|-------------|-----------------|-----------------|--------------|
| 10 MB       | 15 sec          | 18 sec          | 25 sec       |
| 100 MB      | 1.5 min         | 2 min           | 4 min        |
| 1 GB        | 15 min          | 20 min          | 40 min       |

**Hardware**: 16-core CPU, tested on English Wikipedia.

#### Tokenization Speed

| Implementation | 1 GB corpus | Throughput    |
|----------------|-------------|---------------|
| Pure Python    | ~20 minutes | ~50 MB/min    |
| HF Tokenizers  | ~15 seconds | ~4 GB/min     |
| **Speedup**    | **80×**     | **80×**       |

**Test**: English text, average sentence length 20 words.

#### Memory Usage

| Task                    | Memory  |
|-------------------------|---------|
| Load tokenizer          | ~10 MB  |
| Train BPE (30k vocab)   | ~200 MB |
| Encode 1M sentences     | ~500 MB |

### Supported Pretrained Models

Available via `from_pretrained()`:

- **BERT family**: `bert-base-uncased`, `bert-large-cased`, `distilbert-base-uncased`, `roberta-base`, `roberta-large`
- **GPT family**: `gpt2`, `gpt2-medium`, `gpt2-large`, `distilgpt2`
- **T5 family**: `t5-small`, `t5-base`, `t5-large`, `google/flan-t5-xxl`
- **Other**: `facebook/bart-base`, `facebook/mbart-large-cc25`, `albert-base-v2`, `albert-xlarge-v2`, `xlm-roberta-base`, `xlm-roberta-large`

Browse all: https://huggingface.co/models?library=tokenizers

## Pitfalls

- **Do not mix `Tokenizer` and `AutoTokenizer` APIs interchangeably.** `tokenizers.Tokenizer` uses `encode()` / `encode_batch()`; `transformers` tokenizers use `__call__`. Confusing them causes `AttributeError`.
- **Special tokens must be declared in the trainer** before training, not added after. If you add them post-training, token IDs will shift and break model weights.
- **`enable_padding` with a fixed `length`** pads every sequence to that length — memory waste if sequences are short. Use `length=None` to pad to batch max instead.
- **`enable_truncation` modifies the encoding in place.** Once enabled, all subsequent `encode()` calls truncate. Disable with `tokenizer.no_truncation()` if you need full sequences later.
- **WordPiece unknown words become `[UNK]`** if no subword decomposition matches. BPE/Unigram decompose into subwords instead — choose algorithm accordingly.
- **Unigram training is computationally expensive** — expect 2–3× longer than BPE for the same corpus.
- **`from_pretrained` requires network access** to the HuggingFace Hub. For offline use, download the `tokenizer.json` first and use `Tokenizer.from_file()`.
- **ByteLevel pre-tokenizer produces byte-level tokens** — do not pair it with `Whitespace` or you will get inconsistent tokenization for GPT-style models.
- **Alignment offsets are only available when `Tokenizer` is used directly** (not through `transformers.AutoTokenizer` unless you access `.backend_tokenizer`).
- **Windows PowerShell**: use `python` not `python3`. If `pip` is not on PATH, use `python -m pip install ...`.

## Verification

### Verify Installation

```powershell
# Windows PowerShell
python -c "import tokenizers; print(tokenizers.__version__)"
# Expected: 0.20.0 or higher
```

```bash
# Linux/macOS
python3 -c "import tokenizers; print(tokenizers.__version__)"
```

### Verify Pretrained Tokenizer Loads

```python
from tokenizers import Tokenizer

tokenizer = Tokenizer.from_pretrained("bert-base-uncased")
output = tokenizer.encode("Hello, how are you?")
assert output.tokens == ['hello', ',', 'how', 'are', 'you', '?'], f"Unexpected tokens: {output.tokens}"
assert output.ids == [7592, 1010, 2129, 2024, 2017, 1029], f"Unexpected ids: {output.ids}"
print("✓ Pretrained tokenizer verified")
```

### Verify Custom Training

```python
from tokenizers import Tokenizer
from tokenizers.models import BPE
from tokenizers.trainers import BpeTrainer
from tokenizers.pre_tokenizers import Whitespace
import tempfile, os

tokenizer = Tokenizer(BPE(unk_token="[UNK]"))
tokenizer.pre_tokenizer = Whitespace()

trainer = BpeTrainer(
    vocab_size=100,
    special_tokens=["[UNK]", "[CLS]", "[SEP]", "[PAD]", "[MASK]"],
    min_frequency=1
)

# Write a small test corpus
with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
    f.write("hello world hello there world hello\n" * 100)
    test_file = f.name

tokenizer.train([test_file], trainer)
os.unlink(test_file)

# Verify it can encode
output = tokenizer.encode("hello world")
assert len(output.tokens) > 0, "No tokens produced"
assert "[UNK]" not in output.tokens or len(output.tokens) > 1, "Everything is UNK"
print(f"✓ Custom training verified: {len(output.tokens)} tokens for 'hello world'")
```

### Verify Transformers Integration

```python
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
assert tokenizer.is_fast, "Fast tokenizer not loaded"
assert hasattr(tokenizer, "backend_tokenizer"), "No backend_tokenizer attribute"
print(f"✓ Fast tokenizer verified: {type(tokenizer.backend_tokenizer)}")
```

### Verify Alignment Tracking

```python
from tokenizers import Tokenizer

tokenizer = Tokenizer.from_pretrained("bert-base-uncased")
text = "Hello, world!"
output = tokenizer.encode(text)

assert len(output.offsets) == len(output.tokens), "Offset/token count mismatch"
for token, (start, end) in zip(output.tokens, output.offsets):
    assert text[start:end].lower() == token or token in [",", "!"], \
        f"Offset mismatch: token={token}, text_slice={text[start:end]!r}"
print("✓ Alignment tracking verified")
```

## Related Skills

- **huggingface-transformers** — model loading, fine-tuning, and inference pipelines
- **huggingface-datasets** — loading and preprocessing training corpora
- **sentencepiece** — alternative tokenization for T5/ALBERT family models

## References

Load these reference files for deeper detail when the core procedure is insufficient:

- **`references/training.md`** — Train custom tokenizers, configure trainers, handle large datasets. Load when training on corpora >100 MB or when configuring advanced trainer parameters.
- **`references/algorithms.md`** — BPE, WordPiece, Unigram explained in detail. Load when choosing an algorithm or debugging tokenization quality.
- **`references/pipeline.md`** — Normalizers, pre-tokenizers, post-processors, decoders. Load when customizing the tokenization pipeline beyond defaults.
- **`references/integration.md`** — AutoTokenizer, PreTrainedTokenizerFast, special tokens. Load when wrapping a custom tokenizer for `transformers` or debugging integration issues.

## Resources

- **Docs**: https://huggingface.co/docs/tokenizers
- **GitHub**: https://github.com/huggingface/tokenizers
- **Version**: 0.20.0+
- **Course**: https://huggingface.co/learn/nlp-course/chapter6/1
- **Papers**: BPE (Sennrich et al., 2016), WordPiece (Schuster & Nakajima, 2012)
