---
name: train-sentence-transformers
description: Trains or fine-tunes sentence-transformers bi-encoders, CrossEncoder rerankers, and SparseEncoder/SPLADE using the bundled references and example scripts. Use when the user asks to train embeddings, rerankers, or SPLADE on custom data. Not for inference-only embedding calls, Hugging Face paper lookup, or model-card eval tables.
version: 1.0.1
risk: unknown
source: https://github.com/huggingface/skills/tree/main/skills/train-sentence-transformers
source_repo: huggingface/skills
source_type: official
date_added: 2026-07-01
license: Apache-2.0
license_source: https://github.com/huggingface/skills/blob/main/LICENSE
---

# Train a sentence-transformers Model

## Overview

This skill trains or fine-tunes sentence-transformers models across three model classes:

- **`SentenceTransformer`** (bi-encoder; dense or static embedding model) — for retrieval, similarity, clustering, classification, paraphrase mining, dedup, multimodal.
- **`CrossEncoder`** (reranker; pair scoring) — for two-stage retrieval / pair classification.
- **`SparseEncoder`** (SPLADE; sparse vectors over vocabulary) — for learned-sparse retrieval, inverted-index backends (Elasticsearch / OpenSearch / Lucene).

**This SKILL.md is a router, not a manual.** It tells you which references and example scripts to load for your task. The actual content — recommended losses, evaluators, training-script structure, model selection, training-arg knobs, troubleshooting — lives in `references/` and `scripts/`.

**Do not synthesize a training script from this file alone.** Open the matching `train_<type>_example.py` in this skill's scripts folder and copy it as your starting point. The templates contain load-bearing scaffolding (autocast helper, model-card class, logger silencing list, `force=True`, `seed`, TF32, version-compatible imports, named-evaluator metric handling) that prior agent runs have repeatedly missed when rolling their own from a synthesized snippet.

## When to Use

Use this skill when the user needs to:

- Train or fine-tune a **dense embedding model** (retrieval, similarity, clustering, classification, paraphrase mining, dedup, multimodal).
- Train or fine-tune a **reranker / cross-encoder** for two-stage retrieval or pair classification.
- Train or fine-tune a **SPLADE / sparse encoder** for learned-sparse retrieval or inverted-index backends.
- Fine-tune an existing sentence-transformers checkpoint on a custom dataset.
- Add LoRA, distillation, Matryoshka, multi-dataset, multilingual, or static-embedding variants.

**Trigger keywords:** embedding model training, fine-tune sentence-transformers, train reranker, train cross-encoder, train SPLADE, sparse encoder training, retrieval model fine-tuning, sentence similarity model training, bi-encoder training, dense retrieval training.

## Prerequisites

```powershell
pip install "sentence-transformers[train]>=5.0"
# For multimodal [SentenceTransformer], add the relevant extra:
#   pip install "sentence-transformers[train,image]>=5.0"
#   pip install "sentence-transformers[train,audio]>=5.0"
#   pip install "sentence-transformers[train,video]>=5.0"
pip install trackio          # optional tracker; or wandb / tensorboard / mlflow
hf auth login                # or set HF_TOKEN with write scope (for Hub push)
```

GPU strongly recommended. CPU works only for demos and `[SentenceTransformer]` `StaticEmbedding`.

## Procedure

### Step 1 — Identify the model type

| Tag | Class | What it does | When to pick |
|---|---|---|---|
| **[SentenceTransformer]** | `SentenceTransformer` (bi-encoder) | Maps each input to a fixed-dim dense vector | Retrieval, similarity, clustering, classification, paraphrase mining, dedup |
| **[CrossEncoder]** | `CrossEncoder` (reranker) | Scores `(query, passage)` pairs jointly | Two-stage retrieval (rerank top-100 from bi-encoder), pair classification |
| **[SparseEncoder]** | `SparseEncoder` (SPLADE) | Sparse vectors over the vocabulary | Learned-sparse retrieval, inverted-index backends (Elasticsearch / OpenSearch / Lucene) |

**Tiebreakers when the request is ambiguous:**

- "embedding model" / "vector search" / "similarity" → **[SentenceTransformer]**
- "rerank" / "ranker" / "two-stage" → **[CrossEncoder]**
- "SPLADE" / "sparse" / "inverted index" → **[SparseEncoder]**
- If still unclear, ask the user.

### Step 2 — Load required reading (in full, before writing any code)

**Do not triage by perceived relevance. Read every file listed for your type.**

#### Per-type — always required

**[SentenceTransformer]**

- `references/losses_sentence_transformer.md` — loss-to-data-shape mapping; `BatchSamplers.NO_DUPLICATES` requirement for MNRL-family; `Cached*` ↔ `gradient_checkpointing` incompatibility.
- `references/evaluators_sentence_transformer.md` — evaluator-to-task mapping; `metric_for_best_model` key construction (named vs unnamed); per-evaluator `primary_metric` values.
- `references/model_architectures.md` — encoder vs decoder vs static vs Router pipelines; pooling rules (mean / cls / lasttoken); auto-mean-pooling behavior for fresh-start MLM bases.
- `scripts/train_sentence_transformer_example.py` — production template; **copy this as your starting point**.

**[CrossEncoder]**

- `references/losses_cross_encoder.md` — pointwise / pairwise / listwise / distillation; `pos_weight` derivation; `activation_fn=Identity()` mandatory for non-BCE losses (silent eval-rank collapse otherwise).
- `references/evaluators_cross_encoder.md` — `CrossEncoderRerankingEvaluator` recipe; named-evaluator key format `eval_{name}_{primary_metric}`.
- `scripts/train_cross_encoder_example.py` — production template; **copy this as your starting point**.

**[SparseEncoder]**

- `references/losses_sparse_encoder.md` — `SpladeLoss` wrapper requirement; FLOPS regularizer weights; smoke-test active-dim ramp behavior.
- `references/evaluators_sparse_encoder.md` — `SparseNanoBEIREvaluator` (English-only) and the in-domain alternative; `eval_{name}_{primary_metric}` key format.
- `scripts/train_sparse_encoder_example.py` — production template; **copy this as your starting point**.

#### Cross-cutting — always required (regardless of task)

- `references/training_args.md` — `TrainingArguments` knobs, precision rules (load fp32 + autocast bf16/fp16; never `torch_dtype=bfloat16`), `warmup_steps` (float) vs deprecated `warmup_ratio`, `save_steps` must be a multiple of `eval_steps` for `load_best_model_at_end`, schedulers, HPO, tracker, resume, hub-push variants.
- `references/dataset_formats.md` — column-matching rules (label name auto-detection; column-order-not-name); reshaping recipes; hard-negative mining options.
- `references/base_model_selection.md` — discovery commands; per-type model namespaces; ModernBERT-family `max_seq_length=8192` trap; `datasets >= 4` script-loader rejection; non-English starting-point shortcuts.
- `references/troubleshooting.md` — symptom-indexed failure recipes. **Skim the section headings on every run, even a healthy one.** The "Metrics don't improve" and "Hub push fails" entries cover bugs that bite frequently and are cheaper to recognize before they fire than to debug after.

#### Cross-cutting — load when applicable

- `references/hardware_guide.md` — **Required for >24GB models, multi-GPU, or HF Jobs runs.** VRAM sizing, multi-GPU, FSDP / DeepSpeed, HF Jobs flavors.
- `references/hf_jobs_execution.md` — **Required when running on HF Jobs.**
- `references/prompts_and_instructions.md` — **Required when using prompt-tuned bases** (E5, BGE, GTE, Qwen3-Embedding, Instructor, Nomic, etc.) or adding `query: ` / `passage: ` style prefixes.

#### Variant scripts (open when the task matches)

- **[SentenceTransformer]:**
  - `scripts/train_sentence_transformer_matryoshka_example.py`
  - `scripts/train_sentence_transformer_multi_dataset_example.py`
  - `scripts/train_sentence_transformer_with_lora_example.py`
  - `scripts/train_sentence_transformer_distillation_example.py`
  - `scripts/train_sentence_transformer_make_multilingual_example.py`
  - `scripts/train_sentence_transformer_static_embedding_example.py`
- **[CrossEncoder]:**
  - `scripts/train_cross_encoder_distillation_example.py`
  - `scripts/train_cross_encoder_listwise_example.py`
- **[SparseEncoder]:**
  - `scripts/train_sparse_encoder_distillation_example.py`
- **Hard-negative mining CLI:** `scripts/mine_hard_negatives.py`

### Step 3 — Copy the production template

Open the matching `train_<type>_example.py` in this skill's scripts folder (`scripts/train_sentence_transformer_example.py`, `scripts/train_cross_encoder_example.py`, or `scripts/train_sparse_encoder_example.py`) and copy it as your starting point. Do not write a training script from scratch or from a synthesized snippet.

### Step 4 — Replace placeholders with the user's task

Replace `MODEL_NAME`, `DATASET_NAME`, `RUN_NAME`, the loss, and the evaluator with the user's task.

- Cross-check loss/data-shape match against the matching losses file (`references/losses_sentence_transformer.md`, `references/losses_cross_encoder.md`, or `references/losses_sparse_encoder.md`).
- Cross-check the `metric_for_best_model` key against the matching evaluators file (`references/evaluators_sentence_transformer.md`, `references/evaluators_cross_encoder.md`, or `references/evaluators_sparse_encoder.md`) (named evaluators format the key as `eval_{name}_{primary_metric}`).

### Step 5 — Smoke-test before any long run

Set `max_steps=1` with a tiny dataset slice. The production templates show one common pattern using a `SMOKE_TEST` environment variable.

```powershell
# Example smoke-test invocation (pattern from the production template)
$env:SMOKE_TEST = "1"
python scripts/train_sentence_transformer_example.py
```

### Step 6 — Run the full training

```powershell
Remove-Item Env:SMOKE_TEST   # clear smoke-test flag
python scripts/train_sentence_transformer_example.py
```

### Step 7 — After the run

1. Append results to `logs/experiments.md`.
2. Propose iteration if the verdict is weak or marginal.

## Constraints the produced script must satisfy

These are non-negotiable contracts. Implementation lives in the production templates and references — do not reinvent.

1. **Capture the pre-training evaluator score** as `baseline_eval` **before** `trainer.train()`.
2. **Emit a single end-of-run verdict line:**
   ```
   VERDICT: WIN|MARGINAL|REGRESSION | score=... | baseline=... | delta=...
   ```
   A monitor scrapes for this line.
3. **Silence noisy loggers** — set `httpx`, `httpcore`, `huggingface_hub`, `urllib3`, `filelock`, `fsspec` to `WARNING`. Otherwise HF download URLs flood the agent's context.
4. **Tee logs** to `logs/{RUN_NAME}.log`.
5. **End with `model.push_to_hub(...)` wrapped in `try/except`.**
6. **Smoke-test before any long run** (`max_steps=1` + tiny dataset slice). The production templates show one common pattern (`SMOKE_TEST` env var).
7. **[CrossEncoder]** Include `EarlyStoppingCallback(patience>=3)` — CE rerankers often peak mid-training and regress.
8. **[SparseEncoder]** Log `query_active_dims` / `corpus_active_dims` on the verdict line; high nDCG with collapsed sparsity is not a win. The keys come back name-prefixed (e.g. `..._query_active_dims`); use suffix matching to pluck them — see the SPARSE production template for the exact pattern.

## Defaults

Override only if the user specifies otherwise:

- **Local execution.** Pitch HF Jobs only if local hardware can't fit the job.
- **Single run.** After it completes, propose experimentation if the user would benefit (weak/marginal verdict, "see how high you can push it" framing, etc.). Iteration rules in `references/training_args.md` (Experimentation section).
- **Public Hub push at end-of-run, wrapped in try-except.** On HF Jobs (ephemeral env) ALSO enable in-trainer push (`push_to_hub=True` + `hub_strategy="every_save"`); details in `references/hf_jobs_execution.md`.

## Pitfalls

- **Do not synthesize a training script from this file alone.** Always start from the matching `train_<type>_example.py` in this skill's scripts folder. Prior agent runs have repeatedly missed load-bearing scaffolding (autocast helper, model-card class, logger silencing, `force=True`, `seed`, TF32, version-compatible imports, named-evaluator metric handling) when rolling their own.
- **[CrossEncoder] `activation_fn=Identity()` is mandatory for non-BCE losses.** Using the default sigmoid activation with a non-BCE loss causes silent eval-rank collapse.
- **[SentenceTransformer] `Cached*` losses are incompatible with `gradient_checkpointing`.** Do not combine them.
- **[SentenceTransformer] MNRL-family losses require `BatchSamplers.NO_DUPLICATES`.** Using the default batch sampler will silently degrade or break training.
- **`torch_dtype=bfloat16` must never be set at load time.** Load in fp32 and use autocast (bf16/fp16) during training. See `references/training_args.md`.
- **`save_steps` must be a multiple of `eval_steps`** when using `load_best_model_at_end`. Otherwise the trainer raises or silently never loads the best checkpoint.
- **ModernBERT-family models default to `max_seq_length=8192`.** This is a VRAM trap — explicitly set `max_seq_length` to your actual needs. See `references/base_model_selection.md`.
- **`datasets >= 4` rejects some script-based dataset loaders.** Pin or work around per `references/base_model_selection.md`.
- **Named evaluators format `metric_for_best_model` as `eval_{name}_{primary_metric}`**, not `eval_{primary_metric}`. Mismatching this key means the trainer never selects the best model.
- **[SparseEncoder] high nDCG with collapsed sparsity is not a win.** Always check `query_active_dims` / `corpus_active_dims` on the verdict line.
- **HF download URLs flood the agent's context** unless you silence `httpx`, `httpcore`, `huggingface_hub`, `urllib3`, `filelock`, `fsspec` to WARNING.
- **Skim `references/troubleshooting.md` section headings on every run**, even a healthy one. The "Metrics don't improve" and "Hub push fails" entries cover bugs that are cheaper to recognize before they fire.

## Verification

After the training run completes, verify the following:

1. **Verdict line emitted.** Check the log tail for the single-line verdict:
   ```powershell
   Select-String -Path "logs\*.log" -Pattern "^VERDICT:"
   ```
   Expected output:
   ```
   logs/{RUN_NAME}.log:123:VERDICT: WIN | score=0.842 | baseline=0.710 | delta=+0.132
   ```

2. **Baseline was captured before training.** Confirm `baseline_eval` appears in the log before `trainer.train()` output:
   ```powershell
   Select-String -Path "logs\*.log" -Pattern "baseline_eval"
   ```

3. **Best model loaded.** If `load_best_model_at_end=True`, confirm the trainer logged loading the best checkpoint:
   ```powershell
   Select-String -Path "logs\*.log" -Pattern "best model"
   ```

4. **Hub push attempted.** Confirm `push_to_hub` was called (success or caught exception):
   ```powershell
   Select-String -Path "logs\*.log" -Pattern "push_to_hub|Upload|model pushed"
   ```

5. **[SparseEncoder] sparsity logged.** Confirm active dims appear on the verdict line:
   ```powershell
   Select-String -Path "logs\*.log" -Pattern "active_dims"
   ```

6. **[CrossEncoder] early stopping fired (if peak was mid-training).** Confirm callback activity:
   ```powershell
   Select-String -Path "logs\*.log" -Pattern "EarlyStopping|patience"
   ```

7. **Experiments log updated:**
   ```powershell
   Test-Path "logs\experiments.md"
   Select-String -Path "logs\experiments.md" -Pattern $RUN_NAME
   ```

## Related skills

- `references/training_args.md` — deep dive on `TrainingArguments` knobs, precision, schedulers, HPO, resume, hub-push variants.
- `references/hardware_guide.md` — VRAM sizing, multi-GPU, FSDP / DeepSpeed, HF Jobs flavors.
- `references/hf_jobs_execution.md` — running on HF Jobs (ephemeral environment, in-trainer push).
- `references/prompts_and_instructions.md` — prompt-tuned bases (E5, BGE, GTE, Qwen3-Embedding, Instructor, Nomic) and `query: ` / `passage: ` prefixes.
